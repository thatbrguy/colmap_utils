import os
import numpy as np
import pandas as pd

from colmap_wrapper import run_colmap
from read_write_model import read_model

from collections import defaultdict

def extract_poses(params):
    """
    Extracts poses and some other items. TODO: Elaborate.
    """
    ## TODO: If needed, autocheck if colmap already 
    ## run? Or is this feature not necessary?
    if not params.disable_run_colmap:
        run_colmap(params)

    data = defaultdict(list)
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

    # Shape of w2c_mats and c2w_mats is (M, 4, 4), where M is 
    # the number of images.
    w2c_mats = np.array(w2c_mats)
    c2w_mats = np.linalg.inv(w2c_mats)

    img_keys = list(images.keys())
    img_key_to_idx = {key:idx for idx, key in enumerate(img_keys)}

    points = []
    points_visibility = []

    # TODO: Re-read colmap docs to verify info and logic about visibility.
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
    # Shape of points_visibility --> (P, M)
    points_visibility = np.array(points_visibility)
    
    # Shape of z_projs --> (P, M)
    z_projs = calculate_z_projs_vectorized(points, c2w_mats)

    for key in images:
        img = images[key]
        idx = img_key_to_idx[key]

        camera_id = img.camera_id

        # Shape of vis_array --> (P,)
        vis_array = points_visibility[:, idx]
        # Shape of z_vals --> (P,)
        z_vals = z_projs[:, idx]

        valid_z = z_vals[vis_array == 1]
        near, far = np.percentile(valid_z, 0.1), np.percentile(valid_z, 99.9)

        pose_flattened = c2w_mats[idx, :3, :].flatten().tolist()
        img_name = img.name
        camera_model = cameras[camera_id].model
        camera_params = cameras[camera_id].params.flatten().tolist()

        data["image_name"].append(img_name)
        data["camera_model"].append(camera_model)
        data["camera_params"].append(str(camera_params))
        data["pose"].append(str(pose_flattened))
        data["near"].append(near)
        data["far"].append(far)

    df = pd.DataFrame(data)

    # Rearranging columns for consistency.
    df = df[[
        "image_name", "camera_model", "camera_params",
        "pose", "near", "far",
    ]]
    df.to_csv(params.output_path, index = False)

def calculate_z_projs_vectorized(points, c2w_mats):
    """
    TODO: Docstring!

    Same functionality as of calculate_z_projs but this 
    uses vectorized operations. TODO: Elaborate if needed.
    """
    # Shape of z_basis_vecs --> (1, M, 3)
    z_basis_vecs = c2w_mats[np.newaxis, :, :3, 2]

    # Shape of t_vecs --> (1, M, 3)
    t_vecs = c2w_mats[np.newaxis, :, :3, 3]

    # Shape of points_ --> (P, 1, 3)
    points_ = points[:, np.newaxis, :]

    # Shape of z_projs --> (P, M)
    z_projs = np.sum((z_basis_vecs * (points_ - t_vecs)), axis = -1)

    return z_projs

def calculate_z_projs(points, c2w_mats):
    """
    TODO: Docstring!
    """
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
    
    return z_projs

if __name__ == '__main__':

    import yaml
    from box import Box

    with open("params.yaml") as file:
        params = yaml.safe_load(file)
    params = Box(params)

    extract_poses(params)
