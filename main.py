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
from graia.ariadne.model import Friend, Group, MiraiSession, Member, MemberInfo

import mychatbot as ct

import random

from graia.broadcast.interrupt import InterruptControl
from graia.broadcast.interrupt.waiter import Waiter

loop = asyncio.new_event_loop()

host = input("请输入HTTP API地址:")
verifykey = input("请输入verifykey：")
account = input("请输入QQ账号：")

if host == '':
    host = "http://localhost:8080"
if account == '':
    account = 2706192373
else:
    account = int(account)

broadcast = Broadcast(loop=loop)
app = Ariadne(
    broadcast=broadcast,
    connect_info=MiraiSession(
        host=host,  # 填入 HTTP API 服务运行的地址
        verify_key=verifykey,  # 填入 verifyKey
        account=account,  # 你的机器人的 qq 号
    )
)

bcc = app.broadcast
app.count = 0

bot = ct.Chatbot()

setucold = dict()

inc = InterruptControl(bcc)

# 狼人杀
game = ct.Wmh()


@bcc.receiver(TempMessage, decorators=[DetectPrefix("/狼人杀"), DetectSuffix("杀人")])
async def tempmsgforwmh(app: Ariadne, player: Member, message: MessageChain = DetectPrefix("/狼人杀")):
    if game.stage == 1:
        await app.sendMessage(player, MessageChain.create("光天化日之下不能杀人"))
        return
    if not game.canact(player):
        await app.sendMessage(player, MessageChain.create("你不能这样操作哦~"))
        return
    await app.sendMessage(player, MessageChain.create("请直接输入id，如“1”"))

    @Waiter.create_using_function([TempMessage])
    async def wolf_waiter(p: Member, m: MessageChain):
        # 判断和处理
        if p == player:
            msg = str(m.get(Plain))[13:-3]
            try:
                targetid = int(msg)
                return targetid  # 只要不是 None 就会继续执行
            except:
                return Force(None)

    try:
        res = await inc.wait(wolf_waiter, timeout=30)
        game.killlist.append(res)
        await app.sendMessage(
            player,
            MessageChain.create("投票成功：" + str(res))
        )
    except asyncio.TimeoutError:
        await app.sendMessage(
            player,
            MessageChain.create("超时，默认弃票")
        )
        game.killlist.append(0)
    finally:
        await game.isnightfinish()


@bcc.receiver(FriendMessage, decorators=[DetectPrefix("/狼人杀"), DetectSuffix("杀人")])
async def tempmsgforwmh(app: Ariadne, player: Friend, message: MessageChain = DetectPrefix("/狼人杀")):
    if game.stage == 1:
        await app.sendMessage(player, MessageChain.create("光天化日之下不能杀人"))
        return
    if not game.canact(player):
        await app.sendMessage(player, MessageChain.create("你不能这样操作哦~"))
        return
    await app.sendMessage(player, MessageChain.create("请直接输入id，如“1”"))

    @Waiter.create_using_function([FriendMessage])
    async def wolf_waiter(p: Friend, m: MessageChain):
        # 判断和处理
        if p == player:
            msg = str(m.get(Plain))[13:-3]
            try:
                targetid = int(msg)
                return targetid  # 只要不是 None 就会继续执行
            except:
                return Force(None)

    try:
        res = await inc.wait(wolf_waiter, timeout=30)
        game.killlist.append(res)
        await app.sendMessage(
            player,
            MessageChain.create("投票成功：" + str(res))
        )
    except asyncio.TimeoutError:
        await app.sendMessage(
            player,
            MessageChain.create("超时，默认弃票")
        )
        game.killlist.append(0)
    finally:
        await game.isnightfinish()


@bcc.receiver(TempMessage, decorators=[DetectPrefix("/狼人杀"), DetectSuffix("预言")])
async def tempmsgforwmh(app: Ariadne, player: Member, message: MessageChain = DetectPrefix("/狼人杀")):
    if game.stage == 1:
        await app.sendMessage(player, MessageChain.create("光天化日之下不能预言"))
        return
    if not game.canact(player):
        await app.sendMessage(player, MessageChain.create("你不能这样操作哦~"))
        return
    await app.sendMessage(player, MessageChain.create("请直接输入id，如“1”"))

    @Waiter.create_using_function([FriendMessage])
    async def prophet_waiter(p: Friend, m: MessageChain):
        # 判断和处理
        if p == player:
            msg = str(m.get(Plain))[13:-3]
            try:
                targetid = int(msg)
                return targetid  # 只要不是 None 就会继续执行
            except:
                return Force(None)

    try:
        res = await inc.wait(prophet_waiter, timeout=30)
        if res == 0:
            await app.sendMessage(
                player,
                MessageChain.create("预言失败")
            )
            return
        await app.sendMessage(
            player,
            MessageChain.create("他是身份是：" + str(game.role_list[res - 1].name))
        )
        game.killlist.append(0)
    except asyncio.TimeoutError:
        await app.sendMessage(
            player,
            MessageChain.create("超时，默认弃票")
        )
        game.killlist.append(0)
    finally:
        await game.isnightfinish()


@bcc.receiver(FriendMessage, decorators=[DetectPrefix("/狼人杀"), DetectSuffix("预言")])
async def tempmsgforwmh(app: Ariadne, player: Friend, message: MessageChain = DetectPrefix("/狼人杀")):
    if game.stage == 1:
        await app.sendMessage(player, MessageChain.create("光天化日之下不能预言"))
        return
    if not game.canact(player):
        await app.sendMessage(player, MessageChain.create("你不能这样操作哦~"))
        return
    await app.sendMessage(player, MessageChain.create("请直接输入id，如“1”"))

    @Waiter.create_using_function([FriendMessage])
    async def prophet_waiter(p: Friend, m: MessageChain):
        # 判断和处理
        if p == player:
            msg = str(m.get(Plain))[13:-3]
            try:
                targetid = int(msg)
                return targetid  # 只要不是 None 就会继续执行
            except:
                return Force(None)

    try:
        res = await inc.wait(prophet_waiter, timeout=30)
        await app.sendMessage(
            player,
            MessageChain.create("他是身份是：" + str(game.role_list[res - 1].name))
        )
        game.killlist.append(0)
    except asyncio.TimeoutError:
        await app.sendMessage(
            player,
            MessageChain.create("超时，默认弃票")
        )
        game.killlist.append(0)
    finally:
        await game.isnightfinish()


@bcc.receiver(GroupMessage)
async def py2ch(app: Ariadne, group: Group, member: Member, message: MessageChain):
    msg = str(message.get(Plain))[13:-3]
    if msg.islower():
        res = bot.pinyin2hanzi(msg.split(" "))
        if res:
            await app.sendMessage(
                group,
                MessageChain.create("他说：" + res),
            )


@bcc.receiver(
    GroupMessage,
    decorators=[DetectPrefix("/狼人杀")]
)
async def langrensha(app: Ariadne, group: Group, member: Member,
                     message: MessageChain = DetectPrefix("/狼人杀")):
    command = str(message.get(Plain))[13:-3]
    if "新游戏" in command:
        game.app = app
        game.group = group
        if game.ingame:
            await app.sendMessage(
                group,
                game.isingame(),
            )
            return
        else:
            game.ingame = True
            await app.sendMessage(
                group,
                MessageChain.create("开始游戏\n请发送：\n\"/狼人杀 加入\"\n加入游戏"),
            )
    if "加入" in command:
        if not game.ingame:
            await app.sendMessage(
                group,
                MessageChain.create(At(member), "\n未创建新游戏"),
            )
            return
        try:
            if member in game.player_list:
                await app.sendMessage(
                    group,
                    MessageChain.create(At(member), "\n你已经在游戏中了"),
                )
                return
            if game.player_number >= 7:
                await app.sendMessage(
                    group,
                    MessageChain.create(At(member), "\n人已经满啦~"),
                )
                return
            game.joingame(member)
            await app.sendMessage(
                group,
                MessageChain.create(At(member), "\n加入成功, 当前玩家数:" + str(game.player_number)),
            )
        except:
            await app.sendMessage(
                group,
                MessageChain.create(At(member), "\n加入失败, 寄"),
            )
    if "开始游戏" in command:
        gmsg, pmsg, roles = game.startgame()
        await app.sendMessage(
            group,
            gmsg
        )
        for player in game.player_list:
            await app.sendMessage(
                player,
                pmsg
            )
        await app.sendMessage(
            group,
            MessageChain.create("正在分配身份……")
        )
        # 向玩家发送身份
        for item in roles:
            await app.sendTempMessage(
                item[0],
                item[1]
            )
        # 入夜
        wolf_msg_list, prophet_msg_list = game.night()
        for w in wolf_msg_list:
            await app.sendTempMessage(
                w[0],
                w[1]
            )
        for p in prophet_msg_list:
            await app.sendTempMessage(
                p[0],
                p[1]
            )
    if "入夜" in command:
        if game.stage == 0:
            return
        wolf_msg_list, prophet_msg_list = game.night()
        for w in wolf_msg_list:
            await app.sendTempMessage(
                w[0],
                w[1]
            )
        for p in prophet_msg_list:
            await app.sendTempMessage(
                p[0],
                p[1]
            )
    if "结束游戏" in command:
        if not game.ingame:
            await app.sendMessage(
                group,
                MessageChain.create(At(member), "\n未创建新游戏"),
            )
            return
        try:
            game.endgame()
            await app.sendMessage(
                group,
                MessageChain.create("结束成功"),
            )
        except:
            await app.sendMessage(
                group,
                MessageChain.create("报错了，大寄特寄"),
            )


@bcc.receiver(
    GroupMessage,
    decorators=[DetectPrefix("/狼人杀 指认 ")]
)
async def zhiren(app: Ariadne, group: Group, member: Member,
                 message: MessageChain = DetectPrefix("/狼人杀 指认 ")):
    command = str(message.get(Plain))[13:-3]
    try:
        voteid = int(command)
        game.votelist.append(voteid)
        await game.isvotefinish()
    except:
        await app.sendMessage(group, MessageChain.create(At(member), "注意格式"))


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
    option = '0'
    endure = 10
    if "r18" in str(message.get(Plain))[13:-3]:
        option = "1"
        endure = 5
    try:
        sess = requests.get(
            'https://api.lolicon.app/setu/v2?proxy=i.pixiv.re' + "&r18=" + option)
        js = sess.text
        js = json.loads(js)
    except:
        await app.sendMessage(
            group,
            MessageChain.create("呜呜呜找不到涩图"),
        )
        return
    imginfo = "标题: " + js["data"][0]["title"] + "\n" + "pid: " + str(js["data"][0]["pid"]) + "\n作者: " + js["data"][0][
        "author"] + "\nuid: " + str(js["data"][0]["uid"]) + "\n原图链接: " + js["data"][0]["urls"]["original"]
    await app.sendMessage(
        group,
        MessageChain.create(imginfo),
    )
    imgurl = js["data"][0]["urls"]["original"]
    session = get_running(Adapter).session
    try:
        async with session.get(imgurl) as r:
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


app.launch_blocking()
