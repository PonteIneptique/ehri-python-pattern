#!/usr/bin/env python
# -*- coding: utf-8 -*-

from classes.Authorities import Authorities

import sys
from pprint import pprint

auth = Authorities()
if auth.importer(nodesName = "t-auth-nodes-all.csv", edgesName = "t-auth-edges-all.csv"):
	pprint(auth.index)