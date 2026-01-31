from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import time
import re

class SRT:
    def __init__(self, debug=False):
        """브라우저 초기화"""
        self.debug = debug
        
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 10)
        
        self.LOGIN_URL = "https://etk.srail.kr/cmc/01/selectLoginForm.do"
        self.SEARCH_URL = "https://etk.srail.kr/hpg/hra/01/selectScheduleList.do"
        
        self.target_trains = []
    
    def set_target_trains(self, train_numbers):
        """예매할 열차 번호 설정 (최대 5개)"""
        if train_numbers:
            self.target_trains = [str(t).strip() for t in train_numbers[:5]]
            print(f"🎯 타겟 열차: {', '.join(self.target_trains)}")
        else:
            self.target_trains = []
            print("🎯 타겟 열차: 전체")
    
    def is_target_train(self, train_no):
        """해당 열차가 타겟인지 확인"""
        if not self.target_trains:
            return True
        
        # 열차 번호에서 숫자만 추출
        train_no_clean = ''.join(filter(str.isdigit, str(train_no)))
        
        for target in self.target_trains:
            target_clean = ''.join(filter(str.isdigit, str(target)))
            if target_clean and target_clean in train_no_clean:
                return True
        
        return False
    
    def extract_train_number(self, text):
        """텍스트에서 열차 번호 추출"""
        # "SRT 317" 또는 "317" 패턴 찾기
        match = re.search(r'(\d{3,4})', text)
        if match:
            return match.group(1)
        return None
    
    def login(self, srt_id, srt_pw):
        """SRT 로그인"""
        print("🔐 로그인 시도 중...")
        self.driver.get(self.LOGIN_URL)
        time.sleep(1)
        
        self.driver.find_element(By.ID, "srchDvNm01").clear()
        self.driver.find_element(By.ID, "srchDvNm01").send_keys(srt_id)
        self.driver.find_element(By.ID, "hmpgPwdCphd01").clear()
        self.driver.find_element(By.ID, "hmpgPwdCphd01").send_keys(srt_pw)
        
        self.driver.find_element(By.XPATH, "//input[@value='로그인']").click()
        time.sleep(2)
        
        if "selectLoginForm" in self.driver.current_url:
            raise Exception("❌ 로그인 실패! 회원번호와 비밀번호를 확인하세요.")
        
        print("✅ 로그인 성공!")
        return True
    
    def search_train(self, departure, arrival, date, time_str):
        """열차 조회"""
        print(f"🔍 열차 조회: {departure} → {arrival} ({date} {time_str}시 이후)")
        
        self.driver.get(self.SEARCH_URL)
        time.sleep(1)
        
        dep_input = self.driver.find_element(By.ID, "dptRsStnCdNm")
        dep_input.clear()
        dep_input.send_keys(departure)
        
        arr_input = self.driver.find_element(By.ID, "arvRsStnCdNm")
        arr_input.clear()
        arr_input.send_keys(arrival)
        
        self.driver.execute_script(f"document.getElementById('dptDt').value = '{date}'")
        self.driver.execute_script(f"document.getElementById('dptTm').value = '{time_str}0000'")
        
        self.driver.find_element(By.XPATH, "//input[@value='조회하기']").click()
        time.sleep(2)
        
        print("✅ 조회 완료!")
        return True
    
    def refresh_train_list(self):
        """열차 목록 새로고침"""
        try:
            search_btn = self.driver.find_element(By.XPATH, "//input[@value='조회하기']")
            search_btn.click()
        except:
            self.driver.refresh()
        time.sleep(1.5)
    
    def debug_table_structure(self):
        """디버깅: 테이블 구조 출력"""
        print("\n🔧 [DEBUG] 테이블 구조 분석:")
        try:
            rows = self.driver.find_elements(By.CSS_SELECTOR, "table.list_table_inner tbody tr, #result-form tbody tr, .tbl_wrap tbody tr")
            print(f"   발견된 행 수: {len(rows)}")
            
            if rows:
                first_row = rows[0]
                tds = first_row.find_elements(By.TAG_NAME, "td")
                print(f"   첫 번째 행의 td 수: {len(tds)}")
                for i, td in enumerate(tds):
                    text = td.text.replace('\n', ' ').strip()[:30]
                    print(f"   td[{i}]: {text}")
        except Exception as e:
            print(f"   디버그 오류: {e}")
        print()
    
    def check_and_reserve(self, seat_type="일반실", only_reserved=False):
        """예약 가능한 좌석 확인 및 예약 시도"""
        try:
            # 디버그 모드면 테이블 구조 출력
            if self.debug:
                self.debug_table_structure()
            
            # 여러 가능한 셀렉터 시도
            rows = self.driver.find_elements(By.CSS_SELECTOR, "tr.ct_list_pop")
            
            if not rows:
                rows = self.driver.find_elements(By.CSS_SELECTOR, "#result-form tbody tr")
            
            if not rows:
                rows = self.driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
            
            if not rows:
                print("   ⚠️ 열차 목록을 찾을 수 없습니다.")
                return False
            
            found_target = False
            
            for idx, row in enumerate(rows):
                try:
                    # 전체 행 텍스트에서 열차 번호 추출
                    row_text = row.text
                    train_number = self.extract_train_number(row_text)
                    
                    if not train_number:
                        continue
                    
                    # 타겟 열차인지 확인
                    if not self.is_target_train(train_number):
                        continue
                    
                    found_target = True
                    
                    # 시간 추출 (HH:MM 패턴)
                    time_match = re.search(r'(\d{2}:\d{2})', row_text)
                    dep_time = time_match.group(1) if time_match else "?"
                    
                    # 예약하기/예약대기 버튼 찾기
                    buttons = row.find_elements(By.TAG_NAME, "a")
                    
                    for btn in buttons:
                        btn_text = btn.text.strip()
                        btn_class = btn.get_attribute("class") or ""
                        btn_onclick = btn.get_attribute("onclick") or ""
                        
                        # 일반실/특실 구분
                        is_general = "일반" in btn_text or "gnr" in btn_onclick.lower()
                        is_special = "특" in btn_text or "spc" in btn_onclick.lower()
                        
                        # 좌석 타입 필터링
                        if seat_type == "특실" and is_general and not is_special:
                            continue
                        if seat_type == "일반실" and is_special and not is_general:
                            continue
                        
                        # 예약 가능 확인
                        if "예약하기" in btn_text:
                            print(f"   🎉 [SRT {train_number}] {dep_time} - 예약 가능!")
                            btn.click()
                            time.sleep(1)
                            return True
                        
                        # 예약대기 확인
                        if "예약대기" in btn_text and not only_reserved:
                            print(f"   ⏳ [SRT {train_number}] {dep_time} - 예약대기 신청!")
                            btn.click()
                            time.sleep(1)
                            return True
                    
                    # 매진 상태 표시
                    if "매진" in row_text:
                        print(f"   ❌ [SRT {train_number}] {dep_time} - 매진")
                    else:
                        print(f"   ⏸️ [SRT {train_number}] {dep_time} - 확인 중...")
                        
                except Exception as e:
                    if self.debug:
                        print(f"   [DEBUG] 행 처리 오류: {e}")
                    continue
            
            if not found_target:
                print(f"   ⚠️ 타겟 열차({', '.join(self.target_trains)})를 찾을 수 없습니다.")
            
            return False
            
        except Exception as e:
            print(f"   ⚠️ 오류: {e}")
            return False
    
    def run(self, srt_id, srt_pw, departure, arrival, date, time_str, 
            seat_type="일반실", only_reserved=False, refresh_interval=0.5,
            target_trains=None):
        """자동 예매 실행"""
        
        self.set_target_trains(target_trains)
        self.login(srt_id, srt_pw)
        self.search_train(departure, arrival, date, time_str)
        
        attempt = 0
        while True:
            attempt += 1
            print(f"\n{'='*50}")
            print(f"🔄 시도 #{attempt} | 타겟: {self.target_trains if self.target_trains else '전체'}")
            print(f"{'='*50}")
            
            if self.check_and_reserve(seat_type, only_reserved):
                print("\n" + "🎊"*20)
                print("예매 성공! 결제를 진행하세요!")
                print("🎊"*20)
                input("\n엔터를 누르면 종료합니다...")
                break
            
            print(f"\n⏳ {refresh_interval}초 후 재시도...")
            time.sleep(refresh_interval)
            
            self.refresh_train_list()
    
    def close(self):
        """브라우저 종료"""
        self.driver.quit()
