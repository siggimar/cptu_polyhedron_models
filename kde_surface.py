import os
import numpy as np
import pickle
from scipy.stats import gaussian_kde

from study_visualizer import visualize, draw_pt_boundaries
from study_loader import study_loader as loader
from plyfile import PlyData, PlyElement


# Scripts to define KDE mdoels for the CPTu sensitivity study.


def get_mgrids( mgrid_def ):
    xmin, xmax, ymin, ymax, zmin, zmax, n_pts = mgrid_def
    return np.mgrid[ xmin:xmax:(n_pts*1j), ymin:ymax:(n_pts*1j), zmin:zmax:(n_pts*1j) ]


def gen_kdes( dataset, N=10, lims=[[-10,10],[-10,10],[-10,10]] ):
    n_pts = N #100 goood
    kdes = []

    mgrid_def = [ lims[0][0], lims[0][1], lims[1][0], lims[1][1], lims[2][0], lims[2][1], n_pts]

    # grid to be evaluated
    X, Y, Z = get_mgrids( mgrid_def )
    positions = np.vstack([X.ravel(), Y.ravel(), Z.ravel()])

    for soil_group in dataset:
        values = np.vstack( [soil_group['x_trans'], soil_group['y_trans'], soil_group['z_trans']] )

        kernel = gaussian_kde( values ) #, 'silverman' ) # uses scott
        D = np.reshape(kernel(positions).T, X.shape)
        kdes.append ( [kernel, mgrid_def, D, soil_group['id']] )

    return kdes


def get_kdes( data_loader, N ):
    # run times 'without debugging': (0.051*N)^3 sek. N=50->13s, N=150->475s
    
    # file name
    saves_folder = 'saves'
    save_name = 'kdes_study' + str(data_loader.study_nr) + '_N' + str(N) + '_' + data_loader.var_string + '.pkl'
    file_path = os.path.join(saves_folder, save_name)

    if not os.path.isfile(file_path):
        kdes = gen_kdes( data_loader.data(), N=N ) # generate kdes from data

        with open(file_path, 'wb') as f: # save to file
            pickle.dump( kdes, f)
    else: # load from save
        with open( file_path, 'rb' ) as f: 
            kdes = pickle.load( f )
    return kdes


def gen_pts( kdes, ratio ):
    threshold = 0.05 # closeness to desired ratio
    base_threshold = 0.005 # minimum value of kde_sum to be included

    # points from kde-meshgrids
    X, Y, Z = get_mgrids( kdes[0][1] )
    grid_points = np.vstack([X.ravel(), Y.ravel(), Z.ravel()])

    # % of points that are sensitive
    kde_sum = kdes[0][2] + kdes[1][2]
    relative_kde = kdes[1][2] / kde_sum # this opreration is central in this study

    # remove points that are >=threshold from volume center && those having little data
    point_mask = np.logical_and(np.abs(relative_kde.ravel()-ratio)<threshold, kde_sum.ravel() > base_threshold)
    close_points = grid_points[:, point_mask]

    return close_points


def gen_surface_pts( study_nr=0, N=150 ):
    vars = ['BQ','FR','QQT']
    #vars = ['BQ','FSN','QTN']
    
    # load and normalize data
    d_loader = loader(study_nr=study_nr)

    d_loader.fit( vars )    

    kdes = get_kdes( d_loader, N )

    # density based point clouds
    pts = {}
    for ratio in list(np.arange( 0, 11, 1 )/10):
        pts[ratio] = gen_pts( kdes, ratio )

    return pts

def save_point_cloud_to_ply(x, y, z, filename="output.ply"):

    # create structured numpy array to hold points
    points = np.zeros(len(x), dtype=[("x", "f4"), ("y", "f4"), ("z", "f4")])
    points["x"] = x
    points["y"] = y
    points["z"] = z

    # create PlyElement
    vertex_element = PlyElement.describe(points, "vertex")

    # write file
    PlyData([vertex_element], text=True).write(filename)
    print(f"points saved to {filename}")


def generate_ply_files( pts ):
    for key, value in pts.items():
        x, y, z = value
        f_name = str(key).replace( '.', '_' ) + '-transformed.ply'
        save_point_cloud_to_ply( x, y, z, f_name)

def data_to_ply( study_nr ):
    vars = ['BQ','FR','QQT']
    d_loader = loader(study_nr=study_nr)
    d_loader.fit( vars )

    dataset = d_loader.data()
    for soil_group in dataset:        
        name = soil_group['id']
        x, y, z = soil_group['x_trans'], soil_group['y_trans'], soil_group['z_trans']
        f_name = name + '-transformed.ply'
        save_point_cloud_to_ply( x, y, z, f_name)



if __name__=='__main__':
    pts = gen_surface_pts( study_nr=3, N=500 )

    data_to_ply( study_nr=3 )

    generate_ply_files( pts )
    fig, ax = draw_pt_boundaries( pts[0.5], var_names=vars )
    a=1