# Contributing to Career-OS

Career-OS is built in public with the philosophy that job searching should feel less like playing a rigged game. Contributions welcome from anyone who's felt the pain of repetitive applications.

## How to Contribute

### 🎯 High-Impact Contributions

**Better Prompts**
- Industry-specific job analysis prompts
- Role-specific positioning strategies
- Quality review criteria for different career levels

**Examples and Templates**
- Anonymized successful applications
- Narrative examples for different backgrounds
- Worked examples of prompt sequences

**Automation Improvements**
- Better job posting scrapers
- Integration with job boards
- Quality validation tools

**Documentation**
- Clearer setup instructions
- Troubleshooting guides
- Video walkthroughs

### 🔧 Technical Contributions

**Code Quality**
- Bug fixes and error handling
- Performance improvements
- Test coverage

**Features**
- New automation scripts
- Better CLI interfaces
- Integration with career tools

**Platform Support**
- Windows/macOS/Linux compatibility
- Different Python versions
- Cloud deployment options

## Getting Started

### Development Setup

1. **Fork the repository**
2. **Clone your fork**:
   ```bash
   git clone https://github.com/yourusername/career-os
   cd career-os
   ```

3. **Create development branch**:
   ```bash
   git checkout -b feature/your-improvement
   ```

4. **Test your changes**:
   ```bash
   python claude-code/setup_career_os.py  # Test setup
   python claude-code/apply_to_job.py --file examples/sample_job_analysis/sample_job.md  # Test application
   ```

### Contribution Guidelines

#### For Prompt Improvements
- **Test thoroughly** with multiple job types
- **Provide examples** of input and expected output
- **Document edge cases** and limitations
- **Keep authentic voice** - avoid corporate buzzwords

#### For Code Changes
- **Follow existing patterns** in the codebase
- **Add error handling** for edge cases
- **Include docstrings** for new functions
- **Test with sample data** before submitting

#### For Examples and Templates
- **Remove all PII** - use [PLACEHOLDER] format
- **Include context** about why the example works
- **Provide variety** - different industries, roles, experience levels
- **Mark success metrics** if known (interview rate, etc.)

## Content Guidelines

### Voice and Tone
Career-OS maintains an authentic, practical voice:

✅ **Do**: "This saves 3 hours per application"
❌ **Don't**: "Revolutionary AI-powered career transformation"

✅ **Do**: "Here's what worked for 50+ applications"
❌ **Don't**: "Guaranteed interview success"

✅ **Do**: "The system tells you when fit is poor"
❌ **Don't**: "Perfect for any role"

### Privacy and Ethics

**Personal Information**
- Never include real names, emails, phone numbers
- Use contextual placeholders: [YOUR_NAME], [CURRENT_COMPANY]
- Sanitize all metrics: $3.6M → $[X.X]M

**Honest Positioning**
- Don't create fake achievements or experiences
- Include realistic limitations and failure modes
- Emphasize human review and judgment

**Respect for Companies**
- Don't encourage spam or automated submissions
- Include rate limiting and ToS compliance
- Focus on quality over quantity

## Types of Contributions

### 1. Prompt Engineering
**What we need**: Better prompts for specific situations
**Examples**:
- Prompts for career changers
- Industry-specific analysis (fintech, healthcare, etc.)
- Executive-level positioning

**How to contribute**:
1. Test prompts with real job postings
2. Document success patterns
3. Provide before/after examples
4. Submit with clear use cases

### 2. Example Library
**What we need**: Diverse, successful examples
**Examples**:
- Different experience levels (entry, senior, executive)
- Career transitions (consultant to PM, engineer to PM)
- Industry switches
- International candidates

**How to contribute**:
1. Anonymize completely
2. Include context about success (interview rate, etc.)
3. Explain what made the approach work
4. Format consistently with existing examples

### 3. Automation Tools
**What we need**: Better developer experience
**Examples**:
- Improved job scraping
- Better file organization
- Integration with career tools (LinkedIn, job boards)
- Quality validation automation

**How to contribute**:
1. Follow existing code patterns
2. Add comprehensive error handling
3. Include usage examples
4. Test with edge cases

### 4. Documentation
**What we need**: Clearer explanations and guides
**Examples**:
- Video tutorials for setup
- Troubleshooting common issues
- Advanced configuration guides
- Success story compilation

**How to contribute**:
1. Focus on practical, actionable guidance
2. Include screenshots or examples
3. Test instructions with fresh users
4. Maintain authentic voice

## Submission Process

### Pull Request Template

```markdown
## What this changes
Brief description of the improvement

## Why this matters
Connection to user pain points or system limitations

## Testing done
How you validated the changes work

## Examples included
Links to examples or test cases

## Breaking changes
Any changes that affect existing users
```

### Review Process

1. **Initial review** - maintainers check alignment with project goals
2. **Technical review** - code quality, testing, edge cases
3. **User testing** - validate with real job search scenarios
4. **Documentation review** - ensure clear explanations
5. **Merge and release** - integration with main codebase

## Recognition

Contributors are recognized in:
- **README.md** - major contributions
- **Release notes** - feature additions
- **Examples** - attribution for successful templates
- **Documentation** - credit for guides and improvements

## Community Guidelines

### What We Encourage
- **Practical experience sharing** - what actually worked
- **Honest assessment** - including failures and limitations
- **Diverse perspectives** - different backgrounds and approaches
- **Constructive feedback** - helping improve existing content

### What We Discourage
- **Generic advice** - stuff you could find anywhere
- **Unrealistic promises** - "guaranteed success" claims
- **Spam or promotion** - using contributions for self-promotion
- **Toxic behavior** - job searching is stressful enough

## Getting Help

### For Contributors
- **Questions**: Open GitHub discussions
- **Bug reports**: Use issue templates
- **Feature requests**: Explain user impact
- **Documentation**: Suggest improvements

### For Users
- **Setup help**: See QUICKSTART.md
- **Advanced features**: Check advanced/README.md
- **Success stories**: Share in discussions
- **Feedback**: All input helps improve the system

## Project Philosophy

Career-OS exists because job searching currently sucks for candidates. Every contribution should help level the playing field by:

- **Reducing repetitive work** without losing personalization
- **Improving quality** of applications through better strategy
- **Maintaining authenticity** while optimizing for relevance
- **Building transparency** into what companies actually want

The goal isn't to game the system - it's to help good candidates showcase their actual value more effectively.

---

*Thanks for helping build something that makes job searching feel more human. Every contribution moves us closer to a world where talent and fit matter more than keyword optimization.*