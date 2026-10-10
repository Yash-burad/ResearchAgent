from pathlib import Path
from typing import Dict, Any, List, Optional
from research_agent.models.stock import StockOpportunityReport, StockCandidateOpportunity
from research_agent.llm import LLMProvider
from research_agent.data import ScreenerEngine

def load_prompt(filename: str) -> str:
    prompts_dir = Path(__file__).parent.parent / "prompts"
    with open(prompts_dir / filename, "r", encoding="utf-8") as f:
        return f.read()

class StockDislocationAgent:
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
        self.prompt_template = load_prompt("stock_opportunity_analysis.md")

    def screen_and_synthesize_opportunities(
        self,
        macro_context: Dict[str, Any],
        sector_filter: Optional[str] = None
    ) -> StockOpportunityReport:
        screened = ScreenerEngine.screen_opportunities(sector_filter=sector_filter, candidates_limit=4)

        prompt = self.prompt_template.format(
            macro_context=str(macro_context),
            screened_candidates=str([c.model_dump() for c in screened])
        )

        try:
            report = self.llm_provider.generate_structured(
                prompt=prompt,
                response_model=StockOpportunityReport,
                system_instruction="You are an opportunistic equity portfolio manager and dislocation analyst."
            )
            if not report.candidates:
                report.candidates = screened
            return report
        except Exception as e:
            print(f"Warning: StockDislocationAgent failed: {e}. Generating default opportunity report.")
            return StockOpportunityReport(
                macro_context_summary=macro_context.get("macro_summary", "Balanced macro environment."),
                sector_tailwinds_and_headwinds=macro_context.get("sector_trends", {}),
                screener_criteria_applied={"ROIC Filter": ">= 15%", "Revenue Growth": ">= 10%", "Valuation": "Forward P/E <= 40x"},
                candidates=screened,
                critic_risk_summary="Key overarching risk across shortlisted candidates is broader macro multiple compression.",
                report_markdown=""
            )
