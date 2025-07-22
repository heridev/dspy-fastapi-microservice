"""
Training examples for DSPy prompt correction optimization.
"""

from typing import List, Dict, Any, Union
import dspy

# Core training examples for programming prompt correction
PROGRAMMING_EXAMPLES = [
    dspy.Example(raw_prompt="frogs in ruby", corrected_prompt="procs in ruby"),
    dspy.Example(raw_prompt="rails and rels", corrected_prompt="rails and routes"),
    dspy.Example(raw_prompt="how to use cads in ruby", corrected_prompt="how to use procs in ruby"),
    dspy.Example(raw_prompt="ruby on rails gems", corrected_prompt="ruby on rails gems"),
    dspy.Example(raw_prompt="javascript promises and async", corrected_prompt="javascript promises and async"),
    dspy.Example(raw_prompt="react hooks and state", corrected_prompt="react hooks and state"),
    dspy.Example(raw_prompt="python decorators and functions", corrected_prompt="python decorators and functions"),
    dspy.Example(raw_prompt="docker containers and images", corrected_prompt="docker containers and images"),
    dspy.Example(raw_prompt="git branches and merging", corrected_prompt="git branches and merging"),
    dspy.Example(raw_prompt="sql queries and joins", corrected_prompt="sql queries and joins"),
    dspy.Example(raw_prompt="api rest endpoints", corrected_prompt="api rest endpoints"),
    dspy.Example(raw_prompt="microservices architecture", corrected_prompt="microservices architecture"),
    dspy.Example(raw_prompt="machine learning algorithms", corrected_prompt="machine learning algorithms"),
    dspy.Example(raw_prompt="data structures and algorithms", corrected_prompt="data structures and algorithms"),
    dspy.Example(raw_prompt="web development frameworks", corrected_prompt="web development frameworks"),
]

# Additional examples for common speech-to-text errors
SPEECH_ERROR_EXAMPLES = [
    dspy.Example(raw_prompt="how to create a new rails app", corrected_prompt="how to create a new rails app"),
    dspy.Example(raw_prompt="what is dependency injection", corrected_prompt="what is dependency injection"),
    dspy.Example(raw_prompt="explain object oriented programming",
                 corrected_prompt="explain object oriented programming"),
    dspy.Example(raw_prompt="how to debug javascript code", corrected_prompt="how to debug javascript code"),
    dspy.Example(raw_prompt="what are design patterns", corrected_prompt="what are design patterns"),
    dspy.Example(raw_prompt="how to optimize database queries", corrected_prompt="how to optimize database queries"),
    dspy.Example(raw_prompt="explain restful api design", corrected_prompt="explain restful api design"),
    dspy.Example(raw_prompt="what is continuous integration", corrected_prompt="what is continuous integration"),
    dspy.Example(raw_prompt="how to write unit tests", corrected_prompt="how to write unit tests"),
    dspy.Example(raw_prompt="explain version control systems", corrected_prompt="explain version control systems"),
]

# Examples for technical terminology corrections
TECHNICAL_CORRECTIONS = [
    dspy.Example(raw_prompt="lambda functions in python", corrected_prompt="lambda functions in python"),
    dspy.Example(raw_prompt="closures and scope in javascript", corrected_prompt="closures and scope in javascript"),
    dspy.Example(raw_prompt="inheritance and polymorphism", corrected_prompt="inheritance and polymorphism"),
    dspy.Example(raw_prompt="recursion and iteration", corrected_prompt="recursion and iteration"),
    dspy.Example(raw_prompt="asynchronous programming patterns", corrected_prompt="asynchronous programming patterns"),
    dspy.Example(raw_prompt="memory management in programming", corrected_prompt="memory management in programming"),
    dspy.Example(raw_prompt="algorithm complexity analysis", corrected_prompt="algorithm complexity analysis"),
    dspy.Example(raw_prompt="software testing methodologies", corrected_prompt="software testing methodologies"),
    dspy.Example(raw_prompt="database normalization", corrected_prompt="database normalization"),
    dspy.Example(raw_prompt="network protocols and http", corrected_prompt="network protocols and http"),
]


def get_all_examples() -> List[dspy.Example]:
    """
    Get all training examples combined.

    Returns:
        List of all training examples for DSPy optimization.
    """
    return PROGRAMMING_EXAMPLES + SPEECH_ERROR_EXAMPLES + TECHNICAL_CORRECTIONS


def get_examples_by_category(category: str) -> List[dspy.Example]:
    """
    Get examples by category.

    Args:
        category: Category of examples to return ('programming', 'speech', 'technical')

    Returns:
        List of examples for the specified category.
    """
    categories = {
        "programming": PROGRAMMING_EXAMPLES,
        "speech": SPEECH_ERROR_EXAMPLES,
        "technical": TECHNICAL_CORRECTIONS,
        "all": get_all_examples()
    }

    return categories.get(category, [])


def add_example(raw_prompt: str, corrected_prompt: str, category: str = "programming") -> None:
    """
    Add a new example to the training set.

    Args:
        raw_prompt: The raw prompt from speech-to-text
        corrected_prompt: The corrected version
        category: Category to add the example to
    """
    example = dspy.Example(raw_prompt=raw_prompt, corrected_prompt=corrected_prompt)

    if category == "programming":
        PROGRAMMING_EXAMPLES.append(example)
    elif category == "speech":
        SPEECH_ERROR_EXAMPLES.append(example)
    elif category == "technical":
        TECHNICAL_CORRECTIONS.append(example)
    else:
        raise ValueError(f"Unknown category: {category}")


def get_example_count() -> Dict[str, int]:
    """
    Get count of examples by category.

    Returns:
        Dictionary with counts for each category.
    """
    return {
        "programming": len(PROGRAMMING_EXAMPLES),
        "speech": len(SPEECH_ERROR_EXAMPLES),
        "technical": len(TECHNICAL_CORRECTIONS),
        "total": len(get_all_examples())
    }


def convert_dict_to_dspy_examples(examples: List[Dict[str, str]]) -> List[dspy.Example]:
    """
    Convert dictionary examples to DSPy Example objects.

    Args:
        examples: List of dictionary examples

    Returns:
        List of DSPy Example objects
    """
    return [dspy.Example(raw_prompt=ex["raw_prompt"], corrected_prompt=ex["corrected_prompt"])
            for ex in examples]
