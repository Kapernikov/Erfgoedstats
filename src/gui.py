# -*- coding: utf-8 -*-
'''
Simple GUI of 4 select file boxes

Created on 22 feb. 2011

@author: rein
'''
import Tkinter,tkFileDialog
import adlibstats
import webbrowser
import tkMessageBox

    

def generateReport(objecten, thesaurus, outfile, nothesaurus):
    output = file(outfile, "w")
    output.write(adlibstats.get_header())
    if (objecten != ""):
        output.write(adlibstats.generate_compliancereport(objecten, True, nothesaurus))
    if (thesaurus != ""):   
        output.write(adlibstats.generate_thesaurusreport(thesaurus))    
    output.write(adlibstats.get_footer())

def main():
    root = Tkinter.Tk()
    root.withdraw()
    objecten = str(tkFileDialog.askopenfilename(parent=root,title='Kies Adlib XML met objecten', defaultextension="*.xml", initialdir="../data/musea/"))
    thesaurus = str(tkFileDialog.askopenfilename(parent=root,title='Kies Adlib XML met een thesaurus', defaultextension="*.xml", initialdir="../data/musea/"))
    outfile = str(tkFileDialog.asksaveasfilename(parent=root,filetypes=[("HTML bestand", "*.html")] ,title="Waar wil je het resultaat opslaan?", initialdir="../out/"))
    thesauruschecken = tkMessageBox.askyesno("Thesaurus?", "Wil je vergelijken met de thesauri? (AAT-Ned, Am-Move & Mot).  Dit neemt extra tijd in beslag.")
    
    generateReport(objecten, thesaurus, outfile, not thesauruschecken)
    
    webbrowser.open(outfile)
    
    exit()
    
if __name__ == '__main__':
    main()