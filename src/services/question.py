"""
Question service
"""
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
from datetime import datetime

from src.models.database import Question, Subject
from src.core.exceptions import NotFoundError, BadRequestError


class QuestionService:
    """Question service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_question(
        self,
        tenant_id: Optional[UUID],
        subject_id: Optional[UUID] = None,
        subject_code: Optional[str] = None,
        grade_level: Optional[int] = None,
        difficulty: Optional[str] = None,
        topic: Optional[str] = None,
        question_type: Optional[str] = None,
        session_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """
        Generate a question using AI
        TODO: Integrate with AI service (OpenAI, Anthropic, etc.)
        """
        # Resolve subject
        if subject_id:
            subject = self.db.query(Subject).filter(Subject.subject_id == subject_id).first()
        elif subject_code:
            subject = self.db.query(Subject).filter(Subject.subject_code == subject_code).first()
        else:
            raise BadRequestError("Either subject_id or subject_code is required")
        
        if not subject:
            raise NotFoundError("Subject not found")
        
        from src.models.user import SubjectStatus
        if subject.status != SubjectStatus.ACTIVE:
            raise BadRequestError("Subject is not active")
        
        # Validate grade level if subject requires it
        if grade_level and subject.grade_levels:
            if grade_level not in subject.grade_levels:
                raise BadRequestError(f"Grade level {grade_level} not supported for this subject")
        
        # Validate question type
        if question_type and subject.supported_question_types:
            if question_type not in subject.supported_question_types:
                raise BadRequestError(f"Question type {question_type} not supported for this subject")
        
        # TODO: Call AI service to generate question
        # For now, create a placeholder question
        question = Question(
            tenant_id=tenant_id,
            subject_id=subject.subject_id,
            grade_level=grade_level,
            difficulty=difficulty or subject.settings.get("default_difficulty") if subject.settings else "beginner",
            question_type=question_type or "multiple_choice",
            question_text="Placeholder question - AI integration needed",
            options=["Option A", "Option B", "Option C", "Option D"] if question_type == "multiple_choice" else None,
            correct_answer={"answer": "Option A"},
            metadata={
                "topic": topic,
                "learning_objectives": [],
                "estimated_time": 60,
            },
        )
        
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        
        return {
            "question_id": question.question_id,
            "question_text": question.question_text,
            "question_type": question.question_type,
            "options": question.options,
            "metadata": {
                "difficulty": question.difficulty.value if hasattr(question.difficulty, 'value') else question.difficulty,
                "estimated_time": question.metadata.get("estimated_time") if question.metadata else None,
                "learning_objectives": question.metadata.get("learning_objectives", []) if question.metadata else [],
                "topic": question.metadata.get("topic") if question.metadata else None,
            },
            "session_id": session_id,
        }
    
    def get_question(self, question_id: UUID, tenant_id: Optional[UUID] = None) -> Dict[str, Any]:
        """Get question by ID"""
        query = self.db.query(Question).filter(Question.question_id == question_id)
        
        # Enforce tenant isolation if tenant_id provided
        if tenant_id:
            query = query.filter(Question.tenant_id == tenant_id)
        
        question = query.first()
        if not question:
            raise NotFoundError("Question not found")
        
        return {
            "question_id": question.question_id,
            "question_text": question.question_text,
            "question_type": question.question_type,
            "options": question.options,
            "metadata": question.metadata or {},
        }
    
    def get_question_narrative(self, question_id: UUID, tenant_id: Optional[UUID] = None) -> Dict[str, Any]:
        """
        Get educational narrative for a question
        TODO: Integrate with AI service to generate narrative
        """
        question = self.get_question(question_id, tenant_id)
        
        # TODO: Generate narrative using AI
        # For now, return placeholder
        return {
            "question_id": question["question_id"],
            "narrative": "Placeholder narrative - AI integration needed",
            "explanation": {
                "concept": "Concept explanation",
                "steps": ["Step 1", "Step 2", "Step 3"],
                "why_correct": "Why the answer is correct",
                "common_mistakes": ["Common mistake 1", "Common mistake 2"],
                "related_concepts": ["Related concept 1"],
            },
        }

