@echo off

set innopath="C:\Program Files (x86)\Inno Setup 6"
set pythonpath="buildreqs\python381\"

set python_exe=%pythonpath%\python.exe
set iscc_exe=%innopath%\ISCC.exe
set pyinstaller=%pythonpath%\Scripts\pyinstaller.exe

echo - install requirements
%python_exe% -m pip install poetry
%python_exe% -m poetry install

echo - pyinstaller build
%python_exe% -m poetry run pyinstaller --noconfirm chainsign.spec

echo - Inno Setup build
%iscc_exe% "installer.iss" || goto :error

echo - Finished!
pause
exit 0

:error
echo - Failed!
pause
exit 1
