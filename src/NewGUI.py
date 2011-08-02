#!/bin/python
# -*- coding: utf-8 -*-
'''
New GUI

Created on 26-jul-2011

@author: duststorm
'''
import Tkinter,tkFileDialog,tkMessageBox
import os
import adlibstats
import codecs
import webbrowser
import tkFont
import pickle
import utils
import thesaurus
from thesaurus import setCustomThesauri
from gui import generateReport

configFile = "../settings.cfg"

'''Filetypes that are selectable from the input file tables'''
thesaurus_types = thesaurus.valid_filetypes
inputfile_types = ['Adlib XML Objecten', 'Adlib XML Thesaurus', 'XML Fieldstats', 'CSV Fieldstats']

class InputFileTable:
    '''GUI Widget that allows for defining a table in which each row represents an input file.
    Each row or input file has a name, a filetype, and a filepath. Optionally a fixed order of
    rows can be maintained.'''
    def __init__(self, parent, nameColumn=True):
        self.parent = parent
        self.frame = Tkinter.Frame(parent)
        self.availableTypes = []
        self.rows = []
        self.nameColumn=nameColumn
        # Init table header
        self.tableHeader = Tkinter.Frame(self.frame)
        self.tableHeader.pack(fill=Tkinter.X, expand=1)
        if nameColumn:
            nameheader = Tkinter.Label(self.tableHeader, text="Naam", width=15)
            nameheader.pack(side=Tkinter.LEFT, padx=5)
        typeheader = Tkinter.Label(self.tableHeader, text="Type", width=19)
        typeheader.pack(side=Tkinter.LEFT, padx=5)
        pathheader = Tkinter.Label(self.tableHeader, text="Bestandslocatie", width=20)
        pathheader.pack(side=Tkinter.LEFT, padx=5)
        # Frame containing the entries
        self.entries = Tkinter.Frame(self.frame)
        self.entries.pack(fill=Tkinter.X, expand=1)
        self.frame.pack(fill=Tkinter.BOTH, expand=1)
        
    def addRow(self, name="", filetype="", filepath=""):
        '''Add a row for a file to this table.'''
        InputFileRow(self, name, filetype, filepath, self.nameColumn)

    def setAvailableTypes(self, typesList):
        '''Sets the types that will be selectable from the type dropdown.
        Any previously set types will be overwritten. Call this method before
        adding any rows to the table.'''
        self.availableTypes = typesList
        
    def getAvailableFiletypes(self):
        '''Returns all types that are selectable from the type dropdown.'''
        if not self.availableTypes or not isinstance(self.availableTypes, list) or len(self.availableTypes) == 0:
            return ['default']
        return self.availableTypes
    
    def getValues(self):
        '''Returns the values of all rows set in this table as a dict. The result will be of the form:
        result[name]={ "type": type, "path": path, "order": order }
        If the same name is used more than once, subsequent names will be renamed to "name#i" with i 
        an incremental number starting from 1. Order defines the order of the rows within the table widget.
        Only entries with a valid path and type will be returned.'''
        result = dict()
        order = 0
        for inputFileRow in self.rows:
            name = utils.ensureUnicode(inputFileRow.getName())
            type = utils.ensureUnicode(inputFileRow.getType())
            path = utils.ensureUnicode(inputFileRow.getPath())
            if not os.path.exists(path):
                continue
            if type not in self.getAvailableFiletypes():
                continue
            # Name is only required if table shows a name column, otherwise name defaults to order nb
            if not name:
                if self.nameColumn:
                    continue
                else:
                    name=order
            if name not in result:
                result[name] = { "type": type, "path": path, "order": order }
            else:
                i = 1
                while name+"#"+str(i) in result:
                    i = i+1
                result[name+"#"+str(i)] = { "type": type, "path": path, "order": order }
            order = order+1
        return result
    
    def addRows(self, rowValues):
        '''Add rows to this table using rowValues, which should be the same format as is
        returned when calling getValues(). Only rows will be added that have files that exist
        and that have a type that is available for this table.'''
        if not isinstance(rowValues, dict):
            return
        if(dictContainsOrder(rowValues)):
            # An order is defined, use it in this table
            orderedRowsList = getDictAsOrderedList(rowValues)
            for entry in orderedRowsList:
                if "type" not in entry or "path" not in entry or "name" not in entry:
                    continue
                name = entry["name"]
                type = entry["type"]
                path = entry["path"]
                if not os.path.exists(path) or type not in self.getAvailableFiletypes():
                    continue
                self.addRow(name, type, path)
        else:
            # No order is defined, just add rows in name order
            for name in rowValues:
                entry = rowValues[name]
                if "type" not in entry or "path" not in entry:
                    continue
                type = entry["type"]
                path = entry["path"]
                if not os.path.exists(path) or type not in self.getAvailableFiletypes():
                    continue
                self.addRow(name, type, path)
        
class InputFileRow:
    def __init__(self, parentTable, name, filetype, filepath, nameColumn=True):
        self.table = parentTable
        self.parent = parentTable.entries
        self.frame = Tkinter.Frame(self.parent)
        self.frame.pack(fill=Tkinter.X, expand=1)
        self.nameColumn = nameColumn
        if not filetype or not filetype in self.table.getAvailableFiletypes():
            filetype = self.table.getAvailableFiletypes()[0]
        
        # Name column
        if(nameColumn):
            self.nameField = Tkinter.Entry(self.frame, width=15)
            self.nameField.pack(side=Tkinter.LEFT)
            if name and isinstance(name, basestring):
                self.nameField.insert(0, name)
        # Type column
        self.filetype = Tkinter.StringVar()
        self.filetype.set(filetype)
        self.typeSelect = Tkinter.OptionMenu(self.frame, self.filetype, *self.table.getAvailableFiletypes())
        self.typeSelect["width"] = 15
        self.typeSelect.pack(side=Tkinter.LEFT, padx=5)
        # Path column
        self.pathField = Tkinter.Entry(self.frame, width=20)
        self.pathField.pack(side=Tkinter.LEFT, fill=Tkinter.X, expand=1, padx=5)
        if filepath and isinstance(filepath, basestring):
            self.pathField.insert(0, filepath)
        # Browse button
        self.browseButton = Tkinter.Button(self.frame, text="Bladeren", command=self.browseFile)
        self.browseButton.pack(side=Tkinter.LEFT, padx=5)
        # Remove row button
        self.removeButton = Tkinter.Button(self.frame, text="-", command=self.remove)
        self.removeButton.pack(side=Tkinter.LEFT)
        # Add to rows list
        parentTable.rows.append(self)
        
    def browseFile(self):
        filename = ""
        filetype = self.getType()
        if filetype == 'Adlib XML Objecten':
            filename = tkFileDialog.askopenfilename(title="Kies Adlib XML met objecten", initialdir="../data/musea/", defaultextension="*.xml", parent=self.parent)
        if filetype == 'Adlib XML Thesaurus':
            filename = tkFileDialog.askopenfilename(title="Kies Adlib XML met een thesaurus", initialdir="../data/musea/", defaultextension="*.xml", parent=self.parent)
        if filetype == 'TXT Thesaurus':
            filename = tkFileDialog.askopenfilename(title="Kies bestand met TXT thesaurus", initialdir="../data/musea/", defaultextension="*.txt", parent=self.parent)
        if filetype == 'XML Fieldstats':
            filename = tkFileDialog.askopenfilename(title="Kies Adlib XML voor fieldstats", initialdir="../data/musea/", defaultextension="*.xml", parent=self.parent)
        if filetype == 'CSV Fieldstats':
            filename = tkFileDialog.askopenfilename(title="Kies CSV bestand voor fieldstats", initialdir="../data/musea/", defaultextension="*.csv", parent=self.parent)

        if not isValidFile(filename):
            return
        # In path field, remove current text and replace with selected filename
        self.pathField.delete(0, Tkinter.END)
        self.pathField.insert(0, filename)
        'TODO: zijn XML objecten en XML fieldstats hetzelfde?'
        
        'TODO: zijn deze beschikbaar? of worden die gewoon als standaard fieldstats ingeladen?'
        '''
        if self.filetype == 'TXT Thesaurus':
        if self.filetype == 'CSV Thesaurus':
        if self.filetype == 'TXT Objecten':
        if self.filetype == 'CSV Objecten':
        '''
        'TODO: zoek uit welke verschillende typen er juist zijn, is bv thesaurus of objects als gewone fieldstat in te laden?'
        
    def remove(self):
        self.table.rows.remove(self)
        self.frame.destroy()
        
    def getName(self):
        if self.nameColumn:
            return utils.ensureUnicode(self.nameField.get())
        else:
            return ""
        
    def getType(self):
        return utils.ensureUnicode(self.filetype.get())
        
    def getPath(self):
        return utils.ensureUnicode(self.pathField.get()) 

class MainWindow:
    def __init__(self, parent):
        self.parent = parent
        
        self.settings = self.loadConfiguration()
        
        self.logoFrame = Tkinter.Frame(parent)
        self.logoFrame.pack(side=Tkinter.TOP, fill=Tkinter.BOTH, expand=1)
        
        self.frame = Tkinter.Frame(parent)
        self.frame.pack(padx=10, pady=10, fill=Tkinter.X, expand=1)
        
        # Menu
        self.menu = Tkinter.Menu(parent)
        mainmenu = Tkinter.Menu(self.menu, tearoff=False)
        mainmenu.add_command(label='Opties', command=self.showOptions)
        mainmenu.add_separator()
        mainmenu.add_command(label='Afsluiten', command=self.quit)
        self.menu.add_cascade(label='Menu', menu=mainmenu)
        parent.config(menu=self.menu)
        self.parent.protocol("WM_DELETE_WINDOW", self.quit)
        
        ## LOGOs ##
        digiridooImg = Tkinter.PhotoImage("Digiridoo logo", file="images/logo-blue-143.gif")
        digiridooLogo = Tkinter.Label(self.logoFrame, image=digiridooImg)
        digiridooLogo.photo = digiridooImg 
        digiridooLogo.pack(side=Tkinter.LEFT, padx=10, pady=10)
        
        provincieWestVlImg = Tkinter.PhotoImage("Provincie West Vlaanderen logo", file="images/logo_pwv.gif")
        provincieWestVlLogo = Tkinter.Label(self.logoFrame, image=provincieWestVlImg)
        provincieWestVlLogo.photo = provincieWestVlImg
        provincieWestVlLogo.pack(side=Tkinter.RIGHT, padx=10)
        
        # Kies museum naam
        self.museumnaamFrame = Tkinter.Frame(self.frame)
        self.museumnaamFrame.pack(pady=5, fill=Tkinter.X, expand=1)
        font = tkFont.Font(weight="bold")
        museumnaamLabel = Tkinter.Label(self.museumnaamFrame, text="Museum naam: ", font=font, anchor=Tkinter.W)
        museumnaamLabel.pack(side=Tkinter.LEFT, pady=15)
        self.museumnaamField = Tkinter.Entry(self.museumnaamFrame)
        self.museumnaamField.pack(side=Tkinter.LEFT, fill=Tkinter.X, expand=1)
        
        ## Input files ##
        font = tkFont.Font(weight="bold")
        inputsLabel = Tkinter.Label(self.frame, text="Input bestanden: ", anchor=Tkinter.W, font=font)
        inputsLabel.pack(pady=5, fill=Tkinter.X, expand=1)
        self.inputFilesTable = InputFileTable(self.frame, nameColumn=False)
        self.inputFilesTable.setAvailableTypes( inputfile_types )
        # Set default input rows
        self.inputFilesTable.addRow(name="Objecten", filetype='Adlib XML Objecten')
        self.inputFilesTable.addRow(name="Thesaurus", filetype='Adlib XML Thesaurus')
        
        # Input file toevoegen knop
        self.addRowButton = Tkinter.Button(self.frame, text="+", command=self.addInputRow)
        self.addRowButton.pack(pady=5)
        
        # Kies output file
        self.outputFrame = Tkinter.Frame(self.frame)
        self.outputFrame.pack(pady=5, fill=Tkinter.X, expand=1)
        font = tkFont.Font(weight="bold")
        outputLabel = Tkinter.Label(self.outputFrame, text="Output: ", anchor=Tkinter.W, font=font)
        outputLabel.pack(side=Tkinter.LEFT)
        self.outputField = Tkinter.Entry(self.outputFrame)
        self.outputButton = Tkinter.Button(self.outputFrame, text="Bladeren", command=self.browseOutputFile)
        self.outputField.pack(side=Tkinter.LEFT, fill=Tkinter.X, expand=1)
        self.outputButton.pack(side=Tkinter.RIGHT, padx=5)
        
        # Vergelijk met thesauri optie
        self.frame4 = Tkinter.Frame(self.frame)
        self.frame4.pack(pady=10, fill=Tkinter.X, expand=1)
        self.checkThesaurus = Tkinter.IntVar()
        self.checkb = Tkinter.Checkbutton(self.frame4, variable=self.checkThesaurus)
        self.updateThesauriCheckbox()
        self.checkb.pack(side=Tkinter.LEFT, padx=5)
        
        ## Start button ##
        self.startButton = Tkinter.Button(self.frame, text="Start", command=self.start)
        self.startButton.pack(side=Tkinter.BOTTOM)
        centerWindow(self.parent)
    
    def addInputRow(self):
        self.inputFilesTable.addRow()
    
    def browseFile(self, inputField, title, initialdir, defaultExt=None, filetypes=None, isOutputFile=False):
        '''TODO: maybe filter for filetype'''
        if defaultExt:
            filename = tkFileDialog.askopenfilename(title=title, defaultextension=defaultExt, initialdir=initialdir)
        elif filetypes:
            filename = tkFileDialog.askopenfilename(title=title, filetypes=filetypes, initialdir=initialdir)
        else:
            filename = tkFileDialog.askopenfilename(title=title, initialdir=initialdir)
        if isOutputFile:
            if not isValidOutputFile(filename):
                return
        else:
            if not isValidFile(filename):
                return
        # Remove current text and replace with selected filename
        inputField.delete(0, Tkinter.END)
        inputField.insert(0, filename)
        return
    
    def browseOutputFile(self):
        self.browseFile(self.outputField, "Waar wilt u het resultaat opslaan?", "../out/", filetypes=[("HTML bestand", "*.html")], isOutputFile=True)
        
    def showOptions(self):
        '''Show the settings dialog'''
        SettingsDialog(self)
        
    def start(self):
        museumName = self.museumnaamField.get()
        museumName = utils.ensureUnicode(museumName)
        if not museumName.strip():
            tkMessageBox.showerror('Geen naam voor museum opgegeven', 'Vul de naam van het museum in, aub.');
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
            # Will only return input files with valid files and names filled in
            inputFiles = self.inputFilesTable.getValues()
            if len(inputFiles.keys()) == 0:
                waitDialog.close()
                tkMessageBox.showerror('Fout bij het starten', u'Kon niet starten omdat er geen geldige "Input" bestanden zijn opgegeven.\nEr is minstens één input bestand met ingevulde naam, type en bestandslocatie vereist.');

            if self.checkb["state"] != Tkinter.DISABLED and self.checkThesaurus.get():
                checkThesaurus = True
            else:
                checkThesaurus = False

            # Set configured reference thesauri
            referenceThesauri = getDictAsOrderedList(self.settings.thesauri)
            setCustomThesauri(referenceThesauri)
            
            # Set specified input files to analyse
            objects = []
            thesauri = []
            fieldstats = []
            csvfieldstats = []
            for name in inputFiles.keys():
                utils.s("%s - %s - %s\n" % (name, inputFiles[name]['type'], inputFiles[name]['path']))
                if inputFiles[name]["type"] == 'Adlib XML Objecten':
                    objects.append(inputFiles[name]["path"])
                elif inputFiles[name]["type"] == 'XML Fieldstats':
                    fieldstats.append(inputFiles[name]["path"])
                elif inputFiles[name]["type"] == 'CSV Fieldstats':
                    csvfieldstats.append(inputFiles[name]["path"])
                elif inputFiles[name]["type"] == 'Adlib XML Thesaurus':
                    thesauri.append(inputFiles[name]["path"])
                else:
                    print "ERROR: Input bestand %s met type %s kan niet gebruikt worden" % (name, inputFiles[name]["type"])
                generateReport(museumName, objects, thesauri, fieldstats, csvfieldstats, outputFile, checkThesaurus)
                 
        except IOError, e:
            waitDialog.close()
            raise e
            tkMessageBox.showerror("Fout", "Er ging iets mis bij het verwerken van de gegevens.\n(Beschrijving van de fout: %s)" % str(e))
            'TODO: toon stacktrace in venster'
        
        waitDialog.close()
        
        showHtml = tkMessageBox.askyesno('Verwerking voltooid', 'De verwerking van de gegevens is gelukt. Wilt u het resultaat tonen?')
        if showHtml:
            webbrowser.open(outputFile)

        return
    
#        tkMessageBox.showinfo("Bezig met verwerken", "Even geduld, de gegevens worden verwerkt.", parent=self.parent)
        #d = WaitDialog(self.parent)
        #d.top.update()
        #self.parent.wait_window(d.top)
        '''
        height = self.frame.winfo_height()
        width = self.frame.winfo_width()
        self.frame.pack_forget()
        waitLabel = Tkinter.Label(self.parent, text="Even geduld, de gegevens worden verwerkt.", height=height, width=width)
        waitLabel.pack(padx=10, pady=10)
        self.parent.update()
        '''
        objecten = self.inputField1.get()
        thesaurus = self.inputField2.get()
        outfile = self.inputField3.get()
        try:
            generateReport(objecten, thesaurus, outfile, self.checkThesaurus)
        except Exception, e:
            tkMessageBox.showerror("Fout", "Er ging iets mis bij het verwerken van de gegevens.\n(Beschrijving van de fout: %s)" % str(e))
            raise e     
        'TODO: show result in web browser?'
        showHtml = tkMessageBox.askyesno('Verwerking voltooid', 'De verwerking van de gegevens is gelukt. Wil je het resultaat tonen?')
        if showHtml:
            webbrowser.open(outfile)
        '''
        waitLabel.destroy()
        self.frame.pack()
        '''
        
    def loadConfiguration(self):
        '''Load saved configuration of app. If the config file is
        not found or cannot be read, a new settings object is returned
        with defaults. Settings will be validated and are assured not to
        contain thesauri for which the file does not exist.'''
        if not os.path.exists(configFile):
            return getDefaultSettings()
        try:
            unpickler = pickle.Unpickler(open(configFile, 'rb'))  #codecs.open(configFile,'ru', encoding="utf-8" ,errors="ignore"))
            settings = unpickler.load()
            if not isinstance(settings, Settings):
                return getDefaultSettings()
            settings.validate()
            print "Loaded previously saved settings."
            return settings
        except:
            print "Error loading saved settings."
            return getDefaultSettings()
        
    def saveConfiguration(self):
        if not isinstance(self.settings, Settings):
            print "error saving settings"
            return
        try:
            pickler = pickle.Pickler(open(configFile, 'wb'))  #codecs.open(configFile,'wu', encoding="utf-8" ,errors="ignore"))
            pickler.dump(self.settings)
        except:
            print "Error: could not save configuration to file %s" % configFile
            return
    
    def getConfiguredReferenceThesauri(self):
        '''Returns a dict with the standard thesauri currently configured for the app. The dict is
        formatted as described in Settings.getReferenceThesauri()'''
        return self.settings.thesauri
    
    def updateReferenceThesauri(self, thesaurus):
        self.settings.thesauri = thesaurus
        self.updateThesauriCheckbox()
            
    def updateThesauriCheckbox(self):
        availableThesauri = self.getConfiguredReferenceThesauri().keys()
        if(len(availableThesauri) > 0):
            availableThesauri = ', '.join(availableThesauri)
            checkbState = Tkinter.NORMAL
        else:
            checkbState = Tkinter.DISABLED
            availableThesauri = "Geen thesauri gevonden"
        self.checkb.config(state=checkbState, text="Vergelijken met standaard thesauri (%s)" % availableThesauri)
        
    def quit(self):
        print "Quitting, saving config."
        self.saveConfiguration()
        self.frame.quit()
        self.logoFrame.quit()
        self.parent.quit()
        
def getDefaultSettings():
    '''Return an initial default settings object.
    Will try adding the default thesauri to the settings. Only existing files will be added.'''
    settings= Settings()
    settings.addReferenceThesaurus('Mot', '../data/MOT/mot-naam.txt', 'TXT Thesaurus')
    settings.addReferenceThesaurus('Am-Move', '../data/reference/Am_Move_thesaurus06_10.xml', 'Adlib XML Thesaurus')
    settings.addReferenceThesaurus('AAT-Ned', '../data/reference/aat2000.xml', 'Adlib XML Thesaurus')
    print "Loaded initial default settings."
    return settings
        
class Settings:
    def __init__(self):
        self.thesauri = dict()
        
    def addReferenceThesaurus(self, thesaurusName, thesaurusPath, type):
        '''Add reference thesaurus with specified name, path and type to
        to the settings. If the file does not exist or its type is not
        known it is not added.'''
        thesaurusName = utils.ensureUnicode(thesaurusName)
        'TODO: is it safe to convert filenames to unicode?'
        thesaurusPath = utils.ensureUnicode(thesaurusPath)
        type = utils.ensureUnicode(type)
        if not os.path.exists(thesaurusPath):
            return
        if not type in thesaurus_types:
            return
        self.thesauri[thesaurusName] = {"path": thesaurusPath, "type": type, "order": len(self.thesauri)}
        
    def removeReferenceThesaurus(self, thesaurusName):
        '''Removes the thesaurus with specified name if it exists'''
        thesaurusName = utils.ensureUnicode(thesaurusName)
        if thesaurusName in self.thesauri:
            del self.thesauri[thesaurusName]
        
    def validate(self):
        '''Remove all all thesauri for which the file doesnt exist,
        that dont contain the required field "path" and "type", or
        that have an unknown type from the list.'''
        for thesaurusName in self.thesauri.keys():
            thesaurus = self.thesauri[thesaurusName]
            if 'path' not in thesaurus or 'type' not in thesaurus:
                del self.thesauri[thesaurusName]
            path = thesaurus["path"]
            type = thesaurus["type"]
            if not os.path.exists(path) or type not in thesaurus_types:
                del self.thesauri[thesaurusName]
    
    def getReferenceThesauri(self):
        '''Determine which reference thesauri are configured and their locations.
        The returned result is a dict with thesaurus name as key, and a thesaurus dict
        as value. This thesaurus dict has "type" and "path" values'''
        return self.thesauri

class SettingsDialog:
    def __init__(self, mainWindow):
        self.mainWindow = mainWindow
        self.window = Tkinter.Toplevel(takefocus=True)
        self.window.wm_attributes("-topmost", True)
        self.window.title('Instellingen')
        self.frame = Tkinter.Frame(self.window)
        self.frame.pack(fill=Tkinter.BOTH, expand=1, padx=10, pady=10)
        font = tkFont.Font(weight="bold")
        label = Tkinter.Label(self.frame, text='Standaard (referentie) thesauri: ', anchor=Tkinter.W, font=font)
        label.pack(pady=5, fill=Tkinter.X, expand=1)
        # Create an input file table for specifying the thesauri and add configured thesauri to it
        self.thesauriTable = InputFileTable(self.frame)
        self.thesauriTable.setAvailableTypes(thesaurus_types)
        settings = mainWindow.settings
        settings.validate()
        self.thesauriTable.addRows(settings.thesauri)
        # Input file toevoegen knop
        self.addRowButton = Tkinter.Button(self.frame, text="+", command=self.thesauriTable.addRow)
        self.addRowButton.pack(pady=5)
        # Description label
        descrLabel = Tkinter.Label(self.frame, text="De volgorde van de thesauri in deze tabel bepaalt hun belangrijkheid.\nDe bovenste thesaurus is het meest belangrijk.")
        descrLabel.pack(pady=5, fill=Tkinter.X, expand=1)
        # Add Ok and Cancel buttons
        buttonsFrame = Tkinter.Frame(self.frame)
        buttonsFrame.pack()
        buttonsFrame.pack(fill=Tkinter.X, expand=1)
        okButton = Tkinter.Button(buttonsFrame, text="Ok", command=self.okPressed)
        okButton.pack(side=Tkinter.RIGHT)
        cancelButton = Tkinter.Button(buttonsFrame, text="Annuleren", command=self.cancelPressed)
        cancelButton.pack(side=Tkinter.RIGHT, padx=5)
        # Focus and center
        centerWindow(self.window)
        self.window.focus_set()
        self.window.grab_set()
#       self.window.protocol("WM_DELETE_WINDOW", self.close())
        # Lock all interaction of underlying window and wait until the settigns window is closes
        mainWindow.parent.wait_window(self.window)
        
    def okPressed(self):
        '''Update config, close dialog.'''
        configuredReferenceThesauri = self.thesauriTable.getValues()
        self.mainWindow.updateReferenceThesauri(configuredReferenceThesauri)
        self.close()
        
    def close(self):
        self.window.destroy()
        
    def cancelPressed(self):
        '''No changes are made to config, dialog is closed.'''
        self.close()

class WaitDialog:
    def __init__(self, parent):
        self.top = Tkinter.Toplevel(parent, takefocus=True)
        self.top.wm_attributes("-topmost", True)
        self.top.title('Bezig met verwerken')
        Tkinter.Label(self.top, text="Even geduld, de gegevens worden verwerkt.").pack(padx=10, pady=10, fill=Tkinter.X, expand=1)
        # Focus and center
        centerWindow(self.top)
        self.top.focus_set()
        self.top.grab_set()
        self.top.update()

    def close(self):
        self.top.destroy()
        
def generateReport(museumName, objects, thesaurus, fieldstats, csvfieldstats, outputFile, checkThesaurus):
    'TODO: Moet ik ook unicode encoding toepassen op filenames?? voordeel is dat ik dan filenames met vreemde tekens ondersteun, nadeel is dat als OS bijvoorbeeld geen UTF8 filenames ondersteunt dat het wel eens mis kan gaan.'
    'TODO: allow setting museum name in GUI?'
    inputDataMap = {"name" : museumName, 
                    "objects" : objects, 
                    "thesaurus" : thesaurus, 
                    "fieldstats" : fieldstats,
                    "csvfieldstats": csvfieldstats }
    'TODO: missch verbose op false zetten'
    adlibstats.generateReportFile(outputFile, inputDataMap, False, True, True)

def isValidFile(filename):
    '''Reports whether this is a valid and existing filename'''
    if not isinstance(filename, basestring):
        return False
    filename = filename.strip()
    return filename and os.path.exists(filename)

def isValidOutputFile(filename):
    '''Reports whether this is a valid filename for writing output to.'''
    if not isinstance(filename, basestring):
        return False
    filename = filename.strip()
    if filename:
        return True
    else:
        return False

def centerWindow(window):
        window.update_idletasks()
        w= window["width"]!=0 and window["width"] or window.winfo_width()
        h= window["height"]!=0 and window["height"] or window.winfo_height()
        ws,hs = window.winfo_screenwidth(),window.winfo_screenheight()
        window.geometry('%dx%d+%d+%d' % (w, h, (ws/2) - (w/2), (hs/2) - (h/2)))
        window.geometry("") # To enable pack_propagate again (so window dimensions resize with the widgets placed in it)
        
def dictContainsOrder(rowValues):
    '''Determines whether each member of this dict (which should usually be a set of
    rowValues obtained from an inputFileTable) has an "order" member.
    '''
    for name in rowValues.keys():
        if not "order" in rowValues[name]:
            return False
    return True

def getDictAsOrderedList(rowValues):
    '''Transforms a rowValues dict obtained from an inputFileTable to a list in which
    the rows are ordered using their defined order. This requires that the dict satisfies
    dictContainsOrder(). Order values should be unique or rows will be missing from the set.
    The result will be a list with row dicts similar to those in a rowValues dict, only will
    they contain a "name" member. Their order will be ascending.'''
    orderDict = dict()
    for name in rowValues.keys():
        order = rowValues[name]["order"]
        if order not in orderDict:
            row = rowValues[name]
            row["name"] = name
            orderDict[order] = row
    result = []
    for i in sorted(orderDict.keys()):
        result.append(orderDict[i])
    return result
        
        

def main():
    '''Run the GUI'''
    root= Tkinter.Tk()
    root.title('Erfgoedstats')
    
    # Populate window with widgets
    'top = Tkinter.Toplevel()'
    window = MainWindow(root)
    
    # Run main event loop
    root.mainloop()
    



if __name__ == '__main__':
    main()