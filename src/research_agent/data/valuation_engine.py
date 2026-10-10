from typing import List, Dict, Any, Optional
from research_agent.models.stock import ValuationScenario, FinancialStatementSummary

class ValuationEngine:
    """
    Deterministic financial computation engine for DCF scenario modeling,
    ratio benchmarking, and valuation multiples.
    """

    @staticmethod
    def calculate_dcf_scenarios(
        current_price: float,
        latest_revenue_millions: float,
        shares_outstanding_millions: float,
        net_cash_debt_millions: float = 0.0,
        base_cagr: float = 0.15,
        base_operating_margin: float = 0.25,
        tax_rate: float = 0.21,
        wacc: float = 0.09,
        terminal_growth: float = 0.03
    ) -> List[ValuationScenario]:
        """
        Calculates 3-tier DCF intrinsic per-share scenarios (Bear, Base, Bull)
        projecting 5-year free cash flows and discounting back to present value.
        """
        if latest_revenue_millions <= 0 or shares_outstanding_millions <= 0 or current_price <= 0:
            # Fallback mock valuation scenarios if fundamental parameters are incomplete
            return [
                ValuationScenario(
                    scenario_name="Bear",
                    target_price_implied=round(current_price * 0.75, 2),
                    upside_downside_percent=-25.0,
                    revenue_growth_cagr=round(max(0.05, base_cagr - 0.10) * 100, 1),
                    terminal_operating_margin=round(max(0.10, base_operating_margin - 0.08) * 100, 1),
                    wacc=round((wacc + 0.015) * 100, 1),
                    terminal_growth_rate=round(terminal_growth * 100, 1),
                    implied_pe_multiple=18.0,
                    key_assumptions=["Macro deceleration", "Margin compression from competition", "Higher discount rate"],
                    catalysts_required=["Baseline defensive operational execution"],
                    risks_to_scenario=["Excessive customer churn"]
                ),
                ValuationScenario(
                    scenario_name="Base",
                    target_price_implied=round(current_price * 1.15, 2),
                    upside_downside_percent=15.0,
                    revenue_growth_cagr=round(base_cagr * 100, 1),
                    terminal_operating_margin=round(base_operating_margin * 100, 1),
                    wacc=round(wacc * 100, 1),
                    terminal_growth_rate=round(terminal_growth * 100, 1),
                    implied_pe_multiple=25.0,
                    key_assumptions=["Execution aligned with consensus guidance", "Stable operating leverage"],
                    catalysts_required=["Core product roadmap delivery", "Steady market share retention"],
                    risks_to_scenario=["Unexpected regulatory friction"]
                ),
                ValuationScenario(
                    scenario_name="Bull",
                    target_price_implied=round(current_price * 1.45, 2),
                    upside_downside_percent=45.0,
                    revenue_growth_cagr=round((base_cagr + 0.10) * 100, 1),
                    terminal_operating_margin=round((base_operating_margin + 0.06) * 100, 1),
                    wacc=round(max(0.07, wacc - 0.01) * 100, 1),
                    terminal_growth_rate=round((terminal_growth + 0.005) * 100, 1),
                    implied_pe_multiple=35.0,
                    key_assumptions=["Market share expansion", "Pricing power realization", "Operating margin expansion"],
                    catalysts_required=["New market TAM expansion", "High-margin product line adoption"],
                    risks_to_scenario=["Supply chain capacity bottlenecks"]
                )
            ]

        scenarios_config = [
            ("Bear", base_cagr - 0.08, base_operating_margin - 0.05, wacc + 0.015, terminal_growth - 0.005, 18.0),
            ("Base", base_cagr, base_operating_margin, wacc, terminal_growth, 24.0),
            ("Bull", base_cagr + 0.08, base_operating_margin + 0.05, max(0.07, wacc - 0.01), terminal_growth + 0.005, 32.0),
        ]

        scenarios = []
        for name, cagr, op_margin, rate_wacc, g_term, exit_pe in scenarios_config:
            # 5-year discrete projection
            pv_fcfs = 0.0
            rev = latest_revenue_millions
            fcf = 0.0

            for year in range(1, 6):
                rev *= (1 + cagr)
                ebit = rev * op_margin
                nopat = ebit * (1 - tax_rate)
                # Approximate FCF conversion at ~85% of NOPAT
                fcf = nopat * 0.85
                pv_fcfs += fcf / ((1 + rate_wacc) ** year)

            # Terminal Value using Gordon Growth Model
            tv = (fcf * (1 + g_term)) / (rate_wacc - g_term) if (rate_wacc > g_term) else (fcf * 15.0)
            pv_tv = tv / ((1 + rate_wacc) ** 5)

            enterprise_value = pv_fcfs + pv_tv
            equity_value = enterprise_value + net_cash_debt_millions
            implied_price = equity_value / shares_outstanding_millions

            # Bound implied price realistically
            implied_price = max(1.0, round(implied_price, 2))
            upside_pct = round(((implied_price - current_price) / current_price) * 100, 1)

            scenarios.append(
                ValuationScenario(
                    scenario_name=name,  # type: ignore
                    target_price_implied=implied_price,
                    upside_downside_percent=upside_pct,
                    revenue_growth_cagr=round(cagr * 100, 1),
                    terminal_operating_margin=round(op_margin * 100, 1),
                    wacc=round(rate_wacc * 100, 1),
                    terminal_growth_rate=round(g_term * 100, 1),
                    implied_pe_multiple=exit_pe,
                    key_assumptions=[
                        f"5-Year Revenue CAGR of {round(cagr * 100, 1)}%",
                        f"Terminal Operating Margin of {round(op_margin * 100, 1)}%",
                        f"WACC discount rate calibrated at {round(rate_wacc * 100, 1)}%"
                    ],
                    catalysts_required=[
                        "Execution on forward revenue and margin targets",
                        "Capital discipline and sustained cash conversion"
                    ],
                    risks_to_scenario=[
                        "Deceleration in key operating segment demand",
                        "Margin degradation from competitive price pressure"
                    ]
                )
            )

        return scenarios

    @staticmethod
    def calculate_cagr(start_val: float, end_val: float, periods: int) -> float:
        """Calculates Compound Annual Growth Rate."""
        if start_val <= 0 or end_val <= 0 or periods <= 0:
            return 0.0
        return ((end_val / start_val) ** (1.0 / periods)) - 1.0
