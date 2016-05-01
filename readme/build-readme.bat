@echo off
setlocal EnableDelayedExpansion

:: setup paths to use
set D=%~dp0
set DIR=%D:~0,-1%

mkdir "%DIR%\..\tmp" >NUL 2>&1
pushd "%DIR%\..\tmp"
set BUILD=%CD%
popd

pushd "%DIR%\..\"
set SRC=%CD%
popd

:: setup virtual environment
py -m venv -h 1>NUL 2>&1
if ERRORLEVEL 0 (
	py -m venv "%BUILD%" 1>NUL 2>&1
	set STATUS=%ERRORLEVEL%
) else (
	set STATUS=%ERRORLEVEL%
) 

if not "!STATUS!" == "0" (
	virtualenv -h >NUL 2>&1
	if ERRORLEVEL 0 (
		pip install virtualenv
		if not ERRORLEVEL 0 (
			set EXIT=%ERRORLEVEL%
			echo Could not install virtualenv
			exit /b !EXIT!
		)
		set INSTALLED_VENV=1

		virtualenv "%BUILD%" 1>NUL 2>&1
	)
)

if not "!STATUS!" == "0" (
	echo Could not create virtual env
	if "!INSTALLED_VENV!"=="1" pip uninstall -y virtualenv
	exit /b !STATUS!
)

call "%BUILD%\scripts\activate.bat"

:: install dependencies
pip install -r "%DIR%\requirements.txt"

:: run pandoc
:: the final slash in the -F parameter must be /
:: see https://github.com/jgm/pandoc/issues/1096
pandoc -f markdown_github+yaml_metadata_block -H "%DIR%\header-include.tex" --listings --number-sections -F "%DIR%/readme-filter.py" -o "%BUILD%\README.tex" "%SRC%\README.markdown" "%DIR%\metadata.yaml"

if not exist "%BUILD%\README.tex" (
	echo Could not find "%BUILD%\README.tex"
	if "!INSTALLED_VENV!"=="1" pip uninstall -y virtualenv
	exit /b 1
)

:: run texify on the resulting output
pushd %BUILD%
texify -b -p --tex-option="--shell-escape" README.tex

if not ERRORLEVEL 0 (
	set EXIT=%ERRORLEVEL%
	popd
	if "!INSTALLED_VENV!"=="1" pip uninstall -y virtualenv
	exit /b !EXIT!
)
popd

copy "%BUILD%\README.pdf" "%SRC%"
rd /q /s "%BUILD%"
if "!INSTALLED_VENV!"=="1" pip uninstall -y virtualenv
echo Build succeeded
exit /b 0
