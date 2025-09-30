# Career-OS: Job Search Without the Soul-Crushing Parts

Look, job searching sucks. Copying and pasting the same cover letter, pretending you're "passionate" about every company's mission, optimizing for keywords like some kind of search engine.

This toolkit automates the repetitive parts while keeping the human judgment that actually gets interviews.

## What It Does
✅ Analyzes job postings for hidden requirements
✅ Generates tailored resumes that don't sound like everyone else's
✅ Writes cover letters that feel personal (because they reference your actual experience)
✅ Tracks applications so you don't accidentally apply twice

## What It Doesn't Do
❌ Auto-submit applications (you review everything)
❌ Lie about your experience (uses your real background)
❌ Spam employers (built-in rate limits)
❌ Guarantee interviews (this isn't magic)

## Reality Check
- **Time investment**: 5 minutes to try prompts, 30 minutes for automation
- **Cost**: $20/month if you already have Claude/ChatGPT, $25-35 with API keys
- **Skills needed**: Copy/paste for prompts, basic CLI for automation
- **Success rate**: Improves your odds, doesn't guarantee anything

## Three Ways to Use This

### Just Want Better Applications? (5 minutes)
Copy these prompts to Claude/ChatGPT and paste your job posting:

**Job Analysis Prompt**: [prompts/01_analyze_job.md](prompts/01_analyze_job.md)
**Resume Builder**: [prompts/03_generate_resume.md](prompts/03_generate_resume.md)
**Cover Letter Writer**: [prompts/04_write_cover.md](prompts/04_write_cover.md)

### Have Claude Code? (30 minutes)
```bash
git clone https://github.com/manavpthaker/career-os
cd career-os
python claude-code/setup_career_os.py
python claude-code/apply_to_job.py --url [job-url]
```

### Want Full Control? (2+ hours)
Advanced orchestrator with 6 specialized agents, custom workflows, and detailed analytics.
See [advanced/README.md](advanced/README.md) for setup.

## Why This Works
Most job search advice treats you like a generic candidate. This system:
- Analyzes what each company actually wants
- Uses your real experience (not template bullets)
- Positions you strategically for each role
- Maintains authentic voice while optimizing for relevance

Built by someone who's applied to 50+ senior PM roles and knows what works.

## Example: See It In Action

**Before**: Generic cover letter that could be sent to anyone
> "I am excited about this opportunity because I am passionate about your company's mission..."

**After**: Specific positioning based on job analysis
> "Your job posting mentions scaling platform APIs for enterprise clients. At [CURRENT_COMPANY], I led a similar transformation that improved API response times by 80% while handling 3x traffic growth..."

## Cost Breakdown

| Approach | Setup Time | Monthly Cost | What You Get |
|----------|------------|--------------|--------------|
| **Prompts Only** | 5 min | $20 (existing Claude/ChatGPT) | Manual but guided |
| **Claude Code** | 30 min | $20 (existing subscription) | Semi-automated |
| **Advanced** | 2+ hours | $25-35 (API keys) | Full automation |

## Feature Status

| Feature | Status | Mode |
|---------|--------|------|
| Job Analysis Prompts | ✅ Stable | All |
| Resume Generation | ✅ Stable | All |
| Cover Letters | ✅ Stable | All |
| Application Tracking | ⚠️ Beta | Claude Code |
| Company Research | ⚠️ Beta | Advanced |
| Batch Processing | 🧪 Experimental | Advanced |
| ATS Optimization | 🧪 Experimental | Advanced |

## Ethics & Safety

- **Human Review Required**: Nothing gets sent without your approval
- **Rate Limiting**: Respects website ToS and API limits
- **Data Privacy**: Your information stays local
- **No Hallucination**: Uses your real experience only
- **Transparent Process**: You see exactly what's being generated

## Getting Started

1. **Try the prompts** - Copy [prompts/01_analyze_job.md](prompts/01_analyze_job.md) to Claude/ChatGPT
2. **Read the examples** - See [examples/](examples/) for worked examples
3. **Set up automation** - Follow [claude-code/README.md](claude-code/README.md) for automation

## Contributing

This project is built in public. Contributions welcome:
- Better prompts for specific industries
- Additional automation scripts
- Example applications (with PII removed)
- Documentation improvements

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - Use freely, contribute back if you can.

---

**Not working?** Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
**Questions?** Open an [Issue](https://github.com/yourusername/career-os/issues)
**Success story?** Share in [Discussions](https://github.com/yourusername/career-os/discussions)

*Built with the philosophy that job searching should feel less like playing a rigged game and more like showcasing what you can actually do.*