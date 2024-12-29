# _*_ coding:utf-8 _*_

import re
from typing import Callable


class Rules:
    def __init__(self):
        self.rules = {}
        self.default = None
        self.at_me = False  # @自己 时回复
        self.reply_me = False  # 引用自己发过的消息 时回复
        self.keyword = ''  # 群聊关键词触发

    def set_at_me(self, at_me: bool):
        self.at_me = at_me

    def set_reply_me(self, reply_me: bool):
        self.reply_me = reply_me

    def set_keyword(self, keyword: str):
        self.keyword = keyword

    def register_default(self, function):
        self.default = function
        return function

    def register(self, *args):
        args = list(args)
        if callable(args[-1]):
            function = args.pop()
            rule  = self.rules
            for a in args[:-1]:
                rule[a] = {}
                rule = rule[a]
            rule[args[-1]] = function

    def register_rule(self, *args):
        def decorator(function):
            self.register(*args, function)
        return decorator

    async def __call__(self, message, *args, **kwargs):
        texts = []
        reply = False
        args = list(args)
        rule: dict = self.rules
        for msg in message.message.message:
            if msg['type'] == 'at' and msg['data']['qq'] != 'all':
                if int(msg['data']['qq']) == int(message.self_id):
                    if self.at_me:
                        reply = True
                else:
                    texts.append(f"@{msg['data']['qq']}")
            elif msg['type'] == 'text':
                texts.append(msg['data']['text'].strip())
            elif msg['type'] == 'reply' and self.reply_me and int(msg['data']['id']) in message.message_ids:
                reply = True
        texts = ' '.join(texts).strip()
        if self.keyword and self.keyword in texts:
            reply = True
            texts = texts.replace(self.keyword, '', 1).strip()
        if not self.at_me and not self.reply_me and not self.keyword:
            reply = True
        if reply:
            for msg in texts.split(' '):
                if callable(rule):
                    break
                for r in rule:
                    if re.fullmatch(r, msg):
                        args.append(msg)
                        rule = rule[r]
            if callable(rule):
                rule: Callable
                return await rule(message, texts, *args, **kwargs)
            if callable(self.default):
                return await self.default(message, texts, *args, **kwargs)
