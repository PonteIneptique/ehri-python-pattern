#!/usr/bin/env python
# -*- coding: utf-8 -*-

from py2neo import neo4j
class EHRI(object):
	def __init__(self):
		"""Set up class environment"""
		self.field = "scopeAndContent"
		self.lang = "eng"
	#Dependency
	#
	#	- neo4j
	def get(self, field = False, lang = False):
		"""Returns an item list with descriptions from neo4j DB
		
		Keyword arguments:
		field --- Field to search in and returns
		lang --- Lang to search with and returns
		"""
		if field:
			self.field = field
		if lang:
			self.lang = lang
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
				i[key[z]] = k
				z += 1
			#Inserting item in list of formated results
			item.append(i)
		
		#Return list of dictionary
		return item