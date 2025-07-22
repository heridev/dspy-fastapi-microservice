"""
Unit tests for examples module.
"""

import pytest
from dspy_prompt_fixer.examples import (
    get_all_examples,
    get_examples_by_category,
    add_example,
    get_example_count,
    PROGRAMMING_EXAMPLES,
    SPEECH_ERROR_EXAMPLES,
    TECHNICAL_CORRECTIONS
)


class TestExamples:
    """Test cases for examples module."""

    def setup_method(self):
        """Set up test fixtures."""
        # Store original examples to restore after tests
        self.original_programming = PROGRAMMING_EXAMPLES.copy()
        self.original_speech = SPEECH_ERROR_EXAMPLES.copy()
        self.original_technical = TECHNICAL_CORRECTIONS.copy()

    def teardown_method(self):
        """Clean up after tests."""
        # Restore original examples
        PROGRAMMING_EXAMPLES.clear()
        PROGRAMMING_EXAMPLES.extend(self.original_programming)
        SPEECH_ERROR_EXAMPLES.clear()
        SPEECH_ERROR_EXAMPLES.extend(self.original_speech)
        TECHNICAL_CORRECTIONS.clear()
        TECHNICAL_CORRECTIONS.extend(self.original_technical)

    def test_get_all_examples(self):
        """Test getting all examples."""
        examples = get_all_examples()

        assert isinstance(examples, list)
        assert len(examples) > 0

        # Check that all examples have required keys
        for example in examples:
            assert 'raw_prompt' in example
            assert 'corrected_prompt' in example
            assert isinstance(example['raw_prompt'], str)
            assert isinstance(example['corrected_prompt'], str)

    def test_get_examples_by_category_programming(self):
        """Test getting programming examples."""
        examples = get_examples_by_category('programming')

        assert isinstance(examples, list)
        assert len(examples) > 0

        # Check that these are programming examples
        for example in examples:
            assert example in PROGRAMMING_EXAMPLES

    def test_get_examples_by_category_speech(self):
        """Test getting speech error examples."""
        examples = get_examples_by_category('speech')

        assert isinstance(examples, list)
        assert len(examples) > 0

        # Check that these are speech examples
        for example in examples:
            assert example in SPEECH_ERROR_EXAMPLES

    def test_get_examples_by_category_technical(self):
        """Test getting technical correction examples."""
        examples = get_examples_by_category('technical')

        assert isinstance(examples, list)
        assert len(examples) > 0

        # Check that these are technical examples
        for example in examples:
            assert example in TECHNICAL_CORRECTIONS

    def test_get_examples_by_category_all(self):
        """Test getting all examples via category."""
        examples = get_examples_by_category('all')
        all_examples = get_all_examples()

        assert examples == all_examples

    def test_get_examples_by_category_invalid(self):
        """Test getting examples with invalid category."""
        examples = get_examples_by_category('invalid_category')

        assert examples == []

    def test_add_example_programming(self):
        """Test adding a programming example."""
        initial_count = len(PROGRAMMING_EXAMPLES)

        add_example(
            raw_prompt="test raw prompt",
            corrected_prompt="test corrected prompt",
            category="programming"
        )

        assert len(PROGRAMMING_EXAMPLES) == initial_count + 1
        assert PROGRAMMING_EXAMPLES[-1]['raw_prompt'] == "test raw prompt"
        assert PROGRAMMING_EXAMPLES[-1]['corrected_prompt'] == "test corrected prompt"

    def test_add_example_speech(self):
        """Test adding a speech example."""
        initial_count = len(SPEECH_ERROR_EXAMPLES)

        add_example(
            raw_prompt="test raw prompt",
            corrected_prompt="test corrected prompt",
            category="speech"
        )

        assert len(SPEECH_ERROR_EXAMPLES) == initial_count + 1
        assert SPEECH_ERROR_EXAMPLES[-1]['raw_prompt'] == "test raw prompt"
        assert SPEECH_ERROR_EXAMPLES[-1]['corrected_prompt'] == "test corrected prompt"

    def test_add_example_technical(self):
        """Test adding a technical example."""
        initial_count = len(TECHNICAL_CORRECTIONS)

        add_example(
            raw_prompt="test raw prompt",
            corrected_prompt="test corrected prompt",
            category="technical"
        )

        assert len(TECHNICAL_CORRECTIONS) == initial_count + 1
        assert TECHNICAL_CORRECTIONS[-1]['raw_prompt'] == "test raw prompt"
        assert TECHNICAL_CORRECTIONS[-1]['corrected_prompt'] == "test corrected prompt"

    def test_add_example_invalid_category(self):
        """Test adding example with invalid category."""
        with pytest.raises(ValueError, match="Unknown category: invalid"):
            add_example(
                raw_prompt="test raw prompt",
                corrected_prompt="test corrected prompt",
                category="invalid"
            )

    def test_get_example_count(self):
        """Test getting example counts."""
        counts = get_example_count()

        assert isinstance(counts, dict)
        assert 'programming' in counts
        assert 'speech' in counts
        assert 'technical' in counts
        assert 'total' in counts

        # Check that counts are correct
        assert counts['programming'] == len(PROGRAMMING_EXAMPLES)
        assert counts['speech'] == len(SPEECH_ERROR_EXAMPLES)
        assert counts['technical'] == len(TECHNICAL_CORRECTIONS)
        assert counts['total'] == len(get_all_examples())

        # Check that total equals sum of categories
        expected_total = counts['programming'] + counts['speech'] + counts['technical']
        assert counts['total'] == expected_total

    def test_example_structure(self):
        """Test that all examples have correct structure."""
        all_examples = get_all_examples()

        for example in all_examples:
            # Check required fields
            assert 'raw_prompt' in example
            assert 'corrected_prompt' in example

            # Check field types
            assert isinstance(example['raw_prompt'], str)
            assert isinstance(example['corrected_prompt'], str)

            # Check non-empty strings
            assert example['raw_prompt'].strip() != ""
            assert example['corrected_prompt'].strip() != ""

    def test_example_uniqueness(self):
        """Test that examples are unique."""
        all_examples = get_all_examples()
        raw_prompts = [ex['raw_prompt'] for ex in all_examples]

        # Check for duplicates
        assert len(raw_prompts) == len(set(raw_prompts))
