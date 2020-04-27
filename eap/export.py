#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:         export
# Purpose:      Export MUZO opendata from Elasticsearch
#
# Author:       Radim Jager
# Copyright:    (c) SYSNET s.r.o. 2020
# License:      CC BY-SA 4.0
# -------------------------------------------------------------------------------

import codecs
import csv
import getopt
import numbers
import os
import sys

from dateutil.parser import parse
from elasticsearch import Elasticsearch, TransportError, ElasticsearchException
from elasticsearch_dsl import Search

from settings import DATA_SOURCE_DICTIONARY, CSV_FILE_SUFFIX, DATASOURCE_INDEX, BUFFER_SIZE, DATASOURCE_FIELDNAMES, \
    DATASOURCE_SORTITEM, DATASOURCE_DOCTYPE_FAKTURA, DATASOURCE_DOCTYPE_OBJEDNAVKA, DATASOURCE_DOCTYPE_SMLOUVA, \
    CSV_OUTPUT_DIRECTORY, ES_HOST, DATASOURCE_FILENAME


def consolidate_date(date_str):
    out = ''
    try:
        if (date_str is not None) and (date_str != ''):
            d = parse(date_str)
            if d.year > 2200:
                d = d.replace(year=2199)
            out = d.astimezone().date().isoformat()

    except OSError as err:
        print('consolidate_date', 'ERROR', date_str, type(err), err)
        out = 'DATE ERROR: ' + date_str
    return out


def remove_newlines(input_string):
    if input_string is None:
        return ''
    out = input_string.replace("\r", " ")
    out = out.replace("\n", " ")
    return out


def format_float(input_number):
    if input_number is None:
        return ""
    elif not isinstance(input_number, numbers.Number):
        return ""
    return "%.2f" % input_number


def add_utf8_bom(filename):
    f = codecs.open(filename, 'r', 'utf-8')
    content = f.read()
    f.close()
    f2 = codecs.open(filename, 'w', 'utf-8')
    f2.write(u'\ufeff')
    f2.write(content)
    f2.close()


def export_data_source(company, doctype, year=None, path=None):
    # print("export_data_source", "START")
    if company is None:
        print("export_data_source", "ERROR", "company is None")
        return False
    company = company.lower()
    if company not in DATA_SOURCE_DICTIONARY:
        print("export_data_source", "ERROR", "illegal company", company)
        return False
    if doctype is None:
        print("export_data_source", "ERROR", "doctype is None")
        return False
    setting = DATA_SOURCE_DICTIONARY[company]
    doctype = doctype.lower()
    if doctype not in setting:
        print("export_data_source", "ERROR", "illegal doctype", doctype)
        return False
    print("export_data_source", "create exporter")
    exporter = Exporter(company=company, doctype=doctype, year=year, path=path)
    print("export_data_source", "export data")
    exporter.export_data()
    print("export_data_source", "delete exporter")
    del exporter
    return True


def get_latest_index(index_pattern, client=None):
    close_client = False
    if client is None:
        client = Elasticsearch()
        close_client = True
    print('GET LATEST INDEX', index_pattern, client.info)
    # indices = sorted(client.indices.get_alias(index_pattern).keys(), reverse=True)
    indices = client.indices.get_alias(index_pattern).keys()
    if indices is None:
        print('GET LATEST INDEX', index_pattern, 'ERROR', 'indices is None')
        if close_client:
            if client is not None:
                client.transport.close()
                del client
        return None
    if bool(indices):
        print('GET LATEST INDEX', index_pattern, 'ERROR', 'indices is empty')
        if client is not None:
            client.transport.close()
            del client
        return None
    print('GET LATEST INDEX', index_pattern, indices[0])
    index = indices[0]
    if client is not None:
        client.transport.close()
        del client
    return index


class Exporter:
    def __init__(self, company, doctype, year=None, path=None):
        self.company = company.lower()
        self.doctype = doctype.lower()
        self.year = year
        self.filename = DATA_SOURCE_DICTIONARY[self.company][self.doctype][DATASOURCE_FILENAME]
        # self.filename = self.company + '-' + self.doctype
        if self.year is not None:
            self.filename += '_' + str(self.year)
        self.filename += CSV_FILE_SUFFIX
        if path is None:
            if CSV_OUTPUT_DIRECTORY is not None:
                if CSV_OUTPUT_DIRECTORY != '':
                    self.filename = os.path.join(CSV_OUTPUT_DIRECTORY, self.filename)
        else:
            self.filename = os.path.join(path, self.filename)
        self.client = Elasticsearch(ES_HOST)
        self.file = open(self.filename, 'w', encoding='utf-8', newline='')
        self.writer = csv.DictWriter(
            self.file, fieldnames=DATA_SOURCE_DICTIONARY[self.company][self.doctype][DATASOURCE_FIELDNAMES]
        )
        print("Exporter", "file", self.file.name)
        self.hits = None
        self.total = 0
        self.buffer_size = BUFFER_SIZE
        self.from_item = 1
        self.done = False
        self.writer.writeheader()
        self.index_pattern = DATA_SOURCE_DICTIONARY[self.company][self.doctype][DATASOURCE_INDEX]
        print("Exporter", "index_pattern", self.index_pattern)
        self.index = self.get_latest_index(self.index_pattern)
        if self.index is not None:
            print("Exporter", "index", self.index)
            self.sort_item = DATA_SOURCE_DICTIONARY[self.company][self.doctype][DATASOURCE_SORTITEM]
            print("Exporter", "sort_item", self.sort_item)
            self.search = Search(using=self.client, index=self.index) \
                .sort({self.sort_item: {"order": "asc"}})
            if self.year is not None:
                self.search = Search(using=self.client, index=self.index) \
                    .query("match", rok=self.year) \
                    .sort({self.sort_item: {"order": "asc"}})
        else:
            print('Exporter', 'ERROR', self.index_pattern, 'Index neexistuje')

    def get_latest_index(self, index_pattern):
        # print('Exporter.get_latest_index', index_pattern, str(self.client.info()))
        out = None
        try:
            indices = self.client.indices.get_alias(index_pattern).keys()
            if indices is None:
                print('Exporter.get_latest_index', index_pattern, 'ERROR', 'indices is None')
                self.index = None
            elif not bool(indices):
                print('Exporter.get_latest_index', index_pattern, 'ERROR', 'indices is empty')
                self.index = None
            else:
                indices_list = list(indices)
                indices_list.sort(reverse=True)
                # print('Exporter.get_latest_index', index_pattern, indices_list[0])
                self.index = indices_list[0]
                out = self.index

        except (TransportError, ElasticsearchException) as err:
            print('Exporter.get_latest_index', 'ERROR', type(err), err)
            self.index = None
            out = None

        return out

    def close(self, bom=True):
        if self.client is not None:
            self.client.transport.close()
            del self.client
        self.close_csv_file(bom=bom)
        print('Exporter.close', 'Object Exporter closed')

    def close_csv_file(self, bom=True):
        if self.file is not None:
            self.file.flush()
            self.file.close()
        if bom:
            add_utf8_bom(self.filename)

    def __del__(self):
        print('Exporter.delete', 'Delete Exporter')
        self.close()

    def export_data(self):
        if self.index is None:
            return
        error_occured = False
        while not self.done:
            print('Exporter.export_data', 'company=', self.company, 'doctype=', self.doctype, 'year=', self.year,
                  'index=', self.index)
            if self.load_data_from_eap():
                self.add_hits()
                print('Exporter.export_data', self.company, self.doctype, 'exportováno', self.total)
            else:
                error_occured = True
                print('Exporter.export_data', self.company, self.doctype, 'CHYBA EXPORTU')
                break
        if not error_occured:
            print('Exporter.export_data', self.company, self.doctype, 'export dokončen. Celkem: ', self.total)
        else:
            print('Exporter.export_data', self.company, self.doctype, 'export dokončen s chybou. Celkem: ', 0)

    def load_data_from_eap(self):
        out = False
        if self.index is None:
            return out
        try:
            if self.done:
                print('Exporter.load_data_from_eap', 'DONE')
            else:
                # print('Exporter.load_data_from_eap', 'SCAN EAP START ...')
                self.hits = self.search.scan()
                self.done = True
                out = True
                # print('Exporter.__load_data_from_eap', '... SCAN EAP FINISHED')

        except (TransportError, ElasticsearchException) as err:
            print('Exporter.load_data_from_eap', 'ERROR', type(err), err)
            out = False

        return out

    def add_hits(self):
        if self.index is None:
            return
        if self.hits is not None:
            count = 0
            for hit in self.hits:
                if self.doctype == DATASOURCE_DOCTYPE_FAKTURA:
                    self.writer.writerow(
                        {
                            'cislo_smlouvy': hit.cislosmlouvy,
                            'cislo_objednavky': hit.cisloobjednavky,
                            'dodavatel': remove_newlines(hit.dodavatel),
                            'ico': hit.ico,
                            'cislo_faktury': hit.cislofaktury,
                            'datum_vystaveni': consolidate_date(hit.datumvystaveni),
                            'datum_prijeti': consolidate_date(hit.datumprijeti),
                            'datum_splatnosti': consolidate_date(hit.datumsplatnosti),
                            'datum_uhrady': consolidate_date(hit.datumuhrady),
                            'celkova_castka': format_float(hit.celkovacastka),
                            'castka_polozky': format_float(hit.castkapolozky),
                            'mena': 'CZK',
                            'ucel_platby': remove_newlines(hit.ucelplatby),
                            'polozka_rozpoctu': hit.rpolozka,
                            'nazev_plozky_rozpoctu': remove_newlines(hit.nazevpolozkyrozpoctu),
                            'kapitola': '315',
                            'nazev_kapitoly': 'Ministerstvo životního prostředí'
                        }
                    )
                elif self.doctype == DATASOURCE_DOCTYPE_OBJEDNAVKA:
                    self.writer.writerow(
                        {
                            'cislo_objednavky': hit.radaevidcislo,
                            'popis': remove_newlines(hit.title),
                            'dodavatel': remove_newlines(hit.contractorname),
                            'ico': hit.contractorid,
                            'datum_objednani': consolidate_date(hit.dateconclusion),
                            'datum_dodani': consolidate_date(hit.datevalidity),
                            'celkova_castka': format_float(hit.valuewithvat),
                            'mena': 'CZK'
                        }
                    )
                elif self.doctype == DATASOURCE_DOCTYPE_SMLOUVA:
                    self.writer.writerow(
                        {
                            'cislo_smlouvy': hit.contractid,
                            'predmet': remove_newlines(hit.contracttitle),
                            'dodavatel': remove_newlines(hit.contractorcompany),
                            'ico': hit.contractorid,
                            'datum_uzavreni': consolidate_date(hit.dateconclusion),
                            'datum_trvani': consolidate_date(hit.datevalidity),
                            'celkova_castka': format_float(hit.valuewithvat),
                            'mena': 'CZK'
                        }
                    )
                count += 1
                print(".", end='')
            self.total = count
            print(" ")


def main(argv):
    company = None
    doctype = None
    year = None
    output_path = None
    help_string = 'Usage: export.py --company=<company> --doc-type=<doctype> --year=<year> --output-path=<path>'
    help_string += '\nUse export.py -h for help'

    try:
        opts, args = getopt.getopt(argv, 'hi:o:', ['company=', 'doc-type=', 'year=', 'output-path='])

    except getopt.GetoptError:
        print(help_string)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(help_string)
            sys.exit()
        elif opt in ("-c", "--company"):
            company = arg
        elif opt in ("-d", "--doc-type"):
            doctype = arg
        elif opt in ("-y", "--year"):
            year = arg
        elif opt in ("-p", "--output-path"):
            output_path = arg

    print('company:', company, '|', 'doctype:', doctype, '|', 'year:', year, '|', 'path:', output_path)
    if not export_data_source(company=company, doctype=doctype, year=year, path=output_path):
        print(help_string)


if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv[1:])
