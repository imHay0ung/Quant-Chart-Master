"""
report.py
─────────
모든 출력(스냅샷·신호·차트·매크로·5단계 골격)을 한 페이지 HTML로 묶는다.
의존성을 줄이려 Jinja2 없이 f-string으로 짰다(첫 커밋은 가벼운 게 좋다).
"""
from __future__ import annotations


def _li(items: list[str]) -> str:
    return "".join(f"<li>{x}</li>" for x in items)


def build_report(
    ticker: str,
    snap: dict,
    signals: list[str],
    chart_html: str,
    macro_lines: list[str],
    fundamental_notes: dict[str, str],
    timeframe_notes: list[str] | None = None,
) -> str:
    """
    Assemble the full single-page report.

    fundamental_notes: 5단계 분석 텍스트. 코드가 자동 생성하지 않고
    사람/LLM이 채우는 칸 — 빈 값이면 '수동 입력 필요'로 표시된다.
    """
    tf_block = ""
    if timeframe_notes:
        tf_block = f"""
        <section>
          <h2>멀티 타임프레임 상호작용</h2>
          <ul>{_li(timeframe_notes)}</ul>
        </section>"""

    fund_rows = "".join(
        f"<tr><td class='k'>{k}</td><td>{v or '<i>수동 입력 필요</i>'}</td></tr>"
        for k, v in fundamental_notes.items()
    )

    return f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{ticker} — Quant Chart Report ({snap['date']})</title>
<style>
  body {{ font-family: -apple-system, system-ui, sans-serif; max-width: 1100px;
         margin: 0 auto; padding: 24px; color: #1e293b; line-height: 1.6; }}
  h1 {{ font-size: 1.6rem; margin-bottom: 4px; }}
  .sub {{ color: #64748b; margin-bottom: 24px; }}
  section {{ margin: 28px 0; }}
  h2 {{ font-size: 1.15rem; border-bottom: 2px solid #e2e8f0; padding-bottom: 6px; }}
  ul {{ padding-left: 20px; }}
  li {{ margin: 4px 0; }}
  table {{ border-collapse: collapse; width: 100%; }}
  td {{ border: 1px solid #e2e8f0; padding: 8px 12px; vertical-align: top; }}
  .k {{ background: #f8fafc; font-weight: 600; width: 180px; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit,minmax(160px,1fr));
          gap: 12px; }}
  .card {{ background: #f8fafc; border-radius: 8px; padding: 12px; }}
  .card .v {{ font-size: 1.4rem; font-weight: 700; }}
  .card .l {{ color: #64748b; font-size: 0.85rem; }}
  .warn {{ color: #b45309; }}
  .disclaimer {{ color: #94a3b8; font-size: 0.8rem; margin-top: 40px;
                border-top: 1px solid #e2e8f0; padding-top: 12px; }}
</style></head><body>

<h1>{ticker} — 기술적 분석 리포트</h1>
<div class="sub">기준일 {snap['date']} · 자동 생성 (지표·백분위수는 코드, 판단은 사람)</div>

<section>
  <h2>핵심 지표 스냅샷</h2>
  <div class="grid">
    <div class="card"><div class="v">${snap['close']:.2f}</div><div class="l">종가</div></div>
    <div class="card"><div class="v">{snap['rsi']:.1f}</div>
        <div class="l">RSI ({snap['rsi_pctile']:.0f}%ile)</div></div>
    <div class="card"><div class="v">{snap['dist_200ma_pct']:+.1f}%</div>
        <div class="l">200MA 이격 ({snap['dist_200ma_pctile']:.0f}%ile)</div></div>
    <div class="card"><div class="v">{snap['cmf']:+.3f}</div>
        <div class="l">CMF ({snap['cmf_pctile']:.0f}%ile)</div></div>
  </div>
</section>

<section>
  <h2>차트</h2>
  {chart_html}
</section>

<section>
  <h2>기술적 신호 (관찰 사실)</h2>
  <ul>{_li(signals)}</ul>
</section>
{tf_block}
<section>
  <h2>매크로 컨텍스트 (가격성 지표)</h2>
  <ul>{_li(macro_lines)}</ul>
</section>

<section>
  <h2>5단계 펀더멘털 분석</h2>
  <table>{fund_rows}</table>
</section>

<div class="disclaimer">
  본 리포트는 정보 제공용이며 투자 자문이 아닙니다. 지표·백분위수는 자동 계산,
  사이클·밸류에이션 판단은 사람의 해석이 필요합니다. 데이터 출처: Yahoo Finance.
</div>
</body></html>"""
