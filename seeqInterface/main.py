from seeq import spy, sdk
import numpy as np
import pandas as pd

def get_signals(worksheet):
	"""
	Get the signals displayed on a worksheet.

	args:
		worksheet (seeq.spy.workbooks._worksheet.AnalysisWorksheet): Worksheet

	returns:
		signals (pandas.DataFrame): Displayed Signals
	"""
	display_items = worksheet.display_items

	return display_items.query("Type == 'Signal'")

def get_conditiosn(worksheet):
	"""
	Get the conditions displayed on a worksheet.

	args:
		worksheet (seeq.spy.workbooks._worksheet.AnalysisWorksheet): Worksheet

	returns:
		conditions (pandas.DataFrame): Displayed Conditions
	"""
	display_items = worksheet.display_items
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

