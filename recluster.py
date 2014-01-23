#!/usr/bin/env python
# -*- coding: utf-8 -*-

from classes.Authorities import Authorities

import sys
from pprint import pprint

auth = Authorities()

if auth.importer( nodesName = "t-auth-nodes-all.csv", edgesName = "t-auth-edges-all.csv", mode = "authorities"):

	auth.countAuthorities(purge=True)

	auth.stats()

	auth.thresholder(compute=128)

	auth.stats()

	auth.cluster()

	auth.save(nodesName = "t-auth-nodes-cluster.csv", edgesName = "t-auth-edges-cluster.csv", mode="cluster")