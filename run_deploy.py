import sys, os
sys.stdout = open('deploy_log.txt', 'w', buffering=1)
sys.stderr = sys.stdout

print("=== DDx Deploy Starting ===")
sys.stdout.flush()

token = os.getenv("HF_TOKEN")
if not token:
    print("ERROR: Please set the HF_TOKEN environment variable.")
    sys.exit(1)
    
print(f"Token loaded securely from environment...")

from huggingface_hub import HfApi
api = HfApi(token=token)
print("HfApi initialized")
sys.stdout.flush()

repo_id = "niaz9246/ddx-env"
repo_type = "space"

# Create space
print(f"Creating space {repo_id}...")
try:
    info = api.repo_info(repo_id=repo_id, repo_type=repo_type)
    print(f"Space exists: {info.id}")
except Exception as e:
    print(f"Not found ({type(e).__name__}), creating...")
    try:
        r = api.create_repo(repo_id=repo_id, repo_type=repo_type, space_sdk="docker", private=False)
        print(f"Created: {r}")
    except Exception as e2:
        print(f"Create err: {e2}")
sys.stdout.flush()

d = os.path.dirname(os.path.abspath(__file__))
files = [
    (os.path.join(d,"Dockerfile"),"Dockerfile"),
    (os.path.join(d,"README.md"),"README.md"),
    (os.path.join(d,"pyproject.toml"),"pyproject.toml"),
    (os.path.join(d,"openenv.yaml"),"openenv.yaml"),
    (os.path.join(d,"src","envs","ddx_env","__init__.py"),"src/envs/ddx_env/__init__.py"),
    (os.path.join(d,"src","envs","ddx_env","client.py"),"src/envs/ddx_env/client.py"),
    (os.path.join(d,"src","envs","ddx_env","server","__init__.py"),"src/envs/ddx_env/server/__init__.py"),
    (os.path.join(d,"src","envs","ddx_env","server","environment.py"),"src/envs/ddx_env/server/environment.py"),
    (os.path.join(d,"src","envs","ddx_env","server","cases.py"),"src/envs/ddx_env/server/cases.py"),
    (os.path.join(d,"src","envs","ddx_env","server","app.py"),"src/envs/ddx_env/server/app.py"),
    (os.path.join(d,"src","envs","ddx_env","server","ui.py"),"src/envs/ddx_env/server/ui.py"),
    (os.path.join(d,"inference.py"),"inference.py"),
]

ok = 0
for lp, rp in files:
    if os.path.exists(lp):
        try:
            api.upload_file(path_or_fileobj=lp, path_in_repo=rp, repo_id=repo_id, repo_type=repo_type)
            print(f"OK: {rp}")
            ok += 1
        except Exception as e:
            print(f"FAIL {rp}: {e}")
    else:
        print(f"MISSING: {lp}")
    sys.stdout.flush()

print(f"\nDone: {ok}/{len(files)} uploaded")
print(f"Space: https://huggingface.co/spaces/{repo_id}")
print(f"Health: https://niaz9246-ddx-env.hf.space/health")
sys.stdout.flush()
