from dataclasses import dataclass

@dataclass
class DataIngestionConfig:
    raw_data_path: str
    ingestion_artifact_dir: str
    