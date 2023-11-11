@ECHO off

:: Original file from girllife-ecv. https://git.tfgamessite.com/KevinSmarts/girllife-ecv
:: Set those lines to fit your setup.
:: This is where SOB_21_CE.qsp will be copied. If you don't want to move it just comment (::) the line below.
:: set CP_TO=..\GL_ECV

:: This is the program used to open the QSPFILE. If you comment this line windows will launch the default app for the ".qsp" extension.
set QSPGUI=QSP\Player-video\qspgui.exe
set QGEN=QSP\QGen4\QGen.exe

:: The file that will be generated or open
set QSPFILE=SOA.qsp

::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

:menu
cls
echo.
echo :: QSP Compiler and Launcher
echo.

if defined QGEN (
	if not exist "%QGEN%" (
		echo QGEN     : [ERROR] - %QGEN%  not found. Using DEFAULT application.
		set QGEN=
	) else ( echo QGEN     : [OK] - "%QGEN%")
) else echo QGEN     : [NOT DEFINED] - Using DEFAULT application.

if defined QSPGUI (
	if not exist "%QSPGUI%" (
		echo QSP EXEC : [ERROR] - %QSPGUI% not found.
		set QSPGUI=
	) else ( echo QSP EXEC : [OK] - "%QSPGUI%")
) else ( echo QSP EXEC : [NOT DEFINED] - Using Windows DEFAULT.)

if defined QSPFILE (
	if not exist "%QSPFILE%" (
		echo QSP FILE : [WARNING] - %QSPFILE% not found.
	) else ( echo QSP FILE : [OK] - "%QSPFILE%")
) else ( echo QSP FILE : [NOT DEFINED] - ERROR: CAN'T CONTINUE.)

if defined CP_TO (
	if not exist "%CP_TO%" (
		echo COPY     : [ERROR] - Destination "%CP_TO%" not found. Copy DISABLED.
		set CP_TO=
	) else ( echo COPY     : [OK] - "%CP_TO%")
) else (  echo COPY     : [DISABLED] )

echo.

if defined NOT_FOUND (
	echo ERROR: Option '%action%' wasn't recognized. Is it lowercase?
	set NOT_FOUND=
)

echo.
echo ACTIONS: (B)uild .qsp file (G)enerate .qsrc files (C)reate .qproj file (R)un  (F)ull  (Q)Gen (E)xit
echo.
set /p action=Choose an action:

if defined QSPFILE (
	if %action% == b goto build
	if %action% == r goto run
	if %action% == f goto build
	if %action% == q goto qgen
	if %action% == c goto create
	if %action% == g goto generate
)

if %action% == e goto exit

set NOT_FOUND=1
goto menu

:build
echo.
echo Building ...

@ECHO ON
python txtmerge.py translated soa.txt
txt2gam.exe soa.txt %QSPFILE% > nul
@ECHO OFF

echo.
if defined CP_TO ( echo Copying %QSPFILE% to "%CP_TO%" ... & copy %QSPFILE% %CP_TO% > nul )

echo.
echo Done.
pause
if %action% == f ( goto run ) else ( goto menu )

:qgen
echo.
echo Running ...
if defined CP_TO ( start %QGEN% %CP_TO%\%QSPFILE% ) else ( start %QGEN% %QSPFILE% )
goto exit

:run
echo.
echo Running ...

if defined CP_TO ( start %QSPGUI% %CP_TO%\%QSPFILE% ) else ( start %QSPGUI% %QSPFILE% )

:create
echo.
echo Creating .qproj file ...

@ECHO ON
python qprojgen.py translated SOA.qproj
@ECHO OFF

goto menu

:generate
echo.
echo Creating .qsrc files ...

@ECHO ON
python txtsplit_fromtxt.py soa.txt main
@ECHO OFF

goto menu

:exit
