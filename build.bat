@echo off

set innopath="C:\Program Files (x86)\Inno Setup 5"
set pythonpath="buildreqs/WinPython-32bit-2.7.13.1Zero/python-2.7.13"

set python_exe=%pythonpath%\python.exe
set iscc_exe=%innopath%\ISCC.exe
set pyinstaller=%pythonpath%\Scripts\pyinstaller.exe

echo - install requirements
%python_exe% -m pip install pyinstaller -r requirements.txt

echo - pyinstaller build
%pyinstaller% --noconfirm chainsign.spec

echo - Inno Setup build
%iscc_exe% "installer.iss" || goto :error

echo - Finished!
pause
exit 0

:error
echo - Failed!
pause
exit 1
