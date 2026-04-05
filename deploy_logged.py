"""
Deploy ddx-env to HuggingFace Spaces.
Outputs everything to deploy_log.txt for visibility.
Run: python deploy_logged.py YOUR_HF_TOKEN
"""
import sys
import os

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "deploy_log.txt")

def log(msg):
    print(msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

# Clear log
with open(LOG_FILE, "w", encoding="utf-8") as f:
    f.write("=== DDx Deploy Log ===\n")

if len(sys.argv) < 2:
    log("ERROR: Pass token as argument: python deploy_logged.py YOUR_TOKEN")
    sys.exit(1)

token = sys.argv[1].strip()
log(f"Token prefix: {token[:8]}...")

try:
    from huggingface_hub import HfApi
    log("huggingface_hub imported OK")
except ImportError as e:
    log(f"Import error: {e}")
    sys.exit(1)

repo_id = "niaz9246/ddx-env"
repo_type = "space"
api = HfApi(token=token)

log(f"\nChecking/creating space: {repo_id}")
try:
    info = api.repo_info(repo_id=repo_id, repo_type=repo_type)
    log(f"Space exists: {info.id}")
except Exception as e:
    log(f"Repo info error ({type(e).__name__}): {e}")
    log("Attempting to create space...")
    try:
        result = api.create_repo(
            repo_id=repo_id,
            repo_type=repo_type,
            space_sdk="docker",
            private=False,
        )
        log(f"Space created: {result}")
    except Exception as e2:
        log(f"Create error ({type(e2).__name__}): {e2}")
        log("Will attempt uploads anyway...")

script_dir = os.path.dirname(os.path.abspath(__file__))
files = [
    (os.path.join(script_dir, "Dockerfile"), "Dockerfile"),
    (os.path.join(script_dir, "README.md"), "README.md"),
    (os.path.join(script_dir, "openenv.yaml"), "openenv.yaml"),
    (os.path.join(script_dir, "src", "envs", "ddx_env", "__init__.py"), "src/envs/ddx_env/__init__.py"),
    (os.path.join(script_dir, "src", "envs", "ddx_env", "client.py"), "src/envs/ddx_env/client.py"),
    (os.path.join(script_dir, "src", "envs", "ddx_env", "server", "__init__.py"), "src/envs/ddx_env/server/__init__.py"),
    (os.path.join(script_dir, "src", "envs", "ddx_env", "server", "cases.py"), "src/envs/ddx_env/server/cases.py"),
    (os.path.join(script_dir, "src", "envs", "ddx_env", "server", "environment.py"), "src/envs/ddx_env/server/environment.py"),
    (os.path.join(script_dir, "src", "envs", "ddx_env", "server", "app.py"), "src/envs/ddx_env/server/app.py"),
]

log("\nUploading files:")
success = 0
for local_path, repo_path in files:
    if os.path.exists(local_path):
        try:
            api.upload_file(
                path_or_fileobj=local_path,
                path_in_repo=repo_path,
                repo_id=repo_id,
                repo_type=repo_type,
            )
            log(f"  OK: {repo_path}")
            success += 1
        except Exception as e:
            log(f"  FAIL: {repo_path} — {type(e).__name__}: {e}")
    else:
        log(f"  MISSING: {local_path}")

log(f"\n{success}/{len(files)} files uploaded.")
log(f"\nDone!")
log(f"  Space: https://huggingface.co/spaces/{repo_id}")
log(f"  Health: https://niaz9246-ddx-env.hf.space/health")
log(f"  Docs: https://niaz9246-ddx-env.hf.space/docs")
