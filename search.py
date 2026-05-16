import pickle
import faiss
import numpy as np

from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from tensorflow.keras.preprocessing import image

model = ResNet50(weights='imagenet', include_top=False, pooling='avg')

def extract_features(img):
    img = img.resize((224, 224))
    img_array = np.array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)

    features = model.predict(img_array)
    return features.flatten()

def load_data():
    index = faiss.read_index('embeddings/faiss.index')

    with open('embeddings/filenames.pkl', 'rb') as f:
        img_paths = pickle.load(f)

    return index, img_paths

def search(query_img, top_k=5):
    index, img_paths = load_data()

    query = extract_features(query_img).astype('float32').reshape(1, -1)
    faiss.normalize_L2(query)

    scores, indices = index.search(query, top_k)

    results = [img_paths[i] for i in indices[0]]
    return results