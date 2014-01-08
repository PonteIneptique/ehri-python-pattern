#!/usr/bin/env python
# -*- coding: utf-8 -*-

from py2neo import neo4j
class EHRI(object):
	def __init__(self):
		"""Set up class environment"""
		self.field = "scopeAndContent"
		self.lang = "eng"
		self.normal = True

	def normalize(self, s):
		"""Normalize a string
		
		Keyword arguments:
		s	---	string
		
		"""
		if type(s) == unicode: 
			return s.encode('utf8', 'ignore')
		else:
			return str(s)

	def get(self, field = False, lang = False, normal = True):
		"""Returns an item list with descriptions from neo4j DB
		
		Keyword arguments:
		field --- Field to search in and returns
		lang --- Lang to search with and returns
		"""
		if field:
			self.field = field
		if lang:
			self.lang = lang
		if not normal:
			self.normal = normal

		query = "START doc = node:entities(\"__ISA__:documentaryUnit\") MATCH (description)-[describes]->(doc) WHERE HAS (description." + self.field + ") AND description.languageCode = \""+self.lang+"\" RETURN doc.__ID__, description.__ID__, description." + self.field
		#Querying the database
		graph_db = neo4j.GraphDatabaseService()
		query = neo4j.CypherQuery(graph_db, query)

		#Setting up vars
		item = []
		key = ("idDoc", "idDesc", self.field);
		
		#Using the stream of results
		for record in query.stream():
			#Reseting loop's var
			i = {}
			z = 0
			#Getting each column val
			for k in record:
				if self.normal:
					i[key[z]] = self.normalize(k)
				else:
					i[key[z]] = k

				z += 1
			#Inserting item in list of formated results
			item.append(i)
		
		self.descriptions = item
		#Return list of dictionary
		return item

	def debug(self, limit = 10):
		i = 0
		items = []
		for item in self.descriptions:
			items.append(item)
			i += 1
			if i == limit:
				break

		return items

