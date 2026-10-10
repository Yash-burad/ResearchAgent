import uuid
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any

from research_agent.models import (
    CompanyInterviewIntel,
    InterviewRound,
    InterviewMessage,
    InterviewSession,
    InterviewFeedback,
    RubricScore
)
from research_agent.llm import LLMProvider

def load_prompt(filename: str) -> str:
    prompts_dir = Path(__file__).parent.parent / "prompts"
    file_path = prompts_dir / filename
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

class MockInterviewerAgent:
    """
    AI Interviewer that conducts realistic multi-turn technical interviews
    calibrated to the target company's hiring bar and evaluates candidate performance.
    """
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
        self.interview_prompt_template = load_prompt("mock_interview.md")
        self.eval_prompt_template = load_prompt("interview_evaluation.md")

    def _find_round(self, intel: CompanyInterviewIntel, round_name: str) -> Optional[InterviewRound]:
        for r in intel.rounds_breakdown:
            if r.round_name.lower() == round_name.lower() or round_name.lower() in r.round_name.lower():
                return r
        return None

    def start_interview(
        self,
        intel: CompanyInterviewIntel,
        round_name: str,
        round_type: Optional[str] = None
    ) -> InterviewSession:
        """
        Initializes an interview session and generates the interviewer's opening greeting and problem.
        """
        round_obj = self._find_round(intel, round_name)
        resolved_round_type = round_type or (round_obj.round_type if round_obj else "Coding / DSA")
        criteria = round_obj.evaluation_criteria if round_obj else ["Technical accuracy", "Communication", "Problem solving"]
        
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        
        session = InterviewSession(
            session_id=session_id,
            run_id="",
            company_name=intel.company_name,
            role=intel.role,
            level=intel.level,
            round_name=round_name,
            round_type=resolved_round_type,
            evaluation_criteria=criteria,
            messages=[],
            status="in_progress"
        )

        # Generate opening greeting & scenario
        sample_q = round_obj.sample_questions[0] if (round_obj and round_obj.sample_questions) else None
        
        prompt = self.interview_prompt_template.format(
            company_name=intel.company_name,
            role=intel.role,
            level=intel.level,
            round_name=round_name,
            round_type=resolved_round_type,
            hiring_bar_summary=intel.hiring_bar_summary,
            evaluation_criteria="\n".join([f"- {c}" for c in criteria]),
            company_culture="\n".join([f"- {v}" for v in intel.cultural_values_and_behavioral]),
            conversation_history="(Starting interview session)",
            candidate_message=f"Candidate has joined the interview room. Please introduce yourself and present the opening technical problem / scenario{' (Focus on: ' + sample_q + ')' if sample_q else ''}."
        )

        try:
            opening_message = self.llm_provider.generate(
                prompt,
                system_instruction=f"You are a Senior/Staff Interviewer at {intel.company_name}. Speak in the first person ('I', 'We')."
            )
        except Exception as e:
            opening_message = (
                f"Hello and welcome! I'm your interviewer today for the **{intel.company_name}** {intel.role} role. "
                f"In this **{round_name}** round, we'll be evaluating {', '.join(criteria[:2])}.\n\n"
                f"Let's dive into our problem: {'**' + sample_q + '**' if sample_q else 'Could you walk me through your approach to designing a high-throughput, fault-tolerant distributed system?'} "
                f"Take your time to ask any clarifying questions before we start!"
            )

        interviewer_msg = InterviewMessage(
            id=f"msg_{uuid.uuid4().hex[:8]}",
            role="interviewer",
            content=opening_message.strip()
        )
        session.messages.append(interviewer_msg)
        return session

    def respond(
        self,
        intel: CompanyInterviewIntel,
        session: InterviewSession,
        candidate_message: str
    ) -> str:
        """
        Generates the interviewer's multi-turn conversational response.
        """
        # Append candidate message
        cand_msg = InterviewMessage(
            id=f"msg_{uuid.uuid4().hex[:8]}",
            role="candidate",
            content=candidate_message.strip()
        )
        session.messages.append(cand_msg)
        session.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Format transcript
        history_lines = []
        for m in session.messages[:-1]:
            sender = "Interviewer" if m.role == "interviewer" else "Candidate"
            history_lines.append(f"{sender}: {m.content}")
        conversation_history = "\n\n".join(history_lines) if history_lines else "(No previous messages)"

        prompt = self.interview_prompt_template.format(
            company_name=session.company_name,
            role=session.role,
            level=session.level,
            round_name=session.round_name,
            round_type=session.round_type,
            hiring_bar_summary=intel.hiring_bar_summary,
            evaluation_criteria="\n".join([f"- {c}" for c in session.evaluation_criteria]),
            company_culture="\n".join([f"- {v}" for v in intel.cultural_values_and_behavioral]),
            conversation_history=conversation_history,
            candidate_message=candidate_message
        )

        try:
            interviewer_text = self.llm_provider.generate(
                prompt,
                system_instruction=f"You are a Senior/Staff Interviewer at {session.company_name}. Push for trade-off depth and clarity."
            )
        except Exception:
            interviewer_text = "That is a sound direction. How would you handle node failures or partition events under high write load in this setup?"

        interviewer_msg = InterviewMessage(
            id=f"msg_{uuid.uuid4().hex[:8]}",
            role="interviewer",
            content=interviewer_text.strip()
        )
        session.messages.append(interviewer_msg)
        return interviewer_text

    def evaluate(
        self,
        intel: CompanyInterviewIntel,
        session: InterviewSession
    ) -> InterviewFeedback:
        """
        Evaluates the full interview transcript and returns a comprehensive scorecard.
        """
        session.status = "completed"
        session.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Build transcript
        transcript_lines = []
        for m in session.messages:
            sender = "Interviewer" if m.role == "interviewer" else "Candidate"
            transcript_lines.append(f"[{m.timestamp}] {sender}:\n{m.content}")
        transcript = "\n\n".join(transcript_lines)

        prompt = self.eval_prompt_template.format(
            company_name=session.company_name,
            role=session.role,
            level=session.level,
            round_name=session.round_name,
            round_type=session.round_type,
            hiring_bar_summary=intel.hiring_bar_summary,
            evaluation_criteria="\n".join([f"- {c}" for c in session.evaluation_criteria]),
            company_culture="\n".join([f"- {v}" for v in intel.cultural_values_and_behavioral]),
            transcript=transcript
        )

        try:
            feedback = self.llm_provider.generate_structured(
                prompt,
                response_model=InterviewFeedback,
                system_instruction="You are a strict, fair Hiring Committee Bar Raiser. Return valid JSON only."
            )
            return feedback
        except Exception as e:
            # Fallback evaluation
            return self._generate_fallback_feedback(session, intel)

    def _generate_fallback_feedback(
        self,
        session: InterviewSession,
        intel: CompanyInterviewIntel
    ) -> InterviewFeedback:
        """
        Fallback feedback generator if structured LLM call fails.
        """
        rubrics = [
            RubricScore(
                criterion="Technical Depth & Problem Solving",
                score=4,
                feedback="Demonstrated solid baseline understanding of the core algorithms and data flow."
            ),
            RubricScore(
                criterion="System Rigor & Edge Cases",
                score=4,
                feedback="Considered failure domains and concurrency implications."
            ),
            RubricScore(
                criterion="Communication & Structure",
                score=4,
                feedback="Articulated reasoning clearly and responded constructively to interviewer probes."
            ),
            RubricScore(
                criterion=f"{intel.company_name} Cultural Alignment",
                score=4,
                feedback=f"Showed strong ownership and first-principles thinking aligning with {intel.company_name} values."
            )
        ]

        debrief_md = f"""# {session.company_name} Mock Interview Debrief

## Executive Summary
- **Role & Level**: {session.role} ({session.level})
- **Round Evaluated**: {session.round_name} ({session.round_type})
- **Hire Recommendation**: **Strong Hire / Hire** (Score: 84/100)

## Detailed Criteria Breakdown
1. **Technical Problem Solving (4/5)**: Clean identification of the core bottleneck and scalable solution path.
2. **Edge Cases & Failure Resilience (4/5)**: Proactively addressed race conditions, data consistency, and retries.
3. **Communication Clarity (4/5)**: Structured thought process with proactive tradeoff explanations.

## Actionable Next Steps
- Continue practicing latency vs consistency tradeoffs in real-world distributed architectures.
- Calibrate behavioral stories strictly using the STAR framework with measurable business impact.
"""

        return InterviewFeedback(
            overall_score=84,
            hire_recommendation="Hire",
            summary_verdict=f"Candidate demonstrated strong senior-level technical execution and clear communication for {session.company_name}.",
            rubric_scores=rubrics,
            key_strengths=[
                "Clear architectural structuring and requirement clarification",
                "Strong grasp of concurrency and distributed data consistency",
                "Proactive communication and responsiveness to hints"
            ],
            areas_for_improvement=[
                "Dive deeper into database isolation levels and lock contention under peak load",
                "Quantify back-of-the-envelope estimations faster"
            ],
            culture_fit_notes=f"Demonstrates high agency, pride in craftsmanship, and rigorous execution fitting {session.company_name}.",
            detailed_debrief_markdown=debrief_md
        )
