"""
Answer service
"""
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from uuid import UUID

from src.models.database import AnswerSubmission, Question, QuizSession
from src.core.exceptions import NotFoundError, BadRequestError


class AnswerService:
    """Answer service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def submit_answer(
        self,
        question_id: UUID,
        tenant_id: UUID,
        student_id: UUID,
        answer: Any,
        session_id: Optional[UUID] = None,
        time_spent: Optional[int] = None,
        hints_used: Optional[List[UUID]] = None,
    ) -> Dict[str, Any]:
        """
        Submit and validate an answer
        TODO: Integrate with AI service for semantic validation
        """
        # Get question
        question = self.db.query(Question).filter(
            Question.question_id == question_id,
            Question.tenant_id == tenant_id,
        ).first()
        
        if not question:
            raise NotFoundError("Question not found")
        
        # Validate session if provided
        if session_id:
            session = self.db.query(QuizSession).filter(
                QuizSession.session_id == session_id,
                QuizSession.tenant_id == tenant_id,
                QuizSession.student_id == student_id,
            ).first()
            
            if not session:
                raise NotFoundError("Session not found")
        
        # Validate answer based on question type and subject validation method
        # TODO: Implement AI-based validation for different question types
        is_correct = self._validate_answer(question, answer)
        score = self._calculate_score(question, answer, is_correct, hints_used)
        max_score = question.extra_metadata.get("points", 1.0) if question.extra_metadata else 1.0
        
        # Create submission record
        submission = AnswerSubmission(
            tenant_id=tenant_id,
            question_id=question_id,
            student_id=student_id,
            session_id=session_id,
            answer=answer,
            is_correct=is_correct,
            score=score,
            max_score=max_score,
            feedback=self._generate_feedback(question, answer, is_correct),
            time_spent=time_spent or 0,
            hints_used=hints_used or [],
        )
        
        self.db.add(submission)
        self.db.commit()
        self.db.refresh(submission)
        
        return {
            "question_id": question_id,
            "correct": is_correct,
            "score": float(score),
            "max_score": float(max_score),
            "feedback": submission.feedback,
            "correct_answer": question.correct_answer,
            "explanation": None,  # TODO: Generate explanation
            "areas_correct": [] if not is_correct else ["Answer is correct"],
            "areas_incorrect": [] if is_correct else ["Answer is incorrect"],
        }
    
    def validate_answer(
        self,
        question_id: UUID,
        tenant_id: UUID,
        answer: Any,
    ) -> Dict[str, Any]:
        """
        Validate answer without recording submission (for practice mode)
        """
        question = self.db.query(Question).filter(
            Question.question_id == question_id,
            Question.tenant_id == tenant_id,
        ).first()
        
        if not question:
            raise NotFoundError("Question not found")
        
        is_correct = self._validate_answer(question, answer)
        score = self._calculate_score(question, answer, is_correct, None)
        max_score = question.extra_metadata.get("points", 1.0) if question.extra_metadata else 1.0
        
        return {
            "correct": is_correct,
            "score": float(score),
            "max_score": float(max_score),
            "feedback": self._generate_feedback(question, answer, is_correct),
            "areas_correct": [] if not is_correct else ["Answer is correct"],
            "areas_incorrect": [] if is_correct else ["Answer is incorrect"],
        }
    
    def _validate_answer(self, question: Question, answer: Any) -> bool:
        """Validate answer against correct answer"""
        # Simple validation - TODO: Implement AI-based semantic validation
        if question.question_type == "multiple_choice":
            return str(answer).strip().lower() == str(question.correct_answer).strip().lower()
        elif question.question_type == "true_false":
            return bool(answer) == bool(question.correct_answer)
        else:
            # For text-based answers, use simple string comparison
            # TODO: Use AI for semantic validation
            return str(answer).strip().lower() == str(question.correct_answer).strip().lower()
    
    def _calculate_score(
        self,
        question: Question,
        answer: Any,
        is_correct: bool,
        hints_used: Optional[List[UUID]],
    ) -> float:
        """Calculate score for answer"""
        max_score = question.extra_metadata.get("points", 1.0) if question.extra_metadata else 1.0
        
        if is_correct:
            score = max_score
            # Reduce score if hints were used
            if hints_used:
                score = score * (1.0 - len(hints_used) * 0.1)  # 10% reduction per hint
        else:
            score = 0.0
        
        return max(0.0, score)
    
    def _generate_feedback(self, question: Question, answer: Any, is_correct: bool) -> str:
        """Generate feedback message"""
        if is_correct:
            return "Correct! Well done."
        else:
            return f"Incorrect. The correct answer is: {question.correct_answer}"

