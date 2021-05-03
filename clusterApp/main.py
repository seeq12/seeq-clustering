import pandas as pd
import  numpy as np

from .. import seeqInterface
from .. import historicalBenchmarking

__all__ = ('App',)

class App():

	def __init__(self, workbook_id, worksheet_id, api_url, 
		auth_token, quiet = True):

		self.workbook_id = workbook_id
		self.worksheet_id = worksheet_id
		self.api_url = api_url
		self.auth_token = auth_token

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
