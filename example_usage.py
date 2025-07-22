#!/usr/bin/env python3
"""
Example usage script for DSPy Prompt Correction Microservice.

This script demonstrates how to interact with the microservice
from a Node.js/Electron application or any other client.
"""

import requests
import json
import time
from typing import Dict, Any


class DSPyPromptClient:
    """Client for interacting with the DSPy Prompt Correction Microservice."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')

    def health_check(self) -> Dict[str, Any]:
        """Check if the service is healthy."""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    def optimize_prompt(self, raw_prompt: str) -> Dict[str, Any]:
        """Optimize a raw prompt using DSPy."""
        payload = {"raw_prompt": raw_prompt}
        response = requests.post(f"{self.base_url}/optimize-prompt", json=payload)
        response.raise_for_status()
        return response.json()

    def get_examples(self, category: str = None) -> Dict[str, Any]:
        """Get training examples."""
        params = {"category": category} if category else {}
        response = requests.get(f"{self.base_url}/examples", params=params)
        response.raise_for_status()
        return response.json()

    def add_example(self, raw_prompt: str, corrected_prompt: str, category: str = "programming") -> Dict[str, Any]:
        """Add a new training example."""
        payload = {
            "raw_prompt": raw_prompt,
            "corrected_prompt": corrected_prompt,
            "category": category
        }
        response = requests.post(f"{self.base_url}/examples", json=payload)
        response.raise_for_status()
        return response.json()

    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics."""
        response = requests.get(f"{self.base_url}/stats")
        response.raise_for_status()
        return response.json()

    def reinitialize(self) -> Dict[str, Any]:
        """Reinitialize DSPy with current configuration."""
        response = requests.post(f"{self.base_url}/reinitialize")
        response.raise_for_status()
        return response.json()


def main():
    """Main example function."""
    print("🧠 DSPy Prompt Correction Microservice - Example Usage")
    print("="*60)

    # Initialize client
    client = DSPyPromptClient()

    # Check if service is running
    print("\n1. Checking service health...")
    try:
        health = client.health_check()
        print(f"✅ Service status: {health['status']}")
        print(f"📊 DSPy configured: {health['dspy_configured']}")
        print(f"📈 Example count: {health['example_count']['total']}")
    except requests.exceptions.ConnectionError:
        print("❌ Service is not running. Please start the server first:")
        print("   python start_server.py")
        return
    except Exception as e:
        print(f"❌ Error checking health: {e}")
        return

    # Example 1: Basic prompt optimization
    print("\n2. Basic prompt optimization...")
    test_prompts = [
        "frogs in ruby",
        "rails and rels",
        "how to use cads in ruby",
        "javascript promises and async",
        "react hooks and state"
    ]

    for prompt in test_prompts:
        try:
            result = client.optimize_prompt(prompt)
            print(f"   '{prompt}' → '{result['corrected_prompt']}'")
        except Exception as e:
            print(f"   ❌ Error optimizing '{prompt}': {e}")

    # Example 2: Get training examples
    print("\n3. Getting training examples...")
    try:
        examples = client.get_examples(category="programming")
        print(f"   Found {len(examples['examples'])} programming examples")

        # Show first 3 examples
        for i, example in enumerate(examples['examples'][:3]):
            print(f"   {i+1}. '{example['raw_prompt']}' → '{example['corrected_prompt']}'")
    except Exception as e:
        print(f"   ❌ Error getting examples: {e}")

    # Example 3: Add a new training example
    print("\n4. Adding a new training example...")
    try:
        result = client.add_example(
            raw_prompt="how to use maps in javascript",
            corrected_prompt="how to use maps in javascript",
            category="programming"
        )
        print(f"   ✅ {result['message']}")
    except Exception as e:
        print(f"   ❌ Error adding example: {e}")

    # Example 4: Get service statistics
    print("\n5. Getting service statistics...")
    try:
        stats = client.get_stats()
        print(f"   Total examples: {stats['total_examples']}")
        print(f"   Categories: {stats['categories']}")
        print(f"   Module info: {stats['module_info']}")
    except Exception as e:
        print(f"   ❌ Error getting stats: {e}")

    # Example 5: Node.js/Electron integration example
    print("\n6. Node.js/Electron Integration Example:")
    print("""
   // In your Node.js/Express backend:
   const axios = require('axios');
   
   async function optimizePrompt(rawPrompt) {
     try {
       const response = await axios.post('http://localhost:8000/optimize-prompt', {
         raw_prompt: rawPrompt
       });
       return response.data.corrected_prompt;
     } catch (error) {
       console.error('Error optimizing prompt:', error);
       return rawPrompt; // Fallback to original
     }
   }
   
   // Usage in your Electron app:
   const correctedPrompt = await optimizePrompt("frogs in ruby");
   console.log(correctedPrompt); // "procs in ruby"
   """)

    print("\n🎉 Example usage completed!")
    print("\n📚 For more information:")
    print("   - API docs: http://localhost:8000/docs")
    print("   - Health check: http://localhost:8000/health")
    print("   - Run tests: python run_tests.py")


if __name__ == "__main__":
    main()
