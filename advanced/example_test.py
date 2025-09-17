#!/usr/bin/env python3
"""Example test demonstrating the v2 system capabilities."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.orchestrator import JobSearchOrchestrator
from utils import get_logger

logger = get_logger("example_test")


async def test_scoring_example():
    """Test the scoring functionality with a sample job."""
    print("\n" + "="*60)
    print("TEST 1: Scoring a Director-level PM Role")
    print("="*60)

    # Sample job description (Director level at Airbnb-like company)
    job_description = """
    Director of Product Management - Guest Experience

    About the Role:
    We're looking for a Director of Product Management to lead our Guest Experience team.
    You'll own the strategy and roadmap for how millions of guests discover and book unique stays worldwide.

    Responsibilities:
    • Drive product strategy and vision for guest discovery and search
    • Lead a team of 8-10 product managers across multiple product areas
    • Partner with engineering, design, and data science to deliver exceptional experiences
    • Define and track key metrics including conversion, retention, and NPS
    • Present to executive team and board on product initiatives
    • Run A/B tests and experiments to validate hypotheses
    • Manage P&L for your product area

    Requirements:
    • [XX]+ years of product management experience
    • 5+ years of people management experience
    • Experience with marketplace or travel industry preferred
    • Strong analytical skills and data-driven decision making
    • Excellent communication and stakeholder management
    • Track record of driving significant business impact
    • Experience with international markets and scaling global products

    Nice to Have:
    • Experience with AI/ML powered recommendations
    • Background in hospitality or travel technology
    • MBA or technical degree
    """

    orchestrator = JobSearchOrchestrator()

    # Test scoring
    result = await orchestrator.score_job(
        job_url="https://example.com/airbnb-director-pm",
        job_description=job_description
    )

    print(f"\n📊 Scoring Results:")
    print(f"  Company: {result.get('company', 'Unknown')}")
    print(f"  Total Score: {result.get('score', 0)}/100")
    print(f"  Recommendation: {result.get('recommendation', 'N/A')}")
    print(f"  Research Quality: {result.get('research_quality', 'N/A')}")

    if result.get('breakdown'):
        print(f"\n  Category Breakdown:")
        for category, score in result['breakdown'].items():
            print(f"    • {category}: {score:.1f}")

    return result


async def test_positioning_example():
    """Test the positioning agent with different scenarios."""
    print("\n" + "="*60)
    print("TEST 2: Positioning Strategy Examples")
    print("="*60)

    from agents.positioning_agent import PositioningAgent

    positioning_agent = PositioningAgent({
        'narrative_paths': ['knowledge/narrative']
    })

    # Test different role/company combinations
    test_cases = [
        {
            'job_data': {'company': 'Airbnb', 'role': 'Director of Product'},
            'research_data': {'industry': 'Travel & Hospitality'},
            'scoring_result': {'total_score': 85}
        },
        {
            'job_data': {'company': 'Etsy', 'role': 'Principal Product Manager'},
            'research_data': {'industry': 'E-commerce Marketplace'},
            'scoring_result': {'total_score': 78}
        },
        {
            'job_data': {'company': 'Stripe', 'role': 'Senior Product Manager'},
            'research_data': {'industry': 'FinTech/Payments'},
            'scoring_result': {'total_score': 72}
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n  Test Case {i}: {test_case['job_data']['company']} - {test_case['job_data']['role']}")

        result = await positioning_agent.process(test_case)

        if result.success:
            positioning = result.result
            print(f"    Strategy: {positioning.get('strategy_name', 'N/A')}")
            print(f"    Voice Blend: {positioning.get('voice_blend', {})}")
            print(f"    Key Metrics: {', '.join(positioning.get('key_metrics', [])[:3])}")
            print(f"    Hook: {positioning.get('hook', 'N/A')[:100]}...")
        else:
            print(f"    Error: {result.errors}")


async def test_workflow_simulation():
    """Simulate a mini workflow without full agents."""
    print("\n" + "="*60)
    print("TEST 3: Workflow Engine Simulation")
    print("="*60)

    from core.message_bus import MessageBus, AgentMessage, MessageType
    from core.state_manager import StateManager

    # Initialize components
    message_bus = MessageBus()
    state_manager = StateManager()

    # Start message bus
    await message_bus.start()

    # Create a workflow state
    state = state_manager.create_state(
        job_id="test_123",
        job_url="https://example.com/job",
        company="Test Company",
        role="Director of Product",
        workflow_type="director_level"
    )

    print(f"\n  Created workflow state:")
    print(f"    Job ID: {state.job_id}")
    print(f"    Status: {state.status.value}")
    print(f"    Company: {state.company}")
    print(f"    Role: {state.role}")

    # Simulate agent messages
    messages = [
        AgentMessage(
            sender="research_agent",
            recipient="orchestrator",
            message_type=MessageType.COMPANY_INTEL,
            data={"research_complete": True, "quality": "high"}
        ),
        AgentMessage(
            sender="scoring_agent",
            recipient="orchestrator",
            message_type=MessageType.SCORING_RESULT,
            data={"total_score": 82, "recommendation": "Submit after minor edits"}
        ),
        AgentMessage(
            sender="positioning_agent",
            recipient="orchestrator",
            message_type=MessageType.POSITIONING_STRATEGY,
            data={"strategy": "director_travel", "voice_blend": {"gawdat": 55, "mulaney": 30, "maher": 15}}
        )
    ]

    for msg in messages:
        await message_bus.send(msg)
        print(f"    Sent message from {msg.sender} ({msg.message_type.value})")

    # Get message history
    history = message_bus.get_history(limit=3)
    print(f"\n  Message bus history: {len(history)} messages")

    # Stop message bus
    await message_bus.stop()


async def main():
    """Run all example tests."""
    print("\n🚀 Job Search v2 - System Demonstration")
    print("This demonstrates the key components of the enhanced system\n")

    try:
        # Test 1: Scoring
        await test_scoring_example()

        # Test 2: Positioning
        await test_positioning_example()

        # Test 3: Workflow
        await test_workflow_simulation()

        print("\n" + "="*60)
        print("✅ All tests completed successfully!")
        print("="*60)

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())