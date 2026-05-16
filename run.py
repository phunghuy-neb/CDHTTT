"""
One-command launcher: install deps → build missing indexes → launch app.
Usage:  python run.py
"""
import os
import sys
import subprocess
import time

SEP = "=" * 58

def step(n, total, msg):
    print(f"\n[{n}/{total}] {msg}")

def index_exists(model_name):
    new = f'embeddings/{model_name}/faiss.index'
    old = 'embeddings/faiss.index'
    if os.path.exists(new):
        return True
    if model_name == 'resnet50' and os.path.exists(old):
        return True
    return False

def run(cmd, **kwargs):
    result = subprocess.run(cmd, **kwargs)
    if result.returncode != 0:
        print(f"\n  ✖  Command failed: {' '.join(str(c) for c in cmd)}")
        sys.exit(result.returncode)
    return result

def main():
    print(SEP)
    print("  VisualSearch AI  —  Auto Setup & Launch")
    print(SEP)

    # ── Step 1: Install dependencies ────────────────────────────
    step(1, 3, "Installing / verifying dependencies ...")
    run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt',
         '--disable-pip-version-check'])

    # torch needs a special CPU-only wheel URL on Windows to avoid ~2 GB CUDA download
    try:
        import torch  # noqa: F401
    except ImportError:
        print("  Installing PyTorch (CPU) ...")
        run([sys.executable, '-m', 'pip', 'install', 'torch',
             '--index-url', 'https://download.pytorch.org/whl/cpu', '-q',
             '--disable-pip-version-check'])

    print("  ✅ All packages ready")

    # ── Step 2: Build missing FAISS indexes ─────────────────────
    step(2, 3, "Checking FAISS indexes ...")

    MODELS = ['resnet50', 'mobilenetv2', 'vit']
    ESTIMATES = {'resnet50': '~5 min', 'mobilenetv2': '~4 min', 'vit': '~20 min (+ ~330 MB download on first run)'}

    missing = [m for m in MODELS if not index_exists(m)]

    if not missing:
        print("  ✅ All indexes found — skipping build")
    else:
        print(f"  Missing indexes: {', '.join(missing)}")
        for m in missing:
            print(f"\n  Building [{m}]  (estimated {ESTIMATES[m]}) ...")
            t0 = time.time()
            run([sys.executable, 'main.py', m])
            elapsed = int(time.time() - t0)
            print(f"  ✅ [{m}] finished in {elapsed//60}m {elapsed%60}s")

    # ── Step 3: Launch Streamlit ─────────────────────────────────
    step(3, 3, "Launching Streamlit app ...")
    print("  Open  http://localhost:8501  in your browser")
    print("  Press  Ctrl + C  to stop\n")
    print(SEP + "\n")

    subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'app.py',
                    '--server.headless', 'false'])

if __name__ == '__main__':
    main()
