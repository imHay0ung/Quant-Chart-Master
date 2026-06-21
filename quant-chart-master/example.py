"""
example.py — 가장 단순한 사용 예시.
실행: python example.py
(인터넷 연결 필요 — yfinance가 Yahoo Finance에서 데이터를 끌어옴)
"""
from quant_chart_master import analyze

# ── 기본: 차트 이미지/타임프레임 없음 → 정식 단일 분석만 ──────────────
path = analyze("SOXX", date="2026-06-18")
print(f"리포트 생성됨: {path}")
print("브라우저로 열어보세요.")


# ── 응용: 멀티 타임프레임 상호작용까지 (데이터로 주입) ────────────────
# '차트 이미지 첨부 시 타임프레임 분석'에 해당하는 데이터 경로.
# 각 타임프레임의 OHLCV DataFrame을 직접 만들어 넘기면 상호작용을 분석한다.
#
# from quant_chart_master import data
# daily  = data.fetch_ohlcv("SOXX", end="2026-06-18")
# weekly = daily.resample("W").agg(
#     {"Open":"first","High":"max","Low":"min","Close":"last","Volume":"sum"}
# ).dropna()
# analyze("SOXX", date="2026-06-18",
#         timeframes={"weekly": weekly, "daily": daily})


# ── 응용: 5단계 펀더멘털 텍스트를 사람이 채워 넣기 ─────────────────────
# notes = {
#     "1. 매크로 환경": "AI capex 사이클 후반, 금리 안정, VIX 저변동...",
#     "2. 산업/섹터":   "반도체 YTD +90%, 메모리/CPU로 리더십 확산...",
#     "3. 기업 본질":   "ETF이므로 구성종목 가중 분석으로 대체...",
#     "4. 밸류에이션":  "후행 P/E 70배대 = 2000년 이후 상단...",
#     "5. 종합 판단":   "추세 강세 but 진입 위치 극단 → 신규 Hold/Reduce",
# }
# analyze("SOXX", date="2026-06-18", fundamental_notes=notes)
