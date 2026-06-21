"""
quant_chart_master
──────────────────
티커·날짜만 넣으면 기술적 분석 한 페이지 리포트를 뽑는 파이프라인.

기본 사용:
    from quant_chart_master import analyze
    analyze("SOXX", "2026-06-18")              # 차트 이미지 없음 → 정식 분석만
    analyze("SOXX", "2026-06-18",
            timeframes={"weekly": w, "daily": d})  # 멀티 타임프레임 상호작용 포함
"""
from __future__ import annotations
import pandas as pd

from . import data, analysis, charts, report

__all__ = ["analyze"]


# 5단계 분석 칸 — 코드가 자동으로 못 채우는(채워서도 안 되는) 부분은
# 빈 문자열로 두면 리포트에 '수동 입력 필요'로 표시된다.
_FUNDAMENTAL_TEMPLATE = {
    "1. 매크로 환경": "",
    "2. 산업/섹터": "",
    "3. 기업 본질": "",
    "4. 밸류에이션": "",
    "5. 종합 판단": "",
}


def _macro_lines() -> list[str]:
    """가격성 매크로를 yfinance로 끌어와 현재값 + 백분위수로 요약."""
    lines: list[str] = []
    try:
        macro = data.fetch_macro_prices()
    except Exception:
        return ["매크로 데이터 로드 실패 (네트워크 확인)"]
    for name, df in macro.items():
        s = df["Close"].dropna()
        if s.empty:
            continue
        pct = (s < s.iloc[-1]).mean() * 100
        lines.append(f"{name}: {s.iloc[-1]:.2f} (역사적 {pct:.0f}백분위수)")
    return lines or ["매크로 가격 데이터 없음"]


def analyze(
    ticker: str,
    date: str | None = None,
    timeframes: dict[str, pd.DataFrame] | None = None,
    fundamental_notes: dict[str, str] | None = None,
    out_path: str | None = None,
) -> str:
    """
    Run the full pipeline and write an HTML report.

    Parameters
    ----------
    ticker : 분석 대상 (예: "SOXX")
    date   : 기준일 'YYYY-MM-DD'. None이면 최신.
    timeframes : {"weekly": df, "daily": df, ...} 주어지면 타임프레임 상호작용 분석 수행.
                 (= '차트 이미지 추가 첨부 시'에 해당하는 데이터 입력 경로)
    fundamental_notes : 5단계 텍스트. None이면 빈 템플릿(수동 입력 표시).
    out_path : 저장 경로. None이면 './{ticker}_{date}.html'.

    Returns 저장된 파일 경로.
    """
    df = data.fetch_ohlcv(ticker, end=date)
    if date:  # 기준일까지만 잘라서 그 시점 분석 재현
        df = df[df.index <= pd.to_datetime(date)]

    snap = analysis.snapshot(df)
    signals = analysis.build_signals(df)
    chart_html = charts.build_chart(df, ticker)
    macro = _macro_lines()

    tf_notes = None
    if timeframes:
        frames = {k: analysis.snapshot(v) for k, v in timeframes.items()}
        tf_notes = analysis.timeframe_interaction(frames)

    funds = fundamental_notes or dict(_FUNDAMENTAL_TEMPLATE)

    html = report.build_report(
        ticker=ticker, snap=snap, signals=signals, chart_html=chart_html,
        macro_lines=macro, fundamental_notes=funds, timeframe_notes=tf_notes,
    )

    out_path = out_path or f"./{ticker}_{snap['date']}.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    return out_path
