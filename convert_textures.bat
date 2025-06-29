:: Find out if python is installed
@echo off
where python >nul 2>nul
if %errorlevel% neq 0 (
	echo Python is not installed. Please install Python to run this script.
	exit /b 1
)

:: Make sure exactly two files were supplied
set first_file=%1
set second_file=%2
set third_file=%3
if "%first_file%"=="" goto wrong_args
if "%second_file%"=="" goto wrong_args
if "%third_file%" neq "" goto wrong_args

:: Find out which of the two arguments has the "_diffuse" suffix before .png or .dds
set first_file_name=%~n1
set second_file_name=%~n2
if "%first_file_name:~-8%"=="_diffuse" (
	set diffuse_file=%1
	set normal_file=%2
) else if "%second_file_name:~-8%"=="_diffuse" (
	set diffuse_file=%2
	set normal_file=%1
) else (
	echo Neither of the two files has the _diffuse suffix.
	goto wrong_args
)

:: Now call the python script
python.exe %~dp0/gen_fs25_fillplanes.py "%diffuse_file%" "%normal_file%" 
if %errorlevel% neq 0 (
	echo An error occurred while running the Python script.
	pause
	exit /b 1
)

pause
exit /b 0

:wrong_args
echo You need to drag a diffuse and a normal map onto this script.
pause
exit /b 1