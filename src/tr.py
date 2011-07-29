# -*- coding: utf-8 -*-
'''
Translate fields from english to dutch

Created on Jan 7, 2011

@author: kervel
'''

'''Defines fieldnames in english, and their dutch translation'''
vertalingen = {
    "acquisition.date" : "Verwerving: Datum",
    "acquisition.method" : "Verwerving: Methode",
    "acquisition.price.value" : "Aankoopprijs",
    "acquisition.price.currency" : "Aankoopprijs: Valuta",
    "acquisition.source" : "Verwerving: Van",
    "address.country" : "Adres: Adres",
    "address.country" : "Adres: Land",
    "address.place" : "Adres: Plaats",
    "administration_name" : "Naam administratie",
    "alternative_number" : "Nummer",
    "alternative_number.type" : "Nummer: Soort",
    "association.person" : "Geassocieerde persoon/instelling: Naam",
    "association.person.type" : "Geassocieerde persoon/instelling: Soort naam",
    "collection" : "Collectie",
    "completeness" : "Compleetheid",
    "condition" : "Toestand",
    "condition.part" : "Toestand: Onderdeel",
    "condition.check.name" : "Toestand: Controleur",
    "condition.date" : "Toestand: Datum",
    "content.description" : "Inhoudsbeschrijving",
    "creator" : "Vervaardiger",
    "creator.date_of_birth": "Vervaardiger: Geboortedatum",
    "creator.date_of_death": "Vervaardiger: Sterftedatum",
    "current_owner" : "Huidige eigenaar",
    "description" : "Inhoudelijke beschrijving",
    "dimension.part" : "Afmeting: Onderdeel",
    "dimension.type" : "Afmeting: Afmeting",
    "dimension.unit" : "Afmeting: Eenheid",
    "dimension.value" : "Afmeting: Waarde",
    "documentation.author" : "Documentatie: Auteur",
    "documentation.page_reference" : "Documentatie: Pagina-aanduiding",
    "documentation.title" : "Documentatie: Titel",
    "input_by" : "Invoer: Naam",
    "inscription.content" : "Opschriften: Inhoud",
    "inscription.position" : "Opschriften: Positie",
    "institution.name" : "Instellingsnaam",
    "insurance.value" : "Verzekering: Waarde",
    "insurance.value.currency" : "Verzekering: Valuta",
    "insurance.valuer" : "Verzekering: Taxateur",
    "insurance.date" : "Verzekering: Datum",
    "location" : "Standplaats",
    "location.date.begin" : "Standplaats: Begindatum",
    "location.date.end" : "Standplaats: Einddatum",
    "location.default" : "Vaste standplaats",
    "location_check.date" : "Standplaatscontrole: Datum",
    "location_check.name" : "Standplaatscontrole: Controleur",
    "location_normal" : "Vaste standplaats",
    "location_notes" : "Vast standplaats: Bijzonderheden",
    "material" : "Materiaal",
    "material.part" : "Materiaal: Onderdeel",
    "name" : "Naam",
    "name.note" : "Naam: Opmerking",
    "name.type" : "Soort naam",
    "number_of_parts" : "Aantal",
    "object_category" : "Objectcategorie",
    "object_name" : "Objectnaam",
    "object_number" : "Objectnummer",
    "owner_hist.owner" : "Eigendomsgeschiedenis: Eigenaar",
    "owner_hist.date.begin" : "Eigendomsgeschiedenis: Datum vanaf",
    "owner_hist.date.end" : "Eigendomsgeschiedenis: Datum tot",
    "part" : "Onderdeel",
    "physical_description" : "Fysieke beschrijving",
    "preservation_form" : "Bewaarvorm",
    "production.date.end" : "Datering tot",
    "production.date.start" : "Datering van",
    "production.period" : "Datering: Periode",
    "production.place" : "Vervaardiging: Plaats",
    "reproduction.identifier_URL" : "Foto Bestandsnaam",
    "reproduction.reference" : "Foto referentie",
    "technique" : "Techniek",
    "technique_part" : "Technieken: Onderdeel",
    "title" : "Titel",
    "titel.type" : "Titel: Soort"
    }

'''Translate given string, which should be a field name,
from english to dutch, if a translation is defined for it.
Tries Changing . to _ and the other way around to find translation
for name. If no translation is found, the original input string
is returned.'''
def tr(x):
    if (x in vertalingen.keys()):
        return vertalingen[x]
    underscorenotation = x.replace(".","_")
    if (underscorenotation in vertalingen.keys()):
        return vertalingen[underscorenotation]
    dotnotation = x.replace("_",".")
    if (dotnotation in vertalingen.keys()):
        return vertalingen[dotnotation]
    return x