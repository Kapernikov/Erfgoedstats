# -*- coding: utf-8 -*-
from __future__ import division
'''
Generates general fieldstats about occurences of fields in 
a dataset.

Created on Jan 6, 2011

@author: kervel
'''
import invulboek
import utils
import tr
from xml.etree.ElementTree import ElementTree
import htmlutils

global xid

xid=0

def getFreshID():
    '''Returns a new globally unique ID'''
    global xid
    xid = xid + 1
    return xid

class Field:
    '''Represents a field'''
    def __init__(self,fieldname):
        self.fieldname = fieldname
        self.nbMultiValued = 0
        # list of lists: one entry in self.documents = one document
        # this entry contains another list that contains the different documents
        self.documents = []
        '''This should normally be a boolean, but is set to -1 when its value is not yet calculated'''
        self._isReportDetail = -1
       
  
    '''
        a new document uses this field
    '''
    def newDocument(self,use):
        '''Notify this field that it is used by a document.
        The document will be stored in this field's document list.'''
        if (use is None):
            return
        self.documents.append([use])
    
    
    def getAverageUsePerDocument(self):
        '''Calculates the average number of times this field is used per document.'''
        documents_that_use = len(self.documents)
        if (documents_that_use == 0):
            return 0
        return self.getNBUses() / documents_that_use
    
    
    def getAverageFieldLength(self):
        '''Returns the average length of all values that are assigned to this field.'''
        totalLength = 0
        totalFields = 0
        for x in self.documents:
            for y in x:
                totalFields = totalFields + 1
                totalLength = totalLength + len(y)
        if (totalFields == 0):
            return 0
        return totalLength / totalFields    
    
    '''
        a document that already used this field uses it again (multivalued field)
    '''
    def newUse(self,use):
        '''Notify this field that it is used another time by a document
        that already announced its first usage of this field using newDocument.'''
        if (use is None):
            return
        if (len(self.documents) > 0):
            self.documents[-1].append(use)
            self.nbMultiValued = self.nbMultiValued + 1
        else:
            self.documents.append([use])
            
    def getNBDocuments(self):
        '''The number of documents this field is used in.'''
        return len(self.documents)
    
    def getNBUses(self):
        '''Total number of times this field is used.'''
        n = 0
        for doc in self.documents:
            n += len(doc)
        return n
    
    
    def isMeaningLess(self):
        '''Determines whether this field is meaningless. It is meaningless if
        its name is "priref" or "record_number", which are database IDs, or when
        the field's name starts with "edit[._]" or input[._].'''
        badfields = ["priref", "record_number"]
        if (self.fieldname.startswith("edit.") or self.fieldname.startswith("edit_")):
            return True
        if (self.fieldname.startswith("input.") or self.fieldname.startswith("input_")):
            return True
        return self.fieldname in badfields
    
    'TODO: ??  is id gebruikt?'
    def reportValueBreakdown(self, id):
        '''Returns a breakdown of the different unique values and their
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
    
    def isReportDetail(self):
        '''Returns whether the report should be detailed with a counterDict
        table popup with its different values (boolean).
        If the report detail is not yet calculated it is calculated using 
        the value breakdown of the current values in the report.'''
        if self._isReportDetail == -1:
            self.setReportDetail(self.reportValueBreakdown(id))
        return self._isReportDetail
    
    def setReportDetail(self, values):
        '''Set the isReportDetail() based on the values (result from self.reportValueBreakdown(id))
        isReportDetail will be set to true if values is not None, and it contains less than 40 items,
        or when the ratio of the amount of values against the number of documents is smaller than 0.7
        '''
        self._isReportDetail = values and (len(values) < 40 or (len(values) / self.getNBDocuments()) < 0.7)
    
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
        
        values = self.reportValueBreakdown(id)
        self.setReportDetail(values) 

        fieldnameCell = htmlutils.Cell()
        
        '''Determine whether a detailed popup should be shown for this row. Also, if no popup is shown, the checkbox for
        this row is disabled so that the detail table can also not be shown for printing.'''
        if self.isReportDetail():
            # create the tooltip
            row.tooltip = values.getReport()
            row.tooltiptitle = tr.tr(self.fieldname)

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
                
        return row, values


class FieldStats:
    def __init__(self, doc, documentfilter=None, type="xml"):
        self.fields = {}
        self.totaldocs = 0
        self.documentFilter = documentfilter
        if (type=="xml"):
            self._parseDocument(doc)
        if (type=="csv"):
            self._parseCSV(doc)

    def getSize(self):
        return self.totaldocs
        
    def _parseCSV(self,csvDoc):
        headers = csvDoc.next()
        for row in csvDoc:
            map = utils.kv2map(headers, row)
            self._parseDocMap(map)

    def _parseDocument(self, doc):
        if not isinstance(doc, ElementTree):
            return
        for x in doc.findall(".//record"):
            map = utils.doc2map(x)
            self._parseDocMap(map)

    'TODO: Door gebrek aan strong typing kan het hier wel eens grondig misgaan bij vieze input'                        
    def _parseDocMap(self, docmap):
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

    def generateReport(self):
        table = htmlutils.SortableTable()
        table.addClass("fieldreport")
        table.addClass("rpt")
        table.setHeader(["veld", "% gebruikt", "aantal", "meervoudige waarde", "gem. veldlengte", "unieke waarden"])
        
        report_html = u''

        sv = self.fields.values()
        valuesTables = ''
        for x in sorted(sv, key=lambda x: x.getNBDocuments(), reverse=True):
            if not x.isMeaningLess():
                fieldsRow, values = x.reportUsage(self.totaldocs)
                table.addRow(fieldsRow)

        report_html += table.render()
        return report_html
        