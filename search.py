import os
import pickle
import faiss
import numpy as np

_models_cache = {}
_index_cache = {}


def _load_resnet50():
    if 'resnet50' not in _models_cache:
        from tensorflow.keras.applications import ResNet50
        from tensorflow.keras.applications.resnet50 import preprocess_input
        m = ResNet50(weights='imagenet', include_top=False, pooling='avg')
        _models_cache['resnet50'] = (m, preprocess_input)
    return _models_cache['resnet50']


def _load_mobilenetv2():
    if 'mobilenetv2' not in _models_cache:
        from tensorflow.keras.applications import MobileNetV2
        from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
        m = MobileNetV2(weights='imagenet', include_top=False, pooling='avg')
        _models_cache['mobilenetv2'] = (m, preprocess_input)
    return _models_cache['mobilenetv2']


def _load_vit():
    if 'vit' not in _models_cache:
        import timm, torch
        m = timm.create_model('vit_base_patch16_224', pretrained=True, num_classes=0)
        m.eval()
        cfg = timm.data.resolve_model_data_config(m)
        transform = timm.data.create_transform(**cfg, is_training=False)
        _models_cache['vit'] = (m, transform)
    return _models_cache['vit']


def extract_features(img, model_name='resnet50'):
    img_rgb = img.convert('RGB')

    if model_name == 'resnet50':
        model, preprocess_fn = _load_resnet50()
        x = np.array(img_rgb.resize((224, 224)), dtype=np.float32)
        x = np.expand_dims(x, axis=0)
        return model.predict(preprocess_fn(x), verbose=0).flatten()

    if model_name == 'mobilenetv2':
        model, preprocess_fn = _load_mobilenetv2()
        x = np.array(img_rgb.resize((224, 224)), dtype=np.float32)
        x = np.expand_dims(x, axis=0)
        return model.predict(preprocess_fn(x), verbose=0).flatten()

    if model_name == 'vit':
        import torch
        model, transform = _load_vit()
        x = transform(img_rgb).unsqueeze(0)
        with torch.no_grad():
            return model(x).numpy().flatten()

    raise ValueError(f"Unknown model: {model_name}")


def load_data(model_name='resnet50'):
    if model_name in _index_cache:
        return _index_cache[model_name]

    new_index = f'embeddings/{model_name}/faiss.index'
    new_pkl   = f'embeddings/{model_name}/filenames.pkl'
    old_index = 'embeddings/faiss.index'
    old_pkl   = 'embeddings/filenames.pkl'

    if os.path.exists(new_index):
        index_path, pkl_path = new_index, new_pkl
    elif model_name == 'resnet50' and os.path.exists(old_index):
        index_path, pkl_path = old_index, old_pkl
    else:
        raise FileNotFoundError(
            f"Index cho '{model_name}' chưa được tạo. "
            f"Chạy: python main.py {model_name}"
        )

    index = faiss.read_index(index_path)
    with open(pkl_path, 'rb') as f:
        img_paths = pickle.load(f)

    _index_cache[model_name] = (index, img_paths)
    return index, img_paths


def search(query_img, top_k=5, model_name='resnet50'):
    query = extract_features(query_img, model_name).astype('float32').reshape(1, -1)
    faiss.normalize_L2(query)
    index, img_paths = load_data(model_name)
    _, indices = index.search(query, top_k)
    return [img_paths[i] for i in indices[0]]
