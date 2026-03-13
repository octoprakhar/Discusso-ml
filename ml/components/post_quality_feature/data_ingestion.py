import os
import json
import pandas as pd

from ml.entity.post_quality_feature.ingestion_config_entity import DataIngestionConfig
from ml.entity.post_quality_feature.ingestion_artifact_entity import DataIngestionArtifact

class DataIngestion:
    def __init__(self,config: DataIngestionConfig):
        self.config = config
    

    ## Main ingestion class
    def ingest_data(self):

        ## Load json file
        with open(self.config.raw_data_path,"r", encoding="utf-8") as f:
            records = json.load(f)
        
        ## Convert to dataframe
        df = pd.DataFrame(records)

        ## Create artifact directory
        os.makedirs(self.config.ingestion_artifact_dir, exist_ok=True)

        dataset_path = os.path.join(self.config.ingestion_artifact_dir, "dataset.csv")

        ## Save dataset
        df.to_csv(dataset_path, index=False)

        print(f"Ingested {len(df)} posts")

        return DataIngestionArtifact(dataset_path=dataset_path)
    
