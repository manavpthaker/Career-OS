"""Research agent - consolidates company intelligence gathering."""

import asyncio
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import hashlib

from agents.base_agent import BaseAgent, AgentResponse
from utils import get_logger, log_kv
from core import AgentMessage, MessageType

logger = get_logger("research_agent")


class ResearchAgent(BaseAgent):
    """Consolidated research agent for company and role intelligence."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the research agent.

        Args:
            config: Agent configuration
        """
        super().__init__("research_agent", config, logger)

        # Cache configuration
        self.cache_ttl = timedelta(hours=config.get('cache_ttl_hours', 24))
        self.research_cache: Dict[str, Any] = {}

        # API configurations (will be loaded from env)
        self.tavily_api_key = config.get('tavily_api_key')
        self.enable_web_search = config.get('enable_web_search', True)

        logger.info("Research Agent initialized with caching enabled")

    async def process(self, data: Any) -> AgentResponse:
        """Process research request.

        Args:
            data: Input containing job data

        Returns:
            Research results response
        """
        try:
            job_data = data.get('job_data', {})
            company = job_data.get('company', '')
            role = job_data.get('role', '')
            url = job_data.get('url', '')

            # Log request
            log_kv(logger, "research_request",
                company=company,
                role=role,
                url=url)

            # Check cache first
            cache_key = self._get_cache_key(company, role)
            cached_result = self._get_cached_research(cache_key)
            if cached_result:
                logger.info(f"Using cached research for {company}")
                return AgentResponse(
                    success=True,
                    result=cached_result,
                    metrics={'cache_hit': True, 'sources': len(cached_result.get('sources', []))}
                )

            # Perform parallel research
            research_tasks = []

            # Company intelligence
            research_tasks.append(self._research_company(company, role))

            # Industry analysis
            research_tasks.append(self._research_industry(company))

            # Recent news and announcements
            if self.enable_web_search:
                research_tasks.append(self._search_recent_news(company))

            # Culture and values
            research_tasks.append(self._research_culture(company))

            # Execute all research in parallel
            results = await asyncio.gather(*research_tasks, return_exceptions=True)

            # Combine results
            research_data = self._combine_research_results(results, company, role)

            # Cache the result
            self._cache_research(cache_key, research_data)

            # Log success
            log_kv(logger, "research_complete",
                company=company,
                sources_found=len(research_data.get('sources', [])),
                has_recent_news=bool(research_data.get('recent_news')))

            return AgentResponse(
                success=True,
                result=research_data,
                metrics={
                    'cache_hit': False,
                    'sources': len(research_data.get('sources', [])),
                    'has_culture_data': bool(research_data.get('culture')),
                    'has_recent_news': bool(research_data.get('recent_news'))
                }
            )

        except Exception as e:
            logger.error(f"Research failed: {e}")
            return AgentResponse(
                success=False,
                errors=[str(e)]
            )

    async def _research_company(self, company: str, role: str) -> Dict[str, Any]:
        """Research company information.

        Args:
            company: Company name
            role: Role title

        Returns:
            Company research data
        """
        try:
            # This would integrate with actual APIs in production
            # For now, returning structured mock data based on known companies

            company_lower = company.lower()

            # Known company profiles (from v1 knowledge)
            if 'airbnb' in company_lower:
                return {
                    'company': 'Airbnb',
                    'industry': 'Travel & Hospitality',
                    'stage': 'Public',
                    'size': '5000+',
                    'mission': 'Create a world where anyone can belong anywhere',
                    'focus_areas': ['Guest experience', 'Host success', 'Global expansion'],
                    'tech_stack': ['React', 'Ruby on Rails', 'AWS', 'Kubernetes'],
                    'recent_initiatives': ['AI-powered search', 'Host passport program', 'Categories expansion']
                }
            elif 'etsy' in company_lower:
                return {
                    'company': 'Etsy',
                    'industry': 'E-commerce Marketplace',
                    'stage': 'Public',
                    'size': '2000+',
                    'mission': 'Keep commerce human',
                    'focus_areas': ['Seller empowerment', 'Buyer discovery', 'Sustainable commerce'],
                    'tech_stack': ['PHP', 'React', 'MySQL', 'Google Cloud'],
                    'recent_initiatives': ['AI recommendations', 'Seller tools', 'International expansion']
                }
            elif 'stripe' in company_lower:
                return {
                    'company': 'Stripe',
                    'industry': 'FinTech/Payments',
                    'stage': 'Private',
                    'size': '7000+',
                    'mission': 'Increase the GDP of the internet',
                    'focus_areas': ['Developer experience', 'Global payments', 'Platform economy'],
                    'tech_stack': ['Ruby', 'Go', 'JavaScript', 'AWS'],
                    'recent_initiatives': ['Stripe Apps', 'Revenue recognition', 'Climate commitment']
                }
            else:
                # Generic company research
                return {
                    'company': company,
                    'industry': 'Technology',
                    'stage': 'Growth',
                    'size': '100-500',
                    'mission': f'Transform {role.split()[-1].lower()} through innovation',
                    'focus_areas': ['Product excellence', 'Customer success', 'Growth'],
                    'tech_stack': ['Modern stack'],
                    'recent_initiatives': ['Digital transformation', 'AI adoption']
                }

        except Exception as e:
            logger.error(f"Company research failed: {e}")
            return {}

    async def _research_industry(self, company: str) -> Dict[str, Any]:
        """Research industry context.

        Args:
            company: Company name

        Returns:
            Industry research data
        """
        try:
            company_lower = company.lower()

            # Industry mapping
            if any(term in company_lower for term in ['airbnb', 'booking', 'expedia', 'tripadvisor']):
                return {
                    'industry': 'Travel & Hospitality',
                    'market_size': '$1.9T global travel market',
                    'growth_rate': '7.5% CAGR',
                    'key_trends': ['Experiential travel', 'Digital nomads', 'Sustainable tourism'],
                    'competitors': ['Booking.com', 'Expedia', 'VRBO'],
                    'challenges': ['Regulation', 'Trust & safety', 'Post-pandemic recovery']
                }
            elif any(term in company_lower for term in ['etsy', 'ebay', 'amazon', 'shopify']):
                return {
                    'industry': 'E-commerce Marketplace',
                    'market_size': '$5.5T global e-commerce',
                    'growth_rate': '9.7% CAGR',
                    'key_trends': ['Social commerce', 'Creator economy', 'Personalization'],
                    'competitors': ['Amazon Handmade', 'eBay', 'Facebook Marketplace'],
                    'challenges': ['CAC growth', 'Platform differentiation', 'Seller retention']
                }
            elif any(term in company_lower for term in ['stripe', 'square', 'paypal', 'adyen']):
                return {
                    'industry': 'FinTech/Payments',
                    'market_size': '$8.9T payment processing',
                    'growth_rate': '11.2% CAGR',
                    'key_trends': ['Embedded finance', 'Crypto payments', 'B2B payments'],
                    'competitors': ['Square', 'PayPal', 'Adyen'],
                    'challenges': ['Regulation', 'Fraud prevention', 'Global expansion']
                }
            else:
                return {
                    'industry': 'Technology',
                    'market_size': 'Growing',
                    'growth_rate': 'Double-digit',
                    'key_trends': ['AI adoption', 'Digital transformation'],
                    'competitors': ['Various'],
                    'challenges': ['Talent acquisition', 'Innovation pace']
                }

        except Exception as e:
            logger.error(f"Industry research failed: {e}")
            return {}

    async def _search_recent_news(self, company: str) -> Dict[str, Any]:
        """Search for recent company news.

        Args:
            company: Company name

        Returns:
            Recent news data
        """
        try:
            # In production, this would use Tavily API
            # For now, return structured example

            return {
                'recent_news': [
                    {
                        'date': '2024-11-01',
                        'headline': f'{company} announces new product features',
                        'summary': 'Expansion of core platform capabilities',
                        'relevance': 'Product innovation focus'
                    },
                    {
                        'date': '2024-10-15',
                        'headline': f'{company} reports strong Q3 results',
                        'summary': 'Revenue growth exceeds expectations',
                        'relevance': 'Financial stability and growth'
                    }
                ],
                'key_announcements': [
                    'Recent funding round',
                    'New executive hires',
                    'Product launches'
                ]
            }

        except Exception as e:
            logger.error(f"News search failed: {e}")
            return {}

    async def _research_culture(self, company: str) -> Dict[str, Any]:
        """Research company culture and values.

        Args:
            company: Company name

        Returns:
            Culture research data
        """
        try:
            company_lower = company.lower()

            # Culture profiles for known companies
            if 'airbnb' in company_lower:
                return {
                    'culture': {
                        'values': ['Belong anywhere', 'Champion the mission', 'Be a host'],
                        'keywords': ['belonging', 'community', 'hospitality', 'global', 'inclusive'],
                        'work_style': 'Flexible, remote-friendly, collaborative',
                        'leadership_style': 'Mission-driven, data-informed, design-thinking',
                        'employee_sentiment': 'Strong mission alignment, focus on impact'
                    }
                }
            elif 'etsy' in company_lower:
                return {
                    'culture': {
                        'values': ['Keep commerce human', 'Commitment to craft', 'Sustainable practice'],
                        'keywords': ['human', 'creative', 'sustainable', 'authentic', 'community'],
                        'work_style': 'Creative, autonomous, impact-focused',
                        'leadership_style': 'Empowering, transparent, values-driven',
                        'employee_sentiment': 'Purpose-driven, creative freedom'
                    }
                }
            else:
                return {
                    'culture': {
                        'values': ['Innovation', 'Customer focus', 'Excellence'],
                        'keywords': ['collaborative', 'innovative', 'fast-paced', 'data-driven'],
                        'work_style': 'Collaborative and results-oriented',
                        'leadership_style': 'Strategic and empowering',
                        'employee_sentiment': 'Growth-oriented'
                    }
                }

        except Exception as e:
            logger.error(f"Culture research failed: {e}")
            return {}

    def _combine_research_results(self,
                                 results: List[Any],
                                 company: str,
                                 role: str) -> Dict[str, Any]:
        """Combine research results from multiple sources.

        Args:
            results: List of research results
            company: Company name
            role: Role title

        Returns:
            Combined research data
        """
        combined = {
            'company': company,
            'role': role,
            'researched_at': datetime.utcnow().isoformat(),
            'sources': []
        }

        for result in results:
            if isinstance(result, Exception):
                logger.warning(f"Research task failed: {result}")
                continue

            if result:
                combined.update(result)
                if 'source' in result:
                    combined['sources'].append(result['source'])

        # Add research quality indicator
        combined['research_quality'] = self._assess_research_quality(combined)

        return combined

    def _assess_research_quality(self, research_data: Dict[str, Any]) -> str:
        """Assess the quality of research data.

        Args:
            research_data: Combined research data

        Returns:
            Quality assessment (high/medium/low)
        """
        quality_score = 0

        if research_data.get('industry'):
            quality_score += 2
        if research_data.get('culture'):
            quality_score += 2
        if research_data.get('recent_news'):
            quality_score += 3
        if research_data.get('tech_stack'):
            quality_score += 1
        if research_data.get('focus_areas'):
            quality_score += 2

        if quality_score >= 8:
            return 'high'
        elif quality_score >= 5:
            return 'medium'
        else:
            return 'low'

    def _get_cache_key(self, company: str, role: str) -> str:
        """Generate cache key for research.

        Args:
            company: Company name
            role: Role title

        Returns:
            Cache key
        """
        content = f"{company.lower()}:{role.lower()}"
        return hashlib.md5(content.encode()).hexdigest()

    def _get_cached_research(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached research if available and not expired.

        Args:
            cache_key: Cache key

        Returns:
            Cached research or None
        """
        if cache_key not in self.research_cache:
            return None

        cached = self.research_cache[cache_key]
        cached_time = datetime.fromisoformat(cached['researched_at'])

        if datetime.utcnow() - cached_time > self.cache_ttl:
            # Cache expired
            del self.research_cache[cache_key]
            return None

        return cached

    def _cache_research(self, cache_key: str, research_data: Dict[str, Any]) -> None:
        """Cache research data.

        Args:
            cache_key: Cache key
            research_data: Research data to cache
        """
        self.research_cache[cache_key] = research_data
        logger.debug(f"Cached research for key: {cache_key}")

    async def handle_message(self, message: AgentMessage) -> None:
        """Handle incoming messages.

        Args:
            message: Incoming message
        """
        if message.message_type == MessageType.COMPANY_INTEL:
            # Process research request
            result = await self.process(message.data)

            # Send response
            response = AgentMessage(
                sender=self.name,
                recipient=message.sender,
                message_type=MessageType.COMPANY_INTEL,
                data=result.dict(),
                correlation_id=message.correlation_id
            )

            await self.message_bus.send(response)