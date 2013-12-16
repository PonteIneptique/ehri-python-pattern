#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pprint import pprint
from py2neo import neo4j

def getItem():
	#Querying the database
	graph_db = neo4j.GraphDatabaseService()
	query = neo4j.CypherQuery(graph_db, "START doc = node:entities(\"__ISA__:documentaryUnit\") MATCH (description)-[describes]->(doc) WHERE HAS (description.extentAndMedium) RETURN doc.__ID__, description.__ID__, description.extentAndMedium ")

	#Setting up vars
	item = []
	key = ("docId", "descId", "material");
	
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

def getVoc(dic):
	from pattern.en import tag, singularize
	results = {}
	#Looping on items
	for item in dic:
		for word, pos in tag(item["material"]):
			if pos in ["NN", "NNS", "NNP"]:
				w = singularize(word)
				w = w.lower()
				if w not in results:
					results[w] = 0
				results[w] += 1
	return results

def exportCsv(voc):
	import csv
	with open('stats.csv', 'wb') as f:
		writer = csv.writer(f)
		for key in voc:
			obj = [key, str(voc[key])]
			print obj
			writer.writerow(obj)
			
dic = getItem();
voc = getVoc(dic)
exportCsv(voc)

