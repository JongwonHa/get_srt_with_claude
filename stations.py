# SRT 역 코드
STATION_CODE = {
    "수서": "0551",
    "동탄": "0552",
    "평택지제": "0553",
    "천안아산": "0502",
    "오송": "0297",
    "대전": "0010",
    "김천구미": "0507",
    "동대구": "0015",
    "신경주": "0508",
    "울산(통도사)": "0509",
    "부산": "0020",
    "공주": "0514",
    "익산": "0030",
    "정읍": "0033",
    "광주송정": "0036",
    "나주": "0037",
    "목포": "0041",
}

def get_station_code(station_name):
    """역 이름으로 코드 반환"""
    if station_name in STATION_CODE:
        return STATION_CODE[station_name]
    raise ValueError(f"'{station_name}' 역을 찾을 수 없습니다.")
