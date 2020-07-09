from collections import deque
import threading
import websocket
import pystt
import time

class DouyuDanmuCrawler():
    def __init__(self, room_id):
        self.__room_id = room_id
        self.__start_crawling()

        self.chatmsg_queue = deque(maxlen=1000)
        self.uenter_queue = deque(maxlen=1000)
        self.gift_queue = deque(maxlen=1000)
    
    def __get_message_type(self, obj):
        if obj.get('type') == 'chatmsg':
            return obj, 'chatmsg'
        elif obj.get('type') == 'uenter':
            return obj, 'uenter'
        elif obj.get('type') == 'dgb':
            return obj, 'gift'
        elif obj.get('type') in ['rss', 'loginres', 'wiru', 'rankup', 'actfsts1od_r', 'frank',
                                'rri', 'svsnres', 'newblackres', 'fire_user', 'fire_start',
                                'tsboxb', 'ghz2019arkcalc', 'ghz2019s1info', 'ghz2019s2info', 'fire_real_user',
                                'gbroadcast', 'srres', 'spbc', 'ghz2019s2calc', 'upgrade', 'rquizisn',
                                'anbc', 'wirt', 'ghz2019s1disp', 'blab', 'cthn', 'rnewbc', 'pingreq',
                                'noble_num_info', 'rank_change', 'mrkl', 'synexp', 'fswrank', 'ranklist', 'qausrespond']:
            return None, "ignore"
        return None, None

    def __message_encode(self, obj):
        content = pystt.dumps(obj)
        content_byte = bytes(content.encode('utf-8'))
        content_length = len(content_byte) + 8 + 1
        length_byte = int.to_bytes(content_length, length=4, byteorder='little')
        
        magic = bytearray([0xb1, 0x02])
        zero_byte = bytearray([0x00])
        return length_byte + length_byte + magic + zero_byte + zero_byte + content_byte + zero_byte

    def __message_decode(self, message):
        pos = 0
        infos = [ ]
        while pos < len(message):
            content_length = int.from_bytes(message[pos: pos + 4], byteorder='little')
            content = message[pos + 12: pos + 4 + content_length - 1].decode(encoding='utf-8', errors='ignore')
            obj = pystt.loads(content)
            infos.append(self.__get_message_type(obj))
            pos += (4 + content_length)
        return infos

    def __on_message(self, message):
        try:
            for [info, mtype] in self.__message_decode(message):
                if info:
                    if mtype == 'chatmsg':
                        self.chatmsg_queue.append(info)
                    elif mtype == 'uenter':
                        self.uenter_queue.append(info)
                    elif mtype == 'gift':
                        self.gift_queue.append(info)
        except Exception as e:
            print("弹幕信息解包错误：", e, "信息：", message)

    def __on_open(self):
        loginreq = {
            'type': 'loginreq',
            'room_id': self.__room_id,
            'dfl': 'sn@A=105@Sss@A=1',
            'username': 'dhchen',
            'uid': '897038',
            'ver': '20190610',
            'aver': '218101901',
            'ct': '0'
        }
        
        joinreq = {
            'type': 'joingroup',
            'rid': self.__room_id,
            'gid': '-9999'
        }

        self.__ws.send(self.__message_encode(loginreq))
        self.__ws.send(self.__message_encode(joinreq))

    def __crawl(self):
        self.__ws = websocket.WebSocketApp("wss://danmuproxy.douyu.com:8503/", on_message=self.__on_message, on_open=self.__on_open)
        self.__ws.run_forever()
    
    def __keepalive(self):
        binary = self.__message_encode({'type':'mrkl'})
        try:
            self.__ws.send(binary)
            self.__timer_keepalive = threading.Timer(45, self.__keepalive)
            self.__timer_keepalive.start()
        except Exception as e:
            print('心跳包发送错误:', e)

    def __start_crawling(self):
        threading.Thread(target=self.__crawl).start()
        self.__timer_keepalive = threading.Timer(45, self.__keepalive)
        self.__timer_keepalive.start()

    def reset_room_id(self,room_id):
        self.kill()
        self.__room_id = room_id
        self.__start_crawling()

    def kill(self):
        self.chatmsg_queue.clear()
        self.uenter_queue.clear()
        self.gift_queue.clear()
        self.__ws.keep_running = False
        self.__timer_keepalive.cancel()

        
    def get_chatmsg(self):
        return self.chatmsg_queue.popleft() if self.chatmsg_queue else None

    '''
    def get_uenter(self):
        return self.uenter_queue.popleft() if self.uenter_queue else None
    
    def get_gift(self):
        return self.gift_queue.popleft() if self.gift_queue else None
    '''


if __name__ == '__main__':
    rid = input("输入房间号以爬取弹幕：")
    douyu_crawler = DouyuDanmuCrawler(rid)

    while True:
        msg = douyu_crawler.get_chatmsg()
        msg and print(msg['nn'], ':', msg['txt'])
        time.sleep(0.1)

    douyu_crawler.kill()