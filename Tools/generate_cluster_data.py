'''
Author: Emma Montross

For a single year, cluster on two or more attributes
using KMeans, DBSCAN, or Spectral clustering.
Output a dictionary of country codes associated with the
index of the cluster to which that country belongs.
'''
import sys
import sqlite3
import numpy as np
from sklearn.cluster import KMeans, DBSCAN, SpectralClustering

sys.path.append('../Util')
from database_reader import DatabaseReader
import matrix_cleaning

class Cluster(object):
	def __init__(self, year, attributes, k=5, normalizeMethod=0):
		self.k = k # For k-means, the number of clusters (not used in DBSCAN)
		self.year = year # Indicated year for the attributes we are clustering on
		self.attributes = attributes # List of attributes to cluster on
		self.normalizeMethod = normalizeMethod # Method used to normalize the data before clustering
			# 0: ZScore, 1: MinMax, 2: Average
		self.Clusters = None # Instance of indiciated clustering method, used to fit (cluster) data
		self.clusterIndex = None # Index of the cluster that data point belongs to
		self.centers = [] # List of centers of kmeans clusters

		self.values = None # Matrix of values to cluster on (rows are countries, columns are attributes)
		self.countries = None # Dictionary that maps cluster indexes to country codes
		self.col = None # Column dictionary (??)

		self.organizedInfo = {} # In format { Year: {country:value, country:value, etc}, Year: ... }
			# This is the dictionary needed for visuals

		self.getData()

	def getData(self):
		db = DatabaseReader()
		self.values, self.countries, self.col = db.fetchAttributesData(self.attributes,self.year)

		# Replacing NaN values
		matrix_cleaning.transformColumns(self.values,matrix_cleaning.smoothByReplacement(0))

		# Normalizing the values
		if (self.normalizeMethod == 0):
			matrix_cleaning.transformColumns(self.values,matrix_cleaning.normalizeByZScore)
		elif(self.normalizeMethod == 1):
			matrix_cleaning.transformColumns(self.values,matrix_cleaning.normalizeByMinMax)
		elif(self.normalizeMethod == 2):
			matrix_cleaning.transformColumns(self.values,matrix_cleaning.normalizeByAverage)


	def kmeans(self):
		# K-Means Clustering
		self.Clusters = KMeans(n_clusters=self.k,init='k-means++')
		self.clusterIndex = self.Clusters.fit_predict(self.values)
		self.centers = self.Clusters.cluster_centers_
		self.output()

	def dbscan(self):
		# DBSCAN Clustering
		self.Clusters = DBSCAN(eps=0.3)
		self.clusterIndex = self.Clusters.fit_predict(self.values)
		#self.centers = self.DBSCANClusters.core_sample_indices_
		self.output()

	def spectral(self):
		# Spectral Clustering
		self.Clusters = SpectralClustering(n_clusters=self.k, affinity='nearest_neighbors')
		self.clusterIndex = self.Clusters.fit_predict(self.values)
		self.output()

	def output(self):
		# Put the results into a dictionary for JSON output
		countryValues = {}
		for i in range(0,len(self.clusterIndex)):
			countryValues.update({self.countries[i]:self.clusterIndex[i]})
		self.organizedInfo.update({self.year:countryValues})


# if __name__ == "__main__":
#   	cluster = Cluster(2014, ["AG.LND.TOTL.K2","NY.GDP.MKTP.CD"], 10) #NY.GDP.MKTP.KD.ZG - GDP growth rate, NY.GDP.MKTP.CD - GDP
#   		#SG.VAW.ARGU.ZS - % women who think their husband is justified in beating her when she argues with him
#   		#AG.LND.TOTL.K2  - land area in sq. km
#   	# print cluster.values
#   	# cluster.kmeans()
#   	# cluster.dbscan()
#   	cluster.spectral()
#   	# print cluster.countries
#   	# print cluster.values
#   	# print cluster.clusters
#   	# print cluster.centers
#   	print cluster.organizedInfo