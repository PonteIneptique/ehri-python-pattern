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

try:
	from numpy import dot, array, short
	from numpy.linalg import norm
except:
	print "Error: Requires numpy from http://www.scipy.org/. Have you installed scipy?"
	sys.exit() 

try:
	from nltk import cluster
	from nltk.cluster import euclidean_distance
except:
	print "Nltk needed for clusterisation"
	sys.exit()

try: 
	import igraph
except:
	print "Error on importing IGraph"

class Authorities(object):
	
	def __init__(self):
		"""Set up class environment"""
		self.index = {"items" : {}, "authorities" : []}
		self.indexed = {}
		self.field = "scopeAndContent"
		self.debug = False
		self.ids = {}
		self.threshold = (1, 1218)
		
		self.outputNodes = "auth-nodes.csv"
		self.outputEdges = "auth-edges.csv"

	def manual(self):
		"""Filter items disabled manually

		"""

		filter = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December", "World War II"],

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
	
	def thresholder(self, threshold = False, compute = False, computeMin= False):
		"""Clean authorities if their amount of connected item is below the threshold

		Keyword arguments:
		threshold	---	overwrite original threshold of 1 (TUPLE)
		compute	---	Compute a high fraction of links
		"""

		if threshold:
			self.threshold = threshold

		try:
			if compute:
				self.countAuthorities(purge=True)
				x = [self.authorities[i] for i in self.authorities if self.authorities[i] != 1]
				xx = sorted(x)
				l = float(len(xx))
				if computeMin:
					self.threshold = (xx[int(l/compute)], xx[int(l/compute*(compute-1))])
				else:
					self.threshold = (2, xx[int(l/compute*(compute-1))])
		except:
			print "error in compute"
			sys.exit()



		passingTest = [auth for auth in self.authorities if self.authorities[auth] >= self.threshold[0] and self.authorities[auth] <= self.threshold[1]]

		for item in self.index["items"]:
			self.index["items"][item] = [auth for auth in self.index["items"][item] if auth in passingTest]

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
			return s.encode('utf8', 'ignore').replace(";", "")
		else:
			return str(s).replace(";", "")
	
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
			f.write(self.normalize(item) + ";" + self.normalize(item) + ";1;" + self.normalize(str(len(self.index["items"][item]))) + "\n")
		for item in self.ids:
			f.write(str(self.ids[item]) + ";" + self.normalize(item) + ";0;" + self.normalize(str(len([auth for auth in authList if auth == item]))) + "\n")
		f.close()
		
		#Writing Edges
		f = open(self.outputEdges, "wt")
		f.write("source;target\n")
		for item in self.index["items"]:
			for ref in self.indexed[item]:
				f.write(self.normalize(item) + ";" + str(ref) + "\n")
		f.close()

	def saveCluster(self):
		#Writing nodes
		f = open(self.outputNodes, "wt")
		f.write("id;label;weight\n")

		for item in self.index["cluster"]:
			f.write(self.normalize(item) + ";" + self.normalize(item) + ";" + str(len(self.index["cluster"][item])) + "\n")

		f.close()

		f = open(self.outputEdges, "wt")
		f.write("source;target;weight;type;label;hash\n")

		for item in self.index["cluster"]:
			for link in self.index["cluster"][item]:
				try:
					f.write(self.normalize(item) + ";" + self.normalize(link["name"]) + ";" + str(link["weight"]) + ";Undirected;" + self.normalize(",".join(list(link["authority"]))) + ";" + self.normalize(hashlib.md5(",".join(list(link["authority"]))).hexdigest()) + "\n")
				except:
					print "Not possible for " + link["name"] + " -> " + item
					f.write(self.normalize(item) + ";" + self.normalize(link["name"]) + ";" + str(link["weight"]) + ";Undirected;" + self.normalize(hashlib.md5(",".join(list(link["authority"]))).hexdigest()) + ";" + self.normalize(hashlib.md5(",".join(list(link["authority"]))).hexdigest()) + "\n")
				
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

		print mode
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
						try:
							#Index : id, label, item (0 = neo4j, 1 = authority), centrality
							if int(data[2]) == 1:
								self.index["items"][data[1]] = []

							else:
								self.index["authorities"].append(data[1])
								ids[data[0]] = data[1]
						except:
							print data
							#Index : id, label, item (0 = neo4j, 1 = authority), centrality
							if int(data[3]) == 1:
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
		
		elif mode == "cluster":
			print "cluster mode"
			#Nodes
			with open(self.outputNodes, "rt") as nodes:
				i = 0
				for line in nodes:
					if i != 0:
						data = line.split(";")
						#Index : id, label, centrality
						self.index["items"][data[1]] = []
					i += 1
			#Edges
			with open(self.outputEdges, "rt") as edges:
				i = 0
				for line in edges:
					if i != 0:
						#source;target
						data = line.replace("\n", "").split(";")
						if data[0] not in self.index["items"]:
							self.index["items"][data[0]] = []
						self.index["items"][data[0]].append((data[1], float(1)/float(data[2])))
					i += 1

		return True

	def matrix(self):
		self.vectors = []
		ids = {}
		empty = []

		#Saving the index of authorities
		i = 0
		for auth in self.index["authorities"]:
			ids[auth] = i
			i += 1
			empty.append(0)

		#Creating vector
		i = 0
		for item in self.index["items"]:
			v = empty
			print len(self.index["items"][item])
			
			for auth in self.index["items"][item]:
				v[ids[auth]] += 1

			print str(i) + " \t : \t " + str(len(v))
			i += 1
			"""
			if i == 5000:##22400:
				break
			"""
			self.vectors.append(array(v))

		return True

	def clustering(self):
		clusterer = cluster.KMeansClusterer(40, euclidean_distance, repeats=10)
		self.cluster = clusterer.cluster(self.vectors, True)

	def export(self):
		for item in self.cluster:
			print item

	def iGraph(self, debug = False, mode = "authorities", output = "ehri.graphml", direct = False):#Let's create the graph
		#We need its number of nodes first
		graphLength = len(set(self.index["items"]))

		if mode == "authorities":
			graphLength += len(self.index["authorities"])

		#Just checking
		if debug == True:
			print "Graph vertices : " + str(graphLength)

		#Create its instance
		g = igraph.Graph(graphLength, directed = direct)

		#Now we needs names of stuff, lets call it labels
		labels = [item for item in self.index["items"]]

		#We do miss labels of authorities, dont we ?
		if mode == "authorities":
			labels += self.index["authorities"]

		#Have we got same number than graphLength ?
		if debug==True:
			print "Labels length " + str(len(labels))

		#Just to be sure :
		if len(labels) != graphLength:
			print "Not the same number of names and labels you fool"
			print "So you shall not pass"
			sys.exit()
		
		#We create another thing : we save index of items and labels in a dictionary, because that's why
		index = {}
		for name in labels:
			index[name] = len(index)
		#Isn't it beautiful ?

		#So now, we can add labels to our graph 
		g.vs["label"] = labels

		#Would be nice to connect it...
		#Hello EDGES
		edges = []
		weight = []
		for i in self.index["items"]:
			for a in self.index["items"][i]:
				if mode == "cluster":
					edges.append((index[i], index[a[0]]))
					weight.append(a[1])
				else:
					edges.append((index[i], index[a]))
			
		g.add_edges(edges)
		if mode == "cluster":
			g.es["weight"] = weight

		#A little sum-up ?
		if debug == True:
			igraph.summary(g)
		
		try:
			if mode != "cluster":
				#Let's try to make some community out of it...
				d = g.community_fastgreedy()
				cl = d.as_clustering()
				#Let's save this clusterization into an attribute
				g.vs["fastgreedy"] = cl.membership
				#Sping glass not possible
		except:
			print "Fast greedy not working. Multi edges graph ?"


		#And do that with other clusterization modules
		d = g.community_walktrap()
		cl = d.as_clustering()
		#Let's save this clusterization into an attribute
		g.vs["walktrap"] = cl.membership

		g.save(output)

	def countAuthorities(self, purge = False):
		"""
			Make a dictionary with the amount of item linked to it
		"""
		self.authorities = {}
		a = {}
		for item in self.index["items"]:
			for aa in self.index["items"][item]:
				if aa not in a:
					a[aa] = 0
				a[aa] += 1

		self.authorities = a
		if purge:
			self.authorities = {}
			for i in a:
				if a[i] != 1:
					self.authorities[i] = a[i]


	def stats(self):
		"""
			Print out stats about items
		"""
		
		x = [self.authorities[i] for i in self.authorities if self.authorities[i] != 1]
		xx = sorted(x)
		l = float(len(xx))
		print "-----------"
		print "Population : " + str(l)
		print "-----------"
		print "Q1 = " + str(xx[int(l/4)])
		print "Q3 = " + str(xx[int(float(l/4)*3)])
		print "-----------"
		print "01/08 = " + str(xx[int(l/8)])
		print "07/08 = " + str(xx[int(float(l/8)*7)])
		print "-----------"
		print "01/16 = " + str(xx[int(l/16)])
		print "15/16 = " + str(xx[int(float(l/16)*15)])
		print "-----------"
		print "01/32 = " + str(xx[int(l/32)])
		print "31/32 = " + str(xx[int(float(l/32)*31)])
		print "-----------"
		print "01/64 = " + str(xx[int(l/64)])
		print "63/64 = " + str(xx[int(float(l/64)*63)])
		print "-----------"
		print "01/128 = " + str(xx[int(l/128)])
		print "127/128 = " + str(xx[int(float(l/128)*127)])
		print "-----------"
		print "01/256 = " + str(xx[int(l/256)])
		print "255/256 = " + str(xx[int(float(l/256)*255)])
		print "-----------"
		print "01/512 = " + str(xx[int(l/512)])
		print "511/512 = " + str(xx[int(float(l/512)*511)])
		print "-----------"