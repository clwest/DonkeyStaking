import yaml
import json
import os
import shutil
from scripts.helpers.helpful_scripts import FRONT_END_FOLDER


def update_front_end():
    # Send contracts to the front end to be able to interact with them
    copy_folders_to_front_end("./build", f"{FRONT_END_FOLDER}artifacts")
    
    #convert yaml to json
    with open("brownie-config.yaml", "r") as brownie_config:
        config_dict = yaml.load(brownie_config, Loader=yaml.FullLoader)
        with open(f"{FRONT_END_FOLDER}brownie_config.json", "w") as brownie_config_json:
            json.dump(config_dict, brownie_config_json)
        print("Front end updating")
        
def copy_folders_to_front_end(src, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(src, dest)
    
def main():
    update_front_end()