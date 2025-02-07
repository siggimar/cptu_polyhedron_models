import os
import numpy as np
import pyvista as pv
import vtk

from plyfile import PlyData
from cptu_classification_models_2d import model_defs
from studies import STUDY4
from cptu_classification_models_2d import model_defs

import matplotlib.colors as mcolors

from valsson_polyhedrons import format_axes, log_tick_formatter, get_axis_labels, get_ax_lims, vert_face_to_mesh, add_reference_models, draw_data
from valsson_2025_model_restore_coords import files_in_folder, out_dir
from valsson_polyhedrons_2025_point_clouds import prep_p_cloud

'''
    Module presents sensitive material model from 2025 Valsson study using PyVista.

    This was found superior to matplotlib, as it correctly draws point-, and face ordering in 3D.
    The grey chart boundaries, are manually drawn to simulate the Matplotlib used for the simpler models.

    Function to export figures worse than in Matplotlib.

    As in the matplotlib charts, the log-scale for y & z axes are precalculated and 
    plotted on linear axis.
'''

colors={ #(112/255,48/255,160/255) # '#333'    
    'mesh':(0,0,0,0.4),
    'gray':(.4,.4,.4)
}


def c_interp(percentage):
    color_list = [ (93/255,184/255,46/255), (255/255,150/255,0/255), (237/255,28/255,46/255) ] # NPRA green/orange/red
    cmap = mcolors.LinearSegmentedColormap.from_list( "", color_list )
    # interp color at given percentage
    return cmap(percentage)


def prep_mesh( f_name, logs=[False, True, True] ):
    # extract model
    ply_data = PlyData.read( f_name )
    vertices = np.array( [list(vertex) for vertex in ply_data['vertex'].data] )
    faces = np.array( [list(face[0]) for face in ply_data['face'].data] )
    var_names = ply_data.comments[2]

    model_nr = os.path.basename( f_name ).split('p_')[0]
    model_color = c_interp( float(model_nr)/100 )

    # apply logarithms
    vertices_ = vertices * 1

    for i, some_log in enumerate(logs):
        if some_log:
            vertices_[:, i] = np.log10(vertices_[:, i])

    return vertices_, faces, model_color, model_nr, var_names


def add_model_mesh( plotter, meshes ):
    for mesh_collection in meshes:
        # unpack volume model description
        vertices, faces, model_color, model_nr, var_names = mesh_collection
        triangles = np.hstack([[3, *face] for face in faces])
        # create mesh
        mesh = pv.PolyData( vertices, triangles )
        plotter.add_mesh( 
            mesh,
            color=model_color,
            opacity=1,
            show_edges=True,
            edge_color=colors['mesh'],
            label=model_nr,
            edge_opacity=.4
            )


def add_model_points( plotter, p_clouds ):
    for p_cloud in p_clouds:
        vertices_, model_nr, model_color, comments = p_cloud
        label = str(int(model_nr)) + ' (%)'
        plotter.add_mesh(
            vertices_,
            color=model_color,
            point_size=6.0,
            label=label,
            render_points_as_spheres=True
            )



def polyline( points ): #from pyvista documentation
    poly = pv.PolyData()
    poly.points = points
    the_cell = np.arange( 0, len(points), dtype=np.int_ )
    the_cell = np.insert( the_cell, 0, len(points) )
    poly.lines = the_cell
    return poly


def add_face( plotter, vertices, f_color, opacity):
    face = np.array( [4,0,1,2,3] ) # simple faces

    # create mesh
    mesh = pv.PolyData( vertices, face )
    plotter.add_mesh(
        mesh,
        color=f_color,
        opacity=opacity,
        show_edges=False,
        edge_color=colors['mesh'],
        ambient=.6
    )


def add_ax_faces( plotter, meshes ):
    vertices, faces, model_color, model_nr, var_names = meshes[0]
    ax_lims = get_ax_lims( var_names )
    
    f_color = np.array( [.79,.79,.79] )
    opacity = .5
    add_face( plotter, # log(Qt) = 0
             [ ( ax_lims[0][0],ax_lims[1][0], ax_lims[2][0] ),
                ( ax_lims[0][1],ax_lims[1][0], ax_lims[2][0] ),
                ( ax_lims[0][1],ax_lims[1][1], ax_lims[2][0] ),
                ( ax_lims[0][0],ax_lims[1][1], ax_lims[2][0] )
            ], 
            f_color*0.8, 
            opacity)
    
    add_face( plotter, # log(Fr) = -1
             [ ( ax_lims[0][0],ax_lims[1][0], ax_lims[2][0] ),
                ( ax_lims[0][1],ax_lims[1][0], ax_lims[2][0] ),
                ( ax_lims[0][1],ax_lims[1][0], ax_lims[2][1] ),
                ( ax_lims[0][0],ax_lims[1][0], ax_lims[2][1] )
            ], 
            f_color, 
            opacity)
    
    add_face( plotter, # Bq = -0.6
             [ ( ax_lims[0][0],ax_lims[1][0], ax_lims[2][0] ),
                ( ax_lims[0][0],ax_lims[1][1], ax_lims[2][0] ),
                ( ax_lims[0][0],ax_lims[1][1], ax_lims[2][1] ),
                ( ax_lims[0][0],ax_lims[1][0], ax_lims[2][1] )
            ], 
            f_color, 
            opacity)

def add_coordinate_system( plotter, meshes ):
    vertices, faces, model_color, model_nr, var_names = meshes[0]
    ax_lims = get_ax_lims( var_names )

    label_dict = {
        'Bq': '\n' + r'$B_q$',
        'Fr': '\n' + r'$log_{10} \left( F_r \right)$',
        'Qt': '\n' + r'$log_{10} \left( Q_t \right)$',
    }

    ax_labels = [ label_dict['Bq'], label_dict['Fr'], label_dict['Qt'] ]
    ax_lims_comb = list(ax_lims[0] + ax_lims[1] + ax_lims[2])

    grid_args = dict( 
        axes_ranges = ax_lims_comb,
        bounds = ax_lims_comb,
        font_size=12,
        xlabel=ax_labels[0], 
        ylabel=ax_labels[1], 
        zlabel=ax_labels[2],
        n_ylabels=3,
        n_zlabels=4,
        )

    plotter.show_grid(**grid_args)


def add_legend( plotter ):
    plotter.add_legend(
        bcolor='white',
        border=True,
        size=(0.25,0.25),
    )


def add_reference_models( plotter, meshes ):
    vertices, faces, model_color, model_nr, var_names = meshes[0]
    ax_lims = get_ax_lims( var_names )

    model_color = [0.7]*3
    model_lw = 2

    rob90_bq = model_defs['robertson_90_bq']
    rob90_fr = model_defs['robertson_90_fr']
    
    for region in rob90_bq['regions']:
        x, z = rob90_bq['regions'][region]['xy']
        y = [ax_lims[1][0]]*len(x)
        z = np.log10(z)

        pts = np.column_stack([x,y,z])
        plotter.add_mesh( polyline( pts ), color=model_color, line_width=model_lw )
    plotter.add_mesh( polyline( pts ), color=model_color, line_width=model_lw, label='Robertson \'90 SBT charts' )
        

    for region in rob90_fr['regions']: # repeated code as I'm low on time        
        y, z = rob90_fr['regions'][region]['xy']
        y, z = np.log10(y), np.log10(z)
        x = [ax_lims[0][0]]*len(y)

        pts = np.column_stack([x,y,z])
        plotter.add_mesh( polyline( pts ), color=model_color, line_width=model_lw )


def set_view( plotter ):
    camera_pos = ( 5, 6.1, 5 )
    camera_focus = ( 0.7, 0, 1.15 )
    camera_up = ( 0, 0, 1 ) 
    
    cpos = [
        camera_pos,
        camera_focus,
        camera_up,
        ]
    plotter.camera_position = cpos

    if True: # find desired viewpoint coordinate
        def my_cpos_callback():
            plotter.add_text(str(plotter.camera.position), name="cpos")
            return
        plotter.add_key_event("p", my_cpos_callback)


def present_model():
    # load model data & pyvista plotter
    p_cloud_dir = 'PLY_point_cloud_restored'
    meshes = [ prep_mesh( f ) for f in files_in_folder( out_dir ) ]
    p_clouds = [ prep_p_cloud( f ) for f in files_in_folder( p_cloud_dir ) ]
    plotter = pv.Plotter( notebook=False )

    # construct scene
    add_ax_faces( plotter, meshes )
    add_reference_models( plotter, meshes )
    #add_model_mesh( plotter, meshes )
    add_model_points( plotter, p_clouds)
    add_legend( plotter )
    add_coordinate_system( plotter, meshes ) # drawn last for correct scales!

    set_view( plotter )
    
    plotter.save_graphic("valsson_2025_point_cloud.svg") 
    plotter.show( window_size=[1024, 768] )


def write_model_colors():
    fractions = np.arange(0,1.05,0.1)
    for fraction in fractions:
        color = c_interp(fraction)
        print( int(color[0]*255), int(color[1]*255), int(color[2]*255) )



if __name__=='__main__':
    #write_model_colors()
    present_model()
    #test()