@echo off
setlocal EnableDelayedExpansion

:: --- PHẦN TỰ ĐỘNG XIN QUYỀN ADMIN ---
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if '%errorlevel%' NEQ '0' (
    echo Dang yeu cau quyen Administrator...
    goto UACPrompt
) else ( goto gotAdmin )
:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    exit /B
:gotAdmin
    if exist "%temp%\getadmin.vbs" ( del "%temp%\getadmin.vbs" )
    pushd "%CD%"
    CD /D "%~dp0"

:: --- ĐỊNH NGHĨA MÀU ANSI (CHỮ + NỀN) ---
for /F "tokens=1,2 delims=#" %%a in ('"prompt #$E# & echo on & for %%b in (1) do rem"') do (set "ESC=%%a")

set "RESET=%ESC%[0m"
:: Nền Đỏ (41), Chữ Trắng Sáng (97)
set "BG_RED=%ESC%[41;97m"
:: Nền Xanh Lá (42), Chữ Đen (30)
set "BG_GREEN=%ESC%[42;30m"
::nền Xanh dương chữ trắng
set "BG_BLUE=%ESC%[44;97m"
:: Chữ Xanh Dương Sáng (94)
set "C_BLUE=%ESC%[94m"

cls
echo ===========================================
echo     HE THONG DIEU KHIEN INTERNET TU DONG
echo ===========================================

:: Bước 1: Kiểm tra trạng thái
netsh interface show interface | findstr /C:"Connected" >nul

if %errorLevel% == 0 (
    set "final_action=disabled"
    echo    %BG_RED% STATUS: INTERNET DANG MO ==^> DANG TAT %RESET%
    echo.
    echo [ACTION] DANG NGAT TAT CA CAC CARD MANG...
) else (
    set "final_action=enabled"
    echo    %BG_GREEN% STATUS: INTERNET DANG TAT ==^> DANG BAT %RESET%
    echo.
    echo [ACTION] DANG KET NOI LAI TAT CA CAC CARD...
)

echo -------------------------------------------

:: Bước 2: Xử lý các Card mạng
for /f "skip=3 tokens=3,*" %%A in ('netsh interface show interface') do (
    set "type=%%A"
    set "name=%%B"
    if /I "!type!"=="Dedicated" (
        echo  [+] Dang xu ly: !name!
        netsh interface set interface name="!name!" admin=!final_action! >nul 2>&1
    )
)

echo -------------------------------------------
echo %BG_BLUE%[OK] DA HOAN TAT THAY DOI!%RESET%
echo Cua so se tu dong dong sau 5 giay.
timeout /t 5 >nul