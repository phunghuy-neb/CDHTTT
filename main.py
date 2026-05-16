import os
import numpy as np
import pickle
import faiss

from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from tensorflow.keras.preprocessing import image

model = ResNet50(weights='imagenet', include_top=False, pooling='avg')

def extract_features(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)

    features = model.predict(img_array)
    return features.flatten()

def build_faiss_index(data_path):
    img_paths = []
    features = []

    for root, _, files in os.walk(data_path):
        for file in files:
            if file.lower().endswith(('.jpg', '.png', '.jpeg')):
                path = os.path.join(root, file)
                img_paths.append(path)
                features.append(extract_features(path))

    features = np.array(features).astype('float32')
    faiss.normalize_L2(features)

    index = faiss.IndexFlatIP(features.shape[1])
    index.add(features)

    os.makedirs('embeddings', exist_ok=True)

    faiss.write_index(index, 'embeddings/faiss.index')

    with open('embeddings/filenames.pkl', 'wb') as f:
        pickle.dump(img_paths, f)

    print(f"✅ Indexed {len(img_paths)} images")

if __name__ == "__main__":
    build_faiss_index("data/")