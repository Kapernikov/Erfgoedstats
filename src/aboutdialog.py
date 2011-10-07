import tkFont
import utils
import release


# tkinter module was renamed in some python versions
try: from Tkinter import *
except: from tkinter import *
# Override default Tkinter widgets with themed ttk ones (necessary for windows, for GTK they are already themed)
from pyttk import *
# These widgets are by default themed by the OS' window manager
class AboutDialog(Toplevel):
    def __init__(self, mainWindow):
        Toplevel.__init__(self, mainWindow.parent, takefocus=True)
        self.transient(mainWindow.parent)
        self.mainWindow = mainWindow
        self.protocol("WM_DELETE_WINDOW", self.cancelPressed)
        #self.window.wm_attributes("-topmost", True)    # This option does not play well with ttk comboboxes
        self.title('Over erfgoedstats')
        self.grab_set()
        self.frame = Frame(self)
        self.frame.pack(fill=BOTH, expand=1, padx=10, pady=10)
        
        font = tkFont.Font(weight="bold")
        label = Label(self.frame, text="Erfgoedstats versie %s (%s)" % (release.version, release.date), anchor=W, font=font)
        label.pack(pady=5, fill=X, expand=1)
        
        # Add Ok and Cancel buttons
        buttonsFrame = Frame(self.frame)
        buttonsFrame.pack()
        buttonsFrame.pack(fill=X, expand=1)
        okButton = Button(buttonsFrame, text="Ok", command=self.okPressed)
        okButton.pack(side=RIGHT)
        self.bind("<Escape>", self.cancelPressed)
        # Focus and center
        utils.centerWindow(self)
        self.focus_set()
    
    def show(self):
        # Lock all interaction of underlying window and wait until the settigns window is closes
        self.wait_window(self)
        
    def okPressed(self, par=None):
        '''Update config, close dialog.'''
        self.cancelPressed()

        
    def close(self):
        self.destroy()
        
    def cancelPressed(self, par=None):
        '''No changes are made to config, dialog is closed.'''
        self.mainWindow.parent.focus_set()
        self.close()
