# encoding: utf-8

import ncatpy
from ncatpy import logging
from ncatpy.message import GroupMessage,PrivateMessage

_log = logging.get_logger()

class MyClient(ncatpy.Client):
    async def on_group_message(self, message: GroupMessage):
        _log.info(f"收到群消息，ID: {message.message.text.text}")
        if message.message.at.qq == "3786498591":
            await self._SendQQMusic.send_qqmusic(song_name=message.message.text.text, group_id=message.group_id)
    async def on_private_message(self, message: PrivateMessage):
        _log.info(f"收到私聊消息，ID: {message.sender.user_id}")
        if message.sender.user_id == 111111111:# 这里的示例用的QQ号，不用加引号
            await self._SendQQMusic.send_qqmusic(song_name=message.message.text.text, user_id=message.user_id)

if __name__ == "__main__":
    # 1. 通过预设置的类型，设置需要监听的事件通道
    intents = ncatpy.Intents.public() # 可以订阅public，包括了私聊和群聊

    # 2. 通过kwargs，设置需要监听的事件通道
    # intents = ncatpy.Intents(group_event=True)
    client = MyClient(intents=intents, plugins=["SendQQMusic"])# 插件
    client.run()
