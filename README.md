# Text Paraphraser & Expander

A production-ready Python application for text paraphrasing and expansion using transformer models. This application provides a clean, modular architecture with a Gradio web interface for easy interaction.

## Features

- **Text Paraphrasing**: Rewrite text while preserving meaning using multiple T5-based models
- **Text Expansion**: Expand text with additional details and context using Flan-T5 models
- **Quality Metrics**: Analyze grammar, readability, logical flow, and punctuation
- **Visual Comparison**: Side-by-side comparison with highlighted differences
- **CSV Logging**: Track all processing results with detailed statistics
- **Modular Architecture**: Clean, production-ready code structure

## Project Structure

```
humanize/
├── src/
│   ├── models/          # Model loading and configuration
│   ├── processing/       # Text processing logic
│   ├── quality/          # Quality assessment metrics
│   ├── visualization/   # HTML formatting and diff highlighting
│   ├── logging/          # CSV logging functionality
│   ├── ui/              # Gradio interface
│   └── config/           # Configuration management
├── app.py               # Main application entry point
├── requirements.txt     # Python dependencies
└── .env.example         # Environment variables template
```

## Installation

1. **Clone the repository** (or navigate to the project directory)

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv .venv
   .venv/Scripts/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your preferred settings
   ```

## Usage

### Running the Application

```bash
python app.py
```

The application will start a Gradio web interface. By default, it will be available at `http://localhost:7860`.

### Configuration

Edit the `.env` file to customize:

- **CSV_LOG_PATH**: Where to save processing logs
- **MODEL_CACHE_DIR**: Optional directory for caching models
- **LANGUAGE_TOOL_LANG**: Language for grammar checking
- **GRADIO_SERVER_PORT**: Port for the web interface
- **LOG_LEVEL**: Logging verbosity (DEBUG, INFO, WARNING, ERROR)

### Available Models

**Paraphrase Models:**
- ChatGPT-Style-T5 (humarin/chatgpt_paraphraser_on_T5_base)

**Expansion Models:**
- Flan-T5-Base (google/flan-t5-base)
- Flan-T5-Large (google/flan-t5-large)

## Features in Detail

### Text Processing
- Automatic text chunking for long inputs
- Dynamic max_length calculation based on input size
- Configurable generation parameters (temperature, top_p, beams)

### Quality Assessment
- **Grammar Checking**: Uses LanguageTool for grammar and punctuation
- **Readability Score**: Flesch Reading Ease calculation
- **Logical Flow**: Sentence coherence using cosine similarity
- **Comparative Analysis**: Input vs. output quality comparison

### Visualization
- Word-level difference highlighting
- Change statistics (added, removed, modified words)
- Quality metrics comparison table
- HTML-formatted output

### Logging
- All processing results logged to CSV
- Includes timestamps, model used, quality metrics, and statistics
- Thread-safe CSV writing

## Development

### Code Structure

The project follows a modular architecture:

- **Models**: Model loading and caching with singleton pattern
- **Processing**: Core paraphrasing/expansion logic
- **Quality**: Metrics calculation and similarity scoring
- **Visualization**: HTML formatting and diff highlighting
- **Logging**: CSV logging with thread safety
- **UI**: Gradio interface separated from business logic
- **Config**: Environment-based configuration management

### Adding New Models

Edit `src/models/model_config.py` to add new models:

```python
PARAPHRASE_MODELS = {
    "Your-Model": "huggingface/model-path",
}
```

### Extending Functionality

The modular design makes it easy to:
- Add new quality metrics in `src/quality/metrics.py`
- Customize visualization in `src/visualization/`
- Add new processing modes in `src/processing/`

## Requirements

- Python 3.8+
- PyTorch (with CUDA support optional)
- See `requirements.txt` for full dependency list

## License

This project is provided as-is for educational and development purposes.

## Notes

- First run will download models from HuggingFace (can be large)
- GPU recommended for faster processing, but CPU is supported
- LanguageTool can be used locally or remotely (configure in .env)
- CSV logs are automatically created in the configured directory


