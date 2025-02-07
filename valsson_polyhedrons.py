import numpy as np
from plyfile import PlyData
from cptu_classification_models_2d import model_defs

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

'''
    module presents quick clay detection models from Valsson 2013, 2015 & 2017
            the log-scale for y & z axes are precalculated and plotted on linear axis (ax.set_xscale('log') has a bug).
    ticks are modified accordingly
'''

colors={ #(112/255,48/255,160/255) # '#333'    
    0 : (0/255,142/255,194/255), # NPRA blue
    1 : (93/255,184/255,46/255), # NPRA green
    2 : (255/255,150/255,0/255), # NPRA orange
    3 : (237/255,28/255,46/255), # NPRA red
    4 : (68/255,79/255,85/255),  # NPRA dark grey
    'mesh':(0,0,0,0.4)
}

markers={
    0 : "o",
    1 : "^",
    2 : "s"
}

# returns tick labels to simulate log-scale in linear space for 3D plots
# see in comments here: https://stackoverflow.com/questions/3909794/plotting-mplot3d-axes3d-xyz-surface-plot-with-log-scale
def log_tick_formatter( val, pos=None ):
    return f"$10^{{{val:g}}}$"


def format_axes( ax, labels ):
    # axis (x,y,z) are defined as (lin,log,log) - drawn in linear scale    
    axis_label_size = 20
    axis_tick_label_size = axis_label_size * .9

    ax_lims = get_ax_lims( labels )
    axis_labels = get_axis_labels( labels )

    all_axis = [ax.xaxis,ax.yaxis,ax.zaxis]

    # make shift log scale presentation
    for some_axis in all_axis[1:]:
        some_axis.set_major_formatter( mticker.FuncFormatter(log_tick_formatter) )
        some_axis.set_major_locator( mticker.MaxNLocator(integer=True) )

    ax.set_box_aspect([1,1,1])

    # set limits
    ax.set_xlim( ax_lims[0] )
    ax.set_ylim( ax_lims[1] )
    ax.set_zlim( ax_lims[2] )

    # axis labels
    ax.set_xlabel( axis_labels[0], fontsize=axis_label_size )
    ax.set_ylabel( axis_labels[1], fontsize=axis_label_size )
    ax.set_zlabel( axis_labels[2], fontsize=axis_label_size )

    # tick size
    for some_axis in all_axis:
        some_axis.set_tick_params( labelsize=axis_tick_label_size )

    # remove tick at 2 for Bq-axis
    ax.set_xticks(np.arange(-0.5,1.6,0.5))

    ax.view_init(30, 45, 0)


def get_axis_labels( labels ):
    remove = [ 'x(', 'y(', 'z(', ')' ]
    for r in remove:
        labels = labels.replace(r,'')

    x, y, z = labels.split(' ')

    label_dict = {
        'Bq': '\n' + r'$B_q \: (-)$',
        'f_sn': '\n' + r'$f_{sn} \: (-)$',
        'q_tn': '\n' + r'$q_{tn} \: (-)$',
        'Qt': '\n' + r'$Q_t \: (-)$',
        'Fr': '\n' + r'$F_r \: (\%)$',     
    }
    return [ label_dict[x], label_dict[y], label_dict[z] ]


def get_ax_lims( labels ):
    lims = {
        'v13': [ (-0.6, 2), (-1, 1), (0,3) ], # yz in log scale
        'v15/17': [ (-0.6, 2), (-3, 0), (0,3) ],
    }

    ax_lims = lims['v13'] if 'Qt' in labels else lims['v15/17']

    return ax_lims


def vert_face_to_mesh( vertices, faces, alpha, fc=(0,0.5,1), ec=(.3,.3,.3,.1), logs=[False, True, True], flatten_mesh=None ):
    # apply logarithms
    vertices_ = vertices * 1
    
    for i, some_log in enumerate(logs):
        if some_log:
            vertices_[:, i] = np.log10(vertices_[:, i])

    # flatten
    zorder=10
    if flatten_mesh is not None:
        zorder=-2
        for i, lim in enumerate(flatten_mesh):
            if lim is not None:
                vertices_[:, i] *= 0
                vertices_[:, i] += lim
                

    # create polygon collection
    poly3d = [ [vertices_[vertex_idx] for vertex_idx in face] for face in faces ]
    label = 'Model' if flatten_mesh is None else 'Model projection'
    mesh = Poly3DCollection( poly3d, alpha=alpha, facecolor=fc, edgecolor=ec, label=label, zorder=zorder )

    return mesh


def prep_mesh( model_nr, logs=None ):
    # select file
    models = [ 'Valsson2013.ply', 'Valsson2016.ply', 'Valsson2017.ply' ]
    f_name = models[ min(model_nr,len(models)) ]

    if logs is None: logs = [False, True, True] # Robertson charts have (Bq, Fr, Qt) in (lin,log,log)

    # extract model
    ply_data = PlyData.read( f_name )
    vertices = np.array( [list(vertex) for vertex in ply_data['vertex'].data] )
    faces = np.array( [list(face[0]) for face in ply_data['face'].data] )

    # model mesh
    mesh = vert_face_to_mesh( vertices, faces, alpha=0.6, fc=colors[model_nr] )

    # mesh projected onto axis
    flat_meshes = []    
    ax_lims = get_ax_lims( ply_data.comments[2] )

    for i in range(3): # alpha=0.1 makes projected models very faint
        flattener = [ None, None, None ]
        flattener[i] = ax_lims[i][0]
        c = [some_c *.3 for some_c in colors[model_nr] ] # tone down color
        flat_meshes.append( vert_face_to_mesh( vertices, faces, alpha=0.1, fc=c, flatten_mesh=flattener ) )

    return mesh, flat_meshes, ply_data.comments[2]



def add_reference_models( ax, lims ):
    model_color = [0.7]*3
    model_lw = 1.5

    rob90_bq = model_defs['robertson_90_bq']
    rob90_fr = model_defs['robertson_90_fr']
    
    for region in rob90_bq['regions']:
        x, z = rob90_bq['regions'][region]['xy']
        z = np.log10(z)
        ax.plot( x, [lims[1][0]]*len(x), z, lw=model_lw, c=model_color, zorder=-1)

    for region in rob90_fr['regions']: # repeated code as I'm low on time
        y, z = rob90_fr['regions'][region]['xy']
        y, z = np.log10(y), np.log10(z)
        label = ''#'Robertson \'90 SBT charts'
        ax.plot( [lims[0][0]]*len(y), y, z, lw=model_lw, c=model_color, label=label, zorder=-1)

def draw_data( ax, study, is_2025_study=False,s=10,alpha=0.2 ):
    
    for matr in study:
        c = colors[3] if matr['name']=='Sensitive' or 'Quick' in matr['name'] else colors[4]
        m = markers[0] if matr['name']=='Sensitive' or 'Quick' in matr['name'] else markers[1]
        
        x = np.array(matr['BQ'])
        y = np.log10(matr['FSN'])
        z = np.log10(matr['QTN'])

        label = matr['name'].replace('Quick', 'Quick clay').replace('_','-') + ' (' + str(len(x)) + ')'

        if is_2025_study:
            y = np.log10(matr['FR'])
            z = np.log10(matr['QQT'])
            label = label.replace('Quick clay', 'Sensitive')
            label = label.replace('Sensitive', 'Brittle')


        ax.scatter3D(
                    x, 
                    y, 
                    z,
                    label=label,
                    s=s,
                    marker=m,
                    fc=c,
                    alpha=alpha, # no fading
                    zorder=-1
                    )


def draw_model( model_nr ):
    # create figure
    fig, ax = plt.subplots( subplot_kw={"projection": "3d"}, figsize=(12,12) )

    # load 3D model
    mesh, flat_meshes, ax_labels= prep_mesh( model_nr )




    # draw meshes
    ax.add_collection3d( mesh ) # model
    for flat_mesh in flat_meshes:
        ax.add_collection3d( flat_mesh ) # model


    # Robertson '90 models for reference
    if model_nr==0:
        ax_lims = get_ax_lims( ax_labels )
        add_reference_models( ax, ax_lims )
    else:
        from studies import STUDY2, STUDY3
        if model_nr==1:
            draw_data( ax, STUDY2 )
        else:
            pass#draw_data( ax, STUDY3 )



    # pretty print & save
    format_axes( ax, ax_labels )   

    handles, labels = plt.gca().get_legend_handles_labels()

    if model_nr > 0:
        pass
        #handles[4]._set_mar.set_markersize(15)
        #handles[5]._legmarker.set_markersize(15)

    by_label = dict(zip(labels, handles))
    lgnd = plt.legend( by_label.values(), by_label.keys(), markerscale=2.5, bbox_to_anchor=(.8, .85), fontsize=15 )

    
    k = 3+2*i
    #plt.savefig('valsson_201' + str(k) + '.png', dpi=100)
    plt.show()


# runs in current module. called last -> all functions loaded
if __name__=='__main__':
    for i in range(1,3):
        draw_model( i )