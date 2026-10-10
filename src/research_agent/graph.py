from langgraph.graph import StateGraph, START, END
from research_agent.state import ResearchAgentState
from research_agent.config import settings
from research_agent.llm import get_llm_provider
from research_agent.storage import (
    RunStore,
    write_trending_topics_md,
    write_refined_topics_md,
    write_research_notes_md,
    write_summary_md,
    write_final_interview_pack_md,
    write_stock_research_md,
    write_stock_picks_md
)
from research_agent.storage.run_tracker import RUNS_DB
from research_agent.agents import (
    TopicAgent,
    FineTunerAgent,
    ResearcherAgent,
    SummariserAgent,
    InterviewIntelAgent,
    StockEntityAgent,
    StockFinancialAgent,
    StockValuationAgent,
    StockPeerAgent,
    StockNewsAgent,
    StockEarningsAgent,
    StockCriticAgent,
    StockSynthesisAgent,
    StockMacroAgent,
    StockDislocationAgent
)
from research_agent.models import TopicSummary, CompanyInterviewIntel, StockResearchReport, StockOpportunityReport
from typing import Dict, Any

def update_tracker(run_id: str, status: str, progress: int, current_step: str, **kwargs):
    if run_id not in RUNS_DB:
        RUNS_DB[run_id] = {
            "status": "discovering",
            "progress": 0,
            "current_step": "",
            "interests": "",
            "raw_topics": [],
            "refined_topics": [],
            "selected_topics": [],
            "final_pack": "",
            "error": None
        }
    RUNS_DB[run_id]["status"] = status
    RUNS_DB[run_id]["progress"] = progress
    RUNS_DB[run_id]["current_step"] = current_step
    for k, v in kwargs.items():
        RUNS_DB[run_id][k] = v

def research_company_interview_node(state: ResearchAgentState) -> Dict[str, Any]:
    run_id = state["run_id"]
    company = state.get("company_name", "Target Company")
    role = state.get("target_role", "Senior Software Engineer")
    level = state.get("target_level", "Senior / L5")
    
    update_tracker(run_id, "researching", 20, f"Crawling real interview debriefs and experiences for {company} ({role})...")
    print(f"Agent [Interview Intel]: Crawling debriefs for {company} - {role} ({level})...")
    
    llm = get_llm_provider()
    agent = InterviewIntelAgent(llm)
    
    update_tracker(run_id, "researching", 50, f"Analyzing round patterns and questions for {company}...")
    intel = agent.research_company(company_name=company, role=role, level=level)
    
    store = RunStore()
    store.set_run(run_id)
    store.save_interview_intel(intel)
    
    update_tracker(
        run_id,
        "completed",
        100,
        f"Successfully generated Interview Intelligence Pack for {company}.",
        final_pack=intel.prep_pack_markdown,
        interview_intel=intel.model_dump(),
        selected_topics=[f"{company} ({role})"]
    )
    
    print(f"\nSuccess! Company interview intelligence pack saved in: {store.run_path / 'company_interview_pack.md'}")
    return {"interview_intel": intel}

def discover_topics_node(state: ResearchAgentState) -> Dict[str, Any]:
    run_id = state["run_id"]
    
    # If already populated (multi-pass/resume), skip
    if state.get("raw_topics"):
        print("Agent [Topic Discoverer]: Topics already discovered. Skipping node.")
        return {}
        
    update_tracker(run_id, "discovering", 10, "Discovering tech trends from web search...", interests=state["user_interests"])
    print("Agent [Topic Discoverer]: Discovering tech trends from web search...")
    
    llm = get_llm_provider()
    agent = TopicAgent(llm)
    candidates = agent.discover_topics(state["user_interests"], max_candidates=settings.max_topics_discovered)
    
    store = RunStore()
    store.set_run(run_id)
    store.save_trending_topics(candidates)
    write_trending_topics_md(candidates, store)
    
    candidates_dump = [t.model_dump() for t in candidates]
    update_tracker(run_id, "discovering", 25, "Finished topic discovery.", raw_topics=candidates_dump)
    return {"raw_topics": candidates}

def refine_topics_node(state: ResearchAgentState) -> Dict[str, Any]:
    run_id = state["run_id"]
    
    # If already populated (multi-pass/resume), skip
    if state.get("refined_topics"):
        print("Agent [Fine Tuner]: Topics already refined. Skipping node.")
        return {}
        
    update_tracker(run_id, "refining", 30, "Refining discovered topics based on user interests...")
    print("Agent [Fine Tuner]: Refining discovered topics based on user interests...")
    
    llm = get_llm_provider()
    agent = FineTunerAgent(llm)
    refined = agent.refine_topics(
        user_interests=state["user_interests"],
        candidates=state["raw_topics"],
        max_selected=settings.max_topics_selected
    )
    
    store = RunStore()
    store.set_run(run_id)
    store.save_refined_topics(refined)
    write_refined_topics_md(refined, store)
    
    refined_dump = [t.model_dump() for t in refined]
    update_tracker(run_id, "refining", 45, "Finished topic refining.", refined_topics=refined_dump)
    return {"refined_topics": refined}

def select_topics_node(state: ResearchAgentState) -> Dict[str, Any]:
    run_id = state["run_id"]
    
    # If already selected (multi-pass/resume), proceed
    if state.get("selected_topics"):
        print(f"Agent [Selector]: Topic selection already submitted: {state['selected_topics']}")
        return {}
        
    refined = state.get("refined_topics", [])
    if not refined:
        print("Agent [Selector]: No topics found to select.")
        update_tracker(run_id, "researching", 50, "No topics to select.", selected_topics=[])
        return {"selected_topics": []}

    selected_titles = []
    
    # Prompt in terminal if manual selection override is requested
    if state.get("manual_selection"):
        update_tracker(run_id, "pending_selection", 50, "Awaiting manual selection...")
        print("\n=== Discovered & Refined Topics ===")
        for idx, t in enumerate(refined, 1):
            print(f"[{idx}] {t.title}")
            print(f"    Reason: {t.reason_selected}")
            print(f"    Expected Learning Outcome: {t.expected_learning_outcome}")
            print("-" * 40)
        
        try:
            choice_str = input("\nEnter topic indices to select (comma-separated, e.g. 1,3) or press Enter to auto-select all: ")
            if choice_str.strip():
                indices = [int(x.strip()) - 1 for x in choice_str.split(",") if x.strip().isdigit()]
                selected_titles = [refined[i].title for i in indices if 0 <= i < len(refined)]
        except Exception:
            pass

    if not selected_titles:
        selected_titles = [t.title for t in refined]
        print(f"Agent [Selector]: Auto-selected all refined topics: {selected_titles}")
    else:
        print(f"Agent [Selector]: Selected topics: {selected_titles}")
        
    update_tracker(run_id, "researching", 50, "Topics selected.", selected_topics=selected_titles)
    return {"selected_topics": selected_titles}

def route_after_refine(state: ResearchAgentState) -> str:
    # If manual selection is enabled and we have not selected topics yet, exit graph early
    if state.get("manual_selection") and not state.get("selected_topics"):
        run_id = state["run_id"]
        update_tracker(run_id, "pending_selection", 50, "Awaiting manual selection by user.")
        print("Agent [Orchestrator]: Pausing run for manual topic selection.")
        return "end"
    return "select_topics"

def research_topics_node(state: ResearchAgentState) -> Dict[str, Any]:
    run_id = state["run_id"]
    update_tracker(run_id, "researching", 55, "Fetching deep-dive sources and taking technical notes...")
    print("Agent [Researcher]: Fetching deep-dive sources and taking technical notes...")
    
    llm = get_llm_provider()
    agent = ResearcherAgent(llm)
    
    store = RunStore()
    store.set_run(run_id)
    
    notes_dict = {}
    selected_titles = state.get("selected_topics", [])
    refined_topics = state.get("refined_topics", [])
    
    topics_to_research = [t for t in refined_topics if t.title in selected_titles]
    
    for idx, t in enumerate(topics_to_research, 1):
        print(f" -> Researching topic: {t.title}")
        try:
            notes = agent.research_topic(t, max_sources=settings.max_sources_per_topic)
            notes_dict[t.title] = notes
            
            # Save notes
            store.save_research_notes(f"topic_{idx}", notes)
            write_research_notes_md(notes, idx, store)
        except Exception as e:
            print(f"Error researching '{t.title}': {e}")
            
    update_tracker(run_id, "summarizing", 75, "Finished topic research.")
    return {"research_notes": notes_dict}

def summarize_topics_node(state: ResearchAgentState) -> Dict[str, Any]:
    run_id = state["run_id"]
    update_tracker(run_id, "summarizing", 80, "Creating interview guides, analogies and tradeoffs...")
    print("Agent [Summariser]: Creating interview guides, analogies and tradeoffs...")
    
    llm = get_llm_provider()
    agent = SummariserAgent(llm)
    
    store = RunStore()
    store.set_run(run_id)
    
    summaries = {}
    research_notes = state.get("research_notes", {})
    
    for idx, (title, notes) in enumerate(research_notes.items(), 1):
        print(f" -> Generating summary for: {title}")
        try:
            summary = agent.summarize_research(notes)
            summaries[title] = summary.summary_markdown
            
            # Save summaries
            store.save_summary(f"topic_{idx}", summary)
            write_summary_md(summary, idx, store)
        except Exception as e:
            print(f"Error generating summary for '{title}': {e}")
            
    update_tracker(run_id, "summarizing", 95, "Finished generating summaries.")
    return {"summaries": summaries}

def write_final_pack_node(state: ResearchAgentState) -> Dict[str, Any]:
    run_id = state["run_id"]
    print("Agent [Orchestrator]: Compiling all summaries into final_interview_pack.md...")
    
    store = RunStore()
    store.set_run(run_id)
    
    summaries_dict = state.get("summaries", {})
    summaries_list = []
    
    for title, markdown in summaries_dict.items():
        summaries_list.append(TopicSummary(topic=title, summary_markdown=markdown))
        
    if summaries_list:
        write_final_interview_pack_md(summaries_list, store)
        print(f"\nSuccess! Run completed. Pack saved in: {store.run_path / 'final_interview_pack.md'}")
        
        # Read final pack contents to save in tracker
        try:
            with open(store.run_path / 'final_interview_pack.md', 'r', encoding='utf-8') as f:
                pack_content = f.read()
        except Exception:
            pack_content = ""
            
        update_tracker(run_id, "completed", 100, "Research process finished successfully.", final_pack=pack_content)
    else:
        print("Warning: No summaries were generated. Pack generation skipped.")
        update_tracker(run_id, "completed", 100, "Finished but no summaries generated.")
        
    return {}

def research_stock_market_node(state: ResearchAgentState) -> Dict[str, Any]:
    run_id = state["run_id"]
    stock_mode = state.get("stock_sub_mode") or state.get("stock_mode") or "stock_research"
    ticker_query = state.get("stock_ticker") or state.get("ticker") or state.get("user_interests") or "NVDA"
    manual_peers = state.get("manual_peers")
    sector_filter = state.get("sector_filter")

    llm = get_llm_provider()
    store = RunStore()
    store.set_run(run_id)

    if stock_mode == "stock_picks":
        update_tracker(run_id, "researching", 20, "Analyzing global macro environment and sector regimes...", stock_mode="stock_picks")
        print("Agent [Stock Macro]: Analyzing global macro backdrop and sector trends...")
        macro_agent = StockMacroAgent(llm)
        macro_data = macro_agent.analyze_macro_and_sectors(sector_filter=sector_filter)

        update_tracker(run_id, "researching", 60, "Running quantitative screening and detecting market dislocations...")
        print("Agent [Stock Dislocation]: Running quantitative filters and identifying dislocation archetypes...")
        disloc_agent = StockDislocationAgent(llm)
        picks_report = disloc_agent.screen_and_synthesize_opportunities(
            macro_context=macro_data,
            sector_filter=sector_filter
        )

        store.save_stock_picks(picks_report)
        write_stock_picks_md(picks_report, store)

        try:
            with open(store.run_path / "stock_opportunity_report.md", "r", encoding="utf-8") as f:
                report_md = f.read()
        except Exception:
            report_md = picks_report.report_markdown

        picks_report.report_markdown = report_md
        store.save_stock_picks(picks_report)

        update_tracker(
            run_id,
            "completed",
            100,
            "Successfully compiled Stock Market Opportunity & Dislocation Report.",
            final_pack=report_md,
            stock_opportunity_report=picks_report.model_dump(),
            selected_topics=[c.ticker for c in picks_report.candidates]
        )
        print(f"\nSuccess! Stock Opportunity Report saved in: {store.run_path / 'stock_opportunity_report.md'}")
        return {"stock_opportunity_report": picks_report}

    else:
        # Default: stock_research (Specific stock deep dive)
        update_tracker(run_id, "researching", 10, f"Resolving entity and monetization model for: {ticker_query}...", stock_mode="stock_research")
        print(f"Agent [Stock Entity]: Resolving ticker and business model for {ticker_query}...")
        entity_agent = StockEntityAgent(llm)
        profile = entity_agent.resolve_entity(ticker_query)

        ticker = profile.ticker
        company_name = profile.company_name

        update_tracker(run_id, "researching", 25, f"Analyzing financial statements and margin trajectories for {ticker}...")
        print(f"Agent [Stock Financial]: Analyzing 5Y financial statements for {ticker}...")
        financial_agent = StockFinancialAgent(llm)
        financials = financial_agent.analyze_financials(ticker, company_name)

        update_tracker(run_id, "researching", 45, f"Evaluating relative multiples and calculating DCF intrinsic scenarios for {ticker}...")
        print(f"Agent [Stock Valuation]: Modeling relative multiples and 3-tier DCF scenarios for {ticker}...")
        valuation_agent = StockValuationAgent(llm)
        valuation = valuation_agent.analyze_valuation(
            ticker=ticker,
            company_name=company_name,
            current_price=profile.current_price
        )

        update_tracker(run_id, "researching", 60, f"Benchmarking competitive moat against peers for {ticker}...")
        print(f"Agent [Stock Peer]: Benchmarking growth and moat against industry peers...")
        peer_agent = StockPeerAgent(llm)
        peers = peer_agent.analyze_peers(
            ticker=ticker,
            company_name=company_name,
            sector=profile.sector,
            industry=profile.industry,
            manual_peers=manual_peers
        )

        update_tracker(run_id, "researching", 75, f"Clustering news events and analyzing historical earnings surprises for {ticker}...")
        print(f"Agent [Stock News]: Clustering events and filtering transitory noise for {ticker}...")
        news_agent = StockNewsAgent(llm)
        news = news_agent.analyze_and_deduplicate_news(ticker, company_name)

        print(f"Agent [Stock Earnings]: Reviewing earnings surprise track record and guidance tone for {ticker}...")
        earnings_agent = StockEarningsAgent(llm)
        earnings = earnings_agent.analyze_earnings(ticker, company_name)

        update_tracker(run_id, "researching", 85, f"Stress-testing thesis and identifying thesis invalidation triggers with Critic Agent...")
        print(f"Agent [Stock Critic]: Challenging bullish assumptions and formulating invalidation triggers...")
        critic_agent = StockCriticAgent(llm)
        critic = critic_agent.stress_test_thesis(
            ticker=ticker,
            company_name=company_name,
            sector=profile.sector,
            industry=profile.industry,
            current_price=profile.current_price,
            preliminary_synthesis={
                "profile": profile.model_dump(),
                "financials": financials.model_dump(),
                "valuation": valuation.model_dump()
            }
        )

        update_tracker(run_id, "researching", 95, f"Synthesizing 21-section institutional equity research report for {ticker}...")
        print(f"Agent [Stock Synthesis]: Compiling institutional equity research report with sourced evidence...")
        synthesis_agent = StockSynthesisAgent(llm)
        report = synthesis_agent.synthesize_report(
            profile=profile,
            financials=financials,
            valuation=valuation,
            peers=peers,
            news=news,
            earnings=earnings,
            critic=critic
        )

        store.save_stock_research(report)
        write_stock_research_md(report, store)

        try:
            with open(store.run_path / "stock_research_report.md", "r", encoding="utf-8") as f:
                report_md = f.read()
        except Exception:
            report_md = report.report_markdown

        report.report_markdown = report_md
        store.save_stock_research(report)

        update_tracker(
            run_id,
            "completed",
            100,
            f"Successfully compiled Institutional Equity Research Report for {ticker}.",
            final_pack=report_md,
            stock_research_report=report.model_dump(),
            selected_topics=[f"{ticker} ({company_name})"]
        )
        print(f"\nSuccess! Stock Research Report saved in: {store.run_path / 'stock_research_report.md'}")
        return {
            "stock_profile": profile,
            "stock_financials": financials,
            "stock_valuation": valuation,
            "stock_peers": peers,
            "stock_news": news,
            "stock_earnings": earnings,
            "stock_critic": critic,
            "stock_research_report": report
        }

def route_initial_mode(state: ResearchAgentState) -> str:
    mode = state.get("research_mode")
    if mode == "interview_experience":
        return "research_company_interview"
    elif mode == "stock_market":
        return "research_stock_market"
    return "discover_topics"

def create_research_graph():
    workflow = StateGraph(ResearchAgentState)
    
    # Add nodes
    workflow.add_node("research_company_interview", research_company_interview_node)
    workflow.add_node("research_stock_market", research_stock_market_node)
    workflow.add_node("discover_topics", discover_topics_node)
    workflow.add_node("refine_topics", refine_topics_node)
    workflow.add_node("select_topics", select_topics_node)
    workflow.add_node("research_topics", research_topics_node)
    workflow.add_node("summarize_topics", summarize_topics_node)
    workflow.add_node("write_final_pack", write_final_pack_node)
    
    # Add conditional start router
    workflow.add_conditional_edges(
        START,
        route_initial_mode,
        {
            "research_company_interview": "research_company_interview",
            "research_stock_market": "research_stock_market",
            "discover_topics": "discover_topics"
        }
    )
    workflow.add_edge("research_company_interview", END)
    workflow.add_edge("research_stock_market", END)
    
    # Transitions for tech topics flow
    workflow.add_edge("discover_topics", "refine_topics")
    
    # Add conditional router after refine_topics
    workflow.add_conditional_edges(
        "refine_topics",
        route_after_refine,
        {
            "end": END,
            "select_topics": "select_topics"
        }
    )
    
    workflow.add_edge("select_topics", "research_topics")
    workflow.add_edge("research_topics", "summarize_topics")
    workflow.add_edge("summarize_topics", "write_final_pack")
    workflow.add_edge("write_final_pack", END)
    
    return workflow.compile()

