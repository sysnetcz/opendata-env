#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:         upload
# Purpose:      Upload MUZO opendata datasets to CKAN
#
# Author:       Radim Jager
# Copyright:    (c) SYSNET s.r.o. 2020
# License:      CC BY-SA 4.0
# -------------------------------------------------------------------------------
import datetime
import glob
import os

import requests

from settings import DATASOURCE_COMPANIES, FILENAMES_DICTIONARY, DATA_SOURCE_DICTIONARY, DATASOURCE_CKAN, \
    DATASOURCE_CKAN_SCHEME, CKAN_ENDPOINT, CKAN_OPENDATA_LICENSE, CKAN_SCHEMA_FAKTURA, CKAN_FORMAT_SCHEMA, CKAN_API_KEY


def upload_all(data_path='.'):
    file_list = glob.glob(os.path.join(data_path, "*.csv"))
    for file_name in file_list:
        company = parse_company(file_name=file_name)
        doctype = parse_doctype(file_name=file_name)
        year = parse_year(file_name=file_name)
        if (year is None) or (company == '') or (doctype == ''):
            print("upload_all", "CHYBA", "chybný název souboru", file_name)
            pass
        else:
            file_path = os.path.join(data_path, file_name)
            print("upload_all", "OK", company, doctype, year, file_path)
            upload_file(company=company, doctype=doctype, year=year, data_path=file_path)


def parse_company(file_name: str):
    if file_name is None:
        return ''
    elif any(company in file_name for company in DATASOURCE_COMPANIES):
        for company in DATASOURCE_COMPANIES:
            if company in file_name:
                return company
    else:
        return ''


def parse_doctype(file_name: str):
    if file_name is None:
        return ''
    elif any(fname in file_name for fname in list(FILENAMES_DICTIONARY.keys())):
        for fname in list(FILENAMES_DICTIONARY.keys()):
            if fname in file_name:
                return FILENAMES_DICTIONARY[fname]
    else:
        return ''


def parse_file_name(file_name: str):
    if file_name is None:
        return ''
    elif any(fname in file_name for fname in list(FILENAMES_DICTIONARY.keys())):
        for fname in list(FILENAMES_DICTIONARY.keys()):
            if fname in file_name:
                return fname
    else:
        return ''


def parse_year(file_name: str):
    out = datetime.datetime.today().year
    xx = file_name.split('_')[-1]
    if len(xx) != 14:
        return None
    yc = file_name.split('_')[-2]
    if yc.isnumeric():
        out = int(yc)
    return out


def upload_file(company, doctype, year, data_path):
    datasource_ckan = DATA_SOURCE_DICTIONARY[company][doctype][DATASOURCE_CKAN]
    id = datasource_ckan['default']
    if str(year) in datasource_ckan.keys():
        id = datasource_ckan[str(year)]
    scheme = DATA_SOURCE_DICTIONARY[company][doctype][DATASOURCE_CKAN_SCHEME]
    data = {
        "id": id,
        "license_link": CKAN_OPENDATA_LICENSE,
        "describedBy": scheme,
        "describedByType": CKAN_FORMAT_SCHEMA
    }
    headers = {"X-CKAN-API-Key": CKAN_API_KEY}
    files = [('upload', open(data_path, 'r', encoding='utf-8'))]
    # requests.post(CKAN_ENDPOINT, data=data, headers=headers, files=files)
    print(CKAN_ENDPOINT)
    print(data)
    print(headers)
    print(files)
