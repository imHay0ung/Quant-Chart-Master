"""
charts.py
─────────
Plotly로 4단 인터랙티브 차트를 그린다:
  1) 캔들 + 이평선 + 볼린저밴드
  2) 거래량
  3) RSI
  4) MACD
정적 PNG 대신 Plotly를 쓴 이유: 깃허브 Pages에 올려 줌·호버되는
한 페이지로 보기 위함. 출력은 HTML div 문자열 → 보고서에 그대로 삽입.
"""
from __future__ import annotations
import pandas as pd
from . import indicators as ind


def build_chart(df: pd.DataFrame, ticker: str, tail: int = 250) -> str:
    """Return an interactive Plotly chart as an embeddable HTML div string."""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    e = ind.add_all(df).tail(tail)

    fig = make_subplots(
        rows=4, cols=1, shared_xaxes=True,
        row_heights=[0.5, 0.15, 0.175, 0.175], vertical_spacing=0.03,
        subplot_titles=(f"{ticker} — 가격/이평선/볼린저", "거래량", "RSI", "MACD"),
    )

    # 1) Candles + MAs + Bollinger
    fig.add_trace(go.Candlestick(
        x=e.index, open=e["Open"], high=e["High"], low=e["Low"], close=e["Close"],
        name="OHLC"), row=1, col=1)
    for ma, color in [("SMA20", "#f59e0b"), ("SMA50", "#3b82f6"), ("SMA200", "#ef4444")]:
        fig.add_trace(go.Scatter(x=e.index, y=e[ma], name=ma,
                                 line=dict(width=1, color=color)), row=1, col=1)
    fig.add_trace(go.Scatter(x=e.index, y=e["BB_up"], name="BB upper",
                             line=dict(width=0.5, color="gray"), showlegend=False), row=1, col=1)
    fig.add_trace(go.Scatter(x=e.index, y=e["BB_low"], name="BB lower",
                             line=dict(width=0.5, color="gray"), fill="tonexty",
                             fillcolor="rgba(128,128,128,0.08)", showlegend=False), row=1, col=1)

    # 2) Volume
    fig.add_trace(go.Bar(x=e.index, y=e["Volume"], name="Volume",
                         marker_color="#94a3b8"), row=2, col=1)

    # 3) RSI
    fig.add_trace(go.Scatter(x=e.index, y=e["RSI"], name="RSI",
                             line=dict(color="#8b5cf6")), row=3, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.4, row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.4, row=3, col=1)

    # 4) MACD
    fig.add_trace(go.Bar(x=e.index, y=e["MACD_hist"], name="Histogram",
                         marker_color="#cbd5e1"), row=4, col=1)
    fig.add_trace(go.Scatter(x=e.index, y=e["MACD"], name="MACD",
                             line=dict(color="#2563eb")), row=4, col=1)
    fig.add_trace(go.Scatter(x=e.index, y=e["MACD_signal"], name="Signal",
                             line=dict(color="#f97316")), row=4, col=1)

    fig.update_layout(
        template="plotly_white", height=900,
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", y=1.02, x=0),
        margin=dict(l=40, r=20, t=60, b=20),
    )
    return fig.to_html(full_html=False, include_plotlyjs="cdn")
