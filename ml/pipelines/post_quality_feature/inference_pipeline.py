import joblib

from ml.features.post_quality_feature.effort_feature_pipeline import EffortFeaturePipeline
from ml.features.post_quality_feature.openness_feature_pipeline import OpennessFeaturePipeline
from ml.entity.post_quality_feature.config_entity import InferenceConfig

class InferencePipeline:
    def __init__(self,config:InferenceConfig):
        self.effort_pipeline = EffortFeaturePipeline(
            tfidf_path=config.effortInferenceConfig.tfidf_path,
            scaler_path=config.effortInferenceConfig.scaler_path,
            embedding_model_name=config.effortInferenceConfig.embedding_model_name
        )

        self.openness_pipeline = OpennessFeaturePipeline(
            embedding_model_name=config.opennessInferenceConfig.embedding_model_name

        )

        self.effort_model = joblib.load(config.effort_model_path)

        self.openness_model = joblib.load(config.openness_model_path)

    def predict(self,title,body):
        effort_features = self.effort_pipeline.transform(title=title,body=body)
        openness_feature = self.openness_pipeline.transform(title=title,body=body)
        effort = self.effort_model.predict(effort_features)[0]
        openness = self.openness_model.predict(openness_feature)[0]

        score = 2 * openness + effort

        return {
            "effort" : int(effort),
            "openness":int(openness),
            "score": int(score)
        }
        