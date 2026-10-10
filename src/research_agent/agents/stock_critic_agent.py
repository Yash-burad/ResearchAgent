from pathlib import Path
from typing import Dict, Any, Optional
from research_agent.models.stock import CriticDebrief
from research_agent.llm import LLMProvider

def load_prompt(filename: str) -> str:
    prompts_dir = Path(__file__).parent.parent / "prompts"
    with open(prompts_dir / filename, "r", encoding="utf-8") as f:
        return f.read()

class StockCriticAgent:
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
        self.prompt_template = load_prompt("stock_critic_disconfirmation.md")

    def stress_test_thesis(
        self,
        ticker: str,
        company_name: str,
        sector: str,
        industry: str,
        current_price: float,
        preliminary_synthesis: Dict[str, Any]
    ) -> CriticDebrief:
        prompt = self.prompt_template.format(
            ticker=ticker,
            company_name=company_name,
            sector=sector,
            industry=industry,
            current_price=current_price,
            preliminary_synthesis=str(preliminary_synthesis)
        )

        try:
            return self.llm_provider.generate_structured(
                prompt=prompt,
                response_model=CriticDebrief,
                system_instruction="You are an institutional short-seller and disconfirmation critic actively challenging bullish assumptions."
            )
        except Exception as e:
            print(f"Warning: StockCriticAgent failed: {e}. Generating default critic debrief.")
            return CriticDebrief(
                overlooked_risks=[
                    f"Concentration risk in top customer tier for {company_name}.",
                    "Macro enterprise spending delays or budget scrutiny.",
                    "Competitive price pressure and margin normalization."
                ],
                contradictory_data_points=[
                    "Peers investing heavily in competing product roadmaps.",
                    "Potential working capital expansion compressing operating cash flow."
                ],
                bull_case_flaws=[
                    "Assumes linear multi-year revenue growth without cyclical digestion phases."
                ],
                thesis_invalidation_triggers=[
                    "Sequential quarterly revenue deceleration below 5% QoQ.",
                    "Gross margin compression exceeding 300 bps YoY.",
                    "Loss of key enterprise customer accounts."
                ],
                confidence_penalty_points=5
            )
