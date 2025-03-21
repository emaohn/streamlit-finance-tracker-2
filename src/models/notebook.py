from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Notebook:
    """Notebook model for grouping related transactions"""
    id: Optional[str]
    name: str
    description: Optional[str]
    category: str
    budget: Optional[float] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, id: str, data: dict) -> 'Notebook':
        """Create a Notebook from a Firestore document"""
        return cls(
            id=id,
            name=data.get('name', ''),
            description=data.get('description'),
            category=data.get('category', ''),
            budget=float(data.get('budget', 0)) if data.get('budget') else None,
            start_date=data.get('start_date'),
            end_date=data.get('end_date'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    def to_dict(self) -> dict:
        """Convert to a dictionary for Firestore"""
        data = {
            'name': self.name,
            'category': self.category
        }
        
        if self.description:
            data['description'] = self.description
        if self.budget:
            data['budget'] = self.budget
        if self.start_date:
            data['start_date'] = self.start_date
        if self.end_date:
            data['end_date'] = self.end_date
        if self.created_at:
            data['created_at'] = self.created_at
        if self.updated_at:
            data['updated_at'] = self.updated_at
        
        return data
