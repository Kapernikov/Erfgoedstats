'''

    this file tries to read input files and parse them into "doc maps"
    a doc map is one "record" of a file and is a map:
        * the keys of the map are the field names
        * the values of the map are LISTS containing the field values (this way, multiple valued fields are supported)
        
    an example of a doc map:
        {
            "objectname" : [ "schop", "gereedschap" ]
            "material" : [ "aardewerk" ]
            "object_number" : [ "TS0004" ] 
        }
        
    this module can convert both CSV files and XML files to docmaps. it tries to ensure utf-8 wherever possible

'''
import utils
import chardet, codecs
import gc

##################
#### FILE ENCODING
##################

import sys
reload(sys)
''' otherwise python SAX parser defaults to ascii, giving errors, because getFileDescriptor ensures unicode '''
sys.setdefaultencoding('utf-8')


def autoDetectEncodingFromFile(filename):
    result = chardet.detect(open(filename, mode="rb").read(4096))
    encoding = result["encoding"]
    confidence = result["confidence"]
    return encoding

def getFileDescriptor(filename, encoding=None):
    ''' returns a filedescriptor for a file that is guaranteed to be unicode'''
    if not encoding:
        encoding=autoDetectEncodingFromFile(filename)
    file = codecs.open(filename, mode='rU', encoding=encoding, errors="replace")
    return file


#################################
#### ADLIB FILE FORMAT CONVERSION
#################################


''' 
    to support older adlib versions, we map older tag names (xml) to newer tag names.
    here is the mapping
'''
xmlObjectconversionMapping = {
    "adlib-record" : "record",
    "adlib-xml": "recordlist",
    "beschrijving" : "description",
    "instellingsnummer" : "institution.name",
    "materiaal" : "material",
    "objectnaam" : "object_name",
    "objectnummer" : "object_number",
    "standplaats" : "location",
    "titel" : "title",
    "verwerving_methode" : "acquisition.method",
    "verworven_van" : "acquisition.source",
    "verwerving_datum" : "acquisition.date",
    "vervaardiger" : "creator",
    "datering_start" : "production.date.start",
# gaasbeek    
    "afmeting_eenheid" : "dimension.unit",
    "afmeting_soort" : "dimension.type",
    "afmeting_waarde" : "dimension.value",
    "aantal_onderdelen" : "number_of_parts",
    "beschrijving": "description",
    "eigenaar": "owner",
    
}
    
def getConvertedTagName(orig):
    p = orig
    if (p in xmlObjectconversionMapping.keys()):
        p = xmlObjectconversionMapping[p]
    return p


######################################
#### SAX PARSING #####################
######################################

import xml.sax

    

class AdlibDocMapGenerator(xml.sax.ContentHandler):
    '''
        a SAX handler that converts adlib XML in "docmaps"
        whenever a record has been read, the  onRecord method of the handlers will be called.
        a handler should hence implement the following interface:
        
        class Handler:
            def onRecord(self,recrod):
                pass
       
       this class support either a single handler either a list of handlers
         
    '''
    def __init__(self,  handler):
        '''
            handler can be a single handler or a list of handlers
        '''
        xml.sax.ContentHandler.__init__(self)
        self.docmap = {}
        self.inRecord = False
        self.inTag = False
        self.current_tag_name = None
        self.current_value = None
        self.handler = handler
        
    def startElement(self,name,attrs):
        tn = getConvertedTagName(name)
        if (tn == "record"):
            self.docmap = {}
            self.inRecord = True
            self.current_tag_name = None
            self.current_value = None
            return
        if self.inRecord:
            self.inTag = True
            self.current_tag_name = tn
            self.current_value = ""
            if ("value" in attrs.getNames()):
                self.current_value = attrs.getValue("value")
            
    def endElement(self,name):
        tn = getConvertedTagName(name)
        if (tn == "record"):
            self.inRecord = False
            self.emit()
            return
        if (self.inTag):
            if (not (self.current_value is None)):
                n = utils.ensureUnicode(self.current_tag_name.strip())
                v = utils.ensureUnicode(self.current_value.strip())
                if (n in self.docmap.keys()):
                    self.docmap[n].append(v)
                else:
                    self.docmap[n]=[v]
            self.current_tag_name = None
            self.current_value = None
            self.inTag = False
    
    def characters(self,content):
        if (self.inTag):
            self.current_value = self.current_value + content
            
    def emit(self):
        if (type(self.handler) == list):
            for h in self.handler:
                h.onRecord(self.docmap)
        else:
            self.handler.onRecord(self.docmap)


def parseSAXFile(filename, handler):
    '''
        parses an XML file and sends the resulting docmaps to the given handler or the given list of handlers
        see AdlibDocMapGenerator for more details
    '''
    try:
        ad = AdlibDocMapGenerator(handler)
        if (type(filename) == str or type(filename) == unicode):
            xml.sax.parse(getFileDescriptor(filename),ad)
        if (type(filename) == file):
            xml.sax.parse(filename,ad)
        ad = None
        gc.collect()
    except Exception, e:
        import traceback
        raise utils.UserError(e,traceback.format_exc(),"Ongeldig XML bestand %s" % (str(filename)))


######################################
######## CSV PARSING #################
######################################

def kv2map(k, v):
    '''
        method generating a docmap from a list of fieldnames + a list of values
    '''
    map = {}
    if(not isinstance(k, list) or not isinstance(v, list)):
        return map
    for i in range(len(k)):
        # check of waarde leeg (--> negeren)
        if(i >= len(v)):
            continue
        value = utils.ensureUnicode(v[i])
        if not value:
            continue
        value = value.strip()
        if len(value)==0:
            continue

        key = utils.ensureUnicode(k[i])
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


def parseCSVFile(filename, handler):
    '''
        parses a CSV files and sends the found records as docmaps to the handler.
        handler can either be a single handler either a list of handlers.
    '''
    import csv
    fd = getFileDescriptor(filename)
    xdialect =  csv.Sniffer().sniff(fd.read(4096))
    xdialect.delimiter = str(xdialect.delimiter)
    xdialect.quotechar = str(xdialect.quotechar)
    fd.seek(0)
    csvDoc = csv.reader(fd, dialect=xdialect)
    headers = csvDoc.next()
    for row in csvDoc:
        map = kv2map(headers, row)
        if (type(handler) == list):
            for h in handler:
                h.onRecord(map)
        else:
            handler.onRecord(map)

