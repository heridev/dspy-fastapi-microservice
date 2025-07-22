# 🧠 DSPy-Powered Prompt Correction Microservice Plan

This microservice will use [DSPy](https://dspy.ai) to fix ambiguous or incorrect prompts (e.g. from speech-to-text systems) before sending them to a language model like Claude.

---

## 🧱 Architecture Overview

```plaintext
Electron (speech to text)
    ↓
Node.js (Express)
    ↓  [call]
FastAPI Microservice w/ DSPy ← ❗(corrects prompt like "frogs in Ruby" → "procs in Ruby")
    ↓
Node.js sends final prompt to Claude
    ↓
Electron renders Claude's response
```

---

## ✅ What the Python Microservice Does

- Exposes `/optimize-prompt` POST endpoint
- Takes raw prompt (`"frogs in ruby"`)
- Uses DSPy with optimization examples to improve it
- Returns cleaned version (`"procs in ruby"`)

---

## 🔧 Tech Stack

- **Python 3.10+**
- **FastAPI** for API routing
- **DSPy** for optimization
- **Uvicorn** for ASGI server

---

## 📦 Python Dependencies

Create a file `requirements.txt`:

```txt
fastapi
uvicorn
dspy
anthropic  # Claude client
```

Install with:

```bash
pip install -r requirements.txt
```

---

## 📂 Folder Structure

```
dspy_prompt_fixer/
├── main.py              # FastAPI app
├── fix_module.py        # DSPy signature + optimizer
├── examples.py          # Training examples
├── claude_lm.py         # Claude LanguageModel wrapper
├── requirements.txt
```

---

## 🧠 DSPy Signature Module (fix_module.py)

```python
import dspy

class FixProgrammingPrompt(dspy.Signature):
    raw_prompt = dspy.InputField(desc="Prompt from speech-to-text")
    corrected_prompt = dspy.OutputField(desc="Clean programming question")

fix_prompt_module = dspy.Predict(FixProgrammingPrompt)
```

---

## 📘 Optimization Examples (examples.py)

```python
examples = [
    {"raw_prompt": "frogs in ruby", "corrected_prompt": "procs in ruby"},
    {"raw_prompt": "rails and rels", "corrected_prompt": "rails and routes"},
    {"raw_prompt": "how to use cads in ruby", "corrected_prompt": "how to use procs in ruby"},
]
```

---

## 🤖 Claude LanguageModel Wrapper (claude_lm.py)

```python
import anthropic
from dspy import LanguageModel

class ClaudeLM(LanguageModel):
    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def __call__(self, prompt: str, **kwargs) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            temperature=0.7,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text  # Assumes Claude returns structured content blocks
```

---

## 🚀 DSPy Optimizer in FastAPI App (main.py)

```python
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict

import dspy
from dspy.teleprompt import MIPRO
from dspy.evaluate import ExactMatch
from fix_module import fix_prompt_module, FixProgrammingPrompt
from examples import examples
from claude_lm import ClaudeLM

# Init Claude
claude = ClaudeLM(api_key="your-anthropic-key", model="claude-3-opus-20240229")
dspy.settings.configure(lm=claude)

# Define scoring function
metric = ExactMatch(example_outputs=[ex['corrected_prompt'] for ex in examples])
mipro = MIPRO(metric=metric)
compiled_module = mipro.compile(fix_prompt_module, trainset=examples)

# Request model
class PromptRequest(BaseModel):
    raw_prompt: str

@app.post("/optimize-prompt")
def optimize_prompt(data: PromptRequest) -> Dict:
    result = compiled_module(raw_prompt=data.raw_prompt)
    return {"corrected_prompt": result.corrected_prompt}
```

---

## ⚙️ Run the Service

```bash
uvicorn main:app --reload --port 8000
```

---

## 🔁 Example Request from Express

From your Node backend:

```js
const axios = require("axios");

const corrected = await axios.post("http://localhost:8000/optimize-prompt", {
  raw_prompt: "frogs in ruby",
});

console.log(corrected.data.corrected_prompt); // "procs in ruby"
```

---

## ✅ Benefits

- Clean separation: Electron + Node.js remain untouched
- DSPy optimization is centralized in Python (where it thrives)

---

## 🧠 Next Steps

- Add more examples to improve prompt correction
- Log bad completions and auto-learn from them
- Replace OpenAI with Anthropic Claude via custom LM wrapper
