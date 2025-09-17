# Claude Code Automation Scripts

This directory contains the automation scripts for Claude Code users who want to go beyond prompts to semi-automated job application generation.

## What's Here

- `setup_career_os.py` - Interactive setup wizard to build your narrative
- `apply_to_job.py` - End-to-end application generation
- `validate_output.py` - Quality review and validation

## Requirements

- Claude Code or Python 3.8+
- Optional: Basic API keys for job scraping
- 30 minutes for setup, 5 minutes per application

## Quick Start

### 1. Initial Setup
```bash
python setup_career_os.py
```

This will:
- Guide you through building your professional narrative
- Create templates for future applications
- Test the system with sample data

### 2. Apply to Jobs
```bash
python apply_to_job.py --url "https://job-posting-url.com"
```

Or with a saved job description:
```bash
python apply_to_job.py --file job_description.txt
```

### 3. Review Quality
```bash
python validate_output.py --application user_data/applications/latest
```

## How It Works

### Setup Process
1. **Personal Information**: Basic contact details
2. **Professional Identity**: How you position yourself
3. **Key Achievements**: 3-5 major wins with metrics
4. **Technical Skills**: Organized by category
5. **Value Proposition**: What makes you unique

### Application Generation
1. **Job Analysis**: Strategic breakdown of what they want
2. **Resume Generation**: Tailored to specific role requirements
3. **Cover Letter**: Personalized narrative connecting your experience
4. **Quality Review**: Structured feedback and improvement suggestions

## Output Structure

Each application creates a directory with:
```
user_data/applications/[company]_[role]_[timestamp]/
├── job_analysis.md      # Strategic insights about the role
├── resume.md           # Tailored resume
├── cover_letter.md     # Personalized cover letter
├── quality_review.md   # Feedback and suggestions
└── metadata.json       # Application tracking data
```

## Configuration

### User Narrative
Your professional narrative is stored in:
- `user_data/narratives/main_narrative.json`

This can be edited directly or regenerated with the setup script.

### Application Templates
Templates are stored in:
- `templates/narrative_template.json`
- `templates/resume_template.md`
- `templates/cover_letter_template.md`

## Features

| Feature | Status | Description |
|---------|--------|-------------|
| Interactive Setup | ✅ Stable | Guided narrative building |
| Job URL Scraping | ⚠️ Beta | Basic scraping for most sites |
| Resume Generation | ✅ Stable | Tailored formatting and content |
| Cover Letters | ✅ Stable | Personalized narrative approach |
| Quality Review | ✅ Stable | Structured feedback system |
| Application Tracking | 🧪 Experimental | Basic metadata storage |

## Troubleshooting

### Setup Issues
- **"No narrative found"**: Run `setup_career_os.py` first
- **Permission errors**: Check file permissions in user_data/
- **Python errors**: Ensure Python 3.8+ is installed

### Scraping Issues
- **"Error scraping job posting"**: Save job description to a file and use `--file` flag
- **Incomplete content**: Some sites block automated scraping
- **Rate limiting**: Wait a few minutes between attempts

### Quality Issues
- **Generic output**: Review and update your narrative with more specific achievements
- **Poor fit assessment**: The system is designed to be honest about mismatches
- **Formatting problems**: Check that templates haven't been corrupted

## Tips for Best Results

### Building Your Narrative
- **Be specific with metrics**: "40% improvement" not "significant improvement"
- **Include context**: What the achievement means for the business
- **Show progression**: Demonstrate growth over time
- **Stay honest**: Only include verifiable claims

### Using the System
- **Review everything**: Never submit without human review
- **Customize outputs**: Use generated content as a starting point
- **Iterate**: Update your narrative based on what works
- **Track results**: Note which approaches get responses

## Integration with Advanced System

This automation layer sits between the simple prompts and the full orchestrator:

- **Simple**: Copy prompts to Claude/ChatGPT manually
- **Claude Code**: Semi-automated with these scripts
- **Advanced**: Full 6-agent orchestrator system

You can upgrade to the advanced system anytime by:
1. Exporting your narrative from this system
2. Setting up the advanced orchestrator
3. Importing your data with the migration tools

## Support

- **Documentation**: See individual script docstrings
- **Examples**: Check examples/ directory for sample outputs
- **Issues**: Review error messages and logs
- **Advanced features**: See advanced/ directory for full orchestrator

---

*These scripts provide the sweet spot between manual prompts and full automation - enough automation to save time while maintaining control over quality.*