import pandas as pd
import  numpy as np
import pickle
import secrets

from .. import seeqInterface
from .. import historicalBenchmarking

key = 'xAneo3b9Qsa5402ai4YqAg'

__all__ = ('App',)

def push_clusterer_definition_to_seeq_property(serialized_definition, unique_key):
	"""Push a serialized definition of clusterer to a seeq propery. The name will be EKPPropertyStorage<unique_key>

	args:
		serialized_definition (str): Serialized string of binary blob defining the clusterer
		unique_key (str): Identifier for EKPPropertyStorage in Seeq

	returns:
		(str) : ID of pushed capsule.

	"""
	data = pd.DataFrame({
	    'Name':['EKPPropertyStorage{}'.format(unique_key)],
	    'Capsule Start':[pd.Timestamp("10/31/1993")], 
	    'Capsule End': [pd.Timestamp("11/1/1993")],
	    'clusterDefn': ['{}'.format(serialized_definition)],
	    'Type':['Condition'],
	    'Maximum Duration':['1day']
	})

	pushed_ID = seeqInterface.push_capsule(data)
	return pushed_ID


class App():

	def __init__(self, workbook_id, worksheet_id, api_url, 
		auth_token, quiet = True):
		"""need docstring"""

		self.workbook_id = workbook_id
		self.worksheet_id = worksheet_id
		self.api_url = api_url
		self.auth_token = auth_token
		self.quiet = quiet

		workbook = seeqInterface.get_workbook(workbook_id, quiet = False) #quiet False for loading
		self.workbook = workbook

		worksheet = seeqInterface.get_worksheet_from_workbook(worksheet_id, workbook)
		self.worksheet = worksheet

		signals = seeqInterface.get_signals(worksheet)
		self.signals = signals

		conditions = seeqInterface.get_conditions(worksheet)
		self.conditions = conditions

		display_range = seeqInterface.get_display_range(worksheet)
		self.display_range = display_range

		grid = seeqInterface.get_minumum_maximum_interpolation_for_signals_df(signals, display_range)
		self.grid = grid

		worksheet_name = seeqInterface.get_worksheet_name(worksheet)
		self.worksheet_name = worksheet_name

	def cluster(self, signal_list, min_cluster_size, datadf = None, **kwargs):
		"""
		Cluster the data. If datadf is None, we will use hdbscan to cluster and predict. If datadf is passed, the final column must be 'clustern' and we will use contour definition.

		args:
			signal_list (array-like of str): Names of signals to cluster on
			min_cluster_size (int): Minimum cluster size for hdbscan
			datadf (pandas.DataFrame): DataFrame with column 'clustern' which already specifies cluster structure
		"""
		if type(datadf) == type(None):
			#case for doing density based (hdbscan)

			query_str = ""
			for sig in signal_list:
				query_str += "Name == '{}' or ".format(sig)
			query = query_str[:-4] #delete "or" from the end
			
			to_pull = self.signals.query(query)

			datadf = seeqInterface.get_signals_samples(
					to_pull, 
					display_range = self.display_range,
					grid = self.grid
				)
			
			clusteron = list(datadf.columns)

			clusterer = historicalBenchmarking.cluster(datadf, conditioner_cols=clusteron, mcs = min_cluster_size, **kwargs)
		else:
			#case of visual selection and need to use contour

			clusteron = list(datadf.columns)[:-1] #ignore the last one because it is already clustern
			clusterer = historicalBenchmarking.Cluster_Contour(datadf, clusteron).random_walk
		

		self.clusteron = clusteron
		self.clusterer = clusterer
		self.xname = signal_list[0]
		self.yname = signal_list[1]		

		return


	def push_clusterer(self,):
		"""
		Push clusterer to Seeq. Stored as binary blob on Seeq Property.
		"""
		pushed_ids = dict()

		conditioners = self.clusteron

		try:
			scalar = self.extent_scalar
		except AttributeError:
			scalar = 1.25
		
		#todo: update scalar to work with cluterer

		idlist = [self.signals.query("Name == '{}'".format(conditioner)).ID.values[0] for conditioner in conditioners]
		
		byte_clusterer = pickle.dumps(self.clusterer)
		byte_cluster_str = byte_clusterer.hex()
		obj_id_of_cluster_str = push_clusterer_definition_to_seeq_property(byte_cluster_str, secrets.token_hex(10))

		self.clusterer_seeq_id = obj_id_of_cluster_str
		self.idlist = idlist
		return

	def push_cluster_formulas(self, checksum, basename, timeOfRun):
		"""
		Push cluster formulas to Seeq.

		args:
			checksum (str): unique checksum that matches externalCalc checksum.
			basename (str): Basename for the clusters
			timeOfRun (str): Datetime of run. This gives us a unique identifier.
		"""
		self.push_clusterer()

		conditioners = self.clusteron
		bodies = [] #initializing for spy.push

		#determine if we are doing density based or visual:
		try:
			iterable = np.sort(list(set(self.clusterer.labels_)))
		except AttributeError: #case when we are doing contours and visual selection
			iterable = [0]

		#need to account for alphanumeric sorting of clusters:
		max_clustern = max(iterable)
		#how long should each label be? i.e. if we have over 10 clusters, each label should be two digits. if over 100, it should be 3 digits
		len_of_label = len(str(max_clustern))

		for clustern in iterable:

			if clustern == -1:
				continue

			##now generate the formula
			alphabet = 'abcdefghijklmnopqrstuvwxyz'
			
			seeq_dollarsign_ids = []
			j = 0 #multiplier duplicate count of letters
			for i in range(len(conditioners)):
			    if np.mod(i,26) == 0:
			        j+=1
			    seeq_dollarsign_ids.append(alphabet[np.mod(i, 26)]*j)

			insertion_into_formula = ""#an example would be .toSignal(), $a, $b) this is the $a, $b part
			for dollarsign_id in seeq_dollarsign_ids:
				insertion_into_formula += "$" + str(dollarsign_id) + ","
			insertion_into_formula = insertion_into_formula[:-1]

			#TODO: finish up formula
			formula_string = "externalCalculation('{}', '{}&&{}&&{}&&{}'.toSignal(),"+ insertion_into_formula +").setMaxInterpolation({}).toCondition().merge(0, true)"
			formula = formula_string.format(checksum, self.api_url, key, self.clusterer_seeq_id, clustern, self.grid)
			#print(formula)
			
			parametersdict = dict({seeq_dollarsign_ids[i]:self.idlist[i] for i in range(len(conditioners))})

			label = (str('0'*len_of_label) + str(clustern))[-len_of_label:] #for alpha numeric sorting if needed. 

			name = basename + ' ' + label + ' ' + timeOfRun
			body={'Name':name, 'Formula':formula, 
			'Formula Parameters':parametersdict, 'Type':'Condition'}
			bodies.append(body)

		metatag = pd.DataFrame(bodies)

		condition_results = seeqInterface.push_formula(metatag, self.workbook_id, self.worksheet_name)
		self.condition_results = condition_results
		return

	def update_temp_wkstep(self):
		"""
		need docstring
		"""
		worksheet = self.worksheet
		#set to none displayed
		display_items_none = pd.DataFrame({'ID':[], 'Name':[]})
		worksheet.display_items = display_items_none
		returned = self.workbook.push()
		return


	def update_wkstep_and_push(self):
		"""
		need docstring
		"""
		workbook = seeqInterface.get_workbook(self.workbook_id)
		worksheet = seeqInterface.get_worksheet_from_workbook(self.worksheet_id, workbook)

		new_display_items = pd.concat((self.signals[['Name', 'ID', 'Type']], self.condition_results[['Name', 'ID', 'Type']]))

		worksheet.display_items = new_display_items
		#with updated display items
		workbook.push()

		#get workbook with new updates.
		workbook = seeqInterface.get_workbook(self.workbook_id)
		worksheet = seeqInterface.get_worksheet_from_workbook(self.worksheet_id, workbook)

		#get workstep
		new_workstep = worksheet._branch_current_workstep()
		wkstp_stores = new_workstep.get_workstep_stores()

		#put into scatterplot with colors
		to_color_condition_ids = list(self.condition_results['ID'].values)
		
		sq_scatter_plot_store = wkstp_stores['sqScatterPlotStore']
		sq_scatter_plot_store.update({'colorConditionIds':to_color_condition_ids})
		wkstp_stores['sqWorksheetStore'].update({'viewKey':'SCATTER_PLOT'})

		new_workstep.set_as_current()

		returned = workbook.push()
		return



