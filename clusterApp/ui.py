from IPython.display import display
from ipywidgets import VBox, HBox, widgets

__all__ = ('checksum','selectType',)

checksum = 'ClusterCapsule4.py:NUMERIC:cIcVv0Gi5qIc'


def selectType(vboxDisplay, buttonSelectSupervised, buttonSelectUnsupervised,):
    """
    Select either supervised or unsupervised.
    """
    buttonSelectUnsupervised.close()
    buttonSelectSupervised.close()
    display(VBox(vboxDisplay))
    return


def clusterUnsupervised(app, buttons, signals, minClusterSize, exactBox, default_override = 200, percent_of_data = 20):
    """Cluster and generate conditions unsupervised.

    args:
        app (hb.clusterApp.App): App
        buttons (array-like): Buttons to close
        signals (array-like): Signals
        minClusterSize (ipywidgets.widget): minClustersize
        exactBox (ipywidgets.widget): exactBox
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
    
    time.sleep(1)
    
    cl.extent_scalar = float(clusterExtent.value) #for cluster extent looks at self.extent_scalar
    
    sys.stdout.write("\rPushing Conditions...")
    cl.push_cluster_formulas(checksum)
    sys.stdout.write("\rOrganizing Worksheet...")
    sys.stdout.flush()
    
    time.sleep(1)
    
    cl.update_wkstep_and_push()
    sys.stdout.write("\rSUCCESS.                                 ")
    sys.stdout.flush()
    return 




