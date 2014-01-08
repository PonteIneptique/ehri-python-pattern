#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

try:
	from pattern.en import tag
except:
	print "Pattern Library required for classes/LSI.py"
	print "http://www.clips.ua.ac.be/pages/pattern"
	sys.exit()


try:
        from numpy import dot
        from numpy.linalg import norm
except:
        print "Error: Requires numpy from http://www.scipy.org/. Have you installed scipy?"
        sys.exit() 

class Vector(object):
	def __init__(self):
		self.descriptions = {}
		self.filter = "NN"
		self.content = []
		self.field = "scopeAndContent"
		self.identifier = "idDoc"
		self.vocabulary = {"string" : False, "list" : []}


		self.stopwords = []
		self.dir = os.path.dirname(__file__)

		self.externalData = open(os.path.join(self.dir, "./classes/stopwords.txt")) 
		self.stopwords = self.externalData.read()
		self.externalData.close()

		self.stopwords = self.stopwords.split(", ")

	def normalize(self, s):
		"""Normalize a string
		
		Keyword arguments:
		s	---	string
		
		"""
		if type(s) == unicode: 
			return s.encode('utf8', 'ignore')
		else:
			return str(s)

	def clean(self, string, filter = False):
		"""Returns a cleaned sentence where only word with Treebank tags starting with self.filter is returned

		Keyword arguments:
		string	---	string to tokenize and clean
		filter	---	filter to override self.filter
		"""
		if filter:
			self.filter = filter
		return [self.normalize(word) for word,pos in tag(string) if pos.startswith(self.filter) and len(self.normalize(word)) > 1]

	def tokenise(self, string, field = False):
		"""Returns a list of list of words from a list of list of items

		Keyword arguments:
		string	---	String to tokenise
		field	---	Field in which we look for material
		"""
		if field:
			self.field = field

		self.content = self.clean(string)

		return self.content

	def removeStopWords(self, array):
		return [word for word in array if word not in self.stopwords]

	def removeDuplicates(self, array):
		return list(set(array))

	def getVectorKeywordIndex(self, descriptions, field = False):
		""" Create the keyword associated to the position of the elements within the document vectorsments:

		descriptions	---	List of description. Taken from EHRI.get() or a string containing them all
		field	---	Field in which we look for material
		"""
		if field:
			self.field = field

		self.original = descriptions

		#Mapped documents into a single word string
		self.vocabulary["string"] = " ".join([self.normalize(description[self.field]) for description in descriptions])

		self.vocabulary["list"] = self.tokenise(self.vocabulary["string"])

		#Remove common words which have no search value
		self.vocabulary["list"] = self.removeStopWords(self.vocabulary["list"])
		self.vocabulary["unique"] = self.removeDuplicates(self.vocabulary["list"])

		self.vectorIndex={}
		offset=0
		#Associate a position with the keywords which maps to the dimension on the vector used to represent this word
		for word in self.vocabulary["unique"]:
			self.vectorIndex[word]=offset
			offset+=1
		return self.vectorIndex  #(keyword:position)

	def makeVector(self, string):
		""" @pre: unique(vectorIndex) """

		#Initialise vector with 0's
		self.vector = [0] * len(self.vectorIndex)

		wordList = self.tokenise(string)
		wordList = self.removeStopWords(wordList)

		for word in wordList:
			self.vector[self.vectorIndex[word]] += 1; #Use simple Term Count Model

		return self.vector

	def cosine(self, vector1, vector2):
		""" related documents j and q are in the concept space by comparing the vectors :
				cosine  = ( V1 * V2 ) / ||V1|| x ||V2|| """
		return float(dot(vector1,vector2) / (norm(vector1) * norm(vector2)))

	def search(self,searchList):
		""" search for documents that match based on a list of terms """
		queryVector = self.makeVector(searchList)

		ratings = [(self.cosine(queryVector, documentVector), documentId) for documentVector, documentId in self.documentVectors]
		ratings.sort(reverse=True)
		return ratings

	def vectorize(self, descriptions, field = False, identifier = False):
		if field:
			self.field = field
		if identifier:
			self.identifier = identifier

		self.documentVectors = []
		for description in descriptions:
			self.documentVectors.append((self.makeVector(self.normalize(description[self.field])), self.normalize(description[self.identifier])))

		return self.documentVectors