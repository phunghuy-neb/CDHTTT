import os
import sys
import numpy as np
import pickle
import faiss

BATCH = 32   # images per predict call for CNN models
BATCH_VIT = 8


def build_faiss_index(data_path, model_name='resnet50'):
    print(f"\n{'='*55}")
    print(f"  Building index  [{model_name.upper()}]")
    print(f"{'='*55}")

    all_paths = []
    for root, _, files in os.walk(data_path):
        for file in sorted(files):
            if file.lower().endswith(('.jpg', '.png', '.jpeg')):
                all_paths.append(os.path.join(root, file))
    print(f"  Found {len(all_paths)} images")

    # ── ResNet50 / MobileNetV2 (batched CNN) ──
    if model_name in ('resnet50', 'mobilenetv2'):
        if model_name == 'resnet50':
            from tensorflow.keras.applications import ResNet50
            from tensorflow.keras.applications.resnet50 import preprocess_input
            model = ResNet50(weights='imagenet', include_top=False, pooling='avg')
        else:
            from tensorflow.keras.applications import MobileNetV2
            from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
            model = MobileNetV2(weights='imagenet', include_top=False, pooling='avg')

        from tensorflow.keras.preprocessing import image as kimg

        img_paths, features = [], []
        for start in range(0, len(all_paths), BATCH):
            chunk = all_paths[start:start + BATCH]
            xs, valids = [], []
            for p in chunk:
                try:
                    img = kimg.load_img(p, target_size=(224, 224))
                    xs.append(kimg.img_to_array(img))
                    valids.append(p)
                except Exception as e:
                    print(f"  ⚠  Skipped {os.path.basename(p)}: {e}")

            if xs:
                batch_arr = preprocess_input(np.array(xs, dtype='float32'))
                feats = model.predict(batch_arr, verbose=0)
                features.extend(feats)
                img_paths.extend(valids)

            done = min(start + BATCH, len(all_paths))
            print(f"  Progress: {done:>4}/{len(all_paths)}  ({done*100//len(all_paths)}%)",
                  end='\r', flush=True)
        print()

    # ── ViT (batched Transformer) ──
    elif model_name == 'vit':
        import timm, torch
        from PIL import Image as PILImage

        print("  Loading ViT model (first run downloads ~350 MB) ...")
        model = timm.create_model('vit_base_patch16_224', pretrained=True, num_classes=0)
        model.eval()
        cfg = timm.data.resolve_model_data_config(model)
        transform = timm.data.create_transform(**cfg, is_training=False)
        print("  Model ready.")

        img_paths, features = [], []
        for start in range(0, len(all_paths), BATCH_VIT):
            chunk = all_paths[start:start + BATCH_VIT]
            tensors, valids = [], []
            for p in chunk:
                try:
                    img = PILImage.open(p).convert('RGB')
                    tensors.append(transform(img))
                    valids.append(p)
                except Exception as e:
                    print(f"  ⚠  Skipped {os.path.basename(p)}: {e}")

            if tensors:
                x = torch.stack(tensors)
                with torch.no_grad():
                    feats = model(x).numpy()
                features.extend(feats)
                img_paths.extend(valids)

            done = min(start + BATCH_VIT, len(all_paths))
            print(f"  Progress: {done:>4}/{len(all_paths)}  ({done*100//len(all_paths)}%)",
                  end='\r', flush=True)
        print()

    else:
        raise ValueError(f"Unknown model: {model_name}. Choices: resnet50, mobilenetv2, vit, all")

    # ── Save FAISS index ──
    features_arr = np.array(features, dtype='float32')
    faiss.normalize_L2(features_arr)

    index = faiss.IndexFlatIP(features_arr.shape[1])
    index.add(features_arr)

    out_dir = f'embeddings/{model_name}'
    os.makedirs(out_dir, exist_ok=True)
    faiss.write_index(index, f'{out_dir}/faiss.index')
    with open(f'{out_dir}/filenames.pkl', 'wb') as f:
        pickle.dump(img_paths, f)

    print(f"  ✅ Done — {len(img_paths)} images  →  {out_dir}/")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else 'all'
    models = ['resnet50', 'mobilenetv2', 'vit'] if target == 'all' else [target]
    for m in models:
        build_faiss_index("data/", m)
