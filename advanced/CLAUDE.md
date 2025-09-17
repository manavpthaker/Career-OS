# CLAUDE.md - Job Search v2 Assistant Context

This file provides guidance to Claude Code when working with the enhanced job search automation system.

## System Overview

### What This Is
An advanced 6-agent job application system optimized for Director/Principal PM roles. Evolution of v1 with cleaner architecture, faster processing, and strategic positioning capabilities.

### Core Innovation
The **Positioning Agent** - a new component that analyzes role/company context and determines optimal narrative strategy before content generation. This ensures each application feels inevitable rather than generic.

## Agent Architecture

### The 6 Specialized Agents

1. **Research Agent** (`agents/research_agent.py`)
   - Consolidates: EnrichmentAgent + WebSearchAgent + CompanyScraper from v1
   - Gathers company intelligence, news, culture
   - Caches results for efficiency
   - ~85% code reuse from v1

2. **Scoring Agent** (`agents/scoring_agent.py`)
   - Consolidates: FilterAgent + ScoringAgent + JDAnalyzer + RubricAgent from v1
   - Implements 100-point rubric system
   - Provides confidence intervals
   - ~90% code reuse from v1

3. **Positioning Agent** (`agents/positioning_agent.py`)
   - **NEW** - No v1 equivalent
   - Determines strategic angle based on role/industry
   - Calibrates voice blend (50/30/20)
   - Identifies gap mitigation strategies

4. **Content Agent** (`agents/content_agent.py`)
   - Based on: ApplicationAgent + PersonalizationAgent from v1
   - Generates tailored resume/cover letter
   - Uses positioning strategy from Positioning Agent
   - ~75% code reuse from v1

5. **QA Agent** (`agents/qa_agent.py`)
   - Based on: ReviewAgent from v1
   - Multi-stage quality validation
   - Rubric score prediction
   - ~80% code reuse from v1

6. **Export Agent** (`agents/export_agent.py`)
   - Based on: GoogleDriveAgent from v1
   - Minimal changes
   - ~95% code reuse from v1

## Workflow Engine

### Dynamic Workflows by Role
```python
# Director Level - Emphasize management
workflow = {
    "emphasis": "management_scale",
    "key_metrics": ["50+ managed", "25+ built", "15-20 led"],
    "positioning": "organizational_builder"
}

# Principal Level - Emphasize impact
workflow = {
    "emphasis": "strategic_impact",
    "key_metrics": ["$[X.X]M+ impact", "[XX]% efficiency improvement", "[XXX]% YoY growth"],
    "positioning": "strategic_innovator"
}
```

### Message Bus Communication
Agents communicate via standardized messages:
```python
message = AgentMessage(
    sender="research_agent",
    recipient="scoring_agent",
    message_type="company_intel",
    data={"company": "Airbnb", "intel": {...}},
    correlation_id="job_123"
)
```

## Knowledge Systems

### Rubric System (100 points)
From `knowledge/rubrics/director_rubric.json`:
- Role Alignment: 15 points
- Outcomes & Metrics: 15 points
- Scope & Seniority: 12 points
- Experimentation: 10 points
- Product Sense: 8 points
- Cross-functional: 10 points
- Domain/Technical: 10 points
- Communication: 8 points
- Company Fit: 7 points
- Evidence Depth: 5 points

### Positioning Strategies
From `knowledge/positioning/strategies.json`:
```json
{
  "director_travel": {
    "angle": "international_hospitality_leadership",
    "metrics": ["[XX]+ employees", "80% revenue growth"],
    "voice_blend": {"gawdat": 60, "mulaney": 25, "maher": 15}
  },
  "principal_marketplace": {
    "angle": "marketplace_scaling_expert",
    "metrics": ["[XX]% retention rate", "$[X.X]M+ impact", "[XXX]% YoY growth"],
    "voice_blend": {"gawdat": 45, "mulaney": 35, "maher": 20}
  }
}
```

### Voice Calibration
The 50/30/20 formula:
- **50% Mo Gawdat**: "This challenge revealed an opportunity to..."
- **30% John Mulaney**: "[XXX,XXX] transactions across [XXX] endpoints"
- **20% Bill Maher**: "The results speak for themselves"

## Critical Accuracy Rules

### Always True
✅ [XX]+ years experience (2014-2024)
✅ [X] years management
✅ 50+ → 25+ → 15-20 team progression
✅ 1 successful exit ([PREVIOUS_COMPANY_2] only)
✅ $[X.X]M+ impact at [CURRENT_COMPANY]
✅ [XX]% retention rate at [PREVIOUS_COMPANY_2]
✅ [XXX]% YoY growth growth at [PREVIOUS_COMPANY_2]

### Never Claim
❌ 2 exits (only [PREVIOUS_COMPANY_2])
❌ 500K customers ([XXXX]+ customers)
❌ [XX]+ years experience
❌ C-suite titles except CPO
❌ Senior PM at [CURRENT_COMPANY] (just PM)
❌ Building ML models (partnered only)

## Development Patterns

### Agent Development
All agents inherit from BaseAgent:
```python
class ResearchAgent(BaseAgent):
    async def process(self, message: AgentMessage) -> AgentResponse:
        # Process and return standardized response
        return AgentResponse(
            success=True,
            data=research_results,
            metrics={"time": 2.3, "sources": 5}
        )
```

### Workflow Patterns
```python
# Parallel execution
async with workflow.parallel() as p:
    research_task = p.add(research_agent.process(job_data))
    scoring_task = p.add(scoring_agent.process(job_data))

results = await p.gather()
```

### Testing Patterns
```python
# Test positioning logic
def test_director_positioning():
    agent = PositioningAgent()
    strategy = agent.determine_strategy("Director", "Travel")
    assert strategy["angle"] == "international_hospitality_leadership"
    assert strategy["voice_blend"]["gawdat"] == 60
```

## Common Operations

### Add New Positioning Strategy
1. Edit `knowledge/positioning/strategies.json`
2. Add role/industry combination
3. Define angle, metrics, voice blend
4. Test with sample JD

### Modify Scoring Rubric
1. Edit `knowledge/rubrics/director_rubric.json`
2. Adjust point allocations (must sum to 100)
3. Update scoring logic in `agents/scoring_agent.py`
4. Rerun validation tests

### Debug Workflow
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with verbose output
python run.py apply --url "..." --debug --verbose

# Check message bus
tail -f logs/message_bus.log
```

## Performance Optimization

### Caching Strategy
- Research results cached for 24 hours
- Company data shared across applications
- Scoring results cached per JD version

### Parallel Processing
- Research + Initial Scoring: Parallel
- Positioning waits for both
- Content + QA: Can parallelize sections

### Target Metrics
- End-to-end: <5 minutes
- Research: <2 minutes
- Content generation: <1 minute
- QA: <30 seconds

## Migration from v1

### What's Preserved
- NarrativeStore (100% compatible)
- Logging system (100% compatible)
- Guardrails (100% compatible)
- User profile format
- Application output format

### What's New
- Positioning Agent (completely new)
- Workflow engine (new)
- Message bus (new)
- Consolidated agents (merged from 33 to 6)

### Backward Compatibility
The system can import v1 applications:
```python
from migrations import import_v1_data
import_v1_data.migrate("../job-search-automation")
```

## Best Practices

### When Adding Features
1. Check if v1 has similar functionality
2. Reuse code where possible (70%+ target)
3. Maintain message bus compatibility
4. Add comprehensive tests
5. Update this documentation

### When Debugging
1. Check agent health metrics first
2. Review message bus logs
3. Validate positioning strategy
4. Verify narrative store facts
5. Run QA agent in isolation

### When Optimizing
1. Profile with `cProfile` first
2. Check for unnecessary API calls
3. Verify caching is working
4. Consider parallel execution
5. Monitor message bus latency

## System Commands

### Quick Commands
```bash
# Score a job
python run.py score --url "[URL]"

# Apply with specific workflow
python run.py apply --url "[URL]" --workflow director_level

# Test positioning for a company
python -m agents.positioning_agent test --company "Airbnb" --role "Director"

# Validate rubric scoring
python -m agents.scoring_agent validate --jd "job_description.txt"

# Check system health
python run.py health
```

## Important Files

### Core System
- `core/orchestrator.py` - Main workflow coordinator
- `core/message_bus.py` - Agent communication
- `core/workflow_engine.py` - DAG execution

### Configuration
- `config/user_profile.yaml` - User information
- `config/positioning.yaml` - Strategy configuration
- `config/workflows/*.yaml` - Workflow templates

### Knowledge Base
- `knowledge/narrative/verified_facts.json` - Ground truth
- `knowledge/rubrics/director_rubric.json` - Scoring system
- `knowledge/positioning/strategies.json` - Positioning matrix

---

**Remember**: The Positioning Agent is the key innovation. It bridges research and content generation by determining the optimal narrative strategy for each specific role/company combination.