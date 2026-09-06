"""
Database CRUD operations for Case records.
"""

from typing import Optional
from sqlalchemy.orm import Session
from app.services.db.models import Case


def create_case(db: Session, case_id: str, image_path: str) -> Case:
    """Create a new Case record with initial state."""
    case = Case(
        id=case_id,
        image_path=image_path,
        status="created",
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    return case


def get_case(db: Session, case_id: str) -> Optional[Case]:
    """Retrieve a Case by ID."""
    return db.query(Case).filter(Case.id == case_id).first()


def update_case(db: Session, case_id: str, **kwargs) -> Optional[Case]:
    """Update fields on an existing Case."""
    case = get_case(db, case_id)
    if not case:
        return None
    for key, value in kwargs.items():
        if hasattr(case, key):
            setattr(case, key, value)
    db.commit()
    db.refresh(case)
    return case
