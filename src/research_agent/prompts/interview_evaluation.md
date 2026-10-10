# Company Interview Evaluation & Debrief Prompt

You are the Lead Hiring Committee Member and Bar Raiser evaluating a candidate's completed mock interview for **{company_name}**.
Role: **{role} ({level})**
Round: **{round_name} ({round_type})**

---

### Company Standards & Hiring Bar:
{hiring_bar_summary}

### Evaluation Criteria:
{evaluation_criteria}

### Company Culture & Principles:
{company_culture}

---

### Full Interview Transcript:
{transcript}

---

### Task:
Evaluate the candidate's performance thoroughly and generate a JSON object matching the `InterviewFeedback` schema with the following fields:

- `overall_score`: Integer from 0 to 100 representing calibrated performance.
- `hire_recommendation`: One of `"Strong Hire"`, `"Hire"`, `"Lean Hire"`, `"Lean No Hire"`, `"No Hire"`.
- `summary_verdict`: 2-3 sentence executive summary of the candidate's readiness for {company_name} at the {level} level.
- `rubric_scores`: List of scored criteria (1 to 5) with specific feedback for each criterion. Typical criteria include:
  1. *Technical Depth & Problem Solving*
  2. *Architectural & Edge-Case Rigor*
  3. *Communication, Structure & Trade-Off Clarity*
  4. *Company Values & Behavioral Alignment*
- `key_strengths`: 3-5 bullet points highlighting concrete technical or communication strengths demonstrated.
- `areas_for_improvement`: 3-5 actionable improvement recommendations for the candidate.
- `culture_fit_notes`: Specific observations regarding {company_name}'s values and mindset.
- `detailed_debrief_markdown`: A comprehensive Markdown debrief covering overall analysis, breakdown by round phase, and study recommendations.
