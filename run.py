import os
import numpy as np
import pandas as pd

from colmap_wrapper import run_colmap
from read_write_model import read_model

from collections import defaultdict

def extract_and_save_metadata(params):
    """
    Extracts and saves metadata.

    This function can call the funtion run_colmap if required. The function 
    run_colmap runs the feature extractor, exhaustive matcher and mapper. If 
    the user already has the output of a colmap run and they just want to 
    extract the metadata, then they can skip the execution of run_colmap by 
    setting do_not_run_colmap to True in the params yaml file.
    
    The sparse model is the directory which contains (cameras.bin, images.bin 
    and points3D.bin) OR (cameras.txt, images.txt and points3D.txt).

    The path to the sparse model is by default assumed to be:
    
        sparse_model_path = os.path.join(params.basedir, params.sparse_folder_name, "0")
    
    If the user wants to specify a different sparse model path, then the user 
    has to modify that line in the code.
    """
    # If params.do_not_run_colmap is set to True, the function run_colmap 
    # will not be called. This would be useful if you would just like to 
    # extract and save metadata of a colmap run that has already been completed.
    if not params.do_not_run_colmap:
        run_colmap(params)

    data = defaultdict(list)
    sparse_model_path = os.path.join(params.basedir, params.sparse_folder_name, "0")
    cameras, images, points3D = read_model(sparse_model_path)

    # w2c_mats would contain the world to camera transformation matrices
    w2c_mats = []
    images_keys = sorted(images.keys())
    points3D_keys = sorted(points3D.keys())

    for key in images_keys:
        img = images[key]

        # R is a rotation matrix of shape (3, 3) 
        R = img.qvec2rotmat()
        # T is a translation vector of shape (3,)
        T = img.tvec
        
        # Creating the world to camera transformation matrix RT
        RT = np.eye(4)
        RT[:3, :3] = R
        RT[:3,  3] = T

        w2c_mats.append(RT)

    # Shape of w2c_mats and c2w_mats is (M, 4, 4), where M is 
    # the number of images.
    w2c_mats = np.array(w2c_mats)
    c2w_mats = np.linalg.inv(w2c_mats)
    img_key_to_idx = {key:idx for idx, key in enumerate(images_keys)}

    points = []
    points_visibility = []

    for key in points3D_keys:
        # We set point_visibility to 1 if a point is visible in an image. 
        # We set point_visibility to 0 if a point is not visible in an image. 
        # The dict img_key_to_idx maps an image key to an index in the 
        # point_visibility array.
        point_visibility = [0] * len(images_keys)
        for img_key in points3D[key].image_ids:
            point_visibility[img_key_to_idx[img_key]] = 1

        # points_visibility contains the visibility
        # information of all the points.
        points_visibility.append(point_visibility)
        points.append(points3D[key].xyz)

    # Shape of points: (P, 3)
    points = np.array(points)
    # Shape of points_visibility: (P, M)
    points_visibility = np.array(points_visibility)
    
    # Shape of z_projs: (P, M)
    z_projs = calculate_z_projs_vectorized(points, c2w_mats)

    for key in images_keys:
        img = images[key]
        idx = img_key_to_idx[key]
        camera_id = img.camera_id

        # Shape of vis_array: (P,)
        vis_array = points_visibility[:, idx]
        # Shape of z_vals: (P,)
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
    This function calculates z_projs in a vectorized fashion.
    
    Please refer to the function calculate_z_projs for an explanation
    about z_projs

    Args:
        points      :   A np.ndarray of shape (P, 3) where P 
                        is the number of points.
        c2w_mats    :   A np.ndarray array of shape (M, 4, 4) 
                        where M is the number of images.
    
    Returns:
        z_projs     :   A np.ndarray of shape (P, M).
    """
    # Shape of z_basis_vecs: (1, M, 3)
    z_basis_vecs = c2w_mats[np.newaxis, :, :3, 2]

    # Shape of t_vecs: (1, M, 3)
    t_vecs = c2w_mats[np.newaxis, :, :3, 3]

    # Shape of points_: (P, 1, 3)
    points_ = points[:, np.newaxis, :]

    # Shape of z_projs: (P, M)
    z_projs = np.sum((z_basis_vecs * (points_ - t_vecs)), axis = -1)

    return z_projs

def calculate_z_projs(points, c2w_mats):
    """
    This function calculates z_projs. It is recommended to use
    calculate_z_projs_vectorized since that function can calculate z_projs
    in a vectorized manner.
    
    ==========================
    Explanation about z_projs
    ==========================

    Let us first consider a single point "A" in the world coordinate system. 
    Let us assume there is a camera coordinate system "C" whose origin is located 
    at the point "T" in the world coordinate system. The vector starting from 
    T and ending at A is given by A-T. Let us call this new vector "TA" 
    (i.e. TA = A-T). We are interested in computing the "scalar projection" 
    (https://en.wikipedia.org/wiki/Scalar_projection) of this vector TA onto 
    the unit vector representing the Z-direction of this camera coordinate system 
    in the world coordinate system. Let us call this scalar projection the z_proj 
    for this point "A" and for this camera coordinate system "C".

    Now, if there are "M" camera coordinate systems, we can compute the z_proj of 
    this point "A" for each of the "M" camera coordinate systems.

    Now, in addition to "M" camera coordinate systems, if there are "P" points, we 
    can repeat the procedure mentioned above for all points (i.e. compute the 
    z_proj for each point for each camera).

    If we collect the z_proj values for the case above, we would end up with 
    "M" values for each point (since we calculated a z_proj value for each of 
    the "M" cameras for each point). Hence, we can represent the z_proj values 
    for all "P" points in a 2D array of shape (P, M).

    Args:
        points      :   A np.ndarray of shape (P, 3) where P 
                        is the number of points.
        c2w_mats    :   A np.ndarray array of shape (M, 4, 4) 
                        where M is the number of images.
    
    Returns:
        z_projs     :   A np.ndarray of shape (P, M).
    """
    z_projs = []

    # Shape of point: (3,)
    for point in points:        
        z_projs_per_point = []

        # Shape of pose: (4, 4)
        for pose in c2w_mats:
            z_basis = pose[:3, 2]

            # Shape of translation: (3,)
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

    extract_and_save_metadata(params)
