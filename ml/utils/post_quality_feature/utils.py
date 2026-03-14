import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer



def create_combined_text(df: pd.DataFrame):

    def make_text(row):

        title = row["title"].strip() if pd.notna(row["title"]) else ""
        body = row["body"].strip() if pd.notna(row["body"]) else ""

        if title and body:
            return f"Title: {title}\n\nBody: {body}"
        elif title:
            return f"Title: {title}"
        else:
            return body

    df["combined_text"] = df.apply(make_text, axis=1)

    return df


def create_embeddings(embed_model_name, texts):

    model = SentenceTransformer(embed_model_name)

    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True,
    )

    return np.array(embeddings)