#!/usr/bin/env python3
"""Test improved content generation with better formatting and voice."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.orchestrator import JobSearchOrchestrator


async def test_improved_content():
    """Test content generation with improved prompts."""

    orchestrator = JobSearchOrchestrator()

    # Real job description example (Senior PM role)
    job_description = """
    Senior Product Manager - Growth
    
    About the Role:
    We're looking for a Senior Product Manager to drive our growth initiatives through 
    data-driven experimentation and systematic optimization.
    
    What you'll do:
    • Lead cross-functional teams to drive user acquisition and retention
    • Design and execute A/B tests to optimize conversion funnels
    • Analyze user behavior data to identify growth opportunities
    • Partner with engineering to ship features that drive metrics
    • Build scalable systems for growth experimentation
    
    What we're looking for:
    • 7+ years of product management experience
    • Track record of driving growth through experimentation
    • Experience with B2B SaaS or marketplace products
    • Strong analytical skills and data-driven approach
    • Experience leading cross-functional teams
    • Proven ability to ship products that drive business metrics
    """

    print("\n" + "="*60)
    print("🎆 IMPROVED CONTENT GENERATION TEST")
    print("="*60)

    # Test job data
    job_data = {
        'job_id': 'test-improved-001',
        'url': 'https://example.com/senior-pm-growth',
        'company': 'TechGrowth Inc',
        'role': 'Senior Product Manager - Growth',
        'description': job_description
    }

    # Step 1: Score the job
    print("\n📊 Scoring Job...")
    scoring_result = await orchestrator.workflow_engine.agents['scoring_agent'].process({
        'job_data': job_data
    })
    
    print(f"✅ Score: {scoring_result.result.get('total_score', 0)}/100")

    # Step 2: Get positioning strategy
    print("\n🎯 Determining Positioning...")
    positioning_result = await orchestrator.workflow_engine.agents['positioning_agent'].process({
        'job_data': job_data,
        'scoring_result': scoring_result.result
    })
    
    print(f"✅ Strategy: {positioning_result.result.get('strategy_name')}")

    # Step 3: Generate content with improved prompts
    print("\n📝 Generating Content with Improved Format...")
    content_result = await orchestrator.workflow_engine.agents['content_agent'].process({
        'job_data': job_data,
        'scoring_result': scoring_result.result,
        'positioning_strategy': positioning_result.result
    })
    
    if content_result.success:
        print("✅ Content generated successfully!")
        
        # Display resume
        print("\n" + "="*60)
        print("📄 RESUME (First 1000 chars)")
        print("="*60)
        print(content_result.result['resume'][:1000])
        
        # Check for proper header format
        resume = content_result.result['resume']
        if "# **[YOUR_NAME]**" in resume:
            print("\n✅ Header format correct!")
        else:
            print("\n❌ Header format needs fixing")
            
        if "[YOUR_CITY, STATE] |" in resume and "[YOUR_EMAIL]" in resume:
            print("✅ Contact info formatted correctly!")
        else:
            print("❌ Contact info needs fixing")
            
        if "[START_DATE] - September 2025" in resume:
            print("✅ [CURRENT_COMPANY] dates correct (past tense)!")
        else:
            print("❌ [CURRENT_COMPANY] dates need fixing")
            
        # Display cover letter
        print("\n" + "="*60)
        print("💌 COVER LETTER (First 800 chars)")
        print("="*60)
        print(content_result.result['cover_letter'][:800])
        
        # Check cover letter format
        cover = content_result.result['cover_letter']
        if "Dear TechGrowth Inc Team" in cover:
            print("\n✅ Salutation correct!")
        else:
            print("\n❌ Salutation needs fixing")
            
        if "Best regards," in cover and "[YOUR_NAME]" in cover:
            print("✅ Signature format correct!")
        else:
            print("❌ Signature needs fixing")
            
        # Check for specific metrics
        print("\n📊 Content Quality Checks:")
        metrics_found = []
        for metric in ['$400K', '375K', '80%', '70%', '2.3x', '$3.6M', '47 A/B tests']:
            if metric in resume or metric in cover:
                metrics_found.append(metric)
        
        if metrics_found:
            print(f"✅ Specific metrics found: {', '.join(metrics_found)}")
        else:
            print("❌ No specific metrics found")
            
        # Check voice
        if "systematic" in cover.lower() or "discovered" in cover.lower():
            print("✅ Analytical voice present")
        else:
            print("❌ Missing analytical voice")
            
    else:
        print(f"❌ Content generation failed: {content_result.errors}")

    print("\n" + "="*60)
    print("✨ TEST COMPLETE")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(test_improved_content())