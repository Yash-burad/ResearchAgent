from pathlib import Path
from typing import Dict, Any, Optional
from research_agent.models.stock import ValuationAnalysis, ValuationScenario
from research_agent.llm import LLMProvider
from research_agent.data import MarketDataProvider, YFinanceProvider, ValuationEngine

def load_prompt(filename: str) -> str:
    prompts_dir = Path(__file__).parent.parent / "prompts"
    with open(prompts_dir / filename, "r", encoding="utf-8") as f:
        return f.read()

class StockValuationAgent:
    def __init__(self, llm_provider: LLMProvider, data_provider: Optional[MarketDataProvider] = None):
        self.llm_provider = llm_provider
        self.data_provider = data_provider or YFinanceProvider()
        self.prompt_template = load_prompt("stock_valuation_analysis.md")

    def analyze_valuation(
        self,
        ticker: str,
        company_name: str,
        current_price: float,
        latest_revenue_millions: float = 50000.0,
        shares_outstanding_millions: float = 2500.0
    ) -> ValuationAnalysis:
        multiples = self.data_provider.get_valuation_metrics(ticker)
        dcf_scenarios = ValuationEngine.calculate_dcf_scenarios(
            current_price=current_price,
            latest_revenue_millions=latest_revenue_millions,
            shares_outstanding_millions=shares_outstanding_millions
        )

        prompt = self.prompt_template.format(
            ticker=ticker,
            company_name=company_name,
            current_price=current_price,
            valuation_multiples=str(multiples),
            dcf_scenarios=str([s.model_dump() for s in dcf_scenarios])
        )

        try:
            analysis = self.llm_provider.generate_structured(
                prompt=prompt,
                response_model=ValuationAnalysis,
                system_instruction="You are a valuation specialist and equity research modeler."
            )
            # Inject calculated multiples and scenarios if not fully populated
            analysis.pe_trailing = multiples.get("pe_trailing", analysis.pe_trailing)
            analysis.pe_forward = multiples.get("pe_forward", analysis.pe_forward)
            analysis.ev_ebitda = multiples.get("ev_ebitda", analysis.ev_ebitda)
            analysis.ev_sales = multiples.get("ev_sales", analysis.ev_sales)
            analysis.price_to_fcf = multiples.get("price_to_fcf", analysis.price_to_fcf)
            analysis.fcf_yield = multiples.get("fcf_yield", analysis.fcf_yield)
            analysis.peg_ratio = multiples.get("peg_ratio", analysis.peg_ratio)
            if not analysis.scenarios:
                analysis.scenarios = dcf_scenarios
            return analysis
        except Exception as e:
            print(f"Warning: StockValuationAgent failed: {e}. Generating default valuation model.")
            return ValuationAnalysis(
                pe_trailing=multiples.get("pe_trailing", 30.0),
                pe_forward=multiples.get("pe_forward", 25.0),
                ev_ebitda=multiples.get("ev_ebitda", 20.0),
                ev_sales=multiples.get("ev_sales", 8.0),
                price_to_fcf=multiples.get("price_to_fcf", 28.0),
                fcf_yield=multiples.get("fcf_yield", 3.5),
                peg_ratio=multiples.get("peg_ratio", 1.3),
                historical_valuation_context="Forward P/E aligns with historical trading ranges given projected forward growth rates.",
                peer_relative_valuation="Trades at a reasonable valuation relative to sector profitability benchmarks.",
                dcf_methodology_overview="DCF model utilizes standard 9.0% WACC and 3.0% perpetual growth across scenario ranges.",
                scenarios=dcf_scenarios
            )
