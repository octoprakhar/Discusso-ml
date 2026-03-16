import os
import json
import numpy as np
import joblib
import pandas as pd

from sklearn.metrics import accuracy_score,precision_score,recall_score,f1_score

from ml.entity.post_quality_feature.config_entity import ModelEvaluationConfig
from ml.entity.post_quality_feature.artifact_entity import ModelEvaluationArtifact,ModelTrainerArtifact,DataTransformationArtifact

class ModelEvaluation:
    def __init__(self,config:ModelEvaluationConfig, trainer_artifact: ModelTrainerArtifact, transformation_artifact: DataTransformationArtifact):
        self.config = config
        self.trainer_artifact = trainer_artifact
        self.transformation_artifact = transformation_artifact

    def compute_metrics(self,y_true,y_pred):
        metrics = {
            "accuracy": float(accuracy_score(y_true, y_pred)),
            "precision": float(precision_score(y_true, y_pred, average="binary")),
            "recall": float(recall_score(y_true, y_pred, average="binary")),
            "f1": float(f1_score(y_true, y_pred, average="binary"))
        }

        return metrics

    def evaluate_effort_model(self):
        print("Evaluating Effort Model")
        effort_artifact = self.transformation_artifact.effortDataTransformationArtifact

        X_test = np.load(effort_artifact.effort_features_test_path)
        y_test = np.load(effort_artifact.effort_labels_test_path)

        model = joblib.load(self.trainer_artifact.effort_model_path)

        y_pred = model.predict(X_test)

        metrics = self.compute_metrics(y_test,y_pred)

        errors = pd.DataFrame({
            "true_label":y_test,
            "predicted_label":y_pred
        })

        errors = errors[errors.true_label != errors.predicted_label]

        return metrics,errors
    
    def evaluate_openness_model(self):
        print("Evaluating openness model")

        openness_artifact = self.transformation_artifact.opennessDataTransformationArtifact

        X_test = np.load(openness_artifact.openness_features_test_path)
        y_test = np.load(openness_artifact.openness_labels_test_path)

        model = joblib.load(self.trainer_artifact.openness_model_path)

        y_pred = model.predict(X_test)

        metrics = self.compute_metrics(y_test, y_pred)

        errors = pd.DataFrame({
            "true_label": y_test,
            "predicted_label": y_pred
        })

        errors = errors[errors.true_label != errors.predicted_label]

        original_df = pd.read_csv(
        self.transformation_artifact.effortDataTransformationArtifact.original_test_data_path
        )

        wrong_idx = errors.index

        error_posts = original_df.iloc[wrong_idx].copy()

        error_posts["true_label"] = y_test[wrong_idx]
        error_posts["predicted_label"] = y_pred[wrong_idx]

        return metrics, errors
    
    def save_results(self, effort_metrics, effort_errors, openness_metrics, openness_errors):

        os.makedirs(self.config.evaluation_artifact_dir, exist_ok=True)

        with open(self.config.effort_metrics_path, "w") as f:
            json.dump(effort_metrics, f, indent=4)

        with open(self.config.openness_metrics_path, "w") as f:
            json.dump(openness_metrics, f, indent=4)

        effort_errors.to_csv(self.config.effort_errors_path, index=False)
        openness_errors.to_csv(self.config.openness_errors_path, index=False)



    def evaluate_models(self) -> ModelEvaluationArtifact:
        effort_metrics, effort_errors = self.evaluate_effort_model()
        
        openness_metrics, openness_errors = self.evaluate_openness_model()

        self.save_results(
            effort_metrics,
            effort_errors,
            openness_metrics,
            openness_errors
        )

        return ModelEvaluationArtifact(
            effort_metrics_path=self.config.effort_metrics_path,
            openness_metrics_path=self.config.openness_metrics_path,
            effort_errors_path=self.config.effort_errors_path,
            openness_errors_path=self.config.openness_errors_path
        )