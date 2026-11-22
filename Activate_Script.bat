@setlocal DisableDelayedExpansion
@echo off

title Backup and Restore [WINDOWS-OFFICE] - Manh Cuong Nguyen.
::Get APIkey From https://khoatoantin.com/pidms
set "apikey=nVHBz3RIsHpXHofLv3B89iFK8"
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if '%errorlevel%' NEQ '0' (
    goto goUAC 
) else (
 goto goADMIN )

:goUAC
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    set params = %*:"=""
    echo UAC.ShellExecute "cmd.exe", "/c %~s0 %params%", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    del "%temp%\getadmin.vbs"
    exit /B

:goADMIN
    pushd "%CD%"
    CD /D "%~dp0"

:Menu
cls
mode con: cols=75 lines=26
REM Define the Escape character
for /F "tokens=1,2 delims=#" %%a in ('"prompt #$E# & echo on & for %%b in (1) do rem"') do (
    set "ESC=%%a"
)

REM Define some color codes
set "RED=%ESC%[0;31m"
set "GREEN=%ESC%[0;32m"
set "YELLOW=%ESC%[0;33m"
set "BLUE=%ESC%[0;34m"
set "WHITE=%ESC%[0;37m"
set "Cyan=%ESC%[0;36m"


set "RESET=%ESC%[0m"
for /f "tokens=2,*" %%I in ('reg query "HKLM\SOFTWARE\Microsoft\Office\ClickToRun\Configuration" /v ProductReleaseIds 2^>nul') do set OfficeVersion=%%J
if "%OfficeVersion%"=="" for /f "tokens=3*" %%I in ('reg query "HKLM\SOFTWARE\Microsoft\Office" /s /v "ProductName" 2^>nul ^| findstr /i "ProductName"') do set OfficeVersion=%%I %%J
For /f "tokens=3" %%b in ('cscript %windir%\system32\slmgr.vbs /dli ^| findstr /b /c:"License Status"') do set LicenseStatus=%%b
For /f "tokens=*" %%b in ('cscript %windir%\system32\slmgr.vbs /xpr') do set License=%%b

echo ================================================================
echo            %GREEN%SCRIPT Created by: Manh Cuong Nguyen%RESET%
echo            TRANG THAI KICH HOAT WINDOWS - OFFICE.
echo ================================================================
echo            Phien Ban Office Da CAI DAT Tren May Cua Ban La:
echo.
echo                     [ %YELLOW%%OfficeVersion%%RESET% ]
echo =================================================================
echo        %Cyan%[CONG CU SAO LUU KHOI PHUC WINDOWS-OFFICE] %RESET%
echo. 
ECHO    [1] KIEM TRA TRANG THAI KICH HOAT WINDOWS - OFFICE
ECHO    [2] GO SACH KEY OFFICE CU                %GREEN%^>^> [Khuyen dung] ^<^<%RESET%
ECHO    [3] GO KEY OFFICE THEO TUY CHON
ECHO    [4] KICH HOAT BAN QUYEN BANG KEY ONLINE  %GREEN%^>^> [Khuyen dung] ^<^<%RESET%
ECHO    [5] NHAP KEY VA KICH HOAT OFFICE LAY IID CID 
ECHO    [6]%YELLOW% SAO LUU BAN QUYEN WINDOWS - OFFICE %RESET%
ECHO    [7]%YELLOW% KHOI PHUC BAN QUYEN DA SAO LUU %RESET%
ECHO    [0] %Cyan%THOAT%RESET%
echo =================================================================
echo.
echo NHAP LUA CHON CUA BAN [1,2,3,4,5,6,7] VA NHAN ENTER.
set /p choice=" %YELLOW%NHAP LUA CHON CUA BAN:%RESET% "
if "%choice%"=="1" Goto thong_tin
if "%choice%"=="2" Goto gokey
if "%choice%"=="3" Goto gokey_2
if "%choice%"=="4" Goto kich_key_copy
if "%choice%"=="5" Goto nhap_key
if "%choice%"=="6" Goto sao_luu
if "%choice%"=="7" Goto khoi_phuc
if %ERRORLEVEL%==0 goto thoat

::==============[ KIEM TRA THONG TIN KICH HOAT WINDOWS - OFFICE ]==============
:thong_tin
mode con: cols=80 lines=40
cls

echo.
echo ===================== [Kiem Tra Thong Tin Windows] ====================
echo.
echo.

cscript //nologo %windir%\system32\slmgr.vbs /dlv
echo.
echo.
echo ==================== [Kiem Tra Thong Tin Office] ======================
echo.
echo.

:: Office MSI (Office14–16)
for %%a in (14 15 16) do (
    if exist "%ProgramFiles%\Microsoft Office\Office%%a\ospp.vbs" (
	echo Office MSI Office%%a
        cd /d "%ProgramFiles%\Microsoft Office\Office%%a"
        cscript //nologo ospp.vbs /dstatus
    )
    if exist "%ProgramFiles(x86)%\Microsoft Office\Office%%a\ospp.vbs" (
        cd /d "%ProgramFiles(x86)%\Microsoft Office\Office%%a"
        cscript //nologo ospp.vbs /dstatus
    )
)

:: Office Click-to-Run 64-bit
if exist "C:\Program Files\Microsoft Office\root\Licenses16" (
    echo Office Click-to-Run 64-bit
    cd /d "C:\Program Files\Microsoft Office\root\Office16"
    cscript //nologo ospp.vbs /dstatus
)

:: Office Click-to-Run 32-bit
if exist "C:\Program Files (x86)\Microsoft Office\root\Licenses16" (
    echo Office Click-to-Run 32-bit
    cd /d "C:\Program Files (x86)\Microsoft Office\root\Office16"
    cscript //nologo ospp.vbs /dstatus
)

echo.
echo ======================= [Kiem Tra Hoan Tat] ==========================
pause
endlocal
goto Menu


::==========================================================================


:kich_key_copy
cls
echo.
echo  KICH HOAT BAN QUYEN WINDOWS - OFFICE BANG KEY ONLINE
echo ======================================================================
echo.

for /f "tokens=*" %%b in ('powershell -Command "$k=Read-Host 'NHAP PRODUCT KEY' -AsSecureString; $bstr=[Runtime.InteropServices.Marshal]::SecureStringToBSTR($k); [Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr)"') do set k1=%%b
cls
Echo ====================== KIEM TRA PRODUCT KEY ==========================
for /f tokens^=2* %%i in ('sc query^|find "Clipboard"')do >nul cd.|clip & net stop "%%i %%j" >nul 2>&1 && net start "%%i %%j" >nul 2>&1

For /F %%b in ('Powershell -Command $Env:k1.Length') do Set KeyLen=%%b
if "%KeyLen%" NEQ "29" goto InvalidKey
for /f "tokens=*" %%b in ('powershell -Command "$req = [System.Net.WebRequest]::Create('https://pidkey.com/ajax/pidms_api?keys=%k1%&justgetdescription=0&apikey=%apikey%');$resp = New-Object System.IO.StreamReader $req.GetResponse().GetResponseStream(); $resp.ReadToEnd()"') do set CheckKey=%%b
SET CheckKey1=%CheckKey:"=_%
for /f "tokens=12 delims=," %%b in ("%CheckKey1%") do set Keyerr=%%b
if "%Keyerr%" EQU "_errorcode_:_0xC004C060_" goto InvalidKey
if "%Keyerr%" EQU "_errorcode_:_0xC004C003_" goto InvalidKey
for /f "tokens=11 delims=," %%b in ("%CheckKey1%") do set Keyerr=%%b
if "%Keyerr%" EQU "_blocked_:1" goto InvalidKey
for /f "tokens=6 delims=," %%b in ("%CheckKey1%") do set CheckKey2=%%b
for /f "tokens=2 delims=:" %%b in ("%CheckKey2%") do set prd=%%b
for /f "tokens=2 delims=_" %%b in ("%prd%") do set Kind=%%b
set CheckOffVer=%prd:~7,2%
set "OffVer=Licenses16"
if "%CheckOffVer%" == "14" set "OffVer=Licenses"
if "%CheckOffVer%" == "15" set "OffVer=Licenses15"
set prd1=%prd:~1,3%
set prd2=%prd:~1,6%
set prd3=%prd:~1,4%
Echo ... Type: %prd% ...
if "%prd3%" == "null" goto UndefinedKey
if "%WmicActivation%"=="1" goto Wmic_Activation
if "%prd1%" == "Win" goto ActivateWindows
if "%prd2%" == "Office" goto ActivateOffice
Goto Menu


:ActivateWindows
cd /d "%windir%\system32"
cscript slmgr.vbs /ipk %k1%
cls
Echo  KICH HOAT WINDOWS %prd% 
for /f "tokens=3" %%b in ('cscript slmgr.vbs /dti ^| findstr /b /c:"Installation"') do set IID=%%b
for /f "tokens=9 delims=," %%b in ('powershell -Command "$req = [System.Net.WebRequest]::Create('https://pidkey.com/ajax/cidms_api?iids=%IID%&justforcheck=0&apikey=%apikey%');$resp = New-Object System.IO.StreamReader $req.GetResponse().GetResponseStream(); $resp.ReadToEnd()"') do set ACID=%%b
set CID=%ACID:~27,48%
cscript slmgr.vbs /atp %CID%
cscript slmgr.vbs /ato
Echo %prd%>k2.txt & echo IID:%IID% >>k2.txt & echo CID:%CID% >>k2.txt & echo %DATE%_%TIME% >> k2.txt  & ver>>k2.txt & cscript slmgr.vbs /dli >>k2.txt & cscript slmgr.vbs /xpr >>k2.txt & start k2.txt 
start ms-settings:activation          

for /F "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do (set "DEL=%%a")
pause
Goto Menu
:ActivateOffice
for %%a in (4,5,6) do (
if exist "%ProgramFiles%\Microsoft Office\Office1%%a\ospp.vbs" (cd /d "%ProgramFiles%\Microsoft Office\Office1%%a")
if exist "%ProgramFiles(x86)%\Microsoft Office\Office1%%a\ospp.vbs" (cd /d "%ProgramFiles(x86)%\Microsoft Office\Office1%%a")
)
cls
Echo KICH HOAT %prd% ...
for /f "tokens=3" %%b in ('cscript ospp.vbs /inpkey:%k1% ^| findstr /b /c:"ERROR CODE"') do set err=%%b
if "%err%" == "0xC004F069" for /f %%x in ('dir /b ..\root\%OffVer%\%Kind%*.xrm-ms') do cscript ospp.vbs /inslic:"..\root\%OffVer%\%%x"
if "%err%" == "0xC004F069" cscript ospp.vbs /inpkey:%k1%
for /f "tokens=8" %%b in ('cscript ospp.vbs /dinstid ^| findstr /c:"%kind%"') do set IID=%%b
for /f "tokens=9 delims=," %%b in ('powershell -Command "$req = [System.Net.WebRequest]::Create('https://pidkey.com/ajax/cidms_api?iids=%IID%&justforcheck=0&apikey=%apikey%');$resp = New-Object System.IO.StreamReader $req.GetResponse().GetResponseStream(); $resp.ReadToEnd()"') do set ACID=%%b
set CID=%ACID:~27,48%
cscript ospp.vbs /actcid:%CID%
cscript ospp.vbs /act
Echo %prd%>k1.txt & echo IID:%IID%>>k1.txt & echo CID:%CID%>>k1.txt & echo %DATE%_%TIME% >> k1.txt & cscript ospp.vbs /dstatus >>k1.txt & start k1.txt

for /F "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do (set "DEL=%%a")
pause
Goto Menu

:InvalidKey
echo KEY KHONG HOP LE

for /F "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do (set "DEL=%%a")
pause
Goto Menu

:UndefinedKey
echo KEY KHONG XAC DINH

for /F "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do (set "DEL=%%a")
pause
Goto Menu


:gokey
cls
echo DANG XOA KEY OFFICE..

for %%a in (4,5,6) do (
    if exist "%ProgramFiles%\Microsoft Office\Office1%%a\ospp.vbs" (
        cd /d "%ProgramFiles%\Microsoft Office\Office1%%a"
    )
    if exist "%ProgramFiles(x86)%\Microsoft Office\Office1%%a\ospp.vbs" (
        cd /d "%ProgramFiles(x86)%\Microsoft Office\Office1%%a"
    )
    for /f "tokens=8" %%b in ('cscript //nologo OSPP.VBS /dstatus ^| findstr /b /c:"Last 5"') do (
        cscript //nologo ospp.vbs /unpkey:%%b
    )
)
echo NHAN PHIM BAT KY DE QUAY TRO LAI MENU CHINH
pause
Goto Menu
echo.

:gokey_2
mode con: cols=70 lines=50
for %%a in (4,5,6) do (
if exist "%ProgramFiles%\Microsoft Office\Office1%%a\ospp.vbs" (cd /d "%ProgramFiles%\Microsoft Office\Office1%%a")
if exist "%ProgramFiles(x86)%\Microsoft Office\Office1%%a\ospp.vbs" (cd /d "%ProgramFiles(x86)%\Microsoft Office\Office1%%a")
)
cls
cscript ospp.vbs /dstatus 
Goto go_key


:go_key
set "uninstallkey="
echo.
set /p "uninstallkey=NHAP 5 KY TU CUOI KEY CAN XOA:"
if "%uninstallkey%" EQU "" Goto 6_ActivateMicrosoftLicense
cscript ospp.vbs /unpkey:%uninstallkey%
pause
Goto Menu

::=======================================================================

:nhap_key
for %%a in (4,5,6) do (
    if exist "%ProgramFiles%\Microsoft Office\Office1%%a\ospp.vbs" (cd /d "%ProgramFiles%\Microsoft Office\Office1%%a")
    if exist "%ProgramFiles(x86)%\Microsoft Office\Office1%%a\ospp.vbs" (cd /d "%ProgramFiles(x86)%\Microsoft Office\Office1%%a")
)
echo.
set "install="
for /f "delims=" %%A in ('powershell -Command "$k=Read-Host 'NHAP KEY' -AsSecureString; [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($k))"') do set "install=%%A"
if "%install%"=="" Goto 6_ActivateMicrosoftLicense
for /f tokens^=2* %%i in ('sc query^|find "Clipboard"')do >nul cd.|clip & net stop "%%i %%j" >nul 2>&1 && net start "%%i %%j" >nul 2>&1
cscript ospp.vbs /inpkey:%install%
cscript ospp.vbs /dinstid


for /F "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do (set "DEL=%%a")
goto get_iid

:get_iid
for %%a in (4,5,6) do (
if exist "%ProgramFiles%\Microsoft Office\Office1%%a\ospp.vbs" (cd /d "%ProgramFiles%\Microsoft Office\Office1%%a")
if exist "%ProgramFiles(x86)%\Microsoft Office\Office1%%a\ospp.vbs" (cd /d "%ProgramFiles(x86)%\Microsoft Office\Office1%%a")
)
cls
cscript ospp.vbs /dinstid
cscript ospp.vbs /dinstid>"%~dp0iid.txt"
start %~dp0iid.txt

for /F "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do (set "DEL=%%a")
goto get_cid

:get_cid
set "iid="
echo.
set /p "iid=NHAP IID:"
if "%iid%" EQU "" Goto 6_ActivateMicrosoftLicense
for /f "tokens=9 delims=," %%b in ('powershell -Command "$req = [System.Net.WebRequest]::Create('https://pidkey.com/ajax/cidms_api?iids=%iid%&justforcheck=0&apikey=%apikey%');$resp = New-Object System.IO.StreamReader $req.GetResponse().GetResponseStream(); $resp.ReadToEnd()"') do set ACID=%%b
set CID=%ACID:~27,48%
Echo Confirmation ID: %CID%
Echo %CID%|clip

for /F "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do (set "DEL=%%a")
goto nhap_cid

:nhap_cid
for %%a in (4,5,6) do (
if exist "%ProgramFiles%\Microsoft Office\Office1%%a\ospp.vbs" (cd /d "%ProgramFiles%\Microsoft Office\Office1%%a")
if exist "%ProgramFiles(x86)%\Microsoft Office\Office1%%a\ospp.vbs" (cd /d "%ProgramFiles(x86)%\Microsoft Office\Office1%%a")
)
echo. set /p "CID=NHAP CID:"
cscript ospp.vbs /actcid:%CID%
cscript ospp.vbs /act 

for /F "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do (set "DEL=%%a")
echo DA KICH HOAT THANH CONG BAN QUYEN %YELLOW%%OfficeVersion%%RESET% Hay Sao Luu Lai.
pause
Goto Menu



:sao_luu
cd /d "%~dp0"
set "backupPath=%~dp0Backup"
set /a timeoutSec=5

if not exist "%backupPath%" (
    echo Tao thu muc backup...
    md "%backupPath%" 2>nul
    xcopy "%windir%\System32\spp\store" "%backupPath%\" /e /h /q /y
    echo Da tao thu muc va backup thanh cong.
    pause
    goto Menu
) 

choice /c YN /n /m "Thu muc backup da ton tai ban co muon ghi de? (Y/N): "

if "%errorlevel%"=="2" (
    echo Ban chon: Khong ghi de thu muc.
    echo quay lai Menu chinh sau 5 giay nua.
    timeout /t %timeoutSec%
    Goto Menu
)
if "%errorlevel%"=="1" (
    echo Ban chon: Ghi de thu muc backup.
    echo Bat dau backup...
    echo Dang sao chep cac tap tin...
    xcopy "%windir%\System32\spp\store" "%backupPath%" /e /h /q /y
    pause
    goto Menu
)


:khoi_phuc
cd /d "%~dp0"
cls
set OutDir=Backup
if not exist "%OutDir%" goto restore0

echo TAM DUNG MOT SO DICH VU DE KHOI PHUC KICH HOAT 
net stop sppsvc>nul 2>nul 
net stop osppsvc>nul 2>nul
for /f "tokens=6 delims=[.] " %%a in ('ver') do set ver1=%%a

echo KHOI PHUC TEP TIN GIAY PHEP SU DUNG WINDOWS VA OFFICE

if %ver1% LEQ 7601 (
	XCOPY %OutDir%\SoftwareProtectionPlatform\* %Windir%\ServiceProfiles\NetworkService\AppData\Roaming\Microsoft\SoftwareProtectionPlatform /s /i /y
	goto restore1
)
if %ver1% LEQ 4 (
	XCOPY %OutDir%\* %Windir%\System32\spp\store /s /i /y
	XCOPY %OutDir%\OfficeSoftwareProtectionPlatform\* %ProgramData%\Microsoft\OfficeSoftwareProtectionPlatform  /s /i /y 
	goto restore1
) 
XCOPY %OutDir%\* %Windir%\System32\spp\store /s /i /y
goto restore1

:restore0
Echo KHONG TIM THAY THU MUC SAO LUU BAN QUYEN.

for /F "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do (set "DEL=%%a")
pause
Goto Menu

:restore1
echo DANG KHOI PHUC GIAY PHEP MICROSOFT 
echo KHONG DONG CUA SO NAY! VUI LONG CHO TRONG GIAY LAT.

sc config sppsvc start= auto >nul 2>nul& net start sppsvc >nul 2>nul
sc config osppsvc  start= auto >nul 2>nul& net start osppsvc >nul 2>nul
sc config wuauserv start= auto >nul 2>nul& net start wuauserv >nul 2>nul
sc config LicenseManager start= auto >nul 2>nul& net start LicenseManager >nul 2>nul
cscript %windir%\system32\slmgr.vbs -rilc >nul 2>nul
cscript %windir%\system32\slmgr.vbs -dli >nul 2>nul
cscript %windir%\system32\slmgr.vbs -ato 
for %%a in (4,5,6) do (
if exist "%ProgramFiles%\Microsoft Office\Office1%%a\ospp.vbs" (cd /d "%ProgramFiles%\Microsoft Office\Office1%%a")
if exist "%ProgramFiles(x86)%\Microsoft Office\Office1%%a\ospp.vbs" (cd /d "%ProgramFiles(x86)%\Microsoft Office\Office1%%a")
)
echo  KIEM TRA TRANG THAI GIAY PHEP MICROSOFT
cscript %windir%\system32\slmgr.vbs /dli & cscript %windir%\system32\slmgr.vbs /xpr & cscript ospp.vbs /dstatus

for /F "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do (set "DEL=%%a")
pause
Goto Menu

:thoat
exit
exit
