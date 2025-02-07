import os
import pickle

# NPRA specific scritp!

# Projects have been moved, and discs changed names since reporting CPTu sheets
# to the register.  This script attempts to locate the files,  first using alias
# replacements if not found in inital location, and then using a brute force 
# search in historical archive.

cpt_file_list = 'O:\\Landsdekkende\\Geofag\\Geoteknikk\\FoU\\CPTu_lab\\prosjekt.txt' # list of stored results
archive_path = 'O:\\Landsdekkende\\Geofag\\Historisk' # potential aliases
saved_archive = 'historical.pkl' # saved file_list

def read_historical_file_paths( root ):
    file_list = []
    for path, subdirs, files in os.walk(root):
        for name in files:
            file_list.append( os.path.join(path, name) )
    return file_list


def read_f_list_file():
    res = []
    if os.path.isfile( cpt_file_list):
        with open( cpt_file_list, 'r' ) as f:
            f_contents = f.read()
        res = f_contents.split('\n')
    return res


def check_path_alias( f_path ):
    path_replacements = "P:\\,O:\\PROF\\Alta,O:\\PROF\\Arendal,O:\\PROF\\Bergen,O:\\PROF\\Bodø,O:\\PROF\\Drammen,O:\\PROF\\E16 Sandvika-Skaret,O:\\PROF\\E18 Knapstad-Retvet,O:\\PROF\\E18 Vestfold Syd (Farriseidet),O:\\PROF\\E18 Ås prosjektkontor,O:\\PROF\\Hamar,O:\\PROF\\Harstad,O:\\PROF\\Kristiansand,O:\\PROF\\Leikanger,O:\\PROF\\Lillehammer,O:\\PROF\\Molde,O:\\PROF\\Mosjøen,O:\\PROF\\Moss,O:\\PROF\\Oslo,O:\\PROF\\Skarnes anleggskontor,O:\\PROF\\Skien,O:\\PROF\\Stavanger,O:\\PROF\\Steinkjer,O:\\PROF\\Tromsø,O:\\PROF\\Trondheim,O:\\PROF\\Tønsberg,O:\\PROF\\Vadsø,O:\\PROF\\Varoddbrua,O:\\PROF\\Ålesund".split(',')
    if 'P:\\' in f_path:
        for replacement in path_replacements:
            test_path = f_path.replace('P:\\', '\\' + replacement )
            if os.path.isfile( test_path ):
                if f_path != test_path: print(f_path + '\nfound at\n' + test_path)
                return test_path
    return f_path


def validate_f_list( f_list ):
    res, rej = [], []
    for file_path in f_list:
        f_path = check_path_alias( file_path )
        if os.path.isfile( f_path ):
            res.append( f_path )
        else:
            rej.append( file_path )

    return res, rej


def check_rejects( rejects ):
    found_files = []
    rejected_files = []

    all_files = load_results( saved_archive )
    if not all_files:
        all_files = read_historical_file_paths( archive_path )
        save_results( all_files, saved_archive )
    
    
    
    return all_files

# functions to load/save results
def load_results( file_path ):
    res = []
    if os.path.isfile( file_path ):
        with open( file_path, 'rb') as f:
            res = pickle.load( f )
    return res
def save_results( some_list, file_path):
    with open( file_path, 'wb' ) as f:
        pickle.dump( some_list, f )



def get_f_list():
    f_list, rejects = [], []
    #f_list = read_f_list_file()
    #f_list, rejects = validate_f_list( f_list )

    rejects_found, rejects = check_rejects( rejects )

    f_list += rejects
    a=1


def run():
    f_list = get_f_list()


if __name__=='__main__':
    run()