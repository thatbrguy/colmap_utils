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

    # Shape of w2c_mats and c2w_mats is (I, 4, 4), where I is 
    # the number of images.
    w2c_mats = np.array(w2c_mats)
    c2w_mats = np.linalg.inv(w2c_mats)

    img_keys = list(images.keys())
    img_key_to_idx = {key:idx for idx, key in enumerate(img_keys)}

    points = []
    points_visibility = []

    for key in points3D:
        # point_visibility is 1 if a point is visible in an 
        # image, 0 if not. The dict img_key_to_idx maps an 
        # image key to an index in the point_visibility array.
        point_visibility = [0] * len(img_keys)
        for img_key in points3D[key].image_ids:
            point_visibility[img_key_to_idx[img_key]] = 1

        # points_visibility contains the visibility
        # information of all the points.
        points_visibility.append(point_visibility)
        points.append(points3D[key].xyz)

    # Shape of points --> (P, 3)
    points = np.array(points)
    # Shape of points_visibility --> (P, I)
    points_visibility = np.array(points_visibility)

    ## TODO: Implmement vectorized equivalent.
    ## TODO: Verify calculation!
    z_projs = []
    for point in points:
        
        z_projs_per_point = []
        for pose in c2w_mats:
            # Shape of point --> (3,)
            # Shape of translation --> (3,)
            # Shape of pose --> (4, 4)
            z_basis = pose[:3, 2]
            translation = pose[:3, 3]

            z_projection = z_basis @ (point - translation)
            z_projs_per_point.append(z_projection)

        z_projs.append(z_projs_per_point)

    z_projs = np.array(z_projs)
    import pdb; pdb.set_trace()  # breakpoint 4b8694e0 //

if __name__ == '__main__':

    import yaml
    from box import Box

    with open("params.yaml") as file:
        params = yaml.safe_load(file)
    params = Box(params)

    extract_poses(params)
