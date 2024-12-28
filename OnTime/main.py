# encoding: utf-8

import ncatpy
from ncatpy import logging
from ncatpy.message import GroupMessage,PrivateMessage

_log = logging.get_logger()

class MyClient(ncatpy.Client):
    async def on_group_message(self, message: GroupMessage):
        _log.info(f"收到群消息，ID: {message.message.text.text}")
        _log.info(message.user_id)
        if message.message.text.text == "/创建":
            async def test():
                await self._api.send_msg(group_id=623948400, text="你好,o")
            self._OnTime.add_time_task("00:28", "test1", test)# 三个值：时间，线程名，函数，函数得自己创建，异步同步都可以
        if message.message.text.text == "/取消":
            self._OnTime.cancel_time_task("test1")# 线程名

        if message.message.text.text == "/list":
            _log.info(self._OnTime.get_tasks_list())# 获取任务列表

        if message.message.text.text == "/create":# 创建任务，和上面的创建同理
            async def test2():
                await self._api.send_msg(group_id=623948400, text="你好,o")
            self._OnTime.add_time_task("00:29", "test2", test2)

if __name__ == "__main__":
    # 1. 通过预设置的类型，设置需要监听的事件通道
    # intents = ncatpy.Intents.public() # 可以订阅public，包括了私聊和群聊

    # 2. 通过kwargs，设置需要监听的事件通道
    intents = ncatpy.Intents(group_event=True)
    client = MyClient(intents=intents, plugins=["OnTime"])# 插件
    client.run()
