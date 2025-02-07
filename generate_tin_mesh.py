
import os
import numpy as np
import scipy.stats as stats
import open3d as o3d

path_from = 'PLY_cleaned'
path_to = 'PLY_meshed'


# script used to apply ball-pivoting method to "skin" each point group
# 
# requires normals to know which direction the pivoting should use,  normal estimation in on line 56
# only partially successful, resulting in 2 surfaces that do not connect, often with very sharp angles.


def remove_internal_points( point_cloud):
    boundary_points = []

    # iterate through points in the cloud
    points = np.asarray( point_cloud.points )
    grid_dist = stats.mode( point_cloud.compute_nearest_neighbor_distance() )[0][0]
    eps_dist = grid_dist * 1.05 # grid dist + eps

    kdtree = o3d.geometry.KDTreeFlann( point_cloud )

    for idx, point in enumerate(points):
        # Perform radius search within grid_distance + small tolerance
        [k, idxs, _] = kdtree.search_radius_vector_3d(point,eps_dist)

        # check neighbor count; if<6, it's a boundary point
        if k - 1 < 6: boundary_points.append(point) # exclude point itself from count

    # create a point cloud for boundary points
    boundary_cloud = o3d.geometry.PointCloud()
    boundary_cloud.points = o3d.utility.Vector3dVector( boundary_points )
    return boundary_cloud


def get_mesh( some_file_path ):
    # initialize point cloud object
    point_cloud = o3d.io.read_point_cloud( some_file_path )
    #o3d.visualization.draw_geometries([point_cloud], window_name='point cloud')

    point_cloud = remove_internal_points( point_cloud )
    #o3d.visualization.draw_geometries([point_cloud], window_name='point cloud')

    # initial distance estimate
    if True:
        all_dist = point_cloud.compute_nearest_neighbor_distance()
        init_radius = np.mean( all_dist )

    radius = 1.5*init_radius

    # estiate normals
    point_cloud.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=radius, max_nn=50))

    # reorient normals to point outward
    point_cloud.orient_normals_consistent_tangent_plane(k=14, cos_alpha_tol=0.35) # lambda_penalty=0.1

    # compute mesh
    mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting( point_cloud, o3d.utility.DoubleVector([radius*0.6, radius*1.6*0.6]) )

    # simplify
    mesh = mesh.simplify_quadric_decimation( target_number_of_triangles=1500 )

    # clean up
    mesh.remove_degenerate_triangles()
    mesh.remove_duplicated_triangles()
    mesh.remove_duplicated_vertices()
    mesh.remove_non_manifold_edges()

    return mesh


def save_mesh( mesh, file_name ):
    out_name = os.path.basename(file_name).split('.')[0] + '-o3d.ply'
    out_name = os.path.join( 'export', out_name )
    o3d.io.write_triangle_mesh(out_name, mesh, write_ascii=True, compressed=False, write_vertex_normals=False, write_vertex_colors=False, write_triangle_uvs=False, print_progress=True)


def show_mesh( mesh ):
    o3d.visualization.draw_geometries([mesh], mesh_show_wireframe=True, mesh_show_back_face=True, window_name='Mesh')


def run_meshing():
    os.makedirs( path_to, exist_ok=True )
    files = [ os.path.join(path_from,f) for f in os.listdir(path_from) if os.path.isfile(os.path.join(path_from, f)) ]

    for file in files:
        some_mesh = get_mesh( file )
        #show_mesh( some_mesh )
        save_mesh ( some_mesh, file )

if __name__=='__main__':
    run_meshing()

    # madrugada