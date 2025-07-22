"""
DSPy signature and prediction module for prompt correction.
"""

import dspy
from typing import Optional, List, Union


class FixProgrammingPrompt(dspy.Signature):
    """
    DSPy signature for fixing programming prompts from speech-to-text.

    This signature defines the input and output structure for the prompt
    correction task, where raw prompts from speech-to-text systems are
    corrected to proper programming terminology.
    """

    raw_prompt = dspy.InputField(
        desc="Raw prompt from speech-to-text system that may contain errors or ambiguities"
    )

    corrected_prompt = dspy.OutputField(
        desc="Clean, corrected programming question with proper terminology and clarity"
    )


class PromptFixer:
    """
    Main class for prompt correction using DSPy.

    This class encapsulates the DSPy prediction module and provides
    methods for fixing prompts with optional optimization.
    """

    def __init__(self, use_optimization: bool = True):
        """
        Initialize the PromptFixer.

        Args:
            use_optimization: Whether to use MIPRO optimization for the prediction module
        """
        self.use_optimization = use_optimization
        self.fix_prompt_module = dspy.Predict(FixProgrammingPrompt)
        self.compiled_module = None
        self.lm = None

    def compile_with_examples(self, examples: List[Union[dict, dspy.Example]]) -> None:
        """
        Compile the prediction module with training examples using MIPRO optimization.

        Args:
            examples: List of training examples (can be dict or dspy.Example objects)
        """
        if not self.use_optimization:
            return

        try:
            from dspy.teleprompt import MIPROv2
            from dspy.evaluate import EM

            # Convert dict examples to dspy.Example objects if needed
            dspy_examples = []
            for example in examples:
                if isinstance(example, dict):
                    dspy_examples.append(dspy.Example(
                        raw_prompt=example["raw_prompt"],
                        corrected_prompt=example["corrected_prompt"]
                    ))
                elif isinstance(example, dspy.Example):
                    dspy_examples.append(example)
                else:
                    raise ValueError(f"Invalid example format: {type(example)}")

            print(f"🔄 Compiling with {len(dspy_examples)} examples...")

            # Define scoring function
            metric = EM
            mipro = MIPROv2(metric=metric)

            # Compile the module
            self.compiled_module = mipro.compile(self.fix_prompt_module, trainset=dspy_examples)
            print("✅ MIPRO compilation completed successfully")

        except ImportError as e:
            print(f"Warning: Could not import optimization modules: {e}")
            print("Falling back to basic prediction module")
            self.use_optimization = False
        except Exception as e:
            print(f"Warning: Error during compilation: {e}")
            print("Falling back to basic prediction module")
            self.use_optimization = False

    def fix_prompt(self, raw_prompt: str) -> str:
        """
        Fix a raw prompt using the DSPy module.

        Args:
            raw_prompt: The raw prompt from speech-to-text

        Returns:
            The corrected prompt
        """
        if not raw_prompt or not raw_prompt.strip():
            raise ValueError("Raw prompt cannot be empty")

        try:
            # Use compiled module if available, otherwise use basic module
            if self.compiled_module and self.use_optimization:
                result = self.compiled_module(raw_prompt=raw_prompt)
            else:
                result = self.fix_prompt_module(raw_prompt=raw_prompt)

            return result.corrected_prompt

        except Exception as e:
            # Fallback to direct LM call if DSPy structured output fails
            print(f"Warning: DSPy structured output failed, using fallback: {e}")
            return self._fix_prompt_fallback(raw_prompt)

    def _fix_prompt_fallback(self, raw_prompt: str) -> str:
        """
        Fallback method that directly calls the language model without DSPy's structured output.

        Args:
            raw_prompt: The raw prompt to fix

        Returns:
            The corrected prompt
        """
        try:
            # Get the language model from DSPy settings
            lm = dspy.settings.lm
            if not lm:
                raise RuntimeError("No language model configured")

            # Create a simple prompt for correction
            prompt = f"""You are a helpful assistant that corrects programming-related prompts from speech-to-text systems.

Here are some examples of corrections:
- "frogs in ruby" → "procs in ruby"
- "rails and rels" → "rails and routes"
- "how to use cads in ruby" → "how to use procs in ruby"

Please correct the following prompt, making it clearer and more accurate for programming queries. Respond with ONLY the corrected prompt, nothing else.

Raw prompt: "{raw_prompt}"

Corrected prompt:"""

            # Call the language model directly
            response = lm(prompt)

            # Extract the corrected prompt from the response
            # Look for the corrected prompt after "Corrected prompt:"
            if "Corrected prompt:" in response:
                corrected = response.split("Corrected prompt:")[-1].strip()
                # Remove any quotes and extra whitespace
                corrected = corrected.strip('"').strip("'").strip()
                return corrected
            else:
                # If the format is unexpected, just return the response
                # Clean up the response by removing extra text
                response = response.strip()
                # Remove any explanatory text and keep only the corrected prompt
                if "→" in response:
                    corrected = response.split("→")[-1].strip()
                    return corrected.strip('"').strip("'").strip()
                else:
                    return response

        except Exception as e:
            raise RuntimeError(f"Error in fallback prompt fixing: {str(e)}")

    def get_module_info(self) -> dict:
        """
        Get information about the current module configuration.

        Returns:
            Dictionary with module configuration information
        """
        return {
            "use_optimization": self.use_optimization,
            "has_compiled_module": self.compiled_module is not None,
            "module_type": "FixProgrammingPrompt"
        }


# Convenience function for quick prompt fixing
def fix_prompt_quick(raw_prompt: str, examples: Optional[list] = None) -> str:
    """
    Quick function to fix a prompt without creating a full PromptFixer instance.

    Args:
        raw_prompt: The raw prompt to fix
        examples: Optional training examples for optimization

    Returns:
        The corrected prompt
    """
    fixer = PromptFixer(use_optimization=examples is not None)

    if examples:
        fixer.compile_with_examples(examples)

    return fixer.fix_prompt(raw_prompt)
