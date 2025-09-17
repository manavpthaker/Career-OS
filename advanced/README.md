# Advanced Career-OS System

This directory contains the full 6-agent orchestrator system from job-search-v2, with all personal information scrubbed and replaced with placeholders.

## What's Here

This is the sophisticated automation system that includes:
- **6 Specialized Agents**: Research, Scoring, Positioning, Content, QA, Export
- **Advanced Workflows**: Role-specific application strategies
- **Dynamic Positioning**: Strategic narrative development
- **Quality Rubrics**: 100-point evaluation system
- **Batch Processing**: Multiple applications efficiently

## Setup Requirements

- Python 3.8+
- API keys for OpenAI, Anthropic, Tavily
- 2-4 hours setup time
- $20-45/month in API costs
- Intermediate Python skills

## Getting Started

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Set up your profile**:
   ```bash
   # Edit config/user_profile.yaml with your information
   # Update knowledge/narrative/verified_facts.json
   ```

4. **Test the system**:
   ```bash
   python run.py score --url "https://job-url.com"
   python run.py apply --url "https://job-url.com" --workflow director_level
   ```

## Key Files to Customize

- `config/user_profile.yaml` - Your personal information
- `knowledge/narrative/verified_facts.json` - Your achievements and metrics
- `config/positioning.yaml` - Strategic positioning preferences
- `config/workflows/` - Application workflow configurations

## Migration from Simple Mode

If you started with the simple prompts and want to upgrade:

1. Export your narrative from the simple system
2. Use the migration script to convert formats
3. Gradually enable advanced features

## Features

| Feature | Status | Description |
|---------|--------|-------------|
| Job Scraping | ✅ Stable | LinkedIn, company sites |
| Strategic Analysis | ✅ Stable | 6-agent job analysis |
| Resume Generation | ✅ Stable | Tailored with positioning |
| Cover Letters | ✅ Stable | Strategic narrative approach |
| Quality Scoring | ⚠️ Beta | 100-point rubric system |
| Batch Processing | ⚠️ Beta | Multiple applications |
| Google Drive Export | 🧪 Experimental | Auto-export applications |
| Application Tracking | 🧪 Experimental | Status monitoring |

## Architecture

The system uses a message bus architecture with 6 specialized agents:

1. **Research Agent** - Company intelligence gathering
2. **Scoring Agent** - Job fit evaluation (100-point rubric)
3. **Positioning Agent** - Strategic narrative development
4. **Content Agent** - Resume/cover letter generation
5. **QA Agent** - Quality validation and review
6. **Export Agent** - Google Drive integration and tracking

## Support

- Documentation: See individual agent README files
- Issues: Check logs/ directory for debugging
- Performance: Target <5 minutes end-to-end
- Quality: 85+ rubric score for tier 1 companies

## Ethics

- **Human Review Required**: Nothing auto-submits
- **Rate Limiting**: Respects website ToS
- **Data Privacy**: Everything stays local
- **Honest Positioning**: Uses your real achievements only

---

*This system represents the cutting edge of AI-assisted job searching while maintaining ethical standards and human oversight.*
