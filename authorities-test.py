#!/usr/bin/env python
# -*- coding: utf-8 -*-

from classes.EHRI import EHRI
from classes.Authorities import Authorities

#Querying EHRI	
ehri = EHRI()
ehri.get( )
descriptions = ehri.descriptions

#Getting automaticly generated authorities :
indexer = Authorities()
indexer.clean( descriptions = descriptions)
indexer.thresholder(1)
indexer.cluster()
indexer.save(mode="cluster")


#indexer.save(nodesName = "lalala.csv", edgesName = "lololo.csv")