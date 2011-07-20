'''
Utility helper functions

Created on Jan 7, 2011

@author: kervel
'''

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
testmode = False

    
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



def kv2map(k, v, charset=None):
    '''Convert a list of keys and list of values to
    a map with a one-to-one mapping of keys and values.
    Entries with empty key or value will be ignored.
    This map can contain multiple values for one key, 
    in which case that key will have a list as value.
    If charset is specified strings will be decoded from
    this charset, and converted to unicode.'''
    map = {}
    for i in range(len(k)):
        # check of waarde leeg (--> negeren)
        value = v[i]
        if value is None:
            continue
        value = value.strip()
        if len(value)==0:
            continue

        # check of key leeg (--> negeren)
        key = k[i]
        if key is None:
            continue
        key = key.strip()
        if len(key)==0:
            continue
        
        # beiden zijn significant
        if (charset):
            key = key.decode(charset).encode("utf-8","ignore")
            value = value.decode(charset).encode("utf-8","ignore")
            
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
    for f in element:
        value = f.text
        
        # check of waarde leeg (--> negeren)
        if value is None:
            if "value" in f.attrib.keys():
                value = f.attrib["value"]
        if value is None:
            continue
        value = value.strip()
        if  len(value) == 0:
            continue
        
        # waarde is niet leeg
        value = value.encode('utf-8', "ignore")
        fieldname = f.tag.encode('utf-8', "ignore")
        if (fieldname in map):
            oldv = map[fieldname]
            if (type(oldv) is list):
                oldv.append(value)
            else:
                map[fieldname] = [oldv, value]
        else:
            map[fieldname] = value
    return map
