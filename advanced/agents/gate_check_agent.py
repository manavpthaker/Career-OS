"""
Gate Check Agent - Validates hard requirements before application generation.
"""

import re
from typing import Dict, Any, List, Tuple
from utils import get_logger
from .base_agent import BaseAgent, AgentResponse

logger = get_logger("gate_check_agent")

class GateCheckAgent(BaseAgent):
    """Agent that performs gate checks on job requirements vs candidate profile."""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("GateCheckAgent", config or {})

        # Load hard requirement patterns
        self.education_patterns = {
            'quantitative_bachelor': [
                r'bachelor.{0,100}degree.{0,50}in.{0,10}(a )?quantitative.{0,20}field',
                r'bachelor.{0,100}(statistics|economics|operations research|analytics|mathematics|computer science|computer engineering|software engineering|mechanical engineering|information systems)',
                r'b\.?[sa]\.?\s*(statistics|economics|operations research|analytics|mathematics|computer science|computer engineering|software engineering|mechanical engineering|information systems)',
                r'quantitative.{0,20}(bachelor|degree)',
                r'degree.{0,50}(statistics|economics|operations research|analytics|mathematics|computer science)',
            ],
            'any_masters': [
                r'master.{0,20}degree',
                r'm\.?[sa]\.?',
                r'mba'
            ],
            'hard_requirement_indicators': [
                r'required.{0,50}(bachelor|degree)',
                r'minimum.{0,50}(bachelor|degree)',
                r'must have.{0,50}(bachelor|degree)',
                r'bachelor.{0,20}required',
                r'degree.{0,20}required',
                r'bachelor.{0,10}degree',
                r'education.{0,50}requirement'
            ]
        }

        self.location_patterns = {
            'no_remote': [
                r'no remote',
                r'onsite only',
                r'in.office',
                r'must be located in',
                r'local candidates only'
            ],
            'specific_location': [
                r'must be in (.*?)[,\.]',
                r'located in (.*?)[,\.]',
                r'based in (.*?)[,\.]'
            ]
        }

        self.authorization_patterns = [
            r'no sponsorship',
            r'must be authorized to work',
            r'us citizen',
            r'green card',
            r'permanent resident'
        ]

        self.experience_patterns = [
            r'(\d+)\+?\s*years?.{0,50}(product management|pm|product manager)',
            r'minimum.{0,20}(\d+).{0,20}years',
            r'(\d+).{0,20}years.{0,20}experience'
        ]

    async def process(self, data: Dict[str, Any]) -> AgentResponse:
        """Perform gate checks on job requirements."""
        try:
            job_data = data['job_data']
            candidate_profile = data.get('candidate_profile', {})

            logger.info(f"Gate check started for {job_data.get('company')} - {job_data.get('role')}")

            # Extract requirements from JD
            jd_text = job_data.get('description', '').lower()

            gate_results = {
                'overall_status': 'PASS',
                'critical_failures': [],
                'warnings': [],
                'requirements_analysis': {},
                'recommendation': 'PROCEED'
            }

            # Check education requirements
            education_check = self._check_education_requirements(jd_text, candidate_profile)
            gate_results['requirements_analysis']['education'] = education_check

            if education_check['status'] == 'FAIL':
                gate_results['critical_failures'].append(education_check['message'])
                gate_results['overall_status'] = 'FAIL'
            elif education_check['status'] == 'WARNING':
                gate_results['warnings'].append(education_check['message'])

            # Check location requirements
            location_check = self._check_location_requirements(jd_text, candidate_profile)
            gate_results['requirements_analysis']['location'] = location_check

            if location_check['status'] == 'FAIL':
                gate_results['critical_failures'].append(location_check['message'])
                gate_results['overall_status'] = 'FAIL'
            elif location_check['status'] == 'WARNING':
                gate_results['warnings'].append(location_check['message'])

            # Check work authorization
            auth_check = self._check_work_authorization(jd_text, candidate_profile)
            gate_results['requirements_analysis']['work_authorization'] = auth_check

            if auth_check['status'] == 'FAIL':
                gate_results['critical_failures'].append(auth_check['message'])
                gate_results['overall_status'] = 'FAIL'

            # Check experience requirements
            experience_check = self._check_experience_requirements(jd_text, candidate_profile)
            gate_results['requirements_analysis']['experience'] = experience_check

            if experience_check['status'] == 'FAIL':
                gate_results['critical_failures'].append(experience_check['message'])
                gate_results['overall_status'] = 'FAIL'
            elif experience_check['status'] == 'WARNING':
                gate_results['warnings'].append(experience_check['message'])

            # Determine final recommendation
            if gate_results['overall_status'] == 'FAIL':
                gate_results['recommendation'] = 'DO_NOT_SUBMIT'
            elif len(gate_results['warnings']) > 2:
                gate_results['recommendation'] = 'SUBMIT_WITH_CAUTION'
            else:
                gate_results['recommendation'] = 'PROCEED'

            logger.info(f"Gate check completed: {gate_results['overall_status']} - {len(gate_results['critical_failures'])} failures, {len(gate_results['warnings'])} warnings")

            return AgentResponse(
                success=True,
                result=gate_results,
                metrics={
                    'gate_status': gate_results['overall_status'],
                    'critical_failures': len(gate_results['critical_failures']),
                    'warnings': len(gate_results['warnings'])
                }
            )

        except Exception as e:
            logger.error(f"Gate check failed: {str(e)}")
            return AgentResponse(
                success=False,
                result={},
                errors=[f"Gate check failed: {str(e)}"]
            )

    def _check_education_requirements(self, jd_text: str, profile: Dict) -> Dict[str, Any]:
        """Check if candidate meets education requirements."""

        # Check if there are hard education requirements
        has_hard_requirement = any(
            re.search(pattern, jd_text)
            for pattern in self.education_patterns['hard_requirement_indicators']
        )

        if not has_hard_requirement:
            return {
                'status': 'PASS',
                'message': 'No hard education requirements detected',
                'details': 'JD does not specify mandatory degree requirements'
            }

        # Check for quantitative bachelor requirement
        requires_quant_bachelor = any(
            re.search(pattern, jd_text)
            for pattern in self.education_patterns['quantitative_bachelor']
        )

        # Check for any master's degree alternative
        accepts_masters = any(
            re.search(pattern, jd_text)
            for pattern in self.education_patterns['any_masters']
        )

        # Get candidate's education
        candidate_education = profile.get('education', {})
        candidate_degree = candidate_education.get('degree', '').lower()
        candidate_field = candidate_education.get('field', '').lower()

        # Check if candidate meets requirements
        has_quant_bachelor = self._is_quantitative_field(candidate_field) and 'bachelor' in candidate_degree
        has_masters = 'master' in candidate_degree or 'mba' in candidate_degree

        if requires_quant_bachelor:
            if has_quant_bachelor or (accepts_masters and has_masters):
                return {
                    'status': 'PASS',
                    'message': 'Education requirements met',
                    'details': f'Candidate has {candidate_degree} in {candidate_field}'
                }
            else:
                return {
                    'status': 'FAIL',
                    'message': f'Education requirement not met: JD requires quantitative bachelor\'s degree, candidate has {candidate_degree} in {candidate_field}',
                    'details': 'This is typically a hard requirement for senior PM roles at large companies'
                }

        return {
            'status': 'PASS',
            'message': 'Education requirements appear flexible',
            'details': 'No specific quantitative field requirement detected'
        }

    def _is_quantitative_field(self, field: str) -> bool:
        """Check if education field is considered quantitative."""
        quant_fields = [
            'statistics', 'economics', 'mathematics', 'computer science',
            'engineering', 'physics', 'operations research', 'analytics',
            'information systems', 'finance', 'accounting', 'data science'
        ]

        return any(qfield in field for qfield in quant_fields)

    def _check_location_requirements(self, jd_text: str, profile: Dict) -> Dict[str, Any]:
        """Check location compatibility."""

        # Check for no remote work
        no_remote = any(
            re.search(pattern, jd_text)
            for pattern in self.location_patterns['no_remote']
        )

        candidate_location = profile.get('location', {})
        candidate_remote_ok = candidate_location.get('remote_ok', True)
        candidate_city = candidate_location.get('city', '')
        candidate_state = candidate_location.get('state', '')

        if no_remote and candidate_remote_ok:
            return {
                'status': 'WARNING',
                'message': 'Job may require onsite presence, candidate indicates remote preference',
                'details': 'Review specific location requirements carefully'
            }

        # Check for specific location requirements
        for pattern in self.location_patterns['specific_location']:
            match = re.search(pattern, jd_text)
            if match:
                required_location = match.group(1).strip()
                if candidate_city.lower() not in required_location.lower():
                    return {
                        'status': 'WARNING',
                        'message': f'Location mismatch: Job in {required_location}, candidate in {candidate_city}, {candidate_state}',
                        'details': 'Check if relocation or hybrid arrangements are acceptable'
                    }

        return {
            'status': 'PASS',
            'message': 'Location requirements compatible',
            'details': 'No location conflicts detected'
        }

    def _check_work_authorization(self, jd_text: str, profile: Dict) -> Dict[str, Any]:
        """Check work authorization requirements."""

        requires_auth = any(
            re.search(pattern, jd_text)
            for pattern in self.authorization_patterns
        )

        if requires_auth:
            candidate_auth = profile.get('work_authorization', {})
            is_authorized = candidate_auth.get('us_authorized', True)  # Assume true if not specified

            if not is_authorized:
                return {
                    'status': 'FAIL',
                    'message': 'Work authorization requirement not met',
                    'details': 'Job requires US work authorization, candidate may need sponsorship'
                }

        return {
            'status': 'PASS',
            'message': 'Work authorization compatible',
            'details': 'No authorization conflicts detected'
        }

    def _check_experience_requirements(self, jd_text: str, profile: Dict) -> Dict[str, Any]:
        """Check experience requirements."""

        # Extract years of experience required
        required_years = None
        for pattern in self.experience_patterns:
            match = re.search(pattern, jd_text)
            if match:
                required_years = int(match.group(1))
                break

        if required_years is None:
            return {
                'status': 'PASS',
                'message': 'No specific experience requirement detected',
                'details': 'Experience appears flexible'
            }

        candidate_years = profile.get('experience_years', 0)

        if candidate_years < required_years:
            gap = required_years - candidate_years
            if gap > 2:  # Significant gap
                return {
                    'status': 'FAIL',
                    'message': f'Experience gap: requires {required_years}+ years, candidate has {candidate_years} years',
                    'details': f'{gap} year gap may be too significant to overcome'
                }
            else:  # Small gap
                return {
                    'status': 'WARNING',
                    'message': f'Slight experience gap: requires {required_years}+ years, candidate has {candidate_years} years',
                    'details': f'{gap} year gap may be acceptable with strong domain experience'
                }

        return {
            'status': 'PASS',
            'message': f'Experience requirement met: {candidate_years} years >= {required_years} required',
            'details': 'Candidate exceeds minimum experience requirement'
        }