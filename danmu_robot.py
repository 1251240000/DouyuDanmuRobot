from sender import *
from crawler import *
from tuling import *

""" 设置 HEAD_CODE 后将仅回复以 HEAD_CODE 为开始的弹幕
若需要可改为其他字符，如‘ #’、‘>’、甚至 ‘@弹幕姬’
若需要不受限制的回复所有信息，将其设置为空（需将自己加入黑名单！）
"""
HEAD_CODE = '#'

""" 加入黑名单的用户将不会进行回复 
"""
BLACKLIST = ['Ag4nzo']

""" 设置 REPLY_RATE 以配置弹幕回复速率
因弹幕发送功能由selenium实现，而斗鱼规定每条弹幕需间隔一秒发送（实际发送速率设置为1.2秒）
但仍然可以通过多个sender实例（需要多个手机验证过的账户）同时处理消息队列来加快回复速率
"""
REPLY_RATE = 1


class DouyuDanmuRobot():
    def __init__(self, room_id):
        self.crawler = DouyuDanmuCrawler(room_id)
        self.sender = DouyuDanmuSender(room_id)
    
    def start_reply(self):
        while True:
            msg = self.crawler.get_chatmsg()
            if msg:
                if msg['txt'][:len(HEAD_CODE)] == HEAD_CODE and msg['nn'] not in BLACKLIST:
                    res = Tuling.converse(msg['txt'])
                    self.sender.push_message(res)
            time.sleep(REPLY_RATE)

if __name__ == '__main__':
    rid = input("输入房间号以部署弹幕机器人：")
    robot = DouyuDanmuRobot(rid)
    robot.start_reply()
