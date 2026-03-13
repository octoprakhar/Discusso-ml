from ml.components.post_quality_feature.data_ingestion import DataIngestion
from ml.components.post_quality_feature.data_validation import DataValidation

from ml.entity.post_quality_feature.config_entity import DataIngestionConfig,DataValidationConfig

# Ingestion config
ingestion_config = DataIngestionConfig(
    raw_data_path="data/post_quality/raw/post_data_v4.json",
    ingestion_artifact_dir="ml/artifacts/post_quality_feature/ingestion"
)

## Validation config
validation_config = DataValidationConfig(
    validation_artifact_dir="ml/artifacts/post_quality_feature/validation",
    validation_report_path="ml/artifacts/post_quality_feature/validation/validation_report.json",
    required_columns=["id","title","body","effort","openness","is_confident","subreddit"]
)

## Running ingestion
ingestion = DataIngestion(ingestion_config)
ingestion_artifact = ingestion.ingest_data()

## Running Validation
validation = DataValidation(validation_config,ingestion_artifact)
validation_artifact = validation.validate_data()

print("Validated dataset path:", validation_artifact.validated_dataset_path)
print("Validation Status: ", validation_artifact.validation_status)

