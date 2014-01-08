#!/usr/bin/env python
# -*- coding: utf-8 -*-

from classes.EHRI import EHRI
from classes.Authorities import Authorities
from classes.ClusterLSI import ClusterLSI
from classes.Material import Material


#Querying EHRI	
ehri = EHRI()
ehri.get()
descriptions = ehri.debug()

###DEBUG###
from pprint import pprint
lsi = LSI()

lsi.getVectorKeywordIndex(descriptions)
lsi.vectorize(descriptions)

print lsi.search("Holocaust")
print(lsi.documentVectors)