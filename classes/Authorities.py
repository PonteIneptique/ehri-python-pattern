#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import hashlib
try:
	from pattern.en import tag
except:
	print "Pattern Library required for classes/LSI.py"
	print "http://www.clips.ua.ac.be/pages/pattern"
	sys.exit()

class Authorities(object):
	
	def __init__(self):
		"""Set up class environment"""
		self.index = {"items" : {}, "authorities" : []}
		self.indexed = {}
		self.field = "scopeAndContent"
		self.debug = False
		self.ids = {}
		self.threshold = (1, 11)
		
		self.outputNodes = "auth-nodes.csv"
		self.outputEdges = "auth-edges.csv"

	def manual(self):
		"""Filter items disabled manually

		"""

		filter = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

		self.index["authorities"] = [auth for auth in self.index["authorities"] if auth not in filter]

		for item in self.index["items"]:
			self.index["items"][item] = [auth for auth in self.index["items"][item] if auth in self.index["authorities"]]

	
	def cluster(self):
		"""Create links between nodes from their authorities

		"""
		self.index["cluster"] = {}

		for item in self.index["items"]:
			self.index["cluster"][item] = [{"weight" : float(len(set(self.index["items"][item]).intersection( set(self.index["items"][id]))))/float(len(self.index["items"][item])) , "name" : id, "authority" : set(self.index["items"][item]).intersection( set(self.index["items"][id])) } for id in self.index["items"] if id != item and len(set(self.index["items"][item]).intersection( set(self.index["items"][id]))) >= 1]

		return self.index

	def get(self, description, index = False, field = False, debug = False, fields = False):
		"""Get automaticly authorities (All proper nouns) from descriptions, links them to said descriptions and return an index of links and authorities
		
		Keyword arguments:
		description	---	Either a description from an EHRI.get() descriptions list or an EHRI.get() descriptions list
		index	---	Index of items, if already exists
		field ---	Field to query, default is scopeAndContent
		debug ---	Debug mode : print details during execution
		fields	---	If more than one field
		
		"""
		if index:
			self.index = index
		if field:
			self.field = field
		if debug:
			self.debug = debug
		#If Description is a list of description, then we run a loop on it
		if isinstance(description, list):
			for element in description:
				self.get(element, fields = fields)
		else:
			if self.debug:
				print "Handling Item Id " + description[self.identifier]
			
			try:
				if fields:
					tokens = tag(". ".join([description[item] for item in description if item in fields]))
				else:
					tokens = tag(description[self.field])
			except:
				print "Tokenization failed for " + self.field
				sys.exit()

			i = 0
			entities = []
			while i < len(tokens):
				#Setting up temp variables
				name, pos = tokens[i]
				z = 1
				if pos == "NNP":
					entity_name = name
					#if tokens[i+z]:
					if i + z + 1 < len(tokens):
						while tokens[i+z][1] == "NNP" or (z + i + 1 < len(tokens) and tokens[i+z][0].lower() == "of" and tokens[i+z+1][1] == "NNP") :
							entity_name += " " + tokens[i+z][0]
							z += 1
							#Breaking it if not anymore in  index range
							if z + i == len(tokens):
								break
					self.index["authorities"].append(entity_name)
					if description["idDoc"] not in self.index["items"]:
						self.index["items"][description["idDoc"]] = []
					self.index["items"][description["idDoc"]].append(entity_name)
				i += z
		
		return self.index
	
	def thresholder(self, threshold = False):
		"""Clean authorities if their amount of connected item is below the threshold

		Keyword arguments:
		threshold	---	overwrite original threshold of 1 (TUPLE)
		"""

		if threshold:
			self.threshold = threshold


		index = self.index.copy()
		authorities = {}

		for auth in index["authorities"]:
			authorities[auth] = 0

		for item in index["items"]:
			for id in index["items"][item]:
				authorities[id] += 1

		passingTest = [auth for auth in authorities if authorities[auth] > self.threshold[0] and authorities[auth] < self.threshold[1]]

		for item in index["items"]:
			index["items"][item] = [auth for auth in index["items"][item] if auth in passingTest]

		self.index["items"] = index["items"]
		self.index["authorities"] = passingTest

		return self.index


	def clean(self, descriptions = False, fields = False):
		"""Returns a cleaned index of neo4j items and authorities
		
		Keyword arguments:
		descriptions	---	descriptions object from EHRI.get()

		"""
		if descriptions:
			self.index = self.get(descriptions, )
		self.index["authorities"] = list(set(self.index["authorities"]))
		return self.index
	
	def normalize(self, s):
		"""Normalize a string
		
		Keyword arguments:
		s	---	string
		
		"""
		if type(s) == unicode: 
			return s.encode('utf8', 'ignore')
		else:
			return str(s)
	
	def saveNodes(self):	
		i = 1
		self.ids = {}
		
		for au in self.index["authorities"]:
			self.ids[au] = i
			i += 1

		for item in self.index["items"]:
			self.indexed[item] = [self.ids[ref] for ref in self.index["items"][item]]
		
		authList = sum([self.index["items"][iz] for iz in self.index["items"]], [])
		
		#Writing Nodes
		f = open(self.outputNodes, "wt")
		f.write("id;label;item;centrality\n")
		for item in self.index["items"]:
			f.write(self.normalize(item + ";" + item + ";1;" + str(len(self.index["items"][item])) + "\n"))
		for item in self.ids:
			f.write(self.normalize(str(self.ids[item]) + ";" + item + ";0;" + str(len([auth for auth in authList if auth == item])) + "\n"))
		f.close()
		
		#Writing Edges
		f = open(self.outputEdges, "wt")
		f.write("source;target\n")
		for item in self.index["items"]:
			for ref in self.indexed[item]:
				f.write(self.normalize(item + ";" + str(ref) + "\n"))
		f.close()

	def saveCluster(self):
		#Writing nodes
		f = open(self.outputNodes, "wt")
		f.write("id;label;weight\n")

		for item in self.index["cluster"]:
			f.write(self.normalize(item + ";" + item + ";" + str(len(self.index["cluster"][item])) + "\n"))

		f.close()

		f = open(self.outputEdges, "wt")
		f.write("source;target;weight;type;label;hash\n")

		for item in self.index["cluster"]:
			for link in self.index["cluster"][item]:
				try:
					f.write(self.normalize(item) + ";" + self.normalize(link["name"]) + ";" + str(link["weight"]) + ";Undirected;" + self.normalize(",".join(list(link["authority"]))) + ";" + self.normalize(hashlib.md5(",".join(list(link["authority"]))).hexdigest()) + "\n")
				except:
					print "Not possible for " + link["name"] + " -> " + item
					#f.write(self.normalize(item) + ";" + self.normalize(link["name"]) + ";" + str(link["weight"]) + ";Undirected;" + self.normalize(hashlib.md5(",".join(list(link["authority"]))).hexdigest()) + ";" + self.normalize(hashlib.md5(",".join(list(link["authority"]))).hexdigest()) + "\n")
				
		f.close()



	def save(self, nodesName = False, edgesName = False, mode = "authorities"):
		"""Save index of authorities and items and their links in two csv files
		
		Keyword arguments:
		nodesName	---	Filename for Nodes's CSV file
		edgesName	---	Filename for Edges's CSV file
		mode	---	If set to authorities, returns authorities in as nodes. Is set to cluster, returns links between item as they share authorities
		
		"""
		if nodesName:
			self.outputNodes = nodesName
		if edgesName:
			self.outputEdges = edgesName

		if mode == "authorities":
			self.saveNodes()
		elif mode == "cluster":
			self.saveCluster()

	def importer(self, nodesName = False, edgesName = False, mode = "authorities"):

		"""Import csv and recreate a graph
		
		Keyword arguments:
		nodesName	---	Filename for Nodes's CSV file
		edgesName	---	Filename for Edges's CSV file
		mode	---	If set to authorities, returns authorities in as nodes. Is set to cluster, returns links between item as they share authorities
		"""


		if nodesName:
			self.outputNodes = nodesName
		if edgesName:
			self.outputEdges = edgesName
		
		if mode == "authorities":
			ids = {}
			with open(self.outputNodes, "rt") as nodes:
				i = 0
				for line in nodes:
					if i != 0:
						data = line.split(";")
						#Index : id, label, item (0 = neo4j, 1 = authority), centrality
						if data[2] == int(1):
							self.index["items"][data[1]] = []
						else:
							self.index["authorities"].append(data[1])
							ids[data[0]] = data[1]
					i += 1

			self.index["authorities"] = set(self.index["authorities"])

			with open(self.outputEdges, "rt") as edges:
				i = 0
				for line in edges:
					if i != 0:
						#source;target
						data = line.split(";")
						if data[0] not in self.index["items"]:
							self.index["items"][data[0]] = []
						self.index["items"][data[0]].append(ids[data[1].replace("\n", "")])
					i += 1
		return True