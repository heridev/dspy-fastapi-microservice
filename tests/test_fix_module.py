"""
Unit tests for DSPy fix module.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from dspy_prompt_fixer.fix_module import PromptFixer, FixProgrammingPrompt, fix_prompt_quick


class TestFixProgrammingPrompt:
    """Test cases for FixProgrammingPrompt signature."""

    def test_signature_creation(self):
        """Test that the signature can be created."""
        signature = FixProgrammingPrompt(raw_prompt="test", corrected_prompt="test")

        assert hasattr(signature, 'raw_prompt')
        assert hasattr(signature, 'corrected_prompt')

    def test_signature_fields(self):
        """Test that signature fields have correct descriptions."""
        # Test the class definition, not an instance
        assert 'raw_prompt' in FixProgrammingPrompt.model_fields
        assert 'corrected_prompt' in FixProgrammingPrompt.model_fields

        # Check that fields have descriptions
        raw_prompt_field = FixProgrammingPrompt.model_fields['raw_prompt']
        corrected_prompt_field = FixProgrammingPrompt.model_fields['corrected_prompt']

        assert raw_prompt_field.json_schema_extra is not None
        assert corrected_prompt_field.json_schema_extra is not None
        assert 'desc' in raw_prompt_field.json_schema_extra
        assert 'desc' in corrected_prompt_field.json_schema_extra

        # Check that descriptions are strings
        assert isinstance(raw_prompt_field.json_schema_extra['desc'], str)
        assert isinstance(corrected_prompt_field.json_schema_extra['desc'], str)


class TestPromptFixer:
    """Test cases for PromptFixer class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_examples = [
            {"raw_prompt": "frogs in ruby", "corrected_prompt": "procs in ruby"},
            {"raw_prompt": "rails and rels", "corrected_prompt": "rails and routes"},
        ]

    def test_init_with_optimization(self):
        """Test initialization with optimization enabled."""
        fixer = PromptFixer(use_optimization=True)

        assert fixer.use_optimization is True
        assert fixer.fix_prompt_module is not None
        assert fixer.compiled_module is None

    def test_init_without_optimization(self):
        """Test initialization with optimization disabled."""
        fixer = PromptFixer(use_optimization=False)

        assert fixer.use_optimization is False
        assert fixer.fix_prompt_module is not None
        assert fixer.compiled_module is None

    @patch('dspy.teleprompt.MIPROv2')
    @patch('dspy.evaluate.EM')
    def test_compile_with_examples_success(self, mock_exact_match, mock_mipro):
        """Test successful compilation with examples."""
        mock_metric = Mock()
        mock_exact_match.return_value = mock_metric

        mock_optimizer = Mock()
        mock_mipro.return_value = mock_optimizer

        mock_compiled = Mock()
        mock_optimizer.compile.return_value = mock_compiled

        fixer = PromptFixer(use_optimization=True)
        fixer.compile_with_examples(self.test_examples)

        # Check that MIPRO was called correctly
        mock_exact_match.assert_called_once()
        mock_mipro.assert_called_once_with(metric=mock_metric)
        mock_optimizer.compile.assert_called_once()

        assert fixer.compiled_module == mock_compiled

    @patch('dspy.teleprompt.MIPROv2')
    @patch('dspy.evaluate.EM')
    def test_compile_with_examples_import_error(self, mock_exact_match, mock_mipro):
        """Test compilation with import error."""
        mock_mipro.side_effect = ImportError("Module not found")

        fixer = PromptFixer(use_optimization=True)
        fixer.compile_with_examples(self.test_examples)

        # Should fall back to basic module
        assert fixer.use_optimization is False
        assert fixer.compiled_module is None

    def test_compile_without_optimization(self):
        """Test compilation when optimization is disabled."""
        fixer = PromptFixer(use_optimization=False)
        fixer.compile_with_examples(self.test_examples)

        # Should not compile anything
        assert fixer.compiled_module is None

    def test_fix_prompt_empty_input(self):
        """Test fixing prompt with empty input."""
        fixer = PromptFixer()

        with pytest.raises(ValueError, match="Raw prompt cannot be empty"):
            fixer.fix_prompt("")

        with pytest.raises(ValueError, match="Raw prompt cannot be empty"):
            fixer.fix_prompt("   ")

    def test_fix_prompt_none_input(self):
        """Test fixing prompt with None input."""
        fixer = PromptFixer()

        with pytest.raises(ValueError, match="Raw prompt cannot be empty"):
            fixer.fix_prompt(None)

    @patch('dspy_prompt_fixer.fix_module.dspy.Predict')
    def test_fix_prompt_basic_module(self, mock_predict):
        """Test fixing prompt with basic module (no optimization)."""
        mock_result = Mock()
        mock_result.corrected_prompt = "corrected prompt"

        mock_predict_instance = Mock()
        mock_predict_instance.return_value = mock_result
        mock_predict.return_value = mock_predict_instance

        fixer = PromptFixer(use_optimization=False)
        result = fixer.fix_prompt("test prompt")

        assert result == "corrected prompt"
        mock_predict_instance.assert_called_once_with(raw_prompt="test prompt")

    @patch('dspy_prompt_fixer.fix_module.dspy.Predict')
    def test_fix_prompt_compiled_module(self, mock_predict):
        """Test fixing prompt with compiled module."""
        mock_result = Mock()
        mock_result.corrected_prompt = "corrected prompt"

        mock_compiled = Mock()
        mock_compiled.return_value = mock_result

        fixer = PromptFixer(use_optimization=True)
        fixer.compiled_module = mock_compiled

        result = fixer.fix_prompt("test prompt")

        assert result == "corrected prompt"
        mock_compiled.assert_called_once_with(raw_prompt="test prompt")

    @patch('dspy_prompt_fixer.fix_module.dspy.Predict')
    def test_fix_prompt_error_handling(self, mock_predict):
        """Test error handling in fix_prompt."""
        mock_predict_instance = Mock()
        mock_predict_instance.side_effect = Exception("DSPy error")
        mock_predict.return_value = mock_predict_instance

        fixer = PromptFixer(use_optimization=False)

        with pytest.raises(RuntimeError, match="Error fixing prompt"):
            fixer.fix_prompt("test prompt")

    def test_get_module_info(self):
        """Test getting module information."""
        fixer = PromptFixer(use_optimization=True)
        info = fixer.get_module_info()

        assert isinstance(info, dict)
        assert 'use_optimization' in info
        assert 'has_compiled_module' in info
        assert 'module_type' in info

        assert info['use_optimization'] is True
        assert info['has_compiled_module'] is False
        assert info['module_type'] == 'FixProgrammingPrompt'

    def test_get_module_info_with_compiled(self):
        """Test getting module info when compiled module exists."""
        fixer = PromptFixer(use_optimization=True)
        fixer.compiled_module = Mock()  # Simulate compiled module

        info = fixer.get_module_info()

        assert info['has_compiled_module'] is True


class TestFixPromptQuick:
    """Test cases for fix_prompt_quick function."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_examples = [
            {"raw_prompt": "frogs in ruby", "corrected_prompt": "procs in ruby"},
        ]

    @patch('dspy_prompt_fixer.fix_module.PromptFixer')
    def test_fix_prompt_quick_with_examples(self, mock_prompt_fixer_class):
        """Test quick fix with examples."""
        mock_fixer = Mock()
        mock_fixer.fix_prompt.return_value = "corrected prompt"
        mock_prompt_fixer_class.return_value = mock_fixer

        result = fix_prompt_quick("test prompt", self.test_examples)

        assert result == "corrected prompt"
        mock_prompt_fixer_class.assert_called_once_with(use_optimization=True)
        mock_fixer.compile_with_examples.assert_called_once_with(self.test_examples)
        mock_fixer.fix_prompt.assert_called_once_with("test prompt")

    @patch('dspy_prompt_fixer.fix_module.PromptFixer')
    def test_fix_prompt_quick_without_examples(self, mock_prompt_fixer_class):
        """Test quick fix without examples."""
        mock_fixer = Mock()
        mock_fixer.fix_prompt.return_value = "corrected prompt"
        mock_prompt_fixer_class.return_value = mock_fixer

        result = fix_prompt_quick("test prompt")

        assert result == "corrected prompt"
        mock_prompt_fixer_class.assert_called_once_with(use_optimization=False)
        mock_fixer.compile_with_examples.assert_not_called()
        mock_fixer.fix_prompt.assert_called_once_with("test prompt")
