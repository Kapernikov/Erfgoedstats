# -*- coding: utf-8 -*-
'''
Main module for regenerating stats for all musea.

Created on 19 feb. 2011

@author: rein
'''
import adlibstats
import utils

import hashlib
import os
import traceback
import codecs

utils.verbose = True

musea = {}

musea["AbdijmuseumTenDuinen"] = {"name" : "Abdijmuseum Ten Duinen Koksijde", 
                         "objects" : "../data/musea/Abdijmuseum Ten Duinen/TenDuinen_all_Objecten.xml" , 
                         "thesaurus" : "../data/musea/Abdijmuseum Ten Duinen/TenDuinen_all_Thesaurus.xml", 
                         "fieldstats" : ["../data/musea/Abdijmuseum Ten Duinen/TenDuinen_all_Personen-filtered.xml"]}
musea["AbdijmuseumTenDuinen DB1"] = {"name" : "Abdijmuseum Ten Duinen - Adlib 1", 
                         "objects" : "../data/musea/Abdijmuseum Ten Duinen/TenDuinen_1_Objecten.xml" , 
                         "thesaurus" : "../data/musea/Abdijmuseum Ten Duinen/TenDuinen_1_Thesaurus.xml", 
                         "fieldstats" : ["../data/musea/Abdijmuseum Ten Duinen/TenDuinen_1_Personen-filtered.xml"]}
musea["AbdijmuseumTenDuinen DB3"] = {"name" : "Abdijmuseum Ten Duinen - Adlib 3", 
                         "objects" : "../data/musea/Abdijmuseum Ten Duinen/TenDuinen_3_Objecten.xml" , 
                         "thesaurus" : "../data/musea/Abdijmuseum Ten Duinen/TenDuinen_3_Thesaurus.xml", 
                         "fieldstats" : ["../data/musea/Abdijmuseum Ten Duinen/TenDuinen_3_Personen-filtered.xml"]}

musea["Bakkerijmuseum"] = {"name" : "Bakkerijmuseum Veurne", 
                         "objects" : "../data/musea/bakkerijmuseum/bakkerijmuseum-objecten.xml" , 
                         "thesaurus" : "../data/musea/bakkerijmuseum/bakkerijmuseum-thesaurus.xml", 
                         "fieldstats" : ["../data/musea/bakkerijmuseum/bakkerijmuseum-personen.xml", "../data/musea/bakkerijmuseum/bakkerijmuseum-boeken.xml", "../data/musea/bakkerijmuseum/bakkerijmuseum-uitgaande-bruiklenen.xml"]}

musea["Broelmuseum"] = {"name" : "Broelmuseum Kortrijk", 
                         "objects" : "../data/musea/broelmuseum/broelmuseumobjecten.xml" , 
                         "thesaurus" : "../data/musea/broelmuseum/broelmuseumthesaurus.xml", 
                         "fieldstats" : ["../data/musea/broelmuseum/broelmuseumpersoneneninstellingen.xml"]}
musea["BroelmuseumMSK"] = {"name" : "Broelmuseum Kortrijk - Collectie MSK", 
                         "objects" : "../data/musea/broelmuseum/broelmuseummsk.xml"}

musea["BruggeBibliotheek"] = {"name" : "Musea Brugge, Bibliotheek", 
                         "fieldstats" : ["../data/musea/Bruggemuseum - bibliotheek/BruggeBibBoeken.xml"]}

musea["Bruggemuseum"] = {"name" : "Musea Brugge, Bruggemuseum Gruuthuse", 
                         "objects" : "../data/musea/Bruggemuseum - bruggemuseum/BruggemuseumBruggeObjects.xml" , 
                         "thesaurus" : "../data/musea/Bruggemuseum - bruggemuseum/BruggemuseumBruggeThesaurus.xml", 
                         "fieldstats" : ["../data/musea/Bruggemuseum - bruggemuseum/BruggemuseumBruggePersons.xml"]}

musea["BruggeVolkskunde"] = {"name" : "Musea Brugge, Bruggemuseum Volkskunde", 
                         "objects" : "../data/musea/Bruggemuseum - volkskunde/BruggeVolkskunde.xml" , 
                         "thesaurus" : "../data/musea/Bruggemuseum - volkskunde/BruggeVolkskundeThesaurus.xml", 
                         "fieldstats" : ["../data/musea/Bruggemuseum - volkskunde/BruggeVolkskundePersonen.xml"]}

musea["Bulskampveld"] = {"name" : "Provinciaal Museum Bulskampveld Beernem", 
                         "objects" : "../data/musea/Bulskampveld Beernem/Bulskampveld_Objecten.xml" , 
                         "thesaurus" : "../data/musea/Bulskampveld Beernem/Bulskampveld_Thesaurus.xml", 
                         "fieldstats" : ["../data/musea/Bulskampveld Beernem/Bulskampveld_Personen.xml"]}

musea["GeorgeGrard"] = {"name" : "Museum George Grard",
                            "objects": "../data/musea/GeorgeGrard/georgegrard-objecten.xml",
                            "thesaurus": "../data/musea/GeorgeGrard/georgegrard-thesaurus.xml",
                            "fieldstats": ["../data/musea/GeorgeGrard/georgegrard-personeninstellingen.xml"]}

musea["Groeningemuseum"] = {"name" : "Musea Brugge, Groeningemuseum", 
                         "objects" : "../data/musea/Bruggemuseum - Groeninge/BruggeGroeningeObjects.xml" , 
                         "thesaurus" : "../data/musea/Bruggemuseum - Groeninge/BruggeGroeningeThesaurus.xml", 
                         "fieldstats" : ["../data/musea/Bruggemuseum - Groeninge/BruggeGroeningePersonen.xml"]}

musea["Ieper_alles"] = {"name" : "Stedelijke Musea Ieper (alle)",
                        "objects" : "../data/musea/Ieper/Ieper_Objecten_all.xml",
                        "thesaurus" : "../data/musea/Ieper/Ieper_Thesaurus.xml",
                        "fieldstats" : ["../data/musea/Ieper/Ieper_PersonenInstellingen.xml"]}
musea["Ieper_FlandersFields"] = {"name" : "Stedelijke Musea Ieper: In Flanders Fields",
                        "objects" : "../data/musea/Ieper/Ieper_Objecten_FlandersFields.xml"}
musea["Ieper_GodshuisBelle"] = {"name" : "Stedelijke Musea Ieper: Godshuis Belle",
                        "objects" : "../data/musea/Ieper/Ieper_Objecten_GodshuisBelle.xml"}
musea["Ieper_Merghelynck"] = {"name" : "Stedelijke Musea Ieper: Merghelynck",
                        "objects" : "../data/musea/Ieper/Ieper_Objecten_Merghelynck.xml"}
musea["Ieper_Onderwijsmuseum"] = {"name" : "Stedelijke Musea Ieper: Onderwijsmuseum",
                        "objects" : "../data/musea/Ieper/Ieper_Objecten_Onderwijsmuseum.xml"}
musea["Ieper_StedelijkMuseum"] = {"name" : "Stedelijke Musea Ieper: Stedelijk Museum",
                        "objects" : "../data/musea/Ieper/Ieper_Objecten_StedelijkMuseum.xml"}

musea["Izegem_Borstels"] = {"name" : "Stedelijke Musea Izegem (Collectie Borstels)",
                            "objects": "../data/musea/Izegem/Izegem-collectie-borstels.xml",
                            "thesaurus": "../data/musea/Izegem/Izegem-thesaurus.xml",
                            "fieldstats": "../data/musea/Izegem/Izegem-personen-instellingen.xml"}
musea["Izegem_Schoeisel"] = {"name" : "Stedelijke Musea Izegem (Collectie Schoeisel)",
                            "objects": "../data/musea/Izegem/Izegem-collectie-schoeisel.xml",
                            "thesaurus": "../data/musea/Izegem/Izegem-thesaurus.xml",
                            "fieldstats": "../data/musea/Izegem/Izegem-personen-instellingen.xml"}

musea["Hopmuseum"] = {"name" : "Hopmuseum Poperinge", 
                         "objects" : "../data/musea/hopmuseum-poperinge/poperinge-objects.xml" , 
                         "thesaurus" : "../data/musea/hopmuseum-poperinge/poperinge-thesaurus.xml", 
                         "fieldstats" : ["../data/musea/hopmuseum-poperinge/poperinge-personen-materialen.xml"]}

musea["Hospitaalmuseum"] = {"name" : "Musea Brugge, Hospitaalmuseum", 
                         "objects" : "../data/musea/Bruggemuseum - hospitaalmuseum/BruggeHospitaalObjects.xml" , 
                         "thesaurus" : "../data/musea/Bruggemuseum - hospitaalmuseum/BruggeHospitaalThesaurus.xml", 
                         "fieldstats" : ["../data/musea/Bruggemuseum - hospitaalmuseum/BruggeHospitaalPersons.xml"]}

musea["MemorialMuseumPaschendaele1917"] = {"name" : "Memorial Museum Paschendaele 1917 Zonnebeke",
                        "objects" : "../data/musea/Memorial Museum Paschendaele 1917/MMP_Objecten.xml",
                        "thesaurus" : "../data/musea/Memorial Museum Paschendaele 1917/MMP_Thesaurus.xml",
                        "fieldstats" : ["../data/musea/Memorial Museum Paschendaele 1917/MMP_PersonenInstellingen.xml"]}

musea["MuZee"] = {"name" : "Mu.ZEE", 
                         "objects" : "../data/musea/muzee/muzeeobjecten.xml" , 
                         "thesaurus" : "../data/musea/muzee/muzeethesaurus.xml", 
                         "fieldstats" : ["../data/musea/muzee/muzeepersoneneninstellingen.xml"]}

musea["OudeKaasmakerij"] = {"name" : "De oude kaasmakerij Passendale",
                        "objects" : "../data/musea/Oude Kaasmakerij Passendale/OKM_Objecten.xml",
                        "thesaurus" : "../data/musea/Oude Kaasmakerij Passendale/OKM_Thesaurus.xml",
                        "fieldstats" : ["../data/musea/Oude Kaasmakerij Passendale/OKM_PersonenInstellingen.xml"]}
                        
musea["Raversijde"] = {"name" : "Provindiaal Domein Raversijde Oostende",
                            "objects": "../data/musea/Raversijde/raversijdeobjecten.xml",
                            "thesaurus": "../data/musea/Raversijde/raversijdethesaurus.xml",
                            "fieldstats": ["../data/musea/Raversijde/raversijdepersoneneninstellingen.xml"]}

musea["StijnStreuvelsLijsternest"] = {"name" : "Provinciaal Museum Stijn Streuvels Ingooigem", 
                         "objects" : "../data/musea/Stijn Streuvels - Lijsternest/StijnStreuvels_Objecten.xml" , 
                         "thesaurus" : "../data/musea/Stijn Streuvels - Lijsternest/StijnStreuvels_Thesaurus.xml", 
                         "fieldstats" : ["../data/musea/Stijn Streuvels - Lijsternest/StijnStreuvels_Personen.xml"]}

musea["TalbotHouse"] = {"name" : "Talbot House Poperinge", 
                         "objects" : "../data/musea/Talbot house/talbothouse-objects-converted.xml" , 
                         "thesaurus" : "../data/musea/Talbot house/talbothouse-thesaurus-converted.xml", 
                         "fieldstats" : ["../data/musea/Talbot house/talbothouse-personen-converted.xml", "../data/musea/Talbot house/talbothouse-documentatie-literatuur-converted.xml"]}

musea["Visserijmuseum"] = {"name" : "Visserijmuseum Oostduinkerke",
                            "csvfieldstats": "../data/musea/Visserijmuseum/export-visserijmuseum-utf8.txt"}

musea["Vlasmuseum"] = {"name" : "Vlasmuseum Kortrijk", 
                         "objects" : "../data/musea/vlasmuseum/vlasmuseum objecten.xml" , 
                         "thesaurus" : "../data/musea/vlasmuseum/vlasmuseum thesaurus.xml", 
                         "fieldstats" : ["../data/musea/vlasmuseum/vlasmuseum personen en instellingen.xml"]}

musea["Wielermuseum"] = {"name" : "Wielermuseum Roeselare", 
                         "objects" : "../data/musea/Wielermuseum Roeselare/wielermuseum roeselare objecten.xml" , 
                         "thesaurus" : "../data/musea/Wielermuseum Roeselare/wielermuseum roeselare thesaurus.xml", 
                         "fieldstats" : ["../data/musea/Wielermuseum Roeselare/wielermuseum roeselare boeken.xml"]}


output_suffix = "-nc"

def main():
    '''(Re)generate stats for all museums. Within this method, a HTML
    report is made with an overview of all files written.'''
    buf = "<h1>Overzicht onderzochte musea West-Vlaanderen</h1>\n"
    buf+="<ul>\n"
    
    for museumkey in sorted(musea.keys(), key=lambda x: musea[x]["name"] ):
        if not utils.testmode or museumkey=="AbdijmuseumTenDuinen DB3":
            # In testmode doen we alleen het kleinste museum
            museum = musea[museumkey]
            print "Regenerating " + museum["name"]
            htmlfn = museumkey + output_suffix + '-' + hashlib.md5(museumkey).hexdigest()[:6].upper() + ".html"
            htmlfile = os.path.join("..", "out", htmlfn)
            buf += "\t<li><a href=\"" + htmlfn + "\">" + museum["name"] + "</a></li>\n"
            try:
                                                        # Compliance test is always forced to false
                adlibstats.generateReportFile(htmlfile, museum, compliance_test=False, thesaurus_test=True, verbose=True)
            except Exception as e:
                'TODO: informatiever maken'
                print "---- >>>> MISLUKT"
                traceback.print_exc()
        
    buf += "</ul>\n"
    
    output = codecs.open("../out/lijst.html",encoding="utf-8", mode="w")
    output.write(adlibstats.get_header())
    output.write(buf)
    output.write(adlibstats.get_footer())
    
    
if __name__ == '__main__':
    main()

