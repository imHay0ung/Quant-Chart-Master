"""
indicators.py
─────────────
순수 함수만 모음. 입력은 OHLCV DataFrame, 출력은 지표 Series.
'순수 함수'로 짠 이유: 데이터 출처(yfinance든 CSV든)와 무관하게
공식만 검증되면 영원히 신뢰할 수 있기 때문. 테스트하기도 쉽다.

각 지표는 영문 한 줄 설명(docstring)을 달아 영어 학습도 겸함.
"""
from __future__ import annotations
import pandas as pd
import numpy as np


def sma(s: pd.Series, period: int) -> pd.Series:
    """Simple Moving Average: the average closing price over `period` bars."""
    return s.rolling(period).mean()


def ema(s: pd.Series, period: int) -> pd.Series:
    """Exponential Moving Average: a moving average that weights recent prices more."""
    return s.ewm(span=period, adjust=False).mean()


def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    """
    Relative Strength Index (Wilder's smoothing).
    Measures the speed of price changes on a 0-100 scale.
    Above 70 = overbought, below 30 = oversold (rules of thumb, not laws).
    """
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def macd(close: pd.Series, fast: int = 12, slow: int = 26, sig: int = 9):
    """
    Moving Average Convergence Divergence.
    Returns (macd_line, signal_line, histogram).
    macd_line crossing above signal_line = bullish momentum shift.
    """
    macd_line = ema(close, fast) - ema(close, slow)
    signal_line = macd_line.ewm(span=sig, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def bollinger(close: pd.Series, period: int = 20, k: float = 2.0):
    """
    Bollinger Bands. Returns (upper, middle, lower).
    Bands widen when volatility rises and squeeze when it falls.
    """
    mid = sma(close, period)
    std = close.rolling(period).std()
    return mid + k * std, mid, mid - k * std


def cmf(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """
    Chaikin Money Flow.
    Combines price location within the bar AND volume to gauge buying/selling pressure.
    Positive = accumulation (buyers winning), negative = distribution (sellers winning).
    """
    hl = (df["High"] - df["Low"]).replace(0, np.nan)
    mfm = ((df["Close"] - df["Low"]) - (df["High"] - df["Close"])) / hl
    mfv = mfm * df["Volume"]
    return mfv.rolling(period).sum() / df["Volume"].rolling(period).sum()


def detect_gaps(df: pd.DataFrame, min_pct: float = 1.0) -> pd.DataFrame:
    """
    Detect price gaps: today's open vs yesterday's close beyond `min_pct`.
    Gaps often act as support/resistance and signal strong overnight sentiment.
    """
    prev_close = df["Close"].shift(1)
    gap_pct = (df["Open"] - prev_close) / prev_close * 100
    gaps = df[abs(gap_pct) >= min_pct].copy()
    gaps["gap_pct"] = gap_pct[abs(gap_pct) >= min_pct]
    gaps["direction"] = np.where(gaps["gap_pct"] > 0, "up", "down")
    return gaps[["gap_pct", "direction"]]


def historical_percentile(series: pd.Series, current: float | None = None) -> float:
    """
    Where does the current value sit within its own history? (0-100).
    e.g. 95 means 'higher than 95% of all past readings' = historically extreme.
    This is the engine behind the '2000년 이후 백분위수' requirement.
    """
    s = series.dropna()
    if s.empty:
        return float("nan")  # 데이터 부족(예: 짧은 타임프레임의 200MA) → NaN
    if current is None:
        current = s.iloc[-1]
    return float((s < current).mean() * 100)


def add_all(df: pd.DataFrame) -> pd.DataFrame:
    """Attach every indicator as new columns. One call, full picture."""
    out = df.copy()
    out["SMA20"] = sma(df["Close"], 20)
    out["SMA50"] = sma(df["Close"], 50)
    out["SMA200"] = sma(df["Close"], 200)
    out["RSI"] = rsi(df["Close"])
    out["MACD"], out["MACD_signal"], out["MACD_hist"] = macd(df["Close"])
    out["BB_up"], out["BB_mid"], out["BB_low"] = bollinger(df["Close"])
    out["CMF"] = cmf(df)
    out["dist_200ma_pct"] = (df["Close"] / out["SMA200"] - 1) * 100
    return out
