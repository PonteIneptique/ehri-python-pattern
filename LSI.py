#!/usr/bin/env python
# -*- coding: utf-8 -*-

from classes.EHRI import EHRI
from classes.Vector import Vector
import sys

#Querying EHRI	
ehri = EHRI()
ehri.get(field = "extentAndMedium")
descriptions = ehri.descriptions
#descriptions = ehri.debug(limit = 10)

###DEBUG###
from pprint import pprint

"""
lsi = Vector()
lsi.importer()
print lsi.pretty_print(lsi.matrix)
"""

lsi = Vector()
lsi.field = "extentAndMedium"
lsi.method = "Pattern-Filter"
lsi.getVectorKeywordIndex(descriptions)
lsi.vectorize(descriptions)
lsi.matrix()
lsi.transform()
lsi.exporter(output = "extentAndMedium.py")