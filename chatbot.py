import requests
import json
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from yinglish import chs2yin


class Chatbot:
    def __init__(self):
        self.yinglish = False
        self.yinglevel = 0.5

    def chat(self, message: MessageChain):
        msg = str(message.get(Plain))[13:-3]
        msgcopy = msg
        if set(msgcopy) == set(" ") or len(msgcopy) == 0:
            return "@我干嘛？"
        msg = msg[1:]
        if msg == "可以涩涩":
            self.yinglish = True
            command = msg.split()
            if len(command) == 2:
                try:
                    level = float(command[1])
                    self.yinglevel = level
                except:
                    return "涩涩指令格式：可以涩涩 <淫乱度 选填 0~1小数>"
        if msg == "不可以涩涩":
            self.yinglish = False
        sess = requests.get(
            ('https://open.drea.cc/bbsapi/chat/get?keyWord=' + msg + '&userName=type%3Dbbs'))
        js = sess.text
        js = json.loads(js)
        if js['isSuccess']:
            res = js['data']['reply']
        else:
            res = "被玩坏了啦，请联系管理"
        if self.yinglish:
            return chs2yin(res, self.yinglevel)
        else:
            return res