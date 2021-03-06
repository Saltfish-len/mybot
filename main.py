import asyncio
import time

import requests, json
from graia.ariadne import get_running
from graia.ariadne.adapter import Adapter
from graia.ariadne.event.message import GroupMessage, FriendMessage, TempMessage
from graia.ariadne.event.mirai import NudgeEvent
from graia.broadcast import Broadcast, Force

from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, At, Image
from graia.ariadne.message.parser.base import MentionMe, DetectPrefix, ContainKeyword, DetectSuffix
from graia.ariadne.model import Friend, Group, MiraiSession, Member, MemberInfo, MemberPerm
from graia.scheduler.timers import crontabify

import mychatbot as ct

import random

from graia.broadcast.interrupt import InterruptControl, Waiter

from graia.scheduler import timers
from graia.scheduler.saya import SchedulerSchema, GraiaSchedulerBehaviour

from graia.scheduler import GraiaScheduler

import re

import battlefield

loop = asyncio.new_event_loop()

try:
    with open('config.json', 'r') as f:
        config = json.load(f)
    host = config["host"]
    verifykey = config["verifykey"]
    account = config["account"]
except IOError:
    with open('config.json', 'w') as f:
        json.dump({"host": "http://localhost:8080", "verifykey": "XXXX", "account": 114514}, f)
    print(
        "Fail to load config, config file has been created.\nPlease modify config.json and restart.\nPress enter to exit.")
    input()
    import sys

    sys.exit()

broadcast = Broadcast(loop=loop)
app = Ariadne(
    broadcast=broadcast,
    connect_info=MiraiSession(
        host=host,  # 填入 HTTP API 服务运行的地址
        verify_key=verifykey,  # 填入 verifyKey
        account=account,  # 你的机器人的 qq 号
    )
)

session = battlefield.get_session()
gameids = [7151023600512, 7176779910897, ]  # 1服，2服
serverids = []
for id in gameids:
    time.sleep(1)
    serverid = battlefield.get_serverId(session, id)
    if serverid:
        serverids.append(serverid)
        print(f"服务器https://battlefieldtracker.com/bf1/servers/pc/{id}初始化成功")
    else:
        print(f"服务器https://battlefieldtracker.com/bf1/servers/pc/{id}初始化失败！！！！")
bcc = app.broadcast
app.count = 0

bot = ct.Chatbot()

setucold = dict()

inc = InterruptControl(bcc)


# 狼人杀
# game = ct.Wmh()


# @bcc.receiver(TempMessage, decorators=[DetectPrefix("/狼人杀"), DetectSuffix("杀人")])
# async def tempmsgforwmh(app: Ariadne, player: Member, message: MessageChain = DetectPrefix("/狼人杀")):
#     if game.stage == 1:
#         await app.sendMessage(player, MessageChain.create("光天化日之下不能杀人"))
#         return
#     if not game.canact(player):
#         await app.sendMessage(player, MessageChain.create("你不能这样操作哦~"))
#         return
#     await app.sendMessage(player, MessageChain.create("请直接输入id，如“1”"))
#
#     @Waiter.create_using_function([TempMessage])
#     async def wolf_waiter(p: Member, m: MessageChain):
#         # 判断和处理
#         if p == player:
#             msg = str(m.get(Plain))[13:-3]
#             try:
#                 targetid = int(msg)
#                 return targetid  # 只要不是 None 就会继续执行
#             except:
#                 return Force(None)
#
#     try:
#         res = await inc.wait(wolf_waiter, timeout=30)
#         game.killlist.append(res)
#         await app.sendMessage(
#             player,
#             MessageChain.create("投票成功：" + str(res))
#         )
#     except asyncio.TimeoutError:
#         await app.sendMessage(
#             player,
#             MessageChain.create("超时，默认弃票")
#         )
#         game.killlist.append(0)
#     finally:
#         await game.isnightfinish()
#
#
# @bcc.receiver(FriendMessage, decorators=[DetectPrefix("/狼人杀"), DetectSuffix("杀人")])
# async def tempmsgforwmh(app: Ariadne, player: Friend, message: MessageChain = DetectPrefix("/狼人杀")):
#     if game.stage == 1:
#         await app.sendMessage(player, MessageChain.create("光天化日之下不能杀人"))
#         return
#     if not game.canact(player):
#         await app.sendMessage(player, MessageChain.create("你不能这样操作哦~"))
#         return
#     await app.sendMessage(player, MessageChain.create("请直接输入id，如“1”"))
#
#     @Waiter.create_using_function([FriendMessage])
#     async def wolf_waiter(p: Friend, m: MessageChain):
#         # 判断和处理
#         if p == player:
#             msg = str(m.get(Plain))[13:-3]
#             try:
#                 targetid = int(msg)
#                 return targetid  # 只要不是 None 就会继续执行
#             except:
#                 return Force(None)
#
#     try:
#         res = await inc.wait(wolf_waiter, timeout=30)
#         game.killlist.append(res)
#         await app.sendMessage(
#             player,
#             MessageChain.create("投票成功：" + str(res))
#         )
#     except asyncio.TimeoutError:
#         await app.sendMessage(
#             player,
#             MessageChain.create("超时，默认弃票")
#         )
#         game.killlist.append(0)
#     finally:
#         await game.isnightfinish()
#
#
# @bcc.receiver(TempMessage, decorators=[DetectPrefix("/狼人杀"), DetectSuffix("预言")])
# async def tempmsgforwmh(app: Ariadne, player: Member, message: MessageChain = DetectPrefix("/狼人杀")):
#     if game.stage == 1:
#         await app.sendMessage(player, MessageChain.create("光天化日之下不能预言"))
#         return
#     if not game.canact(player):
#         await app.sendMessage(player, MessageChain.create("你不能这样操作哦~"))
#         return
#     await app.sendMessage(player, MessageChain.create("请直接输入id，如“1”"))
#
#     @Waiter.create_using_function([FriendMessage])
#     async def prophet_waiter(p: Friend, m: MessageChain):
#         # 判断和处理
#         if p == player:
#             msg = str(m.get(Plain))[13:-3]
#             try:
#                 targetid = int(msg)
#
#                 return targetid  # 只要不是 None 就会继续执行
#             except:
#                 return Force(None)
#
#     try:
#         res = await inc.wait(prophet_waiter, timeout=30)
#         if res == 0:
#             await app.sendMessage(
#                 player,
#                 MessageChain.create("放弃预言啦")
#             )
#             game.killlist.append(0)
#             return
#         await app.sendMessage(
#             player,
#             MessageChain.create("他是身份是：" + str(game.role_list[res - 1].name))
#         )
#         game.killlist.append(0)
#     except asyncio.TimeoutError:
#         await app.sendMessage(
#             player,
#             MessageChain.create("超时，默认弃票")
#         )
#         game.killlist.append(0)
#     finally:
#         await game.isnightfinish()
#
#
# @bcc.receiver(FriendMessage, decorators=[DetectPrefix("/狼人杀"), DetectSuffix("预言")])
# async def tempmsgforwmh(app: Ariadne, player: Friend, message: MessageChain = DetectPrefix("/狼人杀")):
#     if game.stage == 1:
#         await app.sendMessage(player, MessageChain.create("光天化日之下不能预言"))
#         return
#     if not game.canact(player):
#         await app.sendMessage(player, MessageChain.create("你不能这样操作哦~"))
#         return
#     await app.sendMessage(player, MessageChain.create("请直接输入id，如“1”"))
#
#     @Waiter.create_using_function([FriendMessage])
#     async def prophet_waiter(p: Friend, m: MessageChain):
#         # 判断和处理
#         if p == player:
#             msg = str(m.get(Plain))[13:-3]
#             try:
#                 targetid = int(msg)
#                 return targetid  # 只要不是 None 就会继续执行
#             except:
#                 return Force(None)
#
#     try:
#         res = await inc.wait(prophet_waiter, timeout=30)
#         if res == 0:
#             await app.sendMessage(
#                 player,
#                 MessageChain.create("放弃预言啦")
#             )
#             game.killlist.append(0)
#             return
#         await app.sendMessage(
#             player,
#             MessageChain.create("他是身份是：" + str(game.role_list[res - 1].name))
#         )
#         game.killlist.append(0)
#     except asyncio.TimeoutError:
#         await app.sendMessage(
#             player,
#             MessageChain.create("超时，默认弃票")
#         )
#         game.killlist.append(0)
#     finally:
#         await game.isnightfinish()


@bcc.receiver(GroupMessage)
async def py2ch(app: Ariadne, group: Group, member: Member, message: MessageChain):
    msg = str(message.get(Plain))[13:-3]
    testmgs = msg
    testmgs = testmgs.replace(" ", "")
    test = re.compile(u'[\u4e00-\u9fa5]')
    if testmgs.isalpha() and test.search(testmgs) is None:
        msg = msg.lower()
        try:
            res = bot.pinyin2hanzi(msg.split(" "))
            if res:
                await app.sendMessage(
                    group,
                    MessageChain.create("他说：" + res),
                )
        except:
            return


# @bcc.receiver(
#     GroupMessage,
#     decorators=[DetectPrefix("/狼人杀")]
# )
# async def langrensha(app: Ariadne, group: Group, member: Member,
#                      message: MessageChain = DetectPrefix("/狼人杀")):
#     command = str(message.get(Plain))[13:-3]
#     if "新游戏" in command:
#         game.app = app
#         game.group = group
#         if game.ingame:
#             await app.sendMessage(
#                 group,
#                 game.isingame(),
#             )
#             return
#         else:
#             game.ingame = True
#             await app.sendMessage(
#                 group,
#                 MessageChain.create("开始游戏\n请发送：\n\"/狼人杀 加入\"\n加入游戏"),
#             )
#     if "加入" in command:
#         if not game.ingame:
#             await app.sendMessage(
#                 group,
#                 MessageChain.create(At(member), "\n未创建新游戏"),
#             )
#             return
#         try:
#             if member in game.player_list:
#                 await app.sendMessage(
#                     group,
#                     MessageChain.create(At(member), "\n你已经在游戏中了"),
#                 )
#                 return
#             if game.player_number >= 7:
#                 await app.sendMessage(
#                     group,
#                     MessageChain.create(At(member), "\n人已经满啦~"),
#                 )
#                 return
#             game.joingame(member)
#             await app.sendMessage(
#                 group,
#                 MessageChain.create(At(member), "\n加入成功, 当前玩家数:" + str(game.player_number)),
#             )
#         except:
#             await app.sendMessage(
#                 group,
#                 MessageChain.create(At(member), "\n加入失败, 寄"),
#             )
#     if "开始游戏" in command:
#         if game.player_number == 0:
#             await app.sendMessage(
#                 group,
#                 MessageChain.create("输入“/狼人杀 新游戏”来加入游戏")
#             )
#             return
#         gmsg, pmsg, roles = game.startgame()
#         await app.sendMessage(
#             group,
#             gmsg
#         )
#         for player in game.player_list:
#             await app.sendMessage(
#                 player,
#                 pmsg
#             )
#         await app.sendMessage(
#             group,
#             MessageChain.create("正在分配身份……")
#         )
#         # 向玩家发送身份
#         for item in roles:
#             await app.sendTempMessage(
#                 item[0],
#                 item[1]
#             )
#         # 入夜
#         wolf_msg_list, prophet_msg_list = await game.night()
#         for w in wolf_msg_list:
#             await app.sendTempMessage(
#                 w[0],
#                 w[1]
#             )
#         for p in prophet_msg_list:
#             await app.sendTempMessage(
#                 p[0],
#                 p[1]
#             )
#     if "入夜" in command:
#         if game.stage == 0:
#             await app.sendMessage(
#                 group,
#                 MessageChain.create(At(member), "\n已经在晚上啦"),
#             )
#             return
#         wolf_msg_list, prophet_msg_list = await game.night()
#         for w in wolf_msg_list:
#             await app.sendTempMessage(
#                 w[0],
#                 w[1]
#             )
#         for p in prophet_msg_list:
#             await app.sendTempMessage(
#                 p[0],
#                 p[1]
#             )
#     if "结束游戏" in command:
#         if not game.ingame:
#             await app.sendMessage(
#                 group,
#                 MessageChain.create(At(member), "\n未创建新游戏"),
#             )
#             return
#         try:
#             game.endgame()
#             await app.sendMessage(
#                 group,
#                 MessageChain.create("结束成功"),
#             )
#         except:
#             await app.sendMessage(
#                 group,
#                 MessageChain.create("报错了，大寄特寄"),
#             )
#
#
# @bcc.receiver(
#     GroupMessage,
#     decorators=[DetectPrefix("/狼人杀 指认 ")]
# )
# async def zhiren(app: Ariadne, group: Group, member: Member,
#                  message: MessageChain = DetectPrefix("/狼人杀 指认 ")):
#     command = str(message.get(Plain))[13:-3]
#     try:
#         voteid = int(command)
#         game.votelist.append(voteid)
#         await game.isvotefinish()
#     except:
#         await app.sendMessage(group, MessageChain.create(At(member), "注意格式"))


@bcc.receiver(
    GroupMessage,
    decorators=[ContainKeyword(keyword="rbq")]
)
async def rbq(app: Ariadne, group: Group, member: Member, message: MessageChain):
    reslist = ["rbq? 什么rbq?", "rbq?! 有人叫我？", "你刚刚说了rbq是吗，哈哈，没错就是我！", "rbq rbq, 你才是rbq呢！"]
    await app.sendMessage(
        group,
        MessageChain.create(At(member), "\n" + reslist[random.randint(0, len(reslist) - 1)]),
    )


@bcc.receiver(
    GroupMessage,
    decorators=[DetectPrefix("涩图")]
)
async def setu(app: Ariadne, group: Group, member: Member, message: MessageChain = DetectPrefix("涩图")):
    tgroup = tuple(group)
    if tgroup not in setucold:
        setucold[tgroup] = 0
    if time.time() - setucold[tgroup] <= 15:
        reslist = ["才三秒，你就冲完了？", "冲这么快小心牛牛会爆炸哦~", "哼，不给你看~", "你怎么冲的到处都是！", "好烦啊，你怎么又发情了",
                   "再冲这么快小心被雌堕哦~", "机器人都会被你冲坏的", "冲挺快啊 帮我也冲一下", "你冲出来的是可乐吧"]
        await app.sendMessage(
            group,
            MessageChain.create(At(member), "\n" + reslist[random.randint(0, len(reslist) - 1)]),
        )
        return
    await app.sendMessage(
        group,
        MessageChain.create(At(member), "\n少女祈祷中ing"),
    )
    endure = 10
    option = str(message.get(Plain))[13:-3].lstrip()
    try:
        sess = requests.get(
            'https://api.lolicon.app/setu/v2?proxy=i.pixiv.re' + "&r18=0&tag=" + option)
        js = sess.text
        js = json.loads(js)
    except:
        await app.sendMessage(
            group,
            MessageChain.create("呜呜呜找不到涩图"),
        )
        return
    imginfo = "标题: " + js["data"][0]["title"] + "\n" + "pid: " + str(js["data"][0]["pid"]) + "\n作者: " + js["data"][0][
        "author"] + "\nuid: " + str(js["data"][0]["uid"])
    await app.sendMessage(
        group,
        MessageChain.create(imginfo),
    )
    imgurl = js["data"][0]["urls"]["original"]
    setusession = get_running(Adapter).session
    try:
        async with setusession.get(imgurl) as r:
            imgdata = await r.read()
        msg = await app.sendMessage(
            group,
            MessageChain.create(Image(data_bytes=imgdata)),
        )
        setucold[tgroup] = time.time()
        await asyncio.sleep(endure)
        await app.recallMessage(msg)
    except:
        await app.sendMessage(
            group,
            MessageChain.create("图片加载失败qwq"),
        )


@bcc.receiver(
    GroupMessage,
    decorators=[MentionMe()],  # 注意要实例化
)
async def groupchat(app: Ariadne, group: Group, member: Member, messageChain: MessageChain):
    msg = str(messageChain.get(Plain))[13:-3]
    if "@我" in msg or "at我" in msg:
        textlist = [" ?", " ???", " 什么玩意？", " 干嘛？", " 干嘛", " 什么", " 啥"]
        await app.sendMessage(
            group,
            MessageChain.create([At(member), Plain(textlist[random.randint(0, len(textlist) - 1)])]),
        )
    else:
        await app.sendMessage(
            group,
            MessageChain.create(At(member), bot.chat(messageChain)),
        )


@bcc.receiver(NudgeEvent)
async def getup(app: Ariadne, event: NudgeEvent):
    if event.context_type == "group" and event.target == account:
        app.count += 1
        if app.count == 1:
            await app.sendGroupMessage(
                event.group_id,
                MessageChain.create("？")
            )
        elif app.count == 2:
            await app.sendGroupMessage(
                event.group_id,
                MessageChain.create("嗯?")
            )
        elif app.count == 3:
            app.count = 0
            await app.sendGroupMessage(
                event.group_id,
                MessageChain.create("戳尼玛戳，莫挨老子！")
            )

    elif event.context_type == "friend" and event.target == account:
        await app.sendFriendMessage(
            event.friend_id,
            MessageChain.create("别戳我，好痒！")
        )
    else:
        return


@bcc.receiver(
    GroupMessage,
    decorators=[DetectPrefix(".+vip#")]
)
async def add_vip(app: Ariadne, group: Group, member: Member,
                  message: MessageChain = DetectPrefix(".+vip#")):
    if group.id not in (940987081, 792678279):
        return
    if member.permission.name == "Member":
        await app.sendGroupMessage(
            group,
            MessageChain.create(At(member), f"您没有权限呢~")
        )
        return
    msg = str(message.get(Plain))[13:-3].split()
    try:
        server = int(msg[0]) - 1
        msg = msg[1:]
    except:
        await app.sendGroupMessage(
            group,
            MessageChain.create(At(member), f"请输入服务器的数字编号")
        )
        return
    name = msg[0]
    if msg[0] == msg[-1]:
        days = float(365.0)
    else:
        days = float(msg[1])
    res = battlefield.vip_add(session, serverids[server], name, days)
    if res:
        await app.sendGroupMessage(
            group,
            MessageChain.create(At(member),
                                f"成功添加{name},他的vip还有{int(res)}天。\n目标服务器为："
                                f"\nhttps://battlefieldtracker.com/bf1/servers/pc/{gameids[server]}")
        )
    else:
        await app.sendGroupMessage(
            group,
            MessageChain.create(At(member), f"寄了")
        )


@bcc.receiver(
    GroupMessage,
    decorators=[DetectPrefix(".-vip#")]
)
async def remove_vip(app: Ariadne, group: Group, member: Member,
                     message: MessageChain = DetectPrefix(".-vip#")):
    if group.id not in (940987081, 792678279):
        return
    if member.permission.name == "Member":
        await app.sendGroupMessage(
            group,
            MessageChain.create(At(member), f"您没有权限呢~")
        )
        return
    msg = str(message.get(Plain))[13:-3].split()
    try:
        server = int(msg[0]) - 1
        msg = msg[1:]
    except:
        await app.sendGroupMessage(
            group,
            MessageChain.create(At(member), f"请输入服务器的数字编号")
        )
        return
    name = msg[0]
    res = battlefield.vip_remove(session, serverids[server], name)
    if res:
        await app.sendGroupMessage(
            group,
            MessageChain.create(At(member), f"成功移除{name}的vip。\n目标服务器为："
                                            f"\nhttps://battlefieldtracker.com/bf1/servers/pc/{gameids[server]}")
        )
    else:
        await app.sendGroupMessage(
            group,
            MessageChain.create(At(member), f"寄了")
        )


@bcc.receiver(
    GroupMessage,
    decorators=[DetectPrefix(".server#")]
)
async def player_in_server(app: Ariadne, group: Group, member: Member,
                           message: MessageChain = DetectPrefix(".server#")):
    if group.id not in (940987081, 792678279):
        return
    msg = str(message.get(Plain))[13:-3].split()
    try:
        server = int(msg[0]) - 1
    except:
        await app.sendGroupMessage(
            group,
            MessageChain.create(At(member), f"请输入服务器的数字编号")
        )
        return
    res = battlefield.list_player(gameids[server])
    if res:
        map, team_name, player_list = res
        one_player = '\n'.join([str(i + 1) + ": " + name for i, name in enumerate(player_list[0])])
        two_player = '\n'.join(
            [str(i + len(player_list[0] + 1)) + ": " + name for i, name in enumerate(player_list[1])])

        await app.sendGroupMessage(
            group,
            MessageChain.create(At(member), f"\n当前地图为{map}"
                                            f"\n人数为{len(player_list[0]) + len(player_list[1])}\n{team_name[0]}:\n"
                                            f"{one_player}"
                                            f"{team_name[1]}:\n"
                                            f"{two_player}"
                                )
        )


    else:
        await app.sendGroupMessage(
            group,
            MessageChain.create(At(member), f"寄了")
        )


@bcc.receiver(
    GroupMessage,
    decorators=[DetectPrefix(".vip#")]
)
async def list_vip(app: Ariadne, group: Group, member: Member,
                   message: MessageChain = DetectPrefix(".vip#")):
    if group.id not in (940987081, 792678279):
        return
    msg = str(message.get(Plain))[13:-3].split()
    try:
        server = int(msg[0]) - 1

    except:
        await app.sendGroupMessage(
            group,
            MessageChain.create(At(member), f"请输入服务器的数字编号")
        )
        return

    res = battlefield.vip_list(session, serverids[server])
    await app.sendGroupMessage(
        group,
        MessageChain.create(At(member), f"查询服务器："
                                        f"\nhttps://battlefieldtracker.com/bf1/servers/pc/{gameids[server]}\n{res}")
    )


@bcc.receiver(
    GroupMessage,
    decorators=[DetectPrefix(".vipcheck#")]
)
async def check_vip(app: Ariadne, group: Group, member: Member, message: MessageChain = DetectPrefix(".vipcheck#")):
    if group.id not in (940987081, 792678279):
        return
    if member.permission.name == "Member":
        await app.sendGroupMessage(
            group,
            MessageChain.create(At(member), f"您没有权限呢~")
        )
        return
    msg = str(message.get(Plain))[13:-3].split()
    try:
        server = int(msg[0]) - 1
    except:
        await app.sendGroupMessage(
            group,
            MessageChain.create(At(member), f"请输入服务器的数字编号")
        )
        return

    (res, count) = battlefield.vip_check(session, serverids[server])
    if res == '':
        await app.sendGroupMessage(
            group,
            MessageChain.create(At(member), f"\n清理成功~\n共清理了{count}位成员\n目标服务器为："
                                            f"\nhttps://battlefieldtracker.com/bf1/servers/pc/{gameids[server]}")
        )
    else:
        await app.sendGroupMessage(
            group,
            MessageChain.create(At(member), f"\n成功清理了{count}位成员\n但以下玩家vip已到期但移除失败\n{res}\n目标服务器为："
                                            f"\nhttps://battlefieldtracker.com/bf1/servers/pc/{gameids[server]}")
        )


@bcc.receiver(
    GroupMessage,
    decorators=[DetectPrefix(".vipinit")]
)
async def check_vip(app: Ariadne, group: Group, member: Member, ):
    if group.id not in (940987081, 792678279):
        return
    if member.permission.name == "Member":
        await app.sendGroupMessage(
            group,
            MessageChain.create(At(member), f"您没有权限呢~")
        )
        return
    global session
    session = battlefield.get_session()
    serverids = []
    for id in gameids:
        time.sleep(0.5)
        serverid = battlefield.get_serverId(session, id)
        if serverid:
            serverids.append(serverid)
            await app.sendGroupMessage(
                group,
                MessageChain.create(At(member), f"服务器https://battlefieldtracker.com/bf1/servers/pc/{id}初始化成功")
            )
        await asyncio.sleep(0.5)


scheduler = GraiaScheduler(loop=broadcast.loop, broadcast=broadcast)


@scheduler.schedule(crontabify('0 0,12 * * * 0'))
async def auto_check_vip(app: Ariadne):
    grouplist = (940987081, 792678279)
    global session
    session = battlefield.get_session()
    for group in grouplist:
        await app.sendGroupMessage(
            group,
            MessageChain.create(f"正在执行自动vip清理……")
        )
        for idx, serverid in enumerate(serverids):
            (res, count) = battlefield.vip_check(session, serverid)
            if res == '':
                await app.sendGroupMessage(
                    group,
                    MessageChain.create(f"清理成功~\n共清理了{count}位成员\n目标服务器为："
                                        f"\nhttps://battlefieldtracker.com/bf1/servers/pc/{gameids[idx]}")
                )
            else:
                await app.sendGroupMessage(
                    group,
                    MessageChain.create(f"成功清理了{count}位成员\n但以下玩家vip已到期但移除失败\n{res}\n目标服务器为："
                                        f"\nhttps://battlefieldtracker.com/bf1/servers/pc/{gameids[idx]}")
                )
        await asyncio.sleep(0.5)


app.launch_blocking()
