#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pattern.en import tag
class Authorities(object):
	
	def __init__(self):
		"""Set up class environment"""
		self.index = {"items" : {}, "authorities" : []}
		self.indexed = {}
		self.field = "scopeAndContent"
		self.debug = False
		self.ids = {}
		
		self.outputNodes = "./auth-nodes.csv"
		self.outputEdges = "./auth-edges.csv"
	
	def get(self, description, index = False, field = False, debug = False):
		"""Get automaticly authorities (All proper nouns) from descriptions, links them to said descriptions and return an index of links and authorities
		
		Keyword arguments:
		description	---	Either a description from an EHRI.get() descriptions list or an EHRI.get() descriptions list
		index	---	Index of items, if already exists
		field ---	Field to query, default is scopeAndContent
		debug ---	Debug mode : print details during execution
		
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
				self.get(element)
		else:
			if self.debug:
				print "Handling Item Id " + description[self.identifier]
				
			tokens = tag(description[self.field])
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
						while tokens[i+z][1] == "NNP":
							entity_name += " " + tokens[i+z][0]
							z += 1
					self.index["authorities"].append(entity_name)
					if description["idDoc"] not in self.index["items"]:
						self.index["items"][description["idDoc"]] = []
					self.index["items"][description["idDoc"]].append(entity_name)
				i += z
		
		return self.index
	
	def clean(self, descriptions = False):
		"""Returns a cleaned index of neo4j items and authorities
		
		Keyword arguments:
		descriptions	---	descriptions object from EHRI.get()
		
		"""
		if descriptions:
			self.index = self.get(descriptions)
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
	
	def save(self, nodesName = False, edgesName = False):
		"""Save index of authorities and items and their links in two csv files
		
		Keyword arguments:
		nodesName	---	Filename for Nodes's CSV file
		edgesName	---	Filename for Edges's CSV file
		
		"""
		if nodesName:
			self.outputNodes = nodesName
		if edgesName:
			self.outputEdges = edgesName
			
		i = 1
		self.ids = {}
		
		for au in self.index["authorities"]:
			self.ids[au] = i
			i += 1

		for item in self.index["items"]:
			self.indexed[item] = [self.ids[ref] for ref in self.index["items"][item]]
		
		
		#Writing Nodes
		f = open(self.outputNodes, "wt")
		f.write("id;label;item\n")
		for item in self.index["items"]:
			f.write(self.normalize(item + ";" + item + ";1\n"))
		for item in self.ids:
			f.write(self.normalize(str(self.ids[item]) + ";" + item + ";0\n"))
		f.close()
		
		#Writing Edges
		f = open(self.outputEdges, "wt")
		for item in self.index["items"]:
			for ref in self.indexed[item]:
				f.write(self.normalize(item + ";" + str(ref) + "\n"))
		f.close()
