import os
import numpy as np
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

    data = {}
    path = os.path.join(params.basedir, "sparse", "0")
    cameras, images, points3D = read_model(path, ext = ".bin")

    ## Getting World to Camera transformation matrices.
    w2c_mats = []

    for key in images:
        img = images[key]

        # R --> Rotation matrix, Shape --> (3, 3) 
        R = img.qvec2rotmat()
        # T --> Translation vector, Shape --> (3,)
        T = img.tvec
        
        # Creating the world to camera transformation matrix.
        RT = np.eye(4)
        RT[:3, :3] = R
        RT[:3,  3] = T

        w2c_mats.append(RT)

    # Shape of w2c_mats and c2w_mats is (N, 4, 4)
    w2c_mats = np.array(w2c_mats)
    c2w_mats = np.linalg.inv(w2c_mats)

    import pdb; pdb.set_trace()  # breakpoint 465458f8 //


if __name__ == '__main__':

    import yaml
    from box import Box

    with open("params.yaml") as file:
        params = yaml.safe_load(file)
    params = Box(params)

    extract_poses(params)
