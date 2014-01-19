#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

try:
	from py2neo import neo4j
except:
	print "To run this code, please install py2neo library"
	sys.exit()
try:
	from pattern.en import tag
except:
	print "Pattern Library required for classes/LSI.py"
	print "http://www.clips.ua.ac.be/pages/pattern"
	sys.exit()

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

	def get(self, field = False, lang = False, normal = True, limit = False, fields = False, notOptional = False):
		"""Returns an item list with descriptions from neo4j DB
		
		Keyword arguments:
		field --- Field to search in and returns
		lang --- Lang to search with and returns
		limit	---	Number of fields to return
		fields ---	List of tuple (field name in neo4j, return name)
		notOptional	---	Fields which MUST be in the description. Only of interest if fields not false
		"""
		if field:
			self.field = field
		if lang:
			self.lang = lang
		if not normal:
			self.normal = normal

		if fields:
			queryFields = ", ".join(["description." + f[0] for f in fields])

			if notOptional:
				where = "MATCH (description)-[describes]->(doc) WHERE " + " AND ". join(["HAS (description. " + f[0] + ")" for f in fields if f[0] in notOptional]) + " AND description.languageCode = \""+self.lang+"\""
				ret = ",".join([",".join(["description. " + f[0] for f in fields if f[0] in notOptional]), ",".join(["description. " + f[0] + "?" for f in fields if f[0] not in notOptional])])
			else:
				where = "MATCH (description)-[describes]->(doc) WHERE " + " AND ". join(["HAS (description. " + f[0] + ")" for f in fields]) + " AND description.languageCode = \""+self.lang+"\""
				ret = ",".join(["description. " + f[0] for f in fields])
			#where = "MATCH (description)-[describes]->(doc) WHERE HAS (description." + self.field + ") AND description.languageCode = \""+self.lang+"\""

			if limit:
				query = "START doc = node:entities(\"__ISA__:documentaryUnit\") " + where + " RETURN doc.__ID__, description.__ID__, " + ret + " LIMIT " + str(limit)
			else:
				query = "START doc = node:entities(\"__ISA__:documentaryUnit\") " + where + " RETURN doc.__ID__, description.__ID__, " + ret
		else:
			if limit:
				query = "START doc = node:entities(\"__ISA__:documentaryUnit\") " + where + " RETURN doc.__ID__, description.__ID__, description." + self.field + " LIMIT " + str(limit)
			else:
				query = "START doc = node:entities(\"__ISA__:documentaryUnit\") " + where + " RETURN doc.__ID__, description.__ID__, description." + self.field

		#Querying the database
		graph_db = neo4j.GraphDatabaseService()
		query = neo4j.CypherQuery(graph_db, query)

		#Setting up vars
		item = []
		key = ("idDoc", "idDesc", self.field);
		if fields :
			key = ["idDoc", "idDesc"] + [f[1] for f in fields]
		
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

