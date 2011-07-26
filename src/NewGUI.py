'''
New GUI

Created on 26-jul-2011

@author: duststorm
'''
import Tkinter,tkFileDialog,tkMessageBox
import os
import adlibstats
import webbrowser
import tkMessageBox

class MainWindow:
    def __init__(self, parent):
        self.logoFrame = Tkinter.Frame(parent)
        self.logoFrame.pack(side=Tkinter.TOP, fill=Tkinter.BOTH, expand=1)
        
        self.frame = Tkinter.Frame(parent)
        self.frame.pack(padx=10, pady=10, fill=Tkinter.X, expand=1)
        
        digiridooImg = Tkinter.PhotoImage("Digiridoo logo", file="images/logo-blue-143.gif")
        digiridooLogo = Tkinter.Label(self.logoFrame, image=digiridooImg)
        digiridooLogo.photo = digiridooImg 
        digiridooLogo.pack(side=Tkinter.LEFT, padx=10, pady=10)
        
        provincieWestVlImg = Tkinter.PhotoImage("Provincie West Vlaanderen logo", file="images/logo_pwv.gif")
        provincieWestVlLogo = Tkinter.Label(self.logoFrame, image=provincieWestVlImg)
        provincieWestVlLogo.photo = provincieWestVlImg
        provincieWestVlLogo.pack(side=Tkinter.RIGHT, padx=10, pady=10)
        
        self.frame1 = Tkinter.Frame(self.frame)
        self.frame1.pack(pady=5, fill=Tkinter.X, expand=1)
        label1 = Tkinter.Label(self.frame1, text="File1: ")
        label1.pack(side=Tkinter.LEFT, padx=5)
        self.inputField1 = Tkinter.Entry(self.frame1, text="File 1")
        self.inputButton1 = Tkinter.Button(self.frame1, text="Browse", command=self.browseFile1)
        self.inputField1.pack(side=Tkinter.LEFT, fill=Tkinter.X, expand=1)
        self.inputButton1.pack(side=Tkinter.RIGHT, padx=5)
        
        self.frame2 = Tkinter.Frame(self.frame)
        self.frame2.pack(pady=5, fill=Tkinter.X, expand=1)
        label2 = Tkinter.Label(self.frame2, text="File2: ")
        label2.pack(side=Tkinter.LEFT, padx=5)
        self.inputField2 = Tkinter.Entry(self.frame2, text="File 2")
        self.inputButton2 = Tkinter.Button(self.frame2, text="Browse", command=self.browseFile2)
        self.inputField2.pack(side=Tkinter.LEFT, fill=Tkinter.X, expand=1)
        self.inputButton2.pack(side=Tkinter.RIGHT, padx=5)
        
        self.frame3 = Tkinter.Frame(self.frame)
        self.frame3.pack(pady=5, fill=Tkinter.X, expand=1)
        label3 = Tkinter.Label(self.frame3, text="File3: ")
        label3.pack(side=Tkinter.LEFT, padx=5)
        self.inputField3 = Tkinter.Entry(self.frame3, text="File 3")
        self.inputButton3 = Tkinter.Button(self.frame3, text="Browse", command=self.browseFile3)
        self.inputField3.pack(side=Tkinter.LEFT, fill=Tkinter.X, expand=1)
        self.inputButton3.pack(side=Tkinter.RIGHT, padx=5)
        
        self.frame4 = Tkinter.Frame(self.frame)
        self.frame4.pack(pady=5, fill=Tkinter.X, expand=1)
        label4 = Tkinter.Label(self.frame4, text="File4: ")
        label4.pack(side=Tkinter.LEFT, padx=5)
        self.inputField4 = Tkinter.Entry(self.frame4, text="File 4")
        self.inputButton4 = Tkinter.Button(self.frame4, text="Browse", command=self.browseFile4)
        self.inputField4.pack(side=Tkinter.LEFT, fill=Tkinter.X, expand=1)
        self.inputButton4.pack(side=Tkinter.RIGHT, padx=5)
        
        self.startButton = Tkinter.Button(self.frame, text="Start", command=self.start)
        self.startButton.pack(side=Tkinter.BOTTOM)
        
    def browseFile(self, inputField):
        '''TODO: maybe filter for filetype'''
        filename = tkFileDialog.askopenfilename()
        if not isValidFile(filename):
            return
        # Remove current text and replace with selected filename
        inputField.delete(0, Tkinter.END)
        inputField.insert(0, filename)
        return
    
    def browseFile1(self):
        self.browseFile(self.inputField1)
        
    def browseFile2(self):
        self.browseFile(self.inputField2)
    
    def browseFile3(self):
        self.browseFile(self.inputField3)
        
    def browseFile4(self):
        self.browseFile(self.inputField4)
    
    def start(self):
        if isValidFile(self.inputField1.get()) and (self.inputField2.get()) and (self.inputField3.get()) and (self.inputField4.get()) :
            return
            'TODO: start app'
        else:
            'TODO: Warn which file fails'
            tkMessageBox.showerror("Could not start", "Could not start because a file is not valid.");
            return
        
    def quit(self):
        self.frame.quit()
        self.logoFrame.quit()
        'root.quit()'

def isValidFile(filename):
    '''Reports whether this is a valid and existing filename'''
    if not isinstance(filename, basestring):
        return False
    filename = filename.strip()
    return filename and os.path.exists(filename)


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