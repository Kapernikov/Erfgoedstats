'''
Conversion module for Adlib XML fields of different
alternate versions of Adlib XML files to a common format.

Created on 4-aug-2011

@author: duststorm
'''
import utils
import chardet, codecs
import gc

##################
#### FILE ENCODING
##################

def autoDetectEncodingFromFile(filename):
    'TODO: missch voorkeur geven aan western, latin1 en utf-8 charsets? Misschien is het mogelijk om bepaalde scores wat op te waarderen'
    result = chardet.detect(open(filename, mode="rb").read(4096))
    encoding = result["encoding"]
    confidence = result["confidence"]
    return encoding

def getFileDescriptor(filename, encoding=None):
    '''Returns the contents of the file with specified path. Returned string is guaranteed
    to be unicode. Will attempt to determine the encoding scheme used in the file as good
    as possible for decoding the file.'''
    if not encoding:
        encoding=autoDetectEncodingFromFile(filename)
    file = codecs.open(filename, mode='rU', encoding=encoding, errors="replace")
    '''fileContents = file.read()
    fileContents = utils.ensureUnicode(fileContents)
    return fileContents'''
    return file


#################################
#### ADLIB FILE FORMAT CONVERSION
#################################

'''General mapping of tags that should happen for every Adlib XML file.
Key is the tag name to be replaced, value is the name it will be replaced with.'''
xmlFieldstatsConversionMapping ={
    "adlib-record" : "record",
    "adlib-xml": "recordlist"
}

'''Mapping of Adlib Object fields to a common format. This conversion will only
happen on Object files.'''
xmlObjectconversionMapping = {
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
    
def getTN(orig):
    p = orig
    if (p in xmlFieldstatsConversionMapping.keys()):
        p = xmlFieldstatsConversionMapping[p]
    if (p in xmlObjectconversionMapping.keys()):
        p = xmlObjectconversionMapping[p]
    return p


######################################
#### SAX PARSING #####################
######################################

import xml.sax

    

class AdlibDocMapGenerator(xml.sax.ContentHandler):
    def __init__(self,  handler):
        xml.sax.ContentHandler.__init__(self)
        self.docmap = {}
        self.inRecord = False
        self.inTag = False
        self.current_tag_name = None
        self.current_value = None
        self.handler = handler
        
    def startElement(self,name,attrs):
        tn = getTN(name)
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
        tn = getTN(name)
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


def parseSAXFile(contents, handler):
    ad = AdlibDocMapGenerator(handler)
    if (type(contents) == str or type(contents) == unicode):
        xml.sax.parse(getFileDescriptor(contents),ad)
    if (type(contents) == file):
        xml.sax.parse(contents,ad)
    ad = None
    gc.collect()
    


######################################
######## CSV PARSING #################
######################################

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
    import csv
    'TODO: excel dialect selecteren?'
    fd = getFileDescriptor(filename)
    xdialect =  csv.Sniffer().sniff(fd.read(4096))
    fd.seek()
    csvDoc = csv.reader(fd, dialect=xdialect)
    headers = csvDoc.next()
    for row in csvDoc:
        map = kv2map(headers, row)
        if (type(handler) == list):
            for h in handler:
                h.onRecord(map)
            else:
                handler.onRecord(map)

