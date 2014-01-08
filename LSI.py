#!/usr/bin/env python
# -*- coding: utf-8 -*-

from classes.EHRI import EHRI
from classes.Vector import Vector


#Querying EHRI	
ehri = EHRI()
ehri.get()
descriptions = ehri.debug()

###DEBUG###
from pprint import pprint
lsi = Vector()
lsi.getVectorKeywordIndex(descriptions)
lsi.vectorize(descriptions)
print lsi.search("Holocaust")