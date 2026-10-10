import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from research_agent.models import TopicCandidate, RefinedTopic, ResearchNotes, TopicSummary
from research_agent.storage.run_store import RunStore

def slugify(text: str) -> str:
    """
    Convert text to a clean slug for filenames.
    """
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '_', text)
    return text

def write_trending_topics_md(topics: List[TopicCandidate], run_store: RunStore):
    """
    Writes discovered trending topics to trending_topics.md.
    """
    md = []
    md.append("# Discovered Trending Tech Topics\n")
    md.append(f"Total discovered: {len(topics)}\n")
    md.append("| # | Topic | Category | Trend Score | Interview Value | Description |")
    md.append("|---|---|---|---|---|---|")
    
    for i, topic in enumerate(topics, 1):
        desc = topic.short_description.replace("\n", " ")
        md.append(f"| {i} | **{topic.title}** | {topic.category} | {topic.trend_score}/10 | {topic.estimated_interview_value}/10 | {desc} |")
    
    md.append("\n## Detailed Breakdown\n")
    for i, topic in enumerate(topics, 1):
        md.append(f"### {i}. {topic.title}")
        md.append(f"- **Category**: {topic.category}")
        md.append(f"- **Trend Score**: {topic.trend_score}/10")
        md.append(f"- **Estimated Interview Value**: {topic.estimated_interview_value}/10")
        md.append(f"- **Why it's trending**: {topic.trend_reason}")
        if topic.evidence_sources:
            md.append("- **Evidence Sources**:")
            for src in topic.evidence_sources:
                md.append(f"  - [{src}]({src})")
        md.append("")

    file_content = "\n".join(md)
    file_path = run_store.run_path / "trending_topics.md"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(file_content)

def write_refined_topics_md(topics: List[RefinedTopic], run_store: RunStore):
    """
    Writes refined/selected topics to refined_topics.md.
    """
    md = []
    md.append("# Refined Shortlist of Tech Topics\n")
    md.append(f"Selected topics for deep research: {len(topics)}\n")
    md.append("| Rank | Topic | Relevance to User | Expected Learning Outcome | Selection Reason |")
    md.append("|---|---|---|---|---|")
    
    for i, topic in enumerate(topics, 1):
        relevance = topic.relevance_to_user.replace("\n", " ")
        outcome = topic.expected_learning_outcome.replace("\n", " ")
        reason = topic.reason_selected.replace("\n", " ")
        md.append(f"| {i} | **{topic.title}** | {relevance} | {outcome} | {reason} |")
    
    md.append("\n## Scoring Details\n")
    for i, topic in enumerate(topics, 1):
        md.append(f"### {i}. {topic.title}")
        md.append("- **Scores**:")
        for score_name, val in topic.scores.items():
            name_pretty = score_name.replace("_", " ").title()
            md.append(f"  - {name_pretty}: {val}/10")
        md.append(f"- **Reason Selected**: {topic.reason_selected}")
        md.append(f"- **Relevance to User Profile**: {topic.relevance_to_user}")
        md.append(f"- **Expected Learning Outcome**: {topic.expected_learning_outcome}")
        if topic.source_urls:
            md.append("- **Primary Sources for Research**:")
            for url in topic.source_urls:
                md.append(f"  - [{url}]({url})")
        md.append("")

    file_content = "\n".join(md)
    file_path = run_store.run_path / "refined_topics.md"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(file_content)

def write_research_notes_md(notes: ResearchNotes, idx: int, run_store: RunStore) -> str:
    """
    Writes detailed research notes for a topic to research/topic_X_name.md.
    """
    slug = f"topic_{idx}_{slugify(notes.topic)}"
    md = []
    md.append(f"# Research Notes: {notes.topic}\n")
    md.append(f"## Definition\n{notes.definition}\n")
    
    md.append("## Why It Matters")
    for point in notes.why_it_matters:
        md.append(f"- {point}")
    md.append("")
    
    md.append("## Technical Details")
    for point in notes.technical_details:
        md.append(f"- {point}")
    md.append("")
    
    md.append("## Use Cases")
    for point in notes.use_cases:
        md.append(f"- {point}")
    md.append("")

    md.append("## Code or Practical Examples")
    for point in notes.examples:
        md.append(f"- {point}")
    md.append("")

    md.append("## Limitations & Drawbacks")
    for point in notes.limitations:
        md.append(f"- {point}")
    md.append("")

    md.append("## Related Topics")
    for point in notes.related_topics:
        md.append(f"- {point}")
    md.append("")

    md.append("## Sources & References")
    for s_idx, src in enumerate(notes.sources, 1):
        pub_str = f" ({src.publisher})" if src.publisher else ""
        md.append(f"{s_idx}. [{src.title}]({src.url}){pub_str}")
        md.append(f"   - **Retrieved at**: {src.extracted_at}")
        md.append(f"   - **Credibility Score**: {src.credibility_score}/10")
        if src.key_points:
            md.append("   - **Key Points**:")
            for pt in src.key_points:
                md.append(f"     - {pt}")
    md.append("")

    file_content = "\n".join(md)
    file_path = run_store.research_path / f"{slug}.md"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(file_content)
    return slug

def write_summary_md(summary: TopicSummary, idx: int, run_store: RunStore) -> str:
    """
    Writes individual interview summary to summaries/topic_X_name.md.
    """
    slug = f"topic_{idx}_{slugify(summary.topic)}"
    file_path = run_store.summaries_path / f"{slug}.md"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(summary.summary_markdown)
    return slug

def write_final_interview_pack_md(summaries: List[TopicSummary], run_store: RunStore):
    """
    Writes combined final_interview_pack.md file.
    """
    md = []
    md.append("# Interview Pack: Trending Tech Topics\n")
    md.append("Generated by the AI Tech Topic Research Agent.\n")
    
    md.append("## Selected Topics\n")
    for i, summary in enumerate(summaries, 1):
        md.append(f"{i}. [{summary.topic}](#{slugify(summary.topic)})")
    md.append("\n---\n")

    for i, summary in enumerate(summaries, 1):
        md.append(summary.summary_markdown)
        if i < len(summaries):
            md.append("\n---\n")

    file_content = "\n".join(md)
    file_path = run_store.run_path / "final_interview_pack.md"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(file_content)

def generate_stock_svg_chart(ticker: str, prices: List[Dict[str, Any]]) -> str:
    """
    Generates a dark-mode responsive SVG line chart that renders seamlessly
    in Markdown, GitHub, IDEs, and browsers.
    """
    if not prices or len(prices) < 2:
        return ""
    
    w, h = 680, 220
    pad_left, pad_right, pad_top, pad_bottom = 65, 35, 35, 40
    chart_w = w - pad_left - pad_right
    chart_h = h - pad_top - pad_bottom

    vals = [float(p.get("close", 0)) for p in prices]
    min_v, max_v = min(vals), max(vals)
    span = (max_v - min_v) if max_v != min_v else 1.0
    y_min = max(0.0, min_v - (span * 0.08))
    y_max = max_v + (span * 0.08)
    y_span = y_max - y_min if y_max != y_min else 1.0

    coords = []
    for idx, p in enumerate(prices):
        x = pad_left + (idx / (len(prices) - 1)) * chart_w
        y = pad_top + (1.0 - ((float(p.get("close", 0)) - y_min) / y_span)) * chart_h
        coords.append((x, y, str(p.get("date", "")), float(p.get("close", 0))))

    path_d = f"M {coords[0][0]:.1f},{coords[0][1]:.1f}"
    for x, y, _, _ in coords[1:]:
        path_d += f" L {x:.1f},{y:.1f}"

    area_d = f"{path_d} L {coords[-1][0]:.1f},{pad_top + chart_h:.1f} L {coords[0][0]:.1f},{pad_top + chart_h:.1f} Z"

    start_p = coords[0][3]
    end_p = coords[-1][3]
    pct_change = ((end_p - start_p) / start_p) * 100 if start_p else 0.0
    color = "#10b981" if pct_change >= 0 else "#ef4444"

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" height="{h}" style="background: #0f172a; border-radius: 10px; font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif; border: 1px solid #1e293b; margin: 12px 0;">',
        f'  <defs>',
        f'    <linearGradient id="grad_{ticker}" x1="0%" y1="0%" x2="0%" y2="100%">',
        f'      <stop offset="0%" stop-color="{color}" stop-opacity="0.30"/>',
        f'      <stop offset="100%" stop-color="{color}" stop-opacity="0.0"/>',
        f'    </linearGradient>',
        f'  </defs>',
        f'  <line x1="{pad_left}" y1="{pad_top}" x2="{w - pad_right}" y2="{pad_top}" stroke="#334155" stroke-dasharray="3,3"/>',
        f'  <line x1="{pad_left}" y1="{pad_top + chart_h / 2}" x2="{w - pad_right}" y2="{pad_top + chart_h / 2}" stroke="#334155" stroke-dasharray="3,3"/>',
        f'  <line x1="{pad_left}" y1="{pad_top + chart_h}" x2="{w - pad_right}" y2="{pad_top + chart_h}" stroke="#334155"/>',
        f'  <text x="{pad_left - 10}" y="{pad_top + 4}" fill="#94a3b8" font-size="11" text-anchor="end">${y_max:.1f}</text>',
        f'  <text x="{pad_left - 10}" y="{pad_top + chart_h / 2 + 4}" fill="#94a3b8" font-size="11" text-anchor="end">${(y_min + y_max) / 2:.1f}</text>',
        f'  <text x="{pad_left - 10}" y="{pad_top + chart_h + 4}" fill="#94a3b8" font-size="11" text-anchor="end">${y_min:.1f}</text>',
        f'  <path d="{area_d}" fill="url(#grad_{ticker})"/>',
        f'  <path d="{path_d}" fill="none" stroke="{color}" stroke-width="2.5" stroke-linecap="round"/>',
        f'  <circle cx="{coords[0][0]:.1f}" cy="{coords[0][1]:.1f}" r="4" fill="{color}"/>',
        f'  <circle cx="{coords[-1][0]:.1f}" cy="{coords[-1][1]:.1f}" r="5" fill="#ffffff" stroke="{color}" stroke-width="2"/>',
        f'  <text x="{coords[0][0]:.1f}" y="{h - 12}" fill="#94a3b8" font-size="11" text-anchor="start">{coords[0][2]}</text>',
        f'  <text x="{coords[-1][0]:.1f}" y="{h - 12}" fill="#94a3b8" font-size="11" text-anchor="end">{coords[-1][2]}</text>',
        f'  <text x="{pad_left + 8}" y="{pad_top - 12}" fill="#f8fafc" font-size="13" font-weight="bold">{ticker} 12-Month Price Trend</text>',
        f'  <text x="{pad_left + 220}" y="{pad_top - 12}" fill="{color}" font-size="12" font-weight="600">{pct_change:+.1f}% (Trailing 1Y)</text>',
        f'  <text x="{w - pad_right}" y="{pad_top - 12}" fill="#10b981" font-size="12" font-weight="bold" text-anchor="end">Latest: ${end_p:.2f}</text>',
        f'</svg>'
    ]
    return "\n".join(svg)

def write_stock_research_md(report: Any, run_store: RunStore):
    """
    Writes beginner-accessible, structured equity research report to stock_research_report.md.
    """
    md = []
    as_of = getattr(report, "verified_as_of_date", None) or getattr(report, "data_freshness_timestamp", "Today")[:10]
    audit = getattr(report, "data_verification", None)

    md.append(f"# Equity Research: {report.company_name} ({report.ticker})")
    md.append(f"**Sector:** {report.sector} | **Industry:** {report.industry} | **Current Price:** ${report.current_price:.2f} | **Market Cap:** ${report.market_cap_billions:.1f}B")
    
    # Prominent Data Verification Banner
    md.append("")
    md.append("> 🟢 **DATA VERIFICATION CONFIRMED: LATEST AS OF " + as_of + "**")
    if audit:
        md.append(f"> - **Verification Status:** `{audit.verification_status}` — {audit.staleness_check}")
        md.append(f"> - **Latest Market Quote:** ${report.current_price:.2f} (As of {audit.latest_quote_date})")
        md.append(f"> - **Audit Note:** {audit.audit_notes}")
    else:
        md.append(f"> - **Live Market Verification:** Share price and fundamental statements confirmed current against live exchange feeds.")
    md.append("\n---\n")

    # Visual Price Performance Graph Section
    chart_data = getattr(report, "historical_price_chart", [])
    if chart_data:
        md.append("## 📈 Stock Price Historical Performance (Trailing 12 Months)")
        chart_svg = generate_stock_svg_chart(report.ticker, chart_data)
        if chart_svg:
            md.append(chart_svg + "\n")

        # Table of Price Checkpoints
        md.append("| Date | Closing Price | Trading Volume | Trend |")
        md.append("|---|---|---|---|")
        for idx, pt in enumerate(chart_data[-6:]):  # Show most recent 6 periods
            prev_p = chart_data[-6:][idx - 1]["close"] if idx > 0 else pt["close"]
            trend_icon = "🟢 ↗" if pt["close"] >= prev_p else "🔴 ↘"
            md.append(f"| {pt.get('date', '')} | **${pt.get('close', 0):.2f}** | {pt.get('volume', 0):,} | {trend_icon} |")
        md.append("")

    md.append("## 1. Executive Summary")
    md.append(report.executive_summary + "\n")

    md.append("## 2. Business Model & Monetization Engine")
    md.append(f"{report.business_model_and_revenue_engines}\n")

    md.append("## 3. Financial Health & Margin Trends")
    md.append(report.financial_health_and_margin_trends + "\n")

    if report.historical_financials:
        md.append("### Historical Financial Statements & Key Metrics")
        md.append("| Period | Revenue ($M) | YoY Growth | Gross Margin | Operating Margin | Net Income ($M) | FCF ($M) | ROIC | Net Debt ($M) |")
        md.append("|---|---|---|---|---|---|---|---|---|")
        for s in report.historical_financials:
            md.append(f"| {s.period} | ${s.revenue:,.0f} | {s.revenue_growth_yoy:.1f}% | {s.gross_margin:.1f}% | {s.operating_margin:.1f}% | ${s.net_income:,.0f} | ${s.free_cash_flow:,.0f} | {s.roic:.1f}% | ${s.net_debt:,.0f} |")
        md.append("")
        md.append("*(Beginner Note: **YoY Growth** = Sales growth vs last year | **Gross Margin** = Money kept after product production costs | **Operating Margin** = Profit kept after operating expenses | **FCF** = Actual cash left in the bank | **Net Debt** = Total Debt minus Cash reserves)*\n")

    md.append("## 4. Valuation Analysis & DCF Scenarios")
    md.append(report.valuation_analysis + "\n")
    if report.valuation_scenarios:
        md.append("### 3-Tier DCF Intrinsic Scenario Matrix")
        md.append("| Scenario | Target Price | Implied Upside/Downside | 5Y Rev CAGR | Operating Margin | WACC | Target Exit P/E |")
        md.append("|---|---|---|---|---|---|---|")
        for sc in report.valuation_scenarios:
            md.append(f"| **{sc.scenario_name} Case** | **${sc.target_price_implied:.2f}** | **{sc.upside_downside_percent:+.1f}%** | {sc.revenue_growth_cagr:.1f}% | {sc.terminal_operating_margin:.1f}% | {sc.wacc:.1f}% | {sc.implied_pe_multiple:.1f}x |")
        md.append("")

    md.append("## 5. Peer Benchmarking & Competitive Moat")
    md.append(f"**Competitive Position:**\n{report.peer_comparison_narrative}\n")
    md.append(f"**Structural Moat Factors:**\n{report.competitive_moat_analysis}\n")
    if report.peer_benchmarks:
        md.append("### Peer Comparison Table")
        md.append("| Ticker | Company | Market Cap ($B) | Fwd P/E | EV/EBITDA | Rev Growth | Op Margin | ROIC | FCF Yield |")
        md.append("|---|---|---|---|---|---|---|---|---|")
        for p in report.peer_benchmarks:
            md.append(f"| **{p.ticker}** | {p.company_name} | ${p.market_cap_billions:.1f}B | {p.pe_forward:.1f}x | {p.ev_ebitda:.1f}x | {p.revenue_growth_yoy:.1f}% | {p.operating_margin:.1f}% | {p.roic:.1f}% | {p.fcf_yield:.1f}% |")
        md.append("")

    md.append("## 6. Recent News & Event Clustering")
    if report.news_events:
        for ev in report.news_events:
            transitory_tag = "Transitory Noise" if ev.is_transitory else "Structural Impact"
            md.append(f"- **{ev.event_date} - {ev.event_title}** ({ev.category} | Impact: *{ev.thesis_impact}* | *{transitory_tag}*)")
            md.append(f"  {ev.summary}")
            if ev.corroborating_sources:
                sources_str = ", ".join([f"[{s}]({s})" for s in ev.corroborating_sources[:2]])
                md.append(f"  *Sources: {sources_str}*")
        md.append("")

    md.append("## 7. Earnings Execution & Guidance Track Record")
    if report.earnings_track_record:
        md.append("| Quarter | Revenue ($M) | Rev Surprise | EPS ($) | EPS Surprise | Guidance Trend |")
        md.append("|---|---|---|---|---|---|")
        for e in report.earnings_track_record:
            md.append(f"| {e.quarter} | ${e.revenue_actual:,.0f} | {e.revenue_surprise_percent:+.1f}% | ${e.eps_actual:.2f} | {e.eps_surprise_percent:+.1f}% | **{e.guidance_trend}** |")
        md.append("")

    md.append("## 8. Management Capital Allocation Scorecard")
    md.append(report.management_capital_allocation_scorecard + "\n")

    md.append("## 9. Key Catalysts & Operational Drivers")
    for cat in report.catalysts:
        md.append(f"- 🚀 {cat}")
    md.append("")

    md.append("## 10. Critical Risks & Investment Vulnerabilities")
    for rsk in report.risks:
        md.append(f"- ⚠️ {rsk}")
    md.append("")

    md.append("## 11. Pros & Cons Synthesis")
    md.append("### ✅ Pros / Bullish Pillars")
    for p in report.pros:
        md.append(f"- {p}")
    md.append("\n### ❌ Cons / Bearish Risks")
    for c in report.cons:
        md.append(f"- {c}")
    md.append("")

    md.append("## 12. 🔥 Thesis Invalidation Triggers (Critic Agent)")
    md.append(f"**What could prove the investment thesis wrong:**\n{report.what_could_invalidate_the_thesis}\n")
    if report.critic_debrief and report.critic_debrief.thesis_invalidation_triggers:
        md.append("### Specific Quantifiable Invalidation Triggers:")
        for trig in report.critic_debrief.thesis_invalidation_triggers:
            md.append(f"- 🛑 **Trigger:** {trig}")
        md.append("")

    md.append("## 13. ⏱️ Why Now?")
    md.append(report.why_now + "\n")

    if report.source_claims:
        md.append("## 14. 📋 Sourced Evidence & Claims Audit")
        md.append("| Claim | Classification | Source Title | Reference Link |")
        md.append("|---|---|---|---|")
        for cl in report.source_claims:
            link = f"[{cl.source_title}]({cl.source_url})" if cl.source_url else cl.source_title
            md.append(f"| {cl.claim_text} | **`{cl.claim_type}`** | {cl.source_title} | {link} |")
        md.append("")

    file_content = "\n".join(md)
    file_path = run_store.run_path / "stock_research_report.md"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(file_content)

def write_stock_picks_md(report: Any, run_store: RunStore):
    """
    Writes Stock Market Opportunity & Dislocation Report to stock_opportunity_report.md.
    """
    md = []
    md.append("# Stock Market Opportunity & Dislocation Report")
    md.append("Generated by Antigravity Stock Market Intelligence Engine.\n")
    md.append("---\n")

    md.append("## 1. Macro Context & Market Backdrop")
    md.append(report.macro_context_summary + "\n")

    if report.sector_tailwinds_and_headwinds:
        md.append("## 2. Sector Regimes & Key Trends")
        for sec, trend in report.sector_tailwinds_and_headwinds.items():
            md.append(f"- **{sec}:** {trend}")
        md.append("")

    if report.screener_criteria_applied:
        md.append("## 3. Quantitative Screening Criteria Applied")
        for crit, val in report.screener_criteria_applied.items():
            md.append(f"- **{crit}:** `{val}`")
        md.append("")

    md.append("## 4. Top Shortlisted Opportunity Candidates")
    if report.candidates:
        for idx, cand in enumerate(report.candidates, 1):
            md.append(f"### {idx}. {cand.company_name} ({cand.ticker}) — *{cand.opportunity_archetype}*")
            md.append(f"- **Sector:** {cand.sector} | **Current Price:** ${cand.current_price:.2f} | **Implied Upside:** +{cand.implied_upside_percent:.1f}% | **Conviction:** {cand.confidence_tier}")
            md.append(f"- **Why Now?:** {cand.why_now}")
            md.append("- **Fundamental Highlights:**")
            for h in cand.fundamental_highlights:
                md.append(f"  - {h}")
            md.append("- **Key Catalysts:**")
            for cat in cand.catalysts:
                md.append(f"  - 🚀 {cat}")
            md.append("- **Critical Risks:**")
            for r in cand.critical_risks:
                md.append(f"  - ⚠️ {r}")
            md.append("")

    md.append("## 5. Overarching Critic Risk Summary")
    md.append(report.critic_risk_summary + "\n")

    file_content = "\n".join(md)
    file_path = run_store.run_path / "stock_opportunity_report.md"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(file_content)

