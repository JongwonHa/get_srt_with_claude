# SRT 로그인 정보
SRT_ID = "SRT회원번호"           # 회원번호 입력
SRT_PW = "로그인비밀번호"           # 비밀번호 입력


# 예매 정보
DEPARTURE = "수서"            # 출발역
ARRIVAL = "부산"              # 도착역
DATE = "20260201"             # 날짜 (YYYYMMDD)
TIME = "08"                   # 출발 시간 (00~23, 2자리)

# ⭐ 특정 열차 번호 (최대 5개, 비워두면 전체 열차 대상)
# 예: ["301", "303", "305"]
TARGET_TRAINS = ["317", "319"]

# 옵션
SEAT_TYPE = "일반실"          # "일반실" 또는 "특실"
ONLY_RESERVED = False         # True: 예약만 / False: 예약대기도 허용

# 새로고침 간격 (초)
REFRESH_INTERVAL = 0.5
