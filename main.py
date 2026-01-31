from srt import SRT
from config import (
    SRT_ID, SRT_PW, 
    DEPARTURE, ARRIVAL, DATE, TIME,
    SEAT_TYPE, ONLY_RESERVED, REFRESH_INTERVAL,
    TARGET_TRAINS
)

def main():
    print("="*50)
    print("🚄 SRT 자동 예매 프로그램")
    print("="*50)
    print(f"📍 {DEPARTURE} → {ARRIVAL}")
    print(f"📅 {DATE} {TIME}시 이후")
    print(f"💺 {SEAT_TYPE}")
    print(f"🎯 타겟 열차: {TARGET_TRAINS if TARGET_TRAINS else '전체'}")
    print("="*50 + "\n")
    
    # 🔧 디버그 모드: True로 바꾸면 테이블 구조 출력
    DEBUG_MODE = True
    
    srt = SRT(debug=DEBUG_MODE)
    
    try:
        srt.run(
            srt_id=SRT_ID,
            srt_pw=SRT_PW,
            departure=DEPARTURE,
            arrival=ARRIVAL,
            date=DATE,
            time_str=TIME,
            seat_type=SEAT_TYPE,
            only_reserved=ONLY_RESERVED,
            refresh_interval=REFRESH_INTERVAL,
            target_trains=TARGET_TRAINS
        )
    except KeyboardInterrupt:
        print("\n\n⚠️ 사용자가 중단했습니다.")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
    finally:
        input("\n아무 키나 누르면 브라우저가 닫힙니다...")
        srt.close()

if __name__ == "__main__":
    main()
