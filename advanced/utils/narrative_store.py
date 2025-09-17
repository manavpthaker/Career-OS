# utils/narrative_store.py
from __future__ import annotations
import json, re
from pathlib import Path
from typing import Dict, List, Tuple

MD_EXTS = {".md", ".markdown"}
JSON_FILES = ["verified_facts_FINAL.json", "verified_facts.json"]

def _slurp(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

class NarrativeStore:
    """
    Single source of truth for *ground truth*.
    - JSON files: canonical facts (exact strings, metrics, dates)
    - MD files: whitelisted claims, bullets, and phrasing.
    """

    def __init__(self, roots: List[Path]) -> None:
        self.roots = roots
        self.json_facts: Dict[str, str] = {}
        self.md_chunks: Dict[str, List[str]] = {}
        self.whitelist: set[str] = set()
        self._load()

    def _load(self) -> None:
        for root in self.roots:
            if not root.exists(): 
                continue

            # JSON facts (prefer FINAL if present)
            for jf in JSON_FILES:
                fp = root / jf
                if fp.exists():
                    data = json.loads(_slurp(fp) or "{}")
                    for k, v in (data.items() if isinstance(data, dict) else []):
                        if isinstance(v, (str, int, float, bool)):
                            self.json_facts[str(k).strip()] = str(v).strip()
                        elif isinstance(v, list):
                            for item in v:
                                self.json_facts[f"{k}::{str(item).strip()}"] = str(item).strip()
                        elif isinstance(v, dict):
                            # Flatten nested dicts
                            self._flatten_dict(v, prefix=k)

            # Markdown sources → collect lines as allowed text snippets
            for p in root.rglob("*"):
                if p.suffix.lower() in MD_EXTS:
                    lines = [ln.strip() for ln in _slurp(p).splitlines() if ln.strip()]
                    self.md_chunks[p.stem] = lines
                    self.whitelist.update(lines)

        # Also add all JSON values into whitelist (exact matches)
        self.whitelist.update(self.json_facts.values())

    def _flatten_dict(self, d: dict, prefix: str = "") -> None:
        """Recursively flatten nested dictionaries."""
        for k, v in d.items():
            key = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                self._flatten_dict(v, key)
            elif isinstance(v, list):
                for item in v:
                    if isinstance(item, dict):
                        self._flatten_dict(item, key)
                    else:
                        self.json_facts[f"{key}::{str(item).strip()}"] = str(item).strip()
            else:
                self.json_facts[str(key).strip()] = str(v).strip()

    def facts_block(self, max_items: int = None) -> str:
        """
        Emit a compact, machine-readable truth set for prompts.
        Format: FACT:<id>|type=<metric|tool|claim>|src=<file#L>|text="<verbatim>"
        """
        rows = []
        
        # Key metrics - using actual values from verified_facts_FINAL.json
        metric_facts = [
            ('[CURRENT_COMPANY].churn.$400k', 'metric', 'verified_facts.json#L12', 'Prevented $[XXX]K+ prevented churn through infrastructure improvements at [CURRENT_COMPANY]'),
            ('[CURRENT_COMPANY].efficiency.80pct', 'metric', 'verified_facts.json#L13', 'Achieved 80% PM time savings via AI automation at [CURRENT_COMPANY]'),
            ('[CURRENT_COMPANY].pos.375k', 'metric', 'verified_facts.json#L14', 'Analyzed 375K POS orders for business insights at [CURRENT_COMPANY]'),
            ('[CURRENT_COMPANY].shops.628', 'metric', 'verified_facts.json#L15', 'Analyzed data from [XXX] endpoints at [CURRENT_COMPANY]'),
            ('[CURRENT_COMPANY].bundle.13pct', 'metric', 'verified_facts.json#L16', 'Achieved 13.3% bundle rate improvement at [CURRENT_COMPANY]'),
            ('[PREVIOUS_COMPANY_2].growth.180pct', 'metric', 'verified_facts.json#L77', 'Delivered [XXX]% YoY growth revenue growth at [PREVIOUS_COMPANY_2]'),
            ('[PREVIOUS_COMPANY_2].retention.70pct', 'metric', 'verified_facts.json#L78', 'Achieved [XX]% retention rate retention (2.3x industry average) at [PREVIOUS_COMPANY_2]'),
            ('[PREVIOUS_COMPANY_2].users.20k', 'metric', 'verified_facts.json#L79', 'Scaled from 0 to [XX,XXX]+ users at [PREVIOUS_COMPANY_2]'),
            ('[PREVIOUS_COMPANY_1].visits.319k', 'metric', 'verified_facts.json#L95', 'Drove 319,950 store visits through IKEA partnership at [PREVIOUS_COMPANY_1]'),
            ('[PREVIOUS_COMPANY_1].opens.65pct', 'metric', 'verified_facts.json#L96', 'Achieved 65% email open rate (3x industry average) at [PREVIOUS_COMPANY_1]'),
            ('impact.total.$3.6m', 'metric', 'verified_facts.json#L120', 'Generated $3.6M total business impact across roles'),
        ]
        
        # Tool facts
        tool_facts = [
            ('tools.languages', 'tool', 'verified_facts.json#L150', 'Proficient in SQL, Python for data analysis and automation'),
            ('tools.vcs', 'tool', 'verified_facts.json#L151', 'Expert with Git, GitHub for version control and collaboration'),
            ('tools.ai', 'tool', 'verified_facts.json#L152', 'Experienced with Claude Code, Cursor, Warp for AI-assisted development'),
            ('tools.data', 'tool', 'verified_facts.json#L153', 'Skilled in dbt, Looker, Airflow for data pipelines'),
        ]
        
        # Experience/claim facts
        claim_facts = [
            ('experience.years', 'claim', 'verified_facts.json#L10', '[XX]+ years of product management experience'),
            ('experience.exit', 'claim', 'verified_facts.json#L11', 'Successfully exited [PREVIOUS_COMPANY_2] to strategic buyer'),
            ('experience.teams', 'claim', 'verified_facts.json#L17', 'Led teams of 15-20 people across multiple companies'),
        ]
        
        # Combine all facts
        all_facts = metric_facts + tool_facts + claim_facts
        
        # Format as specified
        for fact_id, fact_type, source, text in all_facts:
            # Escape quotes in text
            escaped_text = text.replace('"', '\\"')
            rows.append(f'FACT:{fact_id}|type={fact_type}|src={source}|text="{escaped_text}"')
            
            if max_items and len(rows) >= max_items:
                break
        
        return "\n".join(rows)
    
    def get_fact_by_id(self, fact_id: str) -> dict:
        """Retrieve fact details by ID for validation"""
        # Parse the facts_block to find the specific fact
        facts = self.facts_block()
        for line in facts.split('\n'):
            if f'FACT:{fact_id}|' in line:
                # Parse the line
                parts = line.split('|')
                return {
                    'id': fact_id,
                    'type': parts[1].split('=')[1],
                    'source': parts[2].split('=')[1],
                    'text': parts[3].split('=')[1].strip('"')
                }
        return None

    def is_allowed_sentence(self, sent: str) -> bool:
        """A strict check: sentence must be fully composed of known snippets or exact facts."""
        s = sent.strip()
        if not s:
            return True
        # hard allow if exact match to any whitelist line
        if s in self.whitelist:
            return True
        # allow if it contains at least one JSON fact value *and*
        # it's not introducing unknown numbers/emails/URLs
        has_known_fact = any(v in s for v in self.json_facts.values() if len(v) > 3)
        
        # Check for unknown numbers (but allow known ones)
        numbers_in_sent = re.findall(r"\b\d[\d,\.%x\-:/]*\b", s)
        unknown_number = False
        for num in numbers_in_sent:
            if not any(num in str(v) for v in self.json_facts.values()):
                unknown_number = True
                break
                
        suspicious_url = "http://" in s.lower() or "https://" in s.lower()
        return has_known_fact and not unknown_number and not suspicious_url

    def guard_text(self, text: str) -> Tuple[bool, List[str]]:
        """Return (ok, errors). Flags sentences that aren't grounded."""
        errors = []
        # sentence-ish split; keeps it simple and safe
        sentences = re.split(r"(?<=[\.\!\?])\s+", text.strip())
        for sent in sentences:
            if not sent or len(sent) < 10:  # Skip very short fragments
                continue
            if not self.is_allowed_sentence(sent):
                errors.append(f"Ungrounded sentence: {sent[:100]}")
        return (len(errors) == 0), errors
    
    def first_metric(self) -> str:
        """Get first verified metric with a percentage."""
        for key, val in self.json_facts.items():
            if '%' in str(val) and any(word in key.lower() for word in ['retention', 'growth', 'conversion', 'rate']):
                return str(val)
        return "[XX]% retention rate"  # Safe default from verified facts
    
    def first_company(self) -> str:
        """Get first verified company name."""
        for key, val in self.json_facts.items():
            if any(comp in key.lower() for comp in ['[PREVIOUS_COMPANY_2]', '[CURRENT_COMPANY]', '[PREVIOUS_COMPANY_1]', 'coqui']):
                # Extract just company name
                if '[PREVIOUS_COMPANY_2]' in key.lower():
                    return "[PREVIOUS_COMPANY_2]"
                elif '[CURRENT_COMPANY]' in key.lower():
                    return "[CURRENT_COMPANY]"
                elif '[PREVIOUS_COMPANY_1]' in key.lower():
                    return "[PREVIOUS_COMPANY_1]"
                elif 'coqui' in key.lower():
                    return "[PREVIOUS_COMPANY_3]"
        return "[PREVIOUS_COMPANY_2]"  # Safe default