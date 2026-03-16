from dataclasses import dataclass

@dataclass
class DataIngestionArtifact:
    dataset_path: str

@dataclass
class DataValidationArtifact:
    validated_dataset_path: str
    validation_status: bool


@dataclass
class EffortDataTransformationArtifact:

    effort_features_train_path: str
    effort_features_test_path: str

    effort_labels_train_path: str
    effort_labels_test_path: str

    tfidf_vectorizer_path: str
    scaler_path: str

@dataclass
class OpennessDataTransformationArtifact:
    openness_features_train_path: str
    openness_features_test_path: str

    openness_labels_train_path: str
    openness_labels_test_path: str

@dataclass
class DataTransformationArtifact:
    effortDataTransformationArtifact: EffortDataTransformationArtifact
    opennessDataTransformationArtifact: OpennessDataTransformationArtifact

@dataclass
class ModelTrainerArtifact:

    effort_model_path: str
    openness_model_path: str

@dataclass
class ModelEvaluationArtifact:
    effort_metrics_path: str
    openness_metrics_path: str

    effort_errors_path: str
    openness_errors_path: str