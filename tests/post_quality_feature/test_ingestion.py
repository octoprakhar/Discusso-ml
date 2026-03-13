from ml.components.post_quality_feature.data_ingestion import DataIngestion
from ml.entity.post_quality_feature.ingestion_config_entity import DataIngestionConfig

config = DataIngestionConfig(
    raw_data_path="data/post_quality/raw/post_data_v4.json",
    ingestion_artifact_dir="ml/artifacts/post_quality_feature/ingestion"
)

ingestion = DataIngestion(config=config)

artifact = ingestion.ingest_data()

print("Dataset created at:", artifact.dataset_path)