import utils
import copy
# tkinter module was renamed in some python versions
try: from Tkinter import *
except: from tkinter import *
# Override default Tkinter widgets with themed ttk ones (necessary for windows, for GTK they are already themed)
try: from ttk import *
except: from pyttk import *
# These widgets are by default themed by the OS' window manager
import tkFileDialog
import tkMessageBox
import os.path
import resources.ButtonIcons_base64

    

class TEntry:
    def __init__(self,name,type,path,order):
        self.path = path
        self.type = type
        self.order = order
        self.name = name
    
    
    
class TEntries:
    def __init__(self):
        self.values = []

    def clear(self):
        self.values = []

    def sort(self):
        self.values.sort(cmp=lambda x,y: x.order > y.order)

    def remove(self,e):
        self.values.remove(e)
    
    def size(self):
        return len(self.values)

    def append(self,entr):
        self.values.append(entr)

class InputFileTable:
    '''GUI Widget that allows for defining a table in which each row represents an input file.
    Each row or input file has a name, a filetype, and a filepath. Optionally a fixed order of
    rows can be maintained.'''
    def __init__(self, parent, nameColumn=True, settings=None, tabletype="thesaurus"):
        self.parent = parent
        self.settings = settings
        self.frame = Frame(parent)
        self.availableTypes = []
        self.tabletype = tabletype
        self.rows = []
        self.nameColumn=nameColumn
        # Init table header
        self.tableHeader = Frame(self.frame)
        self.tableHeader.pack(fill=X, expand=1)
        if nameColumn:
            nameheader = Label(self.tableHeader, text="Naam", width=15)
            nameheader.pack(side=LEFT, padx=5)
        typeheader = Label(self.tableHeader, text="Type", width=19)
        typeheader.pack(side=LEFT, padx=5)
        pathheader = Label(self.tableHeader, text="Bestandslocatie", width=20)
        pathheader.pack(side=LEFT, padx=30)
        # Frame containing the entries
        self.entries = Frame(self.frame)
        self.entries.pack(fill=X, expand=1)
        self.frame.pack(fill=BOTH, expand=1)
        
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
        result = TEntries()
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
            result.append(TEntry(name,type,path,order))
            order = order+1
        return result
    
    def close(self):
        for row in self.rows:
            row.remove()
        self.tableHeader.destroy()
        self.frame.destroy()
    
    def addRows(self, entries):
        '''Add rows to this table using rowValues, which should be the same format as is
        returned when calling getValues(). Only rows will be added that have files that exist
        and that have a type that is available for this table.'''
        if not isinstance(entries, TEntries):
            return
        
        entries.sort()
        
        for entry in entries.values:
            name = entry.name
            type = entry.type
            path=  entry.path
            if not os.path.exists(path) or type not in self.getAvailableFiletypes():
                continue
            self.addRow(name, type, path)

def isValidFile(filename):
    '''Reports whether this is a valid and existing filename'''
    if not isinstance(filename, basestring):
        return False
    filename = filename.strip()
    return filename and os.path.exists(filename)

        
class InputFileRow:
    def __init__(self, parentTable, name, filetype, filepath, nameColumn=True):
        self.table = parentTable
        self.parent = parentTable.entries
        self.frame = Frame(self.parent)
        self.frame.pack(fill=X, expand=1)
        self.nameColumn = nameColumn
        if not filetype or not filetype in self.table.getAvailableFiletypes():
            filetype = self.table.getAvailableFiletypes()[0]
        
        # Name column
        if(nameColumn):
            self.nameField = Entry(self.frame, width=15)
            self.nameField.pack(side=LEFT)
            if name and isinstance(name, basestring):
                self.nameField.insert(0, name)
        # Type column
        # Prepare values so combobox interprets them correctly (escape spaces)
        # This is due to some dirty TCL remains in the pyttk wrapper library
        values = copy.deepcopy(self.table.getAvailableFiletypes())
        i=0
        for v in values:
            v = '{'+v+'}'
            values[i] = v 
            i = i+1
        values = " ".join(values)
        # use ttk.Combobox (please ignore pydev error on this line)
        self.typeSelect = Combobox(self.frame, values=values)
        self.typeSelect["state"] = "readonly" # only allow selection of predefined values
        self.typeSelect.current(self.table.availableTypes.index(filetype))
        self.typeSelect.pack(side=LEFT, padx=5)
        # Path column
        self.pathField = Entry(self.frame, width=20)
        self.pathField.pack(side=LEFT, fill=X, expand=1, padx=5)
        if filepath and isinstance(filepath, basestring):
            self.pathField.insert(0, filepath)
        # Browse button
        self.browseButton = Button(self.frame, text="Bladeren", command=self.browseFile)
        self.browseButton.pack(side=LEFT, padx=5)
        # Remove row button
        self.removeButton = Button(self.frame, image=PhotoImage(data=resources.ButtonIcons_base64.remove), text="Verwijderen", compound=LEFT, command=self.remove)
        self.removeButton.pack(side=LEFT)
        # Add to rows list
        parentTable.rows.append(self)
        
    def browseFile(self):
        initialDir = self.table.settings.getPath(self.table.tabletype)
        filename = ""
        filetype = self.getType()
        if filetype == 'Adlib XML Objecten':
            filename = tkFileDialog.askopenfilename(title="Kies Adlib XML met objecten", initialdir=initialDir, defaultextension="*.xml", parent=self.parent)
        if filetype == 'Adlib XML Thesaurus':
            filename = tkFileDialog.askopenfilename(title="Kies Adlib XML met een thesaurus", initialdir=initialDir, defaultextension="*.xml", parent=self.parent)
        if filetype == 'Adlib XML Personen':
            filename = tkFileDialog.askopenfilename(title="Kies Adlib XML met personen en instellingen", initialdir=initialDir, defaultextension="*.xml", parent=self.parent)
        if filetype == 'TXT Thesaurus':
            filename = tkFileDialog.askopenfilename(title="Kies bestand met TXT thesaurus", initialdir=initialDir, defaultextension="*.txt", parent=self.parent)
        if filetype == 'XML Fieldstats':
            filename = tkFileDialog.askopenfilename(title="Kies Adlib XML voor fieldstats", initialdir=initialDir, defaultextension="*.xml", parent=self.parent)
        if filetype == 'CSV Fieldstats':
            filename = tkFileDialog.askopenfilename(title="Kies CSV bestand voor fieldstats", initialdir=initialDir, defaultextension="*.csv", parent=self.parent)

        if not isValidFile(filename):
            return
        # In path field, remove current text and replace with selected filename
        self.table.settings.setPath(self.table.tabletype,os.path.dirname(filename))
        self.pathField.delete(0, END)
        self.pathField.insert(0, filename)
        
        
    def remove(self):
        self.table.rows.remove(self)
        self.frame.destroy()
        
    def getName(self):
        if self.nameColumn:
            return utils.ensureUnicode(self.nameField.get())
        else:
            return ""
        
    def getType(self):
        return utils.ensureUnicode(self.typeSelect.get())
        
    def getPath(self):
        return utils.ensureUnicode(self.pathField.get()) 
