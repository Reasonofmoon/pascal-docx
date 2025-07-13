"""
파스칼 원서 분석 모듈
영어 원서 정보를 입력받아 6개 핵심 영역별로 분석하고 토론 주제를 생성하는 모듈
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import openai
from openai import AsyncOpenAI
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EducationLevel(str, Enum):
    """교육 레벨 정의"""
    PREPARATION = "preparation"  # AR 4.0-4.5
    REGULAR = "regular"          # AR 4.6-5.2
    MASTERY = "mastery"          # AR 5.3-5.7

class EducationArea(str, Enum):
    """6개 핵심 교육 영역"""
    SCIENCE_TECHNOLOGY = "Science & Technology"
    HUMAN_SOCIETY = "Human & Society"
    FUTURE_CAREERS = "Future & Careers"
    LITERATURE_IDENTITY = "Literature & Identity"
    MATHEMATICAL_THINKING = "Mathematical Thinking"
    ECONOMICS_GLOBAL_CITIZENSHIP = "Economics & Global Citizenship"

@dataclass
class BookInfo:
    """원서 기본 정보"""
    title: str
    author: str
    ar_level: float
    pages: Optional[int] = None
    genre: Optional[str] = None
    publication_year: Optional[int] = None
    isbn: Optional[str] = None
    summary: Optional[str] = None
    
    def get_education_level(self) -> EducationLevel:
        """AR 지수를 기반으로 교육 레벨 결정"""
        if self.ar_level <= 4.5:
            return EducationLevel.PREPARATION
        elif self.ar_level <= 5.2:
            return EducationLevel.REGULAR
        else:
            return EducationLevel.MASTERY

@dataclass
class AreaAnalysis:
    """영역별 분석 결과"""
    area: EducationArea
    relevance_score: float  # 0-10 점수
    key_themes: List[str]
    discussion_points: List[str]
    vocabulary_focus: List[str]
    cultural_context: List[str]
    korean_connection: List[str]

@dataclass
class DebateTopicSet:
    """토론 주제 세트"""
    topic_id: str
    title: str
    description: str
    level: EducationLevel
    area: EducationArea
    debate_format: str  # "character_comparison", "moral_judgment", "issue_analysis"
    pro_arguments: List[str]
    con_arguments: List[str]
    background_info: str
    vocabulary_list: List[str]
    time_estimate: int  # 분 단위

@dataclass
class BookAnalysisResult:
    """전체 분석 결과"""
    book_info: BookInfo
    analysis_id: str
    analysis_date: datetime
    area_analyses: List[AreaAnalysis]
    debate_topics: List[DebateTopicSet]
    overall_assessment: Dict[str, Any]

class BookAnalyzer:
    """원서 분석 및 토론 주제 생성 클래스"""
    
    def __init__(self, openai_api_key: str):
        self.client = AsyncOpenAI(api_key=openai_api_key)
        self.analysis_cache = {}
        
    async def analyze_book(self, book_info: BookInfo) -> BookAnalysisResult:
        """원서 종합 분석 수행"""
        logger.info(f"Starting analysis for book: {book_info.title}")
        
        # 1. 외부 데이터 수집
        enhanced_book_info = await self._enhance_book_info(book_info)
        
        # 2. 6개 영역별 분석
        area_analyses = await self._analyze_by_areas(enhanced_book_info)
        
        # 3. 토론 주제 생성
        debate_topics = await self._generate_debate_topics(enhanced_book_info, area_analyses)
        
        # 4. 전체 평가
        overall_assessment = await self._generate_overall_assessment(
            enhanced_book_info, area_analyses, debate_topics
        )
        
        # 5. 결과 구성
        analysis_result = BookAnalysisResult(
            book_info=enhanced_book_info,
            analysis_id=f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            analysis_date=datetime.now(),
            area_analyses=area_analyses,
            debate_topics=debate_topics,
            overall_assessment=overall_assessment
        )
        
        logger.info(f"Analysis completed for book: {book_info.title}")
        return analysis_result
    
    async def _enhance_book_info(self, book_info: BookInfo) -> BookInfo:
        """외부 API를 통한 도서 정보 보강"""
        try:
            # Google Books API 또는 Goodreads API 호출 시뮬레이션
            # 실제 구현에서는 실제 API 호출
            enhanced_info = book_info
            
            if not enhanced_info.summary:
                enhanced_info.summary = await self._generate_summary_from_title(book_info)
            
            return enhanced_info
        except Exception as e:
            logger.warning(f"Failed to enhance book info: {e}")
            return book_info
    
    async def _generate_summary_from_title(self, book_info: BookInfo) -> str:
        """제목과 저자를 기반으로 줄거리 생성"""
        prompt = f"""
        Please provide a brief summary of the book "{book_info.title}" by {book_info.author}.
        Focus on the main plot, key characters, and central themes.
        Keep it concise (2-3 paragraphs).
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            return "Summary not available"
    
    async def _analyze_by_areas(self, book_info: BookInfo) -> List[AreaAnalysis]:
        """6개 영역별 분석 수행"""
        analyses = []
        
        for area in EducationArea:
            analysis = await self._analyze_single_area(book_info, area)
            analyses.append(analysis)
        
        return analyses
    
    async def _analyze_single_area(self, book_info: BookInfo, area: EducationArea) -> AreaAnalysis:
        """단일 영역 분석"""
        area_prompts = {
            EducationArea.SCIENCE_TECHNOLOGY: """
            Analyze this book from a Science & Technology perspective:
            - Scientific thinking and methodology
            - Technology's impact on society
            - Innovation and discovery themes
            - Ethical considerations in science/tech
            """,
            EducationArea.HUMAN_SOCIETY: """
            Analyze this book from a Human & Society perspective:
            - Social relationships and conflicts
            - Community vs individual needs
            - Cultural diversity and inclusion
            - Social justice and equality themes
            """,
            EducationArea.FUTURE_CAREERS: """
            Analyze this book from a Future & Careers perspective:
            - Skills and competencies for the future
            - Career exploration and development
            - Entrepreneurship and innovation
            - Global career opportunities
            """,
            EducationArea.LITERATURE_IDENTITY: """
            Analyze this book from a Literature & Identity perspective:
            - Character development and identity
            - Cultural identity and belonging
            - Personal growth and self-discovery
            - Literary themes and symbolism
            """,
            EducationArea.MATHEMATICAL_THINKING: """
            Analyze this book from a Mathematical Thinking perspective:
            - Logical reasoning and problem-solving
            - Pattern recognition and analysis
            - Systematic thinking approaches
            - Mathematical concepts in daily life
            """,
            EducationArea.ECONOMICS_GLOBAL_CITIZENSHIP: """
            Analyze this book from an Economics & Global Citizenship perspective:
            - Economic systems and decision-making
            - Global interconnectedness
            - Social responsibility and sustainability
            - Cross-cultural understanding
            """
        }
        
        prompt = f"""
        Book: "{book_info.title}" by {book_info.author}
        AR Level: {book_info.ar_level}
        Summary: {book_info.summary or 'Not available'}
        
        {area_prompts[area]}
        
        Please provide analysis in the following JSON format:
        {{
            "relevance_score": <0-10 score>,
            "key_themes": [<list of 3-5 key themes>],
            "discussion_points": [<list of 4-6 discussion points>],
            "vocabulary_focus": [<list of 10-15 key vocabulary words>],
            "cultural_context": [<list of cultural elements>],
            "korean_connection": [<list of connections to Korean context>]
        }}
        
        Focus on educational value for Korean students learning English through debate.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.3
            )
            
            result_text = response.choices[0].message.content.strip()
            # JSON 파싱
            if result_text.startswith("```json"):
                result_text = result_text[7:-3]
            elif result_text.startswith("```"):
                result_text = result_text[3:-3]
            
            result_data = json.loads(result_text)
            
            return AreaAnalysis(
                area=area,
                relevance_score=result_data["relevance_score"],
                key_themes=result_data["key_themes"],
                discussion_points=result_data["discussion_points"],
                vocabulary_focus=result_data["vocabulary_focus"],
                cultural_context=result_data["cultural_context"],
                korean_connection=result_data["korean_connection"]
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze area {area}: {e}")
            # 기본값 반환
            return AreaAnalysis(
                area=area,
                relevance_score=5.0,
                key_themes=["General themes"],
                discussion_points=["General discussion points"],
                vocabulary_focus=["vocabulary"],
                cultural_context=["cultural elements"],
                korean_connection=["Korean connections"]
            )
    
    async def _generate_debate_topics(self, book_info: BookInfo, area_analyses: List[AreaAnalysis]) -> List[DebateTopicSet]:
        """토론 주제 생성"""
        debate_topics = []
        level = book_info.get_education_level()
        
        # 각 영역별로 토론 주제 생성
        for analysis in area_analyses:
            if analysis.relevance_score >= 6.0:  # 관련성이 높은 영역만
                topics = await self._generate_topics_for_area(book_info, analysis, level)
                debate_topics.extend(topics)
        
        return debate_topics
    
    async def _generate_topics_for_area(self, book_info: BookInfo, analysis: AreaAnalysis, level: EducationLevel) -> List[DebateTopicSet]:
        """특정 영역에 대한 토론 주제 생성"""
        level_guidelines = {
            EducationLevel.PREPARATION: """
            - Use simple, clear language
            - Focus on basic character comparisons
            - Provide structured debate formats
            - Include vocabulary support
            """,
            EducationLevel.REGULAR: """
            - Use intermediate complexity
            - Include moral and ethical dimensions
            - Encourage critical thinking
            - Balance structure with creativity
            """,
            EducationLevel.MASTERY: """
            - Use advanced analytical thinking
            - Include multiple perspectives
            - Encourage independent reasoning
            - Focus on complex themes
            """
        }
        
        prompt = f"""
        Generate 2-3 debate topics for the book "{book_info.title}" by {book_info.author}
        
        Area: {analysis.area}
        Level: {level}
        Key Themes: {', '.join(analysis.key_themes)}
        Discussion Points: {', '.join(analysis.discussion_points)}
        
        Level Guidelines:
        {level_guidelines[level]}
        
        For each topic, provide in JSON format:
        {{
            "topics": [
                {{
                    "title": "<debate topic title>",
                    "description": "<detailed description>",
                    "debate_format": "<character_comparison|moral_judgment|issue_analysis>",
                    "pro_arguments": [<3-4 pro arguments>],
                    "con_arguments": [<3-4 con arguments>],
                    "background_info": "<background information needed>",
                    "vocabulary_list": [<8-12 key vocabulary words>],
                    "time_estimate": <estimated time in minutes>
                }}
            ]
        }}
        
        Make topics engaging for Korean students learning English.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.4
            )
            
            result_text = response.choices[0].message.content.strip()
            if result_text.startswith("```json"):
                result_text = result_text[7:-3]
            elif result_text.startswith("```"):
                result_text = result_text[3:-3]
            
            result_data = json.loads(result_text)
            
            topics = []
            for i, topic_data in enumerate(result_data["topics"]):
                topic = DebateTopicSet(
                    topic_id=f"{analysis.area.value.lower().replace(' ', '_')}_{i+1}",
                    title=topic_data["title"],
                    description=topic_data["description"],
                    level=level,
                    area=analysis.area,
                    debate_format=topic_data["debate_format"],
                    pro_arguments=topic_data["pro_arguments"],
                    con_arguments=topic_data["con_arguments"],
                    background_info=topic_data["background_info"],
                    vocabulary_list=topic_data["vocabulary_list"],
                    time_estimate=topic_data["time_estimate"]
                )
                topics.append(topic)
            
            return topics
            
        except Exception as e:
            logger.error(f"Failed to generate topics for area {analysis.area}: {e}")
            return []
    
    async def _generate_overall_assessment(self, book_info: BookInfo, area_analyses: List[AreaAnalysis], debate_topics: List[DebateTopicSet]) -> Dict[str, Any]:
        """전체 평가 생성"""
        total_relevance = sum(analysis.relevance_score for analysis in area_analyses)
        avg_relevance = total_relevance / len(area_analyses)
        
        best_areas = sorted(area_analyses, key=lambda x: x.relevance_score, reverse=True)[:3]
        
        assessment = {
            "overall_score": round(avg_relevance, 2),
            "total_topics_generated": len(debate_topics),
            "best_areas": [area.area.value for area in best_areas],
            "recommended_level": book_info.get_education_level().value,
            "estimated_program_duration": len(debate_topics) * 2,  # 주 단위
            "key_educational_values": [
                "Critical thinking development",
                "English communication skills",
                "Cultural awareness",
                "Collaborative learning"
            ]
        }
        
        return assessment
    
    def export_to_csv(self, analysis_result: BookAnalysisResult, output_path: str) -> str:
        """분석 결과를 CSV로 내보내기"""
        try:
            # 토론 주제 데이터를 CSV 형태로 변환
            csv_data = []
            
            for topic in analysis_result.debate_topics:
                row = {
                    "Topic_ID": topic.topic_id,
                    "Title": topic.title,
                    "Description": topic.description,
                    "Level": topic.level.value,
                    "Area": topic.area.value,
                    "Format": topic.debate_format,
                    "Pro_Arguments": " | ".join(topic.pro_arguments),
                    "Con_Arguments": " | ".join(topic.con_arguments),
                    "Background": topic.background_info,
                    "Vocabulary": " | ".join(topic.vocabulary_list),
                    "Time_Minutes": topic.time_estimate,
                    "Book_Title": analysis_result.book_info.title,
                    "Book_Author": analysis_result.book_info.author,
                    "AR_Level": analysis_result.book_info.ar_level
                }
                csv_data.append(row)
            
            df = pd.DataFrame(csv_data)
            df.to_csv(output_path, index=False, encoding='utf-8')
            
            logger.info(f"CSV exported to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to export CSV: {e}")
            raise

# 사용 예시 및 테스트 함수
async def test_book_analyzer():
    """테스트 함수"""
    # OpenAI API 키 설정 (환경변수에서 가져오기)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY environment variable not set")
        return
    
    analyzer = BookAnalyzer(api_key)
    
    # 테스트용 도서 정보
    test_book = BookInfo(
        title="Charlotte's Web",
        author="E.B. White",
        ar_level=4.4,
        pages=184,
        genre="Children's Literature"
    )
    
    print(f"Analyzing book: {test_book.title}")
    
    try:
        # 분석 수행
        result = await analyzer.analyze_book(test_book)
        
        print(f"\nAnalysis completed!")
        print(f"Analysis ID: {result.analysis_id}")
        print(f"Overall Score: {result.overall_assessment['overall_score']}")
        print(f"Topics Generated: {result.overall_assessment['total_topics_generated']}")
        print(f"Best Areas: {', '.join(result.overall_assessment['best_areas'])}")
        
        # CSV 내보내기
        csv_path = f"/home/ubuntu/pascal_system/{test_book.title.replace(' ', '_')}_analysis.csv"
        analyzer.export_to_csv(result, csv_path)
        
        print(f"\nCSV exported to: {csv_path}")
        
    except Exception as e:
        print(f"Error during analysis: {e}")

if __name__ == "__main__":
    asyncio.run(test_book_analyzer())
