"""
파스칼 토론 주제 생성 모듈
원서 분석 결과를 바탕으로 체계적인 토론 주제와 교육 자료를 생성하는 전용 모듈
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import openai
from openai import AsyncOpenAI
import pandas as pd
from datetime import datetime
import logging
from book_analyzer import BookInfo, EducationLevel, EducationArea, AreaAnalysis

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DebateFormat(str, Enum):
    """토론 형식 정의"""
    CHARACTER_COMPARISON = "character_comparison"
    MORAL_JUDGMENT = "moral_judgment"
    ISSUE_ANALYSIS = "issue_analysis"
    PROBLEM_SOLUTION = "problem_solution"
    CAUSE_EFFECT = "cause_effect"
    FUTURE_PREDICTION = "future_prediction"

@dataclass
class ReadingQuestion:
    """독해 문제"""
    question_id: str
    question_type: str  # "factual", "inferential", "analytical", "evaluative", "creative"
    question_text: str
    sample_answer: str
    points: int
    bloom_level: str  # "remember", "understand", "apply", "analyze", "evaluate", "create"

@dataclass
class WritingTemplate:
    """글쓰기 템플릿"""
    template_id: str
    level: EducationLevel
    structure: Dict[str, str]  # paragraph_name: template
    word_count_target: int
    time_limit: int  # 분 단위
    evaluation_criteria: List[str]

@dataclass
class EducationalMaterial:
    """교육 자료 패키지"""
    material_id: str
    topic_id: str
    reading_questions: List[ReadingQuestion]
    writing_template: WritingTemplate
    vocabulary_exercises: List[Dict[str, Any]]
    discussion_guide: Dict[str, Any]
    assessment_rubric: Dict[str, Any]

@dataclass
class EnhancedDebateTopic:
    """향상된 토론 주제 (교육 자료 포함)"""
    topic_id: str
    title: str
    description: str
    level: EducationLevel
    area: EducationArea
    debate_format: DebateFormat
    
    # 토론 구성 요소
    opening_statement: str
    key_arguments: Dict[str, List[str]]  # "pro", "con"
    evidence_sources: List[str]
    counter_arguments: Dict[str, List[str]]
    
    # 교육 자료
    educational_materials: EducationalMaterial
    
    # 메타데이터
    difficulty_score: float
    time_estimate: int
    prerequisite_knowledge: List[str]
    learning_objectives: List[str]

class TopicGenerator:
    """토론 주제 생성 전용 클래스"""
    
    def __init__(self, openai_api_key: str):
        self.client = AsyncOpenAI(api_key=openai_api_key)
        self.topic_templates = self._load_topic_templates()
        self.metaprompts = self._load_metaprompts()
    
    def _load_topic_templates(self) -> Dict[str, Any]:
        """토론 주제 템플릿 로드"""
        return {
            DebateFormat.CHARACTER_COMPARISON: {
                "structure": "Character A vs Character B: Who demonstrates better [value]?",
                "focus": "Character analysis, moral values, decision-making",
                "typical_duration": 45
            },
            DebateFormat.MORAL_JUDGMENT: {
                "structure": "Is [character's action] morally justified?",
                "focus": "Ethics, consequences, intentions, context",
                "typical_duration": 50
            },
            DebateFormat.ISSUE_ANALYSIS: {
                "structure": "How should [issue] be addressed?",
                "focus": "Problem identification, solution evaluation, implementation",
                "typical_duration": 60
            },
            DebateFormat.PROBLEM_SOLUTION: {
                "structure": "What is the best solution to [problem]?",
                "focus": "Critical thinking, creativity, feasibility analysis",
                "typical_duration": 55
            },
            DebateFormat.CAUSE_EFFECT: {
                "structure": "What are the main causes/effects of [phenomenon]?",
                "focus": "Causal reasoning, evidence analysis, logical connections",
                "typical_duration": 50
            },
            DebateFormat.FUTURE_PREDICTION: {
                "structure": "What will happen if [scenario] occurs?",
                "focus": "Prediction, scenario analysis, trend identification",
                "typical_duration": 45
            }
        }
    
    def _load_metaprompts(self) -> Dict[str, str]:
        """메타프롬프트 로드"""
        return {
            "topic_generation": """
            You are an expert in creating debate topics for Korean students learning English through literature.
            
            CONTEXT:
            - Students are Korean learners of English
            - Focus on developing critical thinking and English communication skills
            - Topics should connect global themes with Korean cultural context
            - Emphasize collaborative learning and respectful discourse
            
            REQUIREMENTS:
            - Create engaging, age-appropriate topics
            - Ensure cultural sensitivity and inclusivity
            - Provide clear structure and guidance
            - Include vocabulary and language support
            - Connect to real-world applications
            
            EDUCATIONAL GOALS:
            - Develop critical thinking skills
            - Improve English fluency and confidence
            - Foster global citizenship mindset
            - Encourage empathy and perspective-taking
            - Build collaborative learning skills
            """,
            
            "reading_questions": """
            Create reading comprehension questions following Bloom's Taxonomy:
            
            LEVEL 1 (Remember): Factual recall from the text
            LEVEL 2 (Understand): Explain meaning and relationships
            LEVEL 3 (Apply): Use information in new situations
            LEVEL 4 (Analyze): Break down and examine components
            LEVEL 5 (Evaluate): Make judgments and assessments
            LEVEL 6 (Create): Generate new ideas and solutions
            
            Each question should:
            - Be clearly worded and unambiguous
            - Have a specific learning objective
            - Include sample answers for teacher guidance
            - Be appropriate for the student's English level
            """,
            
            "writing_template": """
            Create writing templates that scaffold student learning:
            
            PREPARATION LEVEL:
            - Highly structured with sentence starters
            - Clear paragraph organization
            - Vocabulary banks provided
            - Step-by-step guidance
            
            REGULAR LEVEL:
            - Moderate structure with flexibility
            - Paragraph guidelines with examples
            - Transition word suggestions
            - Balanced support and independence
            
            MASTERY LEVEL:
            - Minimal structure, maximum creativity
            - Advanced organizational patterns
            - Sophisticated language expectations
            - Independent critical thinking
            """
        }
    
    async def generate_comprehensive_topics(
        self, 
        book_info: BookInfo, 
        area_analyses: List[AreaAnalysis],
        num_topics_per_area: int = 2
    ) -> List[EnhancedDebateTopic]:
        """종합적인 토론 주제 생성"""
        
        logger.info(f"Generating comprehensive topics for {book_info.title}")
        
        all_topics = []
        level = book_info.get_education_level()
        
        # 관련성이 높은 영역 선별 (점수 6.0 이상)
        relevant_areas = [analysis for analysis in area_analyses if analysis.relevance_score >= 6.0]
        
        for area_analysis in relevant_areas:
            logger.info(f"Generating topics for area: {area_analysis.area}")
            
            # 영역별 토론 주제 생성
            area_topics = await self._generate_topics_for_area(
                book_info, area_analysis, level, num_topics_per_area
            )
            
            all_topics.extend(area_topics)
        
        logger.info(f"Generated {len(all_topics)} comprehensive topics")
        return all_topics
    
    async def _generate_topics_for_area(
        self, 
        book_info: BookInfo, 
        area_analysis: AreaAnalysis, 
        level: EducationLevel,
        num_topics: int
    ) -> List[EnhancedDebateTopic]:
        """특정 영역에 대한 토론 주제 생성"""
        
        # 1. 기본 토론 주제 생성
        basic_topics = await self._generate_basic_topics(book_info, area_analysis, level, num_topics)
        
        # 2. 각 주제에 대한 교육 자료 생성
        enhanced_topics = []
        for i, basic_topic in enumerate(basic_topics):
            logger.info(f"Enhancing topic {i+1}/{len(basic_topics)}")
            
            # 교육 자료 생성
            educational_materials = await self._generate_educational_materials(
                book_info, basic_topic, level
            )
            
            # 향상된 토론 주제 구성
            enhanced_topic = EnhancedDebateTopic(
                topic_id=f"{area_analysis.area.value.lower().replace(' ', '_')}_{i+1}",
                title=basic_topic["title"],
                description=basic_topic["description"],
                level=level,
                area=area_analysis.area,
                debate_format=DebateFormat(basic_topic["debate_format"]),
                opening_statement=basic_topic["opening_statement"],
                key_arguments=basic_topic["key_arguments"],
                evidence_sources=basic_topic["evidence_sources"],
                counter_arguments=basic_topic["counter_arguments"],
                educational_materials=educational_materials,
                difficulty_score=basic_topic["difficulty_score"],
                time_estimate=basic_topic["time_estimate"],
                prerequisite_knowledge=basic_topic["prerequisite_knowledge"],
                learning_objectives=basic_topic["learning_objectives"]
            )
            
            enhanced_topics.append(enhanced_topic)
        
        return enhanced_topics
    
    async def _generate_basic_topics(
        self, 
        book_info: BookInfo, 
        area_analysis: AreaAnalysis, 
        level: EducationLevel,
        num_topics: int
    ) -> List[Dict[str, Any]]:
        """기본 토론 주제 생성"""
        
        level_specifications = {
            EducationLevel.PREPARATION: {
                "complexity": "Simple and straightforward",
                "language": "Basic vocabulary and sentence structures",
                "support": "High scaffolding with templates and examples",
                "focus": "Character actions and basic moral concepts"
            },
            EducationLevel.REGULAR: {
                "complexity": "Moderate complexity with multiple perspectives",
                "language": "Intermediate vocabulary and varied sentence structures",
                "support": "Balanced guidance with room for creativity",
                "focus": "Deeper character analysis and ethical reasoning"
            },
            EducationLevel.MASTERY: {
                "complexity": "High complexity with nuanced analysis",
                "language": "Advanced vocabulary and sophisticated structures",
                "support": "Minimal scaffolding, maximum independence",
                "focus": "Complex themes and philosophical questions"
            }
        }
        
        prompt = f"""
        {self.metaprompts['topic_generation']}
        
        BOOK INFORMATION:
        Title: {book_info.title}
        Author: {book_info.author}
        AR Level: {book_info.ar_level}
        Summary: {book_info.summary or 'Not provided'}
        
        AREA FOCUS: {area_analysis.area}
        Key Themes: {', '.join(area_analysis.key_themes)}
        Discussion Points: {', '.join(area_analysis.discussion_points)}
        Korean Connections: {', '.join(area_analysis.korean_connection)}
        
        LEVEL SPECIFICATIONS ({level}):
        {json.dumps(level_specifications[level], indent=2)}
        
        TASK: Generate {num_topics} debate topics in JSON format:
        
        {{
            "topics": [
                {{
                    "title": "<engaging debate topic title>",
                    "description": "<detailed description of the debate>",
                    "debate_format": "<one of: character_comparison, moral_judgment, issue_analysis, problem_solution, cause_effect, future_prediction>",
                    "opening_statement": "<clear opening statement to frame the debate>",
                    "key_arguments": {{
                        "pro": [<3-4 strong pro arguments>],
                        "con": [<3-4 strong con arguments>]
                    }},
                    "evidence_sources": [<specific scenes, quotes, or examples from the book>],
                    "counter_arguments": {{
                        "pro": [<potential counter-arguments to con side>],
                        "con": [<potential counter-arguments to pro side>]
                    }},
                    "difficulty_score": <1-10 difficulty rating>,
                    "time_estimate": <estimated time in minutes>,
                    "prerequisite_knowledge": [<background knowledge needed>],
                    "learning_objectives": [<specific learning goals>]
                }}
            ]
        }}
        
        Ensure topics are:
        - Culturally sensitive and inclusive
        - Engaging for Korean students
        - Connected to real-world applications
        - Appropriate for the specified level
        - Designed to promote critical thinking
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.4
            )
            
            result_text = response.choices[0].message.content.strip()
            if result_text.startswith("```json"):
                result_text = result_text[7:-3]
            elif result_text.startswith("```"):
                result_text = result_text[3:-3]
            
            result_data = json.loads(result_text)
            return result_data["topics"]
            
        except Exception as e:
            logger.error(f"Failed to generate basic topics: {e}")
            return []
    
    async def _generate_educational_materials(
        self, 
        book_info: BookInfo, 
        topic_data: Dict[str, Any], 
        level: EducationLevel
    ) -> EducationalMaterial:
        """교육 자료 생성"""
        
        # 1. 독해 문제 생성
        reading_questions = await self._generate_reading_questions(book_info, topic_data, level)
        
        # 2. 글쓰기 템플릿 생성
        writing_template = await self._generate_writing_template(topic_data, level)
        
        # 3. 어휘 연습 문제 생성
        vocabulary_exercises = await self._generate_vocabulary_exercises(book_info, topic_data, level)
        
        # 4. 토론 가이드 생성
        discussion_guide = await self._generate_discussion_guide(topic_data, level)
        
        # 5. 평가 루브릭 생성
        assessment_rubric = await self._generate_assessment_rubric(level)
        
        return EducationalMaterial(
            material_id=f"materials_{topic_data.get('title', 'unknown').lower().replace(' ', '_')}",
            topic_id=topic_data.get('title', 'unknown'),
            reading_questions=reading_questions,
            writing_template=writing_template,
            vocabulary_exercises=vocabulary_exercises,
            discussion_guide=discussion_guide,
            assessment_rubric=assessment_rubric
        )
    
    async def _generate_reading_questions(
        self, 
        book_info: BookInfo, 
        topic_data: Dict[str, Any], 
        level: EducationLevel
    ) -> List[ReadingQuestion]:
        """독해 문제 생성"""
        
        prompt = f"""
        {self.metaprompts['reading_questions']}
        
        BOOK: {book_info.title} by {book_info.author}
        TOPIC: {topic_data['title']}
        LEVEL: {level}
        
        Generate 5 reading comprehension questions following Bloom's Taxonomy:
        
        {{
            "questions": [
                {{
                    "question_type": "<factual|inferential|analytical|evaluative|creative>",
                    "question_text": "<clear, specific question>",
                    "sample_answer": "<detailed sample answer>",
                    "points": <point value 1-5>,
                    "bloom_level": "<remember|understand|apply|analyze|evaluate|create>"
                }}
            ]
        }}
        
        Questions should progress from basic comprehension to higher-order thinking.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.3
            )
            
            result_text = response.choices[0].message.content.strip()
            if result_text.startswith("```json"):
                result_text = result_text[7:-3]
            elif result_text.startswith("```"):
                result_text = result_text[3:-3]
            
            result_data = json.loads(result_text)
            
            questions = []
            for i, q_data in enumerate(result_data["questions"]):
                question = ReadingQuestion(
                    question_id=f"q_{i+1}",
                    question_type=q_data["question_type"],
                    question_text=q_data["question_text"],
                    sample_answer=q_data["sample_answer"],
                    points=q_data["points"],
                    bloom_level=q_data["bloom_level"]
                )
                questions.append(question)
            
            return questions
            
        except Exception as e:
            logger.error(f"Failed to generate reading questions: {e}")
            return []
    
    async def _generate_writing_template(self, topic_data: Dict[str, Any], level: EducationLevel) -> WritingTemplate:
        """글쓰기 템플릿 생성"""
        
        level_specs = {
            EducationLevel.PREPARATION: {
                "word_count": 150,
                "time_limit": 30,
                "structure_detail": "Very detailed with sentence starters"
            },
            EducationLevel.REGULAR: {
                "word_count": 250,
                "time_limit": 40,
                "structure_detail": "Moderate structure with examples"
            },
            EducationLevel.MASTERY: {
                "word_count": 400,
                "time_limit": 50,
                "structure_detail": "Minimal structure, maximum creativity"
            }
        }
        
        prompt = f"""
        {self.metaprompts['writing_template']}
        
        TOPIC: {topic_data['title']}
        LEVEL: {level}
        SPECIFICATIONS: {json.dumps(level_specs[level], indent=2)}
        
        Create a writing template in JSON format:
        
        {{
            "structure": {{
                "introduction": "<template for introduction paragraph>",
                "body_paragraph_1": "<template for first body paragraph>",
                "body_paragraph_2": "<template for second body paragraph>",
                "conclusion": "<template for conclusion paragraph>"
            }},
            "evaluation_criteria": [<list of evaluation criteria>]
        }}
        
        Templates should include:
        - Sentence starters appropriate for the level
        - Transition words and phrases
        - Argument structure guidance
        - Evidence integration tips
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.3
            )
            
            result_text = response.choices[0].message.content.strip()
            if result_text.startswith("```json"):
                result_text = result_text[7:-3]
            elif result_text.startswith("```"):
                result_text = result_text[3:-3]
            
            result_data = json.loads(result_text)
            
            return WritingTemplate(
                template_id=f"template_{level.value}",
                level=level,
                structure=result_data["structure"],
                word_count_target=level_specs[level]["word_count"],
                time_limit=level_specs[level]["time_limit"],
                evaluation_criteria=result_data["evaluation_criteria"]
            )
            
        except Exception as e:
            logger.error(f"Failed to generate writing template: {e}")
            return WritingTemplate(
                template_id=f"template_{level.value}",
                level=level,
                structure={"introduction": "Basic template", "body": "Basic template", "conclusion": "Basic template"},
                word_count_target=200,
                time_limit=30,
                evaluation_criteria=["Content", "Organization", "Language"]
            )
    
    async def _generate_vocabulary_exercises(
        self, 
        book_info: BookInfo, 
        topic_data: Dict[str, Any], 
        level: EducationLevel
    ) -> List[Dict[str, Any]]:
        """어휘 연습 문제 생성"""
        
        prompt = f"""
        Create vocabulary exercises for the debate topic: {topic_data['title']}
        Book: {book_info.title}
        Level: {level}
        
        Generate 3 different types of vocabulary exercises in JSON format:
        
        {{
            "exercises": [
                {{
                    "type": "definition_matching",
                    "instructions": "<clear instructions>",
                    "items": [
                        {{
                            "word": "<vocabulary word>",
                            "definition": "<definition>",
                            "example_sentence": "<example from context>"
                        }}
                    ]
                }},
                {{
                    "type": "context_clues",
                    "instructions": "<clear instructions>",
                    "items": [
                        {{
                            "sentence": "<sentence with vocabulary word>",
                            "target_word": "<word to define>",
                            "answer": "<meaning from context>"
                        }}
                    ]
                }},
                {{
                    "type": "usage_practice",
                    "instructions": "<clear instructions>",
                    "items": [
                        {{
                            "prompt": "<situation requiring vocabulary use>",
                            "target_words": [<words to use>],
                            "sample_response": "<example response>"
                        }}
                    ]
                }}
            ]
        }}
        
        Focus on vocabulary that will be useful for the debate topic.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1200,
                temperature=0.3
            )
            
            result_text = response.choices[0].message.content.strip()
            if result_text.startswith("```json"):
                result_text = result_text[7:-3]
            elif result_text.startswith("```"):
                result_text = result_text[3:-3]
            
            result_data = json.loads(result_text)
            return result_data["exercises"]
            
        except Exception as e:
            logger.error(f"Failed to generate vocabulary exercises: {e}")
            return []
    
    async def _generate_discussion_guide(self, topic_data: Dict[str, Any], level: EducationLevel) -> Dict[str, Any]:
        """토론 가이드 생성"""
        
        guide = {
            "preparation_phase": {
                "time_allocation": "15 minutes",
                "activities": [
                    "Review key vocabulary",
                    "Read background information",
                    "Organize arguments and evidence",
                    "Practice key phrases"
                ]
            },
            "opening_phase": {
                "time_allocation": "10 minutes",
                "structure": [
                    "Opening statement (2 minutes per side)",
                    "Position clarification",
                    "Ground rules reminder"
                ]
            },
            "main_debate": {
                "time_allocation": "20 minutes",
                "structure": [
                    "First arguments (3 minutes per side)",
                    "Cross-examination (2 minutes per side)",
                    "Rebuttal (2 minutes per side)",
                    "Final statements (1 minute per side)"
                ]
            },
            "reflection_phase": {
                "time_allocation": "10 minutes",
                "activities": [
                    "Self-assessment",
                    "Peer feedback",
                    "Key learning points",
                    "Language reflection"
                ]
            },
            "teacher_notes": [
                "Monitor language use and provide support",
                "Encourage respectful disagreement",
                "Focus on evidence-based arguments",
                "Celebrate effort and improvement"
            ]
        }
        
        return guide
    
    async def _generate_assessment_rubric(self, level: EducationLevel) -> Dict[str, Any]:
        """평가 루브릭 생성"""
        
        rubric = {
            "content_knowledge": {
                "excellent": "Demonstrates deep understanding of the topic with accurate, relevant details",
                "good": "Shows solid understanding with mostly accurate information",
                "satisfactory": "Basic understanding with some accurate details",
                "needs_improvement": "Limited understanding with few accurate details"
            },
            "argumentation": {
                "excellent": "Presents clear, logical arguments with strong evidence",
                "good": "Presents mostly clear arguments with adequate evidence",
                "satisfactory": "Presents basic arguments with some evidence",
                "needs_improvement": "Arguments are unclear or lack evidence"
            },
            "language_use": {
                "excellent": "Uses varied vocabulary and complex structures accurately",
                "good": "Uses appropriate vocabulary with mostly correct structures",
                "satisfactory": "Uses basic vocabulary with simple structures",
                "needs_improvement": "Limited vocabulary with frequent errors"
            },
            "participation": {
                "excellent": "Actively engages, listens respectfully, builds on others' ideas",
                "good": "Participates regularly with respectful interaction",
                "satisfactory": "Participates occasionally with basic interaction",
                "needs_improvement": "Limited participation or disrespectful behavior"
            }
        }
        
        return rubric
    
    def export_topics_to_csv(self, topics: List[EnhancedDebateTopic], output_path: str) -> str:
        """토론 주제를 CSV로 내보내기"""
        try:
            csv_data = []
            
            for topic in topics:
                # 기본 토론 주제 정보
                base_row = {
                    "Topic_ID": topic.topic_id,
                    "Title": topic.title,
                    "Description": topic.description,
                    "Level": topic.level.value,
                    "Area": topic.area.value,
                    "Format": topic.debate_format.value,
                    "Opening_Statement": topic.opening_statement,
                    "Pro_Arguments": " | ".join(topic.key_arguments.get("pro", [])),
                    "Con_Arguments": " | ".join(topic.key_arguments.get("con", [])),
                    "Evidence_Sources": " | ".join(topic.evidence_sources),
                    "Difficulty_Score": topic.difficulty_score,
                    "Time_Estimate": topic.time_estimate,
                    "Learning_Objectives": " | ".join(topic.learning_objectives)
                }
                
                # 독해 문제 추가
                for i, question in enumerate(topic.educational_materials.reading_questions):
                    base_row[f"Reading_Q{i+1}"] = question.question_text
                    base_row[f"Reading_A{i+1}"] = question.sample_answer
                
                # 글쓰기 템플릿 추가
                template = topic.educational_materials.writing_template
                base_row["Writing_Template"] = json.dumps(template.structure)
                base_row["Word_Count_Target"] = template.word_count_target
                base_row["Writing_Time_Limit"] = template.time_limit
                
                csv_data.append(base_row)
            
            df = pd.DataFrame(csv_data)
            df.to_csv(output_path, index=False, encoding='utf-8')
            
            logger.info(f"Enhanced topics CSV exported to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to export enhanced topics CSV: {e}")
            raise

# 테스트 함수
async def test_topic_generator():
    """토론 주제 생성기 테스트"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY environment variable not set")
        return
    
    generator = TopicGenerator(api_key)
    
    # 테스트용 데이터
    test_book = BookInfo(
        title="Charlotte's Web",
        author="E.B. White",
        ar_level=4.4,
        summary="A story about friendship between a pig named Wilbur and a spider named Charlotte."
    )
    
    test_area = AreaAnalysis(
        area=EducationArea.HUMAN_SOCIETY,
        relevance_score=8.5,
        key_themes=["friendship", "sacrifice", "loyalty", "growing up"],
        discussion_points=["What makes a true friend?", "When is sacrifice worthwhile?"],
        vocabulary_focus=["friendship", "loyalty", "sacrifice", "courage"],
        cultural_context=["rural American life", "farm animals"],
        korean_connection=["Korean concepts of friendship", "loyalty in Korean culture"]
    )
    
    print("Generating comprehensive topics...")
    
    try:
        topics = await generator.generate_comprehensive_topics(
            test_book, [test_area], num_topics_per_area=2
        )
        
        print(f"\nGenerated {len(topics)} enhanced topics:")
        for topic in topics:
            print(f"- {topic.title}")
            print(f"  Format: {topic.debate_format.value}")
            print(f"  Difficulty: {topic.difficulty_score}/10")
            print(f"  Reading Questions: {len(topic.educational_materials.reading_questions)}")
            print()
        
        # CSV 내보내기
        csv_path = "/home/ubuntu/pascal_system/enhanced_topics.csv"
        generator.export_topics_to_csv(topics, csv_path)
        print(f"CSV exported to: {csv_path}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_topic_generator())
