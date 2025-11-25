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
    with open("web.html", "r", encoding="utf-8") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content, status_code=200)