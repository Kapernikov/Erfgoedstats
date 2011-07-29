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
import tkMessageBox
import thesaurus
import Tkinter

class MainWindow:
    def __init__(self, parent):
        self.parent = parent
        
        self.logoFrame = Tkinter.Frame(parent)
        self.logoFrame.pack(side=Tkinter.TOP, fill=Tkinter.BOTH, expand=1)
        
        self.frame = Tkinter.Frame(parent)
        self.frame.pack(padx=10, pady=10, fill=Tkinter.X, expand=1)
        
        ## LOGOs ##
        digiridooImg = Tkinter.PhotoImage("Digiridoo logo", file="images/logo-blue-143.gif")
        digiridooLogo = Tkinter.Label(self.logoFrame, image=digiridooImg)
        digiridooLogo.photo = digiridooImg 
        digiridooLogo.pack(side=Tkinter.LEFT, padx=10, pady=10)
        
        provincieWestVlImg = Tkinter.PhotoImage("Provincie West Vlaanderen logo", file="images/logo_pwv.gif")
        provincieWestVlLogo = Tkinter.Label(self.logoFrame, image=provincieWestVlImg)
        provincieWestVlLogo.photo = provincieWestVlImg
        provincieWestVlLogo.pack(side=Tkinter.RIGHT, padx=10, pady=10)
        
        ## Input boxes ##
        self.frame1 = Tkinter.Frame(self.frame)
        self.frame1.pack(pady=5, fill=Tkinter.X, expand=1)
        label1 = Tkinter.Label(self.frame1, text="Objecten: ", width=8)
        label1.pack(side=Tkinter.LEFT, padx=5)
        self.inputField1 = Tkinter.Entry(self.frame1)
        self.inputButton1 = Tkinter.Button(self.frame1, text="Bladeren", command=self.browseFile1)
        self.inputField1.pack(side=Tkinter.LEFT, fill=Tkinter.X, expand=1)
        self.inputButton1.pack(side=Tkinter.RIGHT, padx=5)
        
        self.frame2 = Tkinter.Frame(self.frame)
        self.frame2.pack(pady=5, fill=Tkinter.X, expand=1)
        label2 = Tkinter.Label(self.frame2, text="Thesaurus: ", width=8)
        label2.pack(side=Tkinter.LEFT, padx=5)
        self.inputField2 = Tkinter.Entry(self.frame2)
        self.inputButton2 = Tkinter.Button(self.frame2, text="Bladeren", command=self.browseFile2)
        self.inputField2.pack(side=Tkinter.LEFT, fill=Tkinter.X, expand=1)
        self.inputButton2.pack(side=Tkinter.RIGHT, padx=5)
        
        self.frame3 = Tkinter.Frame(self.frame)
        self.frame3.pack(pady=5, fill=Tkinter.X, expand=1)
        label3 = Tkinter.Label(self.frame3, text="Output: ", width=8)
        label3.pack(side=Tkinter.LEFT, padx=5)
        self.inputField3 = Tkinter.Entry(self.frame3)
        self.inputButton3 = Tkinter.Button(self.frame3, text="Bladeren", command=self.browseFile3)
        self.inputField3.pack(side=Tkinter.LEFT, fill=Tkinter.X, expand=1)
        self.inputButton3.pack(side=Tkinter.RIGHT, padx=5)
        
        self.frame4 = Tkinter.Frame(self.frame)
        self.frame4.pack(pady=10, fill=Tkinter.X, expand=1)
        self.checkThesaurus = Tkinter.IntVar()
        availableThesauri = getAvailableReferenceThesauri()
        checkbState = Tkinter.DISABLED
        if(len(availableThesauri) > 0):
            availableThesauri = ', '.join(availableThesauri)
            checkbState = Tkinter.NORMAL
        else:
            availableThesauri = "Geen thesauri gevonden"
        checkb = Tkinter.Checkbutton(self.frame4, text="Vergelijken met standaard thesauri (%s)" % availableThesauri, variable=self.checkThesaurus, state=checkbState)
        checkb.pack(side=Tkinter.LEFT, padx=5)
        
        
        ## Start button ##
        self.startButton = Tkinter.Button(self.frame, text="Start", command=self.start)
        self.startButton.pack(side=Tkinter.BOTTOM)
        
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
        
    def quit(self):
        self.frame.quit()
        self.logoFrame.quit()
        'root.quit()'

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

def getAvailableReferenceThesauri():
    '''Determine which reference thesauri are available from their standard locations.'''
    result = []
    if(os.path.exists('../data/reference/aat2000.xml')):
        result.append('AAT-Ned')
    if(os.path.exists('../data/reference/Am_Move_thesaurus06_10.xml')):
        result.append('Am-Move')
    if(os.path.exists('../data/MOT/mot-naam.txt')):
        result.append('Mot')
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