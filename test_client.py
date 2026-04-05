import sys
import os

# Add the src folder to Python's path so it can find our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from envs.ddx_env.client import DDxEnvClient

def main():
    print("Initializing connection to Hugging Face Space...")
    # Initialize client with your Hugging Face Space URL
    client = DDxEnvClient(base_url="https://niaz9246-ddx-env.hf.space")

    # Check if the server is healthy
    if client.health():
        print("\n✅ Successfully connected to DDx RL Environment!")
        
        # Start a brand new diagnostic episode
        print("\n--- Starting New Diagnostic Episode ---")
        result = client.reset()
        print("Initial Patient Prompt:")
        print(result.observation.prompt)
        
        # Take an action: ask about a symptom
        print("\n--- Taking Action: ask_symptom 'nausea' ---")
        result = client.step("ask_symptom", "nausea")
        print(f"Reward received: {result.reward}")
        print("Resulting Observation:")
        print(result.observation.prompt)
        
        # Take another action: order an ECG
        print("\n--- Taking Action: order_test 'ecg' ---")
        result = client.step("order_test", "ecg")
        print(f"Reward received: {result.reward}")
        print("Resulting Observation:")
        print(result.observation.prompt)
    else:
        print("\n❌ Failed to connect to the Hugging Face Space. Is it still building?")

if __name__ == "__main__":
    main()
