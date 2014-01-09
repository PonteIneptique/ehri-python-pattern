#!/usr/bin/env python
# -*- coding: utf-8 -*-

from classes.EHRI import EHRI
from classes.Vector import Vector
import sys

#Querying EHRI	
ehri = EHRI()
ehri.get()
descriptions = ehri.debug(limit = 10)

###DEBUG###
from pprint import pprint
lsi = Vector()

lsi.importer()
print lsi.pretty_print(lsi.matrix)

lsi = Vector()
lsi.method = "Pattern-Filter"
lsi.getVectorKeywordIndex(descriptions)
lsi.vectorize(descriptions)
lsi.matrix()
lsi.transform()
print lsi.pretty_print(lsi.matrix)