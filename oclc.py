# IMPORTAZIONE LIBRERIE / PACKAGES IMPORT
from pymarc import MARCReader
from langdetect import detect
from googletrans import Translator
from langid import classify
from copy import deepcopy
from time import sleep
import os

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
    forced_lang = ""
    period_arr_it = ['annuale', 'biennale', 'bimensile', 'bisettimanale', 'mese', 'irregolare', 'mensile', 'settimane', 'quotidiano', 'semestrale', 'settimanale', 'anno', 'settimana', 'triennale', 'trimestrale']
    period_arr_de = ['jahre', 'monate', 'wochen', 'jahr', 'monat', 'woche', 'halbjährlich', 'jährlich', 'monatlich', 'täglich', 'unregelmäßig', 'vierteljährlich', 'wöchentlich']
    period_arr_fr = ['annuel', 'biennal', 'bihebdomadaire', 'bimensuel', 'hebdomadaire', 'irrégulier', 'mensuel', 'quotidien', 'semestriel', 'semaine', 'semaines', 'triennal', 'trimestriel', 'mois']

    # LETTURA FILE MARC / READING MARC FILE
    with open('output.mrc', 'ab') as write_file:
        for file in os.listdir('marc'):      
            if file.endswith(".mrc"):           
                with open('marc/'+file, 'rb') as marc_file:
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
                        lang = False
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
                        if not lang:
                            if record.get_fields('300') is not None:
                                for f_300 in record.get_fields('300'):
                                    c_300_line = f_300.value().lower()
                                    c_300_array = c_300_line.split(' ')
                                    for c_300 in c_300_array:
                                        if c_300 in ["pagine", "carta", "carte", "volume", "volumi", "tomo", "tomi", "fascicolo", "fascicoli", "senza", "paginazione", "numerat", "foglio",
                                                    "fogli", "cartina", "cartine", "disco", "dischi", "cd", "cd-rom", "dvd", "dvd-rom", "blu-ray", "vhs", "illustrazioni", "tavole", "disegni", "fotografie",
                                                    "busta", "buste", "cofanetto", "cofanetti", "mappetta", "mappette", "pieghevole", "pieghevoli", "facsim.", "colori", "bianco/nero"]:
                                            lang = it
                                            break
                                        elif c_300 in ["bd.", "seiten", "s.", "band", "bände", "bde", "volumen", "heft", "hefte", "nicht", "paginiert", "ohne", "seitenzählung", "karte", 
                                                    "karten", "blatt", "blätter", "mappe", "illustrationen", "tafeln", "taf.", "abbildungen", "abb.", "fotografien", "faltblatt", "ordner", 
                                                    "schuber", "fak-sim."]:
                                            lang = ger
                                            break
                                        elif c_300 in ["volumes", "tome", "tomes", "fascicule", "fascicules", "paginé", "cartes", "feuille", "feuilles", "disque", "disques"
                                                    "disquette", "disquettes", "pages", "illustrations", "tables", "dessins", "photographies", "sans", "pagination", "noir", 
                                                    "fac-sim.", "couleur", "couleurs"]:
                                            lang = fr
                                            break
                                        elif c_300 in ["issue", "issues", "map", "maps", "drawings", "photographs"]:
                                            lang = en
                                            break
                                        else: lang = False
                                    
                                        
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
                                            lang = False


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
                                        else: lang = False

                        if not lang:
                            if record.get_fields('264') is not None:
                                for f_264 in record.get_fields('264'):
                                    if (f_264.get_subfields('a') is not None and len(f_264.get_subfields('a')) > 0):
                                        val_264 = f_264.get_subfields('a')[0].lower()
                                        if val_264 in ["[luogo di pubblicazione non identificato]", "[luogo di edizione non identificato]", "[luogo di stampa non identificato]"]:
                                            lang = it
                                        elif val_264 in ["[verlagsort nicht ermittelbar]", "[erscheinungsort nicht ermittelbar]"]:
                                            lang = ger
                                        elif val_264 in ["[lieu de publication non identifié]"]:
                                            lang = fr
                                        else: lang = False

                        if not lang:
                            if record.get_fields('264') is not None:  
                                for f_264 in record.get_fields('264'):  
                                    if (f_264.get_subfields('b') is not None and len(f_264.get_subfields('b')) > 0):
                                        val_264_b = f_264.get_subfields('b')[0].lower()
                                        if val_264_b in ["editore non identificato"]:
                                            lang = it
                                        elif val_264_b in ["verlag nicht ermittelbar", "verlagsname nicht ermittelbar"]:
                                            lang = ger
                                        elif val_264_b in ["éditeur non identifié"]:
                                            lang = fr
                                        else: lang = False
                                

                        # Linga campo 040 / Language field 040
                        if my_record.get_fields('040') is not None:
                            for f_040 in my_record.get_fields('040'):
                                if (f_040.get_subfields('b') is not None and len(f_040.get_subfields('b')) > 0):    # if 040 $b exists lang_040 is set
                                    lang_040 = f_040.get_subfields('b')[0]
                                else: lang_040 = False

                        if lang and not lang_040: # if cat. lang is True and 040$b doesn't exist, cat. lang is added to 040 $b
                            lang_040 = lang
                            my_langs = my_record.get_fields('040')
                            my_langs[0].add_subfield('b', lang, pos=1)  # cataloguing language is set in 040 $b subfield
                        elif not lang and lang_040: # if cat. lang is False and 040 $b exist, cat. lang is equal to 040 $b
                            lang = lang_040
                        elif not lang and not lang_040: # if cat. lang and 040 $b are both empty 'Italian' is set as default language
                            lang_040 = 'ita'
                            lang = 'ita'
                            my_langs = my_record.get_fields('040')
                            my_langs[0].add_subfield('b', 'ita', pos=1) # Italian is set as language in 040 $b
                        elif lang and lang_040:
                            if lang != lang_040:    # Se lingua di catalogazione e lingua 040 non coincidono / if cataloguing language e lang_040 are not equals  
                                lang_040 = lang     # lang_040 is equal to cataloguing language
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
                                            if lang_check(forced_lang, lang, my_note.get_subfields('a')[0]) == True:
                                                if (my_note.get_subfields('a')[0].startswith('"') and my_note.get_subfields('a')[0].endswith('"')):
                                                    toclean_text = my_note.get_subfields('a')[0]
                                                    clean_text = toclean_text[1:-1]
                                                    my_note.delete_subfield('a')
                                                    my_note.add_subfield('a', clean_text)
                                            elif lang_check(forced_lang, lang, my_note.get_subfields('a')[0]) == False:   # if text language is not equal to cataloguing language
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
                                            if lang_check(forced_lang, lang, my_note.get_subfields('t')[0]) == True:
                                                toclean_textt = my_note.get_subfields('t')[0]
                                                clean_textt = toclean_textt[1:-1]
                                                my_note.delete_subfield('t')
                                                my_note.add_subfield('t', clean_textt)
                                            elif lang_check(forced_lang, lang, my_note.get_subfields('t')[0]) == False:
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
                                            if lang_check(forced_lang, lang, my_note.get_subfields('c')[0]) == True:
                                                toclean_textc = my_note.get_subfields('c')[0]
                                                clean_textc = toclean_textc[1:-1]
                                                my_note.delete_subfield('c')
                                                my_note.add_subfield('c', clean_textc)
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
    
    return 'Done'
