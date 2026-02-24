"""Gradio UI interface"""

import logging
import traceback
from pathlib import Path
import gradio as gr
from typing import Tuple, Optional

from ..models.model_config import PARAPHRASE_MODELS, EXPANSION_MODELS
from ..processing.paraphraser import Paraphraser
from ..quality.metrics import QualityMetrics
from ..visualization.diff_highlighter import DiffHighlighter
from ..visualization.html_formatter import HTMLFormatter
from ..logging.csv_logger import CSVLogger

logger = logging.getLogger(__name__)


def update_model_choices(mode: str) -> gr.Dropdown:
    """Update model dropdown based on selected mode"""
    if mode == "Paraphrase":
        choices = list(PARAPHRASE_MODELS.keys())
    else:
        choices = list(EXPANSION_MODELS.keys())
    return gr.Dropdown(choices=choices, value=choices[0])


def update_parameters_visibility(mode: str) -> gr.Number:
    """Show/hide target words parameter based on mode"""
    if mode == "Expand":
        return gr.Number(visible=True)
    else:
        return gr.Number(visible=False)


def handle_file_upload(file) -> Tuple[str, str, str]:
    """
    Handle markdown file upload
    
    Args:
        file: Uploaded file object from Gradio
        
    Returns:
        Tuple of (file_content, file_info, error_message)
    """
    from ..processing.file_processor import FileProcessor
    
    if file is None:
        return "", "", ""
    
    try:
        # Get file path from Gradio file object
        file_path = file.name if hasattr(file, 'name') else str(file)
        
        # Read and validate markdown file
        content, error = FileProcessor.read_markdown_file(file_path)
        
        if error:
            logger.error(f"File upload error: {error}")
            return "", "", f"❌ {error}"
        
        # Save a copy to uploads directory
        from ..config.settings import Settings
        saved_path, save_error = FileProcessor.save_markdown_file(
            content, 
            file_path, 
            Settings.UPLOADS_DIR
        )
        
        if save_error:
            logger.warning(f"Could not save copy of upload: {save_error}")
            save_msg = f"✅ Loaded, but could not save copy."
        else:
            save_msg = f"✅ Loaded and saved to: {Path(saved_path).name}"
        
        # Get file info
        file_info = FileProcessor.get_file_info(file_path)
        
        logger.info(f"File uploaded and saved successfully: {file_path}")
        return content, file_info, save_msg
        
    except Exception as e:
        logger.error(f"Unexpected error in file upload: {str(e)}", exc_info=True)
        return "", "", f"❌ Error: {str(e)}"


def process_text(
    input_text: str,
    mode: str,
    model_name: str,
    temperature: float,
    top_p: float,
    max_length: int,
    num_beams: int,
    max_sentences: int,
    target_words: int,
    markdown_mode: bool = False
) -> Tuple[str, str, float, str, str, str, str, Optional[str]]:
    """
    Main processing function with Comparative Quality Metrics
    
    Returns:
        Tuple of (output_text, basic_stats, similarity, highlighted_original,
                 highlighted_generated, stats_html, quality_html, result_file_path)
    """
    try:
        # Initialize components
        paraphraser = Paraphraser()
        quality_metrics = QualityMetrics()
        diff_highlighter = DiffHighlighter()
        html_formatter = HTMLFormatter()
        csv_logger = CSVLogger()
        
        # Analyze INPUT Quality
        input_metrics = quality_metrics.calculate(input_text)
        
        # Generate Paraphrased/Expanded Text
        if markdown_mode:
            # Use markdown-aware processing
            logger.info("Using markdown-aware processing")
            output_text, similarity = paraphraser.process_markdown(
                input_text,
                model_name,
                temperature,
                top_p,
                max_length,
                num_beams,
                max_sentences,
                target_words,
                mode
            )
        else:
            # Use standard processing
            output_text, similarity = paraphraser.process_text(
                input_text,
                model_name,
                temperature,
                top_p,
                max_length,
                num_beams,
                max_sentences,
                target_words,
                mode
            )
        
        # Analyze OUTPUT Quality
        output_metrics = quality_metrics.calculate(output_text)
        
        word_count_original = len(input_text.split())
        word_count_output = len(output_text.split())
        
        # Generate highlighted comparison
        highlighted_original, highlighted_generated, statistics = (
            diff_highlighter.highlight_differences(input_text, output_text)
        )
        
        # Format change statistics
        stats_html = html_formatter.format_statistics(statistics)
        
        # Log to CSV
        csv_logger.log_result(
            input_text,
            output_text,
            similarity,
            statistics,
            output_metrics,
            model_name,
            mode
        )
        
        # Comparative Quality HTML
        quality_html = html_formatter.format_quality_comparison(
            input_metrics,
            output_metrics
        )
        
        # Save refined result if in markdown mode or if requested
        from ..config.settings import Settings
        from ..processing.file_processor import FileProcessor
        
        result_file_path = None
        if markdown_mode:
            saved_result_path, result_save_error = FileProcessor.save_markdown_file(
                output_text,
                "refined_output.md",
                Settings.RESULTS_DIR
            )
            if not result_save_error:
                result_file_path = saved_result_path
                logger.info(f"Result saved to: {result_file_path}")
        
        # Basic stats line
        basic_stats = (
            f"**Original:** {word_count_original} words | "
            f"**Generated:** {word_count_output} words | "
            f"**Similarity:** {similarity:.4f}"
        )
        
        return (
            output_text,
            basic_stats,
            similarity,
            highlighted_original,
            highlighted_generated,
            stats_html,
            quality_html,
            result_file_path
        )
        
    except Exception as e:
        error_msg = f"Error: {str(e)}\n\n{traceback.format_exc()}"
        logger.error(error_msg, exc_info=True)
        return error_msg, "Error occurred", 0.0, "", "", "", "", None


def create_gradio_interface() -> gr.Blocks:
    """Create and configure Gradio interface"""
    
    with gr.Blocks(title="Text Paraphraser & Expander") as demo:
        gr.Markdown(
            """
            # 📝 Text Paraphraser & Expander
            Transform your text with AI-powered paraphrasing and expansion capabilities.
            """
        )
        
        with gr.Row():
            with gr.Column(scale=1):
                mode = gr.Radio(
                    choices=["Paraphrase", "Expand"],
                    value="Paraphrase",
                    label="Mode",
                    info="Choose to paraphrase or expand your text"
                )
                
                # File upload section
                gr.Markdown("### 📂 Upload Markdown File (Optional)")
                file_upload = gr.File(
                    label="Upload .md file",
                    file_types=[".md"],
                    type="filepath"
                )
                file_info_display = gr.Markdown("", visible=False)
                file_status = gr.Markdown("", visible=False)
                
                markdown_mode_checkbox = gr.Checkbox(
                    label="Preserve Markdown Structure",
                    value=False,
                    info="Keep headings, links, and code blocks intact (auto-enabled for file uploads)"
                )
                
                model_dropdown = gr.Dropdown(
                    choices=list(PARAPHRASE_MODELS.keys()),
                    value=list(PARAPHRASE_MODELS.keys())[0],
                    label="Model Selection",
                    info="Choose the model for processing"
                )
                
                gr.Markdown("### ⚙️ Parameters")
                
                temperature = gr.Slider(
                    minimum=0.0,
                    maximum=2.0,
                    value=0.5,
                    step=0.1,
                    label="Temperature",
                    info="Higher = more creative, Lower = more focused"
                )
                
                top_p = gr.Slider(
                    minimum=0.1,
                    maximum=1.0,
                    value=0.9,
                    step=0.05,
                    label="Top-p (Nucleus Sampling)",
                    info="Probability threshold for token selection"
                )
                
                max_length = gr.Slider(
                    minimum=128,
                    maximum=1024,
                    value=512,
                    step=32,
                    label="Max Length (tokens)",
                    info="Maximum length of generated text per chunk"
                )
                
                num_beams = gr.Slider(
                    minimum=1,
                    maximum=10,
                    value=4,
                    step=1,
                    label="Number of Beams",
                    info="Higher = better quality but slower"
                )
                
                max_sentences = gr.Slider(
                    minimum=1,
                    maximum=10,
                    value=4,
                    step=1,
                    label="Sentences per Chunk",
                    info="Number of sentences to process together"
                )
                
                target_words = gr.Number(
                    value=300,
                    label="Target Word Count (Expand mode)",
                    info="Approximate number of words for expansion",
                    visible=False
                )
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 📥 Input Text")
                input_text = gr.Textbox(
                    lines=10,
                    placeholder="Enter your text here...",
                    label="Original Text"
                )
            
            with gr.Column(scale=1):
                gr.Markdown("### 📤 Generated Text")
                output_text = gr.Textbox(
                    lines=10,
                    label="Processed Text"
                )
                
                # Result download component
                result_download = gr.File(
                    label="📥 Download Refined Markdown",
                    interactive=False,
                    visible=False
                )
        
        with gr.Row():
            process_btn = gr.Button("🚀 Generate", variant="primary", size="lg")
            clear_btn = gr.ClearButton(
                [input_text, output_text, file_upload, result_download],
                value="🗑️ Clear"
            )
        
        stats_display = gr.Markdown()
        
        similarity_display = gr.Number(
            label="Cosine Similarity Score",
            precision=4,
            interactive=False
        )
        
        # Highlighted comparison section
        gr.Markdown("---")
        gr.Markdown("## 🔍 Visual Comparison - See What Changed")
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 📄 Original Text (with changes highlighted)")
                highlighted_original = gr.HTML(
                    label="Original with Changes",
                    show_label=False
                )
            
            with gr.Column(scale=1):
                gr.Markdown("### ✨ Generated Text (with changes highlighted)")
                highlighted_generated = gr.HTML(
                    label="Generated with Changes",
                    show_label=False
                )
        
        change_stats = gr.HTML(label="Change Statistics")
        quality_stats = gr.HTML(label="Quality Analysis")
        
        # Event handlers
        # File upload handler
        file_upload.change(
            fn=handle_file_upload,
            inputs=[file_upload],
            outputs=[input_text, file_info_display, file_status]
        ).then(
            fn=lambda info, status: (
                gr.Markdown(value=info, visible=bool(info)),
                gr.Markdown(value=status, visible=bool(status)),
                True  # Auto-enable markdown mode for file uploads
            ),
            inputs=[file_info_display, file_status],
            outputs=[file_info_display, file_status, markdown_mode_checkbox]
        )
        
        mode.change(
            fn=update_model_choices,
            inputs=[mode],
            outputs=[model_dropdown]
        )
        
        mode.change(
            fn=update_parameters_visibility,
            inputs=[mode],
            outputs=[target_words]
        )
        
        process_btn.click(
            fn=process_text,
            inputs=[
                input_text,
                mode,
                model_dropdown,
                temperature,
                top_p,
                max_length,
                num_beams,
                max_sentences,
                target_words,
                markdown_mode_checkbox
            ],
            outputs=[
                output_text,
                stats_display,
                similarity_display,
                highlighted_original,
                highlighted_generated,
                change_stats,
                quality_stats,
                result_download
            ]
        ).then(
            fn=lambda x: gr.File(visible=bool(x)),
            inputs=[result_download],
            outputs=[result_download]
        )
        
        gr.Markdown(
            """
            ---
            ### 💡 Tips:
            - **File Upload**: Upload `.md` files to process markdown content with structure preservation
            - **Download Results**: Refined markdown will be available for download after generation
            - **File Storage**: Uploaded files are saved to `data/uploads/` and refined files to `data/results/`
            - **Markdown Mode**: When enabled, headings, links, and code blocks remain unchanged
            - **Paraphrase Mode**: Rewrites text while preserving meaning
            - **Expand Mode**: Adds details and elaboration to make text longer
            - **Sentences per Chunk**: Controls how many sentences are processed together (4 recommended)
            - Adjust temperature for creativity (0.7-1.0 for paraphrase, 1.0-1.5 for expansion)
            - Higher beam count = better quality but slower processing
            - Max length is automatically calculated based on input, but can be overridden
            - Output chunks are separated by double newlines for readability
            """
        )
    
    return demo

