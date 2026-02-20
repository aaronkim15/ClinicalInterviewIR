from sentence_transformers import SentenceTransformer
from typing import List

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embeddings(texts:List[str]) -> List[List[float]]:
    embeddings = embedding_model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True
    )
    return embeddings.tolist()