@echo off
title Tat Antigravity Remote Bot
chcp 65001 > nul
cd /d "%~dp0"
python stop_bot.py
ping -n 3 127.0.0.1 > nul
