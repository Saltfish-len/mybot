import asyncio
import time
from enum import Enum
import random

from Pinyin2Hanzi import DefaultHmmParams, DefaultDagParams
from Pinyin2Hanzi import viterbi, dag
from Pinyin2Hanzi import is_pinyin, simplify_pinyin

hmmparams = DefaultHmmParams()
dagparams = DefaultDagParams()

import requests
import json
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from yinglish import chs2yin
from graia.ariadne.model import Member, MemberInfo
from graia.ariadne.message.element import Plain, At, Image


class Role(Enum):
    deadman = 0
    villager = 1
    werewolf = 2
    prophet = 3


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
        try:
            sess = requests.get(
                ('http://api.qingyunke.com/api.php?key=free&appid=0&msg=' + msg))
            js = sess.text
            js = json.loads(js)
            res = js['content']
            res = res.replace("菲菲", "RBQ")
            res = res.replace("双字菲", "RBQ")
        except:
            res = "被玩坏了啦，请联系管理"
        if self.yinglish:
            return chs2yin(res, self.yinglevel)
        else:
            return res

    def pinyin2hanzi(self, msg):
        for i, one_pinyin in enumerate(msg):
            msg[i] = simplify_pinyin(one_pinyin)
            if not is_pinyin(msg[i]):
                return False
        result = dag(dagparams, msg, path_num=2)
        return "".join(result[0].path) + "\n或者：" + "".join(result[1].path)


class Wmh:
    # Werewolves of Miller's Hollow:
    def __init__(self):
        self.canactionlist = []
        self.originalrole = None
        self.app = None
        self.group = None
        self.role_list = None
        self.player_list = []
        self.player_number = 0
        self.stage = 0  # 天黑0天亮1
        self.ingame = False
        self.killlist = []
        self.votelist = []

    def endgame(self):
        self.__init__()

    async def whowin(self):
        rolelist = self.role_list
        rolelist = set(rolelist)
        if Role.werewolf not in rolelist:
            await self.app.sendMessage(self.group, MessageChain.create("平民胜利！！！"))
        elif Role.prophet not in rolelist and Role.villager not in rolelist:
            await self.app.sendMessage(self.group, MessageChain.create("狼人胜利~"))
        else:
            return
        temp = ["玩家编号|名称"]
        for i, player in enumerate(self.player_list):
            temp.append("角色：" + str(self.originalrole[i].name) + " | " + str(player.name))
        await self.app.sendMessage(self.group, MessageChain.create("\n".join(temp)))
        self.endgame()

    def isingame(self):
        if self.ingame:
            return MessageChain.create("游戏进行中")
        else:
            return MessageChain.create("游戏未开始")

    def joingame(self, player: Member):
        if player not in self.player_list:
            self.player_list.append(player)
            self.player_number += 1

    def refresh_player_in_game(self) -> str:
        temp = ["玩家编号|名称"]
        for i, player in enumerate(self.player_list):
            if self.role_list[i] != Role.deadman:
                temp.append("ID：" + str(i + 1) + " | " + str(player.name))
        return "\n".join(temp) + "\n"

    def startgame(self) -> (MessageChain,):
        self.ingame = True
        roles = self.assign_roles()
        res = self.refresh_player_in_game()
        groupmsg = MessageChain.create(res)
        for player in self.player_list:
            groupmsg += MessageChain.create(At(player))
        msg = MessageChain.create(res)
        return groupmsg, msg, roles

    def assign_roles(self) -> [Member, MessageChain]:
        roles_table = [(Role.werewolf,), (Role.prophet, Role.werewolf),
                       (Role.villager, Role.prophet, Role.werewolf),
                       (Role.villager, Role.villager, Role.werewolf, Role.prophet),
                       (Role.villager, Role.villager, Role.werewolf, Role.werewolf, Role.prophet),
                       (Role.villager, Role.villager, Role.villager, Role.werewolf, Role.werewolf, Role.prophet),
                       (Role.villager, Role.villager, Role.villager, Role.werewolf, Role.werewolf, Role.werewolf,
                        Role.prophet)]
        self.role_list = list(roles_table[self.player_number - 1])
        self.originalrole = self.role_list
        random.shuffle(self.role_list)
        temp = []
        for i, player in enumerate(self.player_list):
            if self.role_list[i] != Role.deadman:
                temp.append([player, MessageChain.create("你的身份是：" + str(self.role_list[i].name))])
            if self.role_list[i] != Role.deadman and self.role_list[i] != Role.villager:
                self.canactionlist.append(player.id)
        return temp

    def night(self) -> [Member, MessageChain]:
        self.canactionlist = []
        for i, player in enumerate(self.player_list):
            if self.role_list[i] != Role.deadman and self.role_list[i] != Role.villager:
                self.canactionlist.append(player.id)
        self.stage = 0
        fmsg = []
        wolfmsg = MessageChain.create("你是狼人，请输入“/狼人杀 杀人”来投票杀人\n本局的狼人玩家：\n")
        for i, role in enumerate(self.role_list):
            if role == Role.werewolf:
                wolfmsg += MessageChain.create("ID：" + str(i + 1) + " | " + str(self.player_list[i].name), "\n")
        for i, role in enumerate(self.role_list):
            if role == Role.werewolf:
                fmsg.append([self.player_list[i], wolfmsg])
        pmsg = []
        prophertmsg = MessageChain.create("你是预言家，请输入“/狼人杀 预言”来预言")
        for i, role in enumerate(self.role_list):
            if role == Role.prophet:
                pmsg.append([self.player_list[i], prophertmsg])
        return fmsg, pmsg

    async def isnightfinish(self):
        wolfcount = self.role_list.count(Role.werewolf) + self.role_list.count(Role.prophet)
        if len(self.killlist) == wolfcount:
            temp = []
            for id in self.killlist:
                if id != 0:
                    temp.append(id)
            if len(temp) == 0:
                await self.app.sendMessage(self.group, MessageChain.create("昨晚无事发生~"))
                self.killlist = []
                await self.whowin()
                return
            killedid = max(temp, key=temp.count)
            self.role_list[killedid - 1] = Role.deadman
            msg = MessageChain.create("ID:" + str(killedid), At(self.player_list[killedid - 1]), "没了")
            await self.app.sendMessage(self.group, MessageChain.create("天亮啦\n") + msg)
            res = self.refresh_player_in_game()
            await self.app.sendMessage(self.group, MessageChain.create(res))
            self.stage = 1
            self.killlist = []
        await self.whowin()

    async def isvotefinish(self):
        votecount = len(self.votelist)
        if len(self.role_list) - self.role_list.count(Role.deadman) == votecount:
            temp = []
            for id in self.votelist:
                if id != 0:
                    temp.append(id)
            if len(temp) == 0:
                await self.app.sendMessage(self.group, MessageChain.create("今天无事发生~"))
                self.votelist = []
                await self.whowin()
                return
            votedid = max(temp, key=temp.count)
            self.role_list[votedid - 1] = Role.deadman
            msg = MessageChain.create("ID:" + str(votedid), At(self.player_list[votedid - 1]), "被票走了，请说遗言")
            await self.app.sendMessage(self.group, msg)
            res = self.refresh_player_in_game()
            await self.app.sendMessage(self.group, MessageChain.create(res))
            self.votelist = []
        await self.whowin()

    def canact(self, member):
        if member.id in self.canactionlist:
            self.canactionlist.remove(member.id)
            return True
        else:
            return False
