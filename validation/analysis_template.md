# Survey Results Analysis Template

Use this template to analyze your survey data and make the build/iterate/pivot decision.

---

## Step 1: Export & Clean Data

### Export from Survey Tool

**Google Forms:**
1. Open your form
2. Click "Responses" tab
3. Click green Sheets icon (top right)
4. Opens in Google Sheets
5. File → Download → CSV

**Typeform:**
1. Go to Results
2. Click "..." menu
3. Export responses → CSV

**You now have:** `survey_responses.csv`

---

### Clean the Data

**Remove incomplete responses:**
```
Filter criteria:
- Remove if answered <50% of questions
- Remove if straight-line responses (all same answer)
- Remove if nonsensical text in open-ended questions
```

**Remove spam:**
```
Red flags:
- Email like "asdf@asdf.com"
- Answered in <30 seconds (check timestamp if available)
- All text responses are copy/paste gibberish
```

**Expected loss:** 10-20% of responses to cleaning

**Create cleaned dataset:** `survey_responses_clean.csv`

---

## Step 2: Calculate Key Metrics

### Demographics (Qualification)

**Metric 1: Target Audience %**
```
Question: "Are you currently job searching?"

Calculate:
- Count responses where answer = "Yes, actively" OR "Yes, passively"
- Divide by total responses
- Multiply by 100

Target: 60%+ are job searching

[Your Result: ____%]
```

**Metric 2: Premium User %**
```
Question: "Do you use LinkedIn Premium/Sales Nav?"

Calculate:
- Count responses where answer = "Sales Navigator" OR "Premium/Career"
- Divide by total responses
- Multiply by 100

Target: 30%+ are paying for LinkedIn

[Your Result: ____%]
```

**Metric 3: Active Poster %**
```
Question: "How often do you post on LinkedIn?"

Calculate:
- Count responses where answer = "Multiple times/week" OR "Once a week" OR "2-3 times/month"
- Divide by total responses
- Multiply by 100

Target: 40%+ post at least monthly

[Your Result: ____%]
```

---

### Pain Points (Validation)

**Metric 4: Average Weekly Hours on LinkedIn**
```
Question: "How much time do you spend per week on these activities?"

For each activity:
- Convert ranges to midpoints (1-2hrs = 1.5, 3-5hrs = 4, etc.)
- Calculate average across all responses
- Sum all activities

Target: 5+ hours average per week

[Your Result: ___ hours/week]

Breakdown:
- Writing posts: ___ hrs
- Researching companies: ___ hrs
- Connection messages: ___ hrs
- Tailoring applications: ___ hrs
```

**Metric 5: Top Frustration**
```
Question: "Rank your biggest frustrations"

For each frustration:
- Count how many ranked it #1
- Calculate percentage

Example:
- "Takes too much time": 62% ranked #1
- "Don't know what to post": 18% ranked #1
- etc.

Top Frustration: _______________
% who ranked it #1: ____%

Does this align with your solution? [YES / NO]
```

---

### Solution Fit

**Metric 6: Value Rating**
```
Question: "How valuable would this tool be?"

Calculate:
- % who answered "Very valuable" (4) or "Extremely valuable" (5)
- Average score (1-5 scale)

Target: 40%+ rate it 4-5

[Your Results:]
- % rating 4-5: ____%
- Average score: ___ / 5
- Distribution:
  - 5 (Extremely): ____%
  - 4 (Very): ____%
  - 3 (Somewhat): ____%
  - 2 (Slightly): ____%
  - 1 (Not valuable): ____%
```

---

### Pricing

**Metric 7: Willingness to Pay**
```
Question: "What would you pay per month?"

Calculate distribution:
- $0 (free only): ____%
- $1-19: ____%
- $20-39: ____%
- $40-59: ____%
- $60-79: ____%
- $80-99: ____%
- $100+: ____%
- One-time payment: ____%

Key metrics:
- Median price point: $____
- % willing to pay $40+: ____%
- % willing to pay anything: ____%

Target: 30%+ would pay $40+/month
```

---

### Feature Priority

**Metric 8: Most Wanted Feature**
```
Question: "Which ONE feature would be most valuable?"

Count responses for each:
- AI-generated posts: ____%
- Outreach messages: ____%
- Company research: ____%
- Resume/cover letter: ____%
- Content calendar: ____%
- Analytics: ____%

Winner: _______________

Does this match your MVP plan? [YES / NO]
```

---

### Beta Interest

**Metric 9: Beta Signups**
```
Count:
- Total who said "Yes" to beta: ____
- Total who said "Maybe": ____
- Total beta prospects: ____

Beta signup rate: ____% (beta signups / total responses)

Target: 50+ beta signups

[Your Result: ___ signups]
```

---

## Step 3: Qualitative Analysis

### Review Open-Ended Responses

**Question: "Any other thoughts?"**

Read all responses and categorize into themes:

**Theme 1: [Name it]**
- How many mentioned this: ___
- Example quote: "..."
- Insight: ...

**Theme 2: [Name it]**
- How many mentioned this: ___
- Example quote: "..."
- Insight: ...

**Theme 3: [Name it]**
- How many mentioned this: ___
- Example quote: "..."
- Insight: ...

**Surprising findings:**
- What you didn't expect: ...
- New pain points discovered: ...
- Solutions people already use: ...

---

## Step 4: Cross-Tabulation (Advanced)

### Segment by Job Search Status

**Active Job Seekers vs. Passive Networkers**

Compare metrics between groups:

|  Metric | Active Seekers | Passive Networkers |
|---------|----------------|-------------------|
| Avg hours/week | ___ | ___ |
| % rate valuable (4-5) | ___% | ___% |
| Median price willing to pay | $___ | $___ |
| Beta signup rate | ___% | ___% |

**Insight:** Which segment is more interested? ...

---

### Segment by LinkedIn Subscription

**Sales Nav Users vs. Free Users**

|  Metric | Sales Nav | Premium | Free |
|---------|-----------|---------|------|
| Avg hours/week | ___ | ___ | ___ |
| % rate valuable | ___% | ___% | ___% |
| Median price | $___ | $___ | $___ |

**Insight:** Which segment is your best target? ...

---

### Segment by Posting Frequency

**Active Posters vs. Rare Posters**

|  Metric | Post Weekly+ | Post Monthly | Rarely Post |
|---------|--------------|--------------|-------------|
| Top frustration | ___ | ___ | ___ |
| % rate valuable | ___% | ___% | ___% |
| Beta signup rate | ___% | ___% | ___% |

**Insight:** Are active posters more interested? ...

---

## Step 5: Visualization

### Create These Charts

**Chart 1: Time Spent on LinkedIn Activities**
- Type: Stacked bar chart
- X-axis: Activity (Posts, Research, Messages, Applications)
- Y-axis: Average hours/week
- Show: Total = X hours/week

**Chart 2: Top Frustrations**
- Type: Horizontal bar chart
- X-axis: % who ranked #1
- Y-axis: Frustration type
- Sort: Highest to lowest

**Chart 3: Value Rating Distribution**
- Type: Pie chart or bar chart
- Show: % for each rating (1-5)
- Highlight: 4-5 as "Would use"

**Chart 4: Willingness to Pay**
- Type: Bar chart
- X-axis: Price tiers
- Y-axis: % of responses
- Highlight: Your proposed price point

**Chart 5: Feature Priority**
- Type: Pie chart
- Show: % who selected each feature as #1
- Highlight: Your planned MVP feature

**Tools:**
- Google Sheets (built-in charts)
- Excel
- Tableau Public (free)
- Canva (for better design)

---

## Step 6: Decision Framework

### Use This Scorecard

**Audience Validation (30 points)**
- [ ] 60%+ are actively job searching: 10 pts
- [ ] 40%+ post on LinkedIn regularly: 10 pts
- [ ] 30%+ use Sales Nav/Premium: 10 pts

**Your Score: ___ / 30**

---

**Problem Validation (30 points)**
- [ ] Average 5+ hours/week on LinkedIn: 10 pts
- [ ] Top frustration aligns with solution: 10 pts
- [ ] 70%+ spend 3+ hours on your target activity: 10 pts

**Your Score: ___ / 30**

---

**Solution Validation (30 points)**
- [ ] 40%+ rate it "very/extremely valuable": 15 pts
- [ ] Average rating 3.5+ / 5: 10 pts
- [ ] <20% say "not valuable": 5 pts

**Your Score: ___ / 30**

---

**Monetization Validation (10 points)**
- [ ] 30%+ would pay $40+/month: 5 pts
- [ ] <30% say "free only": 5 pts

**Your Score: ___ / 10**

---

**TOTAL SCORE: ___ / 100**

---

### Decision Matrix

**Score 70-100: ✅ BUILD IT**
```
Strong validation across all dimensions.

Next steps:
1. Email beta signups: "We're building this!"
2. Start Week 1: Core AI engine
3. Target: MVP in 4-6 weeks
4. Keep beta list warm with updates
```

**Score 50-69: ⚠️ ITERATE**
```
Some validation but weak areas.

Identify weak areas:
- If audience wrong: Re-survey better channels
- If problem weak: Validate deeper pain
- If solution weak: Refine value prop
- If pricing weak: Consider different model

Next steps:
1. Identify weakest dimension
2. Run follow-up interviews (10 people)
3. Refine approach
4. Re-validate with smaller survey (50 people)
```

**Score <50: ❌ PIVOT OR STOP**
```
Insufficient validation.

Options:
1. PIVOT: Solve different pain point that emerged
2. DIFFERENT SEGMENT: Target different users
3. STOP: Not a real problem, move to different idea

Next steps:
1. Review open-ended responses
2. Look for alternative problems mentioned
3. Decide if you want to pivot or explore new idea
```

---

## Step 7: Write Summary Report

### Template: One-Page Summary

```markdown
# Survey Results Summary

## Overview
- Survey period: [dates]
- Total responses: [X]
- Clean responses: [X] (after removing spam/incomplete)
- Response sources: Reddit (X%), LinkedIn (X%), Other (X%)

## Key Findings

### Audience
- [X]% actively job searching
- [X]% use Sales Nav or Premium
- Average time on LinkedIn: [X] hours/week

### Problem
- Top frustration: [X] ([X]% ranked #1)
- Average [X] hours/week spent on [target activity]
- [X]% spend 3+ hours/week on content creation

### Solution
- [X]% rate AI voice-matching as "very/extremely valuable"
- Average value rating: [X.X] / 5
- Top feature request: [X] ([X]% chose this)

### Pricing
- Median willingness to pay: $[X]-[X]/month
- [X]% would pay $40+/month
- [X]% prefer one-time payment over subscription

### Beta Interest
- [X] beta signups ([X]% conversion rate)
- Strong interest from: [segment]

## Decision

**VALIDATION SCORE: [X] / 100**

**DECISION: [BUILD / ITERATE / PIVOT]**

Reasoning: ...

## Next Steps
1. ...
2. ...
3. ...

## Surprising Insights
- ...
- ...

## Quotes
> "[Most compelling user quote]"

> "[Second best quote]"

---

*Full dataset available at: [link]*
*Detailed analysis: [link]*
```

---

## Step 8: Archive Everything

### Create Portfolio Assets

**Save these files:**
```
career-os/validation/results/
├── survey_responses_raw.csv
├── survey_responses_clean.csv
├── analysis_summary.md (from template above)
├── charts/
│   ├── time_spent.png
│   ├── frustrations.png
│   ├── value_rating.png
│   ├── pricing.png
│   └── features.png
└── case_study.md (see results_sharing_template.md)
```

**For your portfolio:**
- One-page summary (PDF)
- 3-5 key charts
- Most compelling quotes
- Decision rationale

**For interviews:**
```
"Before building AuthenticHire, I validated demand with 300+ survey responses.

Key finding: 67% rated voice-matched AI content as 'very valuable' and
45% would pay $40-60/month.

This gave me confidence that I was solving a real problem, not just
building something I personally wanted."

[Show charts on screen]
```

---

## Common Analysis Mistakes

### ❌ Don't Do This:

**Mistake 1: Cherry-picking data**
```
Wrong: "50% would pay $60+!" (ignoring that 40% said free only)
Right: "Median price point is $40, with 50% willing to pay $40+"
```

**Mistake 2: Ignoring low scores**
```
Wrong: "Average rating is 3.8!" (ignoring that 30% said "not valuable")
Right: "60% rated it 4-5, but 30% weren't interested"
```

**Mistake 3: Over-rotating on outliers**
```
Wrong: "One person said they'd pay $200/month!"
Right: "Median is $49, range $0-200"
```

**Mistake 4: Confirmation bias**
```
Wrong: Looking only for data that supports building
Right: Actively look for disconfirming evidence
```

---

## Quality Checks

**Before finalizing analysis:**

- [ ] Calculated all key metrics
- [ ] Created visualizations
- [ ] Reviewed qualitative responses
- [ ] Identified surprising findings
- [ ] Checked for segment differences
- [ ] Calculated validation score
- [ ] Made build/iterate/pivot decision
- [ ] Wrote summary report
- [ ] Saved all data and charts
- [ ] Ready to share results publicly

---

## Next Steps Based on Decision

### If BUILD (Score 70+)
→ Go to `../backend/` folder
→ Start Week 1: Core AI Engine
→ Email beta list: "We're building this based on your feedback"
→ Set target: MVP in 4-6 weeks

### If ITERATE (Score 50-69)
→ Identify weakest dimension
→ Conduct 10 follow-up interviews
→ Refine solution
→ Re-validate with 50-person survey

### If PIVOT (Score <50)
→ Review what problems DID emerge as important
→ Decide: Pursue those or try new idea?
→ If pivot: Start research on new problem
→ If stop: Move to different project

---

## Analysis Checklist

- [ ] Exported and cleaned data
- [ ] Calculated all 9 key metrics
- [ ] Created 5 visualizations
- [ ] Reviewed qualitative responses
- [ ] Scored validation (0-100)
- [ ] Made decision (build/iterate/pivot)
- [ ] Wrote one-page summary
- [ ] Saved portfolio assets
- [ ] Ready to share results
- [ ] Ready to start next phase

**Time estimate:** 4-6 hours for thorough analysis

**Good luck! The data will tell you what to do next.**
