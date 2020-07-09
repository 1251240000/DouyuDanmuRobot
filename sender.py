import threading
import platform
import pickle
import time
import sys
import os

from selenium import webdriver

PAGE_LOAD_DELAY = 3.0
DANMU_SEND_INTERVAL = 1.2

class DouyuDanmuSender():
    def __init__(self, room_id):
        self.__url = 'https://www.douyu.com/' + room_id + '/'
        self.__driver_path = sys.path[0] + '/driver/chromedriver.exe' if 'Windows' in platform.system() else sys.path[0] + '/driver/chromedriver'
        
        self.__options = webdriver.ChromeOptions()
       	self.__options.add_argument('--headless')
        self.__options.add_argument('log-level=2')
        self.__options.add_argument('--disable-gpu')
        self.__options.add_argument('blink-settings=imagesEnabled=false')

        self.__send_queue = []
        
        self.__login()
        self.__start_sending()
    
    def __login(self):
        self.__driver = webdriver.Chrome(executable_path = self.__driver_path, options = self.__options)
        self.__driver.get(self.__url)
        self.__load_cookies()
        
        error_count = 1
        while True:
            try:
                self.__driver.find_element_by_class_name("UserInfo-link")
                break
            except Exception as e:
                error_count += 1
                time.sleep(PAGE_LOAD_DELAY)
                if error_count > 5:
                    print("登录失败，请尝试手动登录。错误：",e)
                    self.__make_cookies()
                    self.__load_cookies()
                    error_count = 1
        
        js = '''
            document.getElementsByClassName("Header")[0].remove();
            document.getElementsByClassName("layout-Aside")[0].remove();
            document.getElementById("js-room-activity").remove();
            document.getElementsByClassName("layout-Menu")[0].remove();
            document.getElementsByClassName("layout-Bottom")[0].remove();
            document.getElementsByClassName("layout-Player-guessgame")[0].remove();
            document.getElementsByClassName("layout-Player-toolbar")[0].remove();

            intervalID = setInterval(function (){
                if(document.getElementsByClassName("SuperFansGuideTips")[0]){document.getElementsByClassName("SuperFansGuideTips")[0].remove();};
                if(document.getElementsByClassName("theWholePK-guildIknow")[0]){document.getElementsByClassName("theWholePK-guildIknow")[0].click();};
                var reg_pause = /(pause-[0-9a-f]{6})/;
                var reg_danmu = /(showdanmu-[0-9a-f]{6})/;
                var player = document.getElementById("room-html5-player").innerHTML;
                player = player.replace(reg_pause, function($0, $1) {document.getElementsByClassName($1)[0].click();});
                player = player.replace(reg_danmu, function($0, $1) {document.getElementsByClassName($1)[0].click();});
            }, 5000);

            '''

        try:
            self.__driver.execute_script(js)
        except Exception as e:
            print("JS执行错误：", e)
    
    def __load_cookies(self):
        if os.path.exists(sys.path[0] + "/cookie/cookies.pkl"):
            with open(sys.path[0] + "/cookie/cookies.pkl", "rb") as cookiefile:
                cookies = pickle.load(cookiefile)
            for cookie in cookies:
                self.__driver.add_cookie(cookie)
            self.__driver.refresh()
        else:
            print("未检测到cookie，请手动登录。")
            self.__make_cookies()
            self.__load_cookies()
    
    def __make_cookies(self):
        manual_driver =  webdriver.Chrome(executable_path = self.__driver_path)
        manual_driver.get(self.__url)
        time.sleep(PAGE_LOAD_DELAY)
        manual_driver.find_element_by_class_name("UnLogin").click()
        
        while True:
            try:
                manual_driver.find_element_by_class_name("UserInfo-link")
                break
            except:
                time.sleep(PAGE_LOAD_DELAY)
        cookies = manual_driver.get_cookies()
        if not os.path.exists("cookie"):
            os.mkdir("cookie")
        pickle.dump(cookies, open(sys.path[0] + "/cookie/cookies.pkl", "wb"))

        manual_driver.quit()

    def __send(self):
        while self.__keep_sending:
            try:
                if self.__send_queue:
                    message = self.__send_queue.pop(0)
                    send_js = '''
                    document.getElementsByClassName("ChatSend-txt")[0].value = "%s";
                    document.getElementsByClassName("ChatSend-button")[0].click();
                    '''%message
                    try:
                        self.__driver.execute_script(send_js)
                    except Exception as e:
                        print("弹幕发送错误:", e)
					
                time.sleep(DANMU_SEND_INTERVAL)

            except BaseException as e:
                print("弹幕发送异常，错误:",e)
        
    def __start_sending(self):
        self.__keep_sending = True
        threading.Thread(target=self.__send).start()


    def reset_room_id(self, room_id):
        self.__driver.quit()
        self.__url = 'https://www.douyu.com/' + room_id + '/'

        self.__login()
        self.__start_sending()

    def push_message(self, message):
        self.__send_queue.append(message)
    
    def kill(self):
        self.__keep_sending = False
        self.__driver.quit()
        
        
if __name__ == '__main__':
    rid = input("输入房间号以发送弹幕：")
    douyu_sender = DouyuDanmuSender(rid)
    text = input("输入弹幕内容，或输入q退出：\n> ")

    while text != 'q':
        text and douyu_sender.push_message(text)
        text = input('> ')
    douyu_sender.kill()
