#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pattern.vector import Document, Model, HIERARCHICAL
import types
import pattern
class ClusterLSI(object):
	def __init__(self):
		"""Setting up ClusterLSI environment
		"""
		
		
		self.field = "scopeAndContent"
		self.limit = False
		self.identifier = "idDoc"
		
		self.model = False
		self.cluster = False
		
		self.depth = 0
		
		self.outputNodes = "./clus-nodes.csv"
		self.outputEdges = "./clus-edges.csv"
	
	
	def normalize(self, s):
		"""Normalize a string
		
		Keyword arguments:
		s	---	string
		
		"""
		if type(s) == unicode: 
			return s.encode('utf8', 'ignore')
		else:
			return str(s)

	def modeling(self, descriptions, field = False, limit = False):
		"""Model returns a pattern.vector.Model object which is a list of pattern.vector.Document using Ehri.Get() descriptions
		Keyword arguments:
		descriptions ---	EHRI.get() description object
		field 	---		Field to look into, override defaut self.field
		limit	---		Debug option. Limit the model to $limit items
		"""
		if field:
			self.field = field
		if limit:
			self.limit = limit
		D = []
		
		#Creating Pattern Document element from data we got from Neo4J
		#
		
		#For debug reasons, we could set a limit
		if self.limit:
			i = 0
		for description in descriptions:
			D.append(Document(description[self.field], name=description[self.identifier]))
			#And stop the iteration when i reaches the limit
			if self.limit:
				i += 1
				if i == self.limit:
					break
		#Then, creating a model from our array
		self.model = Model(D)
		
		return self.model 
		
	def clusterize(self, model = False):
		"""Returns a cluster of given model
		
		Keyword arguments:
		model	---	If set, override instance model
		
		"""
		if model:
			self.model = model
		self.cluster = self.model.cluster(method=HIERARCHICAL, k=2)
		return self.cluster

	def flatten(self, array, typeOf = "str"):
		"""Returns a 1 dimension list with given type of item inside given array
		
		Keyword arguments:
		array	---	A list of items
		typeOf	---	Type of item the function should return
		
		"""
		#Flatten an array
		if typeOf == "str":
			return [element for element in array if isinstance(element, basestring)]
		elif typeOf == "list":
			return [element for element in array if isinstance(element, list)]

	def csv(self, array, parents = False, fake = 0):
		"""Return a tuple of csv string with given items and number of fake items
		
		Keyword arguments:
		array	---	A list of items
		parents	---	A list of parents
		fake	---	An index for fake parents 
		
		"""
		string = "" 
		#Making list of elements, avoid calling it once more
		currents = self.flatten(array, "str")
		children = self.flatten(array, "list")
		
		if len(currents) == 0:
			fake += 1
		Ffake = fake
		#If we have parents, we have parents connections
		if parents:
			for element in currents:
				for parent in parents:
					string += self.normalize(element) + ";" + parent + "\n"
		
		#Taking care of children
		for child in children:
			if len(currents) > 0:
				Sstring, Ffake = self.csv(child, currents, Ffake)
			else:
				Sstring, Ffake = self.csv(child, ["fake-"+str(fake)], Ffake)
			string += Sstring
				
			
		return string, Ffake
		

	def clusterToArray(self, Graph):
		"""Convert a cluster object to an array list with n-depth where depth is same as cluster.depth
		
		Keyword arguments:
		
		Graph	---	Cluster or list
		"""
		array = []
		
		Docs = [element for element in Graph if isinstance(element, pattern.vector.Document)]
		Clusts = [element for element in Graph if isinstance(element, list)]
		
		for node in Docs:
			array.append(node.name)
		for node in Clusts:
			array.append(self.clusterToArray(node))
		return array
	
	def save(self, descriptions, csv, fakes = 0, nodesName = False, edgesName = False ):
		"""Output cluster into csv files
		
		Keyword arguments:
		descriptions	---	EHRI.get() description item
		fakes	---	Number of fakes parents
		nodesName	---	Filename for Nodes's CSV file
		edgesName	---	Filename for Edges's CSV file
		
		"""
		if nodesName:
			self.outputNodes = nodesName
		if edgesName:
			self.outputEdges = edgesName
		
		
		f = open(self.outputNodes, "wt")
		f.write("id;label;type\n")
		for description in descriptions:
			f.write(self.normalize(description[self.identifier] + ";" + description[self.identifier] + ";1\n"))
		i=0
		while i <= fakes:
			f.write("fake-" + str(i) + ";" + "fake" + str(i) + ";0\n")
			i+= 1
		f.close()

		f = open(self.outputEdges, "wt")
		f.write("source;target\n");
		f.write(csv)
		f.close()
