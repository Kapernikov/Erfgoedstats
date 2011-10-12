import tkFont
import utils
import release
import resources



import resources.logo_kapernikov
import resources.logo_packed

# tkinter module was renamed in some python versions
try: from Tkinter import *
except: from tkinter import *
# Override default Tkinter widgets with themed ttk ones (necessary for windows, for GTK they are already themed)
from pyttk import *
# These widgets are by default themed by the OS' window manager


class HyperlinkManager:

    def __init__(self, text):

        self.text = text

        self.text.tag_config("hyper", foreground="blue", underline=1)

        self.text.tag_bind("hyper", "<Enter>", self._enter)
        self.text.tag_bind("hyper", "<Leave>", self._leave)
        self.text.tag_bind("hyper", "<Button-1>", self._click)

        self.reset()

    def reset(self):
        self.links = {}

    def add(self, action):
        # add an action to the manager.  returns tags to use in
        # associated text widget
        tag = "hyper-%d" % len(self.links)
        self.links[tag] = action
        return "hyper", tag

    def _enter(self, event):
        self.text.config(cursor="hand2")

    def _leave(self, event):
        self.text.config(cursor="")

    def _click(self, event):
        for tag in self.text.tag_names(CURRENT):
            if tag[:6] == "hyper-":
                self.links[tag]()
                return

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
        
        font = tkFont.Font()
        txt = Text(self.frame,  bg="white" )
        txt.pack(pady=5, fill=X, expand=1)
        hyperlink = HyperlinkManager(txt)
        txt.insert(INSERT,"Website: ")
        txt.insert(INSERT, "http://www.packed.be", hyperlink.add(self.openPackedSite))
        txt.config(state=DISABLED)
        txt.config(height=3)
        txt.config(font=font)

        label = Label(self.frame, text="Ontwikkeling:" , anchor=W)
        label.pack(pady=5, fill=X, expand=1)


        self.logoFrame = Frame(self.frame, bg="white")
        self.logoFrame.pack(fill=BOTH, expand=0)

        label = Label(self.frame, text="Sonsors:" , anchor=W)
        label.pack(pady=5, fill=X, expand=1)

        self.logo2Frame = Frame(self.frame, bg="white")
        self.logo2Frame.pack(fill=BOTH, expand=0)

        
        ## LOGOs (supplied as base64 encoded strings) ##
        digiridooLogo = Label(self.logo2Frame, image=resources.logos_provincies.logo__provincie_)
        digiridooLogo.pack(side=LEFT, padx=10, pady=10)
        
        provincieWestVlLogo = Label(self.logoFrame, image=resources.logo_kapernikov.kapernikov)
        provincieWestVlLogo.grid(column=0, row=0, padx=10, sticky=W)
        provincieWestVlLogo = Label(self.logoFrame, image=resources.logo_packed.packed)
        provincieWestVlLogo.grid(column=1, row=0, padx=10, sticky=E)


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
    
    def openPackedSite(self):
        import webbrowser
        webbrowser.open("http://www.packed.be/")
    
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
