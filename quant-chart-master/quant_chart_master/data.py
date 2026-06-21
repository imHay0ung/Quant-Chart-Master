"""
data.py
───────
데이터 수집 계층. '검색 로직 범위 내에서만 돈다'는 요구를 이렇게 해석했다:
  - 외부 유료 API 없이, yfinance(무료·무키)로 끌어올 수 있는 만큼만.
  - 네트워크가 막히거나 티커가 잘못되면 조용히 죽지 말고 명확히 알린다.

핵심 설계: fetch_ohlcv 하나가 '가능한 한 긴 역사'를 가져온다.
백분위수를 2000년 이후로 계산하려면 과거 전체가 필요하기 때문.
"""
from __future__ import annotations
import pandas as pd


def fetch_ohlcv(ticker: str, start: str = "2000-01-01", end: str | None = None) -> pd.DataFrame:
    """
    Download daily OHLCV from Yahoo Finance.
    Returns a clean DataFrame indexed by date with columns:
    Open, High, Low, Close, Volume.
    Raises a clear error if nothing comes back (bad ticker or no network).
    """
    import yfinance as yf

    df = yf.download(
        ticker, start=start, end=end,
        auto_adjust=True, progress=False, multi_level_index=False,
    )
    if df is None or df.empty:
        raise RuntimeError(
            f"'{ticker}' 데이터를 가져오지 못했습니다. "
            f"티커명 또는 네트워크 연결을 확인하세요."
        )
    df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()
    df.index = pd.to_datetime(df.index)
    return df


def fetch_macro_prices() -> dict[str, pd.DataFrame]:
    """
    Fetch *price-based* macro context — no API key needed.
    These four cover 80% of what matters for a chip-cycle read:
      ^TNX  : 10-Year Treasury Yield  (금리 — 밸류에이션 할인율)
      ^VIX  : Volatility Index        (공포 — 레짐 판단)
      DX-Y.NYB : US Dollar Index      (달러 — 수출/유동성)
      CL=F  : Crude Oil               (인플레 대용)
    Returns {name: DataFrame}. Skips any that fail rather than crashing.
    """
    import yfinance as yf

    tickers = {
        "10Y_Yield": "^TNX",
        "VIX": "^VIX",
        "Dollar": "DX-Y.NYB",
        "Oil": "CL=F",
    }
    out: dict[str, pd.DataFrame] = {}
    for name, t in tickers.items():
        try:
            d = yf.download(t, start="2000-01-01", auto_adjust=True,
                            progress=False, multi_level_index=False)
            if d is not None and not d.empty:
                out[name] = d
        except Exception:
            pass  # 하나 실패해도 나머지는 계속
    return out
