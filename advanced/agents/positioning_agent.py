"""Strategic positioning agent - determines optimal narrative angle."""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import yaml

from agents.base_agent import BaseAgent, AgentResponse
from utils import get_logger, log_kv, NarrativeStore
from core import AgentMessage, MessageType

logger = get_logger("positioning_agent")


class PositioningAgent(BaseAgent):
    """Determines strategic positioning based on role, company, and industry."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the positioning agent.

        Args:
            config: Agent configuration
        """
        super().__init__("positioning_agent", config, logger)

        # Load positioning strategies
        self.strategies = self._load_strategies()
        self.voice_profiles = self._load_voice_profiles()

        # Initialize narrative store
        narrative_paths = [Path(p) for p in config.get("narrative_paths", ["knowledge/narrative"])]
        self.narrative_store = NarrativeStore(narrative_paths)

        logger.info(f"Loaded {len(self.strategies)} positioning strategies")

    def _load_strategies(self) -> Dict[str, Any]:
        """Load positioning strategies from knowledge base."""
        strategies_file = Path("knowledge/positioning/strategies.json")

        if not strategies_file.exists():
            logger.warning("Strategies file not found, using defaults")
            return {}

        try:
            with open(strategies_file, 'r') as f:
                data = json.load(f)
            return data.get('positioning_strategies', {})
        except Exception as e:
            logger.error(f"Failed to load strategies: {e}")
            return {}

    def _load_voice_profiles(self) -> Dict[str, Any]:
        """Load voice calibration profiles."""
        voice_file = Path("knowledge/voice/voice_blend.yaml")

        if not voice_file.exists():
            logger.warning("Voice profiles not found, using defaults")
            return self._get_default_voice_profiles()

        try:
            with open(voice_file, 'r') as f:
                data = yaml.safe_load(f)
            return data
        except Exception as e:
            logger.error(f"Failed to load voice profiles: {e}")
            return self._get_default_voice_profiles()

    def _get_default_voice_profiles(self) -> Dict[str, Any]:
        """Get default voice profiles if file not found."""
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
        """Process positioning request.

        Args:
            data: Input containing job data, research, and scoring

        Returns:
            Positioning strategy response
        """
        try:
            # Extract inputs
            job_data = data.get('job_data', {})
            research_data = data.get('research_data', {})
            scoring_result = data.get('scoring_result', {})
            workflow_config = data.get('workflow_config', {})

            # Log inputs
            log_kv(logger, "positioning_request",
                company=job_data.get('company'),
                role=job_data.get('role'),
                score=scoring_result.get('total_score', 0))

            # Determine positioning strategy
            strategy = await self._determine_strategy(
                job_data=job_data,
                research_data=research_data,
                scoring_result=scoring_result,
                workflow_config=workflow_config
            )

            # Select key metrics to emphasize
            key_metrics = self._select_key_metrics(
                strategy=strategy,
                scoring_result=scoring_result
            )

            # Identify gap mitigation strategies
            gap_strategies = self._identify_gap_mitigation(
                scoring_result=scoring_result,
                strategy=strategy
            )

            # Calibrate voice blend
            voice_blend = self._calibrate_voice(
                strategy=strategy,
                company_culture=research_data.get('culture', {})
            )

            # Create hook for opening
            hook = self._create_hook(
                strategy=strategy,
                company=job_data.get('company'),
                research_data=research_data
            )

            # Build positioning result
            positioning_result = {
                'strategy_name': strategy.get('primary_angle', 'general'),
                'key_metrics': key_metrics,
                'voice_blend': voice_blend,
                'hook': hook,
                'gap_mitigation': gap_strategies,
                'industry_language': strategy.get('industry_language', ''),
                'emphasis': self._determine_emphasis(job_data, scoring_result)
            }

            # Log result
            log_kv(logger, "positioning_determined",
                strategy=positioning_result['strategy_name'],
                voice_blend=str(voice_blend))

            return AgentResponse(
                success=True,
                result=positioning_result,
                metrics={
                    'strategy_selected': positioning_result['strategy_name'],
                    'metrics_count': len(key_metrics),
                    'gaps_identified': len(gap_strategies)
                }
            )

        except Exception as e:
            logger.error(f"Positioning failed: {e}")
            return AgentResponse(
                success=False,
                errors=[str(e)]
            )

    async def _determine_strategy(self,
                                 job_data: Dict[str, Any],
                                 research_data: Dict[str, Any],
                                 scoring_result: Dict[str, Any],
                                 workflow_config: Dict[str, Any]) -> Dict[str, Any]:
        """Determine optimal positioning strategy.

        Args:
            job_data: Job information
            research_data: Company research
            scoring_result: Scoring analysis
            workflow_config: Workflow configuration

        Returns:
            Selected positioning strategy
        """
        role = job_data.get('role', '').lower()
        company = job_data.get('company', '').lower()
        industry = research_data.get('industry', '').lower()

        # Check for exact match first
        role_type = self._classify_role(role)
        industry_type = self._classify_industry(industry, company)

        strategy_key = f"{role_type}_{industry_type}"

        if strategy_key in self.strategies:
            logger.info(f"Using exact strategy match: {strategy_key}")
            return self.strategies[strategy_key]

        # Try role-only match
        for key, strategy in self.strategies.items():
            if key.startswith(role_type):
                logger.info(f"Using role-based strategy: {key}")
                return strategy

        # Try industry-only match
        for key, strategy in self.strategies.items():
            if key.endswith(industry_type):
                logger.info(f"Using industry-based strategy: {key}")
                return strategy

        # Use default based on score - adjusted for career stage
        if scoring_result.get('total_score', 0) >= 70:
            return self.strategies.get('senior_marketplace', self._get_default_strategy())
        elif scoring_result.get('total_score', 0) >= 55:
            return self.strategies.get('senior_product', self._get_default_strategy())
        else:
            return self._get_growth_trajectory_strategy()

    def _classify_role(self, role: str) -> str:
        """Classify role into category."""
        role_lower = role.lower()

        if any(term in role_lower for term in ['director', 'vp', 'vice president', 'head']):
            return 'director'
        elif any(term in role_lower for term in ['principal', 'staff', 'lead']):
            return 'principal'
        else:
            return 'senior'

    def _classify_industry(self, industry: str, company: str) -> str:
        """Classify industry into category."""
        industry_lower = industry.lower()
        company_lower = company.lower()

        # Check specific companies first
        travel_companies = ['airbnb', 'booking', 'expedia', 'tripadvisor', 'kayak']
        if any(comp in company_lower for comp in travel_companies):
            return 'travel'

        marketplace_companies = ['etsy', 'ebay', 'amazon', 'doordash', 'uber', 'instacart']
        if any(comp in company_lower for comp in marketplace_companies):
            return 'marketplace'

        # Check industry keywords
        if any(term in industry_lower for term in ['travel', 'hospitality', 'hotel', 'airline']):
            return 'travel'
        elif any(term in industry_lower for term in ['marketplace', 'ecommerce', 'platform']):
            return 'marketplace'
        elif any(term in industry_lower for term in ['saas', 'b2b', 'enterprise', 'software']):
            return 'b2b_saas'
        elif any(term in industry_lower for term in ['ai', 'ml', 'artificial intelligence']):
            return 'ai_platform'
        else:
            return 'general'

    def _select_key_metrics(self,
                           strategy: Dict[str, Any],
                           scoring_result: Dict[str, Any]) -> List[str]:
        """Select key metrics to emphasize based on strategy and scoring.

        Args:
            strategy: Positioning strategy
            scoring_result: Scoring analysis

        Returns:
            List of key metrics to emphasize
        """
        # Start with strategy-recommended metrics
        metrics = strategy.get('key_metrics', []).copy()

        # Add high-scoring categories
        category_scores = scoring_result.get('category_breakdown', {})
        top_categories = sorted(
            category_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]

        # Map categories to metrics
        metric_map = {
            'outcomes_metrics': ['$[X.X]M+ impact', '[XXX]% YoY growth growth', '[XX]% retention rate'],
            'scope_seniority': ['50+ managed', '25+ built', '15-20 led'],
            'experimentation': ['47 A/B tests', 'data-driven decisions'],
            'domain_technical': ['AI/ML implementation', 'marketplace expertise']
        }

        for category, score in top_categories:
            if category in metric_map and score >= 4:
                for metric in metric_map[category]:
                    if metric not in metrics:
                        metrics.append(metric)

        # Limit to top 5 metrics
        return metrics[:5]

    def _identify_gap_mitigation(self,
                                scoring_result: Dict[str, Any],
                                strategy: Dict[str, Any]) -> List[Dict[str, str]]:
        """Identify strategies to mitigate scoring gaps.

        Args:
            scoring_result: Scoring analysis
            strategy: Positioning strategy

        Returns:
            List of gap mitigation strategies
        """
        gaps = []
        category_scores = scoring_result.get('category_breakdown', {})

        # Find low-scoring categories
        for category, score in category_scores.items():
            if score < 3:  # Below average
                mitigation = self._get_mitigation_for_category(category, strategy)
                if mitigation:
                    gaps.append({
                        'gap': category,
                        'score': score,
                        'mitigation': mitigation
                    })

        return gaps

    def _get_mitigation_for_category(self,
                                    category: str,
                                    strategy: Dict[str, Any]) -> str:
        """Get mitigation strategy for a low-scoring category."""
        mitigations = {
            'domain_technical': "Emphasize transferable skills and quick learning ability",
            'company_fit': "Show deep research and genuine interest in mission",
            'experimentation': "Highlight data-driven approach even without formal testing",
            'cross_functional': "Emphasize collaboration from management experience",
            'evidence_depth': "Reference portfolio and specific case studies"
        }

        # Check if strategy has specific mitigation
        strategy_mitigation = strategy.get('gap_mitigation')
        if strategy_mitigation and category in strategy_mitigation:
            return strategy_mitigation

        return mitigations.get(category, f"Address {category} through relevant experience")

    def _calibrate_voice(self,
                        strategy: Dict[str, Any],
                        company_culture: Dict[str, Any]) -> Dict[str, int]:
        """Calibrate voice blend based on strategy and culture.

        Args:
            strategy: Positioning strategy
            company_culture: Company culture analysis

        Returns:
            Voice blend percentages
        """
        # Start with strategy recommendation
        voice_blend = strategy.get('voice_blend', {}).copy()

        if not voice_blend:
            # Use default
            voice_blend = self.voice_profiles.get('voice_blend', {}).get('default', {
                'mo_gawdat': 50,
                'john_mulaney': 30,
                'bill_maher': 20
            })

        # Adjust based on company culture
        culture_keywords = company_culture.get('keywords', [])

        if any(term in culture_keywords for term in ['collaborative', 'inclusive', 'supportive']):
            # More wisdom, less directness
            voice_blend['mo_gawdat'] = min(voice_blend.get('mo_gawdat', 50) + 10, 70)
            voice_blend['bill_maher'] = max(voice_blend.get('bill_maher', 20) - 10, 10)

        elif any(term in culture_keywords for term in ['fast-paced', 'aggressive', 'results']):
            # More directness
            voice_blend['bill_maher'] = min(voice_blend.get('bill_maher', 20) + 10, 35)
            voice_blend['mo_gawdat'] = max(voice_blend.get('mo_gawdat', 50) - 5, 40)

        elif any(term in culture_keywords for term in ['technical', 'engineering', 'data']):
            # More precision
            voice_blend['john_mulaney'] = min(voice_blend.get('john_mulaney', 30) + 15, 50)
            voice_blend['mo_gawdat'] = max(voice_blend.get('mo_gawdat', 50) - 10, 35)

        # Normalize to 100%
        total = sum(voice_blend.values())
        if total != 100:
            factor = 100 / total
            voice_blend = {k: int(v * factor) for k, v in voice_blend.items()}

        return voice_blend

    def _create_hook(self,
                    strategy: Dict[str, Any],
                    company: str,
                    research_data: Dict[str, Any]) -> str:
        """Create a compelling hook for the application.

        Args:
            strategy: Positioning strategy
            company: Company name
            research_data: Company research

        Returns:
            Hook statement
        """
        # Use template if available
        template = strategy.get('hook_template', '')

        if template and '[Company]' in template:
            hook = template.replace('[Company]', company)

            # Add recent context if available
            recent_news = research_data.get('recent_news', '')
            if recent_news:
                hook = f"With {company}'s {recent_news}, " + hook[0].lower() + hook[1:]

            return hook

        # Generate default hook
        angle = strategy.get('primary_angle', 'product leadership')
        key_metric = strategy.get('key_metrics', ['[XX]+ years experience'])[0]

        return f"My experience {key_metric} uniquely positions me to drive {company}'s {angle} forward."

    def _determine_emphasis(self,
                           job_data: Dict[str, Any],
                           scoring_result: Dict[str, Any]) -> str:
        """Determine what to emphasize in the application."""
        role = job_data.get('role', '').lower()
        score = scoring_result.get('total_score', 0)

        if 'director' in role or 'vp' in role:
            return 'management_scale'
        elif score >= 85:
            return 'perfect_fit'
        elif score >= 70:
            return 'strategic_impact'
        else:
            return 'growth_potential'

    def _get_default_strategy(self) -> Dict[str, Any]:
        """Get default positioning strategy."""
        return {
            'primary_angle': 'experienced_product_leader',
            'key_metrics': ['$[X.X]M+ impact', '[X] years management', '[XX]% retention rate'],
            'voice_blend': {
                'mo_gawdat': 50,
                'john_mulaney': 30,
                'bill_maher': 20
            },
            'industry_language': 'product excellence, user focus, data-driven',
            'hook_template': "My track record of driving product transformation positions me to contribute immediately to [Company]'s growth.",
            'gap_mitigation': "Focus on transferable skills and learning agility"
        }

    def _get_growth_trajectory_strategy(self) -> Dict[str, Any]:
        """Get growth trajectory strategy for founder -> PM transition."""
        return {
            'primary_angle': 'founder_to_pm_growth',
            'key_metrics': ['Built 2 startups', '0→1 experience', 'Full product lifecycle'],
            'voice_blend': {
                'mo_gawdat': 40,
                'john_mulaney': 40,
                'bill_maher': 20
            },
            'industry_language': 'startup agility, rapid iteration, customer obsession, scrappy execution',
            'hook_template': "My founder experience building products from 0→1 brings unique perspective on rapid iteration and customer validation to [Company].",
            'gap_mitigation': "Leverage startup experience as strength, position as high-growth potential"
        }

    async def handle_message(self, message: AgentMessage) -> None:
        """Handle incoming messages.

        Args:
            message: Incoming message
        """
        if message.message_type == MessageType.POSITIONING_STRATEGY:
            # Process positioning request
            result = await self.process(message.data)

            # Send response
            response = AgentMessage(
                sender=self.name,
                recipient=message.sender,
                message_type=MessageType.POSITIONING_STRATEGY,
                data=result.dict(),
                correlation_id=message.correlation_id
            )

            await self.message_bus.send(response)