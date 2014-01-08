#!/usr/bin/env python
# -*- coding: utf-8 -*-

from classes.EHRI import EHRI
from classes.Vector import Vector
import sys

#Querying EHRI	
ehri = EHRI()
ehri.get()
descriptions = ehri.debug(limit = 30)

###DEBUG###
from pprint import pprint
lsi = Vector()
lsi.getVectorKeywordIndex(descriptions)
lsi.vectorize(descriptions)
lsi.matrix()
print lsi.pretty_print(lsi.matrix)
print lsi.pretty_print(lsi.transform())
#print lsi.pretty_print(lsi.matrix)