#!/usr/bin/env python
# -*- coding: utf-8 -*-

from classes.EHRI import EHRI
from classes.Authorities import Authorities

import sys
from pprint import pprint

#Querying EHRI

ehri = EHRI()
ehri.get(match = " MATCH (auth)<-[:relatesTo]-(description)-[:describes]->(doc)  ", fields = [("description.name", "title"), ("auth.name", "accessPoint")])
print ehri.descriptions[0]