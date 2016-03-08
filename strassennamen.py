#!/usr/local/bin/python
# coding: utf-8

import json
import httplib
import urllib
import csv
import codecs
import re
from urllib import quote_plus

def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
    csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
    for row in csv_reader:
        yield [unicode(cell, 'utf-8') for cell in row]

words_to_replace = ["str.", "weg", "gasse", "markt", "am ", "an ", "an den","im ", "in ", "platz", "allee", "feld", "zum ", "zur ", "der ", "st\.","den ", "dr\. ", "auf", "von ", "vor", "unter ", "unterer ", "kamp", "gäßchen", "tal"];
csvfile = "20150101_straßenverzeichnis_standard.csv"
reader = unicode_csv_reader(open(csvfile))
words_in_streets = {}
for row in reader:
    name = row[1]
    for word in words_to_replace:
        replace = re.compile(re.escape(word), re.IGNORECASE)
        name = replace.sub("", name)
    names = re.compile('[- ]').split(name)
    new_name = names[0]
    if new_name in words_in_streets:
        words_in_streets[new_name] += 1
    else:
        words_in_streets[new_name] = 1

data = []
for key in  sorted(words_in_streets, key=words_in_streets.get, reverse=True):
    print key + ": " + str(words_in_streets[key])
    req_path   = "/names/{c}/{fn}".format(c="de", fn=quote_plus(key.encode('utf-8'), safe=':/'))

    connection = httplib.HTTPConnection("api.namesia.de")
    connection.request("GET", req_path)

    response   = connection.getresponse()
    name_dict  = json.loads(response.read())
    if "gender" in name_dict:
        data.append({"name": key, "number": words_in_streets[key], "gender": name_dict["gender"]})

with open('data.json', 'w') as outfile:
    json.dump(data, outfile)
