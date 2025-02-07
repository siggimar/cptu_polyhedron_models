import os
import numpy as np
from study_loader import study_loader as loader
from plyfile import PlyData, PlyElement
from study_loader import study_loader as loader


# To enable use of Blender to edit face/vertice geometry, logarithms are applied to triangle vertices
# and the data standard-scaled (x-x_mean)/std(x). This scripts restores the coordinates in the exported files
# to absolute coordinates.

# i.e.
    # 1. load files
    # 2. coordinates scaled and shifted
    # 3. new files saved

in_dir = '2025_model_scaled_shifted'#'PLY_point_cloud_scaled_shifted'#'2025_model_scaled_shifted'
out_dir = '2025_model_restored'#'PLY_point_cloud_restored'


def get_scale_shift():
    # create loader instance & fit to desired vars
    data_loader = loader( study_nr=3 )
    vars = ['BQ','FR','QQT']
    d_loader = loader(study_nr=3)
    d_loader.fit( vars )

    # collect scale_shift values used by loader
    scale_shift = {}
    for i, ax_name in enumerate( [ 'x', 'y', 'z' ] ):
        scale_shift[ ax_name ] = d_loader.trans_fact( i )
    return scale_shift


def files_in_folder( path, filetype=None ):
    paths = []
    for root, _, files in os.walk( path ): # takes hours to finish!
        for file in files:
            if filetype is not None: # simple check
                filename, file_extension = os.path.splitext( file )
                if filetype.lower() not in file_extension.lower(): continue
            paths.append( os.path.join(root, file) )
    return paths


def restore_plydata( file, scale_shift ):
    ply_data = PlyData.read( file ) # load file        

    # create link to vertices
    vertices = ply_data[ 'vertex' ]
    comments = ply_data.comments
    
    # apply transformations to vertex coordinates
    for ax_name in scale_shift:
        u, s = scale_shift[ ax_name ]
        vertices[ ax_name ] *= s # multiply by standard deviation
        vertices[ ax_name ] += u # add median
        if ax_name != 'x':
            ply_data[ 'vertex' ][ ax_name ] = np.power(10, vertices[ ax_name ] )
        rounded_vertex = np.round( vertices[ ax_name ], 5 )
        ply_data[ 'vertex' ][ ax_name ] = rounded_vertex # limit decimals

    comments.append( 'CPTu sensitivity screening - Valsson 2025' )
    comments.append( 'x(Bq) y(Fr) z(Qt)' )

    ply_data.comments = comments

    return ply_data


def restore():
    files = files_in_folder( in_dir, filetype='.PLY' )    
    os.makedirs(out_dir, exist_ok=True) # creates folder if missing

    scale_shift = get_scale_shift()

    for file in files:
        modified_ply_data = restore_plydata( file, scale_shift ) # edit vertices

        # save to file
        new_filename = os.path.join( out_dir, os.path.basename(file) )
        modified_ply_data.write( new_filename ) # save file

if __name__=='__main__':
    restore()