@echo off
title Run Antigravity Remote Tests
chcp 65001 > nul
echo [1/2] Dang chay kiem thu cac luong chinh...
python run_tests.py
echo.
echo [2/2] Dang chay kiem thu edge cases...
python test_edge_cases.py
echo.
pause
