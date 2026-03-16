import os

from ml.entity.post_quality_feature.config_entity import DataIngestionConfig,DataValidationConfig,DataTransformationConfig,ModelTrainerConfig,ModelEvaluationConfig, EffortInferenceConfig,OpennessInferenceConfig,InferenceConfig

class ConfigurationManager:
    def __init__(self):
        self.artifact_root = "ml/artifacts/post_quality_feature"
        os.makedirs(self.artifact_root,exist_ok=True)

    def get_data_ingestion_config(self):
        return DataIngestionConfig(
            raw_data_path="data/post_quality/raw/post_data_v4.json",
            ingestion_artifact_dir=f"{self.artifact_root}/ingestion"
        )
    
    def get_data_validation_config(self):
        return DataValidationConfig(
            validation_artifact_dir=f"{self.artifact_root}/validation",
            validation_report_path=f"{self.artifact_root}/validation/validation_report.json",
            required_columns=["id","title","body","effort","openness","is_confident","subreddit"]
        )
    
    def get_data_trasformation_config(self):
        return DataTransformationConfig(

            transformation_artifact_dir=f"{self.artifact_root}/transformation",

            # Effort
            tfidf_vectorizer_path=f"{self.artifact_root}/transformation/effort/tfidf.pkl",
            scaler_path=f"{self.artifact_root}/transformation/effort/scaler.pkl",
            effort_feature_train_path=f"{self.artifact_root}/transformation/effort/X_train.npy",
            effort_feature_test_path=f"{self.artifact_root}/transformation/effort/X_test.npy",
            effort_labels_train_path=f"{self.artifact_root}/transformation/effort/y_train.npy",
            effort_labels_test_path=f"{self.artifact_root}/transformation/effort/y_test.npy",

            # Openness
            openness_feature_train_path=f"{self.artifact_root}/transformation/openness/X_train.npy",
            openness_feature_test_path=f"{self.artifact_root}/transformation/openness/X_test.npy",
            openness_labels_train_path=f"{self.artifact_root}/transformation/openness/y_train.npy",
            openness_labels_test_path=f"{self.artifact_root}/transformation/openness/y_test.npy"
        )
    
    def get_model_trainer_config(self):
        return ModelTrainerConfig(
                model_artifact_dir=f"{self.artifact_root}/model",

                effort_model_path=f"{self.artifact_root}/model/effort_model.pkl",
                openness_model_path=f"{self.artifact_root}/model/openness_model.pkl",

                effort_model_params={"max_iter":2000,
                    "class_weight":"balanced",
                    "solver":"saga",
                    "n_jobs":-1},
                openness_model_params={"max_iter":1000,
                        "class_weight":"balanced",
                        "random_state":42}
            )
    
    def get_model_evaluation_config(self):
        return ModelEvaluationConfig(

            evaluation_artifact_dir=f"{self.artifact_root}/evaluation",

            effort_metrics_path=f"{self.artifact_root}/evaluation/effort_metrics.json",
            openness_metrics_path=f"{self.artifact_root}/evaluation/openness_metrics.json",

            effort_errors_path=f"{self.artifact_root}/evaluation/effort_errors.csv",
            openness_errors_path=f"{self.artifact_root}/evaluation/openness_errors.csv"
        )
    
    def get_inference_config(self):
        effortInferenceConfig = EffortInferenceConfig(
            tfidf_path= f"{self.artifact_root}/transformation/effort/tfidf.pkl",
            scaler_path=f"{self.artifact_root}/transformation/effort/scaler.pkl")
            

        opennessInferenceConfig = OpennessInferenceConfig()

        return InferenceConfig(effortInferenceConfig=effortInferenceConfig,opennessInferenceConfig=opennessInferenceConfig,effort_model_path=f"{self.artifact_root}/model/effort_model.pkl",openness_model_path=f"{self.artifact_root}/model/openness_model.pkl")
    
