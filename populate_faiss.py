import numpy as np
import faiss
from sklearn.preprocessing import normalize
from transformers import AutoTokenizer, AutoModel
import torch
from typing import List

class ImageFaiss(): 
    def __init__(self):
        #making embedding models
        model_name = "distilbert-base-uncased"  # Use a model suitable for structured data
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name) 
        self.embedding_dim = 768  # Reduce the embedding dimension for small data
        self.index = faiss.IndexFlatL2(self.embedding_dim)

    def _get_text_preprocessing(self, response : dict, weights : dict) : 
        """
        preprocessing text to remove unnecessary words from product description 
        kwargs define weights for different categories 
        """
        #each element corresponds to different category
        input_string = ""
        for key in response.keys(): 
            weight = weights[key] if key in weights.keys() else 0
            for _ in range(weight):
                if isinstance(response[key], list): 
                    for val in response[key]: 
                        input_string += val + ' ' 
                else:
                    input_string += str(response[key]) + ' '
        print(input_string)
        return input_string

    #func to be called on each product string
    def get_text_embedding(self, \
        input_text: str, \
        weights : dict = {
            'gender' : 2, 
            'articleType' : 5, 
            'baseColour' : 3, 
            'season' : 1, 
            'brand' : 2
        }): 

        if isinstance(input_text, dict):
            input_text = self._get_text_preprocessing(input_text, weights) 
        
        inputs = self.tokenizer(input_text, return_tensors='pt', padding=True, truncation=True) 
        with torch.no_grad(): 
            outputs = self.model(**inputs) 
            embeddings = outputs.last_hidden_state.mean(dim=1)
        
        text_embedding = embeddings.numpy() 
        normalized_embedding = normalize(text_embedding, norm='l2', axis=1)
        print('Text embedding created')
        return normalized_embedding

    def populate_faiss(self, file_path:str = "./embeddings.txt"): 
        #getting each prod string to make embedding
        with open(file_path, 'r') as file: 
            content = file.read() 

        #creating faiss instance

        #for each product get embedding and push into index
        products = content.strip().split('\n\n') 
        for product in products[:]:  
            text_embedding = self.get_text_embedding(product) 
            print(text_embedding.shape) 
            self.index.add(text_embedding) 

        #write to disk
        faiss.write_index(self.index, "product_embeddings.index")
        print("Faiss index created")
    
    def _load_faiss_index(self, index_path : str): 
        index = faiss.read_index(index_path)               
        return index
    
    def get_k_similar(self, k : int, text, threshhold : float = 0.5) -> List[str]:
        """k -> number of similar to consider 
        text -> query for which to find similar might be dict (llm parsed) or str
        threshhold -> cosine similarity threshhold"""
        text_embedding = self.get_text_embedding(text) 
        text_embedding = normalize(text_embedding, norm = 'l2', axis=1)
        index = self._load_faiss_index("./product_embeddings.index")
        distances, indices = index.search(text_embedding, k)

        print(distances, indices)

        with open('./embeddings.txt', 'r') as file: 
            content = file.read() 
            
        products = content.strip().split('\n\n')
        closest_prods = []
        for dist, idx in zip(distances[0], indices[0]): 
            nearest_prod_desc = products[idx]
            similarity_score = 1/ (1 + dist)
            if similarity_score >= threshhold : 
                closest_prods.append(nearest_prod_desc) 
        
        return closest_prods
    
def copy_images_to_matches(prod_desc):
    for prod in prod_desc : 
        id = prod.split('\n')[0].split(' : ')[-1]
        import shutil
        print(prod, id) 
        source_path = f'./images/{id}.jpg'
        destination_path = f'./matches/{id}.jpg'

        # Copy the file
        shutil.copy(source_path, destination_path)
        
