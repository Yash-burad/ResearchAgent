import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from research_agent.models import CompanyInterviewIntel, InterviewRound, ResearchSource
from research_agent.llm import LLMProvider
from research_agent.web import search_web, scrape_url, deduplicate_and_rank_sources

def load_prompt(filename: str) -> str:
    prompts_dir = Path(__file__).parent.parent / "prompts"
    file_path = prompts_dir / filename
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

class InterviewIntelAgent:
    """
    Agent that crawls and synthesizes real candidate interview debriefs, question patterns,
    and round structures for a specific company and engineering role.
    """
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
        self.prompt_template = load_prompt("interview_intel.md")

    def research_company(
        self,
        company_name: str,
        role: str = "Senior Software Engineer",
        level: str = "Senior / L5",
        max_sources: int = 5
    ) -> CompanyInterviewIntel:
        """
        Executes targeted web search queries across LeetCode, Reddit, Glassdoor, and blogs,
        scrapes debriefs, and synthesizes structured interview intelligence.
        """
        # 1. Build targeted search queries
        queries = [
            f'"{company_name}" "{role}" interview experience leetcode discuss 2025 2026',
            f'"{company_name}" "{role}" interview questions system design glassdoor reddit',
            f'"{company_name}" engineering hiring process "{level}" rounds',
            f'"{company_name}" behavioral questions leadership principles values'
        ]

        # 2. Search web
        raw_sources = []
        for q in queries:
            results = search_web(q, max_results=3)
            raw_sources.extend(results)

        # 3. Deduplicate and rank
        ranked_sources = deduplicate_and_rank_sources(raw_sources, max_results=max_sources)

        # 4. Scrape debrief pages
        scraped_data_list = []
        sources_models = []

        for idx, src in enumerate(ranked_sources, 1):
            url = src["url"]
            title = src["title"]
            cred_score = src["credibility_score"]

            text_content = scrape_url(url)
            if not text_content:
                text_content = src.get("snippet", "No detailed content extracted.")

            sliced_text = text_content[:3500]

            scraped_data_list.append(
                f"--- Source {idx} ---\n"
                f"Title: {title}\n"
                f"URL: {url}\n"
                f"Credibility Score: {cred_score}/10\n"
                f"Content:\n{sliced_text}\n"
            )

            sources_models.append(
                ResearchSource(
                    url=url,
                    title=title,
                    publisher=None,
                    extracted_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    credibility_score=cred_score,
                    key_points=[]
                )
            )

        scraped_sources_str = "\n".join(scraped_data_list) if scraped_data_list else "No direct debrief pages scraped. Synthesizing from baseline hiring benchmarks."

        # 5. Format prompt
        prompt = self.prompt_template.format(
            company_name=company_name,
            role=role,
            level=level,
            scraped_sources=scraped_sources_str
        )

        system_instruction = (
            f"You are an expert technical recruiter and interview coach specializing in {company_name} "
            f"software engineering hiring bars. Synthesize clear, actionable round-by-round guidance."
        )

        try:
            intel = self.llm_provider.generate_structured(
                prompt=prompt,
                response_model=CompanyInterviewIntel,
                system_instruction=system_instruction
            )
            intel.company_name = company_name
            intel.role = role
            intel.level = level
            intel.sources = sources_models

            if not intel.prep_pack_markdown:
                intel.prep_pack_markdown = self._build_markdown_pack(intel)

            return intel
        except Exception as e:
            print(f"Warning: InterviewIntelAgent structured call failed for {company_name}: {e}. Generating fallback intel.")
            return self._generate_fallback_intel(company_name, role, level, sources_models)

    def _build_markdown_pack(self, intel: CompanyInterviewIntel) -> str:
        md = []
        md.append(f"# {intel.company_name} — {intel.role} ({intel.level})")
        md.append("## Complete Interview Intelligence & Prep Blueprint\n")
        
        md.append("### 🎯 Hiring Bar & Overview")
        md.append(f"{intel.hiring_bar_summary}\n")

        md.append("### 🔄 Interview Rounds Breakdown")
        for idx, round_item in enumerate(intel.rounds_breakdown, 1):
            md.append(f"#### Round {idx}: {round_item.round_name} ({round_item.duration_minutes} mins)")
            md.append(f"- **Type**: `{round_item.round_type}`")
            if round_item.focus_areas:
                md.append(f"- **Focus Areas**: {', '.join(round_item.focus_areas)}")
            if round_item.sample_questions:
                md.append("- **Sample Questions Asked**:")
                for q in round_item.sample_questions:
                    md.append(f"  - {q}")
            if round_item.evaluation_criteria:
                md.append("- **Evaluation Signals (What Interviewers Look For)**:")
                for crit in round_item.evaluation_criteria:
                    md.append(f"  - ✅ {crit}")
            if round_item.tips:
                md.append("- **Pro-Tips & Strategy**:")
                for tip in round_item.tips:
                    md.append(f"  - 💡 {tip}")
            md.append("")

        if intel.top_dsa_patterns:
            md.append("### 💻 Top Coding & DSA Patterns Asked")
            for pat in intel.top_dsa_patterns:
                md.append(f"- **{pat}**")
            md.append("")

        if intel.top_system_design_topics:
            md.append("### 🏗️ Key System Design Architectures Asked")
            for sdt in intel.top_system_design_topics:
                md.append(f"- **{sdt}**")
            md.append("")

        if intel.cultural_values_and_behavioral:
            md.append("### 🤝 Cultural Values & Behavioral Themes")
            for val in intel.cultural_values_and_behavioral:
                md.append(f"- **{val}**")
            md.append("")

        if intel.recent_experiences_summary:
            md.append("### 📝 Recent Candidate Insights & Gotchas (2025/2026)")
            for ins in intel.recent_experiences_summary:
                md.append(f"- {ins}")
            md.append("")

        if intel.sources:
            md.append("### 🔗 Debrief Sources & Citations")
            for s in intel.sources:
                md.append(f"- [{s.title}]({s.url}) (Credibility: {s.credibility_score}/10)")
            md.append("")

        return "\n".join(md)

    def _generate_fallback_intel(
        self,
        company_name: str,
        role: str,
        level: str,
        sources: List[ResearchSource]
    ) -> CompanyInterviewIntel:
        rounds = [
            InterviewRound(
                round_name="Technical Recruiter Screen",
                round_type="Recruiter Screen",
                duration_minutes=30,
                focus_areas=["Resume walk-through", "Timeline", "Expectations & Compensation"],
                sample_questions=["Tell me about your most impactful project", f"Why {company_name}?"],
                evaluation_criteria=["Communication clarity", "Level calibration alignment"],
                tips=["Have 2-minute project elevator pitches ready."]
            ),
            InterviewRound(
                round_name="Technical Phone Screen / OA",
                round_type="Coding / DSA",
                duration_minutes=45,
                focus_areas=["Data Structures", "Algorithms", "Clean Code Execution"],
                sample_questions=["Graph traversal / BFS/DFS problem", "LRU Cache or Sliding Window array problem"],
                evaluation_criteria=["Bug-free syntax", "Optimal time/space complexity", "Proactive test case verification"],
                tips=["Think out loud and verify edge cases before writing final code."]
            ),
            InterviewRound(
                round_name="Onsite: System Design & Architecture",
                round_type="System Design",
                duration_minutes=60,
                focus_areas=["Requirements clarifying", "API Design", "High Availability & Trade-offs"],
                sample_questions=[f"Design a distributed rate limiter for {company_name} API", "Design a real-time event streaming pipeline"],
                evaluation_criteria=["Driving the conversation", "Deep dive into bottleneck mitigation", "Explicit trade-off justification"],
                tips=["Spend first 5 minutes quantifying QPS, storage, and latency SLAs before drawing boxes."]
            ),
            InterviewRound(
                round_name="Onsite: Practical Coding / Bug Squashing",
                round_type="Practical / Bug Squash / API",
                duration_minutes=60,
                focus_areas=["Working with real codebases", "Refactoring", "Testing & Debugging"],
                sample_questions=["Debug a failing integration test suite in a live IDE", "Implement a concurrent rate-limited HTTP client"],
                evaluation_criteria=["IDE proficiency", "Writing unit tests", "Pragmatic modular design"],
                tips=["Read existing test cases carefully before modifying code."]
            ),
            InterviewRound(
                round_name="Onsite: Behavioral & Leadership",
                round_type="Behavioral & Leadership",
                duration_minutes=45,
                focus_areas=["Conflict resolution", "Cross-team collaboration", f"{company_name} core values"],
                sample_questions=["Tell me about a time you disagreed with a technical decision", "Describe your most difficult production outage"],
                evaluation_criteria=["STAR method rigor", "Ownership mindset", "Humility and mentorship"],
                tips=["Prepare 4 core stories mapped to the STAR framework."]
            )
        ]

        intel = CompanyInterviewIntel(
            company_name=company_name,
            role=role,
            level=level,
            hiring_bar_summary=f"{company_name} places a premium on clean code execution, deep system design fundamentals, and strong ownership mindset for {level} roles.",
            rounds_breakdown=rounds,
            top_dsa_patterns=["Trees & Graph Traversals (BFS/DFS)", "Dynamic Programming & Memoization", "Hash Tables & Sliding Window", "Trie & Prefix Trees"],
            top_system_design_topics=["Distributed Caching & Invalidation", "Event-Driven Message Queues (Kafka/Pulsar)", "Sharding & Consistency (Raft/Paxos)", "API Gateway & Rate Limiting"],
            cultural_values_and_behavioral=["Customer Obsession & Bias for Action", "High Standards & Technical Rigor", "Clear Communication & Empathy"],
            recent_experiences_summary=["Heavy emphasis on running code during technical rounds.", "System design rounds prioritize trade-off depth over generic buzzwords.", "Behavioral round is heavily calibrated against leadership expectations."],
            sources=sources
        )
        intel.prep_pack_markdown = self._build_markdown_pack(intel)
        return intel
