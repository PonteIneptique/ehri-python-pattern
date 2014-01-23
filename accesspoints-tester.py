#!/usr/bin/env python
# -*- coding: utf-8 -*-

from classes.EHRI import EHRI
from classes.Authorities import Authorities

import sys
from pprint import pprint

#Querying EHRI

ehri = EHRI()
ehri.get(match = " MATCH (auth)<-[:relatesTo]-(description)-[:describes]->(doc)  ", fields = [("description.name", "title"), ("auth.name", "accessPoint")])

#We create the index following these new authorities
auth = Authorities()
for item in ehri.descriptions:

	if item["idDoc"] not in auth.index["items"]:
		auth.index["items"][item["idDoc"]] = []

	a = item["accessPoint"].split("-")

	auth.index["items"][item["idDoc"]] += a
	auth.index["authorities"] += a

auth.index["authorities"] = list(set(auth.index["authorities"]))


#Saving everything
auth.save(nodesName = "ehri-accesspoints-nodes-all.csv", edgesName = "ehri-accesspoints-edges-all.csv")
print "SAVING Normal DONE"

auth.countAuthorities(purge=True)

auth.stats()

auth.thresholder(compute=128)

auth.stats()

auth.cluster()

auth.save(nodesName = "ehri-accesspoints-nodes-cluster.csv", edgesName = "ehri-accesspoints-cluster.csv", mode="cluster")

auth.iGraph(mode = "cluster", debug = True, output="ehri-accesspoints.graphml")