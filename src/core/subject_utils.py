"""
Subject utility functions for default subject management
"""
from sqlalchemy.orm import Session
from uuid import UUID

from src.models.database import Subject, UserSubjectRole
from src.core.exceptions import BadRequestError


def is_default_subject(subject_id: UUID, db: Session) -> bool:
    """Check if a subject is the default subject"""
    subject = db.query(Subject).filter(Subject.subject_id == subject_id).first()
    return subject is not None and subject.subject_code == "default"


def prevent_remove_from_default_subject(user_id: UUID, subject_id: UUID, db: Session) -> None:
    """
    Prevent removing a user from the default subject.
    Raises BadRequestError if attempting to remove from default subject.
    
    Use this function before deactivating or deleting a UserSubjectRole entry
    to ensure users cannot be removed from the default subject.
    """
    if is_default_subject(subject_id, db):
        raise BadRequestError("Cannot remove student or tutor from the default subject. All users must remain assigned to the default subject.")


def prevent_modify_default_subject_role(assignment_id: UUID, db: Session) -> None:
    """
    Prevent modifying (deactivating/deleting) a UserSubjectRole assignment for the default subject.
    Raises BadRequestError if attempting to modify default subject role assignment.
    
    Use this function before deactivating or deleting a UserSubjectRole entry.
    """
    assignment = db.query(UserSubjectRole).filter(
        UserSubjectRole.assignment_id == assignment_id
    ).first()
    
    if not assignment:
        raise BadRequestError("UserSubjectRole assignment not found")
    
    if is_default_subject(assignment.subject_id, db):
        raise BadRequestError("Cannot remove student or tutor from the default subject. All users must remain assigned to the default subject.")


def can_modify_subject_role(assignment_id: UUID, db: Session) -> bool:
    """
    Check if a UserSubjectRole assignment can be modified (deactivated/deleted).
    Returns False if it's for the default subject.
    """
    assignment = db.query(UserSubjectRole).filter(
        UserSubjectRole.assignment_id == assignment_id
    ).first()
    
    if not assignment:
        return False
    
    return not is_default_subject(assignment.subject_id, db)

