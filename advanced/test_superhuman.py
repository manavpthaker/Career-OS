#!/usr/bin/env python3
"""Test content generation for Superhuman Senior Growth Product Manager role."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.orchestrator import JobSearchOrchestrator


async def test_superhuman():
    """Test content generation for Superhuman job."""

    orchestrator = JobSearchOrchestrator()

    # Superhuman Senior Growth Product Manager job description
    job_description = """
    Senior Growth Product Manager - Superhuman
    
    About the Role:
    We're looking for a Senior Growth Product Manager to drive sustainable growth across the customer lifecycle.
    Superhuman has recently joined forces with Grammarly to revolutionize how professionals work.
    
    What you'll do:
    • Drive Product-Led Growth (PLG) strategy across the entire customer journey
    • Optimize conversion funnels from acquisition to retention
    • Lead experimentation and A/B testing to improve key metrics
    • Partner cross-functionally with engineering, analytics, and customer teams
    • Define and track growth metrics that matter
    • Identify and prioritize growth opportunities through data analysis
    
    What we're looking for:
    • 3+ years experience in growth product management
    • B2B SaaS or product-led environment experience
    • Proven track record in PLG or self-serve models
    • Strong analytical and data skills
    • Ability to design and interpret A/B tests
    • Cross-functional leadership skills
    • AI enthusiasm and experience
    
    Company: Superhuman - The fastest email experience ever made. We've redefined email for professionals
    who want to be more productive and happier at work.
    
    Location: Remote (US/Canada)
    Salary: $172k-$237k (SF/NY/Seattle), $155k-$214k (Other US)
    """

    print("\n" + "="*80)
    print("⚡ SUPERHUMAN - SENIOR GROWTH PRODUCT MANAGER")
    print("="*80)

    # Job data
    job_data = {
        'job_id': 'superhuman-001',
        'url': 'https://jobs.ashbyhq.com/superhuman/7fca4e94-0d4c-4286-a40b-815343968ea4',
        'company': 'Superhuman',
        'role': 'Senior Growth Product Manager',
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
        print(resume[:1500])
        
        # Display cover letter preview
        print("\n" + "="*80)
        print("💌 COVER LETTER PREVIEW")
        print("="*80)
        cover = content_result.result['cover_letter']
        print(cover[:1200])
        
        # Quality checks specific to Superhuman
        print("\n" + "="*80)
        print("✨ QUALITY CHECKS FOR SUPERHUMAN")
        print("="*80)
        
        # Check for growth/experimentation metrics
        growth_metrics = ['47 A/B tests', '[XXX]% YoY growth', '[XX]% retention rate', '100:1 LTV/CAC', 
                         '12% MoM', '[XX]% efficiency improvement', '375K transactions']
        found_metrics = [m for m in growth_metrics if m in resume or m in cover]
        
        print(f"\n📊 Growth Metrics Found: {', '.join(found_metrics) if found_metrics else 'None'}")
        
        # Check for PLG/SaaS experience
        if "saas" in resume.lower() or "b2b" in resume.lower():
            print("✅ B2B SaaS experience highlighted")
        else:
            print("⚠️  Should emphasize B2B SaaS experience more")
            
        # Check for experimentation emphasis
        if "experiment" in resume.lower() or "a/b test" in resume.lower():
            print("✅ Experimentation experience emphasized")
        else:
            print("⚠️  Add more emphasis on A/B testing")
            
        # Check for AI/automation mention
        if "ai" in resume.lower() or "claude" in resume.lower() or "gpt" in resume.lower():
            print("✅ AI experience mentioned")
        else:
            print("⚠️  Should highlight AI implementation experience")
            
        # Check narrative quality
        if "systematic" in cover.lower() or "discovered" in cover.lower():
            print("✅ Systematic approach narrative present")
        else:
            print("⚠️  Narrative could be stronger")
            
    else:
        print(f"❌ Content generation failed: {content_result.errors}")

    print("\n" + "="*80)
    print("⚡ APPLICATION COMPLETE FOR SUPERHUMAN")
    print("="*80)
    print(f"\n📍 Location: Remote (You have: [YOUR_CITY, STATE] - willing to work remotely)")
    print(f"💰 Salary range: $155K-$237K (Your floor: $[XXX]K - may need to address)")
    print(f"🎯 Key match: Growth PM experience, A/B testing, B2B SaaS, AI implementation")
    print(f"\n💡 Superhuman connection: Your systematic experimentation approach at [PREVIOUS_COMPANY_2]")
    print(f"   (47 A/B tests → [XX]% retention rate) directly aligns with their PLG needs")


if __name__ == "__main__":
    asyncio.run(test_superhuman())