#!/usr/bin/env python3
"""Quick test of gate check functionality."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from agents.gate_check_agent import GateCheckAgent
import yaml

async def test_gate_check():
    """Test gate check detection."""

    gate_agent = GateCheckAgent()

    # Load candidate profile
    with open('config/candidate_profile.yaml', 'r') as f:
        candidate_data = yaml.safe_load(f)
        candidate_profile = candidate_data['candidate_profile']

    # Test job with explicit quantitative degree requirement
    job_description = """
    Senior Manager, Product Manager, Generative AI Tooling - Capital One

    What we're looking for:
    • 5+ years of product management experience
    • Bachelor's Degree in a quantitative field (Statistics, Economics, Operations Research, Analytics, Mathematics, Computer Science, Computer Engineering, Software Engineering, Mechanical Engineering, Information Systems, or related field) OR Master's Degree in a quantitative field or MBA
    • Strong technical background
    """

    job_data = {
        'company': 'Capital One',
        'role': 'Senior Manager, Product Manager - Generative AI Tooling',
        'description': job_description
    }

    print("Testing Gate Check System")
    print("=" * 50)
    print(f"Candidate Education: {candidate_profile['education']['degree']} in {candidate_profile['education']['field']}")
    print(f"Job Requirement: Bachelor's in quantitative field")
    print()

    gate_result = await gate_agent.process({
        'job_data': job_data,
        'candidate_profile': candidate_profile
    })

    print("Gate Check Results:")
    print(f"Status: {gate_result.result['overall_status']}")
    print(f"Recommendation: {gate_result.result['recommendation']}")

    if gate_result.result['critical_failures']:
        print("\nCritical Failures:")
        for failure in gate_result.result['critical_failures']:
            print(f"  • {failure}")

    if gate_result.result['warnings']:
        print("\nWarnings:")
        for warning in gate_result.result['warnings']:
            print(f"  • {warning}")

    print("\nDetailed Analysis:")
    for req_type, analysis in gate_result.result['requirements_analysis'].items():
        status_emoji = "✅" if analysis['status'] == 'PASS' else "⚠️" if analysis['status'] == 'WARNING' else "❌"
        print(f"  {status_emoji} {req_type}: {analysis['message']}")
        print(f"    Details: {analysis['details']}")

if __name__ == "__main__":
    asyncio.run(test_gate_check())