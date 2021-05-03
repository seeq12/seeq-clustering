from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import numpy as np
from joblib import Parallel, delayed

import multiprocessing

ncpus = multiprocessing.cpu_count()

__all__ = ('cluster_contours', 'contour', 'contour_check', 'Cluster_Contour')

def cluster_contours(clusterdf, conditioners, **kwargs):
    """returns IN ORIGINAL SPACE contour points (vectors, ls, origin) of each cluster in clusterdf in a dict
    
    for example, to get a boundary in the original space from this data, you must do 
    
            vectors*ls + origin
    
    options: nwalks, angle_cutoff, percentile_cutoff
    """
    out = dict()
    clns = set(clusterdf.clustern.values) - set({-1})
    ndims = len(conditioners)
    
    for cln in clns:
        points_original = clusterdf[clusterdf.clustern == cln][conditioners].to_numpy()
        standardscaler = StandardScaler()
        points = standardscaler.fit_transform(points_original)
        try:
            vectors, ls = contour(points, **kwargs)
        except IndexError: #happens because the angle cutoff is too narrow for low numbers of data
            print('Unable to process cluster ', cln, ' likely that the angle is too narrow, or that it is a sparse cluster')
            continue
        boundary = vectors*ls #this is to convert back to the original space
        boundaryinoldspace = standardscaler.inverse_transform(boundary.T)

        origin_oldspace = standardscaler.inverse_transform(np.zeros(ndims).reshape(1,ndims))
        relative_boundary_old = boundaryinoldspace - origin_oldspace

        lsinoldspace = np.sqrt(np.sum((relative_boundary_old*relative_boundary_old), axis = 1))
        unitv_oldspace = relative_boundary_old.T/lsinoldspace
        out.update({cln:(unitv_oldspace, lsinoldspace, origin_oldspace)})
    
    return out

def contour(clusterpoints, nwalks = 'default', angle_cutoff = 'best', percentile_cutoff = 90, scalar = 1):
    """returns contour np.array([directions,lens]) for a numpy ndarray of clustered points
    HIGHLY advisable to pass normalized points (i.e. sklearn.preprocessing.StandardScalar)
    
    clusterpoints should be of shape (npoints,ndim)
    """
    points = clusterpoints
    ndims = points.shape[1]
    percentile = percentile_cutoff
    #print('scalar:', scalar)

    if nwalks == 'default':
        nwalks = len(points)

    #length of each point
    lens = np.sqrt(np.sum(points**2, axis = 1))
    #divide by each length
    points_unit_vectors = np.prod((1/lens, points.T)).T
        

    unitvectors, distances = [], []
    random_walk = [] #holds tuple (unitvector, l)
    for i in range(nwalks):
        #generate the vectors along which directions we want to go
        vector = np.random.rand(ndims, 1) - np.random.rand(ndims, 1) 
        l = np.sqrt(np.dot(vector.T, vector).flatten()[0])
        unitvector = vector/l #normalizeand
        unitvectors.append(unitvector)



    #randomwalk unitvectors:
    unitvectors = np.reshape(np.array(unitvectors), (nwalks, ndims))

    #distances = Parallel(n_jobs=ncpus)(delayed(get_distance_along)(unitvector, points, unitvectors, points_unit_vectors, angle_cutoff, percentile) for unitvector in unitvectors)

    
    for unitvector in unitvectors:
        #import pdb; pdb.set_trace()

        
        distance_along = get_distance_along(unitvector, points, unitvectors, points_unit_vectors, angle_cutoff, percentile)

        distances.append(distance_along)
        #create a point at that point and add it to the points for the hull
        #selection = vector*distance_along

    ls = np.array(distances)
    ls = ls*scalar

    random_walk = np.array([unitvectors.T, ls]) #first element is column vector matrix of univecs and the second element is l corresponding to each
    
    return random_walk

def get_distance_along(unitvector, points, unitvectors, points_unit_vectors, angle_cutoff, percentile):

    if angle_cutoff == 'best':
        checkarg = 19 #how many closest, in angle, unitvecs to check
        dots = np.dot(unitvectors, unitvector)
        dots[dots>1] = 1
        dots[dots<-1] = -1 #fix numeric errors
        angles = np.arccos(dots) #find angles to all other unitvecs in randomwalk
        args_of_closest = np.argsort(angles)
        ind = args_of_closest[checkarg] #to get your angle cut off take second smalles angle (first smallest will be yourself)
        tangle_cutoff = angles[ind]
    else:
        tangle_cutoff = angle_cutoff

    #first we want to look at points only within some small angle
    dots_with_points = np.dot(points_unit_vectors, unitvector)
    dots_with_points[dots_with_points>1] = 1
    dots_with_points[dots_with_points<-1] = -1 #fix numeric errors
    angles_with_points = np.arccos(dots_with_points)
    points_closetovec = points[angles_with_points<tangle_cutoff]
    
    while len(points_closetovec) < 20:
        if angle_cutoff != 'best':
            print('unable to process, try expanding angle')
            raise IndexError
        checkarg += 1 #check higher number of close points
        ind = args_of_closest[checkarg]
        points_closetovec = points[angles_with_points<angles[ind]]
        


    #check how far along that vector to get some cutoff behind it
    distance_along = np.percentile(np.dot(points_closetovec, unitvector),percentile)

    return distance_along

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


class Cluster_Contour():

    def __init__(self, datadf, conditioners):
        self.random_walk = cluster_contours(datadf, conditioners) #ignore clustern
        self.labels_ = list(datadf.clustern.values)
        return

    def cl_contour_check(self, check_points):
        return contour_check(check_points, self.random_walk)