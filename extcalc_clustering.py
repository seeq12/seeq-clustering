from extcalc import KeywiseExternalCalculationScript
import numpy as np
import pandas as pd
import time
import pickle
import hdbscan
import os


from seeq import spy


model_dir = 'cluster_models'

def save_model_to_disk(clusterer, itemId,):
	"""need docstring"""

	#check to make sure the dir exists
	if model_dir not in set(os.listdir('./')):
		os.mkdir('./{}'.format(model_dir))

	with open('./{}/{}.pkl'.format(model_dir, itemId), 'wb') as f:
		pickle.dump(clusterer, f)

	return


def contour_check(check_points, random_walk):
    """check_points have dim (n, ndim)
    random_walk has 3 elements. 
    [0] is boundary unit vectors (can be in any space), 
    [1] is boundary ls (relative to origin)
    [2] is origin
    
    returns: indexer of [True,..... etc.] of which points are in or not
    
    operates by finding which direction we are closest too and then comparing our l to that l
    """
    boundary_unit_vectors = random_walk[0]
    boundary_ls = random_walk[1]
    origin = random_walk[2]
    points = check_points - origin
    #holds the projections of the points onto each of the unitvectors of the boundary
    projections = np.dot(points, boundary_unit_vectors) #npoints x nunitvecs

    maxprojs = np.argmax(projections, axis = 1) #argmax (of the unitvec) projection for each point
    #this tells us which len to compare against

    compare_distance_to = np.array([boundary_ls[i] for i in maxprojs])
    distances = np.sqrt(points[:,0]**2 + points[:,1]**2)
    whichinside = distances<=compare_distance_to
    
    return whichinside

def get_cluster_defn_str(url, itemId, key):
	spy.login(url=url, username=key, password='U6ky629GvQRpa7nzgmdve75ZhdSFEz', ignore_ssl_errors=True)
	model_byte_str = spy.search({'ID':itemId}).clusterDefn.values[0]
	return model_byte_str

def decode_defn_string(defn):
	clusterer = pickle.loads(bytes.fromhex(defn))
	return clusterer

def get_cluster_defn(url, itemId, key):
	try:
		with open('./{}/{}.pkl'.format(model_dir, itemId), 'rb') as f:
			clusterer = pickle.load(f)
	except FileNotFoundError:
		string = get_cluster_defn_str(url, itemId, key)
		clusterer = decode_defn_string(string)

		#now save to disk once retrieved. 
		save_model_to_disk(clusterer, itemId,)
	return clusterer

def cluster_check(check_points, model):
	#X = model.standard_scaler.transform(check_points)
	#Sp_ = model.pca.transform(X) 
	if str(type(model)) == "<class 'hdbscan.hdbscan_.HDBSCAN'>":
		cln_membership, confidence = hdbscan.approximate_predict(model, check_points) #returns tuple of lists ([clustern], [confidence])
		if int(cln_membership[0]) == int(model.cln):
			return True
		else:
			return False
	else:
		return contour_check(check_points, model[0])[0] #returned list should only have one item


class extcalc_clustering(KeywiseExternalCalculationScript):

	def initialize(self):
		self.model = False
		pass

	def validate(self, validation_object):
		pass

	def check_in_out(self, samples):
				
		if np.isnan(samples[:]).any():
			return False

		ndims = len(samples[:])

		check_point = np.array([float(x) for x in samples[:]])
		check_point = check_point.reshape(1, ndims)
		
		return cluster_check(check_point, self.model)

	def compute(self, key, samples_for_key):
		if type(self.model) == type(False) and self.model == False:
			url, key, itemId, clustern = samples_for_key[0].split('&&')
			self.model = get_cluster_defn(url=url, key=key, itemId=itemId)
			if type(self.model) == dict:
				pass
			else:
				self.model.cln = clustern
		else:
			pass
		checker = self.check_in_out(samples_for_key[1:])
		if checker:
			return key, samples_for_key[1]
		else:
			return key, np.nan

	def compute_output_mode(self):
		return 'NUMERIC'

	def cleanup(self):
		pass

	def get_test_signals_data_types(self):
		from extcalc import TwoNumericSignals
		return TwoNumericSignals().signal_data_types

	def get_test_data(self):
		from extcalc import TwoNumericSignals
		return TwoNumericSignals().signals_data
