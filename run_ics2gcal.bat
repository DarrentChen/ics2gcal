@echo off
rem 用法 1 (預設/未指定帳號):
rem   run_ics2gcal.bat "D:\work\invite.ics"
rem
rem 用法 2 (指定帳號):
rem   run_ics2gcal.bat "D:\work\invite.ics" "darrent.chen@gmail.com"

set "ICS_FILE=%~1"
set "ACCOUNT=%~2"

rem 如果沒有傳入任何 .ics 檔案，呼叫 python 顯示使用說明並暫停視窗
if "%ICS_FILE%"=="" (
    python "D:\work\ics2gcal.py"
    echo.
    pause
    exit /b
)

if "%ACCOUNT%"=="" (
    pythonw "D:\work\ics2gcal.py" "%ICS_FILE%"
) else (
    pythonw "D:\work\ics2gcal.py" "%ICS_FILE%" "%ACCOUNT%"
)
