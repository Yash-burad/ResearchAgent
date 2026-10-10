from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class MarketDataProvider(ABC):
    """
    Abstract interface for financial and market data providers.
    """
    @abstractmethod
    def get_stock_profile(self, ticker: str) -> Dict[str, Any]:
        """Fetch metadata, market cap, sector, industry, and description."""
        ...

    @abstractmethod
    def get_financial_statements(self, ticker: str) -> Dict[str, Any]:
        """Fetch balance sheet, income statement, and cash flow historical periods."""
        ...

    @abstractmethod
    def get_valuation_metrics(self, ticker: str) -> Dict[str, Any]:
        """Fetch relative valuation multiples (P/E, EV/EBITDA, P/S, FCF yield, PEG)."""
        ...

    @abstractmethod
    def get_historical_prices(self, ticker: str, period: str = "1y", current_price: Optional[float] = None) -> List[Dict[str, Any]]:
        """Fetch historical time-series OHLCV data."""
        ...

    @abstractmethod
    def get_recent_news(self, ticker: str, max_items: int = 25) -> List[Dict[str, Any]]:
        """Fetch raw recent news articles with titles, timestamps, and URLs."""
        ...

    @abstractmethod
    def get_analyst_estimates(self, ticker: str) -> Dict[str, Any]:
        """Fetch consensus targets, revenue/EPS estimates, and revision trends."""
        ...
