from IPython.display import display
from ipywidgets import VBox, HBox, widgets
import time
import sys
import os
import numpy as np

from .. import seeqInterface

from bokeh.layouts import row
from bokeh.models import ColumnDataSource, CustomJS, Button
from bokeh.plotting import figure, show, output_notebook
from bokeh.resources import INLINE
from bokeh.palettes import Viridis, Blues
import itertools

__all__ = ('checksum','selectType','clusterUnsupervised', 'clusterSupervised', 'startSupervised')

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

def startSupervised(app, buttons, xsignal, ysignal, buttonClusterSupervised):

    for button in buttons:
        button.close()
    
    #bokeh configuration
    output_notebook(INLINE)

    x, y = xsignal.value, ysignal.value
    global datadf

    #get the samples
    query_str = ""
    for sig in [x, y]:
        query_str += "Name == '{}' or ".format(sig)
    query = query_str[:-4] #delete "or" from the end
    
    to_pull = app.signals.query(query)

    datadf = seeqInterface.get_signals_samples(
            to_pull, 
            display_range = app.display_range,
            grid = app.grid, quiet = app.quiet
        )

    x, y = datadf.columns

    X = datadf[x]
    Y = datadf[y]

    #randomly down sample
    indices = np.random.choice(len(X), 1000)
    Xnew = X[indices]
    Ynew = Y[indices]

    global datasource

    s1 = ColumnDataSource(data=dict(x=Xnew, y=Ynew))
    p1 = figure(plot_width=400, plot_height=400, tools="lasso_select", title="Select Cluster")
    p1.circle('x', 'y', source=s1, alpha=0.1)

    X = datadf[x]
    Y = datadf[y]

    bins = 50

    H, xe, ye = np.histogram2d(X, Y, bins=bins)


    # produce an image of the 2d histogram
                                             ### centering here
    under_hist = p1.image(image=[H.T], x=xe[0]-((xe[1]-xe[0])/2), y=ye[0]-((ye[1]-ye[0])/2), dw=xe[-1] - xe[0], dh=ye[-1] - ye[0], 
                          palette=Blues[9][::-1]) 
    #the number is because the pallette is dict of lists keyed by how many colors
    under_hist.level = 'underlay'

    #build histogram grid:
    xcoords = [(xe[i] + xe[i-1])/2 for i in range(1, len(xe))]
    ycoords = [(ye[i] + ye[i-1])/2 for i in range(1, len(ye))]
    global hist_grid_points
    hist_grid_points = np.array(list(itertools.product(xcoords, ycoords))) # a set of points for each bixel of the histogram

    s1 = ColumnDataSource(data=dict(x=hist_grid_points[:,0], y=hist_grid_points[:,1]))
    p1.circle('x', 'y', source=s1, selection_color='green', alpha=0.0, selection_alpha = 0.5, nonselection_alpha=0.0)
    
    s2 = ColumnDataSource(data=dict(x=[], y=[]))

    out = s1.selected.js_on_change('indices', CustomJS(args=dict(s1=s1, s2=s2), code="""
            var inds = cb_obj.indices;
            var d1 = s1.data;
            var d2 = s2.data;
            d2['x'] = []
            d2['y'] = []
            for (var i = 0; i < inds.length; i++) {
                d2['x'].push(d1['x'][inds[i]])
                d2['y'].push(d1['y'][inds[i]])
            }
            s2.change.emit()
            var command = "global indexofselection; indexofselection =" + inds;

            var kernel = IPython.notebook.kernel;
            kernel.execute(command)
        """)
    )
    layout = row(p1)
    show(layout)
    display(VBox([buttonClusterSupervised]))
    datasource = s1
    return
    
def clusterSupervised(app, buttons, xsignal, ysignal, clusterExtent):
    
    for button in buttons:
        button.close()
    
    try:
        test = indexofselection
    except NameError:
        print('SELECTION ERROR: please use the lasso tool and plot to make a cluster selection')
        return
    
    x, y = xsignal.value, ysignal.value
    X = datadf[x]
    Y = datadf[y]
    
    check_points = np.column_stack((X.values, Y.values))
    
    #find indices of selection:
    sys.stdout.write("\rSelecting unsampled data...")
    indexer = find_true_points_in_selection_boundary(indexofselection, check_points, hist_grid_points) 
    data_to_push = datadf.iloc[indexer,:]
    app.clusteron = datadf.columns
    app.xname = xsignal.value
    app.yname = ysignal.value
    
    sigs = [x,y]
    mcs = len(data_to_push)#all of them 
    
    data_to_push['clustern'] = [0 for i in range(len(data_to_push))]
    
    app.cluster(signals, mcs, datadf = data_to_push)
    app.update_temp_wkstep() #adjusts to 1sec
    
    time.sleep(1)
    
    app.extent_scalar = float(clusterExtent.value) #for cluster extent looks at self.extent_scalar
    
    sys.stdout.write("\rPushing Conditions...")
    app.push_cluster_formulas(checksum)
    sys.stdout.write("\rOrganizing Worksheet...")
    sys.stdout.flush()
    
    time.sleep(1)
    
    app.update_wkstep_and_push()
    sys.stdout.write("\rSUCCESS.                                 ")
    sys.stdout.flush()
    return

def find_true_points_in_selection_boundary(indexofselection, check_points, hist_grid_points):
    """check_points has shape = npoints x 2 (2dims)
    typically indexofselection is a tuple
    
    returns indices of points selected 
    """
    selection_boundary_inclusive = hist_grid_points[list(indexofselection)]
    from scipy.spatial import ConvexHull, convex_hull_plot_2d
    hull = ConvexHull(selection_boundary_inclusive)
    simps = hull.simplices

    #this will turn out simplices into a counter clockwise circle 

    current = 0 #where to start

    ss, es = simps[:,0], simps[:,1] #starts and ends of line segments
    out = [simps[current]]
    starter = out[0][0]#go until you wrap back around

    for i in range(len(simps)):
        s,e = out[i]
        #find the next simplex (which has the end point of the previous one, but is not the previous one)
        #check the ss:
        e_in_ss = np.argwhere(ss == e).flatten()

        #check the es:
        e_in_es = np.argwhere(es == e).flatten()

        #combine and check:
        possible_next_inds = set(np.concatenate((e_in_es, e_in_ss)))
        possible_next_inds.remove(current)
        assert len(possible_next_inds) == 1, 'there exists at least 3 simplices which include {}'.format(current)
        next_ind = possible_next_inds.pop()
        if ss[next_ind] == e:
            #in "starts" ([:,0])
            out.append(simps[next_ind])
        else:
            #in "ends" ([:,1])
            out.append(simps[next_ind][::-1])
        current = next_ind
        if out[-1][1] == starter:
            break

    out = np.array(out)

    starting_points = []
    boundary_segments = []
    for simplex in out:
        boundary_points = selection_boundary_inclusive[simplex] #(XY,XY)
        start = boundary_points[0]
        end = boundary_points[1]
        starting_points.append(start)
        boundary_segments.append(end - start)
    boundary_segments = np.array(boundary_segments)
    starting_points = np.array(starting_points)

    inside_ind, outside_ind = [], []

    for ijk, point in enumerate(check_points):
        if check_hull(point, boundary_segments, starting_points):
            inside_ind.append(ijk)
        else:
            outside_ind.append(ijk)
            
    return inside_ind

def check_hull(point, boundary_segments, starting_points):
    #make the matrices to tell if we are on left or right side of each of the line segments
    #https://stackoverflow.com/questions/16750618/whats-an-efficient-way-to-find-if-a-point-lies-in-the-convex-hull-of-a-point-cl/16906278#16906278
    #https://stackoverflow.com/questions/1560492/how-to-tell-whether-a-point-is-to-the-right-or-left-side-of-a-line
    checker = 0
    for i in range(len(boundary_segments)):
        AM = (point - starting_points[i]).T
        AB = boundary_segments[i].T
        matrix = np.column_stack((AM, AB))
        checker+=np.sign(np.linalg.det(matrix))
    return abs(checker) == len(boundary_segments)



