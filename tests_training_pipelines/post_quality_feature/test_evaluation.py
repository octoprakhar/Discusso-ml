from ml.components.post_quality_feature.data_ingestion import DataIngestion
from ml.components.post_quality_feature.data_validation import DataValidation
from ml.components.post_quality_feature.data_transformation import DataTransformation
from ml.components.post_quality_feature.model_trainer import ModelTrainer
from ml.components.post_quality_feature.model_evaluation import ModelEvaluation

from ml.entity.post_quality_feature.config_entity import DataIngestionConfig,DataValidationConfig,DataTransformationConfig,ModelTrainerConfig,ModelEvaluationConfig

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

## Transformation config
transformation_config = DataTransformationConfig(

    transformation_artifact_dir="ml/artifacts/post_quality_feature/transformation",

    # Effort
    tfidf_vectorizer_path="ml/artifacts/post_quality_feature/transformation/effort/tfidf.pkl",
    scaler_path="ml/artifacts/post_quality_feature/transformation/effort/scaler.pkl",
    effort_feature_train_path="ml/artifacts/post_quality_feature/transformation/effort/X_train.npy",
    effort_feature_test_path="ml/artifacts/post_quality_feature/transformation/effort/X_test.npy",
    effort_labels_train_path="ml/artifacts/post_quality_feature/transformation/effort/y_train.npy",
    effort_labels_test_path="ml/artifacts/post_quality_feature/transformation/effort/y_test.npy",

    # Openness
    openness_feature_train_path="ml/artifacts/post_quality_feature/transformation/openness/X_train.npy",
    openness_feature_test_path="ml/artifacts/post_quality_feature/transformation/openness/X_test.npy",
    openness_labels_train_path="ml/artifacts/post_quality_feature/transformation/openness/y_train.npy",
    openness_labels_test_path="ml/artifacts/post_quality_feature/transformation/openness/y_test.npy"
)

## Model training config
trainer_config = ModelTrainerConfig(
    model_artifact_dir="ml/artifacts/post_quality_feature/model",

    effort_model_path="ml/artifacts/post_quality_feature/model/effort_model.pkl",
    openness_model_path="ml/artifacts/post_quality_feature/model/openness_model.pkl",

    effort_model_params={"max_iter":2000,
        "class_weight":"balanced",
        "solver":"saga",
        "n_jobs":-1},
    openness_model_params={"max_iter":1000,
            "class_weight":"balanced",
            "random_state":42}
)

## Evaluation config
evaluation_config = ModelEvaluationConfig(

    evaluation_artifact_dir="ml/artifacts/post_quality_feature/evaluation",

    effort_metrics_path="ml/artifacts/post_quality_feature/evaluation/effort_metrics.json",
    openness_metrics_path="ml/artifacts/post_quality_feature/evaluation/openness_metrics.json",

    effort_errors_path="ml/artifacts/post_quality_feature/evaluation/effort_errors.csv",
    openness_errors_path="ml/artifacts/post_quality_feature/evaluation/openness_errors.csv"
)

## Running ingestion
ingestion = DataIngestion(ingestion_config)
ingestion_artifact = ingestion.ingest_data()

## Running Validation
validation = DataValidation(validation_config,ingestion_artifact)
validation_artifact = validation.validate_data()

## Running Transformation
transformation = DataTransformation(config=transformation_config, validation_artifact=validation_artifact)
transformation_artifact = transformation.transform_data()

## Running trainer
trainer = ModelTrainer(
    config=trainer_config,
    transformation_artifact=transformation_artifact
)

trainer_artifact = trainer.train_models()

## RUnning evaluation
evaluation = ModelEvaluation(config=evaluation_config,trainer_artifact=trainer_artifact,transformation_artifact=transformation_artifact)

evaluation_artifact = evaluation.evaluate_models()

print("Evaluation completed")