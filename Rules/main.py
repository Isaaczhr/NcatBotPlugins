# encoding: utf-8

import ncatpy
from ncatpy import logging
from ncatpy.message import GroupMessage

_log = logging.get_logger()

bot = None

class MyClient(ncatpy.Client):
    async def on_group_message(self, message: GroupMessage):
        global bot
        _log.info(f"收到群消息，ID: {message.message.text.text}")
        _log.info(message.user_id)
        if not bot:
            bot = (await message.get_login_info())['data']
        if bot['user_id'] != message.sender.user_id:
            await self._Rules(message)


if __name__ == "__main__":
    # 1. 通过预设置的类型，设置需要监听的事件通道
    # intents = ncatpy.Intents.public() # 可以订阅public，包括了私聊和群聊

    # 2. 通过kwargs，设置需要监听的事件通道
    intents = ncatpy.Intents(group_event=True)
    client = MyClient(intents=intents, plugins=["Rules"])# 插件
    client._Rules.set_at_me(True)  # 设置@机器人时回复
    client._Rules.set_reply_me(True)  # 设置引用机器人消息时回复
    client._Rules.set_keyword('小蝴蝶')  # 设置存在关键词回复

    @client._Rules.register_default  # 规则之外的默认值，可以不写
    async def _(message: GroupMessage, texts, *args, **kwargs):
        print('默认', args, kwargs)
        await message.add_text('其他').reply()

    @client._Rules.register_rule('测试1')
    async def _(message: GroupMessage, texts, *args, **kwargs):
        print(message)
        await message.add_text('收到测试1').reply()

    @client._Rules.register_rule('测试2', '.*?')
    async def _(message: GroupMessage, texts, *args, **kwargs):
        print(args[1])
        print(message)
        await message.add_text('收到测试2').reply()

    client.run()
