#!/usr/bin/env python3

from pyautogui import alert as pag_alert
from pyautogui import click, position, rightClick, moveTo
from time import sleep

pag_alert("Ok?")
prev_pos = position()
click(282, 132)

sleep(1)

rightClick(1370, 229)
click(1350, 229)
moveTo(prev_pos)
