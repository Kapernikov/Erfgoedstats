# -*- coding: utf-8 -*-
'''
Representation and analysis of thesauri

Created on Jan 7, 2011

@author: kervel
'''

from xml.etree.ElementTree import ElementTree, iselement
import utils
import tr
import os
import pickle
import copy
import adlibstats
import inputfiletable

'''The fields for which a thesaurus simularities
report should be created. For each of these fields
a separate table will be created in the report.'''
fields_to_check = [
                   "object_name",
                   "material",
                   "technique",
                   "object_category"
        ]

valid_filetypes = ['Adlib XML Thesaurus', 'TXT Thesaurus']

'''Order by which thesauri are ranked. The more to the left, the higher the rank.
This is the default order, will be overwritten when setCustomThesauri() is called.'''
thesaurus_pref_order = ["MOT","AM-MovE","AAT-Ned"]


customThesauri = inputfiletable.TEntries()
import inputfileformat

class Thesaurus:
    '''Represents a thesaurus. Contains a list of terms.'''
    def __init__(self, name=u'Unknown'):
        self.terms = {}
        self.name = utils.ensureUnicode(name)
        pass
    
    def parseAdlibDoc(self,filename):
        inputfileformat.parseSAXFile(filename, self)
        
    def addTerm(self, term):
        '''Add a term to this thesaurus. Term should be a term object
        and should be valid, otherwise it will not be added.'''
        #print "term: %s (%s)" % (term.getTermName(), type(term.getTermName()))
        if(isinstance(term, Term) and term.isValid()):
            self.terms[term.getTermName().lower()] = term
        
    def containsTerm(self,word):
        '''Check whether term is in thesaurus. Word is case insensitive.'''
        word = utils.ensureUnicode(word)
        return word.lower() in self.terms
    
    def getTerm(self,word):
        '''Searches for word in thesaurus, case insensitive. Returns a term object.
        Only supply a word that is in thesaurus, test with containsTerm.'''
        word = utils.ensureUnicode(word)
        return self.terms[word.lower()]
    
    def getAllTerms(self):
        '''Returns all terms in this thesaurus'''
        return self.terms.values()
    
    def parseDefaultAdlibDoc(self, filename):
        '''Parse adLib XML thesaurus from specified filename.
        Will check if there is a cached plaintext version of the thesaurus stored
        already. If so, this will be parsed instead of the XML version,
        because this is a lot faster.'''
        filename = utils.ensureUnicode(filename)
        if utils.cacheThesauri and cachedVersionExists(filename):
            print "    - Loading thesaurus from previously cached file %s" % getCachedVersionFilename(filename)
            cachedThesaurus = loadCachedVersion(filename)
            self.terms = cachedThesaurus.terms
            self.name = cachedThesaurus.name
            return
        inputfileformat.parseSAXFile(filename, self)
        if utils.cacheThesauri:
            print "    - Caching thesaurus to file %s" % getCachedVersionFilename(filename)
            createCachedVersion(self, filename)
        
    def onRecord(self,docmap):
        t = Term()
        t.parseDocmap(docmap)
        self.addTerm(t)
            
    def parseTextFile(self, filename):
        '''Parse thesaurus from plain text file with given filename.'''
        fil = inputfileformat.getFileDescriptor(filename)
        for line in fil:
            line = line.replace("\n","")
            line = line.replace("\r","")
            line = line.strip()
            # leave off newline characters
            word = utils.ensureUnicode(line)
            if word:
                t = Term()
                t.addField(u"term", word)
                self.addTerm(t)

    def getStatusOfWord(self,word):
        '''Compare a specified word with the thesaurus. It will
        either be a preferred term, an unpreferred synonym, or
        not exist in thesaurus.'''
        word = utils.ensureUnicode(word)
        if (not word):
            return u"Leeg (niet ingevuld)"
        if (not self.containsTerm(word)):
            return u"Niet in de %s thesaurus" % (self.name)
        term = self.getTerm(word)
        if (term.getUse() is not None):
            return u"Niet de voorkeurterm"
        return u"Voorkeurterm"
    
    def writeCollectionThesaurusReport(self, writer, collection):
        '''Comparison between this thesaurus and the specified collection.
        Generate a collection with thesaurus comparison report in HTML format of a specified
        museum collection. This report is structured with a counter dict and creates
        a table per field, for each field in fields_to_check.'''
        
        writer.write("<h2>%s Thesaurus</h2>\n" % self.name)
        for f in fields_to_check:
            # start counter dict
            statusmap = utils.CounterDict()
            for object in collection.objects:
                fieldvalue = object[f]
                for value in fieldvalue:
                    statusmap.count(self.getStatusOfWord(value),value)
            writer.write("<h3>%s Thesaurus overeenkomst: %s</h3>\n" % (self.name, tr.tr(f)))
            statusmap.writeL2Report(writer)
    
    
    def writeThesaurusThesaurusReport(self,writer,thesaurus_to_check):
        '''Comparison between this (adlib) thesaurus and another specified reference thesaurus.
        Generate a thesaurus with thesaurus comparison report in HTML format 
        of a specified adlib thesaurus. This adlib thesaurus was produced by filling in the
        museum collection data in adlib.
        This report is structured with a counter dict and creates one table with the different
        word statuses of all words in the dictionary.'''
        
        writer.write("<h2>Vergelijking met %s</h2>\n" % (self.name))
        statusmap = utils.CounterDict()
        for term in thesaurus_to_check.terms.keys():
            statusmap.count(self.getStatusOfWord(term),term)
        statusmap.writeL2Report(writer)


class Term:
    '''Represents a term in a thesaurus. A term contains a
    term name (or possibly an english term name), and an
    optional use parameter. If use is specified, this term
    is a synonym and not the preferred term for the concept
    it represents. If specified, use refers to the name of the
    term that is preferred instead.'''
    def __init__(self):
        self.params = {}
    
    def parseDocmap(self, docmap):
        self.params = docmap

    def addField(self, fieldname, value):
        if(not fieldname or not value):
            return
        fieldname = utils.ensureUnicode(fieldname)
        value = utils.ensureUnicode(value)
        if(fieldname in self.params):
            self.params[fieldname].append(value)
        else:
            self.params[fieldname] = [value]
            
    def removeField(self, fieldname):
        '''Removes the parameter with the given name, if it exists.'''
        if not fieldname:
            return
        fieldname = utils.ensureUnicode(fieldname)
        if fieldname in self.params:
            del self.params[fieldname]

    def getTermName(self):
        '''Returns the name of this term. The parameter
        "term" is preferred (usually dutch name), otherwise
        "english_term" is returned.'''
        if not "term" in self.params:
            return self.getSingleFieldValue(u"english_term")
        return self.getSingleFieldValue(u"term")

    def getSingleFieldValue(self, fieldname):
        '''Returns only the first value of the specified field,
        if it is available'''
        values = self.getFieldValues(fieldname)
        if(len(values) < 1):
            return u""
        return values[0]
        
    def getFieldValues(self, fieldname):
        '''Return the values of the field with specified name'''
        if not fieldname in self.params:
            return []
        return self.params[fieldname]
    
    def getFieldNames(self):
        '''Returns all available field names in this term.'''
        return self.params.keys()
    
    def getUse(self):
        '''Returns none if this is a preferred term, returns
        the name of the preferred term that is a synonym if
        this term is not the preferred one.'''
        if "use" in self.params.keys():
            return self.params["use"]
        return None
    
    def isValid(self):
        '''Verify that the minimal required field for this
        term are filled, so that it's usable'''
        return ('term' in self.params or 'english_term' in self.params)
 
__thesauri = {}
AmMoveName = "AM-MovE"
AATNedName = "AAT-Ned"
MotName = "MOT"


def cachedVersionExists(xmlFilename):
    '''Determines whether a plaintext file is cached
    for this xml thesaurus file.'''
    cachedFile = getCachedVersionFilename(xmlFilename)
    if not cachedFile:
        return False
    return os.path.exists(cachedFile)
    
def getCachedVersionFilename(xmlFilename):
    '''Returns the filename to the plaintext cached version
    of an XML thesaurus. Will return an empty string if no
    cached file is found, or if file is not an xml file.'''
    xmlFilename = utils.ensureUnicode(xmlFilename)
    if not xmlFilename:
        return None
    if not xmlFilename.lower().endswith('.xml'):
        return None
    plaintextFilename = utils.ensureUnicode(os.path.basename(xmlFilename))
    return plaintextFilename.replace('.xml', '_cached.txt')

def createCachedVersion(thesaurus, filename):
    '''Create a cached version of a Thesaurus object
    that can be loaded much more quickly than an xml file.
    Cached file will have specified filename.
    Does nothing if supplied file is not a thesaurus object.'''
    if not isinstance(thesaurus, Thesaurus):
        return
    # Create a copy of this thesaurus, and only keep the important properties
    minimalThesaurus = copy.deepcopy(thesaurus)
    for term in minimalThesaurus.getAllTerms():
        for paramName in term.getFieldNames():
            if(paramName not in [ "term", "english_term", "use"] ):
                term.removeField(paramName)
    # pickler uses the old binary protocol (we don't use new style classes so this is the best choice)
    pickler = pickle.Pickler(open(getCachedVersionFilename(filename), 'wb'), 1)
    pickler.dump(minimalThesaurus)
        
def loadCachedVersion(filename):
    '''Loads a thesaurus object from a cached file.
    Will return None if file does not exist or is not the expected
    object.'''
    if not os.path.exists(filename):
        return None
    unpickler = pickle.Unpickler(open(getCachedVersionFilename(filename), 'rb'))
    thesaurus = unpickler.load()
    if not isinstance(thesaurus, Thesaurus):
        return None
    return thesaurus

def getThesauri():
    '''Singleton access point for all thesauri. Upon first
    call, thesauri are parsed and loaded into memory. Subsequent
    calls will be much faster. Returns a list of all thesauri.'''
    if len(__thesauri) == 0:
        initThesauri()
    return __thesauri.values()

def getThesaurus(name):
    return getThesauri()[name]
    

def bestStatus(existingstatus, newstatus):
    '''From the two statuses, returns the status
    that is ranked the highest (a max for statuses).
    If both statuses are equal, the status from the
    thesaurus that is ranked highest is picked.
    Status parameters are a list with [status, thesaurusname].'''
    if (existingstatus is None):
        return newstatus
    if (existingstatus[0] == "niet_voorkeur" and newstatus[0] == "voorkeur"):
        return newstatus
    if (existingstatus[0] == "voorkeur" and newstatus[0] == "niet_voorkeur"):
        return existingstatus
    
    # In case of a draw, choose the status from the highest ranked thesaurus  
    idx1 = thesaurus_pref_order.index(existingstatus[1])
    idx2 = thesaurus_pref_order.index(newstatus[1])
    
    if (idx2 > idx1):
        return existingstatus
    else:
        return newstatus


def getThesauriStatusOfWord(word):
    '''Get best status from hightest rated thesaurus for the given word.'''
    tmpstatus = None
    for th in getThesauri():
        word = utils.ensureUnicode(word)
        if not word:
            return u"Leeg (niet ingevuld)"
        if (th.containsTerm(word)):
            term = th.getTerm(word)
            if (term.getUse() is not None):
                tmpstatus = bestStatus(tmpstatus,("niet_voorkeur",th.name,"Niet voorkeursterm %s" % (th.name)))
            else:
                tmpstatus = bestStatus(tmpstatus,("voorkeur",th.name,"Voorkeursterm %s" % (th.name)))
    if (tmpstatus is None):
        return u"Eigen term"
    return utils.ensureUnicode(tmpstatus[2])


def writeCollectionThesauriReport(writer,collection):
    '''Comparison between all loaded reference thesauri and the specified collection.
    Generates a HTML report for each fields_to_check,
    of all objects with the best scores of those fields.
    A counterDict style table is created for each
    field. '''
    if (len(getThesauri()) == 0):
        pass
    
    writer.write("<h2>Thesaurus samenvattingen</h2>\n")
    for f in fields_to_check:
        statusmap = utils.CounterDict()
        for object in collection.objects:
            fieldvalue = object[f]
            for value in fieldvalue:
                statusmap.count(getThesauriStatusOfWord(value),value)
        writer.write("<h3>Thesaurus samenvatting: %s</h3>\n" % (tr.tr(f)))
        statusmap.writeL2Report(writer)
    
    
def setCustomThesauri(thesauri):
    '''Set a custom list of reference thesauri. The param should be a list
    of dicts containing "name", "path" and "type". The order in which the
    thesauri are specified counts as the importance of the thesauri.
    The first thesaurus in the list is the most important, and so on.
    Calling this method sets custom reference thesauri, which will override
    the defaults when calling initThesauri(). Should be called before initThesauri()
    and should not be called more than once. Make sure that thesauri have unique names!'''
    
    if not thesauri or not isinstance(thesauri, inputfiletable.TEntries):
        return
    global customThesauri
    customThesauri.clear()
    for entry in thesauri.values:
        if entry.type not in valid_filetypes:
            utils.s ('    ! ERROR: no valid file type (%s) for reference thesaurus "%s" specified' % (entry.type, entry.name))
            continue
        if not os.path.exists(entry.path):
            utils.s( '    ! ERROR: reference thesaurus "%s" with filename "%s" does not exist' % (entry.name, entry.path))
            continue
        
        customThesauri.append(entry)
    global init_done_already
    global __thesauri
    init_done_already = False
    __thesauri.clear()

init_done_already = False
def initThesauri():
    '''Initialize thesauri by parsing them from XML files. Only thesauri for which
    the files are found are loaded, so it is safe to call this method when not all reference
    thesauri are present.'''
    global thesaurus_pref_order
    global init_done_already
    global customThesauri
    if (init_done_already):
        return
    init_done_already = True
    # Custom reference thesauri specified, load those
    global thesaurus_pref_order
    thesaurus_pref_order = []
    customThesauri.sort()
    if len(customThesauri.values) > 0:
        utils.s("    - INITIALIZING custom thesauri (this might take some time) ...")
        for entry in customThesauri.values:
            thesaurus = Thesaurus(entry.name)
            if entry.type == 'Adlib XML Thesaurus':
                thesaurus.parseDefaultAdlibDoc(entry.path)
            elif entry.type == 'TXT Thesaurus':
                thesaurus.parseTextFile(entry.path)
            else:
                utils.s('    ! ERROR: reference thesaurus "%s" is of unknown type (%s), don\'t know how to parse it' % (entry.name, entry.type))
                continue
            __thesauri[thesaurus.name] = thesaurus
            thesaurus_pref_order.append(thesaurus.name)
        
        utils.s("    - DONE thesaurus initialisation %s" % str(thesaurus_pref_order))
        # Drop out here, do not load default thesauri
        return
    
    thesaurus_pref_order = ["MOT","AM-MovE","AAT-Ned"]

    # Else, try loading the defaults
    utils.s("    - INITIALIZING default thesauri (this might take some time) ...")
    thesauruspad = os.path.join(os.path.dirname(__file__), '..', 'data', 'reference', 'Am_Move_thesaurus06_10.xml')
    if(os.path.exists(thesauruspad)):
        try:
            utils.s("    - parsing MOVE thesaurus")
            AmMoveThesaurus = Thesaurus('AM-MovE')
            AmMoveThesaurus.parseDefaultAdlibDoc(thesauruspad)
            AmMoveThesaurus.name = AmMoveName
            __thesauri[AmMoveThesaurus.name] = AmMoveThesaurus
        except IOError as e:
            print("({})".format(e))
    elif 'AM-MovE' in thesaurus_pref_order:
        thesaurus_pref_order.remove('AM-MovE')
    
    thesauruspad = os.path.join(os.path.dirname(__file__),'..', 'data', 'reference', 'aat2000.xml')
    if(os.path.exists(thesauruspad)):
        try:
            utils.s("    - parsing AAT thesaurus")
            AAT2000 = Thesaurus('AAT-Ned')
            AAT2000.parseDefaultAdlibDoc(thesauruspad)
            AAT2000.name = AATNedName
            __thesauri[AAT2000.name] = AAT2000
        except IOError as e:
            print("({})".format(e))
    elif 'AAT-Ned' in thesaurus_pref_order:
        thesaurus_pref_order.remove("AAT-Ned")
    
    thesauruspad = os.path.join(os.path.dirname(__file__), '..', 'data', 'MOT', 'mot-naam.txt')
    if(os.path.exists(thesauruspad)):
        try:
            utils.s("    - parsing MOT name list")
            MOT_name_list =  Thesaurus('MOT')
            MOT_name_list.parseTextFile(thesauruspad)
            MOT_name_list.name = MotName
            __thesauri[MotName] = MOT_name_list
        except IOError as e:
            print("({})".format(e))
    elif 'MOT' in thesaurus_pref_order:
        thesaurus_pref_order.remove("MOT")
        
    utils.s("    - DONE thesaurus initialisation %s" % str(thesaurus_pref_order))

def notInAnyDocFilter(docmap):
    '''Docmapfilter that finds docmaps that contain
    a term that is not in any thesaurus.'''
    for t in getThesauri():
        if t.containsTerm(docmap['term']):
            return False
    return True
