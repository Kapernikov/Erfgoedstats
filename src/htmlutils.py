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
        assert isinstance(cssclass, str)
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
        
        
    def render(self):
        result = '<table class="%s" id="%s" border="0">\n' % (self.getCssClasses(), self.id)
        result += "<thead><tr>\n"
        
        for cell in self.header.cells:
            result += cell.render(True)
        
        result += "</tr></thead>\n"
        result += "<tbody>\n"
        
        for row in self.rows:
            result += row.render()
        
        result += "</tbody>"
        result += "</table>\n"
        return result
        
class TableRow(HtmlElement):
    '''One row in a (sortable) table'''
    def __init__(self, cells=None, classes=None, tableHead=False):
        self.isTableHead = tableHead
        HtmlElement.__init__(self)
        self.cells = []
        if cells != None:
            self.appendCells(cells)
        if classes != None:
            self.classes = classes
        
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
    
    def render(self):
        result = ""
        result += "<%s class=\"%s\" >\n" % (self.getTagname(), self.getCssClasses())
        for cell in self.cells:
            result += cell.render(self.isTableHead)
        result += "</%s>\n" % self.getTagname()
        return result
        
class Cell(HtmlElement):
    '''Cell in a tablerow'''
    def __init__(self, content="", tooltip=None):
        HtmlElement.__init__(self)
        self.content = content
        self.tooltip = tooltip
        
    def render(self, thead=False):
        result = ""
        if thead:
            result += '\t<th id="%s" class="%s">' % (self.id, self.getCssClasses())
        else:
            result += '\t<td id="%s" class="%s">' % (self.id, self.getCssClasses())
        
        result += self.content
        
        if thead:
            result += "</th>\n"
        else:
            result += "</td>\n"
        
        if(self.tooltip != None):
            result += self.attachTooltip()    
        
        return result
    
    def attachTooltip(self):
        '''Attach a tooltip popup to this table cell'''
        return """
        <script type='text/javascript'>
            $(document).ready(function(){
                $("#%s").easyTooltip({content: '<div class=tooltip>%s</div>'});
            });
        </script>
        """ % (self.id, string.replace(self.tooltip, '\n', ' '))
    
    def getTagname(self):
        return "cell"
        
    