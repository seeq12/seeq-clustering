import hdbscan
import pandas as pd
import numpy as np

import warnings

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

import multiprocessing

__all__ = ('recluster', 'cluster')


def cluster(datadf, target_cols = [], conditioner_cols = [], mcs = 'default', pca_n = 'all', verbosity = 0, percent_of_data = 20,
              default_override = None, **kwargs):
    """
        clusters the datadf and returns an hdbscan.clusterer obj
        
        this method removes nans outright
    """
    ddf = datadf
    ddf.dropna(inplace = True)
    
    if mcs == 'default':
        if default_override == None:
            fixedval = 200
        else:
            fixedval = default_override
        mcs = max(int(len(ddf)*percent_of_data/100), fixedval) #where we determine mcs 

    cdf = ddf[conditioner_cols]

    standard_scaler = StandardScaler()
    X = standard_scaler.fit_transform(np.array(cdf))

    if pca_n == 'all':
        pca_n = len(conditioner_cols)

    if verbosity>2:
        from IPython.core.display import display, HTML
        thing = ('<b>Historical Benchmarking cluster instance:</b><br><em>conditioners</em>='+str(conditioner_cols)+'<br><em>min_cluster_size</em>='+str(mcs)+
                 '<br><em>pca_n</em>='+str(pca_n))
        html_str = '<div style="background-color: #d8bbfa ; padding: 10px;">'+thing+'</div>'
        html = HTML(html_str)
        display(html)


    pca = PCA(n_components=pca_n) # how many components to collapse to (here we use 2)
    Sp_ = pca.fit_transform(X)

    data = Sp_
    unscaled_data = np.array(cdf) # we need the original data for posting condition to seeq


    #mcs = mcs #where we specify percentage of data each cluster must should cover 
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=mcs, 
        min_samples=min(2000, int(mcs/10)), 
        core_dist_n_jobs=multiprocessing.cpu_count(),
        prediction_data=True,
        **kwargs
        )

    clusterer.fit(unscaled_data)

    #clusterer.pca = pca
    #clusterer.standard_scaler = standard_scaler

    if sum(clusterer.labels_) == -1*len(cdf):
        raise ValueError('unable to determine any cluster structure, try reducing mcs, or data size')
        
    return clusterer 



def recluster(datadf, target_cols = [], conditioner_cols = [], mcs = 'default', pca_n = 'all', drop_unclustered = False,
              column_values_specified = [],bycluster = False, verbosity = 0, percent_of_data = 20,
              default_override = None, **kwargs):
    """reclusters the datadf on the condtioner_cols. returns a dataframe with only target_cols and conditioner_cols 
        as columns. includes a clustern value - defining what cluster (if any) it belongs to

        #this needs an update
        
        mcs defaults to max(len(datadf/10), 1000), column_values_specified can be specified, i.e. if you to cluster 
        only when a certain col == 1.0 for example you would include [('col', 1.0)]
        drop_unclustered - if true will drop all values that are assigned a clustern of -1 (i.e. not in a cluster)
        
        pca_n = 'all' means pca_n = len(conditioner_cols), otherwise specify
        bycluster = True will cluster within originally created clusters. False will just restart with only previously clustered data.
        default_override changes 200 in max(len(datadf/100), 1000), use as default_override = 20 e.g.
        
        this method removes nans outright
    """
    ddf = datadf.copy()
    ddf.dropna(inplace = True)
    if 'clustern' in set(ddf.columns):
        if bycluster:
            clusterlabels = list(set(ddf.clustern.values) - set({-1}))
        else:
            clusterlabels = [None]
    else:
        clusterlabels = [None]
    
    
    starterclustern = 0
    for cln in clusterlabels:
        if cln == None: 
            indexer = [True for x in range(len(ddf))]
        else:
            indexer = ddf.clustern == cln
        worker = ddf[indexer].copy()
            
        
        if mcs == 'default':
            if default_override == None:
                fixedval = 200
            else:
                fixedval = default_override
            mcs = max(int(len(worker)*percent_of_data/100), fixedval) #where we determine mcs 
            #print('n datapoints:', len(worker))
        for condit in column_values_specified:
            try:
                worker[condit[0]]
            except KeyError:
                continue
            worker = worker[worker[condit[0]] == condit[1]]
            worker.drop(columns = [condit[0]], inplace = True)
            conditioner_cols = np.array(conditioner_cols) #if we drop a column we need to get rid of it from list of conditioner cols
            conditioner_cols = conditioner_cols[[True if not x else False for x in conditioner_cols == condit[0]]]
            conditioner_cols = list(conditioner_cols)
            print('updated conditioner_cols to', conditioner_cols, 'consider updating in notebook')
            if condit[0] in set(target_cols):
                raise ValueError('you are specifying a specific value of a target signal')

        cdf = worker[conditioner_cols]

        X = StandardScaler().fit_transform(np.array(cdf))
        #X = np.array(conditioner_df)
        if pca_n == 'all':
            pca_n = len(conditioner_cols)

        if verbosity>2:
            from IPython.core.display import display, HTML
            thing = ('<b>Historical Benchmarking recluster instance:</b><br><em>conditioners</em>='+str(conditioner_cols)+'<br><em>bycluster</em>='+str(bycluster)+'<br><em>min_cluster_size</em>='+str(mcs)+
                     '<br><em>pca_n</em>='+str(pca_n)+'<br><em>drop_unclustered</em>='+str(drop_unclustered)+'<br><em>column_values_specified</em>='+str(column_values_specified))
            html_str = '<div style="background-color: #d8bbfa ; padding: 10px;">'+thing+'</div>'
            html = HTML(html_str)
            display(html)


        pca = PCA(n_components=pca_n) # how many components to collapse to (here we use 2)
        Sp_ = pca.fit_transform(X) 

        data = Sp_
        unscaled_data = np.array(cdf) # we need the original data for posting condition to seeq


        #mcs = mcs #where we specify percentage of data each cluster must should cover 
        clusterer = hdbscan.HDBSCAN(min_cluster_size=mcs, min_samples=min(2000, int(mcs/10)), core_dist_n_jobs=multiprocessing.cpu_count(),
            **kwargs)
        clusterer.fit(data)
        if sum(clusterer.labels_) == -1*len(cdf) and cln == None:
            raise ValueError('unable to determine any cluster structure, try reducing mcs, or data size')
            
        worker['clustern'] = clusterer.labels_

        worker = worker[target_cols + conditioner_cols + ['clustern']]
        if drop_unclustered:
            print('You are dropping unclustered. This is not recommended. This will soon be depracated')
            worker = worker[worker.clustern != -1]
        if len(worker) == 0:
            if cln != None:
                if verbosity>=1:
                    print('cluster', cln, 'did not resize, appending original')
            else:
                if verbosity>=1:
                    print('clusters did not resize, appending original')
            worker = ddf[indexer].copy()
        else:
            worker['clustern'] = [x + starterclustern if x!=-1 else x for x in worker.clustern.values]
        try:
            out = out.append(worker)
        except NameError:
            out = worker.copy()
            
        starterclustern = int(max(set(out.clustern.values))) + 1
    
    if bycluster:
        try:
            out = out.append(ddf[ddf.clustern == -1])
        except AttributeError:
            "do nothing because we have not yet clustered"
    ddf = out.sort_index()
    return ddf