"""Scoring agent - consolidates job evaluation and rubric scoring."""

import json
import re
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

from agents.base_agent import BaseAgent, AgentResponse
from utils import get_logger, log_kv
from core import AgentMessage, MessageType

logger = get_logger("scoring_agent")


class ScoringAgent(BaseAgent):
    """Consolidated scoring agent for job evaluation using 100-point rubric."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the scoring agent.

        Args:
            config: Agent configuration
        """
        super().__init__("scoring_agent", config, logger)

        # Load rubric
        self.rubric = self._load_rubric()
        self.user_profile = self._load_user_profile(config)

        logger.info(f"Loaded rubric with {len(self.rubric.get('categories', []))} categories")

    def _load_rubric(self) -> Dict[str, Any]:
        """Load scoring rubric from knowledge base."""
        rubric_file = Path("knowledge/rubrics/director_rubric.json")

        if not rubric_file.exists():
            logger.warning("Rubric file not found, using defaults")
            return self._get_default_rubric()

        try:
            with open(rubric_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load rubric: {e}")
            return self._get_default_rubric()

    def _load_user_profile(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Load user profile for scoring context."""
        return {
            'years_experience': 10,
            'years_management': 8,
            'max_team_size': 50,
            'has_exit': True,
            'key_metrics': {
                'financial_impact': '$3.6M',
                'retention': '70%',
                'growth': '[XXX]% YoY growth',
                'efficiency': '[XX]% efficiency improvement'
            },
            'domains': ['marketplace', 'hospitality', 'b2b_saas', 'ai/ml'],
            'location': '[YOUR_CITY, STATE]',
            'remote_preference': True,
            'target_comp': {'min': 250000, 'max': 450000}
        }

    async def process(self, data: Any) -> AgentResponse:
        """Process scoring request.

        Args:
            data: Input containing job data and research

        Returns:
            Scoring results response
        """
        try:
            job_data = data.get('job_data', {})
            research_data = data.get('research_data', {})
            jd_text = job_data.get('description', '')

            # Log request
            log_kv(logger, "scoring_request",
                company=job_data.get('company'),
                role=job_data.get('role'))

            # Extract requirements from JD
            requirements = self._extract_requirements(jd_text)

            # Score each category
            category_scores = {}
            total_score = 0

            for category in self.rubric.get('categories', []):
                score = self._score_category(
                    category=category,
                    jd_text=jd_text,
                    requirements=requirements,
                    research_data=research_data
                )
                category_scores[category['name']] = score
                total_score += score

            # Apply penalties
            penalties = self._calculate_penalties(jd_text, requirements)
            total_score -= sum(penalties.values())

            # Check gate conditions
            gate_failures = self._check_gates(job_data, requirements)

            # Generate recommendation
            recommendation = self._get_recommendation(total_score, gate_failures)

            # Identify top gaps
            top_gaps = self._identify_gaps(category_scores)

            # Build scoring result
            scoring_result = {
                'total_score': max(0, min(100, total_score)),  # Clamp to 0-100
                'category_breakdown': category_scores,
                'penalties': penalties,
                'gate_failures': gate_failures,
                'recommendation': recommendation,
                'top_gaps': top_gaps,
                'confidence': self._calculate_confidence(category_scores, requirements)
            }

            # Log result
            log_kv(logger, "scoring_complete",
                total_score=scoring_result['total_score'],
                recommendation=recommendation,
                gate_failures=len(gate_failures))

            return AgentResponse(
                success=True,
                result=scoring_result,
                metrics={
                    'total_score': scoring_result['total_score'],
                    'categories_scored': len(category_scores),
                    'penalties_applied': len(penalties),
                    'gates_passed': len(gate_failures) == 0
                }
            )

        except Exception as e:
            logger.error(f"Scoring failed: {e}")
            return AgentResponse(
                success=False,
                errors=[str(e)]
            )

    def _extract_requirements(self, jd_text: str) -> Dict[str, Any]:
        """Extract requirements from job description.

        Args:
            jd_text: Job description text

        Returns:
            Extracted requirements
        """
        requirements = {
            'years_required': None,
            'management_required': False,
            'technical_skills': [],
            'soft_skills': [],
            'nice_to_haves': [],
            'responsibilities': []
        }

        # Extract years of experience
        years_pattern = r'(\d+)\+?\s*years?\s*(?:of\s*)?experience'
        years_match = re.search(years_pattern, jd_text.lower())
        if years_match:
            requirements['years_required'] = int(years_match.group(1))

        # Check for management requirements
        management_patterns = [
            r'manage\s+team',
            r'lead\s+team',
            r'manage\s+\d+\+?\s*(?:people|engineers|pms)',
            r'people\s+management',
            r'team\s+leadership'
        ]
        for pattern in management_patterns:
            if re.search(pattern, jd_text.lower()):
                requirements['management_required'] = True
                break

        # Extract technical skills
        tech_keywords = ['python', 'sql', 'javascript', 'react', 'aws', 'gcp', 'kubernetes', 'api', 'microservices']
        for keyword in tech_keywords:
            if keyword in jd_text.lower():
                requirements['technical_skills'].append(keyword)

        # Extract sections
        sections = self._extract_sections(jd_text)
        if 'responsibilities' in sections:
            requirements['responsibilities'] = sections['responsibilities']
        if 'requirements' in sections:
            requirements['nice_to_haves'] = sections.get('nice_to_have', [])

        return requirements

    def _extract_sections(self, jd_text: str) -> Dict[str, List[str]]:
        """Extract sections from job description."""
        sections = {}
        current_section = None
        lines = jd_text.split('\n')

        section_headers = [
            'responsibilities', 'requirements', 'qualifications',
            'what you\'ll do', 'what we\'re looking for', 'nice to have'
        ]

        for line in lines:
            line_lower = line.lower().strip()

            # Check if this is a section header
            for header in section_headers:
                if header in line_lower and len(line) < 100:
                    current_section = header.replace(' ', '_').replace('\'', '')
                    sections[current_section] = []
                    break

            # Add content to current section
            if current_section and line.strip() and line.strip() != line_lower:
                sections[current_section].append(line.strip())

        return sections

    def _score_category(self,
                       category: Dict[str, Any],
                       jd_text: str,
                       requirements: Dict[str, Any],
                       research_data: Dict[str, Any]) -> float:
        """Score a single category.

        Args:
            category: Category configuration
            jd_text: Job description text
            requirements: Extracted requirements
            research_data: Company research

        Returns:
            Category score
        """
        category_name = category['name']
        weight = category['weight']
        keywords = category.get('keywords', [])

        # Count keyword matches
        keyword_matches = sum(1 for kw in keywords if kw in jd_text.lower())
        keyword_ratio = keyword_matches / len(keywords) if keywords else 0

        # Category-specific scoring logic
        if category_name == 'Role Alignment':
            score = self._score_role_alignment(jd_text, requirements)
        elif category_name == 'Outcomes & Metrics':
            score = self._score_outcomes(jd_text)
        elif category_name == 'Scope & Seniority':
            score = self._score_scope(jd_text, requirements)
        elif category_name == 'Experimentation':
            score = self._score_experimentation(jd_text)
        elif category_name == 'Product Sense':
            score = self._score_product_sense(jd_text)
        elif category_name == 'Cross-functional':
            score = self._score_cross_functional(jd_text)
        elif category_name == 'Domain/Technical':
            score = self._score_domain_technical(jd_text, requirements, research_data)
        elif category_name == 'Communication':
            score = self._score_communication(jd_text)
        elif category_name == 'Company Fit':
            score = self._score_company_fit(research_data)
        elif category_name == 'Evidence Depth':
            score = 2.5  # Default to middle score
        else:
            score = keyword_ratio * weight * 0.5

        # Apply weight and cap at category maximum
        return min(score, weight)

    def _score_role_alignment(self, jd_text: str, requirements: Dict[str, Any]) -> float:
        """Score role alignment (15 points max)."""
        jd_lower = jd_text.lower()
        score = 0

        # Check title alignment - very inclusive scoring
        if any(term in jd_lower for term in ['principal', 'staff', 'senior product manager', 'sr. product manager']):
            score += 8  # Great match
        elif any(term in jd_lower for term in ['director', 'head', 'vp', 'vice president']):
            score += 7  # Also great
        elif 'product manager' in jd_lower:
            score += 7  # Standard PM roles are perfectly valid targets
        else:
            score += 3

        # Check leadership/ownership keywords - broader set
        leadership_keywords = ['strategy', 'vision', 'roadmap', 'own', 'drive', 'lead', 'initiative',
                              'ship', 'build', 'define', 'collaborate', 'analyze', 'track']
        keyword_count = sum(1 for kw in leadership_keywords if kw in jd_lower)
        score += min(keyword_count * 2, 8)  # More generous scoring

        return min(score, 15)

    def _score_outcomes(self, jd_text: str) -> float:
        """Score outcomes & metrics focus (15 points max)."""
        jd_lower = jd_text.lower()
        score = 0

        # Check for metrics keywords
        metrics_keywords = ['metrics', 'kpi', 'roi', 'growth', 'retention', 'revenue', 'conversion']
        if any(kw in jd_lower for kw in metrics_keywords):
            score += 7

        # Check for quantified requirements
        if re.search(r'\d+%', jd_text):
            score += 4

        # Check for results orientation
        if any(term in jd_lower for term in ['results', 'impact', 'outcomes', 'deliver']):
            score += 4

        return min(score, 15)

    def _score_scope(self, jd_text: str, requirements: Dict[str, Any]) -> float:
        """Score scope & seniority (12 points max)."""
        jd_lower = jd_text.lower()
        score = 5  # Base score for any PM role (they all have scope)

        # Management is a plus but not required
        if requirements.get('management_required'):
            score += 2

        # Any ownership language gets credit
        ownership_keywords = ['own', 'drive', 'lead', 'responsible', 'accountable', 'deliver',
                             'ship', 'launch', 'build', 'define']
        if any(kw in jd_lower for kw in ownership_keywords):
            score += 3

        # Check for team collaboration (almost always present)
        if any(term in jd_lower for term in ['collaborate', 'work with', 'partner', 'team', 'cross-functional']):
            score += 3

        # Any mention of impact
        if any(term in jd_lower for term in ['impact', 'results', 'success', 'growth']):
            score += 2

        return min(score, 12)

    def _score_experimentation(self, jd_text: str) -> float:
        """Score experimentation focus (10 points max)."""
        jd_lower = jd_text.lower()
        score = 3  # Base score - we have data-driven experience

        exp_keywords = ['a/b test', 'experiment', 'hypothesis', 'data', 'analytics', 'testing',
                       'metrics', 'measure', 'analyze', 'insights']
        keyword_count = sum(1 for kw in exp_keywords if kw in jd_lower)
        score += keyword_count * 1.5

        return min(score, 10)

    def _score_product_sense(self, jd_text: str) -> float:
        """Score product sense requirements (8 points max)."""
        jd_lower = jd_text.lower()
        score = 3  # Base score - we have product sense from Senior PM role

        product_keywords = ['user', 'customer', 'experience', 'discovery', 'validation',
                          'journey', 'needs', 'feedback', 'research', 'design']
        keyword_count = sum(1 for kw in product_keywords if kw in jd_lower)
        score += keyword_count

        return min(score, 8)

    def _score_cross_functional(self, jd_text: str) -> float:
        """Score cross-functional requirements (10 points max)."""
        jd_lower = jd_text.lower()
        score = 0

        xfn_keywords = ['cross-functional', 'collaborate', 'partner', 'engineering', 'design', 'sales', 'marketing']
        keyword_count = sum(1 for kw in xfn_keywords if kw in jd_lower)
        score = keyword_count * 2

        return min(score, 10)

    def _score_domain_technical(self,
                               jd_text: str,
                               requirements: Dict[str, Any],
                               research_data: Dict[str, Any]) -> float:
        """Score domain/technical fit (10 points max)."""
        jd_lower = jd_text.lower()
        industry_lower = research_data.get('industry', '').lower()
        score = 4  # Base score - most PM roles are transferable

        # Strong domain matches (direct experience from [CURRENT_COMPANY]/startups)
        strong_domains = ['marketplace', 'ecommerce', 'e-commerce', 'gifting', 'florist',
                         'b2b2c', 'grocery', 'delivery', 'social']
        if any(domain in industry_lower or domain in jd_lower for domain in strong_domains):
            score += 3

        # Consumer product experience is highly relevant
        consumer_keywords = ['consumer', 'user', 'customer', 'delight', 'experience', 'engagement']
        if any(kw in jd_lower for kw in consumer_keywords):
            score += 2

        # Any product without deep specialization is fine
        no_specialization = not any(term in jd_lower for term in ['blockchain', 'crypto', 'medical device',
                                                                   'pharma', 'defense', 'aerospace'])
        if no_specialization:
            score += 1

        return min(score, 10)

    def _score_communication(self, jd_text: str) -> float:
        """Score communication requirements (8 points max)."""
        jd_lower = jd_text.lower()
        score = 3  # Base score - all PMs need communication skills

        comm_keywords = ['communicate', 'communication', 'present', 'stakeholder', 'collaborate',
                        'work with', 'partner', 'written', 'verbal', 'team', 'cross-functional']
        keyword_count = sum(1 for kw in comm_keywords if kw in jd_lower)
        score += keyword_count

        # Bonus for executive communication
        if any(term in jd_lower for term in ['board', 'c-suite', 'executive']):
            score += 1

        return min(score, 8)

    def _score_company_fit(self, research_data: Dict[str, Any]) -> float:
        """Score company fit (7 points max)."""
        # More generous base score - we can adapt to most companies
        score = 4

        # Bonus for having research data
        if research_data.get('culture'):
            score += 2
        elif research_data.get('mission'):
            score += 1

        return min(score, 7)

    def _calculate_penalties(self, jd_text: str, requirements: Dict[str, Any]) -> Dict[str, int]:
        """Calculate penalties based on rubric rules.

        Args:
            jd_text: Job description text
            requirements: Extracted requirements

        Returns:
            Dictionary of penalties
        """
        penalties = {}

        # Check for vague AI claims
        if 'ai' in jd_text.lower() and not any(term in jd_text.lower() for term in ['implement', 'deploy', 'production']):
            penalties['vague_ai'] = 5

        # Check for tool soup
        tool_count = sum(1 for tool in ['jira', 'confluence', 'slack', 'notion', 'asana'] if tool in jd_text.lower())
        if tool_count > 3:
            penalties['tool_soup'] = 5

        # Check for lack of cross-functional
        if not any(term in jd_text.lower() for term in ['cross-functional', 'collaborate', 'partner']):
            penalties['no_cross_functional'] = 7

        return penalties

    def _check_gates(self, job_data: Dict[str, Any], requirements: Dict[str, Any]) -> List[str]:
        """Check gate conditions that would disqualify the application.

        Args:
            job_data: Job information
            requirements: Extracted requirements

        Returns:
            List of gate failures
        """
        failures = []

        # Location check
        location = job_data.get('location', '').lower()
        if location and not any(term in location for term in ['remote', 'hybrid', 'new york', 'ny', 'nyc', '[YOUR_STATE]', 'nj']):
            failures.append('Location outside 90-minute NYC radius')

        # Compensation check (if available)
        comp = job_data.get('compensation', {})
        if isinstance(comp, dict) and comp.get('max', float('inf')) < 250000:
            failures.append('Compensation below target range')

        # Skills gap check
        if 'hands-on coding' in job_data.get('description', '').lower():
            failures.append('Requires hands-on coding')

        return failures

    def _get_recommendation(self, total_score: float, gate_failures: List[str]) -> str:
        """Get application recommendation based on score and gates.

        Args:
            total_score: Total rubric score
            gate_failures: List of gate failures

        Returns:
            Recommendation string
        """
        if gate_failures:
            return f"Caution - Failed gates: {', '.join(gate_failures)}"

        # Adjusted thresholds for career stage
        if total_score >= 70:
            return "Submit immediately (high priority)"
        elif total_score >= 55:
            return "Submit with tailored positioning"
        elif total_score >= 40:
            return "Submit if particularly interested"
        else:
            return "Skip unless dream company"

    def _identify_gaps(self, category_scores: Dict[str, float]) -> List[Dict[str, Any]]:
        """Identify top gaps to address.

        Args:
            category_scores: Scores by category

        Returns:
            List of top gaps
        """
        gaps = []

        # Find categories with low scores relative to their weight
        for category in self.rubric.get('categories', []):
            name = category['name']
            weight = category['weight']
            score = category_scores.get(name, 0)

            if score < weight * 0.5:  # Less than 50% of possible
                gaps.append({
                    'category': name,
                    'score': score,
                    'possible': weight,
                    'gap': weight - score
                })

        # Sort by gap size and return top 3
        gaps.sort(key=lambda x: x['gap'], reverse=True)
        return gaps[:3]

    def _calculate_confidence(self,
                             category_scores: Dict[str, float],
                             requirements: Dict[str, Any]) -> float:
        """Calculate confidence in the scoring.

        Args:
            category_scores: Scores by category
            requirements: Extracted requirements

        Returns:
            Confidence score (0-1)
        """
        confidence = 0.5  # Base confidence

        # Higher confidence if we extracted clear requirements
        if requirements.get('years_required'):
            confidence += 0.1
        if requirements.get('responsibilities'):
            confidence += 0.1
        if requirements.get('technical_skills'):
            confidence += 0.1

        # Higher confidence if scoring is consistent
        scores = list(category_scores.values())
        if scores:
            variance = sum((s - sum(scores)/len(scores))**2 for s in scores) / len(scores)
            if variance < 10:
                confidence += 0.2

        return min(confidence, 1.0)

    def _get_default_rubric(self) -> Dict[str, Any]:
        """Get default rubric if file not found."""
        return {
            'name': 'Default Rubric',
            'total_points': 100,
            'categories': [
                {'name': 'Role Alignment', 'weight': 15},
                {'name': 'Outcomes & Metrics', 'weight': 15},
                {'name': 'Scope & Seniority', 'weight': 12},
                {'name': 'Experimentation', 'weight': 10},
                {'name': 'Product Sense', 'weight': 8},
                {'name': 'Cross-functional', 'weight': 10},
                {'name': 'Domain/Technical', 'weight': 10},
                {'name': 'Communication', 'weight': 8},
                {'name': 'Company Fit', 'weight': 7},
                {'name': 'Evidence Depth', 'weight': 5}
            ],
            'penalties': [],
            'gate_checks': []
        }

    async def handle_message(self, message: AgentMessage) -> None:
        """Handle incoming messages.

        Args:
            message: Incoming message
        """
        if message.message_type == MessageType.SCORING_RESULT:
            # Process scoring request
            result = await self.process(message.data)

            # Send response
            response = AgentMessage(
                sender=self.name,
                recipient=message.sender,
                message_type=MessageType.SCORING_RESULT,
                data=result.dict(),
                correlation_id=message.correlation_id
            )

            await self.message_bus.send(response)