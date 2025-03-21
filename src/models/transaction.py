from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Transaction:
    """Transaction model representing both expenses and earnings"""
    id: Optional[str]
    description: str
    amount: float  # Negative for expenses, positive for earnings
    category: str
    date: str
    notebook_id: Optional[str] = None
    recurring: bool = False
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @property
    def is_expense(self) -> bool:
        """Return True if this is an expense (negative amount)"""
        return self.amount < 0

    @classmethod
    def from_dict(cls, id: str, data: dict) -> 'Transaction':
        """Create a Transaction from a Firestore document"""
        return cls(
            id=id,
            description=data.get('description', ''),
            amount=float(data.get('amount', 0)),
            category=data.get('category', ''),
            date=data.get('date', ''),
            notebook_id=data.get('notebook_id'),
            recurring=data.get('recurring', False),
            notes=data.get('notes'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    def to_dict(self) -> dict:
        """Convert to a dictionary for Firestore"""
        data = {
            'description': self.description,
            'amount': self.amount,
            'category': self.category,
            'date': self.date,
            'recurring': self.recurring
        }
        
        if self.notebook_id:
            data['notebook_id'] = self.notebook_id
        if self.notes:
            data['notes'] = self.notes
        if self.created_at:
            data['created_at'] = self.created_at
        if self.updated_at:
            data['updated_at'] = self.updated_at
        
        return data
