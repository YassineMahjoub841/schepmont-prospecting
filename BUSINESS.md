# Business Context — Ohio Manufacturing H-1B Sponsorship Intelligence

## Executive summary

This is an end-to-end data project — pipeline plus dashboard — that turns publicly available US Department of Labor H-1B visa disclosure data into a B2B prospecting tool for **Schepmont Group**, a small Ohio-based manufacturing recruitment firm.

The project's headline question:

> **Which Ohio manufacturers are the most attractive sponsorship targets — whether for a recruiter selling them talent or for a candidate seeking an offer?**

The dashboard answers this through a **sponsorship likelihood score** that ranks manufacturers by their H-1B filing frequency, recency, and approval rate. Every other view on the dashboard either feeds that score or lets a user slice it by role, geography, or sub-sector.

This document explains the business logic behind every choice in the build. **Read it before changing any metric, weight, or filter.**

---

## Who is Schepmont Group?

Schepmont Group, LLC is a small recruitment firm (approximately 4 employees) headquartered in Ohio. They specialize in sourcing talent for the manufacturing industry — machinists, engineers, supply chain professionals, and operations executives — primarily for Rust Belt clients.

Public evidence from their LinkedIn activity, such as a post about *"filling 3 Master Machinist positions for one Northeast Ohio client in less than 3 weeks,"* indicates they operate primarily as a **contingency recruiter** (more on what that means below).

They also run a candidate-facing product called **Job-Hopper**, aimed at workers who require visa sponsorship. Job-Hopper already includes a "sponsorship likelihood rating" feature — which means this project's core metric is directly aligned with a product they already ship.

This project deliberately mirrors both sides of Schepmont's business:

- The **recruiter-facing prospecting use case**: which manufacturers to call this week.
- The **candidate-facing sponsorship-discovery use case**: which employers a sponsorship-seeking candidate should target.

---

## How a recruitment firm makes money

Recruiting firms use several business models. The most common — and what Schepmont's posts strongly suggest — is **contingency recruiting**:

1. A company has an open role they cannot fill internally.
2. They engage a recruiter to source qualified candidates.
3. The recruiter screens candidates and presents the strongest ones to the company.
4. **If** the company hires one of those candidates, the recruiter collects a fee — typically **20–30% of the new hire's first-year salary**.
5. **If no hire happens, the recruiter earns nothing.**

This model has three operational consequences that drive every design decision in this project:

- **Prospecting is everything.** No client engagement means no revenue. Finding the right manufacturers to call is the recruiter's #1 daily problem.
- **Hard-to-fill roles are the high-value roles.** Easy roles get filled by the company's in-house HR team — the recruiter never sees them. The roles the recruiter actually gets paid for are the ones internal hiring failed at.
- **High-salary roles pay better commissions.** Twenty percent of $120K is much more than twenty percent of $60K. A recruiter prefers premium clients who pay premium salaries.

A useful tool for Schepmont must therefore help them: **find manufacturers, with active and hard-to-fill open roles, that pay well.** That is exactly what H-1B sponsorship data reveals.

---

## What is "sponsorship"?

In the United States, foreign workers cannot work legally without authorization. The most common work visa for skilled professional roles is the **H-1B**.

A foreign worker cannot apply for an H-1B themselves. A US employer must petition the government on their behalf. That act — the employer formally backing the foreign worker's right to come and work in the US — is called **sponsorship**.

Sponsorship is not casual. The employer incurs:

- **$2,000–$5,000+** in government filing fees per case
- **$3,000–$8,000** in immigration attorney fees per case
- **Several months to over a year** of process time
- **Legal obligations**, including paying at least the "prevailing wage" for that role and location
- **Lottery risk**: the H-1B is capped at 85,000 visas per year and awarded by random selection — the employer might do all the paperwork and still lose the slot

The takeaway: **employers sponsor only when they cannot reasonably fill the role any other way.** Sponsorship is reserved for positions where the talent shortage is severe enough to justify the cost, time, and uncertainty.

---

## Why LCA data is the right signal

Sponsorship leaves a public paper trail. The first regulatory step is the **Labor Condition Application (LCA)**, filed with the US Department of Labor before any H-1B petition can be submitted to USCIS. LCAs are published quarterly and contain:

- Employer name and NAICS sector code
- Job title and SOC occupation code
- Worksite city, state, and ZIP
- Wage rate offered AND prevailing wage for the role
- Full-time vs part-time
- Case status (certified, denied, withdrawn)

Every certified LCA represents a real employer publicly declaring three things at once:

1. **"We have an open position right now."** Concrete, time-stamped hiring signal — far better than a vague press release about growth.
2. **"We could not fill this role locally and are willing to spend $5–10K plus a year of process to fill it via sponsorship."** Strong evidence the role is genuinely hard to fill — the exact situation where a contingency recruiter adds the most value.
3. **"Here is the exact salary we will pay."** Up-front visibility into commission size.

For a contingency recruiter, this is a near-perfect prospecting signal — far richer than the typical "company is hiring" rumors that sales teams chase. For a sponsorship-seeking candidate, it is direct proof that an employer is willing to go through the process.

---

## Why narrow the scope to Ohio + manufacturing + FY2025

The narrow scope is itself part of the message. It demonstrates that the analyst:

- **Understands the client's actual market**: Schepmont's clients are Ohio manufacturers. Anything else is noise.
- **Can scope a project realistically**: A junior analyst who delivers a polished, focused product in four weeks is more valuable than one who delivers a sprawling half-finished one.
- **Knows where to draw the line on data sources**: Adding USCIS approval data, BLS wage benchmarks, or multi-year trends would each be a reasonable extension but would also dilute the core narrative and blow the timeline.

The trade-off is acknowledged in the case study: future enhancements (multi-year trends, OEWS benchmarking, full Rust Belt coverage) are listed as "natural next steps" rather than gaps.

---

## Business questions the dashboard answers

### For Schepmont's business development (the primary use case)

| Question | What the answer tells them |
|----------|----------------------------|
| Which Ohio manufacturers are the largest H-1B sponsors? | Top prospects for outbound sales calls. |
| Which sponsors are growing their filing volume quarter over quarter? | Accounts that are scaling hiring and likely under-resourced. |
| Which roles are sponsored most often? | Where Schepmont should focus candidate sourcing investment. |
| Which manufacturing sub-sectors (machinery, transportation equipment, fabricated metals, food) drive the most sponsorship? | Where to specialize practice areas. |
| Which employers pay meaningfully above the prevailing wage? | Premium clients who can afford agency fees. |
| Which MSA (Cleveland, Cincinnati, Columbus, Akron) has the most activity for a given role? | Where to deploy recruiters or attend industry events. |

### For Job-Hopper candidates (the secondary use case)

| Question | What the answer tells them |
|----------|----------------------------|
| Which Ohio manufacturers sponsor my specific role? | Realistic target employer list. |
| What is the typical offered wage at sponsoring employers for my role? | Realistic compensation expectations. |
| Which employers sponsor consistently across quarters, vs. one-off filers? | Reliability signal — repeat sponsors are safer bets. |
| Which Ohio metro has the most activity for my role? | Where to focus the job search geographically. |

---

## The sponsorship likelihood score

The dashboard's headline metric. It collapses three signals into a single ranking per employer, scaled 0–100.

### Formula

```
score = 0.4 × frequency_norm + 0.3 × recency_norm + 0.3 × approval_rate_norm
```

### Components

- **Frequency** — number of LCAs filed by the employer in FY2025. More filings = more active sponsor.
- **Recency** — quarters since the employer's most recent filing, inverted so recent = high.
- **Approval rate** — certified filings divided by total filings (certified + denied + withdrawn). High = the employer is competent at the process and is unlikely to waste a candidate's time.

Each component is min-max normalized across the Ohio manufacturing population, then combined with the weights above and rescaled to 0–100.

### Why these weights

- **Frequency is weighted highest** because it is the strongest single predictor of future sponsorship behavior — a manufacturer that sponsored 20 people in FY2025 is much more likely to sponsor in FY2026 than one that sponsored once.
- **Recency and approval rate are weighted equally and below frequency** because they are quality filters: a high-frequency sponsor whose last filing was four quarters ago, or whose approval rate is 30%, is a less attractive prospect than a moderate-frequency consistent sponsor.

The weights are intentionally simple and defensible. A more sophisticated version could incorporate wage premium, sub-sector concentration, or year-over-year growth — these are listed as future enhancements in the case study.

### Why it matters

A high score tells the recruiter: this employer sponsors regularly, sponsored recently, and gets approved. It is a high-probability prospect with proven willingness to invest in hard-to-fill hires. From a candidate's perspective, it is a high-probability sponsor.

---

## Use case scenarios

### Scenario A — Monday morning prospecting

Mark Montgomery, Director of Operations at Schepmont, opens the dashboard on a Monday morning. He filters to the Cleveland MSA and the machinery sub-sector (NAICS 333). He sees a ranked list of 12 manufacturers. The top three each filed 8–15 LCAs in FY2025, all for mechanical and industrial engineer roles paying $85,000–$110,000. He now has, in one screen: a target list, the roles to lead with, and a rough commission estimate per placement.

### Scenario B — Candidate targeting (Job-Hopper user)

A mechanical engineer in North Africa, planning a move to the US and needing sponsorship, opens Job-Hopper. They filter by their role and Ohio. They see a list of 25 employers, ranked by sponsorship likelihood, with median offered wages and sponsorship-consistency indicators. They have a credible target list in priority order, with realistic salary expectations — without having to interpret raw government data themselves.

### Scenario C — Strategic service expansion

The dashboard reveals that Ohio's transportation-equipment sub-sector (NAICS 336) saw a 40% increase in industrial-engineer sponsorship filings between Q1 and Q4 of FY2025. Schepmont's leadership uses this to justify building a dedicated industrial-engineer candidate pipeline for that sub-sector. This is the kind of strategic insight an in-house BI report would normally take a consultancy weeks to produce.

---

## Success criteria for this project

The portfolio project is successful if a recruiter or hiring manager at Schepmont can answer "yes" to all of the following after spending 5–10 minutes with the dashboard, the README, and the case study:

1. **Does the candidate understand our business model?** The case study should make this obvious within 60 seconds.
2. **Would this dashboard actually be useful to us on a Monday morning?** The answer should feel concretely yes, not theoretically maybe.
3. **Could this person build the pipeline behind the dashboard, not just the dashboard itself?** The architecture diagram and the GitHub repo make the engineering work visible.
4. **Is the work polished enough to suggest the candidate ships at this quality consistently?** Working dashboard link, clean repo, dbt tests passing, professional Loom walkthrough.

Everything in the project — the dashboard, the score, the README, the Loom video, the one-page case study — exists to surface "yes" to those four questions as quickly as possible.

---

## What this project deliberately does NOT do

- It does not assume Schepmont has asked for a data product — they haven't.
- It does not present itself as a solution or a product pitch. It is evidence of a thought process and a skill set.
- It does not include personal data, scraping of LinkedIn, or any privacy-sensitive material.
- It does not cover the full US, every sector, or multi-year trends. The narrow scope is the point.

A junior analyst who can scope correctly is more valuable than one who tries to boil the ocean. This project is designed to make that point without ever stating it explicitly.
