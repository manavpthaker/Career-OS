#!/usr/bin/env python3
"""Test content generation with ContentAgent."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.orchestrator import JobSearchOrchestrator


async def test_content_generation():
    """Test content generation for a job."""

    orchestrator = JobSearchOrchestrator()

    # Sample job description
    job_description = """
    Senior Product Manager - Consumer Products

    We're looking for a Senior Product Manager to lead our consumer product initiatives.

    What you'll do:
    • Define and execute product strategy
    • Lead cross-functional teams
    • Drive metrics and data-driven decisions
    • Ship products that delight users
    • Collaborate with engineering and design

    What we're looking for:
    • 5+ years of product management experience
    • Experience with consumer products
    • Strong analytical skills
    • Track record of shipping successful products
    • Excellent communication skills
    """

    print("\n" + "="*60)
    print("🚀 CONTENT GENERATION TEST")
    print("="*60)

    # First, score the job
    scoring_result = await orchestrator.score_job(
        job_url="https://example.com/senior-pm-consumer",
        job_description=job_description
    )

    print(f"\n📊 Job Score: {scoring_result['score']}/100")
    print(f"📋 Recommendation: {scoring_result['recommendation']}")

    # Now generate content using the agents directly
    job_data = {
        'job_id': 'test-001',
        'url': 'https://example.com/senior-pm-consumer',
        'company': 'Example Corp',
        'role': 'Senior Product Manager',
        'description': job_description
    }

    # Get positioning strategy
    positioning_result = await orchestrator.workflow_engine.agents['positioning_agent'].process({
        'job_data': job_data,
        'scoring_result': {
            'total_score': scoring_result['score'],
            'category_breakdown': scoring_result.get('breakdown', {}),
            'recommendation': scoring_result['recommendation']
        }
    })

    print(f"\n🎯 Positioning Strategy: {positioning_result.result.get('strategy_name')}")
    print(f"📢 Hook: {positioning_result.result.get('hook')[:100]}...")

    # Generate content
    content_result = await orchestrator.workflow_engine.agents['content_agent'].process({
        'job_data': job_data,
        'scoring_result': {
            'total_score': scoring_result['score'],
            'category_breakdown': scoring_result.get('breakdown', {})
        },
        'positioning_strategy': positioning_result.result
    })

    if content_result.success:
        print("\n✅ Content Generated Successfully!")

        print(f"\n📊 Voice Blend Used:")
        voice = content_result.result.get('voice_blend', {})
        for person, pct in voice.items():
            print(f"  • {person}: {pct}%")

        print(f"\n📄 RESUME PREVIEW:")
        print("-" * 40)
        resume_preview = content_result.result['resume'][:500]
        print(resume_preview + "...")

        print(f"\n💌 COVER LETTER PREVIEW:")
        print("-" * 40)
        cover_preview = content_result.result['cover_letter'][:500]
        print(cover_preview + "...")

        print(f"\n📈 Metrics:")
        print(f"  • Resume: {content_result.metrics['resume_words']} words")
        print(f"  • Cover Letter: {content_result.metrics['cover_letter_words']} words")
        print(f"  • Facts Used: {content_result.metrics['facts_used']}")
    else:
        print(f"\n❌ Content generation failed: {content_result.errors}")

    print("\n" + "="*60)


if __name__ == "__main__":
    asyncio.run(test_content_generation())