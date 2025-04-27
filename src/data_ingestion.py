import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
import pandas as pd
from sklearn.model_selection import train_test_split
from google.cloud import storage
from src.logger import get_logger
from src.custom_exception import CustomException
from config.paths_config import *
from utils.common_functions import read_yaml_file

logger = get_logger(__name__)

class DataIngestion:
    def __init__(self,config):
        self.config = config["data_ingestion"]
        self.bucket_name = self.config["bucket_name"]
        self.bucket_file_name = self.config["bucket_file_name"]
        self.train_test_ratio = self.config["train_ratio"]

        os.makedirs(RAW_DIR,exist_ok=True)

        logger.info(f"Data Ingestion is started for {self.bucket_name} and {self.bucket_file_name} ")
        
    
    def download_csv_from_gcp(self):
        try:
            client = storage.Client()
            bucket = client.bucket(self.bucket_name)
            blob = bucket.blob(self.bucket_file_name)
            blob.download_to_filename(RAW_FILE_PATH)
            logger.info(f"Successfully downloaded the csv file from {self.bucket_name} to {RAW_FILE_PATH}")

        except Exception as e:
            logger.error(f"Error while downloading the csv file from {self.bucket_name} to {RAW_FILE_PATH}: {e}")
            raise CustomException("Error while downloading the csv file from GCP", e)
        
    def split_data_into_train_test(self):
        try:
            logger.info(f"Splitting the data into train and test sets")
            df = pd.read_csv(RAW_FILE_PATH)
            train_df, test_df = train_test_split(df, test_size=1-self.train_test_ratio, random_state=42)
            train_df.to_csv(TRAIN_FILE_PATH, index=False)
            test_df.to_csv(TEST_FILE_PATH, index=False)
            logger.info(f"Successfully split the data into train and test sets and saved to {TRAIN_FILE_PATH} and {TEST_FILE_PATH}")
        except Exception as e:
            logger.error(f"Error while splitting the data into train and test sets: {e}")
            raise CustomException("Error while splitting the data into train and test sets", e)     
        
    def initiate_data_ingestion(self):
        try:
            logger.info(f"Initiating the data ingestion")
            self.download_csv_from_gcp()
            self.split_data_into_train_test()
            logger.info(f"Data ingestion is completed")
        except CustomException as e:
            logger.error(f"Error while initiating the data ingestion: {str(e)}")
            raise CustomException("Error while initiating the data ingestion", e)
        
        finally:
            logger.info(f"Data ingestion is completed")


if __name__ == "__main__":
    try:
        config = read_yaml_file(CONFIG_PATH)
        data_ingestion = DataIngestion(config)
        data_ingestion.initiate_data_ingestion()
    except Exception as e:        
        logger.error(f"Error while initiating the data ingestion: {str(e)}")
        raise CustomException("Error while initiating the data ingestion", e)   
    




