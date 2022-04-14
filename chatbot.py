import asyncio
import time

import requests
import json
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from yinglish import chs2yin
from graia.ariadne.model import Member
from graia.ariadne.message.element import Plain, At, Image

class Chatbot:
    def __init__(self):
        self.session = None
        self.yinglish = False
        self.yinglevel = 0.5

    def chat(self, message: MessageChain):
        msg = str(message.get(Plain))[13:-3]
        msgcopy = msg
        if set(msgcopy) == set(" ") or len(msgcopy) == 0:
            return "@我干嘛？"
        msg = msg[1:]
        if "可以涩涩" in msg:
            if msg[:4] == "可以涩涩":
                self.yinglish = True
                command = msg.split()
                if len(command) == 2:
                    try:
                        level = float(command[1])
                        self.yinglevel = level
                    except:
                        return "涩涩指令格式：可以涩涩 <淫乱度 选填 0~1小数>"
                return "调教成功"
        if msg == "不可以涩涩":
            self.yinglish = False
            return "似乎恢复理智了呢"
        if msg == "涩涩状态":
            return ''.join([str(self.yinglish), str(self.yinglevel)])
        sess = requests.get(
            ('http://api.qingyunke.com/api.php?key=free&appid=0&msg=' + msg))
        js = sess.text
        js = json.loads(js)
        if js['result'] == 0:
            res = js['content']
            res = res.replace("菲菲","RBQ")
            res = res.replace("双字菲", "RBQ")
        else:
            return "被玩坏了啦，请联系管理"
        if self.yinglish:
            return chs2yin(res, self.yinglevel)
        else:
            return res

