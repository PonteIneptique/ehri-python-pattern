# example from figure 14.9, page 517, Manning and Schutze

from nltk import cluster
import numpy

from nltk.cluster import euclidean_distance

vectors = [numpy.array(f) for f in [[2, 1], [1, 3], [4, 7], [6, 7]]]
means = [[4, 3], [5, 5]]

clusterer = cluster.KMeansClusterer(2, euclidean_distance)
clusters = clusterer.cluster(vectors, True, trace=True)

print 'Clustered:', vectors
print 'As:', clusters
print 'Means:', clusterer.means()
print

for doc in clusters:
	print doc