import os
from colmap_wrapper import run_colmap
from read_write_model import read_model

def extract_poses(params):
    """
    Extracts poses and some other items. TODO: Elaborate.
    """
    ## TODO: If needed, autocheck if colmap already 
    ## run? Or is this feature not necessary?
    if not params.disable_run_colmap:
        run_colmap(params)

    path = os.path.join(params.basedir, "sparse", "0")
    cameras, images, points3D = read_model(path, ext = ".bin")
    import pdb; pdb.set_trace()  # breakpoint 0b9789bb //



if __name__ == '__main__':

    import yaml
    from box import Box

    with open("params.yaml") as file:
        params = yaml.safe_load(file)
    params = Box(params)

    extract_poses(params)
