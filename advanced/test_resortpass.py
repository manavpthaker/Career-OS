#!/usr/bin/env python3
"""Test content generation for ResortPass Lead Product Manager role."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.orchestrator import JobSearchOrchestrator


async def test_resortpass():
    """Test content generation for ResortPass job."""

    orchestrator = JobSearchOrchestrator()

    # ResortPass Lead Product Manager - New Ventures job description
    job_description = """
    Lead Product Manager, New Ventures — ResortPass
    
    About the Role:
    As Lead Product Manager - New Ventures, you will be responsible for launching new ResortPass categories, 
    starting with Spa. Within a category, you will oversee the end-to-end product across both sides of the 
    ResortPass marketplace. You will enable guests to benefit from unique experiences that help them recharge, 
    and hotels to unlock new revenue streams and optimize their operations.
    
    What You'll Do:
    • Collaborate closely with engineers, designers, marketers, and cross-functional teams to bring new categories to market
    • Own the category strategy, roadmap, execution of product features across both sides of the marketplace
    • Deeply understand our customers via qualitative interviews and quantitative analyses
    • Drive and be accountable for the revenue and engagement metrics for a ResortPass category
    
    Your Experience:
    • 5+ years of product management experience delivering complex products from concept to launch
    • Experience building 0 to 1 products within a high performing marketplace product function
    • Ability to conduct direct user interviews and build product features that address their needs
    • Deeply quantitative and able to deconstruct a funnel, and define and calibrate target metrics
    • Skilled at operating as a cross-functional leader in situations with high levels of ambiguity
    • Mastery of data and product tools including JIRA, Amplitude, Looker, etc.
    
    Bonus points:
    • Deep knowledge of SQL
    • Entrepreneurial experience
    • Experience in travel or marketplace products
    
    Company: ResortPass has partnered with over 1,800 leading hotels including Ritz-Carlton, Four Seasons. 
    Connected over 3 million people with luxury experiences. Fresh off Series B $30M raise.
    
    Location: NYC (On-site)
    Salary: $185K-$210K + equity
    """

    print("\n" + "="*80)
    print("🏖️  RESORTPASS - LEAD PRODUCT MANAGER, NEW VENTURES")
    print("="*80)

    # Job data
    job_data = {
        'job_id': 'resortpass-001',
        'url': 'https://partners.resortpass.com/careers?gh_jid=4772238007',
        'company': 'ResortPass',
        'role': 'Lead Product Manager - New Ventures',
        'description': job_description
    }

    # Step 1: Score the job
    print("\n📊 SCORING JOB...")
    scoring_result = await orchestrator.workflow_engine.agents['scoring_agent'].process({
        'job_data': job_data
    })
    
    score = scoring_result.result.get('total_score', 0)
    print(f"✅ Score: {score}/100")
    print(f"📋 Recommendation: {scoring_result.result.get('recommendation')}")
    print(f"\n📈 Score Breakdown:")
    for category, cat_score in sorted(scoring_result.result.get('category_breakdown', {}).items(), 
                                      key=lambda x: x[1], reverse=True)[:5]:
        print(f"  • {category}: {cat_score:.1f}")

    # Step 2: Get positioning strategy
    print("\n🎯 DETERMINING POSITIONING...")
    positioning_result = await orchestrator.workflow_engine.agents['positioning_agent'].process({
        'job_data': job_data,
        'scoring_result': scoring_result.result
    })
    
    print(f"✅ Strategy: {positioning_result.result.get('strategy_name')}")
    print(f"📢 Hook: {positioning_result.result.get('hook')[:100]}...")

    # Step 3: Generate content
    print("\n📝 GENERATING TAILORED APPLICATION...")
    content_result = await orchestrator.workflow_engine.agents['content_agent'].process({
        'job_data': job_data,
        'scoring_result': scoring_result.result,
        'positioning_strategy': positioning_result.result
    })
    
    if content_result.success:
        print("✅ Content generated successfully!")
        
        # Export to local files
        print("\n💾 EXPORTING APPLICATION...")
        export_result = await orchestrator.workflow_engine.agents['export_agent'].process({
            'job_data': job_data,
            'content_result': content_result.result,
            'scoring_result': scoring_result.result,
            'positioning_strategy': positioning_result.result
        })
        
        if export_result.success:
            print(f"✅ Exported to: {export_result.result.get('folder')}")
        
        # Display resume preview
        print("\n" + "="*80)
        print("📄 RESUME PREVIEW")
        print("="*80)
        resume = content_result.result['resume']
        print(resume[:1200])
        
        # Display cover letter preview
        print("\n" + "="*80)
        print("💌 COVER LETTER PREVIEW")
        print("="*80)
        cover = content_result.result['cover_letter']
        print(cover[:1000])
        
        # Quality checks
        print("\n" + "="*80)
        print("✨ QUALITY CHECKS")
        print("="*80)
        
        # Check for key ResortPass-relevant metrics
        marketplace_metrics = ['[XX]% retention rate', '2.3x industry', '20K+ users', '47 A/B tests', 
                               '[XXX]% YoY growth', '$3.6M', '375K transactions']
        found_metrics = [m for m in marketplace_metrics if m in resume or m in cover]
        
        print(f"\n📊 Marketplace Metrics Found: {', '.join(found_metrics) if found_metrics else 'None'}")
        
        # Check for 0-to-1 positioning
        if "0" in resume or "zero" in cover.lower() or "built" in resume.lower():
            print("✅ 0-to-1 experience highlighted")
        else:
            print("⚠️  Consider emphasizing 0-to-1 experience more")
            
        # Check for marketplace experience
        if "marketplace" in resume.lower() or "marketplace" in cover.lower():
            print("✅ Marketplace experience mentioned")
        else:
            print("⚠️  Marketplace experience should be highlighted")
            
        # Check for cross-functional leadership
        if "cross-functional" in resume or "cross-functional" in cover:
            print("✅ Cross-functional leadership emphasized")
        else:
            print("⚠️  Add cross-functional leadership emphasis")
            
    else:
        print(f"❌ Content generation failed: {content_result.errors}")

    print("\n" + "="*80)
    print("🏖️  APPLICATION COMPLETE FOR RESORTPASS")
    print("="*80)
    print(f"\n📍 Location requirement: NYC (You have: [YOUR_CITY, STATE] - Open to NYC hybrid ≥25%)")
    print(f"💰 Salary range: $185K-$210K (Your floor: $[XXX]K - may need to address)")
    print(f"🎯 Key match: Marketplace experience, 0-to-1 products, cross-functional leadership")


if __name__ == "__main__":
    asyncio.run(test_resortpass())