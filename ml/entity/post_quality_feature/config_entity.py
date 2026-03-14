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

@dataclass
class DataTransformationConfig:

    transformation_artifact_dir: str

    ## Effort
    tfidf_vectorizer_path: str
    scaler_path: str

    effort_feature_train_path: str
    effort_feature_test_path: str

    effort_labels_train_path: str
    effort_labels_test_path: str

    ## Openness
    openness_feature_train_path: str
    openness_feature_test_path: str

    openness_labels_train_path: str
    openness_labels_test_path: str

    embedding_model_name: str = "all-MiniLM-L6-v2"

    test_size: float = 0.2
    random_state: int = 42

    tfidf_max_features: int = 3000
    tfidf_min_df: int = 5
