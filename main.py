import asyncio

from graia.ariadne.event.message import GroupMessage, FriendMessage
from graia.ariadne.event.mirai import NudgeEvent
from graia.broadcast import Broadcast

from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, At
from graia.ariadne.model import Friend, Group, MiraiSession, Member

import chatbot as ct

import random

loop = asyncio.new_event_loop()

host = input("请输入HTTP API地址:")
verifykey = input("请输入verifykey：")
account = input("请输入QQ账号：")

if host == '':
    host = "http://127.0.0.1:8080"
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

@bcc.receiver(GroupMessage)
async def groupchat(app: Ariadne, group: Group, member: Member, messageChain: MessageChain):
    if At(app.account) in messageChain:
        msg = str(messageChain.get(Plain))[13:-3]
        if "@我" in msg or "at我" in msg:
            textlist = [" ?", " ???", " 什么玩意？", " 干嘛？", " 干嘛", " 什么", " 啥"]
            await app.sendMessage(
                group,
                MessageChain.create([At(member), Plain(textlist[random.randint(0, len(textlist)-1)])]),
            )
        else:
            await app.sendMessage(
                group,
                ct.Chatbot.chat(bot,messageChain),
            )


@bcc.receiver(NudgeEvent)
async def getup(app: Ariadne, event: NudgeEvent):
    if event.context_type == "group" and event.target == 2706192373:
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

    elif event.context_type == "friend" and event.target == 2706192373:
        await app.sendFriendMessage(
            event.friend_id,
            MessageChain.create("别戳我，好痒！")
        )
    else:
        return


app.launch_blocking()
