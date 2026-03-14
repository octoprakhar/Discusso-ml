import os
import numpy as np
import joblib

from sklearn.linear_model import LogisticRegression

from ml.entity.post_quality_feature.config_entity import ModelTrainerConfig
from ml.entity.post_quality_feature.artifact_entity import DataTransformationArtifact, ModelTrainerArtifact

class ModelTrainer:
    
    def __init__(self, config:ModelTrainerConfig, transformation_artifact: DataTransformationArtifact):
        self.config = config
        self.transformation_artifact = transformation_artifact

    def train_effort_model(self):
        print("Loading effort training data")
        print("Training effort model with parameters: ")
        print(self.config.effort_model_params)

        effort_artifact = self.transformation_artifact.effortDataTransformationArtifact

        X_train = np.load(effort_artifact.effort_features_train_path)
        y_train = np.load(effort_artifact.effort_labels_train_path)

        X_test = np.load(effort_artifact.effort_features_test_path)
        y_test = np.load(effort_artifact.effort_labels_test_path)

        print(f"Effort train shape: {X_train.shape}")

        model = LogisticRegression(**self.config.effort_model_params)

        print("Training effort model")

        model.fit(X_train,y_train)

        return model

    def train_openness_model(self):
        print("Loading openness training data")
        print("Training openness model with parameters: ")
        print(self.config.openness_model_params)

        openness_artifact = self.transformation_artifact.opennessDataTransformationArtifact

        X_train = np.load(openness_artifact.openness_features_train_path)
        y_train = np.load(openness_artifact.openness_labels_train_path)

        X_test = np.load(openness_artifact.openness_features_test_path)
        y_test = np.load(openness_artifact.openness_labels_test_path)

        print(f"Openness train shape: {X_train.shape}")

        model = LogisticRegression(**self.config.openness_model_params)

        model.fit(X_train,y_train)

        return model

    def save_models(self,effort_model, openness_model):
        os.makedirs(self.config.model_artifact_dir,exist_ok=True)

        joblib.dump(
            effort_model,
            self.config.effort_model_path
        )

        joblib.dump(
            openness_model,
            self.config.openness_model_path
        )

        print("Models saved successfully")
    
    def train_models(self) -> ModelTrainerArtifact:
        effort_model = self.train_effort_model()
        openness_model = self.train_openness_model()

        self.save_models(effort_model,openness_model)

        return ModelTrainerArtifact(
            effort_model_path=self.config.effort_model_path,
            openness_model_path=self.config.openness_model_path
        )