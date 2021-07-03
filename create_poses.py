from colmap_wrapper import run_colmap
from read_write_model import read_model

def extract_poses(params):
    pass

if __name__ == '__main__':

    import yaml
    from box import Box

    with open("params.yaml") as file:
        params = yaml.safe_load(file)
    params = Box(params)

    extract_poses(params)
