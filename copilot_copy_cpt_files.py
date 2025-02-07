import os
import pickle
import numpy as np # for bincounts

# NPRA specific scritp!

# this script was largely written by MS Copilot, with manual adjustments/additions made
# having same end goal as copy_cpt_files.py script,  see description there.


def load_paths( file_path ):
    with open(file_path, 'r') as file:
        paths = [ line.strip() for line in file if not line.startswith('#') ]
    return paths


def get_leaf_path( path, n ):
    parts = path.split( os.sep )
    return os.sep.join( parts[-n:] )


def find_files(paths, aliases, archive_paths, n):
    found_paths = []
    missed_paths = []
    d, r, a = 0,0,0

    for path in paths:
        if os.path.exists(path):
            found_paths.append(path)
            missed_paths.append( None )
            d += 1
        else:
            found = False
            for alias in aliases:
                new_path = path.replace("P:\\", alias, 1)
                if os.path.exists(new_path):
                    found_paths.append(new_path)
                    missed_paths.append( None )
                    found = True
                    r += 1
                    break
            if not found:
                leaf = get_leaf_path(path, n)
                for archive_path in archive_paths:
                    if leaf in archive_path:
                        found_paths.append(archive_path)
                        missed_paths.append( None )
                        found = True
                        a += 1
                        break
                if not found:
                    found_paths.append(None)
                    missed_paths.append( path )
    print ('Direct:', d, '. Replacements:', r,'. Archived:', a)
    return found_paths, missed_paths


def construct_archive_paths(archive_path):
    archive_paths = []
    for root, _, files in os.walk(archive_path): # takes hours to finish!
        for file in files:
            archive_paths.append(os.path.join(root, file))
    return archive_paths


def main(cpt_file_list, archive_path, saved_archive, aliases, n):
    # Load or construct archive paths
    if os.path.exists(saved_archive):
        with open(saved_archive, 'rb') as file:
            archive_paths = pickle.load(file)
    else:
        archive_paths = construct_archive_paths(archive_path)
        with open(saved_archive, 'wb') as file:
            pickle.dump(archive_paths, file)

    # Load paths from the text file
    paths = load_paths( cpt_file_list )

    # extensions
    ext = list(set([os.path.splitext(p)[1] for p in paths]))
    reduced_archived_paths = [ ap for ap in archive_paths if os.path.splitext(ap)[1] in ext ] # reduce by extensions

    # Find files
    found_paths, missed_paths = find_files(paths, aliases, reduced_archived_paths, n)

    # Save found paths to a text file
    with open('cpt_sheet_paths.txt', 'w') as file:
        for path in found_paths:
            file.write(f"{path}\n")

    with open('cpt_sheet_missed_paths.txt', 'w') as file:
        for path in missed_paths:
            file.write(f"{path}\n")



def update_archive_with_new_paths( archive_paths, new_archive_paths ):
    # Generate lists of contents for each new archive path
    k = 0
    for path in new_archive_paths:
        k += 1
        print('Working on: ' + path + '\n (' + str(k) + '/' + str(len(new_archive_paths)) + ')' )
        if os.path.exists( path ):
            new_paths = construct_archive_paths( path )
            archive_paths.extend( new_paths )
    
    # Remove duplicates
    archive_paths = list(set(archive_paths))
    
    # Save the updated archive paths
    with open('historical_new.pkl', 'wb') as file:
        pickle.dump(archive_paths, file)



def lowest_fruits():
    paths = load_paths( 'cpt_sheet_missed_paths.txt' )
    
    folders = [os.path.dirname(path) for path in paths]
    u_folders = list( set(folders) )

    counts = { f:0 for f in u_folders }

    for f in folders:
        counts[f] += 1

    sorted_counts = {k: v for k, v in sorted(counts.items(), key=lambda item: item[1])}
    
    for key, value in sorted_counts.items():
        print(key,'@' ,value)


if __name__ == "__main__":
    cpt_file_list = 'O:\\Landsdekkende\\Geofag\\Geoteknikk\\FoU\\CPTu_lab\\prosjekt.txt' # list of stored results
    archive_path = 'O:\\Landsdekkende\\Geofag\\Historisk' # potential aliases
    saved_archive = 'historical.pkl' # saved file_list    
    aliases = "O:\\PROF\\Alta,O:\\PROF\\Arendal,O:\\PROF\\Bergen,O:\\PROF\\Bodø,O:\\PROF\\Drammen,O:\\PROF\\E16 Sandvika-Skaret,O:\\PROF\\E18 Knapstad-Retvet,O:\\PROF\\E18 Vestfold Syd (Farriseidet),O:\\PROF\\E18 Ås prosjektkontor,O:\\PROF\\Hamar,O:\\PROF\\Harstad,O:\\PROF\\Kristiansand,O:\\PROF\\Leikanger,O:\\PROF\\Lillehammer,O:\\PROF\\Molde,O:\\PROF\\Mosjøen,O:\\PROF\\Moss,O:\\PROF\\Oslo,O:\\PROF\\Skarnes anleggskontor,O:\\PROF\\Skien,O:\\PROF\\Stavanger,O:\\PROF\\Steinkjer,O:\\PROF\\Tromsø,O:\\PROF\\Trondheim,O:\\PROF\\Tønsberg,O:\\PROF\\Vadsø,O:\\PROF\\Varoddbrua,O:\\PROF\\Ålesund".split(',')  # Add your predefined aliases here

    if False: # mine for files
        n = 2  # Number of last directories to include in the leaf path
        main( cpt_file_list, archive_path, saved_archive, aliases, n )
    elif False: # extend historical archive
# Assuming historical.pkl has been read into variable archive_paths
        with open('historical.pkl', 'rb') as file:
            archive_paths = pickle.load(file)

        new_archive_paths = ['O:\PROF\Leikanger\GEO', '\\svv3p12afil02.vegvesen.no\Prof\GEO','O:\PROF\Molde\_Berg og geoteknikk', '\\SVV4P17AFIL02\prof\Lab', '\\vegvesen.no\data\felles\Landsdekkende\Geofag\Historisk\RS 26070 Vegteknisk', '\\svv4p16afil02\Avdeling\Vegtek\OPPDRAG']  # Add your new archive paths here
        archive_paths = update_archive_with_new_paths(archive_paths, new_archive_paths)
    elif True: # study not-founds
        lowest_fruits()