from config.paths_config import *
from utils.common_functions import read_yaml_file




if __name__ == "__main__":
    try:
        config = read_yaml_file(CONFIG_PATH)
        print(config)
    except Exception as e:
        print(e)


