:: This script builds a windows one file executable package for
:: windows.
:: You need to download and extract pyinstaller in the pyinstaller
:: folder.
:: Also pywin32 needs to be installed. I recommend using python
:: 2.7 as pywin32 had problems installing with python 2.6.
:: Will compress the distributable with UPX if it is installed
:: (to install it, copy upx.exe to C:\WINDOWS\system32)
:: NOTE: you will need at least UPX 1.92 beta due to incompatibilites
:: with the Visual Studio compiler, with which newer versions of
:: python are compiled on windows.
::
:: Remove the --windowed parameter for debugging.

cd pyinstaller

c:\python27\python.exe Configure.py

c:\python27\python.exe Makespec.py --onefile --tk --windowed --upx --name=erfgoedstats ..\src\NewGUI.py

c:\python27\python.exe Build.py erfgoedstats\erfgoedstats.spec

IF NOT EXIST "..\dist" mkdir "..\dist"

copy erfgoedstats\dist\erfgoedstats.exe ..\dist

cd ..
