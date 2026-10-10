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

    def _resolve_canonical_ticker(self, user_query: str) -> str:
        clean = user_query.strip().split()[0].upper().replace("$", "")
        # Common typos and known brand aliases
        known_aliases = {
            "GGOGL": "GOOGL",
            "GOGL": "GOOGL",
            "GOOGLE": "GOOGL",
            "ALPHABET": "GOOGL",
            "APPLE": "AAPL",
            "MICROSOFT": "MSFT",
            "AMAZON": "AMZN",
            "TESLA": "TSLA",
            "FACEBOOK": "META",
            "NETFLIX": "NFLX",
            "NVIDIA": "NVDA"
        }
        if clean in known_aliases:
            return known_aliases[clean]

        # Verify if clean ticker exists on yfinance
        try:
            import yfinance as yf
            t = yf.Ticker(clean)
            if t.info and (t.info.get("currentPrice") or t.info.get("regularMarketPrice") or t.info.get("shortName")):
                return clean
        except Exception:
            pass

        # Try search on yfinance
        try:
            import yfinance as yf
            s = yf.Search(user_query)
            if s.quotes:
                for q in s.quotes:
                    sym = q.get("symbol")
                    if sym and not sym.startswith("^"):
                        return sym.upper()
        except Exception:
            pass

        # Use LLM to resolve ticker if typo or company name
        try:
            resolved = self.llm_provider.generate(
                f"You are a financial entity resolver. Given the user input (which may be a typo, company name, or brand), return ONLY the primary US stock ticker symbol as 1 word with no punctuation.\nInput: {user_query}\nTicker:"
            ).strip().upper().replace("$", "").split()[0]
            if 1 <= len(resolved) <= 6 and resolved.isalpha():
                return resolved
        except Exception:
            pass

        return clean

    def resolve_entity(self, user_query: str) -> StockProfile:
        canonical_ticker = self._resolve_canonical_ticker(user_query)
        market_data = self.data_provider.get_stock_profile(canonical_ticker)


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
