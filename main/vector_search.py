from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
from main.places.models import DiningPlace


class DiningPlaceVectorSearch:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.place_ids = []

    def build_index(self):
        """Build the FAISS index from all dining places in the database"""
        dining_places = DiningPlace.objects.exclude(description='').exclude(rating=0)
        descriptions = []

        for place in dining_places:
            text_for_embedding = f"{place.description}"
            descriptions.append(text_for_embedding)
            self.place_ids.append(place.id)

        embeddings = self.model.encode(descriptions)

        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(np.array(embeddings).astype('float32'))

        return len(dining_places)

    def get_similar_places(self, place_ids, top_k=10, exclude_ids=None):
        """Find places similar to the given place IDs"""
        if exclude_ids is None:
            exclude_ids = []

        places = DiningPlace.objects.filter(id__in=place_ids)
        query_texts = []

        for place in places:
            query_texts.append(f"{place.description}")

        query_embeddings = self.model.encode(query_texts)

        avg_embedding = np.mean(query_embeddings, axis=0).reshape(1, -1).astype('float32')

        extra_k = top_k + len(exclude_ids) + len(place_ids)
        distances, indices = self.index.search(avg_embedding, min(extra_k, len(self.place_ids)))

        result_ids = []
        for idx in indices[0]:
            place_id = self.place_ids[idx]
            if place_id not in place_ids and place_id not in exclude_ids and len(result_ids) < top_k:
                result_ids.append(place_id)

        return result_ids