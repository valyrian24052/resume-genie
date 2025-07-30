#!/usr/bin/env python3
"""Test script for the external prompt configuration system."""

import sys
import os
import logging

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai.prompt_loader import PromptLoader, PromptValidator
from ai.customization_engine import CustomizationEngine
from ai.ai_client import AIClient
from models.job_profile import JobProfile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_prompt_loader():
    """Test the PromptLoader functionality."""
    print("Testing PromptLoader...")
    
    loader = PromptLoader("config/prompts.yaml")
    
    # Test loading
    if not loader.load():
        print("❌ Failed to load prompt configuration")
        return False
    
    print("✅ Successfully loaded prompt configuration")
    
    # Test getting prompts
    available_prompts = loader.get_available_prompts()
    print(f"Available prompts: {available_prompts}")
    
    # Test specific prompt retrieval
    summary_prompt = loader.get_prompt('summary')
    if summary_prompt:
        print("✅ Successfully retrieved summary prompt")
        print(f"System prompt length: {len(summary_prompt.system_prompt)}")
        print(f"Model: {summary_prompt.model_params.get('model', 'N/A')}")
    else:
        print("❌ Failed to retrieve summary prompt")
        return False
    
    # Test default parameters
    default_params = loader.get_default_params()
    print(f"Default parameters: {default_params}")
    
    return True


def test_prompt_validator():
    """Test the PromptValidator functionality."""
    print("\nTesting PromptValidator...")
    
    # Test with valid configuration
    loader = PromptLoader("config/prompts.yaml")
    if not loader.load():
        print("❌ Failed to load configuration for validation test")
        return False
    
    validator = PromptValidator(loader._config_data)
    if validator.validate():
        print("✅ Configuration validation passed")
    else:
        print("❌ Configuration validation failed")
        for error in validator.errors:
            print(f"  Error: {error}")
        return False
    
    return True


def test_customization_engine_integration():
    """Test CustomizationEngine with external prompts."""
    print("\nTesting CustomizationEngine integration...")
    
    # Create a mock AI client (won't actually make requests)
    ai_client = AIClient("test-key", "https://api.example.com/v1")
    
    # Create customization engine with external prompts
    engine = CustomizationEngine(ai_client, "config/prompts.yaml")
    
    # Test prompt retrieval
    summary_prompt_text = engine._get_prompt_text('summary')
    if summary_prompt_text:
        print("✅ Successfully retrieved summary prompt from engine")
        print(f"Prompt preview: {summary_prompt_text[:100]}...")
    else:
        print("❌ Failed to retrieve summary prompt from engine")
        return False
    
    # Test model parameters
    model_params = engine._get_model_params('experience')
    print(f"Experience model params: {model_params}")
    
    # Test context building
    job_profile = JobProfile(
        title="Software Engineer",
        company="Test Company",
        description="Test job description",
        requirements=["Python", "JavaScript"],
        preferred_skills=["React", "Django"]
    )
    
    context = engine._build_context_from_template(
        'summary', 
        "Test summary content", 
        job_profile
    )
    
    if context:
        print("✅ Successfully built context from template")
        print(f"Context preview: {context[:200]}...")
    else:
        print("❌ Failed to build context from template")
        return False
    
    return True


def main():
    """Run all tests."""
    print("Testing External Prompt Configuration System")
    print("=" * 50)
    
    tests = [
        test_prompt_loader,
        test_prompt_validator,
        test_customization_engine_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ Test {test.__name__} failed")
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {str(e)}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)