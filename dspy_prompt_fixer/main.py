"""
Main FastAPI application for DSPy prompt correction microservice.
"""

import os
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import dspy

from .claude_lm import ClaudeLM
from .fix_module import PromptFixer
from .examples import get_all_examples, get_examples_by_category, add_example, get_example_count

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="DSPy Prompt Correction Microservice",
    description="A microservice that uses DSPy to fix ambiguous or incorrect prompts from speech-to-text systems",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for DSPy setup
claude_lm = None
prompt_fixer = None

# Pydantic models


class PromptRequest(BaseModel):
    raw_prompt: str = Field(..., description="Raw prompt from speech-to-text system")


class PromptResponse(BaseModel):
    corrected_prompt: str = Field(..., description="Corrected prompt")
    confidence: Optional[float] = Field(None, description="Confidence score if available")


class ExampleRequest(BaseModel):
    raw_prompt: str = Field(..., description="Raw prompt")
    corrected_prompt: str = Field(..., description="Corrected prompt")
    category: str = Field("programming", description="Category for the example")


class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status")
    dspy_configured: bool = Field(..., description="Whether DSPy is properly configured")
    example_count: Dict[str, int] = Field(..., description="Number of training examples")
    model_info: Optional[Dict] = Field(None, description="Language model information")


class StatsResponse(BaseModel):
    total_examples: int = Field(..., description="Total number of training examples")
    categories: Dict[str, int] = Field(..., description="Examples by category")
    module_info: Dict = Field(..., description="DSPy module information")


def initialize_dspy():
    """Initialize DSPy with Claude language model."""
    global claude_lm, prompt_fixer

    try:
        # Initialize Claude language model
        claude_lm = ClaudeLM(
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            model=os.getenv("CLAUDE_MODEL", "claude-3-opus-20240229")
        )

        # Configure DSPy settings
        dspy.settings.configure(lm=claude_lm)

        # Initialize prompt fixer
        prompt_fixer = PromptFixer(use_optimization=True)

        # Get training examples and compile
        examples = get_all_examples()
        if examples:
            prompt_fixer.compile_with_examples(examples)

        print("✅ DSPy initialized successfully")
        return True

    except Exception as e:
        print(f"❌ Error initializing DSPy: {e}")
        return False


@app.on_event("startup")
async def startup_event():
    """Initialize DSPy on startup."""
    initialize_dspy()


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with service information."""
    return {
        "service": "DSPy Prompt Correction Microservice",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    dspy_configured = claude_lm is not None and prompt_fixer is not None
    model_info = claude_lm.get_config() if claude_lm else None

    return HealthResponse(
        status="healthy" if dspy_configured else "unhealthy",
        dspy_configured=dspy_configured,
        example_count=get_example_count(),
        model_info=model_info
    )


@app.post("/optimize-prompt", response_model=PromptResponse)
async def optimize_prompt(request: PromptRequest):
    """
    Optimize a raw prompt using DSPy.

    This endpoint takes a raw prompt from speech-to-text and returns
    a corrected version using DSPy optimization.
    """
    if not prompt_fixer:
        raise HTTPException(status_code=503, detail="DSPy not initialized")

    try:
        corrected_prompt = prompt_fixer.fix_prompt(request.raw_prompt)

        return PromptResponse(
            corrected_prompt=corrected_prompt,
            confidence=None  # DSPy doesn't provide confidence scores by default
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing prompt: {str(e)}")


@app.get("/examples", response_model=Dict[str, List[Dict[str, str]]])
async def get_examples(category: Optional[str] = None):
    """
    Get training examples.

    Args:
        category: Optional category filter ('programming', 'speech', 'technical', 'all')
    """
    if category:
        examples = get_examples_by_category(category)
    else:
        examples = get_all_examples()

    return {"examples": examples}


@app.post("/examples", response_model=Dict[str, str])
async def add_training_example(request: ExampleRequest):
    """
    Add a new training example.

    This endpoint allows adding new examples to improve the model's performance.
    """
    try:
        add_example(
            raw_prompt=request.raw_prompt,
            corrected_prompt=request.corrected_prompt,
            category=request.category
        )

        # Recompile the model with new examples
        if prompt_fixer:
            examples = get_all_examples()
            prompt_fixer.compile_with_examples(examples)

        return {"message": "Example added successfully"}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding example: {str(e)}")


@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get service statistics."""
    if not prompt_fixer:
        raise HTTPException(status_code=503, detail="DSPy not initialized")

    example_counts = get_example_count()

    return StatsResponse(
        total_examples=example_counts["total"],
        categories={
            "programming": example_counts["programming"],
            "speech": example_counts["speech"],
            "technical": example_counts["technical"]
        },
        module_info=prompt_fixer.get_module_info()
    )


@app.post("/reinitialize")
async def reinitialize_dspy():
    """
    Reinitialize DSPy with current configuration.

    This endpoint allows reinitializing the DSPy system, useful after
    adding new examples or changing configuration.
    """
    try:
        success = initialize_dspy()
        if success:
            return {"message": "DSPy reinitialized successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to reinitialize DSPy")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reinitializing: {str(e)}")

if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "false").lower() == "true"

    uvicorn.run(
        "dspy_prompt_fixer.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )
