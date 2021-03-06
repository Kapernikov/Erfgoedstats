# -*- coding: utf-8 -*-
'''
Utility helper functions

Created on Jan 7, 2011

@author: kervel
'''

from operator import itemgetter
import htmlutils

import tr


global __maxDetail 
__maxDetail = 1000

def getMaxDetail():
    global __maxDetail
    return __maxDetail


def setMaxDetail(m):
    global __maxDetail
    __maxDetail = m

class UserError(Exception):
    '''
        UserError is an error with a user-readable message (msg)
    '''
    def __init__(self,rootcause,stacktrace,msg):
        '''
            rootcause: the exception that caused this exception
            stacktrace: the stacktrace of the root cause
            msg: the user-readable message
        '''
        self.msg = msg
        self.stacktrace = stacktrace
        self.rootcause = rootcause
    
    def __str__(self):
        return "UserError: "+self.message
    
    
class CounterDict:
    ''' a dictionary  like this:
    
     {
         word1: 100,
         word2: 150,
         word3: 300
     }
    
    meaning word1 occurred 100 times, word2 occured 150 times, word3 occured 300 times
    
    this class also supports 2-level deep hierarchies and has a method to turn them in a html report
    
    '''
    def __init__(self):
        self.realdict = {}
        self.level2dict = {}
    
    def count(self, name, level2=None):
        '''Indicate or count one occurence of a specified term.
        Creates that term with count one if it was not counted before.
        level2 is optional, when a second level of hierarchy is needed.
        ''' 
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
    
    def writeL2Report(self,writer):
        ''' writes a 2-level hierarchic report from this dictionary to the given writer (or file)'''
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
            
            if (len(self.level2dict[x[0]].keys()) <= getMaxDetail()):
                row.tooltip = self.getReport(self.level2dict[x[0]])
                row.tooltiptitle = tr.tr(x[0]).replace("'","")
            
            row.appendCells([namecell,valuecell,valuepctcell])
            table.addRow(row)

        table.renderTo(writer)

    
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
    if input == None:
        return unicode("")
    if(isinstance(input, str)):
        return unicode(input, encoding=encoding, errors="replace")
    if(isinstance(input, unicode)):
        return input

    return unicode("")

def packDocMap(map, fields_to_keep=None):
    '''
        reduce memory usage by:
           * only keeping the fields that are in fields_to_keep (list)
           * not using unicode but utf-8 strings
    '''
    m = {}
    for k in map.keys():
        k_ = k
        if (type(k) == unicode):
            k_ = k.encode('utf-8')
        if (fields_to_keep is None or k_ in fields_to_keep):
            l = []
            for val in map[k]:
                val_ = val
                if (type(val) == unicode):
                    val_ = val.encode('utf-8')
                l.append(val_)
            m[k_]=l
    return m

def centerWindow(window):
        window.update_idletasks()
        w= window["width"]!=0 and window["width"] or window.winfo_width()
        h= window["height"]!=0 and window["height"] or window.winfo_height()
        ws,hs = window.winfo_screenwidth(),window.winfo_screenheight()
        window.geometry('%dx%d+%d+%d' % (w, h, (ws/2) - (w/2), (hs/2) - (h/2)))
        window.geometry("") # To enable pack_propagate again (so window dimensions resize with the widgets placed in it)
     