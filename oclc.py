# IMPORTAZIONE LIBRERIE / PACKAGES IMPORT
from pymarc import MARCReader
from langdetect import detect
from googletrans import Translator
from langid import classify
from copy import deepcopy
from time import sleep
import os

# RICONOSCIMENTO AUTOMATICO LINGUA / AUTOMATED LANGUAGE DETECTION
def get_lang(text):
    google = Translator()
    try:
        google_code = google.translate(text).src    # Google Translate API
        detect_code = detect(text)  # Langdetect
        langid_code = classify(text)[0] # Langid
        sleep(0.3)
    except:
        pass
    if ((google_code == detect_code) or (google_code == langid_code) or (detect_code == langid_code)):  # if 2 on 3 are equals than the detected language is considered reliable
        return google_code
    else:
        raise Exception()
    
# NORMALIZZAZIONE CODICE LINGUA / LANGUAGE CODE NORMALISATION
def iso_lang(auto_lang):
    if auto_lang == 'it':
        lang = 'ita'
    elif auto_lang == 'en':
        lang = 'eng'
    elif auto_lang == 'de':
        lang = 'ger'
    elif auto_lang == 'fr':
        lang = 'fre'
    else:
        lang = False
    return lang

# VERIFICA CORRETTEZZA LINGUA / LANGUAGE CHECK
#  for each text in field 5**, if text contains one of the terms in the array, forced_lang is set
# if cataloguing language and forced_lang are equals, the function returns True
# if cataloguing language and forced_lang are not equals, automatic language detection is applied to text (as before 2 on 3 to be considered reliable). 
# If detected language and cataloguing language are equals, the function returns True, else False
# if function returns True nothing happens, else "" are added to text and saved to final MARC file

def lang_check(forced_lang, lang, text):
    # List of hardcoded terms for language match
    if text in ["Bibliografia", "Indice", "italiano", "Titolo originale", "In cofanetto", "Testo", "Catalogo", "Pubblicato", "Frontespizio"]:
        forced_lang = "ita"
    elif text in [" the ", "The ", " and ", "Publ. ", "Index.", "Includes", "Introduction", "Exhibition", "Exhibitions"]:
        forced_lang = "eng"
    elif text in [" und ", "Enthält", "Originaltitel", "zweisprachig", "Name auch", "Titel auf der Mappe", "Abweichender", "Katalog", "Ausstellung", "zweisprachig"]:
        forced_lang = "ger"
    elif text in ["Titre du Companion text", "Textes", "Traduit", "Notes bibliogr", "Portrait", "Catalogues d'exposition", "Exposition"]:
        forced_lang = "fre"
    
    if forced_lang == lang:
        return True
    else:
        google = Translator()
        try:
            google_code = iso_lang(google.translate(text).src)
            detect_code = iso_lang(detect(text))
            sleep(0.2)
        except:
            google_code = ""
            detect_code = ""
        if ((google_code == lang) and (detect_code == lang)):
            return True
        else:
            try:
                google_code = iso_lang(google.translate(text).src)
                langid_code = iso_lang(classify(text)[0])
                sleep(0.2)
            except:
                google_code = ""
                detect_code = ""
        if ((google_code == lang) or (langid_code == lang)):
            return True
        else:
            return False

############################## MAIN ####################################
# Script starts from here
def update_marc():

    # INIZIALIZZAZIONE VARIABILI
    it = "ita"
    ger = "ger"
    fr = "fre"
    en = "eng"
    lang = ""
    forced_lang = ""
    period_arr_it = ['annuale', 'biennale', 'bimensile', 'bisettimanale', 'mese', 'irregolare', 'mensile', 'settimane', 'quotidiano', 'semestrale', 'settimanale', 'anno', 'settimana', 'triennale', 'trimestrale']
    period_arr_de = ['jahre', 'monate', 'wochen', 'jahr', 'monat', 'woche', 'halbjährlich', 'jährlich', 'monatlich', 'täglich', 'unregelmäßig', 'vierteljährlich', 'wöchentlich']
    period_arr_fr = ['annuel', 'biennal', 'bihebdomadaire', 'bimensuel', 'hebdomadaire', 'irrégulier', 'mensuel', 'quotidien', 'semestriel', 'semaine', 'semaines', 'triennal', 'trimestriel', 'par an', 'mois']

    # LETTURA FILE MARC / READING MARC FILE
    with open('output.mrc', 'ab') as write_file:
        for file in os.listdir('test'):      
            if file.endswith(".mrc"):           
                with open('test/'+file, 'rb') as marc_file:
                    reader = MARCReader(marc_file, force_utf8=True)
                    for record in reader:
                        my_record = deepcopy(record)    # Changes apply only to in-memory copy of MARC record

                        # MMS_ID
                        try:
                            mms_id = record.get_fields('001')   # MMS_ID extraction from field 001
                            for g in mms_id:
                                create_file = g.value() + ".mrc"    # MMS_ID is used to name the final MARC file
                        except:
                            with open("errori/errors.txt", 'a') as err_file:    # On error the MARC record is excluded and the loop between records is resumed
                                err_file.write(file)
                            continue
                        
                        # Se LUBUL in 040 $a la lingua è italiano / If LUBUL in 040 $a cataloguing language = ita
                        if record.get_fields('040') is not None:
                            for f_040 in record.get_fields('040'):
                                if (f_040.get_subfields('a') is not None and len(f_040.get_subfields('a')) > 0):    # if 040 $a is not empty             
                                    if "LUBUL" in f_040.get_subfields('a')[0]:  # if "LUBUL" in 040 $a
                                        lang = it   # cataloguing language = ita
                                        my_langs = my_record.get_fields('040')
                                        my_langs[0].add_subfield('b', lang, pos=1)  # add $bita to field 040

                        # Lingua di catalogazione in base al testo 300 / Cataloguing language based on field 300
                        # If 300 text contains a specific term, cataloguing language is set
                        # If text contains an ambiguous term, language set in 040 $b is used as cataloguing language
                        # if 300 text does not contains any of the hardcoded terms, automatic language detection is used (2 on 3)
                        if record.get_fields('300') is not None:
                            for f_300 in record.get_fields('300'):
                                c_300 = f_300.value().lower()
                                if c_300 in ["pagine", "carta", "carte", "volume", "volumi", "tomo", "tomi", "fascicolo", "fascicoli", "senza paginazione", "non numerat", "foglio",
                                            "fogli", "cartina", "cartine", "disco", "dischi", "cd", "cd-rom", "dvd", "dvd-rom", "blu-ray", "vhs"]:
                                    lang = it
                                elif c_300 in ["bd.", "seiten", "s.", "band", "bände", "bde", "volumen", "heft", "hefte", "nicht paginiert", "ohne seitenzählung", "karte", 
                                            "karten", "blatt", "blätter", "mappe"]:
                                    lang = ger
                                elif c_300 in ["volumes", "tome", "tomes", "fascicule", "fascicules", "non paginé", "cartes", "feuille", "feuilles", "disque", "disques"
                                            "disquette", "disquettes"]:
                                    lang = fr
                                elif c_300 in ["issue", "issues", "map", "maps"]:
                                    lang = en
                                elif c_300 in ["pages", "axi", "axv", "vol.", " p."]:   # ambiguous terms
                                    if my_record.get_fields('040') is not None:
                                        for my_040 in my_record.get_fields('040'):
                                            if (my_040.get_subfields('b') is not None and len(my_040.get_subfields('b')) > 0):  # if 040 $b is not empty
                                                lang = my_040.get_subfields('b')[0] # 040 $b is used as cataloguing language
                                else:
                                    try:
                                        auto_lang = get_lang(c_300) # Automatic language detection
                                        lang = iso_lang(auto_lang)  # Language Code normalisation
                                    except:
                                        lang = ""
                        
                        elif record.get_fields('300') is None and record.get_fields('310') is not None: # if 300 is empty and 310 is not empty
                            for f_310 in record.get_fields('310'):
                                if (f_310.get_subfields('a') is not None and len(f_310.get_subfields('a')) > 0):
                                    val_310 = f_310.get_subfields('a')[0].lower()   # 310 text extraction
                                    if val_310 in period_arr_it:    # if text contains a term in the array (line 94-96) cataloguing language is set
                                        lang = it
                                        with open("periodici/"+create_file, 'wb') as period_file:   
                                            period_file.write(my_record.as_marc())
                                    elif val_310 in period_arr_de:
                                        lang = ger
                                        with open("periodici/"+create_file, 'wb') as period_file:
                                            period_file.write(my_record.as_marc())
                                    elif val_310 in period_arr_fr:
                                        lang = fr
                                        with open("periodici/"+create_file, 'wb') as period_file:
                                            period_file.write(my_record.as_marc())
                                    else:
                                        lang = ''
                        
                        elif (record.get_fields('300') is None and record.get_fields('310') is None and record.get_fields('321') is not None):  # if 300 and 310 are empty and 321 is not empty
                            for f_321 in record.get_fields('321'):
                                if (f_321.get_subfields('a') is not None and len(f_321.get_subfields('a')) > 0):
                                    val_321 = f_321.get_subfields('a')[0].lower()   # 321 text extraction
                                    if val_321 in period_arr_it:    # if text contains a term in the array (line 94-96) cataloguing language is set
                                        lang = it
                                        with open("periodici/"+create_file, 'wb') as period_file:
                                            period_file.write(my_record.as_marc())
                                    elif val_321 in period_arr_de:
                                        lang = ger
                                        with open("periodici/"+create_file, 'wb') as period_file:
                                            period_file.write(my_record.as_marc())
                                    elif val_321 in period_arr_fr:
                                        lang = fr
                                        with open("periodici/"+create_file, 'wb') as period_file:
                                            period_file.write(my_record.as_marc())
                                    else:
                                        lang = ''

                        # Linga campo 040 / Language field 040
                        if my_record.get_fields('040') is not None:
                            for f_040 in my_record.get_fields('040'):
                                if (f_040.get_subfields('b') is not None and len(f_040.get_subfields('b')) > 0):    # if 040 $b exists lang_040 is set
                                    lang_040 = f_040.get_subfields('b')[0]
                                elif (f_040.get_subfields('b') is None or len(f_040.get_subfields('b')) == 0):  # if 040 $b is empty
                                    if lang != "":  # if cataloguing language is not null, lang_040 is equal to cataloguing language
                                        lang_040 = lang
                                        my_langs = my_record.get_fields('040')
                                        my_langs[0].add_subfield('b', lang, pos=1)  # cataloguing language is set in 040 $b subfield
                                    elif lang == '':    # if cataloguing language is not set, the default language is set as Italian
                                        lang_040 = 'ita'
                                        lang = 'ita'
                                        my_langs = my_record.get_fields('040')
                                        my_langs[0].add_subfield('b', 'ita', pos=1) # Italian is set as language in 040 $b

                        # Se lingua di catalogazione e lingua 040 non coincidono / if cataloguing language e lang_040 are not equals             
                        if lang != lang_040:
                            if lang != '':  # if cataloguing language is not set
                                lang_040 = lang # lang_040 is equal to cataloguing language
                                my_fields = my_record.get_fields('040')
                                for my_field in my_fields:
                                    my_field.delete_subfield('b')
                                    my_field.add_subfield('b', lang, pos=1) # 040 $b overwriting
                        
                        # Aggiornamento note 5XX / Field 5XX update (subfields $a, $t, $c)     
                        if record.get_fields('500', '501', '502', '504', '506', '507', '508', '510', '511', '513', '514', '515', '516', '518', '520', '521', '522', '524', '525', '526', '530', '532', '533', '535', '536', '538', '540', '541', '542', '544', '545', '546', '547', '550', '552', '555', '556', '561', '562', '563', '565', '567', '580', '581', '583', '584', '585', '586', '588', '590', '591', '592', '593', '594', '595', '596', '597', '598', '599') is not None:
                            notes = record.get_fields('500', '501', '502', '504', '506', '507', '508', '510', '511', '513', '514', '515', '516', '518', '520', '521', '522', '524', '525', '526', '530', '532', '533', '535', '536', '538', '540', '541', '542', '544', '545', '546', '547', '550', '552', '555', '556', '561', '562', '563', '565', '567', '580', '581', '583', '584', '585', '586', '588', '590', '591', '592', '593', '594', '595', '596', '597', '598', '599')
                            my_notes = my_record.get_fields('500', '501', '502', '504', '506', '507', '508', '510', '511', '513', '514', '515', '516', '518', '520', '521', '522', '524', '525', '526', '530', '532', '533', '535', '536', '538', '540', '541', '542', '544', '545', '546', '547', '550', '552', '555', '556', '561', '562', '563', '565', '567', '580', '581', '583', '584', '585', '586', '588', '590', '591', '592', '593', '594', '595', '596', '597', '598', '599')                      
                            if len(notes) > 0:
                                for my_note in my_notes:
                                    if (my_note.get_subfields('a') is not None and len(my_note.get_subfields('a')) > 0):
                                        try:
                                            if lang_check(forced_lang, lang, my_note.get_subfields('a')[0]) == False:   # if text language is not equal to cataloguing language
                                                if (my_note.get_subfields('a')[0].startswith('"') and my_note.get_subfields('a')[0].endswith('"')): # if text already contains ""
                                                    pass    # do nothing
                                                else:
                                                    a_value = my_note.get_subfields('a')[0]
                                                    my_note.delete_subfield('a')
                                                    my_note.add_subfield('a', '"'+a_value+'"')  # else overwrite text wrapped in ""
                                        except:
                                            with open("errori/"+create_file, 'wb') as err_file: # if there is an error the record is excluded and the loop between records is resumed
                                                err_file.write(my_record.as_marc())
                                            continue
                                    if (my_note.get_subfields('t') is not None and len(my_note.get_subfields('t')) > 0):
                                        try:
                                            if lang_check(forced_lang, lang, my_note.get_subfields('t')[0]) == False:
                                                if (my_note.get_subfields('t')[0].startswith('"') and my_note.get_subfields('t')[0].endswith('"')):
                                                    pass
                                                else:
                                                    t_value = my_note.get_subfields('t')[0]
                                                    my_note.delete_subfield('t')
                                                    my_note.add_subfield('t', '"'+t_value+'"') 
                                        except:
                                            with open("errori/"+create_file, 'wb') as err_file:
                                                err_file.write(my_record.as_marc())
                                            continue
                                    if (my_note.get_subfields('c') is not None and len(my_note.get_subfields('c')) > 0):
                                        try:
                                            if lang_check(forced_lang, lang, my_note.get_subfields('c')[0]) == False:
                                                if (my_note.get_subfields('c')[0].startswith('"') and my_note.get_subfields('c')[0].endswith('"')):
                                                    pass
                                                else:
                                                    c_value = my_note.get_subfields('c')[0]
                                                    my_note.delete_subfield('c')
                                                    my_note.add_subfield('c', '"'+c_value+'"') 
                                        except:
                                            with open("errori/"+create_file, 'wb') as err_file:
                                                err_file.write(my_record.as_marc())
                                            continue
                                        
                        
                        # Inserimento record in file di output
                        if my_record.get_fields('040') is not None:
                            for my_final_lang in my_record.get_fields('040'):
                                if (my_final_lang.get_subfields('b') is not None and len(my_final_lang.get_subfields('b')) > 0): # if 040 $b is set the record is written inside final MARC file
                                    write_file.write(my_record.as_marc())
                                else:
                                    with open("eccezioni/"+create_file, 'wb') as out_file:  # if 040 $b is not set MARC record is excluded from final MARC file
                                        out_file.write(my_record.as_marc())
    
    return 'Done'
