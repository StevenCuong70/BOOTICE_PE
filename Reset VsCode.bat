@echo off
chcp 65001 > nul
title RESET VS CODE - CLEAN CONFIG

echo =====================================
echo   RESET VS CODE - CLEAN CONFIG
echo =====================================
echo.

REM Đóng VS Code nếu đang chạy
echo [1/3] Đang đóng VS Code...
taskkill /f /im Code.exe > nul 2>&1

set "path_Apdata=%APPDATA%\Code"
REM Xoá %APPDATA%\Code
echo [2/3] Xoá %path_Apdata%
if exist "%path_Apdata%" (
    rmdir /s /q "%path_Apdata%"
    echo     ✔ Đã xoá folder Code path: %path_Apdata%  
) else (
    echo     ! Không tìm thấy %path_Apdata%
)

REM Xoá C:\Users\ManhCuong\.vscode
set "path_vsCode=%USERPROFILE%\.vscode"

echo [3/3] Xoá %path_vsCode%
::%USERPROFILE%\.vscode

if exist "%path_vsCode%" (
    rmdir /s /q "%path_vsCode%"
    echo     ✔ Đã xoá %path_vsCode%    
) else (
    echo     ! Không tìm thấy %path_vsCode%
)

echo.
echo =====================================
echo   HOÀN TẤT - VS CODE ĐÃ RESET SẠCH.
echo =====================================
echo.
pause
