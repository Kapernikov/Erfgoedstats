#!/bin/python
# -*- coding: utf-8 -*-
'''
New GUI

Created on 26-jul-2011

@author: duststorm
'''
import adlibstats
import webbrowser
import tkFont
import pickle
import utils
import traceback
from thesaurus import setCustomThesauri
from gui import generateReport
# tkinter module was renamed in some python versions
try: from Tkinter import *
except: from tkinter import *
# Override default Tkinter widgets with themed ttk ones (necessary for windows, for GTK they are already themed)
from pyttk import *
# These widgets are by default themed by the OS' window manager
import tkFileDialog
import tkMessageBox

import resources.digiridoologo_base64
import resources.provinciewestvllogo_base64
import resources.ButtonIcons_base64
import resources.logos_provincies
import resources.logos_kapernikovpacked

from inputfiletable import InputFileRow, InputFileTable, TEntries
from settings import Settings, SettingsDialog
import settings


configFile = "erfgoedstats-settings-v1.cfg"


''' this file contains the "main" program for running the GUI + the code for the main window '''
''' The real work is done in the "start" method below '''



class MainWindow:
    def __init__(self, parent):
        self.parent = parent
        
        self.settings = self.loadConfiguration()
        
        self.frame = Frame(parent)
        self.frame.pack(padx=10, pady=10, fill=X, expand=1)
        
        # Menu
        self.menu = Menu(parent)
        mainmenu = Menu(self.menu, tearoff=False)
        mainmenu.add_command(label='Opties / Standaardthesauri', command=self.showOptions)
        mainmenu.add_command(label='Over erfgoedstats', command=self.showAbout)
        mainmenu.add_separator()
        mainmenu.add_command(label='Afsluiten', command=self.quit)
        self.menu.add_cascade(label='Bestand', menu=mainmenu)
        parent.config(menu=self.menu)
        self.parent.protocol("WM_DELETE_WINDOW", self.quit)
        
        
        # Kies museum naam
        self.museumnaamFrame = Frame(self.frame)
        self.museumnaamFrame.pack(pady=5, fill=X, expand=1)
        font = tkFont.Font(weight="bold")
        museumnaamLabel = Label(self.museumnaamFrame, text="Naam collectie: ", font=font, anchor=W)
        museumnaamLabel.pack(side=LEFT, pady=15)
        self.museumnaamField = Entry(self.museumnaamFrame)
        self.museumnaamField.pack(side=LEFT, fill=X, expand=1)
        
        ## Input files ##
        font = tkFont.Font(weight="bold")
        inputsLabel = Label(self.frame, text="Input bestanden: ", anchor=W, font=font)
        inputsLabel.pack(pady=5, fill=X, expand=1)
        self.inputFilesTable = InputFileTable(self.frame, nameColumn=False,settings=self.settings, tabletype="objects")
        self.inputFilesTable.setAvailableTypes( settings.inputfile_types )
        # Set default input rows
        self.inputFilesTable.addRow(name="Objecten", filetype='Adlib XML Objecten')
        self.inputFilesTable.addRow(name="Thesaurus", filetype='Adlib XML Thesaurus')
        self.inputFilesTable.addRow(name="Personen", filetype='Adlib XML Personen')
        
        # Input file toevoegen knop
        self.addRowButton = Button(self.frame, image=resources.ButtonIcons_base64.add, text="Bestand toevoegen", compound=LEFT, command=self.addInputRow)
        self.addRowButton.pack(pady=5)
        
        # Kies output file
        self.outputFrame = Frame(self.frame)
        self.outputFrame.pack(pady=5, fill=X, expand=1)
        font = tkFont.Font(weight="bold")
        outputLabel = Label(self.outputFrame, text="Output: ", anchor=W, font=font)
        outputLabel.pack(side=LEFT)
        self.outputField = Entry(self.outputFrame)
        self.outputButton = Button(self.outputFrame, text="Bladeren", command=self.browseOutputFile)
        self.outputField.pack(side=LEFT, fill=X, expand=1)
        self.outputButton.pack(side=RIGHT, padx=5)
        
        # Vergelijk met thesauri optie
        self.frame4 = Frame(self.frame)
        self.frame4.pack(pady=10, fill=X, expand=1)
        self.checkThesaurus = IntVar()
        self.checkb = Checkbutton(self.frame4, variable=self.checkThesaurus)
        self.updateThesauriCheckbox()
        self.checkb.pack(side=LEFT, padx=5)
        
        ## Start button ##
        self.startButton = Button(self.frame, text="Start", command=self.start)
        self.startButton.pack(side=BOTTOM)
        utils.centerWindow(self.parent)
    
    def addInputRow(self):
        self.inputFilesTable.addRow()
    
    def browseOutputFile(self):
        defaultDir = self.settings.getPath("output")
        filename = tkFileDialog.asksaveasfilename(title="Waar wilt u het resultaat opslaan?", filetypes=[("HTML bestand", "*.html")], defaultextension=".html", initialdir=defaultDir)
        # Remove current text and replace with selected filename
        self.outputField.delete(0, END)
        self.outputField.insert(0, filename)
        self.settings.setPath("output",os.path.dirname(filename))
        
    def showOptions(self):
        s = SettingsDialog(self)
        s.show()
    
    def showAbout(self):
        import aboutdialog
        a = aboutdialog.AboutDialog(self)
        a.show()
        
    def start(self):
        museumName = self.museumnaamField.get()
        museumName = utils.ensureUnicode(museumName)
        if not museumName.strip():
            tkMessageBox.showerror('Geen naam voor de collectie opgegeven', 'Vul de naam van de collectie in, aub.');
            return
        outputFile = self.outputField.get()
        if not isValidOutputFile(outputFile):
            tkMessageBox.showerror('Fout bij het starten', 'Kon niet starten omdat er geen correct "Output" bestand is opgegeven.');
            return
        if os.path.exists(outputFile):
            doOverwrite = tkMessageBox.askyesno('Bestand overschrijven?', 'Het gekozen "Output" bestand bestaat reeds. Wilt u verder gaan en het overschrijven?')
            if not doOverwrite:
                return

        try:
            waitDialog = WaitDialog(self.parent)
            utils.setMaxDetail(self.settings.maxUniqueValues)
            # Will only return input files with valid files and names filled in
            inputFiles = self.inputFilesTable.getValues()
            if inputFiles.size() == 0:
                waitDialog.close()
                tkMessageBox.showerror('Fout bij het starten', u'Kon niet starten omdat er geen geldige "Input" bestanden zijn opgegeven.\nEr is minstens één input bestand met ingevulde naam, type en bestandslocatie vereist.');
                return

            if self.checkb["state"] != DISABLED and self.checkThesaurus.get():
                checkThesaurus = True
            else:
                checkThesaurus = False

            # Set configured reference thesauri
            err = None
            if (checkThesaurus):
                referenceThesauri = self.settings.thesauri
                err = setCustomThesauri(referenceThesauri)
            else:
                err = setCustomThesauri(TEntries())
            if (not (err is None)):
                waitDialog.close()
                tkMessageBox.showerror('Fout bij het starten', err);
                return
                
            # Set specified input files to analyse
            objects = []
            thesauri = []
            fieldstats = []
            csvfieldstats = []
            inputFiles.sort()
            for entry in inputFiles.values:
                utils.s("%s - %s - %s\n" % (entry.name, entry.type, entry.path))
                if entry.type == 'Adlib XML Objecten':
                    objects.append(entry.path)
                elif entry.type == 'XML Fieldstats' or entry.type == "Adlib XML Personen":
                    fieldstats.append(entry.path)
                elif entry.type == 'CSV Fieldstats':
                    csvfieldstats.append(entry.path)
                elif entry.type == 'Adlib XML Thesaurus':
                    thesauri.append(entry.path)
                else:
                    print "ERROR: Input bestand %s met type %s kan niet gebruikt worden" % (entry.name, entry.type)
            generateReport(museumName, objects, thesauri, fieldstats, csvfieldstats, outputFile, False)
                 
        except Exception, e:
            waitDialog.close()
            stacktrace = traceback.format_exc()
            print "exception ..."
            print stacktrace
            print "done"
            ExceptionDialog(self.parent, e, stacktrace)
            return
        
        waitDialog.close()
        
        showHtml = tkMessageBox.askyesno('Verwerking voltooid', 'De verwerking van de gegevens is gelukt. Wilt u het resultaat bekijken?')
        if showHtml:
            webbrowser.open(outputFile)

        return
    

        
    def loadConfiguration(self):
        '''Load saved configuration of app. If the config file is
        not found or cannot be read, a new settings object is returned
        with defaults. Settings will be validated and are assured not to
        contain thesauri for which the file does not exist.'''
        if not os.path.exists(configFile):
            return settings.getDefaultSettings()
        try:
            unpickler = pickle.Unpickler(open(configFile, 'rb'))
            msettings = unpickler.load()
            if not isinstance(msettings, Settings):
                return msettings.getDefaultSettings()
            msettings.validate()
            utils.s("* Loaded previously saved settings.")
            return msettings
        except:
            utils.s(" --> Error loading saved settings.")
            return settings.getDefaultSettings()
        
    def saveConfiguration(self):
        if not isinstance(self.settings, Settings):
            utils.s("* Error saving settings (nothing to save)")
            return
        try:
            pickler = pickle.Pickler(open(configFile, 'wb'))
            pickler.dump(self.settings)
        except:
            utils.s("* Error: could not save configuration to file %s" % configFile)
            return
    
    def getConfiguredReferenceThesauri(self):
        return self.settings.thesauri
    
    def updateReferenceThesauri(self, thesaurus):
        self.settings.thesauri = thesaurus
        self.updateThesauriCheckbox()
        self.saveConfiguration()
            
    def updateThesauriCheckbox(self):
        availableThesauri =self.getConfiguredReferenceThesauri()
        if(len(availableThesauri.values) > 0):
            checkbState = NORMAL
            self.checkThesaurus.set(1)
        else:
            checkbState = DISABLED
            self.checkThesaurus.set(0)
        self.checkb.config(state=checkbState, text="Vergelijken met standaard thesauri" )
        
    def quit(self):
        print "Quitting, saving config."
        self.saveConfiguration()
        self.frame.quit()
        self.parent.quit()
        

class WaitDialog:
    def __init__(self, parent):
        self.top = Toplevel(parent, takefocus=True)
        self.top.wm_attributes("-topmost", True)
        self.top.title('Bezig met verwerken')
        Label(self.top, text="Even geduld, de gegevens worden verwerkt.").pack(padx=10, pady=10, fill=X, expand=1)
        # Focus and center
        utils.centerWindow(self.top)
        self.top.focus_set()
        self.top.grab_set()
        self.top.update()

    def close(self):
        self.top.destroy()
        
class ExceptionDialog:
    '''Shows an exception message with detailed stacktrace. User has the option
    to copy the stacktrace to clipboard for mailing it to the developers.
    
    to give a userfriendly error message, raise a utils.UserError instead of another exeption.
    this way, the message shown to the user can be controlled.
    '''
    def __init__(self, parent, e, stacktrace):
        self.stacktrace = stacktrace
        self.e = e
        self.top = Toplevel(parent, takefocus=True)
        self.top.wm_attributes("-topmost", True)
        self.top.title('Fout')
        # User understandable message
        errorTXT = "Er heeft zich een fout voorgedaan.\nHieronder vindt u een gedetailleerde beschrijving van de fout.\nGelieve deze te rapporteren door ze te kopiëren en in een email bericht te plakken."
        if (isinstance(e, utils.UserError)):
            errorTXT = e.msg
            self.stacktrace = "%s\n\n\nROOT CAUSE:\n %s" % (e.msg, e.stacktrace)  + "\n\n" + self.stacktrace
        userMsg = Label(self.top, text=errorTXT, anchor=W)
        userMsg.config(justify=LEFT)
        userMsg.pack(padx=10, pady=10, fill=X, expand=1)
        # Stacktrace frame
        self.stacktraceFrame = Frame(self.top)
        self.stacktraceFrame.pack(padx=10, pady=10, fill=BOTH, expand=1)
        self.stacktraceBox = Text(self.stacktraceFrame)
        self.stacktraceBox.pack(fill=BOTH, expand=1, side=LEFT)
        self.stacktraceBox.insert(END, self.stacktrace)
        self.stacktraceBox.config(state=DISABLED) # Prohibit any further changes to the textbox
        try:
            scroll = Scrollbar(self.stacktraceFrame)
            scroll.pack(side=RIGHT, fill=Y, expand=1)
            scroll.config(command=self.stacktraceBox.yview)
            self.stacktraceBox.config(yscrollcommand=scroll.set)
        except:
            ''' doesnt work on macosx'''
            pass
        # Copy to clipboard button
        self.clipbCopyButton = Button(self.top, text=u"Kopiëer naar klembord", command=self.copyStacktraceToClipboard)
        self.clipbCopyButton.pack(pady=10)
        # Ok button
        self.buttonsFrame = Frame(self.top)
        self.buttonsFrame.pack(fill=X, expand=1, padx=10, pady=10)
        self.okButton = Button(self.buttonsFrame, text="Ok", command=self.close)
        self.okButton.pack(side=RIGHT)
        # Focus and center
        utils.centerWindow(self.top)
        self.top.focus_set()
        self.top.grab_set()
        self.top.update()
        # Let the rest of the GUI wait until this dialog is closed
        parent.wait_window(self.top)

    def copyStacktraceToClipboard(self):
        self.top.clipboard_clear()
        self.top.clipboard_append(self.stacktrace)
        tkMessageBox.showinfo(u"Beschrijving naar klembord gekopiëerd", u'De gedetailleerde foutbeschrijving is naar het klembord gekopiëerd.\n\nGelieve een email te sturen naar support@digiridoo.be met een beschrijving van uw instellingen en de invoerbestanden die u gebruikte.\nPlak ook de foutboodschap die in uw klembord staat in de mail (dat doet u door in het tekstveld van de email op de rechtermuisknop te klikken en "Plakken" te selecteren.', parent=self.top)

    def close(self):
        self.top.destroy()
        
def generateReport(museumName, objects, thesaurus, fieldstats, csvfieldstats, outputFile, checkThesaurus):
    'TODO: Moet ik ook unicode encoding toepassen op filenames?? voordeel is dat ik dan filenames met vreemde tekens ondersteun, nadeel is dat als OS bijvoorbeeld geen UTF8 filenames ondersteunt dat het wel eens mis kan gaan.'
    inputDataMap = {"name" : museumName, 
                    "objects" : objects, 
                    "thesaurus" : thesaurus, 
                    "fieldstats" : fieldstats,
                    "csvfieldstats": csvfieldstats }
    'TODO: missch verbose op false zetten'
    adlibstats.generateReportFile(outputFile, inputDataMap, False, True, True)


def isValidOutputFile(filename):
    '''Reports whether this is a valid filename for writing output to.'''
    if not isinstance(filename, basestring):
        return False
    filename = filename.strip()
    if filename:
        return True
    else:
        return False

   

        

def main():
    '''Run the GUI'''
    root= Tk()
    root.title('Erfgoedstats')
    
    # Populate window with widgets
    window = MainWindow(root)
    
    # Run main event loop
    root.mainloop()
    



if __name__ == '__main__':
    main()