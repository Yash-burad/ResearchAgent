from pathlib import Path
import re
import os
import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from research_agent.llm import get_llm_provider, LLMProvider

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"
BACKUPS_DIR = PROMPTS_DIR / ".backups"

PROMPT_METADATA = {
    # Tech Topics
    "topic_agent.md": {
        "domain": "tech_topics",
        "title": "Topic Discoverer Agent",
        "agent_class": "TopicAgent",
        "description": "Synthesizes candidates and tech trends from search snippets.",
        "sample_inputs": {
            "user_interests": "Distributed Systems, Vector Databases, eBPF",
            "search_results": "Title: eBPF Linux Observability\nSnippet: High-performance Linux kernel tracing standard.\nURL: https://ebpf.io"
        }
    },
    "fine_tuner_agent.md": {
        "domain": "tech_topics",
        "title": "Fine Tuner & Relevance Agent",
        "agent_class": "FineTunerAgent",
        "description": "Evaluates candidate topics against user interests and computes multi-factor interview relevance scores.",
        "sample_inputs": {
            "user_interests": "AI Infrastructure, Distributed Systems",
            "candidates": '[{"title": "Model Context Protocol (MCP)", "category": "AI Infra", "trend_score": 9, "estimated_interview_value": 9, "short_description": "Open standard unifying AI tool integration."}]',
            "max_selected": 3
        }
    },
    "researcher_agent.md": {
        "domain": "tech_topics",
        "title": "Deep Researcher Agent",
        "agent_class": "ResearcherAgent",
        "description": "Deconstructs web articles and documentation into structured technical notes.",
        "sample_inputs": {
            "topic": "Model Context Protocol (MCP)",
            "expected_outcome": "Understand JSON-RPC transport and client-server architecture",
            "source_data": "MCP standardizes how applications provide context to LLMs using JSON-RPC 2.0."
        }
    },
    "summariser_agent.md": {
        "domain": "tech_topics",
        "title": "Synthesis & Summariser Agent",
        "agent_class": "SummariserAgent",
        "description": "Transforms structured notes into comprehensive architectural deep-dive cheat sheets.",
        "sample_inputs": {
            "topic": "Model Context Protocol (MCP)",
            "notes_json": '{"topic": "Model Context Protocol (MCP)", "definition": "An open standard protocol.", "technical_details": ["JSON-RPC 2.0", "stdio transport"]}'
        }
    },
    # Interview Intel & Simulator
    "interview_intel.md": {
        "domain": "interview_experience",
        "title": "Company Interview Intel Agent",
        "agent_class": "InterviewIntelAgent",
        "description": "Extracts interview blueprints, round breakdowns, hiring bars, and cultural principles from web debriefs.",
        "sample_inputs": {
            "company_name": "Stripe",
            "role": "Staff Software Engineer",
            "level": "L6 / Staff",
            "crawled_data": "Stripe practical coding round uses an existing codebase to add features and fix test suites."
        }
    },
    "mock_interview.md": {
        "domain": "interview_experience",
        "title": "Mock Interviewer Agent",
        "agent_class": "MockInterviewerAgent",
        "description": "Conducts realistic, multi-turn technical and behavioral interview simulations with real-time feedback.",
        "sample_inputs": {
            "company_name": "Google",
            "role": "Senior Software Engineer",
            "round_name": "System Design",
            "round_type": "System Design",
            "conversation_history": "Interviewer: Design a global distributed rate limiter.\nCandidate: Let's use Token Bucket with Redis.",
            "candidate_message": "We can distribute Redis counters across regions and sync asynchronously."
        }
    },
    "interview_evaluation.md": {
        "domain": "interview_experience",
        "title": "Hiring Committee Evaluation Agent",
        "agent_class": "MockInterviewerAgent",
        "description": "Evaluates completed interview transcripts across rubric competencies and delivers Hiring Committee scorecards.",
        "sample_inputs": {
            "company_name": "Meta",
            "role": "Software Engineer",
            "level": "E5 / Senior",
            "round_name": "Coding (DSA)",
            "round_type": "DSA / Coding",
            "hiring_bar_summary": "Top-tier speed and optimal algorithmic space/time complexity.",
            "session_transcript": "Interviewer: Find all anagrams in a string.\nCandidate: Sliding window approach in O(N)."
        }
    },
    # Stock Market Intelligence
    "stock_entity_resolution.md": {
        "domain": "stock_market",
        "title": "Stock Entity Resolution Agent",
        "agent_class": "StockEntityAgent",
        "description": "Resolves user queries to ticker, company profiles, revenue segments, and monetization models.",
        "sample_inputs": {
            "user_query": "NVDA",
            "market_data": "{'ticker': 'NVDA', 'company_name': 'NVIDIA Corp', 'current_price': 120.0}"
        }
    },
    "stock_financial_analysis.md": {
        "domain": "stock_market",
        "title": "Stock Financial & Health Agent",
        "agent_class": "StockFinancialAgent",
        "description": "Analyzes 5-year financial statements, margin trajectories, capital allocation, and solvency.",
        "sample_inputs": {
            "ticker": "NVDA",
            "company_name": "NVIDIA Corp",
            "financial_statements_data": "[{'year': 2025, 'revenue': 96000, 'operating_margin': 62.0, 'net_income': 53000, 'free_cash_flow': 40000}]"
        }
    },
    "stock_valuation_analysis.md": {
        "domain": "stock_market",
        "title": "Stock Valuation & DCF Agent",
        "agent_class": "StockValuationAgent",
        "description": "Evaluates relative multiples and translates 3-tier DCF scenarios into institutional insights.",
        "sample_inputs": {
            "ticker": "NVDA",
            "company_name": "NVIDIA Corp",
            "current_price": 120.0,
            "valuation_multiples": "{'pe_forward': 32.5, 'ev_ebitda': 28.0}",
            "dcf_scenarios": "[{'scenario_name': 'Base', 'target_price_implied': 145.0, 'upside_downside_percent': 20.8}]"
        }
    },
    "stock_peer_analysis.md": {
        "domain": "stock_market",
        "title": "Stock Peer Benchmarking & Moat Agent",
        "agent_class": "StockPeerAgent",
        "description": "Benchmarks growth, margins, and ROIC against competitors and deconstructs structural moats.",
        "sample_inputs": {
            "ticker": "NVDA",
            "company_name": "NVIDIA Corp",
            "sector": "Technology",
            "industry": "Semiconductors",
            "peers_data": "[{'ticker': 'AMD', 'company_name': 'Advanced Micro Devices', 'pe_forward': 30.0}]"
        }
    },
    "stock_news_deduplication.md": {
        "domain": "stock_market",
        "title": "Stock News & Sentiment Agent",
        "agent_class": "StockNewsAgent",
        "description": "Clusters duplicate wire stories, filters transitory noise, and extracts material catalysts.",
        "sample_inputs": {
            "ticker": "NVDA",
            "company_name": "NVIDIA Corp",
            "raw_news_items": "[{'title': 'Blackwell Volume Shipments Ramp in Q4', 'source': 'Reuters', 'snippet': 'Data center demand intact.'}]"
        }
    },
    "stock_earnings_analysis.md": {
        "domain": "stock_market",
        "title": "Stock Earnings & Guidance Agent",
        "agent_class": "StockEarningsAgent",
        "description": "Reviews historical earnings surprise track record and detects management tone shifts.",
        "sample_inputs": {
            "ticker": "NVDA",
            "company_name": "NVIDIA Corp",
            "earnings_data": "{'history': [{'quarter': 'Q3 2025', 'revenue_surprise': 6.2, 'eps_surprise': 8.5}]}"
        }
    },
    "stock_critic_disconfirmation.md": {
        "domain": "stock_market",
        "title": "Adversarial Critic & Disconfirmation Agent",
        "agent_class": "StockCriticAgent",
        "description": "Institutional short-seller persona that challenges bullish assumptions and defines quantitative invalidation triggers.",
        "sample_inputs": {
            "ticker": "NVDA",
            "company_name": "NVIDIA Corp",
            "sector": "Technology",
            "industry": "Semiconductors",
            "current_price": 120.0,
            "preliminary_synthesis": "{'thesis': 'Uncontested AI accelerator monopoly with expanding gross margins.'}"
        }
    },
    "stock_research_synthesis.md": {
        "domain": "stock_market",
        "title": "Stock Institutional Synthesis Agent",
        "agent_class": "StockSynthesisAgent",
        "description": "Compiles the comprehensive 21-section institutional equity research report with sourced evidence.",
        "sample_inputs": {
            "ticker": "NVDA",
            "company_name": "NVIDIA Corp",
            "current_price": 120.0,
            "profile_data": "{'ticker': 'NVDA', 'company_name': 'NVIDIA Corp'}",
            "financial_data": "{'trajectory': 'Improving'}",
            "valuation_data": "{'scenarios': []}",
            "peer_data": "{'structural_moat_factors': ['CUDA ecosystem']}",
            "news_data": "{'recent_events': []}",
            "earnings_data": "{'quarterly_history': []}",
            "critic_data": "{'thesis_invalidation_triggers': ['Hyperscaler CapEx deceleration']}"
        }
    },
    "stock_macro_sector.md": {
        "domain": "stock_market",
        "title": "Stock Macro & Sector Regime Agent",
        "agent_class": "StockMacroAgent",
        "description": "Evaluates interest rate regimes, fiscal tailwinds, and sector rotations for opportunity discovery.",
        "sample_inputs": {
            "sector_filter": "Technology"
        }
    },
    "stock_opportunity_analysis.md": {
        "domain": "stock_market",
        "title": "Stock Dislocation & Screener Agent",
        "agent_class": "StockDislocationAgent",
        "description": "Identifies high-conviction market dislocations and categorizes actionable investment archetypes.",
        "sample_inputs": {
            "macro_context": "{'macro_summary': 'Stabilizing rates and high capital expenditure in cloud computing.'}",
            "screened_candidates": "[{'ticker': 'NVDA', 'current_price': 120.0, 'opportunity_archetype': 'Quality Growth + Temporary Selloff'}]"
        }
    }
}

class PromptItem(BaseModel):
    filename: str
    domain: str
    title: str
    agent_class: str
    description: str
    variables: List[str]
    size_bytes: int
    last_modified: str
    is_modified: bool
    sample_inputs: Dict[str, Any]

class PromptDetail(BaseModel):
    filename: str
    domain: str
    title: str
    agent_class: str
    description: str
    content: str
    variables: List[str]
    is_modified: bool
    sample_inputs: Dict[str, Any]

class PromptManager:
    @staticmethod
    def _ensure_backups_dir():
        BACKUPS_DIR.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def extract_variables(template: str) -> List[str]:
        """Extracts {variable} placeholders from markdown prompt templates."""
        matches = re.findall(r'\{([a-zA-Z0-9_]+)\}', template)
        # Deduplicate while preserving order
        seen = set()
        variables = []
        for m in matches:
            if m not in seen:
                seen.add(m)
                variables.append(m)
        return variables

    @classmethod
    def list_prompts(cls) -> List[PromptItem]:
        cls._ensure_backups_dir()
        items = []
        
        for md_file in sorted(PROMPTS_DIR.glob("*.md")):
            filename = md_file.name
            meta = PROMPT_METADATA.get(filename, {
                "domain": "other",
                "title": filename.replace(".md", "").replace("_", " ").title(),
                "agent_class": "Agent",
                "description": "Agent prompt template.",
                "sample_inputs": {}
            })
            
            content = md_file.read_text(encoding="utf-8")
            variables = cls.extract_variables(content)
            stat = md_file.stat()
            backup_file = BACKUPS_DIR / filename
            is_modified = backup_file.exists()

            items.append(PromptItem(
                filename=filename,
                domain=meta["domain"],
                title=meta["title"],
                agent_class=meta["agent_class"],
                description=meta["description"],
                variables=variables,
                size_bytes=stat.st_size,
                last_modified=datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                is_modified=is_modified,
                sample_inputs=meta.get("sample_inputs", {})
            ))
        return items

    @classmethod
    def get_prompt(cls, filename: str) -> PromptDetail:
        file_path = PROMPTS_DIR / filename
        if not file_path.exists() or not file_path.is_file():
            raise FileNotFoundError(f"Prompt template {filename} not found.")

        content = file_path.read_text(encoding="utf-8")
        variables = cls.extract_variables(content)
        meta = PROMPT_METADATA.get(filename, {
            "domain": "other",
            "title": filename.replace(".md", "").replace("_", " ").title(),
            "agent_class": "Agent",
            "description": "Agent prompt template.",
            "sample_inputs": {}
        })
        backup_file = BACKUPS_DIR / filename
        is_modified = backup_file.exists()

        return PromptDetail(
            filename=filename,
            domain=meta["domain"],
            title=meta["title"],
            agent_class=meta["agent_class"],
            description=meta["description"],
            content=content,
            variables=variables,
            is_modified=is_modified,
            sample_inputs=meta.get("sample_inputs", {})
        )

    @classmethod
    def update_prompt(cls, filename: str, new_content: str) -> PromptDetail:
        cls._ensure_backups_dir()
        file_path = PROMPTS_DIR / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Prompt template {filename} not found.")

        # Save initial backup if not already saved
        backup_file = BACKUPS_DIR / filename
        if not backup_file.exists():
            original_content = file_path.read_text(encoding="utf-8")
            backup_file.write_text(original_content, encoding="utf-8")

        file_path.write_text(new_content, encoding="utf-8")
        return cls.get_prompt(filename)

    @classmethod
    def reset_prompt(cls, filename: str) -> PromptDetail:
        file_path = PROMPTS_DIR / filename
        backup_file = BACKUPS_DIR / filename

        if backup_file.exists():
            original_content = backup_file.read_text(encoding="utf-8")
            file_path.write_text(original_content, encoding="utf-8")
            backup_file.unlink(missing_ok=True)

        return cls.get_prompt(filename)

    @classmethod
    def test_prompt(cls, filename: str, variables: Dict[str, Any], provider_name: Optional[str] = None) -> Dict[str, Any]:
        prompt_detail = cls.get_prompt(filename)
        template = prompt_detail.content

        # Format variables safely (replace missing with empty string or placeholder)
        format_kwargs = {}
        for var in prompt_detail.variables:
            val = variables.get(var, f"[{var}]")
            if isinstance(val, (dict, list)):
                format_kwargs[var] = json.dumps(val, indent=2)
            else:
                format_kwargs[var] = str(val)

        try:
            formatted_prompt = template.format(**format_kwargs)
        except Exception as e:
            formatted_prompt = template
            for k, v in format_kwargs.items():
                formatted_prompt = formatted_prompt.replace(f"{{{k}}}", v)

        # Execute with LLM
        start_time = time.time()
        try:
            llm = get_llm_provider(provider_name) if provider_name else get_llm_provider()
            response_text = llm.generate(
                prompt=formatted_prompt,
                system_instruction=f"You are executing prompt test for {prompt_detail.title} ({prompt_detail.agent_class})."
            )
            duration_ms = round((time.time() - start_time) * 1000)
            return {
                "success": True,
                "filename": filename,
                "formatted_prompt": formatted_prompt,
                "response": response_text,
                "duration_ms": duration_ms,
                "provider": getattr(llm, "provider_name", "llm"),
                "error": None
            }
        except Exception as e:
            duration_ms = round((time.time() - start_time) * 1000)
            return {
                "success": False,
                "filename": filename,
                "formatted_prompt": formatted_prompt,
                "response": None,
                "duration_ms": duration_ms,
                "provider": provider_name or "default",
                "error": str(e)
            }
