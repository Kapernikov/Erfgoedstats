Deployment procedure voor windows
---------------------------------

Compilen van een windows executable package moet gebeuren op een windows machine.
Volg daarvoor deze stappen:

- installeer python 2.7 (dependencies_windows/python-2.7.2.msi)
- installeer pywin32 (dependencies_windows/pywin32-216.win32-py2.7.exe)

- voer compilePyinstaller.bat uit
- de .exe package bevindt zich in de dist/ folder



Distributie van de .exe op windows
----------------------------------

Kopieer de .exe uit de dist folder uit de vorige stap ergens op een windows pc.
Er hoeft verder niets geinstalleerd te zijn.



Code overview
-------------

NewGUI.py: main program for the GUI version + code of the main window
settings.py: code for the settings dialog and the settings class
aboutdialog.py: the about dialog
adlibstats.py: the code for building a complete report + the main program for the command-line version
htmlutils for writing the html report
utils various utility methods

thesaurus.py for parsing thesauri and generating thesaurus reports
fieldstats.py for basic reports
collectionstats.py for the adlib collection reports

resources: 
	* images converted to python code (for embedding in the GUI and the HTML report using img2py.sh)
	* html resources embedded in python code for the report
	