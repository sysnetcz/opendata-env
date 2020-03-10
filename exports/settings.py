import os

from dateutil import utils

BUFFER_SIZE = 100000

FIELD_NAMES_FAKTURA = [
    'cislo_smlouvy', 'cislo_objednavky', 'dodavatel', 'ico', 'cislo_faktury', 'datum_vystaveni', 'datum_prijeti',
    'datum_splatnosti', 'datum_uhrady', 'celkova_castka', 'castka_polozky', 'mena', 'ucel_platby', 'polozka_rozpoctu',
    'nazev_plozky_rozpoctu', 'kapitola', 'nazev_kapitoly'
]

FIELD_NAMES_OBJEDNAVKA = [
    'cislo_objednavky', 'popis', 'dodavatel', 'ico', 'datum_objednani', 'datum_dodani', 'celkova_castka', 'mena'
]

FIELD_NAMES_SMLOUVA = [
    'cislo_smlouvy', 'predmet', 'dodavatel', 'ico', 'datum_uzavreni', 'datum_trvani', 'celkova_castka', 'mena'
]

CSV_FILE_SUFFIX = '_' + utils.datetime.now().strftime('%Y-%m-%d') + '.csv'
CSV_FILE_NAME_TEST = 'test' + CSV_FILE_SUFFIX
CSV_OUTPUT_DIRECTORY = os.getenv('CSV_OUTPUT_DIRECTORY', '')


DATASOURCE_COMPANY_AOPK = 'aopk'
DATASOURCE_COMPANY_CENIA = 'cenia'
DATASOURCE_COMPANY_CGS = 'cgs'
DATASOURCE_COMPANY_CIZP = 'cizp'
DATASOURCE_COMPANY_MZP = 'mzp'
DATASOURCE_COMPANY_SJCR = 'sjcr'

DATASOURCE_DOCTYPE_FAKTURA = 'faktura'
DATASOURCE_DOCTYPE_OBJEDNAVKA = 'objednavka'
DATASOURCE_DOCTYPE_SMLOUVA = 'smlouva'

DATASOURCE_INDEX = 'index'
DATASOURCE_CKAN = 'ckan'
DATASOURCE_FIELDNAMES = 'fieldnames'
DATASOURCE_SORTITEM = 'sort'

SORTITEM_FAKTURA = "idpolozky"
SORTITEM_OBJEDNAVKA = "_id"
SORTITEM_SMLOUVA = "_id"


DATA_SOURCE_DICTIONARY = {
    DATASOURCE_COMPANY_AOPK: {
        DATASOURCE_DOCTYPE_FAKTURA: {
            DATASOURCE_INDEX: 'muzo-aopk-zavazek',
            DATASOURCE_FIELDNAMES: FIELD_NAMES_FAKTURA,
            DATASOURCE_SORTITEM: SORTITEM_FAKTURA,
            DATASOURCE_CKAN: '',
        },
        DATASOURCE_DOCTYPE_OBJEDNAVKA: {
            DATASOURCE_INDEX: 'muzo-aopk-objednavka',
            DATASOURCE_FIELDNAMES: FIELD_NAMES_OBJEDNAVKA,
            DATASOURCE_SORTITEM: SORTITEM_OBJEDNAVKA,
            DATASOURCE_CKAN: '',
        },
        DATASOURCE_DOCTYPE_SMLOUVA: {
            DATASOURCE_INDEX: 'muzo-aopk-smlouva',
            DATASOURCE_FIELDNAMES: FIELD_NAMES_SMLOUVA,
            DATASOURCE_SORTITEM: SORTITEM_SMLOUVA,
            DATASOURCE_CKAN: '',
        },
    },
    DATASOURCE_COMPANY_CENIA: {
        DATASOURCE_DOCTYPE_FAKTURA: {
            DATASOURCE_INDEX: 'muzo-cenia-zavazek',
            DATASOURCE_FIELDNAMES: FIELD_NAMES_FAKTURA,
            DATASOURCE_SORTITEM: SORTITEM_FAKTURA,
            DATASOURCE_CKAN: '',
        },
        DATASOURCE_DOCTYPE_SMLOUVA: {
            DATASOURCE_INDEX: 'muzo-cenia-smlouva',
            DATASOURCE_FIELDNAMES: FIELD_NAMES_SMLOUVA,
            DATASOURCE_SORTITEM: SORTITEM_SMLOUVA,
            DATASOURCE_CKAN: '',
        },
    },
    DATASOURCE_COMPANY_CGS: {
        DATASOURCE_DOCTYPE_FAKTURA: {
            DATASOURCE_INDEX: 'muzo-cgs-zavazek',
            DATASOURCE_FIELDNAMES: FIELD_NAMES_FAKTURA,
            DATASOURCE_SORTITEM: SORTITEM_FAKTURA,
            DATASOURCE_CKAN: '',
        },
        DATASOURCE_DOCTYPE_OBJEDNAVKA: {
            DATASOURCE_INDEX: 'muzo-cgs-objednavka',
            DATASOURCE_FIELDNAMES: FIELD_NAMES_OBJEDNAVKA,
            DATASOURCE_SORTITEM: SORTITEM_OBJEDNAVKA,
            DATASOURCE_CKAN: ''
        },
        DATASOURCE_DOCTYPE_SMLOUVA: {
            DATASOURCE_INDEX: 'muzo-cgs-smlouva',
            DATASOURCE_FIELDNAMES: FIELD_NAMES_SMLOUVA,
            DATASOURCE_SORTITEM: SORTITEM_SMLOUVA,
            DATASOURCE_CKAN: ''
        },
    },
    DATASOURCE_COMPANY_CIZP: {
        DATASOURCE_DOCTYPE_FAKTURA: {
            DATASOURCE_INDEX: 'muzo-cizp-zavazek',
            DATASOURCE_FIELDNAMES: FIELD_NAMES_FAKTURA,
            DATASOURCE_SORTITEM: SORTITEM_FAKTURA,
            DATASOURCE_CKAN: ''
        },
        DATASOURCE_DOCTYPE_OBJEDNAVKA: {
            DATASOURCE_INDEX: 'muzo-cizp-objednavka',
            DATASOURCE_FIELDNAMES: FIELD_NAMES_OBJEDNAVKA,
            DATASOURCE_SORTITEM: SORTITEM_OBJEDNAVKA,
            DATASOURCE_CKAN: ''
        },
        DATASOURCE_DOCTYPE_SMLOUVA: {
            DATASOURCE_INDEX: 'muzo-cizp-smlouva',
            DATASOURCE_FIELDNAMES: FIELD_NAMES_SMLOUVA,
            DATASOURCE_SORTITEM: SORTITEM_SMLOUVA,
            DATASOURCE_CKAN: ''
        },
    },
    DATASOURCE_COMPANY_MZP: {
        DATASOURCE_DOCTYPE_FAKTURA: {
            DATASOURCE_INDEX: 'muzo-mzp-zavazek*',
            DATASOURCE_FIELDNAMES: FIELD_NAMES_FAKTURA,
            DATASOURCE_SORTITEM: SORTITEM_FAKTURA,
            DATASOURCE_CKAN: ''
        },
        DATASOURCE_DOCTYPE_OBJEDNAVKA: {
            DATASOURCE_INDEX: 'muzo-mzp-objednavka',
            DATASOURCE_FIELDNAMES: FIELD_NAMES_OBJEDNAVKA,
            DATASOURCE_SORTITEM: SORTITEM_OBJEDNAVKA,
            DATASOURCE_CKAN: ''
        },
    },
    DATASOURCE_COMPANY_SJCR: {
        DATASOURCE_DOCTYPE_FAKTURA: {
            DATASOURCE_INDEX: 'muzo-sjcr-zavazek',
            DATASOURCE_FIELDNAMES: FIELD_NAMES_FAKTURA,
            DATASOURCE_SORTITEM: SORTITEM_FAKTURA,
            DATASOURCE_CKAN: ''
        },
        DATASOURCE_DOCTYPE_SMLOUVA: {
            DATASOURCE_INDEX: 'muzo-sjcr-smlouva',
            DATASOURCE_FIELDNAMES: FIELD_NAMES_SMLOUVA,
            DATASOURCE_SORTITEM: SORTITEM_SMLOUVA,
            DATASOURCE_CKAN: ''
        },
    }
}
