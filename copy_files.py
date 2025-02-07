import hashlib
import os
import shutil
from copilot_copy_cpt_files import construct_archive_paths

# script to locate CPTu sheets from lab-registry and copy to a local archive.

# run on 01.01.2025
# all sheets opened to ensure no VBA errors,  adding code to account for new 
# VBA version in 64bit Excel (pointerSafe command - see library module)

found  = 'cpt_sheet_paths.txt'
missing = 'cpt_sheet_missed_paths.txt'
copied = 'O:\\Landsdekkende\\Geofag\\Geoteknikk\\FoU\\CPTu_lab\\2024'


path_to = 'CPTu_lab_files'
ids = set()


def list_from_files( file_path ):
    res = []
    if os.path.isfile( file_path ):
        with open( file_path, 'r' ) as f:
            f_cont = f.read()
        res = f_cont.strip().split( '\n' )

    res = [ r for r in res if r!='None']
    return res


def verify_files( file_list ):
    ok = True
    count = 0

    for f in file_list:        
        if not os.path.isfile( f ):
            print( 'not found: ' + f )
            ok=False
            continue

        count += 1

    if ok: print( 'All (' + str(count) +  ') files found' )
    else: print( str(count) +  ') files found' )


def retrieve( missing_files ):
    found = []
    lissman_files = construct_archive_paths( copied )

    k=0
    for mf in missing_files:
        f_name = os.path.basename( mf )
        for lf in lissman_files:
            if f_name in lf:
                k += 1
                #print('>> found: ' + str(k), end='\r')
                found.append( lf )
                break
    print('\n')
    return found


def files_to_copy():
    files_found = list_from_files( found )
    files_missing = list_from_files( missing )
    retrieved = retrieve( files_missing )

    all_candidates = files_found + retrieved
    #all_candidates = list(set(all_candidates)) # remove duplicates (sadly also mixes order!)

    return all_candidates


def prep_dir( some_directory ):
    if not os.path.isdir( some_directory ): os.makedirs( some_directory, exist_ok=True)


def dir_hash_id( some_str, n=5 ):    
    some_id = hashlib.md5(some_str.encode('utf-8') ).hexdigest()[:n]    
    return some_id

def copy_files():
    bh_names = []

    all_files = files_to_copy()
    prep_dir( path_to )

    for some_file in all_files:
        # split into components
        head, tail = os.path.split( some_file )

        # only one bh with each name (counter copies)
        if tail in bh_names: continue
        bh_names.append( tail )

        # generate a short generic to_path
        dir_id = dir_hash_id( head, n=5 )
        to_dir = os.path.join( path_to, dir_id )
        to_path = os.path.join(to_dir, tail)

        # prep directory
        prep_dir( to_dir )

        # copy the file
        shutil.copy2( some_file, to_path )





if __name__ == '__main__':
    copy_files()