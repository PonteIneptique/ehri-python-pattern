#!/usr/bin/env python
# -*- coding: utf-8 -*-

from classes.Authorities import Authorities

import sys
from pprint import pprint
#For sorting 
import operator

auth = Authorities()

"""

if auth.importer( nodesName = "ehri-accesspoints-nodes-cluster.csv", edgesName = "ehri-accesspoints-cluster.csv", mode = "cluster"):
	auth.iGraph(mode = "cluster", debug = True, output="ehri-graphml.graphml")

"""

if auth.importer(nodesName = "t-auth-nodes-threshold.csv", edgesName = "t-auth-edges-threshold.csv"):
	auth.countAuthorities()
	auth.stats()
	auth.iGraph(debug = True, output="ehri-authorities-threshold.graphml")