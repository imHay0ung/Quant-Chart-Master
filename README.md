# Quant Chart Master

티커와 날짜만 넣으면 **기술적 분석 한 페이지 리포트**를 자동 생성하는 파이프라인.
캔들·이동평균·MACD·RSI·CMF·거래량·갭을 계산하고, **2000년 이후 역사적 백분위수**와
인터랙티브 Plotly 차트, 가격성 매크로 컨텍스트를 하나의 HTML로 묶는다.

```python
from quant_chart_master import analyze
analyze("SOXX", date="2026-06-18")   # → SOXX_2026-06-18.html
```

---

## 설계 철학 — 알고리즘 모니터링

이 도구는 **매수/매도를 추천하지 않는다.** 코드는 "관찰 사실"만!
(예: *"RSI 베어리시 다이버전스 발생", "200일선 +60% 이격 = 98백분위수"*).

---

## 지금 수준에서 실제로 어디까지 되나? 앞으로의 계획

| 기능 | 상태 | 방법 | API 키 |
|---|:---:|---|:---:|
| OHLCV 가격 | ✅ 완전 | yfinance | 불필요 |
| RSI·MACD·CMF·볼린저·이평선·갭 | ✅ 완전 | 직접 계산 (공식 고정) | 불필요 |
| **2000년 이후 백분위수** | ✅ 완전 | 과거 전체 데이터로 계산 | 불필요 |
| Plotly 인터랙티브 차트 (4단) | ✅ 완전 | plotly | 불필요 |
| 매크로 가격성 (금리·VIX·달러·유가) | ✅ 완전 | yfinance | 불필요 |
| 멀티 타임프레임 상호작용 | ✅ 데이터 주입 시 | `timeframes=` 인자 | 불필요 |
| 매크로 경제지표 (CPI·GDP·실업률) | ⚠️ 미구현 | FRED API 연동 예정 | 무료 키 |
| P/E 등 밸류에이션 역사 백분위 | ⚠️ 부분 | yfinance 현재값만 안정적 | 불필요 |
| 5단계 펀더멘털 *판단* | ✋ 수동 | 사람이 텍스트 입력 | — |

**한 줄 요약:** 차트 기술분석 + 백분위수 + 가격성 매크로는 **키 없이 100% 자동화**된다.
경제지표(FRED)와 펀더멘털 판단만 이후 단계 / 수동으로.

### 매크로는 다 API로 끌어와야 하나?
아니다. 의사결정에 중요한 **금리·VIX·달러·유가는 yfinance로 키 없이** 끌어온다(80% 커버).
진짜 경제지표(CPI·GDP)만 FRED 무료 키가 필요, 추가 예정

---

## 설치

```bash
pip install -r requirements.txt
python example.py
```

> 컨테이너/사내망 환경에서는 Yahoo Finance 도메인이 막혀 있을 수 있다.
> 그 경우 `data.fetch_ohlcv`가 명확한 에러를 던지니 네트워크 설정을 확인하라.

---

## 멀티 타임프레임 분석 (선택)

차트 이미지를 코드가 직접 읽진 못한다. 대신 **각 타임프레임의 OHLCV를 주입**하면
상위 타임프레임 과열 vs 하위 강세 같은 충돌/정렬을 자동으로 짚는다.

```python
from quant_chart_master import analyze, data

daily  = data.fetch_ohlcv("SOXX", end="2026-06-18")
weekly = daily.resample("W").agg(
    {"Open":"first","High":"max","Low":"min","Close":"last","Volume":"sum"}
).dropna()

analyze("SOXX", date="2026-06-18", timeframes={"weekly": weekly, "daily": daily})
```

---

## 구조

```
quant_chart_master/
├── data.py         # yfinance 수집 (가격 + 가격성 매크로)
├── indicators.py   # 순수 함수: RSI/MACD/CMF/BB/SMA/갭/백분위수
├── analysis.py     # 지표 → 신호(관찰 사실) + 타임프레임 상호작용
├── charts.py       # Plotly 4단 인터랙티브 차트
├── report.py       # 한 페이지 HTML 리포트 조립
└── __init__.py     # analyze() 진입점
```

각 지표 함수에는 영문 docstring을 달아 영어 학습 자료로도 쓸 수 있게 했다.

---

## 로드맵

- [ ] FRED 연동 (CPI·GDP·실업률 + 백분위수)
- [ ] 밸류에이션 역사 백분위 (P/E·EV/EBITDA) 안정화
- [ ] GitHub Actions로 매일 자동 리포트 → GitHub Pages 게시
- [ ] 한국 시장(KRX) 티커 지원
- [ ] 지표 단위 테스트(pytest) 추가

---

## ⚠️ 면책

정보 제공 및 학습 목적이며 **투자 자문이 아니다.** 모든 투자 책임은 본인에게 있다.
데이터 출처: Yahoo Finance.

<img width="884" height="1204" alt="image" src="https://github.com/user-attachments/assets/c0731b70-a8ee-4c81-b823-d535eddd6514" />

