"""LLM Client for OpenAI and Anthropic integration."""

import os
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
import json

# Load environment variables
env_path = Path(__file__).parent.parent / 'config' / '.env'
if env_path.exists():
    load_dotenv(env_path)

try:
    from openai import AsyncOpenAI
    openai_available = True
except ImportError:
    openai_available = False
    print("OpenAI not installed. Run: pip install openai")

try:
    from anthropic import AsyncAnthropic
    anthropic_available = True
except ImportError:
    anthropic_available = False
    print("Anthropic not installed. Run: pip install anthropic")

from utils import get_logger

logger = get_logger("llm_client")


class LLMClient:
    """Unified client for OpenAI and Anthropic LLMs."""

    def __init__(self, provider: str = None):
        """Initialize LLM client.

        Args:
            provider: 'openai' or 'anthropic' (defaults to env variable)
        """
        self.provider = provider or os.getenv('DEFAULT_LLM_PROVIDER', 'openai')

        # Initialize OpenAI client
        if self.provider == 'openai' and openai_available:
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                self.openai_client = AsyncOpenAI(api_key=api_key)
                self.openai_model = os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview')
                logger.info(f"Initialized OpenAI client with model {self.openai_model}")
            else:
                logger.warning("OpenAI API key not found")
                self.openai_client = None
        else:
            self.openai_client = None

        # Initialize Anthropic client
        if self.provider == 'anthropic' and anthropic_available:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if api_key:
                self.anthropic_client = AsyncAnthropic(api_key=api_key)
                self.anthropic_model = os.getenv('ANTHROPIC_MODEL', 'claude-3-opus-20240229')
                logger.info(f"Initialized Anthropic client with model {self.anthropic_model}")
            else:
                logger.warning("Anthropic API key not found")
                self.anthropic_client = None
        else:
            self.anthropic_client = None

    async def generate_content(self,
                              prompt: str,
                              system_prompt: str = None,
                              temperature: float = 0.7,
                              max_tokens: int = 2000) -> str:
        """Generate content using the configured LLM.

        Args:
            prompt: User prompt
            system_prompt: System instructions
            temperature: Creativity level (0-1)
            max_tokens: Maximum response length

        Returns:
            Generated text content
        """
        try:
            if self.provider == 'openai' and self.openai_client:
                return await self._generate_openai(
                    prompt, system_prompt, temperature, max_tokens
                )
            elif self.provider == 'anthropic' and self.anthropic_client:
                return await self._generate_anthropic(
                    prompt, system_prompt, temperature, max_tokens
                )
            else:
                logger.error(f"No LLM client available for provider: {self.provider}")
                return self._generate_fallback(prompt)

        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return self._generate_fallback(prompt)

    async def _generate_openai(self,
                              prompt: str,
                              system_prompt: str,
                              temperature: float,
                              max_tokens: int) -> str:
        """Generate content using OpenAI."""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await self.openai_client.chat.completions.create(
            model=self.openai_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        return response.choices[0].message.content

    async def _generate_anthropic(self,
                                 prompt: str,
                                 system_prompt: str,
                                 temperature: float,
                                 max_tokens: int) -> str:
        """Generate content using Anthropic."""

        # Anthropic requires system prompt in create() call
        response = await self.anthropic_client.messages.create(
            model=self.anthropic_model,
            system=system_prompt if system_prompt else "You are a helpful assistant.",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )

        return response.content[0].text

    def _generate_fallback(self, prompt: str) -> str:
        """Generate fallback content when LLM is unavailable."""
        logger.warning("Using fallback generation (no LLM available)")

        # Return a basic template response
        if "resume" in prompt.lower():
            return self._get_fallback_resume()
        elif "cover" in prompt.lower():
            return self._get_fallback_cover_letter()
        else:
            return "Unable to generate content. Please check LLM configuration."

    def _categorize_role(self, role_title: str, description: str) -> str:
        """Categorize role for better targeting."""
        role_lower = role_title.lower()
        desc_lower = description.lower()

        if 'growth' in role_lower or 'growth' in desc_lower:
            return "GROWTH PM: Emphasize experimentation (47 A/B tests), retention (70%, 2.3x industry), funnel optimization"
        elif 'marketplace' in desc_lower or 'two-sided' in desc_lower:
            return "MARKETPLACE: Emphasize liquidity, network effects, two-sided dynamics ([PREVIOUS_COMPANY_2], [CURRENT_COMPANY])"
        elif 'enterprise' in role_lower or 'b2b' in desc_lower:
            return "ENTERPRISE: Emphasize IKEA partnership, B2B SaaS, unit economics ([PREVIOUS_COMPANY_1])"
        elif 'ai' in role_lower or 'ml' in desc_lower:
            return "AI/ML: Emphasize Claude/GPT-4 implementation, evaluation harnesses, [XX]% efficiency improvement gains"
        elif 'platform' in role_lower:
            return "PLATFORM: Emphasize system thinking, API design, technical depth"
        else:
            return "GENERAL PM: Balance all experiences, emphasize versatility"

    def _get_fallback_resume(self) -> str:
        """Get fallback resume template."""
        return """# [YOUR_NAME]
Product Manager | [XX]+ years Experience

## PROFESSIONAL SUMMARY
Experienced product manager with proven track record of preventing $400K in churn and achieving [XX]% efficiency improvement gains through AI automation.

## PROFESSIONAL EXPERIENCE

### Product Manager | [CURRENT_COMPANY] | Sept 2024 - Sept 2025
• Prevented $400K in customer churn through data-driven strategies
• Achieved [XX]% efficiency improvement gains via AI automation
• Led cross-functional team of 10+ members

### Head of Product | [PREVIOUS_COMPANY_1] | [START_DATE] - [END_DATE]
• Raised $3.2M in Series A funding
• Built and led team of 15-20
• Achieved [XXX]% YoY growth growth

### Head of Product | [PREVIOUS_COMPANY_2] | 2017 - 2021
• Built marketplace achieving [XX]% retention rate
• Led successful exit
• Scaled to 1000+ users

## SKILLS
Technical: Python, SQL, AI/ML, APIs
Tools: Jira, Figma, Amplitude, Mixpanel"""

    def _get_fallback_cover_letter(self) -> str:
        """Get fallback cover letter template."""
        return """Dear Hiring Manager,

Having just delivered $400K in churn prevention and [XX]% efficiency improvement gains at [CURRENT_COMPANY], I'm excited to bring this same impact to your team.

My experience includes:
• Preventing $400K in customer churn through data-driven retention strategies
• Achieving [XX]% efficiency improvement gains via AI automation
• Leading teams of 15-20 through successful exits and Series A funding

I'm ready to contribute immediately to your product organization.

Best regards,
[YOUR_NAME]"""

    async def generate_resume(self,
                             job_data: Dict[str, Any],
                             facts: Dict[str, Any],
                             positioning: str,
                             voice_blend: Dict[str, int]) -> str:
        """Generate a tailored resume for a specific job.

        Args:
            job_data: Job information
            facts: Verified facts about the candidate
            positioning: Positioning strategy
            voice_blend: Voice calibration percentages

        Returns:
            Generated resume content
        """
        system_prompt = f"""You are an expert resume writer optimizing for the Universal JD-to-Application Scoring Rubric (85+ score target).

CRITICAL STRUCTURE - MUST SCORE 5/5 ON EACH RUBRIC CATEGORY:

1. HEADER (Exact format - no deviation):
# **[YOUR_NAME]**

[YOUR_CITY, STATE] | [[YOUR_EMAIL]](mailto:[YOUR_EMAIL]) | [YOUR_PHONE] | Open to NYC hybrid ≥25%
[LinkedIn](http://linkedin.com/in/manavpthaker) | [GitHub](http://github.com/manavpthaker) | [Portfolio](http://mpthaker.xyz)

---

2. POSITIONING STATEMENT:
- For AI/Platform roles: "Product leader combining AI platform innovation with proven business impact scaling cross-functional teams from 15 to 50+ across multiple organizations"
- For Growth PM: "Growth-focused product leader with systematic experimentation approach driving Product-Led Growth (PLG) strategies"
- For Marketplace: "Two-sided marketplace expert who's built liquidity from zero and optimized network effects at scale"
- For Enterprise: "B2B product leader driving enterprise transformation through strategic partnerships and unit economics optimization"

3. IMPACT LINE (Choose 4-5 most relevant to JD):
**Impact: [key metrics] | [team scaling if senior role] | X years management experience**

Key metrics to use:
- AI/Platform roles: 80% AI efficiency gains | $[X.X]M+ impact delivered | [XX]% retention rate (2.3x industry) | [X] years management experience
- Growth roles: 47 A/B tests conducted | [XX]% retention rate (2.3x industry) | [XXX]% YoY growth growth | 100:1 LTV/CAC
- Marketplace: 375K transactions analyzed | 99.2% order accuracy | 20K+ active users | Successful exit
- Enterprise: 319,950 store visits | $[XXX]K+ ARR potential | 65% email open rates (3x industry) | 12% MoM growth

4. ## EXPERIENCE (MUST INCLUDE ALL FOUR ROLES - NEVER SKIP ANY):

### Product Manager | [CURRENT_COMPANY] | [START_DATE] - September 2025
**[FUNDING_STAGE] company serving [XXXX]+ customers artisan florists**
• [Choose 3 bullets most relevant to JD, for AI/Platform roles emphasize]:
  - **AI Platform Implementation**: Deployed multi-modal LLMs across product workflows, achieving [XX]% efficiency improvement improvement in PM operations while identifying $6M revenue opportunities through systematic behavioral analysis
  - **Developer Experience Optimization**: Collaborated with a 10+ person engineering team to design AI model evaluation frameworks and automate quality gates, enabling weekly releases. Led interviews to pinpoint and resolve major workflow bottlenecks, resulting in an [XX]% efficiency improvement in deployment efficiency
  - **Cross-functional Platform Strategy**: Led analysis of 375K transactions across 628 merchant endpoints, discovering 13.3% bundle opportunities that informed $50M to $200M marketplace transformation roadmap

### Head of Product | [PREVIOUS_COMPANY_1] | [START_DATE] - 2024
**PropTech B2B SaaS - led [XX-XX] person cross-functional team through Series A**
• [Choose 3 bullets most relevant to JD]:
  - **Enterprise Platform Pivot**: Drove strategic transformation from SMB to enterprise model, securing IKEA partnership, generating 319,950 store visits (28% over projection) and $[XXX]K+ ARR potential potential
  - **Cross-functional Team Leadership**: Built and managed a [XX-XX] person team across product, engineering, design, and analytics, improving unit economics by 35% while maintaining 12% MoM user growth during pivot
  - **Developer-Focused Product Strategy**: Established API-first architecture and partner integration platform, achieving 65% email engagement rates (3x industry average) through systematic personalization

### Head of Product | [PREVIOUS_COMPANY_2] | 2017 - 2021
**Food delivery marketplace - built a 25+ person product organization from zero to successful exit**
• [Choose 3 bullets most relevant to JD]:
  - **Retention Platform Innovation**: Achieved [XX]% retention rate rate (2.3x industry average) through systematic A/B testing program spanning 47 experiments, resulting in 100:1 LTV/CAC ratio and successful exit
  - **Team Building & Platform Scale**: Built 25+ person product organization from the ground up, scaling to [XX,XXX]+ users through systematic platform optimization and data-driven product development
  - **Technical Product Leadership**: Led systematic approach to marketplace dynamics, achieving [XXX]% YoY growth revenue growth while partnering with engineering on prediction algorithms, reaching 73% accuracy

### Director of Customer Experience | [PREVIOUS_COMPANY_3] | 2014 - 2016
**Luxury hospitality group in [LOCATION] - managed [XX]+ employees across 10 departments and 4 properties**
• **International Operations Leadership**: Achieved 80% YoY revenue growth and zero employee turnover while managing a cross-cultural team of 50+ across 10 departments in [LOCATION]

5. ## TECHNICAL SKILLS (Grouped by category):
**AI & Analytics**: Claude/GPT-4 deployment, A/B testing, SQL, Python, statistical analysis, ML model evaluation
**Product Platforms**: API design, SDK development, developer experience, platform architecture, microservices integration
**Tools & Methods**: Jira, Figma, Amplitude, Looker, GitHub, Agile/Scrum, OKRs, user research, competitive analysis

6. ## EDUCATION:
[YOUR_DEGREE] in [YOUR_FIELD] — [YOUR_UNIVERSITY] ([GRADUATION_YEAR])

RUBRIC OPTIMIZATION RULES:
- Every bullet must have QUANTIFIED OUTCOMES (%, $, time, scale)
- Use JD's exact verbs when possible (own, drive, ship, optimize, scale)
- Include team sizes, budget ownership, and scope for seniority signal
- Show cross-functional work with specific teams (engineering, PMM, data science)
- Include experimentation methodology (A/B tests, sample sizes, confidence intervals)
- NO TYPOS OR GRAMMATICAL ERRORS (automatic -3 points)
- NEVER write "not relevant" or skip any role
- NO meta-commentary about the resume"""

        user_prompt = f"""Generate a RUBRIC-OPTIMIZED resume for:
Company: {job_data.get('company', 'Unknown')}
Role: {job_data.get('role', 'Product Manager')}

JOB REQUIREMENTS TO ADDRESS:
{job_data.get('description', '')[:1000]}

ROLE CATEGORIZATION:
{self._categorize_role(job_data.get('role', ''), job_data.get('description', ''))}

VERIFIED FACTS (USE EXACTLY AS PROVIDED):
{json.dumps(facts, indent=2)[:3500]}

RUBRIC OPTIMIZATION CHECKLIST:
✅ Role Alignment (15%): Mirror JD verbs exactly (own, drive, ship, optimize)
✅ Outcomes & Metrics (15%): Every bullet has numbers with context
✅ Scope & Seniority (12%): Include team sizes, budgets, portfolio scope
✅ Experimentation (10%): Show A/B tests with methodology
✅ Product Sense (8%): Connect research to outcomes
✅ Cross-Functional (10%): Name specific teams and joint outcomes
✅ Domain & Technical (10%): Use relevant technical depth
✅ Communication (8%): Clean formatting, no filler
✅ Company Fit (7%): Tailor positioning to company
✅ Evidence Depth (5%): Reference portfolio where relevant

BULLET SELECTION RULES:
1. Choose bullets that directly match JD requirements
2. Prioritize metrics mentioned in JD (growth, retention, revenue)
3. Include methodology for any testing/experimentation
4. Show progression across roles
5. Balance technical and business outcomes

Generate the resume following the exact structure provided.

FINAL CHECKLIST:
✓ ALL 4 ROLES have complete descriptions
✓ NO text saying "not relevant to JD"
✓ NO meta-commentary
✓ ENDS with education - nothing after"""

        return await self.generate_content(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=2000
        )

    async def generate_cover_letter(self,
                                   job_data: Dict[str, Any],
                                   facts: Dict[str, Any],
                                   positioning: Dict[str, Any],
                                   voice_blend: Dict[str, int]) -> str:
        """Generate a tailored cover letter for a specific job.

        Args:
            job_data: Job information
            facts: Verified facts about the candidate
            positioning: Positioning strategy with hook
            voice_blend: Voice calibration percentages

        Returns:
            Generated cover letter content
        """
        system_prompt = f"""You are an expert cover letter writer creating a DIRECT, CONCISE cover letter (300 words MAX, 4 paragraphs).

CRITICAL: NO HALLUCINATION - Use ONLY verified facts from the provided JSON. NEVER make up companies, roles, or experiences.

EXACT STRUCTURE TO FOLLOW:

1. COMPANY HOOK (1-2 sentences, company's current moment):
Examples:
- Capital One: "Capital One's completion of the Discover acquisition creates the perfect moment for AI platform transformation - exactly when developer tooling becomes mission-critical. Your Gen AI SDK Experiences team's focus on empowering developers to 'rapidly bring state-of-the-art Gen AI experiences to market' directly parallels the challenge I solved at [CURRENT_COMPANY]."
- Superhuman: "Superhuman's acquisition by Grammarly signals something profound about the future of email. While others chase features, you've proven that methodical craft wins."

2. YOUR PARALLEL EXPERIENCE (The "I solved this" paragraph - 80-100 words):
MUST use real experience from verified facts:
- For AI roles: Use [CURRENT_COMPANY] AI implementation story
- For marketplace: Use [PREVIOUS_COMPANY_2] 47 experiments story
- For enterprise: Use [PREVIOUS_COMPANY_1] IKEA partnership story

Example format:
"When I joined [CURRENT_COMPANY], I discovered that I was spending 80% of my time on repetitive tasks instead of strategic platform development. Rather than accept this, I partnered with engineering to implement various LLM models across our workflows with systematic evaluation frameworks. The result: [XX]% efficiency improvement improvements that freed me to identify $6M in previously hidden opportunities. This taught me that powerful AI tools work best when they integrate seamlessly into existing developer workflows - your team's exact mission."

3. PATTERN RECOGNITION (Different company - 60-80 words):
"My approach centers on identifying patterns others miss, then building cross-functional consensus around scalable solutions. At [PREVIOUS_COMPANY_1], I established an API-first architecture enabling our IKEA partnership that generated 319,950 store visits. At [PREVIOUS_COMPANY_2], I built systematic A/B testing spanning 47 experiments that achieved [XX]% retention rate rates and successful exit. Having managed teams from 15 to 50+ people, I understand the technical and organizational challenges of scaling AI tooling across enterprise teams."

4. CLOSING (30-40 words):
"Your timing is remarkable - [specific company moment/news]. I'm excited about helping [Company] [specific goal from JD] during this transformational moment."

MUST END WITH:
Best regards,
[YOUR_NAME]

ABSOLUTE RULES:
- Use ONLY the 4 companies from facts: [CURRENT_COMPANY], [PREVIOUS_COMPANY_1], [PREVIOUS_COMPANY_2], [PREVIOUS_COMPANY_3]
- NO made-up companies or roles
- NO generic statements
- Include specific metrics from facts
- Reference real company news/leaders when known
- ALWAYS sign as "[YOUR_NAME]" (never "[Your Name]")
- NO contact info in signature, just name"""

        user_prompt = f"""Generate a CONCISE cover letter for:
Company: {job_data.get('company', 'Unknown')}
Role: {job_data.get('role', 'Product Manager')}

Key Job Requirements:
{job_data.get('description', '')[:800]}

Verified Facts (USE ONLY THESE - NO HALLUCINATION):
{json.dumps(facts, indent=2)[:2500]}

COMPANY-SPECIFIC HOOKS:
{self._get_company_hooks(job_data.get('company', ''))}

PARAGRAPH SELECTION GUIDE:
1. Hook: Reference company's CURRENT moment (acquisition, product launch, etc.)
2. Main story: Choose ONE based on role:
   - AI/Platform roles → [CURRENT_COMPANY] AI story ([XX]% efficiency improvement, $[X]M+ ARR opportunities)
   - Growth roles → [PREVIOUS_COMPANY_2] experiments (47 tests, [XX]% retention rate)
   - Enterprise → [PREVIOUS_COMPANY_1] IKEA (319,950 visits, 15-20 team)
   - Marketplace → [CURRENT_COMPANY] transactions (375K analyzed) or [PREVIOUS_COMPANY_2] scale
3. Secondary proof: Use DIFFERENT company showing pattern recognition
4. Close: Reference timing and specific JD language

WORD LIMITS:
- Total: 300 words MAX
- P1: 40-50 words
- P2: 80-100 words
- P3: 60-80 words
- P4: 30-40 words

NO PHILOSOPHICAL OPENINGS. START WITH COMPANY, NOT YOU.
NEVER use placeholder text like "[Your Name]" - always sign as "[YOUR_NAME]"
ALWAYS end letter with:
Best regards,
[YOUR_NAME]"""

        return await self.generate_content(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.8,
            max_tokens=1500
        )

    def _get_company_hooks(self, company: str) -> str:
        """Get company-specific hooks for cover letter."""
        hooks = {
            'Capital One': "Hook: 'Capital One's completion of the Discover acquisition creates the perfect moment for AI platform transformation - exactly when developer tooling becomes mission-critical.' Reference: Gen AI SDK Experiences team, Prem Natarajan, Aparna Sinha",
            'Superhuman': "Hook: 'Superhuman's acquisition by Grammarly signals something profound about the future of email.' Reference: 40% very disappointed benchmark, manual onboarding, craft over convenience",
            'ResortPass': "Hook: 'ResortPass's spa category launch reveals the untapped potential in day-use hospitality.' Reference: 1800+ partners, Series B $30M, marketplace transformation",
            'Etsy': "Hook: 'Etsy's AI-powered discovery across 100M unique items shows how personalization scales craft.' Reference: algotorial curation, Josh Silverman's vision",
            'Plaid': "Hook: 'Plaid's expansion beyond connections - now 20% ARR from new products - proves infrastructure evolves.' Reference: serving half of Americans, developer-first"
        }
        return hooks.get(company, "Research recent company news, product launches, funding, or strategic initiatives")

    def _get_primary_story(self, role: str, description: str) -> str:
        """Select primary story based on role type."""
        if 'growth' in role.lower() or 'growth' in description.lower():
            return "Use [PREVIOUS_COMPANY_2] story: 47 A/B tests leading to [XX]% retention rate (2.3x industry), systematic experimentation"
        elif 'marketplace' in description.lower():
            return "Use [CURRENT_COMPANY] or [PREVIOUS_COMPANY_2]: two-sided dynamics, liquidity building, network effects"
        elif 'enterprise' in role.lower() or 'b2b' in description.lower():
            return "Use [PREVIOUS_COMPANY_1] story: IKEA partnership, enterprise pivot, 319,950 visits"
        elif '0-to-1' in description.lower() or 'new venture' in description.lower():
            return "Use [PREVIOUS_COMPANY_2] founding story: building from zero, achieving exit"
        else:
            return "Choose most relevant experience based on JD requirements"