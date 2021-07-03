## This code is a slightly modified version of 
## colmap_wrapper.py from https://github.com/Fyusion/LLFF
import os
import subprocess

def get_additional_args(dict_):
    """
    Gets additional args from the given dictionary.
    """
    additional_args = []
    for key, value in dict_.items():
        assert (type(key) is str) and (type(value) is str)
        additional_args.extend([f"--{key}", value])

    return additional_args

def run_colmap(params):
    """
    Runs colmap
    """
    basedir = params.basedir

    db_path = os.path.join(basedir, params.db_name)
    logfile_path = os.path.join(basedir, params.log_file_name)
    img_folder_path = os.path.join(basedir, params.img_folder_name)
    sparse_folder_path = os.path.join(basedir, params.sparse_folder_name)

    if not os.path.exists(sparse_folder_path):
        os.makedirs(sparse_folder_path)

    ## Feature Extraction
    feature_extractor_args = [
        "colmap", "feature_extractor",
        "--database_path", db_path, "--image_path", img_folder_path,
    ]

    additional_args = get_additional_args(params.feature_extractor)
    feature_extractor_args += additional_args

    ## TODO: Are paranthesis needed?
    feat_output = (subprocess.check_output(feature_extractor_args, universal_newlines=True))

    print("[*] feature_extractor has finished execution.")

    ## Exhaustive Matching
    exhaustive_matcher_args = [
        "colmap", "exhaustive_matcher", "--database_path", db_path
    ]

    ## TODO: Are paranthesis needed?
    match_output = (subprocess.check_output(exhaustive_matcher_args, universal_newlines=True))

    print("[*] exhaustive_matcher has finished execution.")

    ## Mapping
    mapper_args = [
        "colmap", "mapper", "--database_path", db_path, 
        "--image_path", img_folder_path, "--output_path", sparse_folder_path,
    ]

    additional_args = get_additional_args(params.mapper)
    mapper_args += additional_args

    ## TODO: Are paranthesis needed?
    map_output = (subprocess.check_output(mapper_args, universal_newlines=True))

    print("[*] mapper has finished execution.")

    ## Writing to log file.
    with open(logfile_path, "w") as logfile:
        logfile.write(feat_output)
        logfile.write(map_output)

    print("[*] Finished writing to log file.")
