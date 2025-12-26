"""
Hint service
"""
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4

from src.models.database import Hint, Question
from src.core.exceptions import NotFoundError, BadRequestError


class HintService:
    """Hint service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_hint(
        self,
        question_id: UUID,
        tenant_id: UUID,
        hint_level: Optional[int] = None,
        student_id: UUID = None,
        previous_attempts: Optional[List[Any]] = None,
        hints_already_shown: Optional[List[UUID]] = None,
    ) -> Dict[str, Any]:
        """
        Get hint for a question
        TODO: Integrate with AI service to generate contextual hints
        """
        # Get question
        question = self.db.query(Question).filter(
            Question.question_id == question_id,
            Question.tenant_id == tenant_id,
        ).first()
        
        if not question:
            raise NotFoundError("Question not found")
        
        # Determine hint level
        if hint_level is None:
            # Get next available hint level
            existing_hints = self.db.query(Hint).filter(
                Hint.question_id == question_id,
                Hint.tenant_id == tenant_id,
            ).order_by(Hint.hint_level).all()
            
            if existing_hints:
                hint_level = existing_hints[-1].hint_level + 1
            else:
                hint_level = 1
        
        if hint_level < 1 or hint_level > 4:
            raise BadRequestError("Hint level must be between 1 and 4")
        
        # Check if hint already exists
        existing_hint = self.db.query(Hint).filter(
            Hint.question_id == question_id,
            Hint.tenant_id == tenant_id,
            Hint.hint_level == hint_level,
        ).first()
        
        if existing_hint:
            hint = existing_hint
        else:
            # Generate new hint using AI
            # TODO: Integrate with AI service
            hint_text = self._generate_hint_text(question, hint_level, previous_attempts)
            
            hint = Hint(
                tenant_id=tenant_id,
                question_id=question_id,
                hint_level=hint_level,
                hint_text=hint_text,
            )
            self.db.add(hint)
            self.db.commit()
            self.db.refresh(hint)
        
        # Calculate remaining hints
        remaining_hints = 4 - hint_level
        
        return {
            "hint_id": hint.hint_id,
            "hint_level": hint.hint_level,
            "hint_text": hint.hint_text,
            "remaining_hints": remaining_hints,
        }
    
    def _generate_hint_text(
        self,
        question: Question,
        hint_level: int,
        previous_attempts: Optional[List[Any]],
    ) -> str:
        """
        Generate hint text using AI
        TODO: Integrate with AI service
        """
        # Placeholder implementation
        hint_texts = {
            1: "Consider the key concepts related to this topic.",
            2: "Think about the fundamental principles that apply here.",
            3: "Focus on the specific approach needed to solve this.",
            4: "The solution involves applying the following steps...",
        }
        
        return hint_texts.get(hint_level, "Hint not available")

