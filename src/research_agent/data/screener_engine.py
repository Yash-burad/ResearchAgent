from typing import List, Dict, Any, Optional
from research_agent.models.stock import StockCandidateOpportunity

class ScreenerEngine:
    """
    Deterministic quantitative stock screening and dislocation detection engine.
    """

    DEFAULT_UNIVERSE = [
        {"ticker": "NVDA", "company_name": "NVIDIA Corp", "sector": "Technology", "price": 124.50, "mkt_cap": 3060.0, "pe_fwd": 32.5, "rev_growth": 45.0, "roic": 62.0, "drawdown_3m": -8.5, "fcf_yield": 3.8},
        {"ticker": "MSFT", "company_name": "Microsoft Corp", "sector": "Technology", "price": 428.00, "mkt_cap": 3180.0, "pe_fwd": 29.0, "rev_growth": 15.2, "roic": 28.5, "drawdown_3m": -4.2, "fcf_yield": 3.1},
        {"ticker": "GOOGL", "company_name": "Alphabet Inc", "sector": "Communication Services", "price": 165.20, "mkt_cap": 2040.0, "pe_fwd": 19.5, "rev_growth": 14.0, "roic": 26.0, "drawdown_3m": -12.0, "fcf_yield": 4.5},
        {"ticker": "AMZN", "company_name": "Amazon.com Inc", "sector": "Consumer Discretionary", "price": 188.40, "mkt_cap": 1960.0, "pe_fwd": 33.0, "rev_growth": 12.5, "roic": 18.0, "drawdown_3m": -5.0, "fcf_yield": 3.6},
        {"ticker": "META", "company_name": "Meta Platforms Inc", "sector": "Communication Services", "price": 505.00, "mkt_cap": 1280.0, "pe_fwd": 22.0, "rev_growth": 22.0, "roic": 31.0, "drawdown_3m": -3.5, "fcf_yield": 4.2},
        {"ticker": "TSM", "company_name": "Taiwan Semiconductor", "sector": "Technology", "price": 172.00, "mkt_cap": 890.0, "pe_fwd": 21.0, "rev_growth": 28.0, "roic": 29.0, "drawdown_3m": -11.5, "fcf_yield": 4.0},
        {"ticker": "ASML", "company_name": "ASML Holding NV", "sector": "Technology", "price": 780.00, "mkt_cap": 310.0, "pe_fwd": 27.5, "rev_growth": 18.0, "roic": 42.0, "drawdown_3m": -22.0, "fcf_yield": 3.4},
        {"ticker": "LLY", "company_name": "Eli Lilly & Co", "sector": "Healthcare", "price": 910.00, "mkt_cap": 860.0, "pe_fwd": 38.0, "rev_growth": 36.0, "roic": 25.0, "drawdown_3m": -7.0, "fcf_yield": 2.2},
        {"ticker": "UNH", "company_name": "UnitedHealth Group", "sector": "Healthcare", "price": 570.00, "mkt_cap": 525.0, "pe_fwd": 18.2, "rev_growth": 9.5, "roic": 17.5, "drawdown_3m": -1.5, "fcf_yield": 5.2},
        {"ticker": "JPM", "company_name": "JPMorgan Chase & Co", "sector": "Financials", "price": 215.00, "mkt_cap": 615.0, "pe_fwd": 12.5, "rev_growth": 11.0, "roic": 16.5, "drawdown_3m": 3.0, "fcf_yield": 6.1},
        {"ticker": "RELIANCE.NS", "company_name": "Reliance Industries Ltd", "sector": "Energy & Digital Services", "price": 2980.00, "mkt_cap": 240.0, "pe_fwd": 23.0, "rev_growth": 14.5, "roic": 12.5, "drawdown_3m": -6.0, "fcf_yield": 3.2}
    ]

    @classmethod
    def screen_opportunities(
        cls,
        sector_filter: Optional[str] = None,
        min_roic: float = 15.0,
        min_rev_growth: float = 10.0,
        max_pe: float = 40.0,
        candidates_limit: int = 5
    ) -> List[StockCandidateOpportunity]:
        """
        Filters the universe on fundamental quality and classifies dislocation archetypes.
        """
        shortlist = []
        universe = cls.DEFAULT_UNIVERSE

        if sector_filter and sector_filter.lower() != "all":
            universe = [s for s in universe if sector_filter.lower() in s["sector"].lower()]

        for item in universe:
            if item["roic"] >= min_roic and item["rev_growth"] >= min_rev_growth and item["pe_fwd"] <= max_pe:
                # Classify Archetype
                if item["drawdown_3m"] <= -10.0 and item["roic"] >= 25.0:
                    archetype = "Quality Growth + Temporary Selloff"
                    why_now = f"Structural moat compounder experiencing temporary {abs(item['drawdown_3m'])}% 3-month drawdown while ROIC remains pristine at {item['roic']}%."
                    upside = 28.0
                    tier = "High Conviction"
                elif item["rev_growth"] >= 20.0 and item["pe_fwd"] <= 25.0:
                    archetype = "Improving Fundamentals + Multiple Compression"
                    why_now = f"Rapid {item['rev_growth']}% revenue expansion trading at modest {item['pe_fwd']}x forward earnings."
                    upside = 32.0
                    tier = "High Conviction"
                elif item["fcf_yield"] >= 4.0:
                    archetype = "Capital Allocation & FCF Inflection"
                    why_now = f"Strong cash generative engine with {item['fcf_yield']}% FCF yield supporting ongoing share repurchases and reinvestment."
                    upside = 22.0
                    tier = "Medium Conviction"
                else:
                    archetype = "Earnings Inflection + Unrecognized Catalyst"
                    why_now = f"Consistent top-line growth ({item['rev_growth']}%) positioning the company for forward operating leverage."
                    upside = 18.0
                    tier = "Medium Conviction"

                shortlist.append(
                    StockCandidateOpportunity(
                        ticker=item["ticker"],
                        company_name=item["company_name"],
                        sector=item["sector"],
                        current_price=item["price"],
                        market_cap_billions=item["mkt_cap"],
                        opportunity_archetype=archetype,  # type: ignore
                        why_now=why_now,
                        fundamental_highlights=[
                            f"ROIC of {item['roic']}% reflects high capital return efficiency",
                            f"YoY Revenue Growth of {item['rev_growth']}% outpaces industry averages",
                            f"Forward P/E of {item['pe_fwd']}x vs historical 5-year average"
                        ],
                        catalysts=[
                            "Upcoming quarterly earnings release and guidance update",
                            "New product line deployment and gross margin expansion"
                        ],
                        critical_risks=[
                            "Macro consumer/enterprise spending headwinds",
                            "Heightened competitive pressure in core business vertical"
                        ],
                        implied_upside_percent=upside,
                        confidence_tier=tier,  # type: ignore
                        source_links=[
                            f"https://finance.yahoo.com/quote/{item['ticker']}",
                            f"https://www.sec.gov/edgar/searchedgar/companysearch"
                        ]
                    )
                )

        return shortlist[:candidates_limit]
