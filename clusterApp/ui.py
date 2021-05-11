##this should be run in the background of the app. (in appmode)

from .display import checksum
from .display import loading


from ipywidgets import widgets, HTML, Layout, VBox, HBox, Image, Checkbox
import numpy as np
import warnings
import IPython
import os
from seeq import spy
import pandas as pd
from IPython.display import display
from urllib.parse import unquote
import sys
from IPython.display import clear_output
import time

from cluster_ui_backend import clusterBackend

#get the url
url = unquote(jupyter_notebook_url)

#worsheet id
wks = url.split('worksheetId=')[1].split('&')[0]
loading()

#worbook id
wkb = url.split('workbookId=')[1].split('&')[0]

#fix formatting
wkb = wkb.replace('"', '')
wks = wks.replace('"', '')

#url for api
api_url = url.split('data-lab')[0]

#authentication
auth_token = spy.client.auth_token

