# 🧠 DSPy-Powered Prompt Correction Microservice

A FastAPI microservice that uses [DSPy](https://dspy.ai) to fix ambiguous or incorrect prompts from speech-to-text systems before sending them to language models like Claude.

## ✨ Features

- **DSPy Integration**: Uses DSPy's MIPRO optimization for prompt correction
- **Claude API**: Custom LanguageModel wrapper for Anthropic's Claude
- **Training Examples**: Comprehensive set of programming prompt corrections
- **RESTful API**: Clean FastAPI endpoints with automatic documentation
- **Health Monitoring**: Built-in health checks and statistics
- **CORS Support**: Cross-origin resource sharing enabled
- **Environment Configuration**: Flexible configuration via environment variables
- **Comprehensive Testing**: Unit and integration tests with coverage reporting

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Anthropic API key
- pip or conda

### Installation (with Virtual Environment)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd dspy-fastapi-microservice
   ```
2. **Run the setup script**
   ```bash
   python setup_venv.py
   ```
3. **Activate the virtual environment**
   ```bash
   # On macOS/Linux:
   source venv/bin/activate
   ```
4. **Edit environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your Anthropic API key
   ```
5. **Start the server**
   ```bash
   python start_server.py
   ```

The server will start on `http://localhost:8000` with automatic API documentation available at `/docs`.

## 🔧 Virtual Environment Management

### Creating and Using a Virtual Environment

```bash
# Create a new virtual environment (if not using setup_venv.py)
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage Examples

### Using curl

```bash
# Health check
curl http://localhost:8090/health

# Informational query
curl -X POST http://localhost:8090/optimize-prompt \
  -H "Content-Type: application/json" \
  -d '{
    "raw_prompt": "frogs in ruby"
  }'
```

### Best Practices

- Always activate the virtual environment before working on the project.
- Install new packages only when the virtual environment is active.
- Use `deactivate` to exit the virtual environment when done.
- Update `requirements.txt` after installing new packages:
  ```bash
  pip freeze > requirements.txt
  ```

### Troubleshooting

- If you see errors about missing packages, make sure the virtual environment is activated.
- If activation fails, recreate the environment:
  ```bash
  rm -rf venv
  python -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  ```

## 📋 API Endpoints

### Core Endpoints

#### `POST /optimize-prompt`

Optimize a raw prompt using DSPy.

**Request:**

```json
{
  "raw_prompt": "frogs in ruby"
}
```

**Response:**

```json
{
  "corrected_prompt": "procs in ruby",
  "confidence": null
}
```

#### `GET /health`

Check service health and configuration.

**Response:**

```json
{
  "status": "healthy",
  "dspy_configured": true,
  "example_count": {
    "programming": 15,
    "speech": 10,
    "technical": 10,
    "total": 35
  },
  "model_info": {
    "model": "claude-3-opus-20240229",
    "provider": "anthropic",
    "temperature": 0.7,
    "max_tokens": 1024
  }
}
```

### Management Endpoints

#### `GET /examples`

Get training examples (optionally filtered by category).

**Query Parameters:**

- `category` (optional): `programming`, `speech`, `technical`, or `all`

#### `POST /examples`

Add a new training example.

**Request:**

```json
{
  "raw_prompt": "test raw prompt",
  "corrected_prompt": "test corrected prompt",
  "category": "programming"
}
```

#### `GET /stats`

Get service statistics and module information.

#### `POST /reinitialize`

Reinitialize DSPy with current configuration (useful after adding examples).

## 🧪 Testing

### Running Tests

The project includes comprehensive unit and integration tests with coverage reporting.

#### Quick Test Run

```bash
python run_tests.py
```

#### Manual Test Execution

1. **Unit Tests Only**

   ```bash
   pytest tests/ -m unit -v
   ```

2. **Integration Tests Only**

   ```bash
   pytest tests/ -m integration -v
   ```

3. **All Tests with Coverage**

   ```bash
   pytest tests/ --cov=dspy_prompt_fixer --cov-report=term-missing --cov-report=html
   ```

4. **Specific Test File**
   ```bash
   pytest tests/test_claude_lm.py -v
   ```

### Test Coverage

The test suite covers:

- **Claude LanguageModel Wrapper** (`test_claude_lm.py`)

  - API key validation
  - Environment variable configuration
  - API call handling
  - Error scenarios
  - Response processing

- **Examples Module** (`test_examples.py`)

  - Example retrieval by category
  - Adding new examples
  - Data validation
  - Uniqueness checks

- **DSPy Fix Module** (`test_fix_module.py`)

  - Signature creation
  - PromptFixer initialization
  - MIPRO optimization
  - Error handling
  - Module information

- **FastAPI Application** (`test_main.py`)
  - All API endpoints
  - Request/response validation
  - Error handling
  - Health checks
  - CORS configuration

### Test Structure

```
tests/
├── __init__.py
├── test_claude_lm.py      # Claude API wrapper tests
├── test_examples.py       # Training examples tests
├── test_fix_module.py     # DSPy module tests
└── test_main.py          # FastAPI integration tests
```

### Coverage Reports

After running tests with coverage, reports are generated in:

- **Terminal**: Missing lines displayed
- **HTML**: `htmlcov/index.html` - Interactive coverage report
- **XML**: `coverage.xml` - For CI/CD integration

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `env.example`:

```bash
# Anthropic API Configuration
ANTHROPIC_API_KEY=your-anthropic-api-key-here
CLAUDE_MODEL=claude-3-opus-20240229

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false

# DSPy Configuration
DSPY_TEMPERATURE=0.7
DSPY_MAX_TOKENS=1024
```

### Required Variables

- `ANTHROPIC_API_KEY`: Your Anthropic API key (required)

### Optional Variables

- `CLAUDE_MODEL`: Claude model to use (default: claude-3-opus-20240229)
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `DEBUG`: Enable debug mode (default: false)
- `DSPY_TEMPERATURE`: DSPy temperature setting (default: 0.7)
- `DSPY_MAX_TOKENS`: DSPy max tokens (default: 1024)

## 📦 Project Structure

```
dspy-fastapi-microservice/
├── dspy_prompt_fixer/           # Main package
│   ├── __init__.py
│   ├── main.py                  # FastAPI application
│   ├── claude_lm.py            # Claude LanguageModel wrapper
│   ├── fix_module.py           # DSPy signature and optimizer
│   └── examples.py             # Training examples
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── test_claude_lm.py
│   ├── test_examples.py
│   ├── test_fix_module.py
│   └── test_main.py
├── requirements.txt            # Python dependencies
├── env.example                 # Environment variables template
├── pytest.ini                 # Pytest configuration
├── run_tests.py               # Test runner script
├── start_server.py            # Server startup script
└── README.md                  # This file
```

## 🚀 Deployment

### Development

```bash
# Start with auto-reload
DEBUG=true python start_server.py
```

### Production

```bash
# Start production server
python start_server.py
```

### Docker (Optional)

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "start_server.py"]
```

## 🔍 Monitoring

### Health Checks

Monitor service health via the `/health` endpoint:

```bash
curl http://localhost:8000/health
```

### Statistics

Get service statistics via the `/stats` endpoint:

```bash
curl http://localhost:8000/stats
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests before committing
python run_tests.py

# Check code style
flake8 dspy_prompt_fixer tests
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [DSPy](https://dspy.ai) for the prompt optimization framework
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- [Anthropic](https://anthropic.com/) for Claude API
- [Pytest](https://pytest.org/) for testing framework

## 📞 Support

For issues and questions:

1. Check the [API documentation](http://localhost:8000/docs) when running
2. Review the test files for usage examples
3. Open an issue on GitHub

---

**Happy coding! 🚀**
