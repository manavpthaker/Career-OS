# Career-OS Quick Start Guide

Get your first job application generated in 30 minutes or less.

## Choose Your Path

### 🚀 Fastest: Prompts Only (5 minutes)
Best for: One-off applications, testing the approach

1. **Copy the job analysis prompt** from [prompts/01_analyze_job.md](prompts/01_analyze_job.md)
2. **Open Claude or ChatGPT** (we recommend Claude for better reasoning)
3. **Paste the prompt + job posting + your background**
4. **Follow the sequence**: Job analysis → Resume → Cover letter → Quality review

### ⚡ Recommended: Claude Code (30 minutes)
Best for: Regular job searching, building a system

1. **Clone this repository**:
   ```bash
   git clone https://github.com/manavpthaker/career-os
   cd career-os
   ```

2. **Run the setup wizard**:
   ```bash
   python claude-code/setup_career_os.py
   ```

3. **Apply to your first job**:
   ```bash
   python claude-code/apply_to_job.py --url [job-url]
   ```

### 🎯 NEW: LinkedIn Surround Sound (2 weeks)
Best for: Getting noticed BEFORE you apply (3-5x better response rate)

1. **Set up your campaign**:
   ```bash
   python claude-code/linkedin/setup_surround_sound.py
   ```

2. **Generate weekly content**:
   ```bash
   python claude-code/linkedin/generate_weekly_content.py
   ```

3. **Track your progress**:
   ```bash
   python claude-code/linkedin/track_campaign.py
   ```

See [linkedin/README.md](linkedin/README.md) for complete strategy.

### 🔧 Advanced: Full Orchestrator (2+ hours)
Best for: Power users, high-volume applications

See [advanced/README.md](advanced/README.md) for complete setup.

## What You Need

### For Prompts Only
- Claude or ChatGPT account ($20/month)
- Your resume or LinkedIn profile
- A job posting to test with

### For Claude Code
- Python 3.8+ ([Download here](https://python.org))
- Claude or ChatGPT account
- 30 minutes for initial setup

### For Advanced System
- All of the above plus:
- API keys (OpenAI, Anthropic, optional Tavily)
- 2-4 hours setup time
- $20-45/month in API costs

## Step-by-Step: Claude Code Path

### 1. Setup (15 minutes)

**Install Python** (if needed):
- Download from [python.org](https://python.org)
- Choose "Add to PATH" during installation

**Clone the repository**:
```bash
git clone https://github.com/manavpthaker/career-os
cd career-os
```

**Run setup wizard**:
```bash
python claude-code/setup_career_os.py
```

The wizard will ask for:
- Basic contact information
- Professional positioning (2-3 sentences)
- Current/recent role details
- 3-5 key achievements with metrics
- Technical skills and tools
- Target roles and value proposition

### 2. First Application (10 minutes)

**Find a job posting** you want to apply to

**Generate application**:
```bash
python claude-code/apply_to_job.py --url "https://job-posting-url"
```

This creates:
- Strategic job analysis
- Tailored resume
- Personalized cover letter
- Quality review with feedback

**Review outputs** in `user_data/applications/[company]_[role]_[timestamp]/`

### 3. Refine and Submit (5 minutes)

1. **Read the quality review** - honest feedback about strengths/weaknesses
2. **Edit the generated materials** - use as a starting point, not final output
3. **Format for submission** - convert to PDF, etc.
4. **Submit through company's system** - never auto-submit

## Sample Workflow

```bash
# Setup once
python claude-code/setup_career_os.py

# For each job application
python claude-code/apply_to_job.py --url "https://linkedin.com/jobs/view/123456"

# Review output
cd user_data/applications/latest_application/
cat quality_review.md  # Read feedback first
cat resume.md         # Review tailored resume
cat cover_letter.md   # Review personalized letter

# Edit, format, and submit manually
```

## Quality Expectations

### What Career-OS Does Well
- **Strategic analysis** of what companies actually want
- **Specific positioning** based on your real experience
- **Authentic voice** that doesn't sound templated
- **Honest assessment** of fit and potential concerns

### What You Still Need To Do
- **Review everything** before submitting
- **Customize for your voice** and specific insights
- **Format professionally** (PDF, proper spacing, etc.)
- **Submit through proper channels**

### Success Metrics
- **Better positioning**: Applications feel more relevant to specific roles
- **Time savings**: 3+ hours of writing reduced to 30 minutes of review
- **Higher quality**: More strategic, less generic than template approaches
- **Honest feedback**: System tells you when fit is poor

## Common Issues

### "Error scraping job posting"
- Save the job description to a text file
- Use `--file job_description.txt` instead of `--url`

### "No narrative found"
- Run `python claude-code/setup_career_os.py` first
- Check that `user_data/narratives/main_narrative.json` exists

### "Generic output"
- Add more specific metrics to your narrative
- Include more context about your achievements
- Update your value proposition to be more distinctive

### "Poor quality review scores"
- The system is designed to be honest about fit
- Consider whether the role is actually a good match
- Focus on roles that align better with your background

## Next Steps

### After Your First Application
1. **Track results** - note which approaches get responses
2. **Refine narrative** - update based on what works
3. **Batch applications** - apply to multiple similar roles
4. **Upgrade gradually** - consider advanced features as needed

### Building Your System
- **Create role templates** for target position types
- **Develop company research** process for better customization
- **Track application outcomes** to optimize approach
- **Build feedback loop** from interviews back to narrative

### Advanced Features
- **Full orchestrator** with 6 specialized agents
- **Batch processing** for multiple applications
- **Advanced analytics** and success tracking
- **Custom workflows** for specific industries

## Support

- **Examples**: See `examples/` directory for sample outputs
- **Documentation**: Each directory has detailed README files
- **Issues**: Open GitHub issues for bugs or questions
- **Discussions**: Share success stories and ask questions

---

*Remember: This is automation for the repetitive parts. Your judgment, customization, and human review are what actually get interviews.*