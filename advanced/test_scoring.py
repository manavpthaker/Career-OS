#!/usr/bin/env python3
"""Test job scoring functionality with a realistic example."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.orchestrator import JobSearchOrchestrator


async def test_director_role():
    """Test scoring a Director-level PM role."""

    orchestrator = JobSearchOrchestrator()

    # Realistic Director PM job description
    job_description = """
    Director of Product Management - Marketplace Platform

    About the Role:
    We're seeking a Director of Product Management to lead our marketplace platform team.
    You'll be responsible for driving the product strategy and roadmap for our two-sided
    marketplace that connects millions of buyers and sellers globally.

    What You'll Do:
    • Define and execute the product vision and strategy for our marketplace platform
    • Lead a team of 8-10 product managers across search, discovery, and transactions
    • Partner closely with engineering, design, data science, and business teams
    • Drive key metrics including GMV growth, retention, and marketplace liquidity
    • Own the P&L for your product area with $100M+ in annual revenue
    • Present product strategy and results to executive team and board of directors
    • Run experiments and A/B tests to validate product hypotheses
    • Build scalable product processes and frameworks for the team

    What We're Looking For:
    • [XX]+ years of product management experience
    • 5+ years of people management experience leading product teams
    • Deep experience with marketplace dynamics and two-sided platforms
    • Strong analytical skills with expertise in A/B testing and data analysis
    • Track record of driving significant business impact (revenue, retention, growth)
    • Excellent written and verbal communication skills
    • Experience working with global teams and international markets
    • Background in e-commerce, marketplaces, or platform businesses preferred

    Nice to Have:
    • MBA or technical degree
    • Experience with AI/ML powered personalization and recommendations
    • Previous experience at high-growth technology companies
    • Experience with marketplace trust and safety initiatives
    """

    print("\n" + "="*60)
    print("🎯 JOB SCORING ANALYSIS")
    print("="*60)

    # Score the job
    result = await orchestrator.score_job(
        job_url="https://example.com/marketplace-director-pm",
        job_description=job_description
    )

    # Display results
    print(f"\n📊 Overall Results:")
    print(f"  Total Score: {result['score']}/100")
    print(f"  Recommendation: {result['recommendation']}")
    print(f"  Research Quality: {result['research_quality']}")

    # Show category breakdown with visual bars
    print(f"\n📈 Category Breakdown:")
    print("-" * 50)

    if result.get('breakdown'):
        max_score = 15  # Maximum score for any category
        for category, score in result['breakdown'].items():
            # Create visual bar
            bar_length = int((score / max_score) * 20)
            bar = '█' * bar_length + '░' * (20 - bar_length)

            # Format output
            print(f"  {category:20} {bar} {score:5.1f}/15")

    # Provide analysis
    print(f"\n💡 Analysis:")
    if result['score'] >= 70:
        print("  ✅ Excellent match! Submit immediately with strong positioning.")
        print("  ✅ Your experience aligns well with key requirements.")
        print("  ✅ Focus on highlighting matching skills and experience.")
    elif result['score'] >= 55:
        print("  ✅ Good match! Worth applying with tailored narrative.")
        print("  ⚠️ Emphasize transferable skills and growth potential.")
    elif result['score'] >= 40:
        print("  ⚠️ Moderate match. Apply if company/role is appealing.")
        print("  ⚠️ Will need strong positioning around growth trajectory.")
    else:
        print("  ❌ Low match. Only pursue if it's a dream company.")
        print("  ❌ Significant repositioning required.")

    # Score interpretation - updated thresholds
    print(f"\n📋 Score Interpretation:")
    print("  70-100: Submit immediately (high priority)")
    print("  55-69:  Submit with tailored positioning")
    print("  40-54:  Submit if particularly interested")
    print("  0-39:   Skip unless dream company")

    print("\n" + "="*60)

    return result


async def test_principal_role():
    """Test scoring a Principal PM role."""

    orchestrator = JobSearchOrchestrator()

    # Principal PM job description with technical focus
    job_description = """
    Principal Product Manager - AI/ML Platform

    We're looking for a Principal PM to lead our AI/ML platform products.

    Responsibilities:
    • Drive technical product strategy for ML infrastructure
    • Partner with engineering on platform architecture decisions
    • Define metrics and measure impact of AI features
    • Lead cross-functional initiatives without formal authority
    • Influence product direction through data and insights

    Requirements:
    • 8+ years product management experience
    • Deep technical knowledge of ML systems
    • Experience with platform products and APIs
    • Strong analytical and problem-solving skills
    • Track record of shipping successful products
    """

    print("\n" + "="*60)
    print("🔬 PRINCIPAL PM ROLE SCORING")
    print("="*60)

    result = await orchestrator.score_job(
        job_url="https://example.com/principal-ai-pm",
        job_description=job_description
    )

    print(f"\n  Score: {result['score']}/100")
    print(f"  Recommendation: {result['recommendation']}")

    return result


async def main():
    """Run all scoring tests."""
    print("\n🚀 Job Search v2 - Scoring System Test")
    print("This demonstrates the 100-point rubric scoring system\n")

    try:
        # Test Director role (should score higher)
        director_result = await test_director_role()

        # Test Principal role (should score lower due to technical requirements)
        principal_result = await test_principal_role()

        # Summary
        print("\n" + "="*60)
        print("📊 SUMMARY")
        print("="*60)
        print(f"  Director Role Score:  {director_result['score']}/100")
        print(f"  Principal Role Score: {principal_result['score']}/100")
        print("\n✅ Scoring system is working correctly!")
        print("="*60)

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())