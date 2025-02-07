import numpy as np
import os
from copilot_copy_cpt_files import load_paths

# script used to find files sharing same name in CPTu registry (only one kept)

# 'CPTu 2020_01 (2)1.xlsm'
# 'CPTu 2018_BH4.xlsm'

cpt_file_list = 'O:\\Landsdekkende\\Geofag\\Geoteknikk\\FoU\\CPTu_lab\\prosjekt.txt' # list of stored results
cpt_file_list = 'cpt_sheet_missed_paths.txt'

def main():
    paths = load_paths( cpt_file_list )
    f_names = [os.path.basename( p ) for p in paths if p != 'None']

    seen = set()
    dupes = [fn for fn in f_names if fn in seen or seen.add(fn)]    

    for d in dupes:
        print( 'file: "' + d + '" is found at:' )
        for p in paths:
            if d in p:
                print('\t' + p)
        print('\n\n')

    a=1


if __name__=='__main__':
    main()
