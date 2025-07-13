"""
파스칼 시스템 FastAPI 서버
원서 분석, 토론 주제 생성, DOCX 교재 생성을 위한 통합 API 서버
"""

import os
import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
import pandas as pd
import json
from pathlib import Path

# 로컬 모듈 import
from book_analyzer import BookAnalyzer, BookInfo, EducationLevel, EducationArea
from topic_generator import TopicGenerator
from docx_generator import DOCXGenerator, DocumentSettings

# FastAPI 앱 초기화
app = FastAPI(
    title="Pascal Debate Textbook System",
    description="AI-powered system for generating debate topics and textbooks from English books",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 변수
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
UPLOAD_FOLDER = Path("./uploads")
OUTPUT_FOLDER = Path("./outputs")

# 폴더 생성
UPLOAD_FOLDER.mkdir(exist_ok=True)
OUTPUT_FOLDER.mkdir(exist_ok=True)

# 분석 작업 상태 저장
analysis_tasks: Dict[str, Dict[str, Any]] = {}
generation_tasks: Dict[str, Dict[str, Any]] = {}

# 서비스 인스턴스
book_analyzer = None
topic_generator = None

@app.on_event("startup")
async def startup_event():
    """서버 시작 시 초기화"""
    global book_analyzer, topic_generator
    
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY environment variable not set")
    
    book_analyzer = BookAnalyzer(OPENAI_API_KEY)
    topic_generator = TopicGenerator(OPENAI_API_KEY)

# Pydantic 모델 정의
class BookInfoRequest(BaseModel):
    title: str = Field(..., description="Book title")
    author: str = Field(..., description="Book author")
    ar_level: float = Field(..., ge=1.0, le=10.0, description="AR reading level")
    pages: Optional[int] = Field(None, description="Number of pages")
    genre: Optional[str] = Field(None, description="Book genre")
    publication_year: Optional[int] = Field(None, description="Publication year")
    isbn: Optional[str] = Field(None, description="ISBN")
    summary: Optional[str] = Field(None, description="Book summary")

class DocumentSettingsRequest(BaseModel):
    title: str = Field(..., description="Document title")
    subtitle: str = Field(..., description="Document subtitle")
    author: str = Field(..., description="Document author")
    institution: str = Field(..., description="Institution name")
    level: str = Field(..., description="Education level (preparation/regular/mastery)")

class AnalysisStatusResponse(BaseModel):
    task_id: str
    status: str  # "pending", "processing", "completed", "failed"
    progress: float  # 0.0 to 1.0
    message: str
    result: Optional[Dict[str, Any]] = None

class GenerationStatusResponse(BaseModel):
    task_id: str
    status: str
    progress: float
    message: str
    download_url: Optional[str] = None

# API 엔드포인트

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "Pascal Debate Textbook System API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "book_analyzer": book_analyzer is not None,
            "topic_generator": topic_generator is not None
        }
    }

@app.post("/api/v1/books/analyze")
async def analyze_book(
    book_info: BookInfoRequest,
    background_tasks: BackgroundTasks
):
    """원서 분석 시작"""
    task_id = str(uuid.uuid4())
    
    # 작업 상태 초기화
    analysis_tasks[task_id] = {
        "status": "pending",
        "progress": 0.0,
        "message": "Analysis task created",
        "created_at": datetime.now(),
        "book_info": book_info.dict()
    }
    
    # 백그라운드에서 분석 실행
    background_tasks.add_task(run_book_analysis, task_id, book_info)
    
    return {
        "task_id": task_id,
        "message": "Book analysis started",
        "estimated_time": "2-3 minutes"
    }

@app.get("/api/v1/books/analyze/{task_id}/status")
async def get_analysis_status(task_id: str) -> AnalysisStatusResponse:
    """분석 상태 조회"""
    if task_id not in analysis_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = analysis_tasks[task_id]
    return AnalysisStatusResponse(
        task_id=task_id,
        status=task["status"],
        progress=task["progress"],
        message=task["message"],
        result=task.get("result")
    )

@app.get("/api/v1/books/analyze/{task_id}/result")
async def get_analysis_result(task_id: str):
    """분석 결과 조회"""
    if task_id not in analysis_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = analysis_tasks[task_id]
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="Analysis not completed yet")
    
    return task["result"]

@app.get("/api/v1/books/analyze/{task_id}/csv")
async def download_analysis_csv(task_id: str):
    """분석 결과 CSV 다운로드"""
    if task_id not in analysis_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = analysis_tasks[task_id]
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="Analysis not completed yet")
    
    csv_path = task.get("csv_path")
    if not csv_path or not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="CSV file not found")
    
    return FileResponse(
        csv_path,
        media_type="text/csv",
        filename=f"analysis_{task_id}.csv"
    )

@app.post("/api/v1/documents/generate")
async def generate_document(
    background_tasks: BackgroundTasks,
    csv_file: UploadFile = File(...),
    settings: str = None  # JSON string
):
    """DOCX 문서 생성"""
    task_id = str(uuid.uuid4())
    
    try:
        # 설정 파싱
        if settings:
            settings_dict = json.loads(settings)
            doc_settings = DocumentSettingsRequest(**settings_dict)
        else:
            # 기본 설정
            doc_settings = DocumentSettingsRequest(
                title="파스칼 토론 교재",
                subtitle="AI 생성 토론 주제 모음",
                author="파스칼 시스템",
                institution="파스칼 교육원",
                level="regular"
            )
        
        # CSV 파일 저장
        csv_path = UPLOAD_FOLDER / f"input_{task_id}.csv"
        with open(csv_path, "wb") as buffer:
            content = await csv_file.read()
            buffer.write(content)
        
        # 작업 상태 초기화
        generation_tasks[task_id] = {
            "status": "pending",
            "progress": 0.0,
            "message": "Document generation task created",
            "created_at": datetime.now(),
            "csv_path": str(csv_path),
            "settings": doc_settings.dict()
        }
        
        # 백그라운드에서 문서 생성 실행
        background_tasks.add_task(run_document_generation, task_id, str(csv_path), doc_settings)
        
        return {
            "task_id": task_id,
            "message": "Document generation started",
            "estimated_time": "1-2 minutes"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to start document generation: {str(e)}")

@app.get("/api/v1/documents/{task_id}/status")
async def get_generation_status(task_id: str) -> GenerationStatusResponse:
    """문서 생성 상태 조회"""
    if task_id not in generation_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = generation_tasks[task_id]
    download_url = None
    
    if task["status"] == "completed" and "output_path" in task:
        download_url = f"/api/v1/documents/{task_id}/download"
    
    return GenerationStatusResponse(
        task_id=task_id,
        status=task["status"],
        progress=task["progress"],
        message=task["message"],
        download_url=download_url
    )

@app.get("/api/v1/documents/{task_id}/download")
async def download_document(task_id: str):
    """생성된 문서 다운로드"""
    if task_id not in generation_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = generation_tasks[task_id]
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="Document generation not completed yet")
    
    output_path = task.get("output_path")
    if not output_path or not os.path.exists(output_path):
        raise HTTPException(status_code=404, detail="Document file not found")
    
    return FileResponse(
        output_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=f"textbook_{task_id}.docx"
    )

@app.get("/api/v1/tasks")
async def list_tasks():
    """모든 작업 목록 조회"""
    return {
        "analysis_tasks": len(analysis_tasks),
        "generation_tasks": len(generation_tasks),
        "total_tasks": len(analysis_tasks) + len(generation_tasks)
    }

@app.delete("/api/v1/tasks/cleanup")
async def cleanup_old_tasks():
    """오래된 작업 정리"""
    current_time = datetime.now()
    cleanup_count = 0
    
    # 24시간 이상 된 작업 삭제
    for task_id in list(analysis_tasks.keys()):
        task = analysis_tasks[task_id]
        if (current_time - task["created_at"]).total_seconds() > 86400:  # 24시간
            del analysis_tasks[task_id]
            cleanup_count += 1
    
    for task_id in list(generation_tasks.keys()):
        task = generation_tasks[task_id]
        if (current_time - task["created_at"]).total_seconds() > 86400:  # 24시간
            del generation_tasks[task_id]
            cleanup_count += 1
    
    return {
        "message": f"Cleaned up {cleanup_count} old tasks",
        "remaining_tasks": len(analysis_tasks) + len(generation_tasks)
    }

# 백그라운드 작업 함수

async def run_book_analysis(task_id: str, book_info: BookInfoRequest):
    """백그라운드에서 원서 분석 실행"""
    try:
        # 상태 업데이트
        analysis_tasks[task_id]["status"] = "processing"
        analysis_tasks[task_id]["progress"] = 0.1
        analysis_tasks[task_id]["message"] = "Starting book analysis..."
        
        # BookInfo 객체 생성
        book = BookInfo(
            title=book_info.title,
            author=book_info.author,
            ar_level=book_info.ar_level,
            pages=book_info.pages,
            genre=book_info.genre,
            publication_year=book_info.publication_year,
            isbn=book_info.isbn,
            summary=book_info.summary
        )
        
        # 분석 실행
        analysis_tasks[task_id]["progress"] = 0.3
        analysis_tasks[task_id]["message"] = "Analyzing book content..."
        
        result = await book_analyzer.analyze_book(book)
        
        # CSV 내보내기
        analysis_tasks[task_id]["progress"] = 0.8
        analysis_tasks[task_id]["message"] = "Exporting results to CSV..."
        
        csv_path = OUTPUT_FOLDER / f"analysis_{task_id}.csv"
        book_analyzer.export_to_csv(result, str(csv_path))
        
        # 결과 저장
        analysis_tasks[task_id]["status"] = "completed"
        analysis_tasks[task_id]["progress"] = 1.0
        analysis_tasks[task_id]["message"] = "Analysis completed successfully"
        analysis_tasks[task_id]["csv_path"] = str(csv_path)
        analysis_tasks[task_id]["result"] = {
            "analysis_id": result.analysis_id,
            "overall_score": result.overall_assessment["overall_score"],
            "topics_generated": result.overall_assessment["total_topics_generated"],
            "best_areas": result.overall_assessment["best_areas"],
            "book_info": {
                "title": result.book_info.title,
                "author": result.book_info.author,
                "ar_level": result.book_info.ar_level,
                "education_level": result.book_info.get_education_level().value
            }
        }
        
    except Exception as e:
        analysis_tasks[task_id]["status"] = "failed"
        analysis_tasks[task_id]["message"] = f"Analysis failed: {str(e)}"
        print(f"Analysis error for task {task_id}: {e}")

async def run_document_generation(task_id: str, csv_path: str, settings: DocumentSettingsRequest):
    """백그라운드에서 문서 생성 실행"""
    try:
        # 상태 업데이트
        generation_tasks[task_id]["status"] = "processing"
        generation_tasks[task_id]["progress"] = 0.1
        generation_tasks[task_id]["message"] = "Starting document generation..."
        
        # DocumentSettings 객체 생성
        doc_settings = DocumentSettings(
            title=settings.title,
            subtitle=settings.subtitle,
            author=settings.author,
            institution=settings.institution,
            level=EducationLevel(settings.level),
            book_title="Unknown",  # CSV에서 추출 예정
            book_author="Unknown",  # CSV에서 추출 예정
            ar_level=0.0,  # CSV에서 추출 예정
            creation_date=datetime.now()
        )
        
        # CSV에서 도서 정보 추출
        generation_tasks[task_id]["progress"] = 0.2
        generation_tasks[task_id]["message"] = "Reading CSV data..."
        
        df = pd.read_csv(csv_path)
        if not df.empty:
            doc_settings.book_title = df.iloc[0].get("Book_Title", "Unknown")
            doc_settings.book_author = df.iloc[0].get("Book_Author", "Unknown")
            doc_settings.ar_level = df.iloc[0].get("AR_Level", 0.0)
        
        # 문서 생성
        generation_tasks[task_id]["progress"] = 0.5
        generation_tasks[task_id]["message"] = "Generating DOCX document..."
        
        generator = DOCXGenerator()
        output_path = OUTPUT_FOLDER / f"textbook_{task_id}.docx"
        
        result_path = generator.generate_textbook(csv_path, str(output_path), doc_settings)
        
        # 완료
        generation_tasks[task_id]["status"] = "completed"
        generation_tasks[task_id]["progress"] = 1.0
        generation_tasks[task_id]["message"] = "Document generated successfully"
        generation_tasks[task_id]["output_path"] = result_path
        
    except Exception as e:
        generation_tasks[task_id]["status"] = "failed"
        generation_tasks[task_id]["message"] = f"Document generation failed: {str(e)}"
        print(f"Generation error for task {task_id}: {e}")

# 개발용 엔드포인트
@app.get("/api/v1/test/sample-analysis")
async def get_sample_analysis():
    """샘플 분석 결과 반환 (테스트용)"""
    return {
        "book_info": {
            "title": "Charlotte's Web",
            "author": "E.B. White",
            "ar_level": 4.4
        },
        "analysis_result": {
            "overall_score": 7.17,
            "topics_generated": 15,
            "best_areas": ["Literature & Identity", "Human & Society", "Future & Careers"]
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
