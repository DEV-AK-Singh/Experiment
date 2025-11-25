from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os
import tempfile
from typing import Dict, Any, List

from text_utils import TextAnalyzer
from document_processor import DocumentProcessor

# Create FastAPI app
app = FastAPI(
    title="Advanced Text Analyzer", 
    version="2.0.0",
    description="Analyze text from various document types: PDF, DOCX, TXT"
)

# Create uploads directory
os.makedirs("uploads", exist_ok=True)

# Request model for text analysis
class TextAnalysisRequest(BaseModel):
    text: str

# Response models
class AnalysisResponse(BaseModel):
    word_count: int
    character_counts: Dict[str, int]
    sentence_count: int
    common_words: List[Dict[str, Any]]
    readability: Dict[str, float]
    paragraph_count: int
    longest_words: List[Dict[str, Any]]
    unique_words: int

class FileAnalysisResponse(BaseModel):
    word_count: int
    character_counts: Dict[str, int]
    sentence_count: int
    common_words: List[Dict[str, Any]]
    readability: Dict[str, float]
    paragraph_count: int
    longest_words: List[Dict[str, Any]]
    unique_words: int
    file_info: Dict[str, Any]
    document_info: Dict[str, Any]

@app.get("/")
def read_root():
    return {"message": "Welcome to Advanced Text Analyzer API - Supports PDF, DOCX, TXT"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/supported-formats")
def supported_formats():
    """List supported document formats"""
    return {
        "supported_formats": ["PDF", "DOCX", "TXT"],
        "max_file_size": "10MB",
        "features": [
            "Text extraction",
            "Word and character counting", 
            "Sentence analysis",
            "Common word identification",
            "Readability metrics",
            "Document statistics"
        ]
    }

@app.post("/analyze/text", response_model=AnalysisResponse)
async def analyze_text_direct(request: TextAnalysisRequest) -> AnalysisResponse:
    """
    Analyze text directly from request body
    
    - **text**: The text you want to analyze (required)
    
    Returns comprehensive text analysis including word count, character counts, 
    sentence count, common words, and readability metrics.
    """
    try:
        text = request.text
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        analysis = TextAnalyzer.analyze_text(text)
        return AnalysisResponse(**analysis)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/analyze/file", response_model=FileAnalysisResponse)
async def analyze_document_file(file: UploadFile = File(...)) -> FileAnalysisResponse:
    """
    Analyze text from uploaded document file
    
    - **file**: Document file to upload and analyze (supported: PDF, DOCX, TXT)
    
    Returns comprehensive analysis including document metadata and text statistics.
    """
    try:
        # Validate file type
        if not DocumentProcessor.is_supported_file_type(str(file.filename)):
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Supported: PDF, DOCX, TXT"
            )
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as temp_file:
            # Save uploaded file to temporary location
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        try:
            # Extract text from document
            extraction_result = DocumentProcessor.extract_text(temp_path, str(file.filename))
            text = extraction_result["text"]
            
            if not text.strip():
                raise HTTPException(status_code=400, detail="No text content found in document")
            
            # Analyze text
            analysis = TextAnalyzer.analyze_text(text)
            
            # Add file and document info
            analysis["file_info"] = {
                "filename": file.filename,
                "file_size": len(content),
                "content_type": file.content_type
            }
            
            analysis["document_info"] = {
                "file_type": extraction_result["file_type"],
                "page_count": extraction_result["page_count"],
                "extracted_word_count": extraction_result["word_count"],
                "extracted_character_count": extraction_result["character_count"]
            }
            
            return FileAnalysisResponse(**analysis)
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document analysis failed: {str(e)}")

@app.get("/demo")
async def demo_analysis():
    """
    Demo endpoint with sample text analysis
    
    Returns a pre-defined text analysis for demonstration purposes.
    """
    sample_text = """
    Artificial intelligence is transforming our world. 
    Machine learning algorithms can now recognize patterns in data that humans might miss.
    Natural language processing allows computers to understand and generate human language.
    This technology is being used in healthcare, finance, and education.
    The future of AI looks very promising indeed!
    """
    
    analysis = TextAnalyzer.analyze_text(sample_text)
    return {
        "sample_text": sample_text.strip(),
        "analysis": analysis
    }

# Enhanced web interface
@app.get("/web", response_class=HTMLResponse)
async def web_interface():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Advanced Text Analyzer</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
            .feature-list { background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0; }
            textarea { width: 100%; height: 200px; margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
            button { padding: 12px 25px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
            button:hover { background: #0056b3; }
            .result { margin-top: 20px; padding: 20px; background: #f8f9fa; border-radius: 5px; display: none; }
            .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
            .stat-card { background: white; padding: 15px; border-radius: 5px; border-left: 4px solid #007bff; }
            .file-info { background: #e7f3ff; padding: 15px; border-radius: 5px; margin: 15px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 Advanced Text Analyzer</h1>
            
            <div class="feature-list">
                <h3>✨ Supported Features:</h3>
                <p><strong>Document Types:</strong> PDF, DOCX, TXT</p>
                <p><strong>Analysis:</strong> Word count, character stats, sentence analysis, common words, readability scores, and more!</p>
            </div>
            
            <h3>📝 Analyze Direct Text:</h3>
            <textarea id="textInput" placeholder="Paste your text here...">Artificial intelligence is transforming various industries. Machine learning algorithms analyze vast amounts of data to identify patterns and make predictions. This technology enables computers to perform tasks that typically require human intelligence.</textarea>
            <button onclick="analyzeText()">Analyze Text</button>
            
            <h3>📄 Or Upload Document:</h3>
            <input type="file" id="fileInput" accept=".pdf,.docx,.txt,.doc">
            <button onclick="analyzeFile()">Analyze Document</button>
            <small>Supported: PDF, DOCX, TXT files (Max 10MB)</small>
            
            <div id="result" class="result"></div>
        </div>

        <script>
            async function analyzeText() {
                const text = document.getElementById('textInput').value;
                if (!text.trim()) {
                    alert('Please enter some text');
                    return;
                }

                showLoading();
                try {
                    const response = await fetch('/analyze/text', {
                        method: 'POST',
                        headers: { 
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ text: text })
                    });
                    
                    if (!response.ok) {
                        const error = await response.json();
                        throw new Error(error.detail || 'Analysis failed');
                    }
                    
                    const result = await response.json();
                    displayResult(result);
                } catch (error) {
                    showError(error.message);
                }
            }

            async function analyzeFile() {
                const fileInput = document.getElementById('fileInput');
                const file = fileInput.files[0];
                
                if (!file) {
                    alert('Please select a file');
                    return;
                }

                // Validate file type
                const fileName = file.name.toLowerCase();
                if (!fileName.endsWith('.pdf') && !fileName.endsWith('.docx') && !fileName.endsWith('.txt') && !fileName.endsWith('.doc')) {
                    alert('Please select a PDF, DOCX, or TXT file');
                    return;
                }

                showLoading();
                try {
                    const formData = new FormData();
                    formData.append('file', file);

                    const response = await fetch('/analyze/file', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (!response.ok) {
                        const error = await response.json();
                        throw new Error(error.detail || 'File analysis failed');
                    }
                    
                    const result = await response.json();
                    displayResult(result, true);
                } catch (error) {
                    showError(error.message);
                }
            }

            function showLoading() {
                const resultDiv = document.getElementById('result');
                resultDiv.style.display = 'block';
                resultDiv.innerHTML = '<p>⏳ Analyzing... Please wait.</p>';
            }

            function showError(message) {
                const resultDiv = document.getElementById('result');
                resultDiv.style.display = 'block';
                resultDiv.innerHTML = `<div style="color: red; background: #ffe6e6; padding: 15px; border-radius: 5px;">
                    <strong>Error:</strong> ${message}
                </div>`;
            }

            function displayResult(data, isFile = false) {
                const resultDiv = document.getElementById('result');
                resultDiv.style.display = 'block';
                
                let fileInfoHtml = '';
                if (isFile && data.file_info) {
                    fileInfoHtml = `
                        <div class="file-info">
                            <h4>📋 Document Information</h4>
                            <p><strong>File:</strong> ${data.file_info.filename}</p>
                            <p><strong>Size:</strong> ${(data.file_info.file_size / 1024).toFixed(2)} KB</p>
                            ${data.document_info ? `<p><strong>Type:</strong> ${data.document_info.file_type.toUpperCase()}</p>` : ''}
                            ${data.document_info ? `<p><strong>Pages:</strong> ${data.document_info.page_count}</p>` : ''}
                        </div>
                    `;
                }

                resultDiv.innerHTML = `
                    <h3>📊 Analysis Results</h3>
                    ${fileInfoHtml}
                    
                    <div class="stats-grid">
                        <div class="stat-card">
                            <strong>📝 Words</strong><br>
                            ${data.word_count}
                        </div>
                        <div class="stat-card">
                            <strong>🔤 Sentences</strong><br>
                            ${data.sentence_count}
                        </div>
                        <div class="stat-card">
                            <strong>📖 Paragraphs</strong><br>
                            ${data.paragraph_count}
                        </div>
                        <div class="stat-card">
                            <strong>✨ Unique Words</strong><br>
                            ${data.unique_words}
                        </div>
                    </div>

                    <div class="stats-grid">
                        <div class="stat-card">
                            <strong>🔢 Characters (with spaces)</strong><br>
                            ${data.character_counts.with_spaces}
                        </div>
                        <div class="stat-card">
                            <strong>🔡 Characters (no spaces)</strong><br>
                            ${data.character_counts.without_spaces}
                        </div>
                        <div class="stat-card">
                            <strong>⏱️ Reading Time</strong><br>
                            ${data.readability.reading_time_minutes} min
                        </div>
                        <div class="stat-card">
                            <strong>📐 Avg. Sentence Length</strong><br>
                            ${data.readability.average_sentence_length} words
                        </div>
                    </div>

                    <div style="margin: 20px 0;">
                        <h4>📈 Most Common Words</h4>
                        <ul>
                            ${data.common_words.map(word => 
                                `<li>"<strong>${word.word}</strong>" - ${word.count} times (${word.percentage}%)</li>`
                            ).join('')}
                        </ul>
                    </div>

                    <div style="margin: 20px 0;">
                        <h4>📏 Longest Words</h4>
                        <ul>
                            ${data.longest_words.map(word => 
                                `<li>"<strong>${word.word}</strong>" - ${word.length} characters</li>`
                            ).join('')}
                        </ul>
                    </div>
                `;
            }
            
            // Auto-analyze sample text on page load
            window.onload = function() {
                setTimeout(() => {
                    analyzeText();
                }, 1000);
            };
        </script>
    </body>
    </html>
    """