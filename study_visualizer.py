import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# (see: https://stackoverflow.com/questions/3909794/plotting-mplot3d-axes3d-xyz-surface-plot-with-log-scale)
def log_tick_formatter( val, pos=None ): # tick labels to simulate log-scale in linear space for 3D plots
    return f"$10^{{{val:g}}}$"


def format_axis( ax, d_set=None, ax_lims=[ -4, 4 ], ax_names=['x', 'y', 'z'] ):
    ax_ticks_fsize = 12
    ax_label_fsize = 18

    all_axis = [ax.xaxis,ax.yaxis,ax.zaxis]


    # make shift log scale presentation
    for ax_name, some_axis in zip( ax_names, all_axis ):
        if d_set:
            if d_set[0]['log'+ax_name]==True:
                some_axis.set_major_formatter( mticker.FuncFormatter(log_tick_formatter) )
                some_axis.set_major_locator( mticker.MaxNLocator(integer=True) )

    ax.set_xlim( ax_lims )
    ax.set_ylim( ax_lims )
    ax.set_zlim( ax_lims )

    # axis labels
    if d_set:
        ax.set_xlabel( '\n' + d_set[0]['xlabel'], fontsize=ax_label_fsize )
        ax.set_ylabel( '\n' + d_set[0]['ylabel'], fontsize=ax_label_fsize )
        ax.set_zlabel( '\n' + d_set[0]['zlabel'], fontsize=ax_label_fsize )


markers={
    0 : "o",
    1 : "^",
    2 : "s"
}


def visualize( datasaet ):
    fig, ax = plt.subplots( subplot_kw={"projection": "3d"}, figsize=(12,12) )    
    for some_soil in datasaet:
        m = markers[0] if 'Quick' in some_soil['id'] else markers[1]
        ax.scatter3D(
            some_soil['x_trans'], some_soil['y_trans'], some_soil['z_trans'], # coords
            label=some_soil['id'],            
            s=14,
            marker=m,
            fc=some_soil['color'],
            alpha=.5, # no fading
            zorder=-1
            )
    format_axis( ax, datasaet )
    plt.show()


def draw_pt_boundaries( pts, show=True, var_names=None ):
    fig, ax = plt.subplots( subplot_kw={"projection": "3d"}, figsize=(12,12) )


    format_axis( ax )

    ax.scatter3D(
        pts[0], # coords
        pts[1], 
        pts[2],
        label='boundary',
        s=5,
        marker=markers[0],
        fc=(1,0,0),
        alpha=.5, # no fading
        zorder=-1
    )

    if show:
        plt.show()
    return fig, ax