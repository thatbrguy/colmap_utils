# colmap_utils

This codebase contains some utility functionality using which [COLMAP](https://github.com/colmap/colmap) can be run and some information about the scene can be retrieved.

The file `run.py` contains the function `extract_and_save_metadata` which can (optionally) run COLMAP and then extract information about the scene. The word "optionally" is mentioned because the user can opt to skip running COLMAP if the output of a previous COLMAP run is available and compatible with this codebase. If the user opts to run COLMAP, then the function `run_colmap` (which is defined in `colmap_wrapper.py`) runs the feature extractor, exhaustive matcher and mapper. Please refer to `colmap_wrapper.py` for more information.

The information about the scene is collected and stored in a CSV file. The CSV file would contain information about the camera models, camera parameters, camera pose, near and far bounds for each image. While the information about the camera models, camera parameters and camera pose are computed by COLMAP, the near and far bounds are computed in the function `extract_and_save_metadata` in `run.py`.

Please refer to the docstrings, code and comments in the files `run.py` and `colmap_wrapper.py` to understand how this codebase works and how to set the parameters in `params.yaml`.

## Installation

1. Install COLMAP by following the instructions in their [documentation](https://colmap.github.io/install.html).
2. Git clone this repository and change your directory to where this repository was cloned in your local filesystem.
	- For example, if you git cloned this repository to the path `/path/to/colmap_utils`, please run `cd /path/to/colmap_utils`
3. Create a virtual environment using your preferred method. Install dependencies for this library using `pip install -r requirements.txt`

## Usage

1. Change your directory to the path where this repository was cloned in your local filesystem.
	- For example, if you git cloned this repository to the path `/path/to/colmap_utils`, please run `cd /path/to/colmap_utils`
2. Activate the virtual environment where you had previously installed the dependencies.
3. Set parameters in `params.yaml` appropriately.
4. Run `python run.py` to (optionally) run colmap and extract information about the scene.

## Notes
- The file `read_write_model.py` was taken from the `dev` branch of the [COLMAP](https://github.com/colmap/colmap) repository. The latest commit in the `dev` branch of the [COLMAP](https://github.com/colmap/colmap) repository when the file was taken was `cf4a39cee879a1c1000bac7f92cdc024c4c4c523`. The file was found in `scripts/python` in the [COLMAP](https://github.com/colmap/colmap) repository.

## References
1. [COLMAP](https://github.com/colmap/colmap)
2. [LLFF](https://github.com/Fyusion/LLFF)
