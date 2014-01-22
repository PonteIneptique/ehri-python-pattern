#!/usr/bin/env python
# -*- coding: utf-8 -*-

from classes.Authorities import Authorities

import sys
from pprint import pprint
#For sorting 
import operator

try: 
	import igraph
except:
	print "Error on importing IGraph"

auth = Authorities()
if auth.importer(nodesName = "t-auth-nodes-threshold.csv", edgesName = "t-auth-edges-threshold.csv"):
	"""
	data = {}

	for item in auth.index["items"]:
		for authority in auth.index["items"][item]:
			if authority not in data:
				data[authority] = 0
			data[authority] += 1

	sorted_data = sorted(data.iteritems(), key=operator.itemgetter(1))
	pprint(sorted_data)
	print "Import done"
	"""
	print len(auth.index["items"])
	print len(auth.index["authorities"])
	print len(auth.index["authorities"]) * len(auth.index["items"])

	
	"""
	#Now we want a matrix of that
	print "Matrix ->"
	auth.matrix()
	print "Cluster ->"
	auth.clustering()
	"""
	#auth.export()