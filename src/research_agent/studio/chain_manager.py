from pathlib import Path
import json
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from research_agent.config import settings

CONFIG_FILE = Path(__file__).resolve().parent.parent.parent / "pipeline_config.json"

class PipelineConfig(BaseModel):
    # LLM Settings
    llm_provider: str = Field(default="ollama", description="ollama, gemini, openai, or mock")
    default_model: str = Field(default="qwen2.5:7b")
    ollama_base_url: str = Field(default="http://localhost:11434")

    # Orchestration Toggles & Parameters
    enable_critic_agent: bool = Field(default=True, description="Enable adversarial disconfirmation critic in stock research")
    enable_peer_benchmarking: bool = Field(default=True, description="Benchmark against industry peers")
    enable_news_clustering: bool = Field(default=True, description="Crawl and deduplicate financial news")
    
    # Quantitative & Search Limits
    max_topics_discovered: int = Field(default=20, ge=1, le=50)
    max_topics_selected: int = Field(default=5, ge=1, le=15)
    max_sources_per_topic: int = Field(default=5, ge=1, le=10)
    stock_screener_limit: int = Field(default=4, ge=1, le=10)
    dcf_default_wacc: float = Field(default=9.0, ge=4.0, le=20.0)
    dcf_default_terminal_growth: float = Field(default=3.0, ge=1.0, le=6.0)

class ChainManager:
    @classmethod
    def get_config(cls) -> PipelineConfig:
        if CONFIG_FILE.exists():
            try:
                data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
                return PipelineConfig(**data)
            except Exception:
                pass
        
        # Fallback to defaults from settings
        return PipelineConfig(
            llm_provider=settings.llm_provider,
            default_model=settings.default_model,
            ollama_base_url=settings.ollama_base_url,
            max_topics_discovered=settings.max_topics_discovered,
            max_topics_selected=settings.max_topics_selected,
            max_sources_per_topic=settings.max_sources_per_topic
        )

    @classmethod
    def update_config(cls, new_config: PipelineConfig) -> PipelineConfig:
        CONFIG_FILE.write_text(new_config.model_dump_json(indent=2), encoding="utf-8")
        
        # Update in-memory settings
        settings.llm_provider = new_config.llm_provider
        settings.default_model = new_config.default_model
        settings.ollama_base_url = new_config.ollama_base_url
        settings.max_topics_discovered = new_config.max_topics_discovered
        settings.max_topics_selected = new_config.max_topics_selected
        settings.max_sources_per_topic = new_config.max_sources_per_topic

        return new_config

    @classmethod
    def get_graph_schema(cls) -> Dict[str, Any]:
        """Returns visual representation of all available agent nodes and routing chains."""
        return {
            "domains": [
                {
                    "id": "tech_topics",
                    "title": "Tech Topics Research Pipeline",
                    "description": "Trend discovery, multi-factor scoring, web scraping, and synthesis.",
                    "nodes": [
                        {"id": "discover_topics", "agent": "TopicAgent", "prompt": "topic_agent.md", "status": "active"},
                        {"id": "refine_topics", "agent": "FineTunerAgent", "prompt": "fine_tuner_agent.md", "status": "active"},
                        {"id": "research_topics", "agent": "ResearcherAgent", "prompt": "researcher_agent.md", "status": "active"},
                        {"id": "summarize_topics", "agent": "SummariserAgent", "prompt": "summariser_agent.md", "status": "active"},
                        {"id": "gamification", "agent": "GamificationAgent", "prompt": "games/flashcards.md", "status": "active"}
                    ]
                },
                {
                    "id": "interview_experience",
                    "title": "Interview Intelligence & Simulator",
                    "description": "Company debrief deconstruction, hiring bar rubrics, and interactive mock sessions.",
                    "nodes": [
                        {"id": "interview_intel", "agent": "InterviewIntelAgent", "prompt": "interview_intel.md", "status": "active"},
                        {"id": "mock_interview", "agent": "MockInterviewerAgent", "prompt": "mock_interview.md", "status": "active"},
                        {"id": "interview_evaluation", "agent": "MockInterviewerAgent", "prompt": "interview_evaluation.md", "status": "active"}
                    ]
                },
                {
                    "id": "stock_market",
                    "title": "Stock Market Intelligence Pipeline",
                    "description": "8-Agent institutional research deep-dive and quantitative dislocation screener.",
                    "nodes": [
                        {"id": "stock_entity", "agent": "StockEntityAgent", "prompt": "stock_entity_resolution.md", "status": "active"},
                        {"id": "stock_financials", "agent": "StockFinancialAgent", "prompt": "stock_financial_analysis.md", "status": "active"},
                        {"id": "stock_valuation", "agent": "StockValuationAgent", "prompt": "stock_valuation_analysis.md", "status": "active"},
                        {"id": "stock_peers", "agent": "StockPeerAgent", "prompt": "stock_peer_analysis.md", "status": "active"},
                        {"id": "stock_news", "agent": "StockNewsAgent", "prompt": "stock_news_deduplication.md", "status": "active"},
                        {"id": "stock_earnings", "agent": "StockEarningsAgent", "prompt": "stock_earnings_analysis.md", "status": "active"},
                        {"id": "stock_critic", "agent": "StockCriticAgent", "prompt": "stock_critic_disconfirmation.md", "status": "active"},
                        {"id": "stock_synthesis", "agent": "StockSynthesisAgent", "prompt": "stock_research_synthesis.md", "status": "active"},
                        {"id": "stock_macro", "agent": "StockMacroAgent", "prompt": "stock_macro_sector.md", "status": "active"},
                        {"id": "stock_dislocation", "agent": "StockDislocationAgent", "prompt": "stock_opportunity_analysis.md", "status": "active"}
                    ]
                }
            ]
        }
