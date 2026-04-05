"""
Deploy ddx-env to Hugging Face Spaces using huggingface_hub Python API.

Usage:
    python deploy_to_hf.py YOUR_HF_TOKEN

Get your token from: https://huggingface.co/settings/tokens
(needs write permission)
"""

import os
import sys

def main():
    # Get token from args or env
    token = None
    if len(sys.argv) > 1:
        token = sys.argv[1].strip()
    else:
        token = os.environ.get("HF_TOKEN", "").strip()

    if not token:
        print("ERROR: No token provided.")
        print("Usage: python deploy_to_hf.py YOUR_HF_TOKEN")
        print("Get token from: https://huggingface.co/settings/tokens")
        sys.exit(1)

    print(f"Token received (first 8 chars): {token[:8]}...")

    try:
        from huggingface_hub import HfApi
    except ImportError:
        print("Installing huggingface_hub...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "huggingface_hub"])
        from huggingface_hub import HfApi

    repo_id = "niaz9246/ddx-env"
    repo_type = "space"

    api = HfApi(token=token)

    # Create space if it doesn't exist
    print(f"\nCreating/verifying space: {repo_id}")
    try:
        info = api.repo_info(repo_id=repo_id, repo_type=repo_type)
        print(f"Space already exists: {info.id}")
    except Exception as e:
        if "404" in str(e) or "not found" in str(e).lower() or "RepositoryNotFoundError" in str(type(e)):
            print("Space not found, creating...")
            api.create_repo(
                repo_id=repo_id,
                repo_type=repo_type,
                space_sdk="docker",
                private=False,
            )
            print(f"Created space: https://huggingface.co/spaces/{repo_id}")
        else:
            print(f"Error checking repo: {type(e).__name__}: {e}")
            # Try to create anyway
            try:
                api.create_repo(
                    repo_id=repo_id,
                    repo_type=repo_type,
                    space_sdk="docker",
                    private=False,
                )
                print(f"Created space: https://huggingface.co/spaces/{repo_id}")
            except Exception as e2:
                print(f"Note: {e2}")

    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Files to upload: (local_path, path_in_repo)
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

    print("\nUploading files...")
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
                print(f"  OK: {repo_path}")
                success += 1
            except Exception as upload_err:
                print(f"  FAIL: {repo_path} — {upload_err}")
        else:
            print(f"  MISSING: {local_path}")

    if success == len(files):
        print(f"\nAll {success} files uploaded successfully!")
    else:
        print(f"\n{success}/{len(files)} files uploaded.")

    print(f"\nDeployment complete!")
    print(f"  Space URL:    https://huggingface.co/spaces/{repo_id}")
    print(f"  Health check: https://niaz9246-ddx-env.hf.space/health")
    print(f"  API docs:     https://niaz9246-ddx-env.hf.space/docs")
    print("\nNote: It may take 1-3 minutes for the Docker build to finish.")

if __name__ == "__main__":
    main()
