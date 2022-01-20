#DO NOT CHANGE THE FOLLOWING LINE OR THIS LINE
wkdir = 'C:/defaultpath'

from extcalc import KeywiseExternalCalculationScript, ValidationObject
from typing import Dict
import textwrap
import numpy as np
import pandas as pd
import time
import pickle
import hdbscan
import os
import sys

from seeq import spy

model_dir = 'cluster_models'

def save_model_to_disk(clusterer, itemId,):
	"""need docstring"""

	#check to make sure the dir exists
	print('entered save_model_to_disk')
	if model_dir not in set(os.listdir(wkdir)):
		os.mkdir('{}/{}'.format(wkdir, model_dir))

	with open('{}/{}/{}.pkl'.format(wkdir, model_dir, itemId), 'wb') as f:
		pickle.dump(clusterer, f)
		print('opened file', '{}/{}/{}.pkl'.format(wkdir, model_dir, itemId))

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
	print("entering get_cluster_defn_str")
	spy.login(url=url, auth_token=key, ignore_ssl_errors=True)
	model_byte_str = spy.search({'ID':itemId}).clusterDefn.values[0]
	return model_byte_str

def decode_defn_string(defn):
	print("entering decode_defn_string")
	clusterer = pickle.loads(bytes.fromhex(defn))
	print("exiting decode_defn_string")
	return clusterer

def get_cluster_defn(url, itemId, key):
	try:
		print('attempting to open model at ', '{}/{}/{}.pkl'.format(wkdir, model_dir, itemId))
		with open('{}/{}/{}.pkl'.format(wkdir, model_dir, itemId), 'rb') as f:
			clusterer = pickle.load(f)
	except FileNotFoundError:
		string = get_cluster_defn_str(url, itemId, key)
		clusterer = decode_defn_string(string)

		#now save to disk once retrieved.
		print('attempting to SAVE model at ', '{}/{}/{}.pkl'.format(wkdir, model_dir, itemId)) 
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


class Basic(KeywiseExternalCalculationScript):
	"""
	Clustering external calculation for n-dimensions.
	"""
	def function_definition(self) -> Dict[str, str]:
		"""
		Defines the parameters, formula, name, examples and documentation
		for this calculation.

		:return: dictionary containing function details
		"""
		parameters = [
			{'Name':'modelSignal', 'Type':'Signal'},
			{'Name': 'signal0', 'Type': 'Signal'},
			{'Name': 'signal1', 'Type': 'Signal'},
			{'Name': 'signal2', 'Type': 'Signal', 'Optional':True},
			{'Name': 'signal3', 'Type': 'Signal', 'Optional':True},
			{'Name': 'signal4', 'Type': 'Signal', 'Optional':True},
			{'Name': 'signal5', 'Type': 'Signal', 'Optional':True},
			{'Name': 'signal6', 'Type': 'Signal', 'Optional':True},
			{'Name': 'signal7', 'Type': 'Signal', 'Optional':True},
			{'Name': 'signal8', 'Type': 'Signal', 'Optional':True},
			{'Name': 'signal9', 'Type': 'Signal', 'Optional':True},
			{'Name': 'signal10', 'Type': 'Signal', 'Optional':True},
			{'Name': 'signal11', 'Type': 'Signal', 'Optional':True},
			{'Name': 'signal12', 'Type': 'Signal', 'Optional':True},
			{'Name': 'signal13', 'Type': 'Signal', 'Optional':True},
			{'Name': 'signal14', 'Type': 'Signal', 'Optional':True},
			{'Name': 'signal15', 'Type': 'Signal', 'Optional':True},
			{'Name': 'signal16', 'Type': 'Signal', 'Optional':True},
			{'Name': 'signal17', 'Type': 'Signal', 'Optional':True},
			{'Name': 'signal18', 'Type': 'Signal', 'Optional':True},
			{'Name': 'signal19', 'Type': 'Signal', 'Optional':True},
		]

		examples = [
			{
				'Formula': '@@functionName@@($modelSignal, $series1, $series2)',
				'Description': '2D cluster'
			},
			{
				'Formula': '@@functionName@@($modelSignal, $series1, $series2, $series3)',
				'Description': '3D cluster'
			}
		]

		function_details = {
			'Name': 'ndim',
			'Documentation': textwrap.dedent("""
				This function returns n-dimensional clusters from n-dim signals. Only (up-to) 20 currently signals supported
			""").strip(),
			'Formula': 'externalCalculation(@@scriptId@@, $modelSignal, $signal0, $signal1, $signal2, $signal3, $signal4, $signal5, $signal6, $signal7, $signal8, $signal9, $signal10, $signal11, $signal12, $signal13, $signal14, $signal15, $signal16, $signal17, $signal18, $signal19)',
			'Parameters': parameters,
			'Examples': examples
		}
		return function_details

# The remainder of the script is setup identically to legacy
# external calculation scripts.

	def initialize(self):
		self.model = False
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

	def validate(self, validation_object: ValidationObject):
		"""
		Optional method to validate the types and quantity of input
		signals. Called once each time the script is loaded.
		If validation fails, the error raised will be visible in Seeq
		as part of the formula error during formula execution.

		In this example, it asserts that two input signals are used
		and that these signals have type 'NUMERIC'.

		ValidationObject offers two methods:
		- get_signal_types() which returns a list of types for the
		  input signals
		- get_signal_count() which returns the number of input
		  signals defined in the Seeq formula for the given
		  script invocation

		:param validation_object: ValidationObject
		:return: return value is not checked, an error should be raised
				 in case of validation errors
		"""
		pass

	def compute_output_mode(self) -> str:
		"""
		Type of output signal.
		:return: either 'NUMERIC' or 'STRING'
		"""
		return 'NUMERIC'




