#!/usr/bin/env python
# -*- coding: utf-8 -*-

from classes.Authorities import Authorities

import sys
from pprint import pprint
#For sorting 
import operator

auth = Authorities()

if auth.importer( nodesName = "t-auth-nodes-cluster.csv", edgesName = "t-auth-edges-cluster.csv", mode = "cluster"):
	auth.iGraph(mode = "cluster", debug = True)
