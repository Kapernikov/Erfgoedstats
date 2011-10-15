# -*- coding: utf-8 -*-
from __future__ import division
'''
Generates general fieldstats about occurences of fields in 
a dataset.

Main goal of the "fieldstats" report is just to see how fields are filled in.
'''
import invulboek
import utils
import tr
import htmlutils

global xid
xid=0
def getFreshID():
    '''Returns a new unique ID'''
    global xid
    xid = xid + 1
    return xid



class Field:
    '''Represents a field in a dataset.
        this Field object will contain statistics about the usage of a certain field.
        it contains a lot of data (for all records, it will contain the value for this field)
    '''
    def __init__(self,fieldname):
        self.fieldname = fieldname
        
        ''' we keep several counters to speed up the calculation of statistics '''
        self._nbDocuments= 0          # number of documents having this field
        self._nbUses = 0              # number of values (can be more than number of documents if multivalued)
        self._totalFieldLength = 0    # total number of characters of all values together (needed for average length calculation)

        ''' data structure: 
            a list of lists: for each document it will contain the values for this field.
            eg field "materiaal", 2 documents, one with a single value, one with 2 values
            [
                [ "aardewerk" ],
                [ "metaal", "hout" ],
            ]
        '''
        self.documents = []
          
    def newDocument(self,use):
        '''Notify this field that it is used by a document.
        The document will be stored in this field's document list.'''
        if (use is None):
            return
        self.documents.append([use.encode('utf-8')])
        self._nbDocuments = self._nbDocuments + 1
        self._nbUses = self._nbUses + 1
        self._totalFieldLength = self._totalFieldLength + len(use)

    def newUse(self,use):
        '''Notify this field that it is used another time by a document
        that already announced its first usage of this field using newDocument.'''
        if (use is None):
            return
        self._nbUses = self._nbUses + 1
        self._totalFieldLength = self._totalFieldLength + len(use)

        if (len(self.documents) > 0):
            self.documents[-1].append(use.encode('utf-8'))
        else:
            self.documents.append([use.encode('utf-8')])

    
    
    def getAverageUsePerDocument(self):
        '''Calculates the average number of times this field is used per document.'''
        documents_that_use = self._nbDocuments
        if (documents_that_use == 0):
            return 0
        return self.getNBUses() / documents_that_use
    
    
    def getAverageFieldLength(self):
        '''Returns the average length of all values that are assigned to this field.'''
        totalLength = self._totalFieldLength
        totalFields = self.getNBUses()
        if (totalFields == 0):
            return 0
        return totalLength / totalFields    
    
            
    def getNBDocuments(self):
        '''The number of documents this field is used in.'''
        return self._nbDocuments
    
    def getNBUses(self):
        return self._nbUses
    
    
    def isMeaningLess(self):
        '''Determines whether this field is meaningless. It is meaningless if
        its name is "priref" or "record_number", which are database IDs, or when
        the field's name starts with "edit[._]" or input[._].
        
        meaningless fields are not shown in the report'''
        badfields = ["priref", "record_number"]
        if (self.fieldname.startswith("edit.") or self.fieldname.startswith("edit_")):
            return True
        if (self.fieldname.startswith("input.") or self.fieldname.startswith("input_")):
            return True
        return self.fieldname in badfields
    
    def reportValueBreakdown(self, id):
        '''Returns a breakdown (CounterDict) of the different unique values and their
        number of occurences in the report (all values of all documents).
        A counterDict is returned. Returns None if no documents are added
        to this report yet.'''
        if (self.getNBDocuments() == 0):
            return None
        values = utils.CounterDict()
        for x in self.documents:
            for y in x:
                values.count(y)
        return values        
    
    
    def shouldReportDetail(self, values):
        if values and self.getNBDocuments() > 0:
            if (len(values) <= utils.getMaxDetail()):
                return  True
            else:
                return False
        else:
            return False
    
    def reportUsage(self, totaldocs):
        '''Generate a row about this field in the fieldstats table containing the usage statistics
        of the field this row represents.'''

        
        row = htmlutils.TableRow()
        row.addClass("value-row")
        if (self.getNBDocuments() / totaldocs > 0.99):
            row.addClass("q-complete")
        elif (self.getNBDocuments() / totaldocs > 0.8):
            row.addClass("q-almost-complete")
        if (self.getAverageUsePerDocument() > 1.001):
            row.addClass("multi-value")
        if (self.fieldname in invulboek.allfields):
            row.addClass("invulboek")
        

        
        '''Determine whether a detailed popup should be shown for this row. Also, if no popup is shown, the checkbox for
        this row is disabled so that the detail table can also not be shown for printing.'''
        values = self.reportValueBreakdown(id)
        if self.shouldReportDetail(values):
            # create the tooltip
            row.tooltip = values.getReport()
            row.tooltiptitle = tr.tr(self.fieldname)

        fieldnameCell = htmlutils.Cell()
        fieldnameCell.addClass("fieldname")
        fieldnameCell.content = tr.tr(self.fieldname)

        usedDocs = htmlutils.Cell("%.0f" % round(100.0 * self.getNBDocuments() / totaldocs))
        usedDocs.addClass("usedDocs")

        usedDocsAbs = htmlutils.Cell(str(self.getNBDocuments()))
        usedDocsAbs.addClass("usedDocsAbs")
        
        valuesperdoc = htmlutils.Cell("%.2f" % self.getAverageUsePerDocument())
        valuesperdoc.addClass("valuesperdoc")
        
        averagefieldlength = htmlutils.Cell("%.0f" % self.getAverageFieldLength())
        averagefieldlength.addClass("averagefieldlength")
        
        numberofuses = htmlutils.Cell(str(len(values)))
        numberofuses.addClass("number-of-use")
        
        row.appendCells([fieldnameCell,usedDocs, usedDocsAbs, valuesperdoc, averagefieldlength, numberofuses])
                
        return row

import inputfileformat

class FieldStats:
    '''
        class for generating the FieldStats
        this class does:
            * serve as a handler for the inputfileformat (it has the onRecord row)
            * keeps a collection of Fields
            * has methods to write a html report
    '''
    def __init__(self, filename=None, documentfilter=None, type="xml"):
        '''
            filename is the name of the file to parse or None if there is no parsing needed.
            
            documentfilter is a method:
                documentfilter(docmap) that will return true if this docmap is to be included, and false if the docmap is to be excluded
                when documentfilter is None, all records will be included
            
            type is either xml either csv. if filename is None, type can also be None
        '''
        self.fields = {}
        self.totaldocs = 0
        self.documentFilter = documentfilter
        if (filename is None):
            return
        if (type=="xml"):
            inputfileformat.parseSAXFile(filename, self)
        if (type=="csv"):
            inputfileformat.parseCSVFile(filename, self)

    def getSize(self):
        return self.totaldocs

    def onRecord(self,docmap):
        '''
            parses this docmap: update / add Fields
        '''
        include_d = True
        if (self.documentFilter is not None):
            include_d = self.documentFilter(docmap)
        if include_d:
            self.totaldocs = self.totaldocs + 1
            alreadyfields = []
            for field in docmap:
                fieldname = field.encode('utf-8','ignore')
                fieldvalue = docmap[fieldname]
                alreadyfields.append(fieldname)
                if not (fieldname in self.fields.keys()):
                    self.fields[fieldname]=Field(fieldname)
                if (type(fieldvalue) == list):
                    self.fields[fieldname].newDocument(fieldvalue[0])
                    for val in fieldvalue[1:]:
                        self.fields[fieldname].newUse(val)
                else:
                    if (fieldvalue != ''):
                        self.fields[fieldname].newDocument(fieldvalue)

    def generateReport(self, ofile):
        table = htmlutils.SortableTable()
        table.addClass("fieldreport")
        table.addClass("rpt")
        table.setHeader(["veld", "% gebruikt", "aantal", "meervoudige waarde", "gem. veldlengte", "unieke waarden"])

        sv = self.fields.values()
        for x in sorted(sv, key=lambda x: x.getNBDocuments(), reverse=True):
            if not x.isMeaningLess():
                fieldsRow = x.reportUsage(self.totaldocs)
                table.addRow(fieldsRow)
                import gc
                gc.collect()

        table.renderTo(ofile)

        
        
