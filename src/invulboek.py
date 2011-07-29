# -*- coding: utf-8 -*-
'''
This module contains the definitions of categories
of field types and validation criteria for those fields.
These are used to determine to which AM-MovE levels the
data of museum collection objects is satisfied.
More info on AM-MovE: http://www.museuminzicht.be/public/musea_werk/thesaurus/index.cfm

Created on Jan 6, 2011

@author: kervel
'''

invulboek_fields = {}
invulboek_possiblevalues = {}

'''
    Definitions of fields required for each category or level
'''

'''Minimal required fields for each museum item'''
invulboek_fields["MovE Minimale registratie"] = [
        "institution.name",
        "object_number",
        "object_name",
        "title",
        "acquisition.date",
        "acquisition.method",
        "acquisition.source",
        "location"
    ]

'''Minimal required fields for "ontsluiting" category'''
invulboek_fields["Ontsluiting - minimaal"] = [
        "institution.name",
        "object_number",
        "object_name"
#        "object_category",
    ]

'''Fields required for reaching a detailed documentation level of "Onstluiting" category'''
invulboek_fields["Ontsluiting"] = invulboek_fields["Ontsluiting - minimaal"] + [
        "description",
        "creator",
        "production.date.start",
    ]

'''Fields required for conforming to "Ontsluiting met foto" category'''
invulboek_fields["Ontsluiting met foto"] = invulboek_fields["Ontsluiting"] + [
        "reproduction.identifier_URL"
    ]

'''Minimal fields required for objects of category "beheer"'''
invulboek_fields["Minimaal beheer"] = invulboek_fields["Ontsluiting"] + [
        "location",
        "acquisition.method",
    ]

'''Minimal fields required for qualifying for "MovE Basis registratie" criteria'''
invulboek_fields["MovE Basis registratie"] = invulboek_fields["MovE Minimale registratie"] + [
        "description",
        "creator",
        "production.date.start",
        "material",
        "dimension.value",
        "dimension.unit",
        "condition",
        "acquisition.price.value",
        "acquisition.price.currency"
    ]


'''
    Validation criteria of the fields (a field could belong to multiple categories)
    Specified as a list of exact values that are accepted. 
'''

'''Accepted acquisition.method values'''
invulboek_possiblevalues["acquisition.method"] = [
        "aankoop",
        "bruikleen",
        "legaat",
        "museum",
        "opdracht",
        "overdracht",
        "ruil",
        "schenking",
        "vondst",
        "onbekend"
    ]

'''Accepted condition values'''
invulboek_possiblevalues["condition"] = [
        "goed",
        "redelijk",
        "matig",
        "slecht"
    ]

'''Accepted dimension_unit values'''
invulboek_possiblevalues["dimension_unit"] = [
	"cm",
	"m",
	"kg",
	"gr",
	"mm",
	"s",
	"u",
	"min"
]

'''Accepted dimension values'''
invulboek_possiblevalues["dimension"] = [
	"hoogte", 
	"breedte",
	"diepte", 
	"diameter",
	"schaal",
	"gewicht",
    "lengte"
]


'''Fill allfields list'''
allfields = []

for x in invulboek_fields.keys():
    for fn in invulboek_fields[x]:
        if (not (fn in allfields)):
            allfields.append(fn)
            
