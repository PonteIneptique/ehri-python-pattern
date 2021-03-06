#!/usr/bin/env python
# -*- coding: utf-8 -*-

from classes.EHRI import EHRI
from classes.Authorities import Authorities
from classes.ClusterLSI import ClusterLSI
from classes.Material import Material
from classes.Vector import Vector

#Querying EHRI	
ehri = EHRI()
ehri.get()
descriptions = ehri.debug()

#Getting semi-Automatic material indexing
materialDescription = ehri.get(field = "extentAndMedium")
material = Material()
materialIndexing = material.get(materialDescription, mode= "link")

#Getting automaticly generated authorities :
indexer = Authorities()
indexer.clean( descriptions = descriptions)
indexer.save(nodesName = "lalala.csv", edgesName = "lololo.csv")

#Clustering
cluster = ClusterLSI()
cluster.modeling(descriptions, limit= 100)	#Limiting the modeling to 100 items
cluster.clusterize()

cluster.array = cluster.clusterToArray(cluster.cluster)
cluster.csv , cluster.fakes = cluster.csv(cluster.array)
cluster.save(descriptions, cluster.csv, cluster.fakes)

#Vector
lsi = Vector()
lsi.getVectorKeywordIndex(descriptions)
lsi.vectorize(descriptions)
print lsi.search("Holocaust")