#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:         esmouvy
# Purpose:      Import opendata from eSmouvy to EAP
#
# Author:       Radim Jager
# Copyright:    (c) SYSNET s.r.o. 2020
# License:      CC BY-SA 4.0
# -------------------------------------------------------------------------------

import getopt
import re
import sys

import elasticsearch_dsl
import requests
from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Document, Keyword, Text, Date, Integer, Float
from elasticsearch_dsl.exceptions import ElasticsearchDslException
from requests import RequestException

from settings import ES_HOST

URL_JSON = "https://www.mzp.cz/www/smlouvy-web.nsf/exportAllAsJSON.xsp?id=cv"
URL_CSV = "https://www.mzp.cz/www/smlouvy-web.nsf/exportAllAsCSV.xsp?id=cv"
INDEX_MZP_SMLOUVA = "muzo-mzp-smlouva"


def import_esmlouvy(url=URL_JSON, host=ES_HOST, index=INDEX_MZP_SMLOUVA):
    try:
        index += '-' + elasticsearch_dsl.date.today().isoformat().replace('-', '.')
        r = requests.get(url)
        json = r.json()
        count = json["total"]
        # success = json["success"]
        data = json["data"]
        n = 0
        if data is not None:
            client = Elasticsearch(hosts=host)
            idx_client = client.indices
            if idx_client.exists(index):
                idx_client.delete(index)
                print('Index odstraněn', index)
            dot = 0
            for sml in data:
                sml_es = Smlouva()
                sml_es.load_data(sml)
                # doc_id = sml_es.id
                # sml_es.meta.id = doc_id
                sml_es.save(using=client, index=index)
                dot += 1
                n += 1
                if dot <= 100:
                    print(".", end="")
                else:
                    print(".")
                    dot = 0
            if client is not None:
                client.transport.close()
                del client
                print("*")
        print("Hotovo", 'pocet', count, 'nahrano', n, 'index', index)
        return True
    except RequestException as err:
        print("CHYBA: {0}".format(err))
        return False


class Smlouva(Document):
    contractid = Keyword()
    contractor = Keyword()
    contractoraddresscity = Keyword()
    contractoraddressstreet = Keyword()
    contractoraddresszip = Keyword()
    contractorcompany = Keyword
    contractorid = Keyword()
    contracttitle = Text(fields={'raw': Keyword()})
    contracttype = Keyword()
    dateconclusion = Date()
    datevalidity = Date()
    date_updated = Date()
    form = Keyword()
    ico = Keyword()
    id = Keyword()
    keyword = Keyword()
    originator = Keyword()
    originatorico = Keyword()
    radaevidcislo = Keyword()
    rok = Integer()
    title = Text(fields={'raw': Keyword()})
    total = Keyword()
    valuewithvat = Float()

    class Index:
        name = INDEX_MZP_SMLOUVA

    def save(self, **kwargs):
        try:
            self.date_updated = elasticsearch_dsl.datetime.now()
            return super(Smlouva, self).save(**kwargs)
        except ElasticsearchDslException as err:
            print("CHYBA ES: {0}".format(err))
            return None

    def load_data(self, data):
        self.rok = -1
        dc_iso = consolidate_date(data['DateConclusion'])
        if dc_iso is not None:
            self.dateconclusion = datetime.fromisoformat(dc_iso)
        dv_iso = consolidate_date(data['DateValidity'])
        if dv_iso is not None:
            self.datevalidity = datetime.fromisoformat(dv_iso)
        self.contractid = data['ContractID']
        self.title = data['Title']
        self.contractorid = data['ContractorID']
        self.contractorcompany = data['ContractorName']
        t: str = str(data['ValueWithVAT'])
        t = t.replace(' ', '')
        t = t.replace('Kč', '')
        t = t.replace(',', '.')
        if not isfloat(t):
            t1 = re.findall(r'\d+', t)
            if t1:
                t = t1[0]
            else:
                t = '-1'
        self.valuewithvat = t
        if self.dateconclusion is not None:
            self.rok = int(dc_iso.split('-')[0])
        self.contracttitle = self.title
        self.contractor = self.contractorcompany
        self.keyword = ["MZP", "MŽP", "smlouva", "OpenData", "MUZO", "JASU", "EKIS"]
        self.form = "smlouva"
        self.ico = self.contractorid
        self.total = str(self.valuewithvat)
        self.originator = "Ministerstvo životního prostředí"
        self.originatorico = "00164801"
        self.id = self.contractid + "_" + dc_iso


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def consolidate_date(value: str):
    if value is None:
        return None
    date_string_iso = None
    value_array = value.split(' ')
    date_string = value_array[0]
    d = date_string.split('.')
    if d:
        if len(d) == 3:
            if len(d[2]) < 4:  # je rok mensi nez 2000?
                date_string_iso = '19' + d[2] + '-' + d[1] + '-' + d[0]
            else:
                date_string_iso = d[2] + '-' + d[1] + '-' + d[0]
    return date_string_iso


def index_date_suffix(index):
    index += '-' + elasticsearch_dsl.date.today().isoformat().replace('-', '.')
    return index


def main(argv):
    url_json = URL_JSON
    es_host = ES_HOST
    index = INDEX_MZP_SMLOUVA
    help_string = 'Usage: esmlouvy.py ' \
                  '--url-json=<esmlouvy json source> --es-host=<elasticsearch hostname:port> --index=<EAP index>'
    help_string += '\nUse esmlouvy.py -h for help'

    try:
        opts, args = getopt.getopt(argv, 'hi:o:', ['url-json=', 'es-host=', 'index='])

    except getopt.GetoptError:
        print(help_string)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(help_string)
            sys.exit()
        elif opt in ("-u", "--url-json"):
            url_json = arg
        elif opt in ("-e", "--es-host"):
            es_host = arg
        elif opt in ("-i", "--index"):
            index = arg

    print('url_json:', url_json, '|', 'es_host:', es_host, '|', 'index:', index)

    if not import_esmlouvy(url=url_json, host=es_host, index=index):
        print(help_string)


if __name__ == "__main__":
    # execute only if run as a script
    main(sys.argv[1:])
