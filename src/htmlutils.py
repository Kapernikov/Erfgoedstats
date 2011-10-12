# -*- coding: utf-8 -*-
'''
Reusable HTML elements, building blocks for HTML reports.

Created on 3 mrt. 2011

@author: rein
'''

import string

class HtmlID:
    """Dit moet als Singleton gebruikt worden!
    """
    def __init__(self):
        self.id = 0
        
    def getNext(self):
        self.id += 1
        return self.id
    
global htmlid
htmlid  = HtmlID()

class HtmlElement():
    '''"abstract" baseclass for a HTML element'''
    def __init__(self):
        self.id = self.getTagname() + str(htmlid.getNext())
        self.classes = []
    
    def getCssClasses(self):
        '''Get all CSS classes associated with this HTML element'''
        return ' '.join(self.classes)
    
    def getTagname(self):
        raise Exception("you should implement this")
    
    def render(self):
        raise Exception("you should implement this")
    
    def addClass(self, cssclass):
        '''Add a CSS class to this element'''
        if not isinstance(cssclass, str):
            return
        self.classes.append(cssclass)

class HelpElement(HtmlElement):
    '''Hideable help message HTML element'''
    def __init__(self, help, show, hide="Verberg deze uitleg"):
        HtmlElement.__init__(self)
        self.addClass('help')
        self.showMessage = show
        self.hideMessage = hide
        self.helpHtml = help
    
    def getTagname(self):
        return 'div'
    
    def render(self):
        return """<p class="showhidehelpmessage" id="showhide%(id)s">%(show)s</p>
        <div class="helptext" id="help%(id)s">%(help)s</div>
        <script>
            $('#showhide%(id)s').toggle(
                function () {
                    $(this).text("%(hide)s")
                    $('#help%(id)s').show()
                },
                function () {
                    $(this).text("%(show)s")
                    $('#help%(id)s').hide()
                }
            );
        </script>
        """ % {'show': self.showMessage, 'hide': self.hideMessage, 'id': htmlid.getNext(), 'help': self.helpHtml}

class SortableTable(HtmlElement):
    '''Sortable table HTML element'''
    def __init__(self):
        HtmlElement.__init__(self)
        self.addClass('sortable')
        self.header = None
        self.rows = []
        self.columns = None
        self.enablePersistTooltips = False

    def getTagname(self):
        return "table"

    def toRow(self, cells):
        '''Create a table row from a list of cells. If cells is already
        a table row, it is simply returned.'''
        if isinstance(cells, TableRow):
            row = cells
        else:
            row = TableRow(cells)
        return row

    def checkLength(self, row):
        '''Check and set the number of columns of this table, using the length of the specified row.
        Can only be called once for a table.'''
        if self.columns == None:
            self.columns = row.getLength()
        if self.columns != row.getLength():
            raise Exception("Nb of columns was already initialised to %s for this table and you are adding a row with the wrong number (%s) of columns" % (self.columns, row.getLength()))

    def setHeader(self,cells):
        '''Set header cells'''
        row = self.toRow(cells)
        row.isTableHead = True
        self.checkLength(row)
        self.header = row
        
    def addRow(self, cells):
        '''Add a row to this table'''
        row = self.toRow(cells)
        self.checkLength(row)
        self.rows.append(row)
        if (row.tooltip):
            self.enablePersistTooltips = True
        
    def renderTo(self, writer):
        writer.write( u'<table class="%s" id="%s" border="0">\n' % (self.getCssClasses(), self.id))
        writer.write( "<thead><tr>\n")
        
        for cell in self.header.cells:
            cell.renderTo(writer, True)
        
        writer.write( "</tr></thead>\n")
        writer.write( "<tbody>\n")
        
        for row in self.rows:
             row.renderTo(writer,self.enablePersistTooltips)
        
        writer.write( "</tbody>")
        writer.write( "</table>\n")
        
        # now for the tooltips!
        
        
        for row in self.rows:
            if (row.tooltip):
                    writer.write( '<div id="valuetable%s" style="display: none;">\n' % row.id)
                    writer.write( "\t<h2>"+ row.tooltiptitle  +"</h2>\n" + row.tooltip)
                    writer.write( '</div>\n')
        
        
class TableRow(HtmlElement):
    '''One row in a (sortable) table'''
    def __init__(self, cells=None, classes=None, tableHead=False, tooltip=None, tooltiptitle=None):
        self.isTableHead = tableHead
        HtmlElement.__init__(self)
        self.cells = []
        if cells != None:
            self.appendCells(cells)
        if classes != None:
            self.classes = classes
        if tooltip:
            self.tooltip = unicode(tooltip)
            self.tooltiptitle = unicode(tooltiptitle)
        else:
            self.tooltip = None
            self.tooltiptitle = None
            
        
    def appendCells(self,cells):
        '''Append given cells to this row'''
        for cell in cells:
            if isinstance(cell, Cell):
                self.cells.append(cell)
            else:
                self.cells.append(Cell(cell)) 
        
    def getTagname(self):
        if self.isTableHead:
            return "th"
        else:
            return "tr"
        
    def getLength(self):
        '''The number of cells in this row'''
        return len(self.cells)
    
    def renderTo(self, writer, persist_tooltips = False):
        writer.write( "<%s id=\"%s\" class=\"%s\" >\n" % (self.getTagname(), self.id, self.getCssClasses()))
        first = True
        for cell in self.cells:
            tooltipid = None
            if (first and persist_tooltips):
                tooltipid = "none"
            if (first and self.tooltip):
                tooltipid = self.id
            cell.renderTo(writer,self.isTableHead, tooltipid)
            first = False
        writer.write("</%s>\n" % self.getTagname())
        if(self.tooltip):
            writer.write(self.attachTooltip())

    def attachTooltip(self):
        '''Attach a tooltip popup to this table cell'''
        return u"""
        <script type='text/javascript'>
            $(document).ready(function(){
                $("#%s td").easyTooltip({content: '<div class=tooltip>%s</div>'});
            });
        </script>
        """ % (self.id, string.replace(self.tooltip, '\n', ' '))

        
class Cell(HtmlElement):
    '''Cell in a tablerow'''
    def __init__(self, content=""):
        HtmlElement.__init__(self)
        self.content = content
        
        
    def renderTo(self, writer, thead=False, tooltipid=None):
        if thead:
            writer.write('\t<th id="%s" class="%s">' % (self.id, self.getCssClasses()))
        else:
            writer.write('\t<td id="%s" class="%s">' % (self.id, self.getCssClasses()))
        
        
        disabled=''
        if (tooltipid=='none'):
            disabled="""disabled='disabled'"""
        if (tooltipid):
            writer.write("""<input name='#inputvaluetable%(id)s' id='#inputvaluetable%(id)s' %(disabled)s type='checkbox' onClick="javascript:$('#valuetable%(tid)s').toggle();"/><label for='#inputvaluetable%(id)s'>\n"""  % {'id': self.id, "tid": tooltipid, 'disabled': disabled})

        
        writer.write(self.content)
        
        if (tooltipid):
            writer.write("</label>")
        
        if thead:
            writer.write("</th>\n")
        else:
            writer.write("</td>\n")
        
    

    
    def getTagname(self):
        return "cell"
        
    