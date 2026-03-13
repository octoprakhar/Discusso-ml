from dataclasses import dataclass

@dataclass
class DataIngestionConfig:
    raw_data_path: str
    ingestion_artifact_dir: str
    
@dataclass
class DataValidationConfig:
    validation_artifact_dir: str
    validation_report_path: str
    required_columns: list
