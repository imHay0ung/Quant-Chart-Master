"""
analysis.py
───────────
지표(숫자)를 신호(해석)로 바꾸는 계층.
중요한 철학: 여기서 코드는 '관찰 사실'만 말한다. ("RSI 다이버전스 발생")
'매수해라' 같은 결정은 절대 자동화하지 않는다 — 그건 사람 몫.
당신 원칙 그대로: 알고리즘은 모니터링, 결정은 인간.
"""
from __future__ import annotations
import pandas as pd
from . import indicators as ind


def snapshot(df: pd.DataFrame) -> dict:
    """
    Build a one-day technical snapshot with historical percentiles.
    Every percentile is computed against the FULL history loaded
    (so '2000년 이후 백분위수' holds as long as data starts in 2000).
    """
    e = ind.add_all(df)
    last = e.iloc[-1]

    def pct(col):
        return ind.historical_percentile(e[col])

    return {
        "date": str(e.index[-1].date()),
        "close": float(last["Close"]),
        "volume": float(last["Volume"]),
        "rsi": float(last["RSI"]),
        "rsi_pctile": pct("RSI"),
        "macd_hist": float(last["MACD_hist"]),
        "cmf": float(last["CMF"]),
        "cmf_pctile": pct("CMF"),
        "dist_200ma_pct": float(last["dist_200ma_pct"]),
        "dist_200ma_pctile": pct("dist_200ma_pct"),
        "sma_stack_bullish": bool(last["SMA20"] > last["SMA50"] > last["SMA200"]),
        "above_200ma": bool(last["Close"] > last["SMA200"]),
    }


def detect_divergence(df: pd.DataFrame, lookback: int = 20) -> str | None:
    """
    Bearish RSI divergence: price makes a higher high but RSI makes a lower high.
    A classic late-stage warning — the move continues but its 'engine power' fades.
    Returns a human-readable string or None.
    """
    e = ind.add_all(df).dropna(subset=["RSI"])
    if len(e) < lookback * 2:
        return None
    recent, prior = e.iloc[-lookback:], e.iloc[-lookback * 2:-lookback]
    price_hh = recent["Close"].max() > prior["Close"].max()
    rsi_lh = recent["RSI"].max() < prior["RSI"].max()
    if price_hh and rsi_lh:
        return ("베어리시 RSI 다이버전스: 가격은 신고가인데 RSI는 더 낮은 고점 "
                "→ 상승 동력 약화 신호")
    return None


def build_signals(df: pd.DataFrame) -> list[str]:
    """Collect plain-language observations. Facts, not advice."""
    snap = snapshot(df)
    sigs: list[str] = []

    sigs.append(
        f"추세: 이평선 {'정배열(20>50>200)' if snap['sma_stack_bullish'] else '정배열 아님'}, "
        f"200일선 {'위' if snap['above_200ma'] else '아래'}"
    )
    sigs.append(
        f"200일선 이격: {snap['dist_200ma_pct']:+.1f}% "
        f"(역사적 {snap['dist_200ma_pctile']:.0f}백분위수)"
    )
    sigs.append(
        f"RSI: {snap['rsi']:.1f} (역사적 {snap['rsi_pctile']:.0f}백분위수)"
    )
    sigs.append(
        f"CMF: {snap['cmf']:+.3f} "
        f"({'자금 유입' if snap['cmf'] > 0 else '자금 유출'}, "
        f"{snap['cmf_pctile']:.0f}백분위수)"
    )
    sigs.append(
        f"MACD 히스토그램: {snap['macd_hist']:+.3f} "
        f"({'상승 모멘텀' if snap['macd_hist'] > 0 else '하락 모멘텀'})"
    )
    div = detect_divergence(df)
    if div:
        sigs.append("⚠️ " + div)
    if snap["dist_200ma_pctile"] >= 95:
        sigs.append("⚠️ 200일선 이격이 역사적 극단(95백분위 이상) — 평균 회귀 압력")
    return sigs


# ─────────────────────────────────────────────────────────────
# 멀티 타임프레임 상호작용 — 차트 이미지 첨부 시 채워지는 골격
# ─────────────────────────────────────────────────────────────
def timeframe_interaction(frames: dict[str, dict]) -> list[str]:
    """
    Compare snapshots across timeframes (e.g. weekly vs daily vs 4H vs 1H).
    `frames` = {"weekly": snapshot_dict, "daily": ..., ...}

    설계 의도: 이미지를 직접 읽진 못하지만, 사용자가 각 타임프레임의
    수치(또는 별도 데이터)를 넣어주면 '상위는 과열인데 하위는 강세' 같은
    충돌/정렬을 자동으로 짚어준다. 이미지 없으면 이 함수는 호출되지 않는다.
    """
    notes: list[str] = []
    order = ["weekly", "daily", "4h", "2h", "1h"]
    present = [f for f in order if f in frames]
    if len(present) < 2:
        return ["타임프레임이 2개 미만 — 상호작용 분석 생략"]

    higher, lower = present[0], present[-1]
    h, l = frames[higher], frames[lower]

    def safe(v, d=0.0):  # NaN/None → 기본값 (짧은 프레임의 200MA 백분위 보호)
        return d if v is None or v != v else v

    # 상위 타임프레임 과열 + 하위 강세 = 전형적 후반부 충돌
    if safe(h.get("dist_200ma_pctile")) >= 90 and safe(l.get("rsi")) > 60:
        notes.append(
            f"{higher} 과열(200MA {h['dist_200ma_pctile']:.0f}백분위) vs "
            f"{lower} 강세(RSI {l['rsi']:.0f}) → 단기 상승 여력 < 중장기 하락 리스크"
        )
    # 모든 타임프레임 RSI 정렬 확인
    rsis = {f: frames[f].get("rsi") for f in present if frames[f].get("rsi")}
    if rsis and all(v > 50 for v in rsis.values()):
        notes.append("전 타임프레임 RSI>50 → 다중 시간대 모멘텀 정렬(강세 일관)")
    return notes or ["타임프레임 간 뚜렷한 충돌/정렬 신호 없음"]
