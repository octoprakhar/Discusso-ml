from ml.components.post_quality_feature.data_ingestion import DataIngestion
from ml.components.post_quality_feature.data_validation import DataValidation
from ml.components.post_quality_feature.data_transformation import DataTransformation
from ml.components.post_quality_feature.model_trainer import ModelTrainer
from ml.components.post_quality_feature.model_evaluation import ModelEvaluation

from ml.config.post_quality_feature.configuration import ConfigurationManager

class TrainingPipeline:
    def __init__(self):
        self.config_manager = ConfigurationManager()

    def run_pipeline(self):
        print("Starting Training Pipeline")

        ingestion_config = self.config_manager.get_data_ingestion_config()
        validation_config = self.config_manager.get_data_validation_config()
        transformation_config = self.config_manager.get_data_trasformation_config()
        trainer_config = self.config_manager.get_model_trainer_config()
        evaluation_config = self.config_manager.get_model_evaluation_config()

        ingestion = DataIngestion(ingestion_config)
        ingestion_artifact = ingestion.ingest_data()

        validation = DataValidation(config=validation_config,ingestion_artifact=ingestion_artifact)
        validation_artifact = validation.validate_data()

        trasformation = DataTransformation(config=transformation_config,validation_artifact=validation_artifact)
        transformation_artifact = trasformation.transform_data()

        trainer = ModelTrainer(config=trainer_config,transformation_artifact=transformation_artifact)
        trainer_artifact = trainer.train_models()

        evaluation = ModelEvaluation(config=evaluation_config,trainer_artifact=trainer_artifact,transformation_artifact=transformation_artifact)
        evaluation.evaluate_models()

        print("Training Pipeline Completed")