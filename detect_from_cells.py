# -*- coding: utf-8 -*-
"""
Created on Wed Feb 11 09:47:26 2015

@author: leo_cdo_intern

###############################################################################
Ce script analyse les premières lignes d'un CSV pour essayer de déterminer le
contenu possible des champs


ACTUELLEMENT EN DEVELOPPEMENT : Indactions comment tester tout en bas
"""

import pandas as pd
import chardet
from os.path import join

from detect_autres import _sexe, _code_csp_insee, _csp_insee, _url, _courriel, _tel_fr, _siren
from detect_geographiques import _code_postal, _code_commune_insee, _code_departement, _code_iso_pays, _pays, _region, _departement, _commune, _adresse
from detect_temporel import _jour_de_la_semaine, _annee, _date


#############################################################################
############### ROUTINE DE TEST CI DESSOUS ##################################

# TODO : Mettre un pourcentage de valeurs justes (au lieu de nécessiter que toutes les valeurs soient justes)

def detect_delimiter(file):
    '''Trouve le délimitateur du csv'''
    # TODO: add a robust detection:
    # si on a un point virgule comme texte et \t comme séparateur, on renvoit
    # pour l'instant un point virgule
    with open(file, 'r') as myCsvfile:
        header = myCsvfile.readline()
        possible_separators = [";", ",", "|", "\t"]
        for sep in possible_separators:
            if header.find(sep) != -1:
                return sep
    # default delimiter (MS Office export)
    return ";"


def detect_headers(file, sep):
    ''' teste les 5 première ligne pour voir si on a une
        ligne qui ferait un bon header '''
    with open(file, 'r') as myCsvfile:
        for i in range(5):
            header = myCsvfile.readline()
            chaine = header.split(sep)
            if (chaine[-1] not in ['', '\n'] and 
                 all(mot not in ['', '\n'] for mot in chaine[1:-1])):
                return i
    return 0


def test_col(serie, test_func):
    '''Teste progressivement une colonne avec la foncition test_func, renvoie True si toutes
    les valeurs de la série renvoient True avec test_func. False sinon.
    '''
    serie = serie[serie.notnull()]
    ser_len = len(serie)
    if ser_len == 0:
        return False
    for range_ in [range(0,min(1, ser_len)), range(min(1, ser_len),min(5, ser_len)), range(min(5, ser_len),min(50, ser_len))]: # Pour ne pas faire d'opérations inutiles, on commence par 1, puis 5 puis 50 valeurs
        if all(serie.iloc[range_].apply(test_func)):
            pass
        else:
            return False
    return True


def routine(file):
    '''Renvoie un table avec en colonnes les colonnes du csv et en ligne, les champs testes'''

    if not any([extension in file for extension in ['.csv', '.tsv']]):
        return False

    sep = detect_delimiter(file)
    headers_row = detect_headers(file, sep)
    
    with open(file, 'r') as myCsvfile:
        print chardet.detect(myCsvfile.read())

    table = pd.read_csv(file, sep = sep, 
                        skiprows = headers_row,
                        nrows = 50, dtype = 'unicode')
    fonctions_test = dict()
    # Geographique
    fonctions_test['code_postal'] = _code_postal
    fonctions_test['code_commune_insee'] = _code_commune_insee
    fonctions_test['code_departement'] = _code_departement
    fonctions_test['code_iso_pays'] = _code_iso_pays

    fonctions_test['pays'] = _pays
    fonctions_test['region'] = _region
    fonctions_test['departement'] = _departement
    fonctions_test['commune'] = _commune

    fonctions_test['adresse'] = _adresse

    # Date
    fonctions_test['jour_de_la_semaine'] = _jour_de_la_semaine
    fonctions_test['annee'] = _annee
    fonctions_test['date'] = _date

    # Autres
    fonctions_test['csp_code_insee'] = _code_csp_insee
    fonctions_test['csp_insee'] = _csp_insee
    fonctions_test['sexe'] = _sexe
    fonctions_test['url'] = _url
    fonctions_test['courriel'] = _courriel
    fonctions_test['tel_fr'] = _tel_fr
    fonctions_test['siren'] = _siren


    return_table = pd.DataFrame(columns = table.columns)

    for key, test_func in fonctions_test.iteritems():
        try:
            return_table.loc[key] = table.apply(lambda serie: test_col(serie, test_func))
        except Exception, e:
            import pdb
            print str(e)
            pdb.set_trace()


    for x in return_table.columns:

        valeurs_possibles = list(return_table[return_table[x]].index)
        if valeurs_possibles != []:
            print '  >>  La colonne', x, 'est peut-être :',
            print valeurs_possibles
    return return_table


if __name__ == '__main__':

    from os import listdir
    from os.path import isfile, join

    ### CONSIGNES : Mettre toutes les data a tester dans le dossier indiqué par path
    # et lancer le script. Il doit afficherc pour chaque fichier dans ce dossier (ne doit contenir que des csv)
    # les colonnes pour lesquelles un match a été trouvé
    path = 'data'
    all_files = [join(path, f) for f in listdir(path) if isfile(join(path,f)) ]

    for file in all_files:
        print '*****************************************'
        print file
        routine(file)
        print '\n'



