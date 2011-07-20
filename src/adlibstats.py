'''
Main program for analysing stats of one museum.
This module generates HTML output reports.

Created on Jan 6, 2011

@author: kervel
'''

import fieldstats
import htmlutils
import thesaurus
import collectionstats

from xml.etree.ElementTree import ElementTree
import getopt, sys
import utils
import os

def dn(filename):
    '''Turns filename into readable name,
    by leaving only the filename, without path,
    and removing .xml extension.'''
    path = filename.split("/")[-1]
    path = path.replace(".xml","")
    return path

def generate_report(filename):
    '''Write HTML report of fieldstats using XML file with given name.
    These fieldstats are a general statistic about the occurence of fields
    in a dataset.'''
    utils.s("parsing file %s" % (filename))
    the_doc = ElementTree(file=filename)
    utils.s("generating fieldstats")
    fs = fieldstats.FieldStats(the_doc)
    html = ""
    html += '<h1>Records in lijst: %s</h1>' % (dn(filename))
    html += "<p>Aantal records: %s</p>" % (fs.totaldocs)
    html += htmlutils.HelpElement(show="Toon uitleg bij deze tabel", help="""
    <p>Onderstaande tabel toont alle velden die ingevuld werden voor minstens 
    &eacute;&eacute;n record uit de lijst. Voor elk veld wordt volgende
    informatie getoond:</p>
    <dl>
      <dt>VELD</dt><dd>De naam van het veld.</dd>
      <dt>% GEBRUIKT</dt><dd>Het percentage van de records waarvoor dit veld is ingevuld.
          Opgepast: een waarde "0" geldt ook als ingevuld.</dd>
      <dt>AANTAL</dt><dd>Het aantal records waarvoor dit veld is ingevuld.</dd>
      <dt>MEERVOUDIGE WAARDE</dt><dd>Dit geeft aan hoeveel keer het veld 
          <em>gemiddeld</em> is ingevuld per record. Een waarde van "1.2" betekent dat het 
          veld meestal slechts &eacute;&eacute;nmaal is ingevuld, maar voor sommige records
          twee (of meerdere) keren.<br/>
          Indien het veld meermaals is ingevuld voor ook maar &eacute;&eacute;n record, wordt
          het vakje paars gekleurd.</dd>
      <dt>GEM. VELDLENGTE</dt><dd>Het gemiddeld aantal karakters dat ingevuld werd in het veld.</dd>
      <dt>UNIEKE WAARDEN</dt><dd>Het aantal verschillende waarden dat ingevuld werd in dit veld.<br/>
          Voorbeeldje:<br/>
          Elk record zou een eigen, unieke "Naam" moeten hebben, dus
          moeten er evenveel unieke waarden ingevuld zijn als het aantal records.
      </dd>
    </dl>
    <p>Je kunt op de kolomtitel klikken om de tabel te sorteren volgens die kolom.</p>
    <p>Als je met de muis boven de naam van het veld hangt (waarde in de kolom "VELD"),
    krijg je een tooltip met daarin de verschillende waarden die zijn ingevuld voor dit veld
    en het aantal records waarvoor deze waarde is ingevuld.<br/>
    Wanneer je het vinkje aanklikt v&oacute;&oacute;r de naam van het veld, verschijnt
    dit detailtabelletje onderaan de grote tabel, zodat je dit eventueel kunt afdrukken.<br/>
    Opgepast: de tooltip en de checkbox verschijnen alleen indien niet teveel verschillende waarden
    bestaan.</p>
    """).render()

    utils.s("writing report")
    html += fs.generateReport()
    return html

def generate_csvreport(filename):
    '''Write HTML report of fieldstats using CSV input file with given name.
    These fieldstats are a general statistic about the occurence of fields
    in a dataset.'''
    utils.s("parsing file %s" % (filename))
    utils.s("generating fieldstats")
    fs = fieldstats.FieldStats(filename,type="csv")
    html = ""
    html += '<h1>Records in bestand: %s</h1>\n' % dn(filename)
    html += "<p>Aantal records: %s</p>\n" % fs.totaldocs
    html += htmlutils.HelpElement(show="Toon uitleg bij deze tabel", help="""
    <p>Onderstaande tabel toont alle velden die ingevuld werden voor minstens 
    &eacute;&eacute;n record uit de lijst. Voor elk veld wordt volgende
    informatie getoond:</p>
    <dl>
      <dt>VELD</dt><dd>De naam van het veld.</dd>
      <dt>% GEBRUIKT</dt><dd>Het percentage van de records waarvoor dit veld is ingevuld.
          Opgepast: een waarde "0" geldt ook als ingevuld.</dd>
      <dt>AANTAL</dt><dd>Het aantal records waarvoor dit veld is ingevuld.</dd>
      <dt>MEERVOUDIGE WAARDE</dt><dd>Dit geeft aan hoeveel keer het veld 
          <em>gemiddeld</em> is ingevuld per record. Een waarde van "1.2" betekent dat het 
          veld meestal slechts &eacute;&eacute;nmaal is ingevuld, maar voor sommige records
          twee (of meerdere) keren.<br/>
          Indien het veld meermaals is ingevuld voor ook maar &eacute;&eacute;n record, wordt
          het vakje paars gekleurd.</dd>
      <dt>GEM. VELDLENGTE</dt><dd>Het gemiddeld aantal karakters dat ingevuld werd in het veld.</dd>
      <dt>UNIEKE WAARDEN</dt><dd>Het aantal verschillende waarden dat ingevuld werd in dit veld.<br/>
          Voorbeeldje:<br/>
          Elk record zou een eigen, unieke "Naam" moeten hebben, dus
          moeten er evenveel unieke waarden ingevuld zijn als het aantal records.
      </dd>
    </dl>
    <p>Je kunt op de kolomtitel klikken om de tabel te sorteren volgens die kolom.</p>
    <p>Als je met de muis boven de naam van het veld hangt (waarde in de kolom "VELD"),
    krijg je een tooltip met daarin de verschillende waarden die zijn ingevuld voor dit veld
    en het aantal records waarvoor deze waarde is ingevuld.<br/>
    Wanneer je het vinkje aanklikt v&oacute;&oacute;r de naam van het veld, verschijnt
    dit detailtabelletje onderaan de grote tabel, zodat je dit eventueel kunt afdrukken.<br/>
    Opgepast: de tooltip en de checkbox verschijnen alleen indien niet teveel verschillende waarden
    bestaan.</p>
    """).render()

    utils.s("writing report")
    html += fs.generateReport()
    return html


def generate_compliancereport(filename, no_compliance=True, no_thesaurus=False):
    '''Generate thesaurus compliance report for writing to HTML'''
    utils.s("parsing file %s" % filename)
    the_doc = ElementTree(file=filename)
    html = ""
    html += '<h1>Collectie: %s</h1>\n' % dn(filename)
    utils.s("generating fieldstats")
    fs = fieldstats.FieldStats(the_doc)
    html += "<p>Aantal objecten in collectie: %s</p>\n" % fs.getSize()
    
    html += "<h2>Overzicht gebruikte velden</h2>\n"
    html += htmlutils.HelpElement(show="Toon uitleg bij deze tabel", help="""
    <p>Onderstaande tabel toont alle velden die ingevuld werden voor minstens 
    &eacute;&eacute;n object uit de collectie. Voor elk veld wordt volgende
    informatie getoond:</p>
    <dl>
      <dt>VELD</dt><dd>De naam van het veld.</dd>
      <dt>% GEBRUIKT</dt><dd>Het percentage van de objecten waarvoor dit veld is ingevuld.
          Opgepast: een waarde "0" geldt ook als ingevuld.</dd>
      <dt>AANTAL</dt><dd>Het aantal objecten waarvoor dit veld is ingevuld.</dd>
      <dt>MEERVOUDIGE WAARDE</dt><dd>Dit geeft aan hoeveel keer het veld 
          <em>gemiddeld</em> is ingevuld per object. Een waarde van "1.2" betekent dat het 
          veld meestal slechts &eacute;&eacute;nmaal is ingevuld, maar voor sommige objecten
          twee (of meerdere) keren.<br/>
          Indien het veld meermaals is ingevuld voor ook maar &eacute;&eacute;n object, wordt
          het vakje paars gekleurd.</dd>
      <dt>GEM. VELDLENGTE</dt><dd>Het gemiddeld aantal karakters dat ingevuld werd in het veld.</dd>
      <dt>UNIEKE WAARDEN</dt><dd>Het aantal verschillende waarden dat ingevuld werd in dit veld.<br/>
      Twee voorbeelden:<br/>
      Aan elk object moet een eigen, uniek "Objectnummer" toegekend zijn, dus
      moeten er evenveel unieke waarden ingevuld zijn als het aantal objecten.<br/>
      Meestal beslaat een collectie slechts &eacute;&eacute;n instelling, dus zou er slechts
      &eacute;&eacute;n unieke waarde mogen zijn voor het veld "Instellingsnaam".
      </dd>
    </dl>
    <p>Je kunt op de kolomtitel klikken om de tabel te sorteren volgens die kolom.</p>
    <p>Als je met de muis boven de naam van het veld hangt (waarde in de kolom "VELD"),
    krijg je een tooltip met daarin de verschillende waarden die zijn ingevuld voor dit veld
    en het aantal objecten waarvoor deze waarde is ingevuld.<br/>
    Wanneer je het vinkje aanklikt v&oacute;&oacute;r de naam van het veld, verschijnt
    dit detailtabelletje onderaan de grote tabel, zodat je dit eventueel kunt afdrukken.<br/>
    Opgepast: de tooltip en de checkbox verschijnen alleen indien niet teveel verschillende waarden
    bestaan.</p>
    <p>De veldnamen die het belangrijkst zijn volgens het MovE-invulboek, staan
    <strong>vet</strong> aangegeven.
    </p>
    """).render()
    utils.s("writing report")
    html += fs.generateReport()
    
    utils.s("generating collectionstats")
    fs = collectionstats.Collection(the_doc)
    utils.s("writing report")
    html += fs.generateReport(no_compliance, no_thesaurus)
    
    return html

def generate_thesaurusreport(filename):
    '''Generate HTML report about the thesaurus of an adlib
    library.'''
    th = thesaurus.Thesaurus()
    th.name = dn(filename)
    utils.s("parsing file %s" % (filename))
    the_doc = ElementTree(file=filename)
    utils.s("parsing thesaurus")
    th.parseAdlibDoc(the_doc)
    html = ""
    html += "<h1>Thesaurus: %s</h1>" % (dn(filename))
    html += "<p>Aantal termen: %s</p>" % (len(th.terms.keys()))
    
    html += htmlutils.HelpElement(show="Toon uitleg bij deze vergelijkingen", help="""
    <p>Onderstaande tabellen vergelijken de thesaurus uit de gebruikte registratiesoftware
    met een aantal standaard-thesauri.<br/>
    Er wordt geteld hoeveel termen uit de eigen thesaurus overeenkomen met de standaard-thesaurus.</p>
    <p>Bemerk dat dit een andere vergelijking is dan hoger bij "Gebruik van 
    thesaurustermen": Hier worden de thesauri term per term vergeleken, 
    onafhankelijk van het aantal keren dat een thesaurusterm werkelijk gebruikt werd
    in de collectie. In het hoofdstuk "Gebruik van thesaurustermen" wordt
    rekening gehouden met hoeveel objecten de term werkelijk gebruiken.</p>
    <p>Mogelijke resultaten zijn:</p>
    <dl>
      <dt>Voorkeurterm</dt><dd>De term uit de eigen thesaurus komt overeen met een voorkeurterm
      uit de standaard-thesaurus.</dd>
      <dt>Niet de voorkeurterm</dt><dd>De term uit de eigen thesaurus bestaat
      in de standaard-thesaurus maar is niet de voorkeurterm. De waarde zou vervangen
      moeten worden door de voorkeurterm.</dd>
      <dt>Niet in de ... thesaurus</dt><dd>De term is niet bekend in de standaard-thesaurus.</dd>
    </dl>
    """).render()
    
    utils.s("writing report")
    for thesa in thesaurus.getThesauri():
        html += thesa.getThesaurusThesaurusReport(th)
    html += "<h2>Overzicht gebruikte velden bij de zelf gedefinieerde termen</h2>\n\n"
    html += htmlutils.HelpElement(show="Toon uitleg bij deze tabel", help="""
    <p>Onderstaande tabel toont alle velden die ingevuld werden voor minstens 
    &eacute;&eacute;n thesaurusterm die in de registratiedatabank werd ingevoerd.
    Voor elk veld wordt volgende informatie getoond:</p>
    <dl>
      <dt>VELD</dt><dd>De naam van het veld.</dd>
      <dt>% GEBRUIKT</dt><dd>Het percentage van de thesaurustermen waarvoor dit veld is ingevuld.
          Opgepast: een waarde "0" geldt ook als ingevuld.</dd>
      <dt>AANTAL</dt><dd>Het aantal thesaurustermen waarvoor dit veld is ingevuld.</dd>
      <dt>MEERVOUDIGE WAARDE</dt><dd>Dit geeft aan hoeveel keer het veld 
          <em>gemiddeld</em> is ingevuld per thesaurustermen. Een waarde van "1.2" betekent dat het 
          veld meestal slechts &eacute;&eacute;nmaal is ingevuld, maar voor sommige thesaurustermen
          twee (of meerdere) keren.<br/>
          Indien het veld meermaals is ingevuld voor ook maar &eacute;&eacute;n thesaurusterm, wordt
          het vakje paars gekleurd.</dd>
      <dt>GEM. VELDLENGTE</dt><dd>Het gemiddeld aantal karakters dat ingevuld werd in het veld.</dd>
      <dt>UNIEKE WAARDEN</dt><dd>Het aantal verschillende waarden dat ingevuld werd in dit veld.</dd>
    </dl>
    <p>Je kunt op de kolomtitel klikken om de tabel te sorteren volgens die kolom.</p>
    <p>Als je met de muis boven de naam van het veld hangt (waarde in de kolom "VELD"),
    krijg je een tooltip met daarin de verschillende waarden die zijn ingevuld voor dit veld
    en het aantal objecten waarvoor deze waarde is ingevuld.<br/>
    Wanneer je het vinkje aanklikt v&oacute;&oacute;r de naam van het veld, verschijnt
    dit detailtabelletje onderaan de grote tabel, zodat je dit eventueel kunt afdrukken.<br/>
    Opgepast: de tooltip en de checkbox verschijnen alleen indien niet teveel verschillende waarden
    bestaan.</p>
    """).render()
    
    utils.s("generating fieldstats notdoc")
    fs = fieldstats.FieldStats(the_doc, documentfilter=thesaurus.notInAnyDocFilter)
    utils.s("writing report")
    html += fs.generateReport()
    
    return html

def get_header():
    '''Retrieve HTML header data from file'''
    with open(os.path.join(os.path.dirname(__file__),'html/header.html'), 'r') as f:
        read_data = f.read()
    f.closed
    return read_data

def get_footer():
    '''Retrieve HTML footer data from file'''
    with open(os.path.join(os.path.dirname(__file__),'html/footer.html'), 'r') as f:
        read_data = f.read()
    f.closed
    return read_data

def usage():
    '''Print usage help message to console'''
    print "usage: adlibstats [--verbose] [--no-compliance-test] [--no-thesaurus-test] --csvfieldstats=FILENAME --fieldstats=FILENAME --objectstats=FILENAME --thesaurusstats=FILENAME"

def main():
    '''Main method of this program. Generate stats for one museum, with options supplied on commandline.'''
    output = sys.stdout
    try:
        opts, args = getopt.getopt(sys.argv[1:], "", ["verbose", "no-thesaurus-test", "no-compliance-test", "csvfieldstats=" ,"fieldstats=", "objectstats=", "outputfile=", "thesaurusstats=", "help"])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(2)
    
    nothing = True
    noCompliance = False
    noThesaurus = False
    # pre-parsing
    for o,a in opts:
        if o == "--help":
            usage()
            sys.exit(2)
        if o == "--outputfile":
            output = file(a,"w")
        if o == "--verbose":
            utils.verbose = True
        if o == "--no-compliance-test":
            noCompliance = True
        if o == "--no-thesaurus-test":
            noThesaurus = True
    
    # main loop
    
    
    buf = ""
    for o,a in opts:
        if o == "--fieldstats":
            buf += generate_report(a)
            nothing = False
        if o == "--csvfieldstats":
            buf += generate_csvreport(a)
            nothing = False
        if o == "--objectstats":
            buf += generate_compliancereport(a,noCompliance, noThesaurus)
            nothing = False
        if o == "--thesaurusstats":
            buf += generate_thesaurusreport(a)
            nothing = False
            
            
    if (nothing):
        usage()
        sys.exit(2)

        
    output.write(get_header())
    output.write(buf)
    output.write(get_footer())


def ensureList(datamap, key):
    '''Ensure that datamap[key] exists and is a list.
    The returned object is always a list, that could
    be empty or contain only one element'''
    if (not (key in datamap)):
        return []
    data = datamap[key]
    if (type(data) == list):
        return data
    if (data == ""):
        return []
    return [data]

def generateReportFile(reportfilename, datamap, compliance_test=False, thesaurus_test=True, verbose=True):
    '''Obtain all data and write to HTML. This method is called by regenAll.
    datamap is a mapping of museum data files.'''
    output = file(reportfilename,"w")
    output.write(get_header())
    if "name" in datamap:
        output.write("<div class='title'>Statistieken <strong>%s</strong></div>\n" % (datamap['name']))
    utils.verbose = verbose
    for infile in ensureList(datamap,"objects"):
        output.write(generate_compliancereport(infile, not compliance_test, not thesaurus_test))
    for infile in ensureList(datamap,"thesaurus"):
        output.write(generate_thesaurusreport(infile))
    for infile in ensureList(datamap,"fieldstats"):
        output.write(generate_report(infile))
    for infile in ensureList(datamap,"csvfieldstats"):
        output.write(generate_csvreport(infile))
    output.write(get_footer())



if __name__ == '__main__':
    main()