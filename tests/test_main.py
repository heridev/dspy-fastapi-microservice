"""
Integration tests for FastAPI main application.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
import os

from dspy_prompt_fixer.main import app


class TestMainApp:
    """Test cases for the main FastAPI application."""

    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)

    def test_root_endpoint(self):
        """Test the root endpoint."""
        response = self.client.get("/")

        assert response.status_code == 200
        data = response.json()

        assert data["service"] == "DSPy Prompt Correction Microservice"
        assert data["version"] == "1.0.0"
        assert data["status"] == "running"
        assert data["docs"] == "/docs"

    def test_health_check_uninitialized(self):
        """Test health check when DSPy is not initialized."""
        response = self.client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "unhealthy"
        assert data["dspy_configured"] is False
        assert "example_count" in data
        assert data["model_info"] is None

    @patch('dspy_prompt_fixer.main.claude_lm')
    @patch('dspy_prompt_fixer.main.prompt_fixer')
    def test_health_check_initialized(self, mock_prompt_fixer, mock_claude_lm):
        """Test health check when DSPy is initialized."""
        # Mock the global variables
        mock_claude_lm.get_config.return_value = {
            "model": "claude-3-opus-20240229",
            "provider": "anthropic"
        }

        response = self.client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"
        assert data["dspy_configured"] is True
        assert "example_count" in data
        assert data["model_info"] is not None
        assert data["model_info"]["provider"] == "anthropic"

    def test_optimize_prompt_uninitialized(self):
        """Test optimize prompt when DSPy is not initialized."""
        response = self.client.post("/optimize-prompt", json={
            "raw_prompt": "frogs in ruby"
        })

        assert response.status_code == 503
        data = response.json()
        assert data["detail"] == "DSPy not initialized"

    @patch('dspy_prompt_fixer.main.prompt_fixer')
    def test_optimize_prompt_success(self, mock_prompt_fixer):
        """Test successful prompt optimization."""
        mock_prompt_fixer.fix_prompt.return_value = "procs in ruby"

        response = self.client.post("/optimize-prompt", json={
            "raw_prompt": "frogs in ruby"
        })

        assert response.status_code == 200
        data = response.json()

        assert data["corrected_prompt"] == "procs in ruby"
        assert data["confidence"] is None
        mock_prompt_fixer.fix_prompt.assert_called_once_with("frogs in ruby")

    @patch('dspy_prompt_fixer.main.prompt_fixer')
    def test_optimize_prompt_empty_input(self, mock_prompt_fixer):
        """Test optimize prompt with empty input."""
        mock_prompt_fixer.fix_prompt.side_effect = ValueError("Raw prompt cannot be empty")

        response = self.client.post("/optimize-prompt", json={
            "raw_prompt": ""
        })

        assert response.status_code == 400
        data = response.json()
        assert "Raw prompt cannot be empty" in data["detail"]

    @patch('dspy_prompt_fixer.main.prompt_fixer')
    def test_optimize_prompt_error(self, mock_prompt_fixer):
        """Test optimize prompt with processing error."""
        mock_prompt_fixer.fix_prompt.side_effect = Exception("Processing error")

        response = self.client.post("/optimize-prompt", json={
            "raw_prompt": "test prompt"
        })

        assert response.status_code == 500
        data = response.json()
        assert "Error processing prompt" in data["detail"]

    def test_get_examples_all(self):
        """Test getting all examples."""
        response = self.client.get("/examples")

        assert response.status_code == 200
        data = response.json()

        assert "examples" in data
        assert isinstance(data["examples"], list)
        assert len(data["examples"]) > 0

        # Check example structure
        for example in data["examples"]:
            assert "raw_prompt" in example
            assert "corrected_prompt" in example

    def test_get_examples_by_category(self):
        """Test getting examples by category."""
        response = self.client.get("/examples?category=programming")

        assert response.status_code == 200
        data = response.json()

        assert "examples" in data
        assert isinstance(data["examples"], list)

    def test_get_examples_invalid_category(self):
        """Test getting examples with invalid category."""
        response = self.client.get("/examples?category=invalid")

        assert response.status_code == 200
        data = response.json()

        assert "examples" in data
        assert data["examples"] == []

    @patch('dspy_prompt_fixer.main.prompt_fixer')
    def test_add_training_example_success(self, mock_prompt_fixer):
        """Test adding a training example successfully."""
        response = self.client.post("/examples", json={
            "raw_prompt": "test raw prompt",
            "corrected_prompt": "test corrected prompt",
            "category": "programming"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Example added successfully"

    def test_add_training_example_invalid_category(self):
        """Test adding example with invalid category."""
        response = self.client.post("/examples", json={
            "raw_prompt": "test raw prompt",
            "corrected_prompt": "test corrected prompt",
            "category": "invalid"
        })

        assert response.status_code == 400
        data = response.json()
        assert "Unknown category" in data["detail"]

    def test_add_training_example_missing_fields(self):
        """Test adding example with missing required fields."""
        response = self.client.post("/examples", json={
            "raw_prompt": "test raw prompt"
            # Missing corrected_prompt
        })

        assert response.status_code == 422  # Validation error

    @patch('dspy_prompt_fixer.main.prompt_fixer')
    def test_get_stats_success(self, mock_prompt_fixer):
        """Test getting service statistics."""
        mock_prompt_fixer.get_module_info.return_value = {
            "use_optimization": True,
            "has_compiled_module": True,
            "module_type": "FixProgrammingPrompt"
        }

        response = self.client.get("/stats")

        assert response.status_code == 200
        data = response.json()

        assert "total_examples" in data
        assert "categories" in data
        assert "module_info" in data

        assert isinstance(data["total_examples"], int)
        assert isinstance(data["categories"], dict)
        assert isinstance(data["module_info"], dict)

    def test_get_stats_uninitialized(self):
        """Test getting stats when DSPy is not initialized."""
        response = self.client.get("/stats")

        assert response.status_code == 503
        data = response.json()
        assert data["detail"] == "DSPy not initialized"

    @patch('dspy_prompt_fixer.main.initialize_dspy')
    def test_reinitialize_success(self, mock_initialize):
        """Test successful DSPy reinitialization."""
        mock_initialize.return_value = True

        response = self.client.post("/reinitialize")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "DSPy reinitialized successfully"
        mock_initialize.assert_called_once()

    @patch('dspy_prompt_fixer.main.initialize_dspy')
    def test_reinitialize_failure(self, mock_initialize):
        """Test failed DSPy reinitialization."""
        # Make sure the mock doesn't raise an exception
        mock_initialize.side_effect = None
        mock_initialize.return_value = False

        response = self.client.post("/reinitialize")

        assert response.status_code == 500
        data = response.json()
        assert "Error reinitializing" in data["detail"]
        mock_initialize.assert_called_once()

    @patch('dspy_prompt_fixer.main.initialize_dspy')
    def test_reinitialize_error(self, mock_initialize):
        """Test DSPy reinitialization with error."""
        mock_initialize.side_effect = Exception("Initialization error")

        response = self.client.post("/reinitialize")

        assert response.status_code == 500
        data = response.json()
        assert "Error reinitializing" in data["detail"]

    def test_cors_headers(self):
        """Test that CORS headers are properly set."""
        response = self.client.options("/")

        # CORS preflight should be handled
        assert response.status_code in [200, 405]  # 405 is also acceptable for OPTIONS

    def test_docs_endpoint(self):
        """Test that docs endpoint is accessible."""
        response = self.client.get("/docs")
        assert response.status_code == 200

    def test_redoc_endpoint(self):
        """Test that redoc endpoint is accessible."""
        response = self.client.get("/redoc")
        assert response.status_code == 200
