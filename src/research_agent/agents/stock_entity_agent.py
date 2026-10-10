from pathlib import Path
from typing import Dict, Any, Optional
from research_agent.models.stock import StockProfile
from research_agent.llm import LLMProvider
from research_agent.data import MarketDataProvider, YFinanceProvider

def load_prompt(filename: str) -> str:
    prompts_dir = Path(__file__).parent.parent / "prompts"
    with open(prompts_dir / filename, "r", encoding="utf-8") as f:
        return f.read()

class StockEntityAgent:
    def __init__(self, llm_provider: LLMProvider, data_provider: Optional[MarketDataProvider] = None):
        self.llm_provider = llm_provider
        self.data_provider = data_provider or YFinanceProvider()
        self.prompt_template = load_prompt("stock_entity_resolution.md")

    def resolve_entity(self, user_query: str) -> StockProfile:
        # Step 1: Clean query to extract candidate ticker or company name
        raw_ticker = user_query.strip().split()[0].upper().replace("$", "")
        market_data = self.data_provider.get_stock_profile(raw_ticker)

        prompt = self.prompt_template.format(
            user_query=user_query,
            market_data=str(market_data)
        )

        try:
            return self.llm_provider.generate_structured(
                prompt=prompt,
                response_model=StockProfile,
                system_instruction="You are an expert equity research analyst specializing in entity resolution."
            )
        except Exception as e:
            print(f"Warning: StockEntityAgent structured generation failed: {e}. Falling back to provider data.")
            return StockProfile(
                ticker=market_data.get("ticker", raw_ticker),
                company_name=market_data.get("company_name", raw_ticker),
                exchange=market_data.get("exchange", "NASDAQ"),
                currency=market_data.get("currency", "USD"),
                sector=market_data.get("sector", "Technology"),
                industry=market_data.get("industry", "Software & Services"),
                market_cap_billions=market_data.get("market_cap_billions", 100.0),
                current_price=market_data.get("current_price", 100.0),
                business_description=market_data.get("business_description", "Global enterprise delivering technology solutions."),
                monetization_engine=market_data.get("monetization_engine", "Generates revenue via core products, enterprise software, and subscriptions."),
                revenue_segments=market_data.get("revenue_segments", {}),
                geographic_exposure=market_data.get("geographic_exposure", {}),
                key_executives=market_data.get("key_executives", [])
            )
