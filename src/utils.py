# -*- coding: utf-8 -*-
'''
Utility helper functions

Created on Jan 7, 2011

@author: kervel
'''

from operator import itemgetter
import htmlutils

import tr

class CounterDict:
    '''Wrapper class around a dictionary that allows storing key/value pairs.
    The key is the name of a term, the value is defined as its count (the number
    of occurences of that property).
    Has some utility functions, and is able to generate a HTML report from itself.'''
    def __init__(self):
        self.realdict = {}
        self.level2dict = {}
    
    def count(self, name, level2=None):
        '''Indicate or count one occurence of a specified term.
        Creates that term with count one if it was not counted before.''' 
        if name not in self.realdict:
            self.realdict[name] = 1
            self.level2dict[name] = {}
        else:
            self.realdict[name] = self.realdict[name] + 1
            if (level2):
                d = self.level2dict[name]
                if level2 not in d:
                    d[level2]=1
                else:
                    d[level2]=d[level2]+1
        
    def getSortedResult(self, dict=None, reverse=True):
        '''Returns a sorted list of (term, count) tuples, sorted by their number of occurences.
        The term with the most occurences comes first.''' 
        if (dict is None):
            dict = self.realdict
        return sorted(dict.iteritems(), key=itemgetter(1), reverse=reverse)
    
    def getReport(self, dict=None):
        '''Generate a HTML report from this dictionary.'''
        html = ""
        html += '<table class="countertable" border="0">'
        html += "<thead><tr><th>Aantal</th><th>%</th><th>Waarde</th></tr></thead>\n<tbody>"
        if (dict is None):
            dict = self.realdict
        total = sum(dict.values())
        for x in self.getSortedResult(dict):
            html += "<tr>\n<td>%s</td>\n<td>%d&#37</td>\n<td>%s</td>\n</tr>" % (x[1], 100*x[1]/total , tr.tr(x[0]).replace("'",""))
        html += "</tbody></table>"
        return html
    
    def getL2Report(self):
        table = htmlutils.SortableTable()
        table.addClass("rpt")
        total = sum(self.values())
        table.setHeader(["Waarde", "Aantal", "Percentage"])
        for x in self.getSortedResult():
            row = htmlutils.TableRow()
            row.addClass("value-row")
            namecell = htmlutils.Cell()
            namecell.addClass("fieldname")
            namecell.content = tr.tr(x[0]).replace("'","")
            
            valuecell = htmlutils.Cell()
            valuecell.content = "%s" % x[1]
            
            valuepctcell = htmlutils.Cell()
            valuepctcell.content = "%d&#37" % (100*x[1]/total)
            
            row.tooltip = self.getReport(self.level2dict[x[0]])
            row.tooltiptitle = tr.tr(x[0]).replace("'","")
            
            row.appendCells([namecell,valuecell,valuepctcell])
            table.addRow(row)

        return table.render()

    
    def __len__(self):
        '''The size of this dictionary (or collection).'''
        return len(self.realdict)
    
    def keys(self):
        '''Returns the keys in this dictionary (or collection).'''
        return self.realdict.keys()
    
    def values(self):
        '''Returns the counts in this dictionary (or collection).'''
        return self.realdict.values()
    
    def __getitem__(self,key):
        '''Retrieve one term and its count, by specifying the name of the
        term as key.'''
        return self.realdict[key]


'''
    Configuration parameters used globally
'''
verbose = False
testmode = True
cacheThesauri = True

    
def s(message):
    '''Print message to console if in verbose mode.
    Allows for debug printing.'''
    if (verbose):
        print message

def nencode(x):
    '''Encode string in unicode. Ignore any encoding errors 
    (no UnicodeError exceptions will be raised).'''
    #@@@TEST
    #if x is None:
    #    return x
    return x.encode("utf-8", "ignore")
    
def nencode_list(x):
    '''Encode a whole list in unicode. Encoding ignores any
    errors.'''
    return map(nencode, x)




        
'''Dependency on CSV standard lib'''
import csv
def unicode_csv_reader(utf8_data, **kwargs):
    '''Reads a CSV represented as a unicode string.
    Possible to specify additional arguments to csv reader.
    This is a generator function: Returns a generator object.
    Call next() consecutively until an exception is thrown.
    Each next() call will return a new line in the CSV,
    represented as a list, encoded in unicode.'''
    'TODO: heeft csv reader mooiere methode om encoding te specifiëren? nope, komt rechtstreeks uit python manual'
    csv_reader = csv.reader(utf8_data,  **kwargs)
    for row in csv_reader:
        yield [unicode(cell, 'utf-8') for cell in row]        



def ensureUnicode(input, encoding="utf-8"):
    '''Make sure string is decoded unicode string. If it is
    a regular bytestring, decode it, using the utf-8 charset
    by default, unless specified otherwise. Makes sure that
    the result is a unicode string, also if the specified
    type of input is not a string or unicode string.'''
    #print "input: %s (%s)  encoding: %s (%s)\n" % (input, type(input), encoding, type(encoding))
    if input == None:
        return unicode("")
    if(isinstance(input, str)):
        return unicode(input, encoding=encoding, errors="replace")
    if(isinstance(input, unicode)):
        return input
    '''
    if(isinstance(input, list)):
        i = 0
        while i < len(input):
            input[i] = ensureUnicode(input[i], encoding)
        return input
    if(isinstance(input, dict)):
        keys = input.keys()
        for key in keys:
            entry = input[key]
            del input[key]
            key = ensureUnicode(key, encoding)
            input[key] = ensureUnicode(entry, encoding)
    '''
    return unicode("")


def centerWindow(window):
        window.update_idletasks()
        w= window["width"]!=0 and window["width"] or window.winfo_width()
        h= window["height"]!=0 and window["height"] or window.winfo_height()
        ws,hs = window.winfo_screenwidth(),window.winfo_screenheight()
        window.geometry('%dx%d+%d+%d' % (w, h, (ws/2) - (w/2), (hs/2) - (h/2)))
        window.geometry("") # To enable pack_propagate again (so window dimensions resize with the widgets placed in it)
     