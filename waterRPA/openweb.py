#!/usr/bin/python
# Filename: openweb.py

import os
import webbrowser
import pyautogui
import time

#打开浏览器CHROME
# 这个太笨了
# os.startfile("C:\\Users\\何博\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe")
#这个简单
#webbrowser.open('https://pt.btschool.club/login.php', new=0, autoraise=True)

webbrowser.open('https://www.haidan.video/index.php', new=0, autoraise=True)

time.sleep(3)
pyautogui.hotkey('ctrl', '0')
