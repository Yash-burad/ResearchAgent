from typing import Type, TypeVar, Optional, Any
from pydantic import BaseModel
from research_agent.llm.base import LLMProvider
from research_agent.models import (
    TopicCandidate,
    RefinedTopic,
    ResearchNotes,
    ResearchSource,
    TopicSummary,
    FlashcardsGame,
    FlashcardItem,
    CompanyInterviewIntel,
    InterviewRound,
    InterviewFeedback,
    RubricScore
)



T = TypeVar("T", bound=BaseModel)

class MockProvider(LLMProvider):
    """
    Mock LLM provider for offline testing and fast dry-run demonstrations.
    Returns pre-structured responses matching the requested Pydantic models.
    """
    def __init__(self, model_name: str = "mock-model"):
        self.model_name = model_name

    def generate(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        return f"# Mock LLM Output\nGenerated response for prompt length {len(prompt)}."

    def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_instruction: Optional[str] = None
    ) -> T:
        model_name = response_model.__name__

        if "TopicCandidatesList" in model_name:
            candidates = [
                TopicCandidate(
                    title="Model Context Protocol (MCP)",
                    short_description="An open standard unifying how AI applications integrate with data sources and tools.",
                    category="AI Infrastructure",
                    trend_reason="Rapid industry adoption by Anthropic and developer tooling ecosystems.",
                    evidence_sources=["https://modelcontextprotocol.io", "https://github.com/modelcontextprotocol"],
                    estimated_interview_value=9,
                    trend_score=9
                ),
                TopicCandidate(
                    title="Vector Databases & HNSW Indexing",
                    short_description="Specialized high-performance databases for fast similarity search across embeddings.",
                    category="Databases & Distributed Systems",
                    trend_reason="Core infrastructure for Retrieval-Augmented Generation (RAG) applications at scale.",
                    evidence_sources=["https://qdrant.tech/articles", "https://milvus.io/docs"],
                    estimated_interview_value=8,
                    trend_score=8
                ),
                TopicCandidate(
                    title="Agentic Workflows with LangGraph",
                    short_description="Cyclic state machine orchestration for reliable multi-agent systems and task planning.",
                    category="AI Agents",
                    trend_reason="Shift from linear LLM chains to robust agent loops with state persistence.",
                    evidence_sources=["https://langchain-ai.github.io/langgraph/"],
                    estimated_interview_value=9,
                    trend_score=9
                )
            ]
            return response_model(topics=candidates)

        elif "RefinedTopicsList" in model_name:
            refined = [
                RefinedTopic(
                    title="Model Context Protocol (MCP)",
                    reason_selected="Top match for AI infrastructure and backend developer tooling with immense interview relevance.",
                    relevance_to_user="Aligns directly with AI infrastructure, backend systems, and protocol design.",
                    expected_learning_outcome="Master MCP client-server architecture, JSON-RPC transports, and tool integration patterns.",
                    scores={
                        "interest_match": 9,
                        "interview_value": 9,
                        "depth": 8,
                        "freshness": 9,
                        "source_quality": 9
                    },
                    source_urls=["https://modelcontextprotocol.io"]
                ),
                RefinedTopic(
                    title="Vector Databases & HNSW Indexing",
                    reason_selected="Fundamental for modern backend and distributed systems system design rounds.",
                    relevance_to_user="Key for distributed storage, indexing trade-offs, and scalability.",
                    expected_learning_outcome="Understand HNSW graph construction, memory vs recall trade-offs, and sharding strategies.",
                    scores={
                        "interest_match": 8,
                        "interview_value": 9,
                        "depth": 9,
                        "freshness": 8,
                        "source_quality": 8
                    },
                    source_urls=["https://qdrant.tech/articles"]
                )
            ]
            return response_model(topics=refined)

        elif response_model == ResearchNotes:
            return response_model(
                topic="Model Context Protocol (MCP)",
                definition="An open protocol developed to standardize how AI models and agent runtimes discover, connect to, and execute external tools and contextual resources.",
                why_it_matters=[
                    "Eliminates bespoke point-to-point integrations between LLM apps and developer environments.",
                    "Provides standardized schema discovery, tool invocation, and prompt template sharing.",
                    "Enables secure context isolation and local execution via stdio or Server-Sent Events (SSE)."
                ],
                technical_details=[
                    "Transport layer: Supports stdio for local processes and SSE (Server-Sent Events) over HTTP for networked servers.",
                    "Message Protocol: Standard JSON-RPC 2.0 request/response and notification primitives.",
                    "Primitives: Resources (data/files), Prompts (templates), Tools (executable functions with JSON schema), and Sampling."
                ],
                examples=[
                    "Connecting an IDE assistant to a PostgreSQL database server via a local MCP server.",
                    "Fetching GitHub issue context directly into an AI coding workflow via GitHub MCP server."
                ],
                use_cases=[
                    "Enterprise developer tooling",
                    "Database and filesystem contextualization for coding agents",
                    "Multi-agent collaborative tool networks"
                ],
                limitations=[
                    "Early-stage ecosystem with evolving specifications.",
                    "Transport overhead and connection management for distributed multi-hop agents."
                ],
                related_topics=["JSON-RPC 2.0", "Language Server Protocol (LSP)", "Function Calling", "Agent Tooling"],
                sources=[
                    ResearchSource(
                        url="https://modelcontextprotocol.io",
                        title="Model Context Protocol Specification",
                        publisher="Anthropic",
                        extracted_at="2026-06-13 12:00:00",
                        credibility_score=10,
                        key_points=["Defines client-server architecture", "JSON-RPC 2.0 foundation"]
                    )
                ]
            )

        elif response_model == TopicSummary:
            summary_md = """# Model Context Protocol (MCP)

## One-Line Explanation
An open standard specification that acts as the "USB-C for AI apps", defining how LLM clients discover and communicate with external tools, prompts, and contextual data servers over JSON-RPC.

## Simple Explanation
Before MCP, every AI tool and framework (LangChain, AutoGen, custom scripts) had to write unique custom connectors to read databases or call APIs. MCP introduces a universal protocol—similar to how LSP (Language Server Protocol) unified programming language support in IDEs—so an AI model can plug into any MCP-compatible data source instantly.

## Why This Is Trending
- **Ecosystem Standardization**: Solves the fragmented N-to-M integration problem across AI agents and data stores.
- **Backed by Major AI Labs**: Spearheaded by Anthropic and rapidly integrated by IDEs (like Claude Desktop, Cursor, Zed) and cloud providers.
- **Security & Sandboxing**: Designed for clean separation of concerns, letting tools execute with scoped local permissions.

## How It Works
1. **Architecture**: Client-Host-Server topology. The AI Client (e.g. IDE) communicates with one or more MCP Servers (e.g. Postgres MCP Server, GitHub MCP Server).
2. **Transport Layer**:
   - `stdio`: Fast, secure IPC for local tool servers running as child processes.
   - `SSE (Server-Sent Events)`: HTTP-based streaming for remote networked services.
3. **Protocol Layer**: JSON-RPC 2.0 messages handle capabilities negotiation, resource listing, tool execution, and subscription updates.

## Real-World Example
An engineer using an AI coding assistant asks: *"Find all open high-priority bugs in our billing repository and show the relevant database schema."*
- The AI client calls the **GitHub MCP Server** via JSON-RPC to query issues.
- It then queries the **Postgres MCP Server** via standard MCP tool calls to inspect the schema—without hardcoded glue code.

## System Design Relevance & Trade-Offs
- **Scalability**: Decouples model orchestration from tool maintenance. Tool developers only write one MCP server.
- **Latency**: JSON-RPC over stdio adds sub-millisecond overhead, but remote SSE requires persistent connection pooling and timeout handling.
- **Security**: MCP servers run in isolation; capability negotiation ensures clients only access explicitly permitted tools.

## Common Interview Questions
1. **How does MCP differ from raw function calling (OpenAI tools)?**
   - *Answer*: Function calling is just an API schema for an LLM to emit tool arguments. MCP is a complete bidirectional protocol defining connection lifecycle, capabilities negotiation, resource subscriptions, and tool discovery between client runtimes and independent servers.
2. **What architectural challenges arise when scaling MCP to distributed microservices?**
   - *Answer*: Managing persistent SSE connections, authentication token pass-through, distributed tracing (W3C traceparent headers), and handling rate limits across multiple third-party servers.

## Sources
- [Model Context Protocol Documentation](https://modelcontextprotocol.io)
- [Anthropic MCP GitHub Repository](https://github.com/modelcontextprotocol)
"""
            return response_model(
                topic="Model Context Protocol (MCP)",
                summary_markdown=summary_md
            )

        elif response_model == FlashcardsGame or "FlashcardsGame" in model_name:
            cards = [
                FlashcardItem(
                    id="card_1",
                    category="Core Architecture",
                    difficulty="Medium",
                    front_prompt="How does MCP differ from standard OpenAI Function Calling in multi-service agent systems?",
                    back_explanation="Function Calling is only an LLM schema for emitting tool arguments. MCP is a complete bidirectional client-server protocol with transport negotiation (stdio/SSE), dynamic resource discovery, and security isolation across independent server processes.",
                    hint="Think about connection lifecycle, discovery, and transport layers vs JSON schemas.",
                    key_takeaway="MCP standardizes the entire connection & tool discovery protocol, not just function schemas."
                ),
                FlashcardItem(
                    id="card_2",
                    category="Trade-offs & Scalability",
                    difficulty="Hard",
                    front_prompt="What are the latency and security trade-offs of using MCP over stdio vs SSE (HTTP)?",
                    back_explanation="stdio offers sub-millisecond IPC latency and simple local process sandboxing, but cannot scale across distributed networks. SSE enables remote microservice connections but introduces HTTP connection pooling, token forwarding, and network jitter overhead.",
                    hint="Compare local IPC pipes vs persistent HTTP streams.",
                    key_takeaway="stdio for local fast tooling; SSE for distributed microservices."
                ),
                FlashcardItem(
                    id="card_3",
                    category="System Design",
                    difficulty="Medium",
                    front_prompt="How does MCP handle capability negotiation and tool schema evolution between client and server?",
                    back_explanation="During the initialization handshake, the client and server exchange supported protocol versions and capabilities (resources, prompts, tools). Tools emit JSON-Schema parameter definitions, allowing dynamic discovery and schema validation without redeploying the client runtime.",
                    hint="Consider initialization handshake messages in JSON-RPC 2.0.",
                    key_takeaway="Initialization handshake negotiates capabilities dynamically."
                )
            ]
            return response_model(
                topic="Model Context Protocol (MCP)",
                game_type="flashcards",
                total_cards=len(cards),
                cards=cards
            )

        elif response_model == CompanyInterviewIntel or "CompanyInterviewIntel" in model_name:
            rounds = [
                InterviewRound(
                    round_name="Technical Recruiter Screen",
                    round_type="Recruiter Screen",
                    duration_minutes=30,
                    focus_areas=["Background & Key Achievements", "Role expectations", "Level calibration"],
                    sample_questions=["Walk me through your most complex architectural project", "Why are you interested in this team?"],
                    evaluation_criteria=["Communication clarity", "Project impact articulation"],
                    tips=["Keep initial answers crisp (under 2 minutes)."]
                ),
                InterviewRound(
                    round_name="Coding & Data Structures (Phone Screen)",
                    round_type="Coding / DSA",
                    duration_minutes=45,
                    focus_areas=["Algorithmic problem solving", "Data structures", "Clean modular code"],
                    sample_questions=["Implement an LRU Cache with TTL expiry", "Word Search II / Trie Matrix Traversal"],
                    evaluation_criteria=["Optimal complexity (O(1) lookups)", "Edge case validation", "Production-grade code"],
                    tips=["Discuss time & space complexity before writing code."]
                ),
                InterviewRound(
                    round_name="Onsite: Distributed System Design",
                    round_type="System Design",
                    duration_minutes=60,
                    focus_areas=["Distributed Architecture", "Data modeling", "High Availability & Partitioning"],
                    sample_questions=["Design a global idempotent payment processing gateway", "Design a distributed metrics aggregation system"],
                    evaluation_criteria=["Driving design trade-offs", "Addressing single points of failure", "Clear API contracts"],
                    tips=["Clarify functional and non-functional requirements in the first 5 minutes."]
                ),
                InterviewRound(
                    round_name="Onsite: Practical Bug Squashing / API Design",
                    round_type="Practical / Bug Squash / API",
                    duration_minutes=60,
                    focus_areas=["Working in a real codebase", "Debugging failing tests", "Refactoring"],
                    sample_questions=["Debug a race condition in a multi-threaded payment orchestrator in VS Code"],
                    evaluation_criteria=["Navigating unfamiliar codebases", "Effective test-driven debugging", "Clean commits"],
                    tips=["Run the test suite immediately to understand the baseline failure."]
                ),
                InterviewRound(
                    round_name="Onsite: Behavioral & Leadership Bar",
                    round_type="Behavioral & Leadership",
                    duration_minutes=45,
                    focus_areas=["Engineering leadership", "Conflict resolution", "Company core values"],
                    sample_questions=["Tell me about a high-stakes technical disagreement and how you resolved it"],
                    evaluation_criteria=["STAR method depth", "Humility & growth mindset", "Cross-functional empathy"],
                    tips=["Use concrete metrics to explain the business or technical outcome."]
                )
            ]

            pack_md = """# Stripe — Staff Backend Engineer (L6)
## Complete Interview Intelligence & Prep Blueprint

### 🎯 Hiring Bar & Overview
Stripe has a uniquely pragmatic engineering bar. Unlike pure algorithm testing, Stripe heavily emphasizes **real-world software craftsmanship**: building clean APIs, navigating existing codebases, understanding distributed financial correctness (idempotency, ACID vs BASE), and strong written communication.

### 🔄 Interview Rounds Breakdown
#### Round 1: Recruiter Screen (30 mins)
- **Type**: `Recruiter Screen`
- **Focus**: Background, Level calibration, Timeline.

#### Round 2: Coding & Data Structures (45 mins)
- **Type**: `Coding / DSA`
- **Sample**: LRU Cache with TTL, JSON parser / tree traversal.
- **Evaluation**: Production-ready code, clean variable naming, modular functions.

#### Round 3: Practical Bug Squash / Integration (60 mins)
- **Type**: `Practical / Bug Squash / API`
- **Sample**: Live debugging in an actual IDE (VS Code) on an open-source payment repo.
- **Pro-Tip**: Read the unit tests first!

#### Round 4: Distributed System Design (60 mins)
- **Type**: `System Design`
- **Sample**: Idempotent payment pipeline, Webhook delivery infrastructure at scale.

#### Round 5: Behavioral & Leadership Bar (45 mins)
- **Type**: `Behavioral & Leadership`
- **Focus**: Stripe operating principles, ownership, cross-functional collaboration.

### 💻 Top Coding & DSA Patterns Asked
- **Hash Maps + Doubly Linked Lists (LRU / LFU)**
- **String Parsing & State Machines**
- **Interval Scheduling & Rate Limiting Algorithms**

### 🏗️ Key System Design Architectures Asked
- **Idempotent API Design with Distributed Locks (Redis/Postgres)**
- **Reliable Webhook Delivery with Exponential Backoff & Dead Letter Queues**
- **Distributed Ledger & Double-Entry Accounting Architecture**

### 🤝 Cultural Values & Behavioral Themes
- **Macro optimism, micro pessimism**: Obsession over reliability and edge cases.
- **High agency & execution speed**: Delivering clean, self-contained solutions.
"""

            return response_model(
                company_name="Stripe",
                role="Staff Backend Engineer",
                level="L6",
                hiring_bar_summary="Stripe evaluates pragmatic engineering execution, real IDE debugging, idempotent system design, and rigorous ownership.",
                rounds_breakdown=rounds,
                top_dsa_patterns=["LRU Cache / Linked Hash Maps", "Parsing & Tree Traversal", "Rate Limiter Algorithms"],
                top_system_design_topics=["Idempotent Payment Gateway", "Reliable Webhook Delivery Engine", "Distributed Ledger Consistency"],
                cultural_values_and_behavioral=["Macro optimism, micro pessimism", "Users first", "Rigorous execution"],
                recent_experiences_summary=["Practical coding round uses your own local IDE.", "System design rounds heavily test database isolation and idempotency.", "Fast feedback loop within 48-72 hours."],
                sources=[
                    ResearchSource(
                        url="https://leetcode.com/discuss/interview-experience",
                        title="Stripe Staff Engineer Onsite Experience 2026",
                        publisher="LeetCode Discuss",
                        extracted_at="2026-09-18 12:00:00",
                        credibility_score=9,
                        key_points=["Emphasized bug squash in local IDE", "Idempotent payment design"]
                    )
                ],
                prep_pack_markdown=pack_md
            )

        elif response_model == InterviewFeedback or "InterviewFeedback" in model_name:
            return response_model(
                overall_score=88,
                hire_recommendation="Hire",
                summary_verdict="Candidate demonstrated strong senior-level technical execution and clear communication.",
                rubric_scores=[
                    RubricScore(criterion="Technical Depth & Problem Solving", score=5, feedback="Flawless grasp of distributed locking and idempotency keys."),
                    RubricScore(criterion="System Rigor & Edge Cases", score=4, feedback="Handled network partition and retry storms well."),
                    RubricScore(criterion="Communication & Structure", score=4, feedback="Articulated assumptions and system constraints clearly."),
                    RubricScore(criterion="Cultural & Leadership Bar", score=5, feedback="High agency and first-principles reasoning.")
                ],
                key_strengths=[
                    "Immediate clarification of idempotency constraints and concurrency expectations",
                    "Clean modular architecture with single-responsibility boundaries",
                    "Proactive identification of distributed lock race conditions"
                ],
                areas_for_improvement=[
                    "Consider memory overhead of in-memory caching under burst traffic",
                    "Add explicit back-of-the-envelope calculations for storage capacity"
                ],
                culture_fit_notes="Aligns exceptionally well with pragmatic craft and ownership values.",
                detailed_debrief_markdown="# Detailed Mock Interview Scorecard\n\nCandidate performed at a solid Staff L6 bar."
            )

        elif "StockProfile" in model_name:
            from research_agent.models.stock import StockProfile
            return StockProfile(
                ticker="NVDA",
                company_name="NVIDIA Corporation",
                exchange="NASDAQ",
                currency="USD",
                sector="Technology",
                industry="Semiconductors & AI Compute",
                market_cap_billions=3060.0,
                current_price=124.50,
                business_description="NVIDIA is the pioneer of GPU-accelerated computing and dominant architecture supplier for AI hyperscalers.",
                monetization_engine="NVIDIA monetizes high-margin accelerated compute hardware (Hopper, Blackwell), enterprise CUDA software, and InfiniBand networking.",
                revenue_segments={"Compute & Networking": 87.0, "Gaming": 9.0, "Professional Visualization": 3.0, "Automotive": 1.0},
                geographic_exposure={"United States": 45.0, "Taiwan": 25.0, "China": 15.0, "Rest of World": 15.0},
                key_executives=["Jensen Huang (CEO & Founder)", "Colette Kress (EVP & CFO)"]
            )

        elif "FinancialAnalysis" in model_name:
            from research_agent.models.stock import FinancialAnalysis, FinancialStatementSummary
            return FinancialAnalysis(
                trajectory="Improving",
                revenue_trend_summary="Robust top-line expansion driven by exponential data center infrastructure investments.",
                margin_trend_summary="Gross margins sustained above 72% reflecting strong pricing power and software-attached mix.",
                balance_sheet_health="Pristine net cash balance sheet with minimal leverage and robust interest coverage.",
                cash_flow_quality="Exceptional free cash flow conversion exceeding 90% of GAAP net income.",
                capital_allocation_assessment="Aggressive R&D reinvestment complemented by opportunistic share repurchases and strategic supplier prepayments.",
                key_metrics_table=[
                    FinancialStatementSummary(
                        period="FY2025",
                        revenue=120000.0,
                        revenue_growth_yoy=125.0,
                        gross_profit=90000.0,
                        gross_margin=75.0,
                        operating_income=75000.0,
                        operating_margin=62.5,
                        net_income=60000.0,
                        eps=2.45,
                        free_cash_flow=55000.0,
                        fcf_conversion=91.6,
                        net_debt=-18000.0,
                        debt_to_equity=0.18,
                        roic=65.0,
                        roe=72.0
                    )
                ]
            )

        elif "ValuationAnalysis" in model_name:
            from research_agent.models.stock import ValuationAnalysis, ValuationScenario
            return ValuationAnalysis(
                pe_trailing=36.0,
                pe_forward=28.5,
                ev_ebitda=24.0,
                ev_sales=14.5,
                price_to_fcf=31.0,
                fcf_yield=3.2,
                peg_ratio=1.2,
                historical_valuation_context="Forward P/E of 28.5x represents an attractive PEG ratio relative to expected 30%+ multi-year EPS CAGR.",
                peer_relative_valuation="Trades at a justified premium to legacy semiconductor peers given 60%+ operating margins and market leadership.",
                dcf_methodology_overview="DCF model utilizes a 9.5% WACC and 3.0% perpetual growth rate across Bear, Base, and Bull scenarios.",
                scenarios=[
                    ValuationScenario(
                        scenario_name="Bear",
                        target_price_implied=85.00,
                        upside_downside_percent=-31.7,
                        revenue_growth_cagr=15.0,
                        terminal_operating_margin=48.0,
                        wacc=10.5,
                        terminal_growth_rate=2.5,
                        implied_pe_multiple=20.0,
                        key_assumptions=["Hyperscaler CapEx pause", "Custom ASIC market share erosion"],
                        catalysts_required=["Baseline defensive data center spend"],
                        risks_to_scenario=["Aggressive price discounting by competitors"]
                    ),
                    ValuationScenario(
                        scenario_name="Base",
                        target_price_implied=145.00,
                        upside_downside_percent=16.5,
                        revenue_growth_cagr=28.0,
                        terminal_operating_margin=58.0,
                        wacc=9.5,
                        terminal_growth_rate=3.0,
                        implied_pe_multiple=30.0,
                        key_assumptions=["Blackwell volume ramp on schedule", "Stable hyperscaler CapEx cadence"],
                        catalysts_required=["Sustained Tier-1 cloud GPU cluster buildout"],
                        risks_to_scenario=["Packaging capacity bottlenecks at TSMC"]
                    ),
                    ValuationScenario(
                        scenario_name="Bull",
                        target_price_implied=195.00,
                        upside_downside_percent=56.6,
                        revenue_growth_cagr=38.0,
                        terminal_operating_margin=65.0,
                        wacc=9.0,
                        terminal_growth_rate=3.5,
                        implied_pe_multiple=38.0,
                        key_assumptions=["Sovereign AI & Enterprise adoption inflection", "CUDA ecosystem lock-in"],
                        catalysts_required=["Enterprise AI agent adoption driving second-wave inference demand"],
                        risks_to_scenario=["Geopolitical trade and export control restrictions"]
                    )
                ]
            )

        elif "PeerComparison" in model_name:
            from research_agent.models.stock import PeerComparison, PeerBenchmark
            return PeerComparison(
                primary_peers=[
                    PeerBenchmark(
                        ticker="AMD",
                        company_name="Advanced Micro Devices",
                        market_cap_billions=250.0,
                        pe_forward=32.0,
                        ev_ebitda=28.0,
                        revenue_growth_yoy=18.0,
                        operating_margin=18.5,
                        roic=14.0,
                        fcf_yield=2.4,
                        competitive_moat_comparison="Strong x86 and emerging GPU competitor with open-source ROCm software stack."
                    ),
                    PeerBenchmark(
                        ticker="INTC",
                        company_name="Intel Corporation",
                        market_cap_billions=90.0,
                        pe_forward=45.0,
                        ev_ebitda=16.0,
                        revenue_growth_yoy=2.0,
                        operating_margin=4.0,
                        roic=2.0,
                        fcf_yield=-1.5,
                        competitive_moat_comparison="Incumbent CPU supplier undergoing costly foundry transition with trailing GPU share."
                    )
                ],
                competitive_position_narrative="NVIDIA maintains an estimated 85%+ market share in AI training clusters backed by the CUDA developer ecosystem.",
                growth_profitability_matrix="Top right quadrant: Leading industry growth paired with peer-leading operating margins.",
                structural_moat_factors=["Deep CUDA software lock-in", "Full-stack networking integration (Quantum InfiniBand / Spectrum-X)", "Scale advantages in advanced packaging"]
            )

        elif "NewsAnalysis" in model_name:
            from research_agent.models.stock import NewsAnalysis, NewsEvent
            return NewsAnalysis(
                recent_events=[
                    NewsEvent(
                        event_title="Blackwell Ultra Architecture Unveiled at Keynote",
                        event_date="2026-03-10",
                        category="Product",
                        summary="Management announced next-generation AI accelerators with 4x inference throughput improvements.",
                        thesis_impact="Positive",
                        is_transitory=False,
                        corroborating_sources=["https://reuters.com/tech/nvidia-keynote", "https://bloomberg.com/news/blackwell-ramp"],
                        duplicate_count=14
                    ),
                    NewsEvent(
                        event_title="Enterprise Software Tier Surpasses $2B Run-Rate",
                        event_date="2026-02-18",
                        category="Earnings",
                        summary="Software and services recurring revenue reached record milestone, diversifying hardware cycles.",
                        thesis_impact="Positive",
                        is_transitory=False,
                        corroborating_sources=["https://finance.yahoo.com/news/nvidia-software-growth"],
                        duplicate_count=8
                    )
                ],
                news_sentiment_summary="Predominantly bullish narrative centered around robust architectural execution and expanding software revenue streams.",
                material_catalysts_identified=["Accelerating production ramp of next-generation compute racks", "Commercial expansion of sovereign AI contracts"],
                recent_thesis_changes=["Reinforced confidence in software-attached margin durability"]
            )

        elif "EarningsAnalysis" in model_name:
            from research_agent.models.stock import EarningsAnalysis, EarningsTrackRecord
            return EarningsAnalysis(
                quarterly_history=[
                    EarningsTrackRecord(
                        quarter="Q4 FY2025",
                        revenue_actual=39500.0,
                        revenue_estimate=38000.0,
                        revenue_surprise_percent=3.9,
                        eps_actual=0.88,
                        eps_estimate=0.82,
                        eps_surprise_percent=7.3,
                        guidance_trend="Raised",
                        management_commentary_summary="Demand for accelerated compute continues to outpace supply across hyperscalers."
                    ),
                    EarningsTrackRecord(
                        quarter="Q3 FY2025",
                        revenue_actual=35000.0,
                        revenue_estimate=33500.0,
                        revenue_surprise_percent=4.5,
                        eps_actual=0.78,
                        eps_estimate=0.72,
                        eps_surprise_percent=8.3,
                        guidance_trend="Raised",
                        management_commentary_summary="Strong operating leverage demonstrated across data center networking."
                    )
                ],
                beat_miss_consistency="Consistent beat-and-raise cadence across 8 consecutive quarters.",
                guidance_revision_trajectory="Wall Street consensus models have been revised upward by 18% over the trailing 180 days.",
                management_tone_shift="Shifted from managing severe supply constraints toward scaling diversified enterprise inference deployments."
            )

        elif "CriticDebrief" in model_name:
            from research_agent.models.stock import CriticDebrief
            return CriticDebrief(
                overlooked_risks=[
                    "Hyperscaler customer concentration: Top 4 customers account for ~40% of total revenue.",
                    "Internal custom silicon development (Google TPU, Amazon Trainium, Meta MTIA) could reduce external merchant silicon share over 3-5 years.",
                    "Geopolitical and export restrictions on advanced AI silicon."
                ],
                contradictory_data_points=[
                    "Hyperscalers are actively diversifying supplier bases to reduce single-vendor pricing exposure.",
                    "Power and data center electrical grid constraints could delay cluster rollouts."
                ],
                bull_case_flaws=[
                    "Assumes perpetual 60%+ operating margins without accounting for competitive pricing pressure in inference.",
                    "Underestimates capital expenditure digestion cycles among cloud service providers."
                ],
                thesis_invalidation_triggers=[
                    "Sequential Data Center revenue growth decelerates below 5% QoQ for two consecutive quarters.",
                    "Gross margins compress below 68% due to packaging cost inflation or price cuts.",
                    "Custom in-house ASIC workloads exceed 35% of hyperscaler AI compute budgets."
                ],
                confidence_penalty_points=5
            )

        elif "StockResearchReport" in model_name:
            from research_agent.models.stock import (
                StockResearchReport, StockProfile, FinancialStatementSummary,
                ValuationScenario, PeerBenchmark, NewsEvent, EarningsTrackRecord,
                CriticDebrief, SourceClaim
            )
            report_md = """# Institutional Equity Research: NVIDIA Corporation (NASDAQ: NVDA)

## 1. Executive Summary
NVIDIA Corporation represents the preeminent full-stack accelerated computing platform globally.

## 2. Valuation & DCF Scenarios
- **Bear Case**: $85.00 (-32%)
- **Base Case**: $145.00 (+16%)
- **Bull Case**: $195.00 (+56%)

## 3. Thesis Invalidation Triggers
- Cloud CapEx digestion cycle leading to sequential revenue contraction.
- Custom ASIC penetration exceeding 30% of hyperscaler workloads.
"""
            from datetime import datetime
            from research_agent.models.stock import DataVerificationAudit
            now_str = datetime.now().strftime("%Y-%m-%d")
            
            exec_summary_mock = (
                "**30-Second Verdict**: NVIDIA Corporation (NVDA) is the preeminent accelerated computing platform globally, making it a high-conviction compounder for long-term investors.\n\n"
                "**Beginner Quick Scorecard**:\n"
                "- 🟢 **Overall Stance**: Bullish Compounder\n"
                "- 🛡️ **Risk Level**: Moderate (High Growth)\n"
                "- ⏳ **Ideal Horizon**: Long-Term (3-5 Years)\n\n"
                "**Top 2 Reasons to Buy (Bull Case)**:\n"
                "- High profitability with sustained software moat (CUDA) and high pricing power.\n"
                "- Clean balance sheet with net cash and strong free cash flow generation.\n\n"
                "**Top 2 Risks to Watch (Bear Case)**:\n"
                "- Valuation multiple contraction if cloud CapEx slows.\n"
                "- Customer concentration among hyperscaler buyers."
            )
            biz_model_mock = (
                "- **What They Sell**: High-performance GPU hardware (Hopper, Blackwell), enterprise CUDA AI software, and InfiniBand networking.\n"
                "- **How They Get Paid**: Compute & Networking sales (~87%), Gaming GPUs (~9%), Professional Visualization & Automotive (~4%).\n"
                "- **Who Pays Them**: Major cloud service providers (Microsoft, Google, Amazon, Meta) and enterprise developers worldwide.\n"
                "- **The Sticky Factor (Moat)**: Over 5 million developers are locked into NVIDIA's proprietary CUDA programming ecosystem, creating enormous switching costs."
            )
            fin_health_mock = (
                "- **Are they making money? (Profitability)**: Exceptionally high profitability. For every $100 in sales, NVIDIA keeps ~$75 after direct chip costs and ~$62 in pure operating profit.\n"
                "- **Can they pay their bills? (Debt & Safety)**: Extremely safe. NVIDIA holds $18 billion more cash than debt (negative net debt), so bankruptcy risk is virtually non-existent.\n"
                "- **Real Cash Flow (Money in the Bank)**: Converts over 91% of net income into actual spendable Free Cash Flow ($55B+).\n"
                "- **Beginner Financial Health Rating**: 🟢 Strong & High Safety"
            )

            chart_mock = [
                {"date": "2025-10-01", "close": 105.0, "volume": 45000000},
                {"date": "2026-01-01", "close": 115.0, "volume": 48000000},
                {"date": "2026-06-01", "close": 120.0, "volume": 52000000},
                {"date": now_str, "close": 124.50, "volume": 55000000}
            ]

            return StockResearchReport(
                ticker="NVDA",
                company_name="NVIDIA Corporation",
                sector="Technology",
                industry="Semiconductors",
                current_price=124.50,
                market_cap_billions=3060.0,
                verified_as_of_date=now_str,
                data_verification=DataVerificationAudit(
                    is_verified_latest=True,
                    verified_as_of_date=now_str,
                    verification_status="VERIFIED_LATEST",
                    latest_quote_date=now_str,
                    staleness_check="PASSED: Market Current (0-day lag)",
                    audit_notes=f"Confirmed NVDA price $124.50 and FY2025 financials current as of {now_str}."
                ),
                historical_price_chart=chart_mock,
                executive_summary=exec_summary_mock,
                business_model_and_revenue_engines=biz_model_mock,
                financial_health_and_margin_trends=fin_health_mock,
                historical_financials=[],
                valuation_analysis="Attractive on a PEG basis relative to multi-year earnings expansion.",
                valuation_scenarios=[],
                peer_benchmarks=[],
                peer_comparison_narrative="Dominant market share with wide software moat relative to AMD and Intel.",
                news_events=[],
                earnings_track_record=[],
                management_capital_allocation_scorecard="Superb capital allocation balancing R&D leadership and share repurchases.",
                competitive_moat_analysis="CUDA ecosystem network effects, advanced packaging scale, and full-stack networking integration.",
                catalysts=["Next-gen GPU volume ramp", "Enterprise inference adoption inflection"],
                risks=["Customer concentration", "Custom ASIC competition", "Geopolitical export controls"],
                pros=["Structural monopoly in AI compute", "Software switching costs", "Pristine balance sheet"],
                cons=["High valuation multiple", "Cyclical CapEx risk", "Customer concentration"],
                what_could_invalidate_the_thesis="Hyperscaler CapEx contraction and rapid custom ASIC adoption.",
                why_now="Volume ramp of next-generation architecture driving multi-year revenue acceleration.",
                critic_debrief=CriticDebrief(
                    overlooked_risks=["Hyperscaler customer concentration"],
                    contradictory_data_points=["Custom ASIC buildouts"],
                    bull_case_flaws=["Assumes non-cyclical hyperscaler CapEx"],
                    thesis_invalidation_triggers=["Sequential revenue deceleration below 5% QoQ"],
                    confidence_penalty_points=5
                ),
                source_claims=[
                    SourceClaim(
                        claim_text=f"Gross margin sustained at 75% in FY2025 confirmed as of {now_str}.",
                        claim_type="FACT",
                        source_title="SEC Form 10-K FY2025",
                        source_url="https://www.sec.gov/edgar",
                        confidence_score=1.0
                    )
                ],
                report_markdown=report_md
            )

        elif "StockOpportunityReport" in model_name:
            from research_agent.models.stock import StockOpportunityReport, StockCandidateOpportunity
            report_md = """# Stock Market Opportunity & Dislocation Report

## 1. Macro Context & Sector Regimes
- **Technology & Infrastructure**: Secular tailwinds in AI compute infrastructure.

## 2. High-Conviction Candidates
- **NVDA**: Quality Growth + Temporary Selloff (32% Upside)
- **ASML**: Quality Monopoly + Cyclical Drawdown (28% Upside)
"""
            return StockOpportunityReport(
                macro_context_summary="Moderating inflation and resilient enterprise IT budgets favor high-ROIC compounders.",
                sector_tailwinds_and_headwinds={"Technology": "AI and cloud infrastructure tailwinds", "Consumer": "Selective consumer discretionary spending"},
                screener_criteria_applied={"Min ROIC": "15%", "Min Revenue Growth": "10%", "Max Forward PE": "40x"},
                candidates=[
                    StockCandidateOpportunity(
                        ticker="NVDA",
                        company_name="NVIDIA Corporation",
                        sector="Technology",
                        current_price=124.50,
                        market_cap_billions=3060.0,
                        opportunity_archetype="Quality Growth + Temporary Selloff",
                        why_now="Temporary 8% price pullback provides attractive entry ahead of architecture volume ramp.",
                        fundamental_highlights=["65% ROIC", "75% Gross Margin", "Net Cash Balance Sheet"],
                        catalysts=["Architecture volume ramp", "Enterprise inference inflection"],
                        critical_risks=["Hyperscaler CapEx pause", "Custom ASIC competition"],
                        implied_upside_percent=32.0,
                        confidence_tier="High Conviction",
                        source_links=["https://finance.yahoo.com/quote/NVDA"]
                    )
                ],
                critic_risk_summary="Key risk across technology candidates is concentrated cloud CapEx digestion.",
                report_markdown=report_md
            )

        # Generic fallback instance if any other BaseModel is requested
        return response_model()


