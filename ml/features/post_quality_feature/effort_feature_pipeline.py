import joblib
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

from ml.features.post_quality_feature.effort_features import generate_effort_features

class EffortFeaturePipeline:
    def __init__(self,tfidf_path,scaler_path, embedding_model_name):
        self.vectorizer = joblib.load(tfidf_path)
        self.scaler = joblib.load(scaler_path)

        self.embedding_model = SentenceTransformer(embedding_model_name)

    def create_text(self, title, body):
        return title + " "+ body
    
    def compute_embedding(self,text):
        embedding = self.embedding_model.encode([text],batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True,)
        return embedding
    
    def compute_tfidf(self,text):
        tfidf = self.vectorizer.transform([text])

        return tfidf.toarray()
    
    def compute_structural_feature(self,title,body):
        df = pd.DataFrame({
            "title": [title],
            "body": [body]
        })

        df["text"] = df["title"] + " " + df["body"]
        df = generate_effort_features(df)
        drop_cols = [
            "title","body","text","id",
            "openness","effort","is_confident",
            "subreddit","tag","combined_text"
        ]

        numerical = df.drop(columns=drop_cols,errors='ignore')
        return numerical.values
    
    def transform(self,title,body):
        text = self.create_text(title=title,body=body)

        tfidf = self.compute_tfidf(text=text)

        embedding = self.compute_embedding(text=text)

        structural = self.compute_structural_feature(title=title,body=body)

        combined = np.hstack([structural,embedding])

        combined_scaled = self.scaler.transform(combined)

        final_feature = np.hstack([tfidf,combined_scaled])

        return final_feature
    