from seeq import spy, sdk
import numpy as np
import pandas as pd

__all__ = ('get_signals', 
	'get_conditions', 
	'get_display_range', 
	'get_minumum_maximum_interpolation_for_signals_df',
	'get_workbook',
	'get_worksheet_from_workbook',
	'get_worksheet_name',
	'get_signals_samples',
	'push_capsule',
	'push_formula',

)

def get_signals(worksheet):
	"""
	Get the signals displayed on a worksheet. Order the the resulting dataframe such that the first two rows correspond to x and y on the scatterplot.

	args:
		worksheet (seeq.spy.workbooks._worksheet.AnalysisWorksheet): Worksheet

	returns:
		signals (pandas.DataFrame): Displayed Signals
	"""
	display_items = worksheet.display_items

	if len(display_items) == 0:
		raise ValueError('No items (signals, conditions, etc) are displayed in this worksheet.')

	signals_df = display_items.query("Type == 'Signal'")

	try:

		# order by the scatterplot series
		sps = worksheet.scatter_plot_series
		X_id, Y_id = sps['X']['ID'], sps['Y']['ID']
		if X_id == Y_id: # case when you are plotting a straightline, it happens.
			return signals_df

		X_index = signals_df[signals_df['ID'] == X_id].index[0] # first element is the index
		Y_index = signals_df[signals_df['ID'] == Y_id].index[0]
		remaining_indices = list(set(signals_df['ID'].values) - set([X_id, Y_id]))
		indexer = [X_index, Y_index]
		
		for ind in remaining_indices:
			indexer.append(signals_df[signals_df['ID'] == ind].index[0])
			
		return signals_df.reindex(indexer).reset_index(drop = True)
	
	except:
		
		return signals_df

def get_conditions(worksheet):
	"""
	Get the conditions displayed on a worksheet.

	args:
		worksheet (seeq.spy.workbooks._worksheet.AnalysisWorksheet): Worksheet

	returns:
		conditions (pandas.DataFrame): Displayed Conditions
	"""
	display_items = worksheet.display_items

	if len(display_items) == 0:
		raise ValueError('No items (signals, conditions, etc) are displayed in this worksheet.')

	return display_items.query("Type == 'Condition'")


def get_display_range(worksheet):
	"""
	Get the conditions displayed on a worksheet.

	args:
		worksheet (seeq.spy.workbooks._worksheet.AnalysisWorksheet): Worksheet

	returns:
		conditions (dict): Display range. {'Start':Timestamp, 'End':Timestamp}
	"""
	return worksheet.display_range


def get_minumum_maximum_interpolation_for_signals_df(signals, display_range, quiet = True):
	"""
	Get the minimum maximum interpolation for a set of signals.

	args:
		signals (pandas.DataFrame): Signals
		display_range (dict): display range dict. i.e. {'Start': Timestamp(), 'End': Timestamp()}
		quiet (bool): quiet

	returns:
		interpolation_period (str): Minimum maximum interpolation in seconds. i.e. '10s'
	"""
	meta_data = spy.search(
			signals, 
			estimate_sample_period = display_range, 
			quiet = quiet
		) 

	timedelta = min(meta_data['Estimated Sample Period'].values)#type timedelta64
	seconds = timedelta / np.timedelta64(1, 's')
	interpolation_period = str(seconds) + 's'

	return interpolation_period

def get_workbook(workbook_id, quiet = True):
	"""
	Get workbook.

	args:
		workbook_id (str): ID of workbook
		quiet (bool): quiet

	returns:
		workbook (seeq.spy.workbooks._workbook.Analysis)
	"""
	wkb_df = spy.workbooks.search({'ID':workbook_id}, quiet = quiet)
	assert len(wkb_df) == 1, ValueError('workbook_id, {}, is not unique in spy.workbooks.search'.format(workbook_id))
	workbook, *_ = spy.workbooks.pull(wkb_df, include_inventory = False, include_referenced_workbooks=False, quiet = quiet)

	return workbook

def get_worksheet_from_workbook(worksheet_id, workbook, quiet = True):
	"""
	Get a specified worksheet from a workbook.

	args:
		worksheet_id (str): ID of desired worksheet
		workbook (seeq.spy.workbooks._workbook.Analysis): Workbook from which to retrieve
	
	returns:
		worksheet (seeq.spy.workbooks._worksheet.AnalysisWorksheet): Worksheet
	"""
	worksheets = workbook.worksheets
	worksheet_ids = np.array([wk.id for wk in worksheets])
	where_worksheet_id = worksheet_ids == worksheet_id #indexer
	assert sum(where_worksheet_id) == 1, ValueError('worksheet_id, {}, is not found in workbook {}, or is not unique'.format(worksheet_id, workbook))

	worksheet, *_ = np.array(worksheets)[where_worksheet_id]
	return worksheet

def get_worksheet_name(worksheet):
	"""
	Get the name of a worksheet

	args:
		worksheet (): Worksheet

	returns:
		name (str): Name of the worksheet
	"""

	return worksheet.name

def get_signals_samples(signals, display_range, grid, quiet = True):
	"""
	Get samples for set of signals.

	args: 
		signals (pandas.DataFrame): Signals
		display_range (dict): Range to pull samples
		grid (str): The grid to pull the signals. (see get_minumum_maximum_interpolation_for_signals_df())
		quiet (bool): quiet

	returns:
		out (pandas.DataFrame): Samples
	"""
	out = spy.pull(
			signals, 
			start = display_range['Start'],
			end = display_range['End'],
			grid = grid
		)
	return out

def push_capsule(data, quiet = True):
	"""Push capsule to Seeq. Return ID of pushed capsule

	args:
		data (pandas.DataFrame): Capsule data.
		quiet (bool): quiet

	returns: 
		id (str): ID of pushed capsule
	"""
	pushed_data_response = spy.push(metadata = data, quiet = quiet)

	return pushed_data_response['ID'][0]

def push_formula(data, workbook_id, worksheet_name, quiet = True):
	"""
	Push formula to Seeq. Return results of push

	args:
		data (pandas.DataFrame): Data to push.
		workbook_id (str): ID of workbook to scope to.
		worksheet_name (str): Name of the worksheet to scope to
		quiet (bool): quiet

	returns:
		results (pandas.DataFrame): results
	"""

	results = spy.push(
			metadata=data, 
			workbook = workbook_id, 
			worksheet = worksheet_name,
			quiet = quiet
		)

	return results