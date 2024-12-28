# encoding=utf-8

from .. import logging
import threading
import time
import asyncio

_log = logging.get_logger()

class OnTime:
    def __init__(self):
        self._tasks_list = {}
        self._stop_events = {}

    def add_time_task(self, trigger_time, thread_name, func):
        _log.info(f"添加定时任务：{trigger_time} --> {func.__name__}")

        async def task_wrapper(stop_event):
            while not stop_event.is_set():
                _time = time.strftime("%H:%M", time.localtime())
                if _time == trigger_time:
                    _log.info(f"定时任务触发：{func.__name__}")
                    # 怕有人创建函数用同步异步都有，所以这里判断一下🤪
                    if asyncio.iscoroutinefunction(func):
                        await func()
                    else:
                        func()
                    break
                await asyncio.sleep(1)

        if thread_name in self._tasks_list:
            _log.warning(f"线程 {thread_name} 已存在，无法重复创建")
            return

        stop_event = threading.Event()
        self._stop_events[thread_name] = stop_event

        def start_async_task():
            asyncio.run(task_wrapper(stop_event))

        task_thread = threading.Thread(target=start_async_task, name=thread_name, daemon=True)
        self._tasks_list[thread_name] = task_thread
        task_thread.start()
        _log.info(f"线程 {thread_name} 启动成功")

    def cancel_time_task(self, thread_name):
        _log.info(f"尝试取消线程 {thread_name}")
        stop_event = self._stop_events.get(thread_name)

        if not stop_event:
            _log.warning(f"线程 {thread_name} 不存在")
            return

        stop_event.set()
        self._tasks_list.pop(thread_name, None)
        self._stop_events.pop(thread_name, None)
        _log.info(f"线程 {thread_name} 已从任务列表中移除")

    def get_tasks_list(self):
        """
        获取所有定时任务的列表。

        :return: 定时任务列表
        """
        _log.info(f"所有定时任务的列表：{list(self._tasks_list.keys())}")
        return list(self._tasks_list.keys())


