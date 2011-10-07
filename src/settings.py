
import tkFont
import pickle
import utils
import thesaurus


# tkinter module was renamed in some python versions
try: from Tkinter import *
except: from tkinter import *
# Override default Tkinter widgets with themed ttk ones (necessary for windows, for GTK they are already themed)
from pyttk import *
# These widgets are by default themed by the OS' window manager



import resources.ButtonIcons_base64


from inputfiletable import  InputFileTable, TEntries

'''Filetypes that are selectable from the input file tables'''
thesaurus_types = thesaurus.valid_filetypes
inputfile_types = ['Adlib XML Objecten', 'Adlib XML Thesaurus', 'Adlib XML Personen', 'XML Fieldstats', 'CSV Fieldstats']


def getDefaultSettings():
    '''Return an initial default settings object.
    Will try adding the default thesauri to the settings. Only existing files will be added.'''
    settings= Settings()
    settings.addReferenceThesaurus('Mot', '../data/MOT/mot-naam.txt', 'TXT Thesaurus')
    settings.addReferenceThesaurus('Am-Move', '../data/reference/Am_Move_thesaurus06_10.xml', 'Adlib XML Thesaurus')
    settings.addReferenceThesaurus('AAT-Ned', '../data/reference/aat2000.xml', 'Adlib XML Thesaurus')
    print "Loaded initial default settings."
    return settings

def getDefaultDirectory(path=""):
    if not path or not os.path.exists(path):
        # Works on linux and windows
        return os.path.expanduser('~')
    return path
        

        
class Settings:
    def __init__(self):
        self.thesauri = TEntries()
        self.paths = {}
        
    def getPath(self, type):
        xp = "../data/musea/"
        if type in self.paths.keys():
            xp = self.paths[type]
        return getDefaultDirectory(path=xp)
        
    def setPath(self,type,path):
        self.paths[type] = path
        
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
        for entry in self.thesauri.values:
            if not os.path.exists(entry.path) or entry.type not in thesaurus_types:
                self.thesauri.remove(entry)
    
    def getReferenceThesauri(self):
        '''Determine which reference thesauri are configured and their locations.
        The returned result is a dict with thesaurus name as key, and a thesaurus dict
        as value. This thesaurus dict has "type" and "path" values'''
        return self.thesauri

class SettingsDialog(Toplevel):
    def __init__(self, mainWindow):
        Toplevel.__init__(self, mainWindow.parent, takefocus=True)
        self.transient(mainWindow.parent)
        self.mainWindow = mainWindow
        self.protocol("WM_DELETE_WINDOW", self.cancelPressed)
        #self.window.wm_attributes("-topmost", True)    # This option does not play well with ttk comboboxes
        self.title('Instellingen')
        self.grab_set()
        self.frame = Frame(self)
        self.frame.pack(fill=BOTH, expand=1, padx=10, pady=10)
        font = tkFont.Font(weight="bold")
        label = Label(self.frame, text='Standaard (referentie) thesauri: ', anchor=W, font=font)
        label.pack(pady=5, fill=X, expand=1)
        # Create an input file table for specifying the thesauri and add configured thesauri to it
        self.thesauriTable = InputFileTable(self.frame,settings=mainWindow.settings)
        self.thesauriTable.setAvailableTypes(thesaurus_types)
        settings = mainWindow.settings
        settings.validate()
        self.thesauriTable.addRows(settings.thesauri)
        if settings.thesauri.size() == 0:
            # Add an empty row to GUI if no thesauri are configured, as a visual cue of what the purpose of this menu is
            self.thesauriTable.addRow()
        # Input file toevoegen knop
        self.addRowButton = Button(self.frame, text="Thesaurus toevoegen", image=resources.ButtonIcons_base64.add, compound=LEFT, command=self.thesauriTable.addRow)
        self.addRowButton.pack(pady=5)
        # Description label
        descrLabel = Label(self.frame, text="De volgorde van de thesauri in deze tabel bepaalt hun belangrijkheid.\nDe bovenste thesaurus is het meest belangrijk.", anchor=W)
        descrLabel.config(justify=LEFT)
        descrLabel.pack(pady=5, fill=X, expand=1)
        # Add Ok and Cancel buttons
        buttonsFrame = Frame(self.frame)
        buttonsFrame.pack()
        buttonsFrame.pack(fill=X, expand=1)
        okButton = Button(buttonsFrame, text="Ok", command=self.okPressed)
        okButton.pack(side=RIGHT)
        cancelButton = Button(buttonsFrame, text="Annuleren", command=self.cancelPressed)
        cancelButton.pack(side=RIGHT, padx=5)
        self.bind("<Escape>", self.cancelPressed)
        # Focus and center
        utils.centerWindow(self)
        self.focus_set()
#       self.window.protocol("WM_DELETE_WINDOW", self.close())

    
    def show(self):
        # Lock all interaction of underlying window and wait until the settigns window is closes
        self.wait_window(self)
        
    def okPressed(self, par=None):
        '''Update config, close dialog.'''
        configuredReferenceThesauri = self.thesauriTable.getValues()
        self.mainWindow.updateReferenceThesauri(configuredReferenceThesauri)
        self.cancelPressed()

        
    def close(self):
        self.thesauriTable.close()
        self.destroy()
        
    def cancelPressed(self, par=None):
        '''No changes are made to config, dialog is closed.'''
        self.mainWindow.parent.focus_set()
        self.close()
