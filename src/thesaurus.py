'''
Representation and analysis of thesauri

Created on Jan 7, 2011

@author: kervel
'''

from xml.etree.ElementTree import ElementTree
import utils
import tr
import os

'''The fields for which a thesaurus simularities
report should be created. For each of these fields
a separate table will be created in the report.'''
fields_to_check = [
                   "object_name",
                   "material",
                   "technique",
                   "object_category"
        ]

class Thesaurus:
    '''Represents a thesaurus. Contains a list of terms.'''
    def __init__(self, name='Unknown'):
        self.terms = {}
        self.name = name
        pass
    
    def addTerm(self, term):
        '''Add a term to this thesaurus. Term should be a term object.'''
        self.terms[term.getTermName().lower()] = term
        
    def containsTerm(self,word):
        '''Check whether term is in thesaurus. Word is case insensitive.'''
        return word.lower() in self.terms
    
    def getTerm(self,word):
        '''Searches for word in thesaurus, case insensitive. Returns a term object.
        Only supply a word that is in thesaurus, test with containsTerm.'''
        return self.terms[word.lower()]
    
    def parseDefaultAdlibDoc(self, filename):
        '''Parse adLib XML thesaurus from specified filename.'''
        the_doc = ElementTree(file=filename)
        self.parseAdlibDoc(the_doc)

    def parseTextFile(self, filename):
        '''Parse thesaurus from plain text file with given filename'''
        fil = file(filename,'r')
        x = fil.readline().decode("iso-8859-15").encode("utf-8")
        while x:
            word = x[:-1]
            if (word != ''):
                t = Term()
                t.params["term"] = word
                self.addTerm(t)
            x = fil.readline().decode("iso-8859-15").encode("utf-8")
        fil.close()

    
    def parseAdlibDoc(self, doc):
        '''Parse records from XML adlib doc at specified
        filename.'''
        assert isinstance(doc, ElementTree)
        for x in doc.findall(".//record"):
            t = Term()
            t.parseAdlibDoc(x)
            self.addTerm(t)
    
    def getStatusOfWord(self,word):
        '''Compare a specified word with the thesaurus. It will
        either be a preferred term, an unpreferred synonym, or
        not exist in thesaurus.'''
        'TODO: lots of input testing here, verify why'
        if (word is None or len(word) == 0):
            return "Leeg (niet ingevuld)"
        assert isinstance(word, str) or isinstance(word, unicode)
        if (not self.containsTerm(word)):
            return "Niet in de %s thesaurus" % (self.name)
        term = self.getTerm(word)
        if (term.getUse() is not None):
            return "Niet de voorkeurterm"
        return "Voorkeurterm"
    
    def getCollectionThesaurusReport(self, collection):
        '''Generate a collection with thesaurus comparison report in HTML format of a specified
        museum collection. This report is structured with a counter dict and creates
        a table per field, for each field in fields_to_check.'''
        html = ""
        html += "<h2>%s Thesaurus</h2>\n" % self.name
        for f in fields_to_check:
            # start counter dict
            statusmap = utils.CounterDict()
            for object in collection.objects:
                'TODO: what if field does not exist?'
                fieldvalue = object[f]
                'TODO: vies''' 
                if (type(fieldvalue) != list):
                    statusmap.count(self.getStatusOfWord(fieldvalue))
                else:
                    for value in fieldvalue:
                        statusmap.count(self.getStatusOfWord(value))
            html += "<h3>%s Thesaurus overeenkomst: %s</h3>\n" % (self.name, tr.tr(f))
            html += statusmap.getReport()
        return html
    
    
    def getThesaurusThesaurusReport(self,thesaurus_to_check):
        '''Generate a thesaurus with thesaurus comparison report in HTML format 
        of a specified adlib thesaurus. This adlib thesaurus was produced by filling in the
        museum collection data in adlib.
        This report is structured with a counter dict and creates one table with the different
        word statuses of all words in the dictionary.'''
        html = ""
        html += "<h2>Vergelijking met %s</h2>\n" % (self.name)
        statusmap = utils.CounterDict()
        for term in thesaurus_to_check.terms.keys():
            statusmap.count(self.getStatusOfWord(term))
        html += statusmap.getReport()
        return html


class Term:
    '''Represents a term in a thesaurus. A term contains a
    term name (or possibly an english term name), and an
    optional use parameter. If use is specified, this term
    is a synonym and not the preferred term for the concept
    it represents. If specified, use refers to the name of the
    term that is preferred instead.'''
    def __init__(self):
        self.params = {}
    
    def parseAdlibDoc(self, element):
        '''Fill the parameters of this term by parsing
        an XML element. The tags in the XML are mapped
        one to one to the params of this term, but they
        are expected to  contain at least a term or 
        english_term tag with value, and possible a
        use parameter. Tags with empty values are 
        ignored and parameter values can contain multiple
        values (in which case they become a list).'''
        'TODO: you cant be certain that required fields will be present!'
        for x in element:
            if x.text is None:
                continue
            value = x.text.strip()
            if len(value) == 0:
                continue
            value = utils.nencode(value)
            #@@@TEST
            #fieldname = utils.nencode(x.tag)
            fieldname = x.tag
            if fieldname in self.params:
                l = self.params[fieldname]
                if type(l) is list:
                    l.append(value)
                else:
                    self.params[fieldname] = [l, value]
            else:
                self.params[fieldname] = value    

    def getTermName(self):
        '''Returns the name of this term. The parameter
        "term" is preferred (usually dutch name), otherwise
        "english_term" is returned.'''
        if not "term" in self.params:
            return "english_term"
        'TODO: what if term is also not present?'
        return self.params["term"]
    
    def getUse(self):
        '''Returns none if this is a preferred term, returns
        the name of the preferred term that is a synonym if
        this term is not the preferred one.'''
        if "use" in self.params.keys():
            return self.params["use"]
        return None
 
__thesauri = {}
AmMoveName = "AM-MovE"
AATNedName = "AAT-Ned"
MotName = "MOT"


def getThesauri():
    '''Singleton access point for all thesauri. Upon first
    call, thesauri are parsed and loaded into memory. Subsequent
    calls will be much faster. Returns a list of all thesauri.'''
    'TODO: try loading thesauri from cached txt files if they exist, instead of parsing the XML files. This is much faster.'
    if len(__thesauri) == 0:
        initThesauri()
    return __thesauri.values()

def getThesaurus(name):
    '''Singleton access point for a specific named thesaurus.
    Upon first call, thesauri are parsed and loaded into memory. 
    Subsequent calls will be much faster.'''
    if len(__thesauri) == 0:
        initThesauri()
    return __thesauri[name]
    

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
    
    # In order of a draw, choose the status from the highest ranked thesaurus
    '''Order by which thesauri are ranked. The more to the left, the higher the rank.'''
    thesaurus_pref_order = ["MOT","AM-MovE","AAT-Ned"]
    
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
        if (word is None or len(word) == 0):
            return "Leeg (niet ingevuld)"
        assert isinstance(word, str) or isinstance(word, unicode)
        if (th.containsTerm(word)):
            term = th.getTerm(word)
            if (term.getUse() is not None):
                tmpstatus = bestStatus(tmpstatus,("niet_voorkeur",th.name,"Niet voorkeursterm %s" % (th.name)))
            else:
                tmpstatus = bestStatus(tmpstatus,("voorkeur",th.name,"Voorkeursterm %s" % (th.name)))
    if (tmpstatus is None):
        return "Eigen term"
    return tmpstatus[2]


def getCollectionThesauriReport(collection):
    '''Generates a HTML report for each fields_to_check,
    of all objects with the best scores of those fields.
    A counterDict style table is created for each
    field. '''
    html = ""
    html += "<h2>Thesaurus samenvattingen</h2>\n"
    for f in fields_to_check:
        statusmap = utils.CounterDict()
        for object in collection.objects:
            fieldvalue = object[f]
            if (type(fieldvalue) != list):
                statusmap.count(getThesauriStatusOfWord(fieldvalue))
            else:
                for value in fieldvalue:
                    statusmap.count(getThesauriStatusOfWord(value))
        html += "<h3>Thesaurus samenvatting: %s</h3>\n" % (tr.tr(f))
        html += statusmap.getReport()
    return html
    
    
def initThesauri():
    '''Initialize thesauri by parsing them from XML files.'''
    utils.s("INITIALIZING default thesauri (this might take some time) ...")
    try:
        utils.s("parsing MOVE thesaurus")
        thesauruspad = os.path.join(os.path.dirname(__file__), '..', 'data', 'reference', 'Am_Move_thesaurus06_10.xml')
        AmMoveThesaurus = Thesaurus('AM-MovE')
        AmMoveThesaurus.parseDefaultAdlibDoc(thesauruspad)
        AmMoveThesaurus.name = AmMoveName
        __thesauri[AmMoveThesaurus.name] = AmMoveThesaurus
    except IOError as e:
        print("({})".format(e))
    
    try:
        utils.s("parsing AAT thesaurus")
        thesauruspad = os.path.join(os.path.dirname(__file__),'..', 'data', 'reference', 'aat2000.xml')
        AAT2000 = Thesaurus('AAT-Ned')
        AAT2000.parseDefaultAdlibDoc(thesauruspad)
        AAT2000.name = AATNedName
        __thesauri[AAT2000.name] = AAT2000
    except IOError as e:
        print("({})".format(e))
        
    try:
        utils.s("parsing MOT name list")
        MOT_name_list =  Thesaurus('MOT')
        MOT_name_list.parseTextFile(os.path.join(os.path.dirname(__file__), '..', 'data', 'MOT', 'mot-naam.txt'))
        MOT_name_list.name = MotName
        __thesauri[MotName] = MOT_name_list
    except IOError as e:
        print("({})".format(e))
        
    utils.s("DONE thesaurus initialisation")

def notInAnyDocFilter(docmap):
    '''Docmapfilter that finds docmaps that contain
    a term that is not in any thesaurus.'''
    for t in getThesauri():
        if t.containsTerm(docmap['term']):
            return False
    return True
