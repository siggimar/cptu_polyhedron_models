import os
import numpy as np
from plyfile import PlyData
from cptu_classification_models_2d import model_defs
from studies import STUDY4

import matplotlib.pyplot as plt
#import matplotlib.ticker as mticker
import matplotlib.colors as mcolors

#from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from valsson_polyhedrons import format_axes, log_tick_formatter, get_axis_labels, get_ax_lims, vert_face_to_mesh, add_reference_models, draw_data
from valsson_2025_model_restore_coords import files_in_folder, out_dir

'''
    Module presents data used to generate the 2025 Valsson polyhedron model for sensitivity screening
    
    the log-scale for y & z axes are precalculated and plotted on linear axis (ax.set_xscale('log') has a bug).
    ticks are modified accordingly
'''

colors={ #(112/255,48/255,160/255) # '#333'    
    '000' : (0/255,142/255,194/255), # NPRA blue
    '010' : (93/255,184/255,46/255), # NPRA green
    '020' : (255/255,150/255,0/255), # NPRA orange
    '030' : (237/255,28/255,46/255), # NPRA red
    '040' : (68/255,79/255,85/255),  # NPRA dark grey
    '050' : (0/255,142/255,194/255), # NPRA blue
    '060' : (93/255,184/255,46/255), # NPRA green
    '070' : (255/255,150/255,0/255), # NPRA orange
    '080' : (237/255,28/255,46/255), # NPRA red
    '090' : (68/255,79/255,85/255),  # NPRA dark grey
    '100' : (0/255,142/255,194/255), # NPRA blue
    'mesh':(0,0,0,0.4)
}


def c_interp(percentage):
    color_list = [(93/255,184/255,46/255), (255/255,150/255,0/255), (237/255,28/255,46/255)] # NPRA green/orange/red
    cmap = mcolors.LinearSegmentedColormap.from_list("", color_list)
    # interp color at given percentage
    return cmap(percentage)


def prep_mesh( f_name, logs=[False, True, True] ):
    # extract model
    ply_data = PlyData.read( f_name )
    vertices = np.array( [list(vertex) for vertex in ply_data['vertex'].data] )
    faces = np.array( [list(face[0]) for face in ply_data['face'].data] )

    model_nr = os.path.basename( f_name ).split('p_')[0]
    model_color = c_interp( float(model_nr)/100 )

    # model mesh
    mesh = vert_face_to_mesh( vertices, faces, alpha=1, fc=model_color ) #colors[model_nr]

    # mesh projected onto axis
    flat_meshes = []    
    ax_lims = get_ax_lims( ply_data.comments[2] )

    for i in range(3): # alpha=0.1 makes projected models very faint
        flattener = [ None, None, None ]
        flattener[i] = ax_lims[i][0]
        c = [some_c *.3 for some_c in colors[model_nr] ] # tone down color
        flat_meshes.append( vert_face_to_mesh( vertices, faces, alpha=0.1, fc=c, flatten_mesh=flattener ) )

    return mesh, flat_meshes, ply_data.comments[2]


def present_model():
    meshes = [ prep_mesh( f ) for f in files_in_folder( out_dir ) ]

    # create figure
    fig, ax = plt.subplots( subplot_kw={"projection": "3d"}, figsize=(12,12) )

    # Robertson '90 models for reference
    label_dict = {
        'Bq': '\n' + r'$B_q$',
        'Fr': '\n' + r'$log_{10} \left( F_r \right)$',
        'Qt': '\n' + r'$log_{10} \left( Q_t \right)$',
    }

    ax_labels = [ label_dict['Bq'], label_dict['Fr'], label_dict['Qt'] ]

    ax_labels_ = 'x(Bq) y(Fr) z(Qt)'

    ax_lims = get_ax_lims( ax_labels )
    ax_lims[1] = (-1,1)
    add_reference_models( ax, ax_lims )
    draw_data( ax, STUDY4, is_2025_study=True,s=14,alpha=.35 )

    # pretty print & save
    format_axes( ax, ax_labels_ )   
    handles, labels = plt.gca().get_legend_handles_labels()

    by_label = dict(zip(labels, handles))
    lgnd = plt.legend( by_label.values(), by_label.keys(), markerscale=2, bbox_to_anchor=(.65, .85), fontsize=15 )

    plt.savefig('valsson_2025_data.png', dpi=100)
    plt.show()


if __name__=='__main__':
    present_model()