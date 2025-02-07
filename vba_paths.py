import os
from copilot_copy_cpt_files import construct_archive_paths


# script to 

def gen_paths():
    working_dir = os.getcwd()
    directory = 'CPTu_lab_files'
    files = construct_archive_paths( directory )
    full_paths = [ os.path.join(working_dir, f) for f in files ]
    return full_paths


if __name__ == '__main__':
    full_paths = gen_paths()
    paths_string = '\n'.join(full_paths).strip()

    with open( 'cptu_file_list_for_vba.txt', 'w' ) as f:
        f.write( paths_string )