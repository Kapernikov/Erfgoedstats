# -*- coding: utf-8 -*-
'''
Utility helper functions

Created on Jan 7, 2011

@author: kervel
'''

from xml.etree.ElementTree import iselement
from operator import itemgetter

import tr

class CounterDict:
    '''Wrapper class around a dictionary that allows storing key/value pairs.
    The key is the name of a term, the value is defined as its count (the number
    of occurences of that property).
    Has some utility functions, and is able to generate a HTML report from itself.'''
    def __init__(self):
        self.realdict = {}
    
    def count(self, name):
        '''Indicate or count one occurence of a specified term.
        Creates that term with count one if it was not counted before.''' 
        if name not in self.realdict:
            self.realdict[name] = 1
        else:
            self.realdict[name] = self.realdict[name] + 1
        
    def getSortedResult(self, reverse=True):
        '''Returns a sorted list of (term, count) tuples, sorted by their number of occurences.
        The term with the most occurences comes first.''' 
        return sorted(self.realdict.iteritems(), key=itemgetter(1), reverse=reverse)
        
    def getReport(self):
        '''Generate a HTML report from this dictionary.'''
        html = ""
        html += '<table class="countertable" border="0">'
        html += "<thead><tr><th>count</th><th>%</th><th>item</th></tr></thead>\n<tbody>"
        total = sum(self.values())
        for x in self.getSortedResult():
            html += "<tr>\n<td>%s</td>\n<td>%d&#37</td>\n<td>%s</td>\n</tr>" % (x[1], 100*x[1]/total , tr.tr(x[0]).replace("'",""))
        html += "</tbody></table>"
        return html
    
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



def kv2map(k, v):
    '''Convert a list of keys and list of values to
    a map with a one-to-one mapping of keys and values.
    Entries with empty key or value will be ignored.
    This map can contain multiple values for one key, 
    in which case that key will have a list as value.
    '''
    map = {}
    if(not isinstance(k, list) or not isinstance(v, list)):
        return map
    for i in range(len(k)):
        # check of waarde leeg (--> negeren)
        if(i >= len(v)):
            continue
        value = ensureUnicode(v[i])
        if not value:
            continue
        value = value.strip()
        if len(value)==0:
            continue

        key = ensureUnicode(k[i])
        key = key.strip()
        # check of key leeg (--> negeren)
        if not key:
            continue
            
        if (key in map):
            oldv = map[key]
            if (type(oldv) is list):
                oldv.append(value)
            else:
                map[key] = [oldv, value]
        else:
            map[key] = value
    return map
        
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

def doc2map(element):
    '''Convert XML element to a map.
    Map will contain tag, value pairs, encoded in unicode.
    Values can be represented in XML either as text in the
    tag element, or as value="" attribute of the element.
    Values are stripped from leading and trailing spaces. 
    Tags with empty text will be ignored.
    The returned map can contain multiple values for one key,
    in which case the a lookup for that key will return a list
    of values.'''
    map = {}
    if(not iselement(element)):
        return map
    for f in element:
        value = f.text
        
        # check of waarde leeg (--> negeren)
        if value is None:
            if "value" in f.attrib.keys():
                value = f.attrib["value"]
            else:
                continue
        value = ensureUnicode(value)
        value = value.strip()
        if len(value) == 0:
            continue
        
        # waarde is niet leeg
        #value = value.encode('utf-8', "ignore")
        #fieldname = f.tag.encode('utf-8', "ignore")
        fieldname = ensureUnicode(f.tag)
        if(not fieldname):
            continue
        if (fieldname in map):
            map[fieldname].append(value)
        else:
            map[fieldname] = [value]
    return map

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
     