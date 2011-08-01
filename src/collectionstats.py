# -*- coding: utf-8 -*-
'''
Module that generates statistics about a collection.

Created on Jan 6, 2011

@author: kervel
'''

from xml.etree.ElementTree import ElementTree, iselement

import htmlutils
import invulboek
import utils
import thesaurus



class Collection:
    '''Represents a museum collection (catalogue) and statistics about it.
    '''
    def __init__(self,doc):
        self.objects = []
        self.parseDocument(doc)
    
    def getSize(self):
        '''Returns the number of objects in this collection.'''
        return len(self.objects)
        
    def parseDocument(self,doc):
        '''Append all records from the given doc (which is an XML element tree)
        to this collection as Collection Objects.'''
        if(not isinstance(doc, ElementTree)):
            return
        
        assert isinstance(doc, ElementTree)
        for x in doc.findall(".//record"):
            self.objects.append(CollectionObject(x))

    def getComplianceLevels(self):
        '''Returns a Counter Dictionary (see utils) with the aggregated
        compliance levels to standard thesauri of the terms for all objects
        in this collection.
        ''' 
        levels = utils.CounterDict()
        for x in self.objects:
            cl = x.getMoveComplianceLevels()
            for cll in cl:
                levels.count(cll)
        return levels

    def getMissingFields(self,compliancelevel):
        mf = utils.CounterDict()
        for x in self.objects:
            for field in x.getMissingFields(invulboek.invulboek_fields[compliancelevel]):
                mf.count(field)
        return mf

    def generateReport(self, no_compliance = False, no_thesaurus = False):
        '''Generate fieldstats about this collection. Unless specified otherwise, also compliance report
        (compliance of field values to reference thesauri) and comparison with reference thesaurus
        will be produced.'''
        html = ""
        if (not no_compliance):
            x = self.getComplianceLevels()
            html += "<h2>Aan welke registraties voldoen de objecten</h2>\n";
            html += x.getReport()
            for cl in map(lambda y: y[0], x.getSortedResult()):
                if(invulboek.invulboek_fields.has_key(cl)): 
                    html += "<h2>Ontbrekende velden voor %s</h2>\n" % cl
                    mfx = self.getMissingFields(cl)
                    html += mfx.getReport()
        if (not no_thesaurus):
            if thesaurus.getThesauri():
                html += "<h1>Gebruik van thesaurustermen</h1>"
                html += htmlutils.HelpElement(show="Toon uitleg bij deze controles", help="""
    <p>Per standaard-thesaurus, wordt van een aantal velden nagekeken of de gebruikte waarden in 
    het veld voldoen aan die standaard-thesaurus.</p>
    <p>Mogelijke resultaten zijn:</p>
    <dl>
      <dt>Voorkeurterm</dt><dd>Het veld is ingevuld en de waarde is 
      de voorkeurterm uit de thesaurus.</dd>
      <dt>Niet de voorkeurterm</dt><dd>Het veld is ingevuld en de waarde is 
      bekend in de thesaurus, doch niet als voorkeurterm. De waarde zou vervangen
      moeten worden door de voorkeurterm.</dd>
      <dt>Niet in de ... thesaurus</dt><dd>Het veld is ingevuld maar de waarde is 
      niet bekend in de thesaurus.</dd>
      <dt>Leeg (niet ingevuld)</dt><dd>Het veld niet ingevuld.</dd>
    </dl>
    """).render()
            # General comparison summary with all reference thesauri  
            html += thesaurus.getCollectionThesauriReport(self)
            # Comparisons with individual reference thesauri
            for thesa in thesaurus.getThesauri():
                html += thesa.getCollectionThesaurusReport(self)
        return html

class CollectionObject(object):
    '''Represents an object in a Collection. This would generally be
    a piece in a museam.'''
    
    def __init__(self,element):
        '''
        Constructor, creates a new collection object from
        the specified XML element. The collection object
        contains a mapping of tags as keys, and their non-empty
        values, all encoded in unicode.
        Entries are defined in XML as follows:
            <key>value</key>
        Tag names are keys, their text is the value.
        A key can have multiple values if a tag with the same
        name has multiple occurences within the same html element. 
        The value of each key in the constructed collection object 
        can either be a singular value, or a list of values.
        '''
        self.params = {}
        if(not iselement(element)):
            return        
        for x in element:   # for all tags in element
            value = x.text
            fieldname = x.tag
            self.addParam(fieldname, value)
            
    def addParam(self, fieldname, value):
        '''Add param as key-value pair to this object.'''
        if(not value):
            return
        value = value.strip()  # that is not just whitespaces
        if len(value) == 0:
            return
        value = utils.nencode(value)
        #@@@TEST
        #fieldname = utils.nencode(x.tag)
        fieldname = utils.nencode(fieldname)
        if fieldname in self.params:
            # append value to existing param 
            self.params[fieldname].append(value)
        else:
            self.params[fieldname] = [value]
    
    
    def __getitem__(self,key):
        '''Get the value of field with specified key. Returns
        empty list if key does not exist, else returns a list
        of its values.''' 
        if (not (key in self.params.keys())):
            return u""
        return self.params[key]
    
    def getMissingFields(self,set_of_fields):
        '''Given a set of fields (a list of key names),
        returns a list of all keys that do not exist
        for this collection object. If no fields are
        missing, an empty list is returned.'''
        missingfields = []
        for x in set_of_fields:
            if (not (x in self.params.keys())):
                missingfields.append(x)
        return missingfields
    
    def hasAll(self,set_of_fields):
        '''Determines whether this collection object
        contains all the requested fields.'''
        return (len(self.getMissingFields(set_of_fields)) == 0)
    
    def validateAll(self,set_of_fields,validationrules):
        '''Validate a set of keys with their respective validation rules.
        Returns a list of keys that failed the validation. If none failed,
        an empty list is returned.
        Set_of_fields is a list of fields of this object that should be 
        evaluated, validationrules is a mapping of a fieldname to a 
        validationrule for that field.
        A validationrule is a list of accepted values. A field fails 
        validation if one of its values (a field can have multiple) is not 
        in the accepted values for that field. 
        Fields to be validated that do not exist are not validated and are 
        not seen as failed. A field for which no validation rules are 
        defined is automatically seen as valid. 
        '''
        failed = []
        for x in set_of_fields:
            if (x in self.params.keys() and x in validationrules.keys()):
                val = self.params[x]
                if (not isinstance(val,list)): continue
                possiblevalues = validationrules[x]
                for ival in val:
                    if (not (ival in possiblevalues)):
                        if (not (x in failed)):
                            failed.append(x)
        return failed

    def getMoveComplianceLevels(self):
        '''Produce statistics that indicate compliance to AM-MovE standards. (see invulboek module)
        Returns all the AM-MovE levels for which this object qualifies. Qualifying means that all
        the required fields for that level are filled in. An extra notice is added if all the fields
        for a level are present, but the value of some did not validate correctly.'''
        levels = []
        # Try each AM-MovE standard
        for standaard in invulboek.invulboek_fields.keys():
            # If an object has all the fields specified for that standard, we can evaluate it
            if (self.hasAll(invulboek.invulboek_fields[standaard])):
                # Append the category to the levels if all validations for that category validate correctly
                if (len(self.validateAll(invulboek.invulboek_fields[standaard], invulboek.invulboek_possiblevalues)) == 0):
                    levels.append(standaard)
                else:
                    levels.append(standaard + " maar sommige velden ongeldig ingevuld")
            else:
                pass
        # If object does not satisfy any standard
        if (len(levels) == 0):
            if (len(self.validateAll(self.params.keys(), invulboek.invulboek_possiblevalues)) > 0):
                    levels.append("Voldoet aan geen enkele validatie en sommige velden ongeldig ingevuld")
            else:
                    levels.append("Voldoet aan geen enkele validatie")
        return levels
    
