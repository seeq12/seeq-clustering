from IPython.display import display
from ipywidgets import VBox, HBox, widgets
import time
import sys
import os

__all__ = ('checksum','selectType','clusterUnsupervised')

checksum = 'ClusterCapsule4.py:NUMERIC:cIcVv0Gi5qIc'

def clear():
    os.system( 'cls' )


def selectType(vboxDisplay, buttonSelectSupervised, buttonSelectUnsupervised,):
    """
    Select either supervised or unsupervised.
    """
    buttonSelectUnsupervised.close()
    buttonSelectSupervised.close()
    display(VBox(vboxDisplay))
    return


def clusterUnsupervised(app, buttons, signals, minClusterSize, exactBox, percentOfData, clusterExtent, 
    default_override = 200, percent_of_data = 20):
    """Cluster and generate conditions unsupervised.

    args:
        app (hb.clusterApp.App): App
        buttons (array-like): Buttons to close
        signals (array-like): Signals
        minClusterSize (ipywidgets.widget): minClustersize
        exactBox (ipywidgets.widget): exactBox
        percentOfData (ipywidgets.widget): percentOfData
        clusterExtent (ipywidgets.widget): clusterExtent
        default_override (int):
        percent_of_data (int or float):

    """
    for button in buttons:
        button.close()


    try:
        mcs = int(minClusterSize.value)
    except ValueError:
        raise TypeError('Minimum number of points must be an integer')
    
    if exactBox.value:
        mcs = int(minClusterSize.value)
    else:
        mcs = 'default' #then the algorithm will choose largest of the two (percent of data and default_override)
        default_override = int(minClusterSize.value)
        percent_of_data = float(percentOfData.value)
    

    app.cluster(signals, mcs, default_override=default_override, percent_of_data=percent_of_data)
    app.update_temp_wkstep() #adjusts to 1sec
    
    #sleep to let the workstep adjust
    time.sleep(1)
    
    #for cluster extent looks at .extent_scalar
    app.extent_scalar = float(clusterExtent.value) 
    
    sys.stdout.write("\rPushing Conditions...")
    clear()
    app.push_cluster_formulas(checksum)
    sys.stdout.write("\rOrganizing Worksheet...")
    sys.stdout.flush()
    
    time.sleep(1)
    clear()
    app.update_wkstep_and_push()
    sys.stdout.write("\rSUCCESS.                                 ")
    sys.stdout.flush()
    return 




