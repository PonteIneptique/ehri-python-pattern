#!/usr/bin/env python
# -*- coding: utf-8 -*-

from classes.EHRI import EHRI
from classes.Authorities import Authorities

import sys
from pprint import pprint

#Querying EHRI	
ehri = EHRI()
ehri.get(fields = [("description.scopeAndContent", "description"), ("description.name", "title"), ("description.biographicalHistory", "bio")], notOptional = ["name"])

print "NEO4J DONE"
#Getting automaticly generated authorities :
indexer = Authorities()
indexer.get( description = ehri.descriptions, fields = ["description", "title", "biographicalHistory"])
indexer.clean()
indexer.manual()

print "AUTHORITIES DONE"

#Saving everything
indexer.save(nodesName = "t-auth-nodes-all.csv", edgesName = "t-auth-edges-all.csv")
print "SAVING Normal DONE"

#With Thresholding
indexer.thresholder()
indexer.save(nodesName = "t-auth-nodes-threshold.csv", edgesName = "t-auth-edges-threshold.csv")
print "SAVING thresholder DONE"

#Saving cluster
indexer.cluster()
indexer.save(nodesName = "t-auth-nodes-cluster.csv", edgesName = "t-auth-edges-cluster.csv", mode="cluster")

#indexer.save(nodesName = "lalala.csv", edgesName = "lololo.csv")
