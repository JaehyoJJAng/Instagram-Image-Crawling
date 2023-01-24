from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from config.config import get_instagram_infos
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from typing import Dict,Union
import requests as rq
import sys
import datetime
import time
import os

class ChromeDriver:
    @staticmethod
    def set_driver():
        # options 객체
        chrome_options = Options()

        # headless Chrome 선언
        # chrome_options.add_argument('--headless')

        # 브라우저 꺼짐 방지
        chrome_options.add_experimental_option('detach', True)

        # 불필요한 에러메시지 없애기
        chrome_options.add_experimental_option(
            'excludeSwitches', ['enable-logging'])

        browser = webdriver.Chrome(
            ChromeDriverManager().install(), chrome_options=chrome_options)
        browser.maximize_window()
        return browser

class Instagram:
    def __init__(self) -> None:
        # Target User ID
        self.target_user_id : str = self.input_user_id()

        # Base Instagram URL
        self.insta_url: str = 'https://www.instagram.com/'

        # Instagram Login Infos
        self._insta_secrets: Dict[str, str] = get_instagram_infos(key='infos')

        # Web Driver Instance
        self.browser = ChromeDriver().set_driver()

    def run(self)-> None:
        # 인스타그램 로그인
        self.insta_login()

        # 상대방 인스타그램 주소로 URL 재지정
        URL: str = self.insta_url + self.target_user_id
        
        # 사용자 인스타그램으로 브라우저 이동
        self.browser.get(url=URL)
        
        # 첫번째 게시글 클릭하기
        self.get_first_content()

        count = 1 
        while True:
            print(f'{count} 번째 게시글 이미지 추출 시작 ..')

            # 다음 이미지로 넘어가기
            self.click_next_image()

            # 다음 게시글로 넘어가기
            loop_check : int = self.click_next_content()

            if loop_check == 0:
                break
            else:
                # Count 변수 증감 시키기
                count += 1

    def insta_login(self)-> None:
        """ 인스타그램 로그인 메소드 """
        # 로그인 성공 시 까지 아이디 돌리기
        self.browser.get(url=self.insta_url)
        self.browser.implicitly_wait(time_to_wait=10)

        _ID: str = self._insta_secrets['id']
        _PW: str = self._insta_secrets['pw']

        # 아이디 입력
        try:
            self.browser.find_elements(By.CSS_SELECTOR, 'input._aa4b._add6._ac4d')[
                0].send_keys(_ID)
            time.sleep(1.0)
        except:
            print("아이디 입력에 실패하였습니다!")
            sys.exit()

        # 패스워드 입력
        try:
            self.browser.find_elements(By.CSS_SELECTOR, 'input._aa4b._add6._ac4d')[1].send_keys(_PW)
            time.sleep(1.0)                
        except:
            print("패스워드 입력에 실패하였습니다!")
            sys.exit()

        # 로그인 클릭
        self.browser.find_element(By.CSS_SELECTOR,'button._acan._acap._acas._aj1-').click()
        
        # 잠시 대기
        time.sleep(1.5)

        # 만약 로그인 중 에러 메시지 뜨는 경우
        exit_flag : bool = True
        try:
            err_ch = self.browser.find_element(By.CSS_SELECTOR,'p#slfErrorAlert')
            if err_ch :
                print('아이디나 패스워드에 문제가 있습니다\n')
                exit_flag : bool = False
        except:
            # 에러메시지가 뜨지 않고 정상적으로 넘어가는 경우
            print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} - 로그인 성공!")
            time.sleep(5.0)
        
        # 로그인 에러에 대한 처리
        if exit_flag == False:
            os.system('cls')
            sys.exit()
            
        # 로그인 정보 알람창이 뜨는 경우
        try:
            self.browser.find_element(By.CSS_SELECTOR,'button._acan._acao._acas._aj1-').click()
            time.sleep(3)
        except:
            pass        
        
        # 브라우저 로딩대기
        try:
            WebDriverWait(self.browser, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'article._ab6k._ab6m._aggc._aatb._aatc._aate._aatf._aati')))
        except:
            print('게시글 목록을 불러올 수 없었습니다!')
            sys.exit()

    def download_image(self)-> None:
        """ 사진 다운로드 """
        try :
            # 이미지 태그
            img_src = self.browser.find_element(By.CSS_SELECTOR,'div._aatk._aatl img').get_attribute('src')

            # 파일 저장 경로 지정
            savePath : str = os.path.abspath(f'인스타그램_{self.target_user_id}')
            if not os.path.exists(savePath):
                os.mkdir(savePath)
            
            # 파일이름 정의
            fileName : str = os.path.join(savePath,img_src.split('?')[0].split('/v/')[-1].split('/')[-1])
            
            # 추출 이미지 태그를 jpg 파일로 다운로드
            try :
                with rq.get(url=img_src) as resp:
                    with open(fileName,'wb') as fp:
                        img = resp.content
                        fp.write(img)
                        print(f'파일 저장 성공! - {fileName}\n')
            except :
                print(f'파일 저장 실패! - {fileName}\n')
        except Exception as e:
            print(f'이미지 파일이 아닌 것 같습니다 아래 오류를 확인해보세요\n{e}\n')
            pass
    
    def get_first_content(self)-> None:
        """ 첫번째 게시글 가져오기 """
        # 첫 게시글 태그 클릭
        first_content  = self.browser.find_element(By.CSS_SELECTOR,'div._aagu').click()
        time.sleep(2.0)

    def click_next_image(self)-> None:
        """ 게시글의 다음(Next) 이미지 클릭 """
        while True:
            try:
                # 이미지 다운로드
                self.download_image()

                self.browser.find_element(By.CSS_SELECTOR,'button._afxw').click()
                time.sleep(4.0)
            except:
                print('사진이 더 이상 없습니다!\n')
                break

    def click_next_content(self)-> Union[None,int]:
        """ 다음 게시글 넘어가기 """
        try :
            self.browser.find_element(By.CSS_SELECTOR,'div._aaqg._aaqh > button').click()
            time.sleep(2.5)
        except:
            print('다음 게시글이 없습니다!')
            return 0
        
    def input_user_id(self) -> str:
        """ Target 유저 ID 입력 """
        while True:
            user_id: str = input('User ID를 입력하세요\n:')
            if not user_id:
                print("ID를 입력하셔야 합니다!")
                continue
            return user_id

def main()-> None:
    # Instagram Instance
    insta = Instagram()

    # Execute Instagram Program
    insta.run()


if __name__ == '__main__':
    main()
