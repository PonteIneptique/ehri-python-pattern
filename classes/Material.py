#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pattern.en import tag, singularize
import csv

class Material(object):
	def __init__(self):
		"""Set up class environment"""
		self.field = "extentAndMedium"
		self.identifier = "idDoc"
		
		self.index = {}
		self.count = {}
		
		self.lexicon = {
			"audio" : ["Audio",	"Music", "Recording"],		
			"book" : ["Book",	"Thesis"],
			"file" : ["File", "Box", "Collection", "Document", "Folder"],
			"graphic" : ["Drawing", "Frame", "Image", "Photo", "Photograph"],
			"map" : ["Map"],
			"microfilm" : ["Microfilm"],
			"journal" :	["Newspaper", "Periodical"],
			"cards" : ["Poster", "Card"]		
		}
		
		self.available = []
		for l in self.lexicon:
			self.available += [i for i in self.lexicon[l]]
		
		for item in self.lexicon:
			self.count[item] = 0
			
	
	def get(self, descriptions, mode = "link", index = False, field = False, count = False):
		""" Returns a list of names or connect a list of item to lexicon items
		
		descriptions	---	EHRI.get() descriptions list
		mode	---	Either link or search
		index	---	Overide self.index
		count	---	Overide self.count
		
		"""
		
		if index:
			self.index = index
		if field:
			self.field = field
		if count:
			self.count = count
		
		results = {}
		
			
		#Looping on items
		for description in descriptions:
			for word, pos in tag(description[self.field]):
				
				if pos in ["NN", "NNS", "NNP"]:
					w = singularize(word)
					w = w.lower()
					if w not in results:
						results[w] = 0
					results[w] += 1
					
					# If we are looking for stats about items
					if mode == "link":
						if w.title() in self.available:
							for item in self.lexicon:
								print item
								if w.title() in self.lexicon[item]:
									self.count[item] += 1
									if description[self.identifier] not in self.index:
										self.index[description[self.identifier]] = []
									self.index[description[self.identifier]].append(item)
		if mode == "link":
			return self.index
		elif mode == "search":
			return results
			
	
	def csv(self, filename = False):
		if filename:
			self.filename = filenam
		with open(self.filename, 'wb') as f:
			writer = csv.writer(f)
			for key in self.index:
				obj = [key] + list(set(self.index[key]))
				writer.writerow(obj)
