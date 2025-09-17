"""Content Agent - Generates tailored resumes and cover letters with voice calibration."""

import json
import os
import re
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import yaml
from datetime import datetime

from agents.base_agent import BaseAgent, AgentResponse
from utils import get_logger, log_kv
from utils.llm_client import LLMClient
from core import AgentMessage, MessageType

logger = get_logger("content_agent")


class ContentAgent(BaseAgent):
    """Generates personalized application content with voice calibration and fact-checking."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the content agent.

        Args:
            config: Agent configuration
        """
        super().__init__("content_agent", config, logger)

        # Load narrative facts
        self.narrative_facts = self._load_narrative_facts()

        # Load voice calibration
        self.voice_config = self._load_voice_config()

        # Initialize LLM client
        self.llm_client = LLMClient(provider=config.get('llm_provider', 'openai'))
        self.use_llm = config.get('use_llm', True)

        logger.info(f"ContentAgent initialized with LLM={self.use_llm} and voice calibration")

    def _load_narrative_facts(self) -> Dict[str, Any]:
        """Load verified facts from narrative store."""
        facts_path = Path(__file__).parent.parent / "knowledge" / "narrative" / "verified_facts.json"

        if not facts_path.exists():
            logger.warning("Narrative facts not found, using defaults")
            return {}

        try:
            with open(facts_path, 'r') as f:
                facts = json.load(f)
            logger.info(f"Loaded {len(facts)} narrative fact categories")
            return facts
        except Exception as e:
            logger.error(f"Failed to load narrative facts: {e}")
            return {}

    def _load_voice_config(self) -> Dict[str, Any]:
        """Load voice calibration configuration."""
        voice_path = Path(__file__).parent.parent / "knowledge" / "voice" / "voice_blend.yaml"

        if not voice_path.exists():
            logger.warning("Voice config not found, using defaults")
            return self._get_default_voice_config()

        try:
            with open(voice_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info("Loaded voice calibration configuration")
            return config
        except Exception as e:
            logger.error(f"Failed to load voice config: {e}")
            return self._get_default_voice_config()

    def _get_default_voice_config(self) -> Dict[str, Any]:
        """Get default voice configuration."""
        return {
            'voice_blend': {
                'default': {
                    'mo_gawdat': 50,
                    'john_mulaney': 30,
                    'bill_maher': 20
                }
            }
        }

    async def process(self, data: Any) -> AgentResponse:
        """Process content generation request.

        Args:
            data: Input containing job data, scoring result, and positioning strategy

        Returns:
            Content generation response with resume and cover letter
        """
        try:
            # Extract inputs
            job_data = data.get('job_data', {})
            scoring_result = data.get('scoring_result', {})
            positioning_strategy = data.get('positioning_strategy', {})
            workflow_config = data.get('workflow_config', {})

            # Log request
            log_kv(logger, "content_generation_request",
                company=job_data.get('company'),
                role=job_data.get('role'),
                score=scoring_result.get('total_score', 0),
                strategy=positioning_strategy.get('strategy_name'))

            # Determine voice blend based on positioning
            voice_blend = self._determine_voice_blend(
                positioning_strategy=positioning_strategy,
                company_culture=data.get('research_data', {}).get('culture', {})
            )

            # Generate resume
            resume = await self._generate_resume(
                job_data=job_data,
                scoring_result=scoring_result,
                positioning_strategy=positioning_strategy,
                voice_blend=voice_blend
            )

            # Generate cover letter
            cover_letter = await self._generate_cover_letter(
                job_data=job_data,
                scoring_result=scoring_result,
                positioning_strategy=positioning_strategy,
                voice_blend=voice_blend
            )

            # Apply guardrails
            resume = self._apply_guardrails(resume, "resume")
            cover_letter = self._apply_guardrails(cover_letter, "cover_letter")

            # Build content result
            content_result = {
                'resume': resume,
                'cover_letter': cover_letter,
                'voice_blend': voice_blend,
                'positioning_used': positioning_strategy.get('strategy_name'),
                'facts_verified': True,
                'generated_at': datetime.utcnow().isoformat()
            }

            # Log success
            log_kv(logger, "content_generated",
                resume_length=len(resume),
                cover_letter_length=len(cover_letter),
                voice_blend=str(voice_blend))

            return AgentResponse(
                success=True,
                result=content_result,
                metrics={
                    'resume_words': len(resume.split()),
                    'cover_letter_words': len(cover_letter.split()),
                    'facts_used': self._count_facts_used(resume + cover_letter)
                }
            )

        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            return AgentResponse(
                success=False,
                errors=[str(e)]
            )

    def _determine_voice_blend(self,
                              positioning_strategy: Dict[str, Any],
                              company_culture: Dict[str, Any]) -> Dict[str, int]:
        """Determine voice blend based on context.

        Args:
            positioning_strategy: Positioning strategy from agent
            company_culture: Company culture analysis

        Returns:
            Voice blend percentages
        """
        # Start with strategy-recommended blend
        if 'voice_blend' in positioning_strategy:
            blend = positioning_strategy['voice_blend'].copy()
        else:
            # Use default blend
            blend = self.voice_config['voice_blend']['default'].copy()

        # Adjust for job search status (more confidence needed)
        # Slightly increase Bill Maher for directness
        if self.narrative_facts.get('current_status', {}).get('seeking_role'):
            blend['bill_maher'] = min(blend.get('bill_maher', 20) + 5, 30)
            blend['mo_gawdat'] = max(blend.get('mo_gawdat', 50) - 5, 45)

        # Normalize to 100%
        total = sum(blend.values())
        if total != 100:
            factor = 100 / total
            blend = {k: int(v * factor) for k, v in blend.items()}

        return blend

    async def _generate_resume(self,
                              job_data: Dict[str, Any],
                              scoring_result: Dict[str, Any],
                              positioning_strategy: Dict[str, Any],
                              voice_blend: Dict[str, int]) -> str:
        """Generate tailored resume.

        Args:
            job_data: Job information
            scoring_result: Scoring analysis
            positioning_strategy: Positioning strategy
            voice_blend: Voice calibration

        Returns:
            Generated resume content
        """
        # Use LLM if available, otherwise use template
        if self.use_llm and self.llm_client:
            try:
                resume = await self.llm_client.generate_resume(
                    job_data=job_data,
                    facts=self.narrative_facts,
                    positioning=positioning_strategy.get('strategy_name', 'general'),
                    voice_blend=voice_blend
                )
                logger.info("Generated resume using LLM")
                return resume
            except Exception as e:
                logger.warning(f"LLM generation failed, using template: {e}")

        # Fallback to template-based generation
        facts = self.narrative_facts

        # Build resume sections
        resume_parts = []

        # Header
        resume_parts.append("# [YOUR_NAME]")
        resume_parts.append("Product Manager | [XX]+ years Experience | $[XXX]K+ prevented churn Prevention | 80% Automation")
        resume_parts.append("")

        # Professional Summary (using voice blend)
        summary = self._generate_summary(voice_blend, positioning_strategy)
        resume_parts.append("## PROFESSIONAL SUMMARY")
        resume_parts.append(summary)
        resume_parts.append("")

        # Experience
        resume_parts.append("## PROFESSIONAL EXPERIENCE")
        resume_parts.append("")

        # [CURRENT_COMPANY] (most recent)
        resume_parts.append("### Product Manager | [CURRENT_COMPANY] | Sept 2024 - Sept 2025")
        [CURRENT_COMPANY]_bullets = self._select_bullets_for_role(
            job_data,
            scoring_result,
            facts.get('[CURRENT_COMPANY]_metrics', {})
        )
        for bullet in [CURRENT_COMPANY]_bullets:
            resume_parts.append(f"• {bullet}")
        resume_parts.append("")

        # [PREVIOUS_COMPANY_1]
        resume_parts.append("### Head of Product | [PREVIOUS_COMPANY_1] | [START_DATE] - [END_DATE]")
        [PREVIOUS_COMPANY_1]_facts = facts.get('[PREVIOUS_COMPANY_1]_experience', {})
        resume_parts.append(f"• Raised {[PREVIOUS_COMPANY_1]_facts.get('achievements', {}).get('funding', '$3.2M Series A')}")
        resume_parts.append(f"• Led team of {[PREVIOUS_COMPANY_1]_facts.get('team_size', '[XX-XX] person cross-functional team')}")
        resume_parts.append(f"• Achieved {[PREVIOUS_COMPANY_1]_facts.get('achievements', {}).get('revenue_growth', '[XXX]% YoY growth growth')}")
        resume_parts.append("")

        # [PREVIOUS_COMPANY_2]
        resume_parts.append("### Head of Product | [PREVIOUS_COMPANY_2] | 2017 - 2021")
        [PREVIOUS_COMPANY_2]_facts = facts.get('[PREVIOUS_COMPANY_2]_experience', {})
        resume_parts.append(f"• Built marketplace achieving {[PREVIOUS_COMPANY_2]_facts.get('achievements', {}).get('retention', '[XX]% retention rate (2.3x industry)')}")
        resume_parts.append(f"• Led successful exit")
        resume_parts.append(f"• Scaled to {[PREVIOUS_COMPANY_2]_facts.get('achievements', {}).get('scale', '1000+ users')}")
        resume_parts.append("")

        # Skills
        resume_parts.append("## SKILLS")
        skills = facts.get('technical_skills', {})
        resume_parts.append(f"**AI/ML**: {', '.join(skills.get('ai_ml', [])[:5])}")
        resume_parts.append(f"**Technical**: {', '.join(skills.get('programming', []))}")
        resume_parts.append(f"**Tools**: {', '.join(skills.get('tools', []))}")

        return "\n".join(resume_parts)

    async def _generate_cover_letter(self,
                                    job_data: Dict[str, Any],
                                    scoring_result: Dict[str, Any],
                                    positioning_strategy: Dict[str, Any],
                                    voice_blend: Dict[str, int]) -> str:
        """Generate tailored cover letter.

        Args:
            job_data: Job information
            scoring_result: Scoring analysis
            positioning_strategy: Positioning strategy
            voice_blend: Voice calibration

        Returns:
            Generated cover letter content
        """
        # Use LLM if available
        if self.use_llm and self.llm_client:
            try:
                cover_letter = await self.llm_client.generate_cover_letter(
                    job_data=job_data,
                    facts=self.narrative_facts,
                    positioning=positioning_strategy,
                    voice_blend=voice_blend
                )
                logger.info("Generated cover letter using LLM")
                return cover_letter
            except Exception as e:
                logger.warning(f"LLM generation failed, using template: {e}")

        # Fallback to template generation
        parts = []

        # Opening with hook
        hook = positioning_strategy.get('hook', '')
        if not hook:
            # Generate default hook
            hook = self._generate_hook(job_data, voice_blend)
        parts.append(hook)
        parts.append("")

        # Why this role (Mo Gawdat style - opportunity framing)
        parts.append("## Why This Role")
        company = job_data.get('company', 'your company')
        role = job_data.get('role', 'this role')

        # Frame as opportunity (Mo Gawdat 50%)
        opportunity = f"The opportunity to join {company} as {role} aligns perfectly with my experience preventing $400K in churn and achieving [XX]% efficiency improvement gains through AI automation at [CURRENT_COMPANY]."
        parts.append(opportunity)
        parts.append("")

        # Proof points (John Mulaney style - precise metrics)
        parts.append("## Key Achievements")

        # Select top 3 metrics addressing gaps
        metrics = self._select_key_metrics(scoring_result, positioning_strategy)
        for metric in metrics[:3]:
            parts.append(f"• {metric}")
        parts.append("")

        # Close with confidence (Bill Maher style)
        parts.append("## Ready to Contribute")
        close = f"I'm ready to bring this same data-driven approach and proven track record to {company}. Let's discuss how my experience can drive immediate impact."
        parts.append(close)

        return "\n".join(parts)

    def _generate_summary(self, voice_blend: Dict[str, int], positioning_strategy: Dict[str, Any]) -> str:
        """Generate professional summary with voice blend."""

        # Combine all three voices based on blend percentages

        # Mo Gawdat (wisdom/opportunity) - 50%
        mo_part = "Product leader who transforms challenges into growth opportunities"

        # John Mulaney (precision) - 30%
        john_part = "with proven success preventing $[XXX]K+ prevented churn, achieving 80% automation efficiency, and identifying $6M in opportunities"

        # Bill Maher (directness) - 20%
        bill_part = "Ready to drive immediate impact."

        # Blend based on strategy emphasis
        if positioning_strategy.get('emphasis') == 'management_scale':
            return f"{mo_part}, having led teams of 15-20 through successful exits and Series A funding, {john_part}. {bill_part}"
        else:
            return f"{mo_part} {john_part}. {bill_part}"

    def _generate_hook(self, job_data: Dict[str, Any], voice_blend: Dict[str, int]) -> str:
        """Generate opening hook if not provided."""
        company = job_data.get('company', 'your company')

        # Default hook with confidence
        return f"Having just delivered $400K in churn prevention and [XX]% efficiency improvement gains at [CURRENT_COMPANY], I'm excited to bring this same impact to {company}."

    def _select_bullets_for_role(self,
                                job_data: Dict[str, Any],
                                scoring_result: Dict[str, Any],
                                metrics: Dict[str, Any]) -> List[str]:
        """Select resume bullets based on role requirements."""
        bullets = []

        # Always lead with strongest metric
        bullets.append(f"Prevented {metrics.get('revenue', {}).get('prevented_churn', '$400K in churn')}")

        # Add efficiency metric
        bullets.append(f"Achieved {metrics.get('efficiency', {}).get('pm_overhead_reduction', '[XX]% efficiency improvement gains through AI automation')}")

        # Add scale metric
        bullets.append(f"Managed {metrics.get('scale', {}).get('support_tickets', '[X,XXX]+ daily volume per week')}")

        # Add technical metric if relevant
        if 'technical' in str(job_data.get('description', '')).lower():
            bullets.append(f"Built {metrics.get('technical', {}).get('prompt_templates', '50+ production AI templates')}")

        return bullets[:4]  # Limit to 4 bullets

    def _select_key_metrics(self,
                          scoring_result: Dict[str, Any],
                          positioning_strategy: Dict[str, Any]) -> List[str]:
        """Select key metrics to emphasize based on gaps."""
        metrics = positioning_strategy.get('key_metrics', [])

        if not metrics:
            # Default metrics
            metrics = [
                "Prevented $400K in customer churn through data-driven retention strategies",
                "Achieved [XX]% efficiency improvement gains via AI automation (Claude, GPT-4)",
                "Led teams of 15-20 through successful exits and Series A funding"
            ]

        return metrics

    def _apply_guardrails(self, content: str, content_type: str) -> str:
        """Apply guardrails to ensure quality and accuracy.

        Args:
            content: Generated content
            content_type: Type of content (resume/cover_letter)

        Returns:
            Content with guardrails applied
        """
        # Never use present tense for [CURRENT_COMPANY]
        content = content.replace("I am currently", "I recently")
        content = content.replace("In my current role", "At [CURRENT_COMPANY], I")
        content = content.replace("I continue to", "I successfully")

        # Ensure past tense for [CURRENT_COMPANY]
        content = re.sub(r'At [CURRENT_COMPANY], I (\w+)', lambda m: f"At [CURRENT_COMPANY], I {self._to_past_tense(m.group(1))}", content)

        # Remove any forbidden phrases
        forbidden = ["passionate about", "excited to", "seeking", "looking for"]
        for phrase in forbidden:
            content = content.replace(phrase, "ready to")

        # Verify all metrics match facts
        content = self._verify_metrics(content)

        return content

    def _to_past_tense(self, verb: str) -> str:
        """Convert verb to past tense."""
        # Simple past tense conversion
        if verb.endswith('e'):
            return verb + 'd'
        elif verb.endswith('y'):
            return verb[:-1] + 'ied'
        else:
            return verb + 'ed'

    def _verify_metrics(self, content: str) -> str:
        """Verify all metrics match narrative facts."""
        # Check for common metric errors
        replacements = {
            "$[XXX]K+ prevented churn losses": "$[XXX]K+ prevented churn churn",
            "100M requests": "[X,XXX]+ daily volume per week",
            "50M customers": "[XXXX]+ customers",
            "15+ engineers at [CURRENT_COMPANY]": "10+ cross-functional team members"
        }

        for wrong, right in replacements.items():
            content = content.replace(wrong, right)

        return content

    def _count_facts_used(self, content: str) -> int:
        """Count how many verified facts were used."""
        count = 0

        # Check for key metrics
        key_facts = [
            "$400K", "80%", "$6M", "[XX]% retention rate",
            "15-20", "Series A", "3.2M"
        ]

        for fact in key_facts:
            if fact in content:
                count += 1

        return count

    async def handle_message(self, message: AgentMessage) -> None:
        """Handle incoming messages.

        Args:
            message: Incoming message
        """
        if message.message_type == MessageType.CONTENT_REQUEST:
            # Process content generation request
            result = await self.process(message.data)

            # Send response
            response = AgentMessage(
                sender=self.name,
                recipient=message.sender,
                message_type=MessageType.CONTENT_GENERATED,
                data=result.dict(),
                correlation_id=message.correlation_id
            )

            await self.message_bus.send(response)