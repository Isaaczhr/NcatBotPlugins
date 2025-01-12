# encoding=utf-8

from ..wsapi import WsApi
from .. import logging
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By

import json
import pyperclip
import requests
import time
import os
import re
import yaml

_log = logging.get_logger()

class SendQQMusic:
    def __init__(self, max_try = 3):
        try:
            with open(os.path.join(os.getcwd(), "config.yaml"), "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
        except FileNotFoundError:
            _log.error("[ncatpy] 配置文件不存在，请检查config.yaml是否在当前目录")
            exit(1)
        except yaml.YAMLError:
            _log.error("[ncatpy] 配置文件格式错误，请检查！")
            exit(1)
        except Exception as e:
            _log.error(f"[ncatpy] 配置文件读取错误，请检查config.yaml是否正确，错误信息：{e}")
            exit(1)
        self.driver = config["plugin"]["qqmusic"]["driver"]
        self.driver_path = config["plugin"]["qqmusic"]["driver_path"]
        self.max_try = max_try
        self.attempt = 0
        self.wsapi = WsApi()

    async def send_qqmusic(self, song_name, **kwargs):
        song_name = song_name.replace(" ", "")
        while self.attempt < self.max_try:
            url = f"https://api.52vmy.cn/api/music/qq?msg={song_name}&n=1"
            service = Service(self.driver_path)
            if self.driver == "edge":
                driver = webdriver.Edge(service=service)
            elif self.driver == "chrome":
                driver = webdriver.Chrome(service=service)
            elif self.driver == "firefox":
                driver = webdriver.Firefox(service=service)
            else:
                raise ValueError("[ncatpy] 配置文件错误，driver参数错误，请检查config.yaml")
            driver.minimize_window()
            response = requests.get(url)
            response.raise_for_status()
            music_data = response.json().get("data")
            if not music_data:
                _log.warning("[ncatpy] 未找到相关歌曲数据，正在重试...")
                self.attempt += 1
                continue

            music_url = music_data.get("url")
            _log.info(f"[ncatpy] 获取歌曲链接 {music_url} 成功，正在尝试发送...")
            if "cookies.json" not in os.listdir(os.getcwd()):
                _log.warning("[ncatpy] 未找到cookies.json文件，需要进行一次登入操作，登入成功后回车...")
                driver.get("http://y.qq.com/")
                driver.implicitly_wait(10)
                cookies = driver.get_cookies()
                with open('cookies.json', 'w') as f:
                    json.dump(cookies, f)
                _log.info("[ncatpy] cookies 保存成功，请勿删除！重新运行一次即可...")
                driver.quit()
            else:
                driver.get('http://y.qq.com/')
                with open('cookies.json', 'r') as f:
                    cookies = json.load(f)

                driver.delete_all_cookies()
                for cookie in cookies:
                    driver.add_cookie(cookie)

                driver.refresh()

            driver.get(music_url)
            driver.implicitly_wait(10)

            try:
                xpath = '//div[@class="data__actions"]/a[5][@class="mod_btn"]'
                element = driver.find_element(by=By.XPATH, value=xpath)
                element.click()
                xpath = '//div[@class="operate_menu__cont"]/ul[@class="operate_menu__list"]/li[2][@class="operate_menu__item"]'
                element = driver.find_element(by=By.XPATH, value=xpath)
                element.click()
                xpath = '//div[@class="operate_menu__cont"]/ul[@class="operate_menu__list operate_menu__list--no_icon"]/li[5]'
                element = driver.find_element(by=By.XPATH, value=xpath)
                driver.execute_script("arguments[0].click();", element)
                music_share_url = pyperclip.paste()
                song_id = re.search(r'songid=(\d+)', music_share_url)
                if song_id:
                    return await self.wsapi.send_msg(music=song_id.group(1), **kwargs)
                return None
            except Exception as e:
                _log.error(f"[ncatpy] 获取歌曲失败，正在重试...错误信息：{e}")
                self.attempt += 1
            finally:
                driver.quit()


