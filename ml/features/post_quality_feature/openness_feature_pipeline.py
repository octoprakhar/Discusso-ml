import numpy as np
from sentence_transformers import SentenceTransformer

class OpennessFeaturePipeline:
    def __init__(self,embedding_model_name):
        self.embedding_model = SentenceTransformer(embedding_model_name)

    def create_text(self,title,body):
        return title + " "+ body
    
    def transform(self,title,body):
        text = self.create_text(title=title,body=body)

        embedding = self.embedding_model.encode([text],batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True,)

        return np.array(embedding)