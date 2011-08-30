'''
Conversion module for Adlib XML fields of different
alternate versions of Adlib XML files to a common format.

Created on 4-aug-2011

@author: duststorm
'''
import utils

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

'''Convert XML field names of specified adlib XML to a common XML format
as specified by the configured mappings. If isObjectXML is true then the
object specific fields will also be converted to common names.''' 
def convertToCommonAdlibXML(xmlStr, isObjectXML=False):
    utils.s("Mapping values of xml file to standard adlib version.")
    xmlStr = utils.ensureUnicode(xmlStr)
    mapping = dict(xmlFieldstatsConversionMapping)
    if(isObjectXML):
        mapping.update(xmlObjectconversionMapping)
    
    for srcName, destName in mapping.iteritems():
        xmlStr = replaceTag(xmlStr, srcName, destName)
    return utils.ensureUnicode(xmlStr)
        
def replaceTag(xmlString, srcName, destName):
    xmlString = xmlString.replace("<"+srcName+">", "<"+destName+">")
    xmlString = xmlString.replace("</"+srcName+">", "</"+destName+">")
    return xmlString
    

'''Test method'''    
if __name__ == "__main__":
    import codecs
    f = codecs.open("../data/musea/Talbot house/talbothouse-objects.xml", encoding="utf-8", errors="replace")
    xmlStr = f.read()
    f.close()
    result = convertToCommonAdlibXML(xmlStr, isObjectXML=True)
