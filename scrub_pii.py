#!/usr/bin/env python3
"""
PII Scrubbing Script for Career-OS
Removes personal information and replaces with contextual placeholders.

Usage: python scrub_pii.py --source /path/to/job-search-v2 --output advanced/
"""

import argparse
import json
import re
import shutil
from pathlib import Path

# PII Replacement Patterns
PII_REPLACEMENTS = {
    # Personal identifiers
    r'Manav\s+Thaker': '[YOUR_NAME]',
    r'manav@mpthaker\.xyz': '[YOUR_EMAIL]',
    r'732-995-3007': '[YOUR_PHONE]',
    r'732\.995\.3007': '[YOUR_PHONE]',
    r'\(732\)\s*995-3007': '[YOUR_PHONE]',
    r'linkedin\.com/in/m?p?thaker': 'linkedin.com/in/[YOUR_LINKEDIN]',
    r'github\.com/m?p?thaker': 'github.com/[YOUR_GITHUB]',

    # Location
    r'Rahway,?\s*NJ': '[YOUR_CITY, STATE]',
    r'New Jersey': '[YOUR_STATE]',
    r'Mexico': '[LOCATION]',
    r'Yucatan Peninsula': '[LOCATION]',

    # Companies (preserve context where important)
    r'Lovingly(?!\s+(Series|B2B|marketplace))': '[CURRENT_COMPANY]',
    r'Panso(?!\s+(Hospitality|technology))': '[PREVIOUS_COMPANY_1]',
    r'Subziwalla(?!\s+(D2C|food))': '[PREVIOUS_COMPANY_2]',
    r'Coqui Coqui(?!\s+(Group|hospitality))': '[PREVIOUS_COMPANY_3]',

    # Specific metrics (preserve structure)
    r'\$3\.6M\+?(?:\s+(?:impact|value|delivered))': '$[X.X]M+ impact',
    r'\$400K\+?(?:\s+(?:prevented|churn|saved))': '$[XXX]K+ prevented churn',
    r'\$6M\+?(?:\s+(?:identified|ARR|opportunities))': '$[X]M+ ARR opportunities',
    r'\$500K\+?(?:\s+(?:ARR|potential))': '$[XXX]K+ ARR potential',
    r'80%\s+(?:reduction|efficiency|improvement)': '[XX]% efficiency improvement',
    r'70%\s+(?:retention|customer)': '[XX]% retention rate',
    r'180%\s+(?:YoY|growth)': '[XXX]% YoY growth',
    r'40%\s+(?:conversion|reduction)': '[XX]% improvement',
    r'65%\s+(?:open\s+rates)': '[XX]% open rates',
    r'35%\s+(?:improvement|reduction)': '[XX]% improvement',

    # Scale metrics
    r'1,?500\+?\s+(?:florists|local|artisan)': '[XXXX]+ customers',
    r'20,?000\+?\s+(?:active\s+)?users': '[XX,XXX]+ users',
    r'375,?000\s+transactions': '[XXX,XXX] transactions',
    r'50\+?\s+(?:employees|person)': '[XX]+ employees',
    r'15-20\s+person': '[XX-XX] person',
    r'1,?000\+?\s+(?:daily\s+orders|tickets)': '[X,XXX]+ daily volume',

    # Experience and time
    r'15\+?\s+years': '[XX]+ years',
    r'10\+?\s+years': '[XX]+ years',
    r'8\s+years\s+management': '[X] years management',
    r'September\s+2024': '[START_DATE]',
    r'July\s+2021': '[START_DATE]',
    r'April\s+2017': '[START_DATE]',
    r'June\s+2021': '[END_DATE]',
    r'June\s+2024': '[END_DATE]',
    r'October\s+2014': '[START_DATE]',
    r'October\s+2016': '[END_DATE]',

    # Compensation
    r'\$300K': '$[XXX]K',

    # Education
    r'Pace University': '[YOUR_UNIVERSITY]',
    r'B\.A\.\s+English Language & Literature': '[YOUR_DEGREE] in [YOUR_FIELD]',
    r'2007': '[GRADUATION_YEAR]',

    # Technical specifics that might be identifying
    r'628\s+(?:endpoints|shops)': '[XXX] endpoints',
    r'319,?950\s+customer\s+footfall': '[XXX,XXX] customer footfall',
    r'13\.3%\s+bundle\s+patterns': '[XX.X]% patterns identified',

    # Keep structure, anonymize specifics
    r'Series\s+B\s+(?:company|gift\s+marketplace)': '[FUNDING_STAGE] company',
    r'Seed\s+→\s+Series\s+A': '[EARLY_STAGE] → [GROWTH_STAGE]',
    r'\$3\.2M\s+raised': '$[X.X]M raised',
    r'\$2\.3M\s+annual': '$[X.X]M annual',
}

# Files to exclude from processing
EXCLUDE_PATTERNS = [
    '*.pyc',
    '__pycache__',
    '.git',
    '.DS_Store',
    '*.log',
    'node_modules',
    '.env',
    'venv',
    '*.pdf',
    '*.png',
    '*.jpg',
    '*.jpeg'
]

def main():
    """Main scrubbing function."""
    parser = argparse.ArgumentParser(description="Scrub PII from job search system")
    parser.add_argument("--source", required=True, help="Source directory (job-search-v2)")
    parser.add_argument("--output", default="advanced", help="Output directory")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed")

    args = parser.parse_args()

    source_path = Path(args.source)
    output_path = Path(args.output)

    if not source_path.exists():
        print(f"❌ Source directory not found: {source_path}")
        return

    print("🧹 Career-OS PII Scrubbing Tool")
    print("=" * 50)
    print(f"Source: {source_path}")
    print(f"Output: {output_path}")
    print(f"Mode: {'Dry run' if args.dry_run else 'Live execution'}")
    print()

    # Create output directory
    if not args.dry_run:
        output_path.mkdir(parents=True, exist_ok=True)

    # Process files
    processed_files = 0
    scrubbed_files = 0

    for file_path in source_path.rglob("*"):
        if file_path.is_file() and not should_exclude(file_path):
            processed_files += 1

            # Read file
            try:
                content = read_file(file_path)
                if content is None:
                    continue

                # Scrub PII
                original_content = content
                scrubbed_content = scrub_content(content, file_path)

                if scrubbed_content != original_content:
                    scrubbed_files += 1
                    print(f"🧹 Scrubbing: {file_path.relative_to(source_path)}")

                    if args.dry_run:
                        show_changes(original_content, scrubbed_content, file_path)
                    else:
                        # Write to output
                        output_file = output_path / file_path.relative_to(source_path)
                        output_file.parent.mkdir(parents=True, exist_ok=True)
                        write_file(output_file, scrubbed_content)
                else:
                    # Copy file unchanged
                    if not args.dry_run:
                        output_file = output_path / file_path.relative_to(source_path)
                        output_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(file_path, output_file)

            except Exception as e:
                print(f"⚠️  Error processing {file_path}: {e}")

    print(f"\n✅ Processing complete!")
    print(f"📊 Files processed: {processed_files}")
    print(f"🧹 Files scrubbed: {scrubbed_files}")

    if not args.dry_run:
        print(f"📁 Output directory: {output_path}")

        # Create README for advanced directory
        create_advanced_readme(output_path)

def should_exclude(file_path):
    """Check if file should be excluded from processing."""
    file_str = str(file_path)

    for pattern in EXCLUDE_PATTERNS:
        if pattern.replace('*', '') in file_str:
            return True

    return False

def read_file(file_path):
    """Read file content, handling encoding issues."""
    try:
        # Try UTF-8 first
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        try:
            # Try latin-1 as fallback
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
        except:
            # Skip binary files
            return None
    except:
        return None

def write_file(file_path, content):
    """Write file content."""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def scrub_content(content, file_path):
    """Scrub PII from content."""
    scrubbed = content

    # Apply all replacement patterns
    for pattern, replacement in PII_REPLACEMENTS.items():
        scrubbed = re.sub(pattern, replacement, scrubbed, flags=re.IGNORECASE)

    # File-specific scrubbing
    if file_path.name.endswith('.json'):
        scrubbed = scrub_json_specific(scrubbed)
    elif file_path.name.endswith('.yaml') or file_path.name.endswith('.yml'):
        scrubbed = scrub_yaml_specific(scrubbed)
    elif file_path.name.endswith('.md'):
        scrubbed = scrub_markdown_specific(scrubbed)

    return scrubbed

def scrub_json_specific(content):
    """JSON-specific scrubbing patterns."""
    patterns = {
        r'"name":\s*"Manav Thaker"': '"name": "[YOUR_NAME]"',
        r'"email":\s*"manav@mpthaker\.xyz"': '"email": "[YOUR_EMAIL]"',
        r'"phone":\s*"\(732\) 995-3007"': '"phone": "[YOUR_PHONE]"',
        r'"linkedin":\s*"linkedin\.com/in/mpthaker"': '"linkedin": "linkedin.com/in/[YOUR_LINKEDIN]"',
    }

    for pattern, replacement in patterns.items():
        content = re.sub(pattern, replacement, content)

    return content

def scrub_yaml_specific(content):
    """YAML-specific scrubbing patterns."""
    patterns = {
        r'name:\s*"?Manav Thaker"?': 'name: "[YOUR_NAME]"',
        r'email:\s*"?manav@mpthaker\.xyz"?': 'email: "[YOUR_EMAIL]"',
        r'location:\s*"?Rahway,?\s*NJ"?': 'location: "[YOUR_CITY, STATE]"',
    }

    for pattern, replacement in patterns.items():
        content = re.sub(pattern, replacement, content)

    return content

def scrub_markdown_specific(content):
    """Markdown-specific scrubbing patterns."""
    patterns = {
        r'# Manav Thaker': '# [YOUR_NAME]',
        r'\*\*Manav Thaker\*\*': '**[YOUR_NAME]**',
        r'Built by someone who': 'Built by a PM who',
        r'my 50\+ senior PM roles': '50+ senior PM applications',
    }

    for pattern, replacement in patterns.items():
        content = re.sub(pattern, replacement, content)

    return content

def show_changes(original, scrubbed, file_path):
    """Show what changes would be made in dry run mode."""
    if original != scrubbed:
        print(f"\n--- Changes for {file_path.name} ---")

        # Find first few differences
        original_lines = original.split('\n')
        scrubbed_lines = scrubbed.split('\n')

        changes_shown = 0
        for i, (orig, scrub) in enumerate(zip(original_lines, scrubbed_lines)):
            if orig != scrub and changes_shown < 3:
                print(f"Line {i+1}:")
                print(f"  Before: {orig[:100]}...")
                print(f"  After:  {scrub[:100]}...")
                changes_shown += 1

def create_advanced_readme(output_path):
    """Create README for advanced directory."""
    readme_content = """# Advanced Career-OS System

This directory contains the full 6-agent orchestrator system from job-search-v2, with all personal information scrubbed and replaced with placeholders.

## What's Here

This is the sophisticated automation system that includes:
- **6 Specialized Agents**: Research, Scoring, Positioning, Content, QA, Export
- **Advanced Workflows**: Role-specific application strategies
- **Dynamic Positioning**: Strategic narrative development
- **Quality Rubrics**: 100-point evaluation system
- **Batch Processing**: Multiple applications efficiently

## Setup Requirements

- Python 3.8+
- API keys for OpenAI, Anthropic, Tavily
- 2-4 hours setup time
- $20-45/month in API costs
- Intermediate Python skills

## Getting Started

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Set up your profile**:
   ```bash
   # Edit config/user_profile.yaml with your information
   # Update knowledge/narrative/verified_facts.json
   ```

4. **Test the system**:
   ```bash
   python run.py score --url "https://job-url.com"
   python run.py apply --url "https://job-url.com" --workflow director_level
   ```

## Key Files to Customize

- `config/user_profile.yaml` - Your personal information
- `knowledge/narrative/verified_facts.json` - Your achievements and metrics
- `config/positioning.yaml` - Strategic positioning preferences
- `config/workflows/` - Application workflow configurations

## Migration from Simple Mode

If you started with the simple prompts and want to upgrade:

1. Export your narrative from the simple system
2. Use the migration script to convert formats
3. Gradually enable advanced features

## Features

| Feature | Status | Description |
|---------|--------|-------------|
| Job Scraping | ✅ Stable | LinkedIn, company sites |
| Strategic Analysis | ✅ Stable | 6-agent job analysis |
| Resume Generation | ✅ Stable | Tailored with positioning |
| Cover Letters | ✅ Stable | Strategic narrative approach |
| Quality Scoring | ⚠️ Beta | 100-point rubric system |
| Batch Processing | ⚠️ Beta | Multiple applications |
| Google Drive Export | 🧪 Experimental | Auto-export applications |
| Application Tracking | 🧪 Experimental | Status monitoring |

## Architecture

The system uses a message bus architecture with 6 specialized agents:

1. **Research Agent** - Company intelligence gathering
2. **Scoring Agent** - Job fit evaluation (100-point rubric)
3. **Positioning Agent** - Strategic narrative development
4. **Content Agent** - Resume/cover letter generation
5. **QA Agent** - Quality validation and review
6. **Export Agent** - Google Drive integration and tracking

## Support

- Documentation: See individual agent README files
- Issues: Check logs/ directory for debugging
- Performance: Target <5 minutes end-to-end
- Quality: 85+ rubric score for tier 1 companies

## Ethics

- **Human Review Required**: Nothing auto-submits
- **Rate Limiting**: Respects website ToS
- **Data Privacy**: Everything stays local
- **Honest Positioning**: Uses your real achievements only

---

*This system represents the cutting edge of AI-assisted job searching while maintaining ethical standards and human oversight.*
"""

    with open(output_path / "README.md", "w") as f:
        f.write(readme_content)

if __name__ == "__main__":
    main()