#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from math import *

try:
	from pattern.en import tag
except:
	print "Pattern Library required for classes/LSI.py"
	print "http://www.clips.ua.ac.be/pages/pattern"
	sys.exit()


try:
	from numpy import dot, array
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

		self.externalData = open(os.path.join(self.dir, "./stopwords.txt")) 
		self.stopwords = self.externalData.read()
		self.externalData.close()

		self.stopwords = self.stopwords.split(", ")
		self.stopwords = self.stopwords + [word.title() for word in self.stopwords]

		self.method = "Simple"

	def pretty_print(self, matrix):
		""" Make the matrix look pretty """
		out = ""

		rows,cols = matrix.shape

		out += "["
		for voc in self.vocabulary["list"]:
			out += voc + "\t"

		out += "]\n"

		for row in xrange(0,rows):
			out += "["

			for col in xrange(0,cols):
				out += "%+0.2f"%matrix[row][col]
				out += "\t"

			out += "]\n"

		return out


	def clean(self, string, filter = False):
		"""Returns a cleaned sentence where only word with Treebank tags starting with self.filter is returned

		Keyword arguments:
		string	---	string to tokenize and clean
		filter	---	filter to override self.filter
		"""
		if filter:
			self.filter = filter

		try:
			string = string.replace("’", "'")
			return [word.encode("utf-8", "ignore") for word,pos in tag(string) if pos.startswith(self.filter) and len(word) > 1]
		except:
			print "Error : Can't parse following string :"
			print string
			sys.exit()

	def tokenise(self, string, field = False, method = False):
		"""Returns a list of list of words from a list of list of items

		Keyword arguments:
		string	---	String to tokenise
		field	---	Field in which we look for material
		method	---	Available method are :
			-	Pattern-Filter
			-	Pattern
			-	Simple
		"""
		if field:
			self.field = field
		if method:
			self.method = method


		if self.method == "Pattern-Filter":
			self.content = self.clean(string)
		elif self.method == "Pattern":
			self.content = self.clean(string, "")
		else:
			self.content = [word for word in string.split(" ") if word not in ["\n", "'", "\"", "”", "’", "...", ".", "!", "?", ")", "(", "[", "]"]]
			self.content = [word.replace(" ", "") for word in self.content]


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
		self.vocabulary["string"] = " ".join([description[self.field] for description in descriptions])

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
		""" Returns a vector from a string

		string	---	String to convert to a vector index"""

		#Initialise vector with 0's
		self.vector = [0] * len(self.vectorIndex)

		wordList = self.tokenise(string)
		wordList = self.removeStopWords(wordList)

		for word in wordList:
			if word in self.vectorIndex:
				self.vector[self.vectorIndex[word]] += 1; #Use simple Term Count Model
			else:
				print "Error : Following word is not in vector Index"
				print word

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
			self.documentVectors.append((self.makeVector(description[self.field]), description[self.identifier]))

		return self.documentVectors

	def getTermDocumentOccurences(self, col):
		""" Find how many documents a term occurs in"""

		term_document_occurrences = 0

		rows, cols = self.matrix.shape

		for n in xrange(0,rows):
			if self.matrix[n][col] > 0: #Term appears in document
				term_document_occurrences +=1
		return term_document_occurrences

	def transform(self, matrix = False):
		""" Apply TermFrequency(tf)*inverseDocumentFrequency(idf) for each matrix element.
		This evaluates how important a word is to a document in a corpus

		With a document-term matrix: matrix[x][y]
		tf[x][y] = frequency of term y in document x / frequency of all terms in document x
		idf[x][y] = log( abs(total number of documents in corpus) / abs(number of documents with term y)  )
		Note: This is not the only way to calculate tf*idf
		"""

		documentTotal = len(self.matrix)
		rows,cols = self.matrix.shape

		for row in xrange(0, rows): #For each document

			wordTotal= reduce(lambda x, y: x+y, self.matrix[row] )

			for col in xrange(0,cols): #For each term

				#For consistency ensure all self.matrix values are floats
				self.matrix[row][col] = float(self.matrix[row][col])

				if self.matrix[row][col]!=0:

					termDocumentOccurences = self.getTermDocumentOccurences(col)

					termFrequency = self.matrix[row][col] / float(wordTotal)
					inverseDocumentFrequency = log(abs(documentTotal / float(termDocumentOccurences)))

					self.matrix[row][col] = float(termFrequency*inverseDocumentFrequency)

		return self.matrix


	def matrix(self, documentVectors = False):
		if documentVectors:
			self.documentVectors = documentVectors

		matrix = [vector for vector, documentId in self.documentVectors]

		self.matrix = array(matrix, dtype=float)

		return matrix
