'''
Created on 7-aug-2011

@author: duststorm
'''
import regenAll
import adlibstats

def getFilenames(keyName, museumMap):
    if keyName not in museumMap:
        return []
    value = museumMap[keyName]
    if isinstance(value, basestring):
        return [value]
    if isinstance(value, list):
        return value
    return []




for museumkey in sorted(regenAll.musea.keys(), key=lambda x: regenAll.musea[x]["name"] ):
    museum = regenAll.musea[museumkey]
    print "Testing files of " + museum["name"]

    for filename in getFilenames("objects", museum):
        adlibstats.autoDetectEncodingFromFile(filename)
       
    for filename in getFilenames("thesaurus", museum):
        adlibstats.autoDetectEncodingFromFile(filename)
    
    for filename in getFilenames("fieldstats", museum):
        adlibstats.autoDetectEncodingFromFile(filename)
    
    for filename in getFilenames("csvfieldstats", museum):
        adlibstats.autoDetectEncodingFromFile(filename)
        
