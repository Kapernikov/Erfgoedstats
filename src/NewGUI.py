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
import thesaurus
import tkFont
import pickle
import utils

configFile = "../settings.cfg"

thesaurus_types = ['Adlib XML Thesaurus', 'TXT Thesaurus']
inputfile_types = ['Adlib XML Objecten', 'XML Fieldstats', 'CSV Fieldstats'] + thesaurus_types

class InputFileTable:
    def __init__(self, parent):
        self.parent = parent
        self.frame = Tkinter.Frame(parent)
        self.availableTypes = []
        self.rows = []
        # Init table header
        self.tableHeader = Tkinter.Frame(self.frame)
        self.tableHeader.pack(fill=Tkinter.X, expand=1)
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
        InputFileRow(self, name, filetype, filepath)

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
        result[name]={ "type": type, "path": path  }
        If the same name is used more than once, subsequent names will be renamed to "name#i" with i 
        an incremental number starting from 1.
        Only entries with a valid path and type will be returned.'''
        result = dict()
        for inputFileRow in self.rows:
            name = utils.ensureUnicode(inputFileRow.getName())
            type = utils.ensureUnicode(inputFileRow.getType())
            path = utils.ensureUnicode(inputFileRow.getPath())
            if not os.path.exists(path):
                continue
            if type not in self.getAvailableFiletypes():
                continue
            if not name:
                continue
            if name not in result:
                result[name] = { "type": type, "path": path }
            else:
                i = 1
                while name+"#"+str(i) in result:
                    i = i+1
                result[name+"#"+str(i)] = { "type": type, "path": path }
        return result
    
    def addRows(self, rowValues):
        '''Add rows to this table using rowValues, which should be the same format as is
        returned when calling getValues(). Only rows will be added that have files that exist
        and that have a type that is available for this table.'''
        if not isinstance(rowValues, dict):
            return
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
    def __init__(self, parentTable, name, filetype, filepath):
        self.table = parentTable
        self.parent = parentTable.entries
        self.frame = Tkinter.Frame(self.parent)
        self.frame.pack(fill=Tkinter.X, expand=1)
        if not filetype or not filetype in self.table.getAvailableFiletypes():
            filetype = self.table.getAvailableFiletypes()[0]
        
        # Name column
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
            filename = tkFileDialog.askopenfilename(title="Kies Adlib XML met objecten", initialdir="../data/musea/", defaultextension="*.xml")
        if filetype == 'Adlib XML Thesaurus':
            filename = tkFileDialog.askopenfilename(title="Kies Adlib XML met een thesaurus", initialdir="../data/musea/", defaultextension="*.xml")
        if filetype == 'XML Fieldstats':
            filename = tkFileDialog.askopenfilename(title="Kies Adlib XML voor fieldstats", initialdir="../data/musea/", defaultextension="*.xml")
        if filetype == 'CSV Fieldstats':
            filename = tkFileDialog.askopenfilename(title="Kies CSV bestand voor fieldstats", initialdir="../data/musea/", defaultextension="*.csv")

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
        return utils.ensureUnicode(self.nameField.get())
        
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
        mainmenu = Tkinter.Menu(self.menu)
        mainmenu.add_command(label='Opties', command=self.showOptions)
        mainmenu.add_command(label='Afsluiten', command=self.parent.quit)
        self.menu.add_cascade(label='Menu', menu=mainmenu)
        parent.config(menu=self.menu)
        
        ## LOGOs ##
        digiridooImg = Tkinter.PhotoImage("Digiridoo logo", file="images/logo-blue-143.gif")
        digiridooLogo = Tkinter.Label(self.logoFrame, image=digiridooImg)
        digiridooLogo.photo = digiridooImg 
        digiridooLogo.pack(side=Tkinter.LEFT, padx=10, pady=10)
        
        provincieWestVlImg = Tkinter.PhotoImage("Provincie West Vlaanderen logo", file="images/logo_pwv.gif")
        provincieWestVlLogo = Tkinter.Label(self.logoFrame, image=provincieWestVlImg)
        provincieWestVlLogo.photo = provincieWestVlImg
        provincieWestVlLogo.pack(side=Tkinter.RIGHT, padx=10)
        
        'TODO: kunnen table en logos niet allemaal in 1 frame?'
        ## Input files ##
        font = tkFont.Font(weight="bold")
        inputsLabel = Tkinter.Label(self.frame, text="Input bestanden: ", anchor=Tkinter.W, font=font)
        inputsLabel.pack(padx=5, pady=5, fill=Tkinter.X, expand=1)
        self.inputFilesTable = InputFileTable(self.frame)
        self.inputFilesTable.setAvailableTypes( inputfile_types )
        # Set default input rows
        self.inputFilesTable.addRow(name="Objecten", filetype='Adlib XML Objecten')
        self.inputFilesTable.addRow(name="Thesaurus", filetype='Adlib XML Thesaurus')
        
        # Input file toevoegen knop
        self.addRowButton = Tkinter.Button(self.frame, text="+", command=self.addInputRow)
        self.addRowButton.pack()
        
        # Kies output file
        self.frame3 = Tkinter.Frame(self.frame)
        self.frame3.pack(pady=10, fill=Tkinter.X, expand=1)
        font = tkFont.Font(weight="bold")
        label3 = Tkinter.Label(self.frame3, text="Output: ", width=8, font=font)
        label3.pack(side=Tkinter.LEFT)
        self.inputField3 = Tkinter.Entry(self.frame3)
        self.inputButton3 = Tkinter.Button(self.frame3, text="Bladeren", command=self.browseFile3)
        self.inputField3.pack(side=Tkinter.LEFT, fill=Tkinter.X, expand=1)
        self.inputButton3.pack(side=Tkinter.RIGHT, padx=5)
        
        # Vergelijk met thesauri optie
        self.frame4 = Tkinter.Frame(self.frame)
        self.frame4.pack(pady=10, fill=Tkinter.X, expand=1)
        self.checkThesaurus = Tkinter.IntVar()
        availableThesauri = self.getConfiguredReferenceThesauri().keys()
        self.checkb = Tkinter.Checkbutton(self.frame4, variable=self.checkThesaurus)
        self.updateThesauriCheckbox()
        self.checkb.pack(side=Tkinter.LEFT, padx=5)
        
        ## Start button ##
        self.startButton = Tkinter.Button(self.frame, text="Start", command=self.start)
        self.startButton.pack(side=Tkinter.BOTTOM)
    
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
    
    def browseFile1(self):
        self.browseFile(self.inputField1, "Kies Adlib XML met objecten", "../data/musea/", defaultExt="*.xml")
        
    def browseFile2(self):
        self.browseFile(self.inputField2, "Kies Adlib XML met een thesaurus", "../data/musea/", defaultExt="*.xml")
    
    def browseFile3(self):
        self.browseFile(self.inputField3, "Waar wil je het resultaat opslaan?", "../out/", filetypes=[("HTML bestand", "*.html")], isOutputFile=True)
        
    def showOptions(self):
        '''Show the settings dialog'''
        SettingsDialog(self)
        
    def start(self):
        if not isValidFile(self.inputField1.get()):
            tkMessageBox.showerror('Fout bij het starten', 'Kon niet starten omdat er geen correct "Objecten" bestand is opgegeven.');
            return
        if not isValidFile(self.inputField2.get()):
            tkMessageBox.showerror('Fout bij het starten', 'Kon niet starten omdat er geen correct "Thesaurus" bestand is opgegeven.');
            return
        if not isValidOutputFile(self.inputField3.get()):
            tkMessageBox.showerror('Fout bij het starten', 'Kon niet starten omdat er geen correct "Output" bestand is opgegeven.');
            return
        
        if os.path.exists(self.inputField3.get()):
            doOverwrite = tkMessageBox.askyesno('Bestand overschrijven?', 'Het gekozen "Output" bestand bestaat reeds. Wil je verder gaan en het overschrijven?')
            if not doOverwrite:
                return
#        tkMessageBox.showinfo("Bezig met verwerken", "Even geduld, de gegevens worden verwerkt.", parent=self.parent)
        #d = WaitDialog(self.parent)
        #d.top.update()
        #self.parent.wait_window(d.top)
        height = self.frame.winfo_height()
        width = self.frame.winfo_width()
        self.frame.pack_forget()
        waitLabel = Tkinter.Label(self.parent, text="Even geduld, de gegevens worden verwerkt.", height=height, width=width)
        waitLabel.pack(padx=10, pady=10)
        self.parent.update()
        
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
        waitLabel.destroy()
        self.frame.pack()
        
    def loadConfiguration(self):
        '''Load saved configuration of app. If the config file is
        not found or cannot be read, a new settings object is returned
        with defaults. Settings will be validated and are assured not to
        contain thesauri for which the file does not exist.'''
        if not os.path.exists(configFile):
            return getDefaultSettings()
        try:
            unpickler = pickle.Unpickler(codecs.open(configFile,'ru', encoding="utf-8" ,errors="ignore"))
            settings = unpickler.load()
            if not isinstance(settings, Settings):
                return getDefaultSettings()
            settings.validate()
            return settings
        except:
            return getDefaultSettings()
        
    def saveConfiguration(self, settings):
        if not isinstance(settings, Settings):
            return
        try:
            pickler = pickle.Pickler(codecs.open(configFile,'wu', encoding="utf-8" ,errors="ignore"))
            pickler.dump(settings)
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
        self.frame.quit()
        self.logoFrame.quit()
        'root.quit()'
        
def getDefaultSettings():
    '''Return an initial default settings object.
    Will try adding the default thesauri to the settings. Only existing files will be added.'''
    settings= Settings()
    settings.addReferenceThesaurus('AAT-Ned', '../data/reference/aat2000.xml', 'Adlib XML Thesaurus')
    settings.addReferenceThesaurus('Am-Move', '../data/reference/Am_Move_thesaurus06_10.xml', 'Adlib XML Thesaurus')
    settings.addReferenceThesaurus('Mot', '../data/MOT/mot-naam.txt', 'TXT Thesaurus')
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
        self.thesauri[thesaurusName] = {"path": thesaurusPath, "type": type}
        
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
        self.window = Tkinter.Toplevel()
        self.window.title = 'Instellingen'
        label = Tkinter.Label(self.window, text='Standaard (referentie) thesauri: ')
        label.pack()
        # Create an input file table for specifying the thesauri and add configured thesauri to it
        self.thesauriTable = InputFileTable(self.window)
        self.thesauriTable.setAvailableTypes(thesaurus_types)
        settings = mainWindow.settings
        settings.validate()
        self.thesauriTable.addRows(settings.thesauri)
        # Input file toevoegen knop
        self.addRowButton = Tkinter.Button(self.window, text="+", command=self.thesauriTable.addRow)
        self.addRowButton.pack()
        # Add Ok and Cancel buttons
        okButton = Tkinter.Button(self.window, text="Ok", command=self.okPressed)
        okButton.pack()
        cancelButton = Tkinter.Button(self.window, text="Annuleren", command=self.cancelPressed)
        cancelButton.pack()
        self.window.transient()
        self.window.focus_set()
        self.window.grab_set()
        self.window.protocol("WM_DELETE_WINDOW", self.close())
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
        self.top = Tkinter.Toplevel(parent)
        self.top.title = 'Bezig met verwerken'
        Tkinter.Label(self.top, text="Even geduld, de gegevens worden verwerkt.", width= 20, height=8).pack(padx=10, pady=10)

    def ok(self):
        print "value is", self.e.get()
        self.top.destroy()
        
def generateReport(objecten, thesaurus, outfile, checkThesaurus):
    'TODO: Moet ik ook unicode encoding toepassen op filenames?? voordeel is dat ik dan filenames met vreemde tekens ondersteun, nadeel is dat als OS bijvoorbeeld geen UTF8 filenames ondersteunt dat het wel eens mis kan gaan.'
    output = codecs.open(outfile, mode="w", encoding="utf-8", errors="ignore")
    output.write(adlibstats.get_header())
    if (objecten):
        output.write(adlibstats.generate_compliancereport(objecten, True, not checkThesaurus))
    if (thesaurus):   
        output.write(adlibstats.generate_thesaurusreport(thesaurus))    
    output.write(adlibstats.get_footer())

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