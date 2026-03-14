import os
import numpy as np
import pandas as pd
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

from ml.features.post_quality_feature.effort_features import generate_effort_features

from ml.entity.post_quality_feature.config_entity import DataTransformationConfig
from ml.entity.post_quality_feature.artifact_entity import DataValidationArtifact,DataTransformationArtifact,EffortDataTransformationArtifact,OpennessDataTransformationArtifact
from ml.utils.post_quality_feature.utils import create_combined_text,create_embeddings

class DataTransformation:

    def __init__(self, config: DataTransformationConfig, validation_artifact: DataValidationArtifact):
        self.config = config
        self.validation_artifact = validation_artifact

    def load_data(self)->pd.DataFrame:
        df = pd.read_csv(self.validation_artifact.validated_dataset_path)
        return df
    
    def create_tfidf_features(self, train_text,test_text):

        vectorizer = TfidfVectorizer(
            ngram_range=(1,1),
            min_df=self.config.tfidf_min_df,
            max_features=self.config.tfidf_max_features,
            stop_words='english'
        )

        X_train = vectorizer.fit_transform(train_text)
        X_test = vectorizer.transform(test_text)

        ## Make that directory if not exist
        os.makedirs(os.path.dirname(self.config.tfidf_vectorizer_path), exist_ok=True)


        joblib.dump(
            vectorizer,
            self.config.tfidf_vectorizer_path
        )

        return X_train,X_test
    
    def process_numerical_features(self, train_df:pd.DataFrame, test_df:pd.DataFrame):
        numerical_cols = train_df.columns.tolist()

        scaler = StandardScaler()

        X_train = scaler.fit_transform(train_df[numerical_cols])
        X_test = scaler.transform(test_df[numerical_cols])

        os.makedirs(os.path.dirname(self.config.scaler_path), exist_ok=True)

        joblib.dump(
            scaler,
            self.config.scaler_path
        )

        return X_train,X_test
        
    def transform_effort_data(self, train_df:pd.DataFrame, test_df:pd.DataFrame,embed_train,embed_test) -> EffortDataTransformationArtifact:

        print("Started effort transformation")

        ## Generate features
        print("Generating effort features")

        train_df = generate_effort_features(train_df)
        test_df = generate_effort_features(test_df)

        print(f"Generated features: {train_df.columns}")

        ## Define columns to drop
        drop_cols = ['title','body','text','id','openness','effort','is_confident','subreddit','tag','combined_text']

        ## Get numerical feature columns
        numerical_columns = train_df.drop(columns=drop_cols,errors='ignore').columns

        print(f"Numerical Features: {numerical_columns}")

        ## Labels
        y_train = train_df["effort"]
        y_test = test_df["effort"]

        ## Text features
        X_train_text = train_df["text"]
        X_test_text = test_df["text"]

        ## Numerical features
        X_train_num = train_df[numerical_columns]
        X_test_num = test_df[numerical_columns]

        print(f"Text Train Shape: {X_train_text.shape}, Test Shape: {X_test_text.shape}")
        print(f"Num Train Shape: {X_train_num.shape}, Test Shape: {X_test_num.shape}")

        ## TF-IDF
        tfidf_train, tfidf_test = self.create_tfidf_features(X_train_text, X_test_text)

        print(f"TF-IDF train shape: {tfidf_train.shape}, test shape: {tfidf_test.shape}")

        ## Embedding including
        print("Using embedding for effort model....")


        print(f"Embedding train shape: {embed_train.shape}")
        print(f"Embedding test shape: {embed_test.shape}")

        ## Combining numerical + embedding
        combined_train = np.hstack([X_train_num.values, embed_train])
        combined_test = np.hstack([X_test_num.values, embed_test])

        print(f"Combined numerical+embedding train: {combined_train.shape}")
        print(f"Combined numerical+embedding test: {combined_test.shape}")

        ## Scaling both nums + embed
        scaler = StandardScaler()

        combined_train_scaled = scaler.fit_transform(combined_train)
        combined_test_scaled = scaler.transform(combined_test)

        os.makedirs(os.path.dirname(self.config.scaler_path), exist_ok=True)

        joblib.dump(
            scaler,
            self.config.scaler_path
        )

        print("Scaling complete")

        ## Feature concatenation
        X_train = np.hstack([tfidf_train.toarray(), combined_train_scaled])
        X_test = np.hstack([tfidf_test.toarray(), combined_test_scaled])

        print(f"Final X_train: {X_train.shape}")
        print(f"Final X_test: {X_test.shape}")

        ## Save artifacts
        os.makedirs(self.config.transformation_artifact_dir, exist_ok=True)

        np.save(self.config.effort_feature_train_path, X_train)
        np.save(self.config.effort_feature_test_path, X_test)

        np.save(self.config.effort_labels_train_path, y_train)
        np.save(self.config.effort_labels_test_path, y_test)

        return EffortDataTransformationArtifact(
            effort_features_train_path=self.config.effort_feature_train_path,
            effort_features_test_path=self.config.effort_feature_test_path,
            effort_labels_train_path=self.config.effort_labels_train_path,
            effort_labels_test_path=self.config.effort_labels_test_path,
            tfidf_vectorizer_path=self.config.tfidf_vectorizer_path,
            scaler_path=self.config.scaler_path
        )

    def transform_openness_data(self,train_df:pd.DataFrame, test_df:pd.DataFrame, embed_train, embed_test)->OpennessDataTransformationArtifact:
        
        print("Started openness transformation")
        
        X_train = embed_train
        X_test = embed_test

        y_train = train_df["openness"]
        y_test = test_df["openness"]

        os.makedirs(
            os.path.dirname(self.config.openness_feature_train_path),
            exist_ok=True
        )

        np.save(self.config.openness_feature_train_path, X_train)
        np.save(self.config.openness_feature_test_path, X_test)

        np.save(self.config.openness_labels_train_path, y_train)
        np.save(self.config.openness_labels_test_path, y_test)

        print(
            f"Openness features saved: "
            f"train {X_train.shape}, test {X_test.shape}"
        )

        return OpennessDataTransformationArtifact(
            openness_features_train_path=self.config.openness_feature_train_path,
            openness_features_test_path=self.config.openness_feature_test_path,
            openness_labels_train_path=self.config.openness_labels_train_path,
            openness_labels_test_path=self.config.openness_labels_test_path
        )


        



    def transform_data(self)->DataTransformationArtifact:
        print("Loading validated data")

        df = self.load_data()

        train_df, test_df = train_test_split(
            df,
            test_size=self.config.test_size,
            random_state=self.config.random_state,
            stratify=df['effort']
        )

        print(
        f"Train shape: {train_df.shape}, "
        f"Test shape: {test_df.shape}"
        )

        print("Creating combined text for embedding")

        train_df = create_combined_text(train_df)
        test_df = create_combined_text(test_df)

        train_text = train_df["combined_text"].tolist()
        test_text = test_df["combined_text"].tolist()

        print("Generating embeddings once for both models")

        embed_train = create_embeddings(
            texts=train_text,
            embed_model_name=self.config.embedding_model_name
        )

        embed_test = create_embeddings(
            texts=test_text,
            embed_model_name=self.config.embedding_model_name
        )

        print(f"Embedding train shape: {embed_train.shape}")
        print(f"Embedding test shape: {embed_test.shape}")

        ## Run effort
        effort_artifact = self.transform_effort_data(train_df=train_df.copy(),test_df=test_df.copy(),embed_train=embed_train, embed_test=embed_test)

        ## Run openness
        openness_artifact = self.transform_openness_data(train_df=train_df.copy(),test_df=test_df.copy(),embed_train=embed_train, embed_test=embed_test)

        return DataTransformationArtifact(
            effortDataTransformationArtifact=effort_artifact,
            opennessDataTransformationArtifact=openness_artifact
        )

