from datetime import datetime
from typing import List, Optional, Dict, Any
import firebase_admin
from firebase_admin import credentials, firestore
import os
import streamlit as st

from ..models.transaction import Transaction
from ..models.notebook import Notebook

def get_firebase_instance() -> 'FirebaseService':
    """Get or create a Firebase service instance"""
    if "firebase_instance" not in st.session_state:
        try:
            # Get the absolute path to the service account key
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            key_path = os.path.join(base_dir, 'firestore-key.json')
            
            if not os.path.exists(key_path):
                raise FileNotFoundError(f"Service account key not found at {key_path}")
            
            # Initialize Firebase Admin SDK with a unique name
            cred = credentials.Certificate(key_path)
            app_name = f"streamlit-finance-tracker-{id(st.session_state)}"
            
            # Check if app already exists
            try:
                app = firebase_admin.get_app(app_name)
            except ValueError:
                app = firebase_admin.initialize_app(cred, name=app_name)
            
            # Get Firestore client
            db = firestore.client(app)
            st.session_state.firebase_instance = FirebaseService(db)
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Firebase: {str(e)}")
    
    return st.session_state.firebase_instance

class FirebaseService:
    """Service class for Firebase operations"""
    
    def __init__(self, db: firestore.Client):
        self.db = db
        self._user_id = None
    
    @property
    def user_id(self) -> Optional[str]:
        return self._user_id
    
    @user_id.setter
    def user_id(self, value: str):
        self._user_id = value
    
    def _get_user_collection(self, collection_name: str) -> firestore.CollectionReference:
        """Get a user-specific collection reference"""
        if not self.user_id:
            raise ValueError("User ID not set")
        return self.db.collection('users').document(self.user_id).collection(collection_name)
    
    def get_transactions(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        notebook_id: Optional[str] = None
    ) -> List[Transaction]:
        """Get transactions with optional filters"""
        collection = self._get_user_collection('transactions')
        query = collection
        
        if notebook_id:
            query = query.where('notebook_id', '==', notebook_id)
        if start_date:
            query = query.where('date', '>=', start_date.strftime('%Y-%m-%d'))
        if end_date:
            query = query.where('date', '<=', end_date.strftime('%Y-%m-%d'))
        
        # Order by date and then by creation time
        query = query.order_by('date', direction=firestore.Query.DESCENDING)
        
        transactions = []
        for doc in query.stream():
            transaction = Transaction.from_dict(doc.id, doc.to_dict())
            transactions.append(transaction)
        
        return transactions
    
    def add_transaction(self, transaction: Transaction) -> Optional[str]:
        """Add a new transaction"""
        collection = self._get_user_collection('transactions')
        transaction.created_at = datetime.now()
        transaction.updated_at = transaction.created_at
        
        doc_ref = collection.add(transaction.to_dict())
        return doc_ref[1].id if doc_ref else None
    
    def update_transaction(self, transaction: Transaction) -> bool:
        """Update an existing transaction"""
        if not transaction.id:
            raise ValueError("Transaction ID is required for update")
        
        collection = self._get_user_collection('transactions')
        transaction.updated_at = datetime.now()
        
        try:
            collection.document(transaction.id).update(transaction.to_dict())
            return True
        except Exception:
            return False
    
    def delete_transaction(self, transaction_id: str) -> bool:
        """Delete a transaction"""
        try:
            self._get_user_collection('transactions').document(transaction_id).delete()
            return True
        except Exception:
            return False
    
    def get_notebooks(self) -> List[Notebook]:
        """Get all notebooks"""
        collection = self._get_user_collection('notebooks')
        query = collection.order_by('created_at', direction=firestore.Query.DESCENDING)
        
        notebooks = []
        for doc in query.stream():
            notebook = Notebook.from_dict(doc.id, doc.to_dict())
            notebooks.append(notebook)
        
        return notebooks
    
    def add_notebook(self, notebook: Notebook) -> Optional[str]:
        """Add a new notebook"""
        collection = self._get_user_collection('notebooks')
        notebook.created_at = datetime.now()
        notebook.updated_at = notebook.created_at
        
        doc_ref = collection.add(notebook.to_dict())
        return doc_ref[1].id if doc_ref else None
    
    def update_notebook(self, notebook: Notebook) -> bool:
        """Update an existing notebook"""
        if not notebook.id:
            raise ValueError("Notebook ID is required for update")
        
        collection = self._get_user_collection('notebooks')
        notebook.updated_at = datetime.now()
        
        try:
            collection.document(notebook.id).update(notebook.to_dict())
            return True
        except Exception:
            return False
    
    def delete_notebook(self, notebook_id: str) -> bool:
        """Delete a notebook and its transactions"""
        try:
            # Start a batch
            batch = self.db.batch()
            
            # Delete the notebook
            notebook_ref = self._get_user_collection('notebooks').document(notebook_id)
            batch.delete(notebook_ref)
            
            # Delete associated transactions
            transactions = self._get_user_collection('transactions').where('notebook_id', '==', notebook_id).stream()
            for transaction in transactions:
                batch.delete(transaction.reference)
            
            # Commit the batch
            batch.commit()
            return True
        except Exception:
            return False
    
    def get_categories(self) -> List[str]:
        """Get all categories"""
        doc = self._get_user_collection('metadata').document('categories').get()
        return doc.to_dict().get('categories', []) if doc.exists else []
    
    def update_categories(self, categories: List[str]) -> bool:
        """Update the list of categories"""
        try:
            self._get_user_collection('metadata').document('categories').set({
                'categories': sorted(list(set(categories))),
                'updated_at': datetime.now()
            })
            return True
        except Exception:
            return False
    
    def get_budgets(self) -> Dict[str, Any]:
        """Get budget settings"""
        doc = self._get_user_collection('metadata').document('budgets').get()
        return doc.to_dict() if doc.exists else {
            'monthly': {'total': 0, 'categories': {}},
            'annual': {'total': 0, 'categories': {}}
        }
    
    def update_budgets(self, budgets: Dict[str, Any]) -> bool:
        """Update budget settings"""
        try:
            budgets['updated_at'] = datetime.now()
            self._get_user_collection('metadata').document('budgets').set(budgets)
            return True
        except Exception:
            return False

    def get_user_collection_ref(self, collection_name: str):
        """Get a reference to a user-specific collection"""
        if "user_id" not in st.session_state:
            return None
        return self.db.collection("users").document(st.session_state.user_id).collection(collection_name)

    # Asset Management
    def fetch_assets(self) -> List[Dict[str, Any]]:
        """Fetch all assets for the current user"""
        if not self.user_id:
            return []
        
        try:
            assets_ref = self.db.collection("users").document(self.user_id).collection("assets")
            assets = []
            
            for doc in assets_ref.stream():
                asset = doc.to_dict()
                asset["id"] = doc.id
                assets.append(asset)
            
            return sorted(assets, key=lambda x: x.get("name", ""))
        except Exception as e:
            st.error(f"Error fetching assets: {str(e)}")
            return []

    def add_asset(self, asset_data: Dict[str, Any]) -> Optional[str]:
        """Add a new asset"""
        if not self.user_id:
            return None
        
        try:
            # Add timestamps
            asset_data["created_at"] = datetime.now()
            asset_data["updated_at"] = datetime.now()
            
            # Add the asset
            doc_ref = self.db.collection("users").document(self.user_id).collection("assets").add(asset_data)
            return doc_ref[1].id
        except Exception as e:
            st.error(f"Error adding asset: {str(e)}")
            return None

    def update_asset(self, asset_id: str, asset_data: Dict[str, Any]) -> bool:
        """Update an existing asset"""
        if not self.user_id:
            return False
        
        try:
            # Update timestamp
            asset_data["updated_at"] = datetime.now()
            
            # Update the asset
            self.db.collection("users").document(self.user_id).collection("assets").document(asset_id).update(asset_data)
            return True
        except Exception as e:
            st.error(f"Error updating asset: {str(e)}")
            return False

    def delete_asset(self, asset_id: str) -> bool:
        """Delete an asset"""
        if not self.user_id:
            return False
        
        try:
            self.db.collection("users").document(self.user_id).collection("assets").document(asset_id).delete()
            return True
        except Exception as e:
            st.error(f"Error deleting asset: {str(e)}")
            return False

    # Transaction Management
    def fetch_transactions(self, start_date=None, end_date=None, notebook_id=None) -> List[Dict[str, Any]]:
        """Fetch transactions for the current user with optional date and notebook filtering"""
        transactions_ref = self.get_user_collection_ref("transactions")
        if not transactions_ref:
            return []
        
        query = transactions_ref
        if start_date:
            query = query.where("date", ">=", start_date)
        if end_date:
            query = query.where("date", "<=", end_date)
        if notebook_id:
            query = query.where("notebook_id", "==", notebook_id)
        
        transactions = query.stream()
        return [{"id": doc.id, **doc.to_dict()} for doc in transactions]

    def add_transaction(self, transaction_data: Dict[str, Any]) -> Optional[str]:
        """Add a new transaction"""
        transactions_ref = self.get_user_collection_ref("transactions")
        if not transactions_ref:
            return None
        
        try:
            # Ensure amount is positive for earnings, negative for expenses
            if transaction_data.get("type") == "earning":
                transaction_data["amount"] = abs(transaction_data["amount"])
            else:  # expense
                transaction_data["amount"] = -abs(transaction_data["amount"])
            
            transaction_data["created_at"] = datetime.now()
            transaction_data["updated_at"] = datetime.now()
            doc_ref = transactions_ref.add(transaction_data)
            return doc_ref[1].id
        except Exception as e:
            st.error(f"Error adding transaction: {str(e)}")
            return None

    def update_transaction(self, transaction_id: str, transaction_data: Dict[str, Any]) -> bool:
        """Update an existing transaction"""
        transactions_ref = self.get_user_collection_ref("transactions")
        if not transactions_ref:
            return False
        
        try:
            # Ensure amount is positive for earnings, negative for expenses
            if "amount" in transaction_data:
                if transaction_data.get("type") == "earning":
                    transaction_data["amount"] = abs(transaction_data["amount"])
                else:  # expense
                    transaction_data["amount"] = -abs(transaction_data["amount"])
            
            transaction_data["updated_at"] = datetime.now()
            transactions_ref.document(transaction_id).update(transaction_data)
            return True
        except Exception as e:
            st.error(f"Error updating transaction: {str(e)}")
            return False

    def delete_transaction(self, transaction_id: str) -> bool:
        """Delete a transaction"""
        transactions_ref = self.get_user_collection_ref("transactions")
        if not transactions_ref:
            return False
        
        try:
            transactions_ref.document(transaction_id).delete()
            return True
        except Exception as e:
            st.error(f"Error deleting transaction: {str(e)}")
            return False

    # Budget Management
    def fetch_budgets(self) -> Optional[Dict[str, Any]]:
        """Fetch budgets for the current user"""
        budgets_ref = self.get_user_collection_ref("budgets")
        if not budgets_ref:
            return None
        
        try:
            budgets_doc = budgets_ref.document("current").get()
            if budgets_doc.exists:
                return budgets_doc.to_dict()
            return None
        except Exception as e:
            st.error(f"Error fetching budgets: {str(e)}")
            return None

    def update_budgets(self, budget_data: Dict[str, Any]) -> bool:
        """Update budgets for the current user"""
        budgets_ref = self.get_user_collection_ref("budgets")
        if not budgets_ref:
            return False
        
        try:
            budget_data["updated_at"] = datetime.now()
            budgets_ref.document("current").set(budget_data)
            return True
        except Exception as e:
            st.error(f"Error updating budgets: {str(e)}")
            return False

    # Category Management
    def fetch_categories(self) -> List[str]:
        """Fetch all categories for the current user"""
        categories_ref = self.get_user_collection_ref("categories")
        if not categories_ref:
            return []
        
        try:
            categories = categories_ref.document("current").get()
            if categories.exists:
                return categories.to_dict().get("categories", [])
            return []
        except Exception as e:
            st.error(f"Error fetching categories: {str(e)}")
            return []

    def update_categories(self, categories: List[str]) -> bool:
        """Update categories for the current user"""
        categories_ref = self.get_user_collection_ref("categories")
        if not categories_ref:
            return False
        
        try:
            categories_ref.document("current").set({
                "categories": list(set(categories)),  # Ensure unique categories
                "updated_at": datetime.now()
            })
            return True
        except Exception as e:
            st.error(f"Error updating categories: {str(e)}")
            return False

    # Notebook Management
    def fetch_notebooks(self) -> List[Dict[str, Any]]:
        """Fetch all notebooks for the current user"""
        notebooks_ref = self.get_user_collection_ref("notebooks")
        if not notebooks_ref:
            return []
        
        notebooks = notebooks_ref.stream()
        return [{"id": doc.id, **doc.to_dict()} for doc in notebooks]

    def add_notebook(self, notebook_data: Dict[str, Any]) -> Optional[str]:
        """Add a new notebook"""
        notebooks_ref = self.get_user_collection_ref("notebooks")
        if not notebooks_ref:
            return None
        
        try:
            notebook_data["created_at"] = datetime.now()
            notebook_data["updated_at"] = datetime.now()
            doc_ref = notebooks_ref.add(notebook_data)
            return doc_ref[1].id
        except Exception as e:
            st.error(f"Error adding notebook: {str(e)}")
            return None

    def update_notebook(self, notebook_id: str, notebook_data: Dict[str, Any]) -> bool:
        """Update an existing notebook"""
        notebooks_ref = self.get_user_collection_ref("notebooks")
        if not notebooks_ref:
            return False
        
        try:
            notebook_data["updated_at"] = datetime.now()
            notebooks_ref.document(notebook_id).update(notebook_data)
            return True
        except Exception as e:
            st.error(f"Error updating notebook: {str(e)}")
            return False

    def delete_notebook(self, notebook_id: str) -> bool:
        """Delete a notebook and all its transactions"""
        notebooks_ref = self.get_user_collection_ref("notebooks")
        if not notebooks_ref:
            return False
        
        try:
            # Start a batch write
            batch = self.db.batch()
            
            # Delete the notebook
            notebook_ref = notebooks_ref.document(notebook_id)
            batch.delete(notebook_ref)
            
            # Delete all transactions in this notebook
            transactions_ref = self.get_user_collection_ref("transactions")
            if transactions_ref:
                transactions = transactions_ref.where("notebook_id", "==", notebook_id).stream()
                for transaction in transactions:
                    batch.delete(transaction.reference)
            
            # Commit the batch
            batch.commit()
            return True
        except Exception as e:
            st.error(f"Error deleting notebook: {str(e)}")
            return False

    def get_notebook_summary(self, notebook_id: str, start_date=None, end_date=None) -> Dict[str, Any]:
        """Get summary statistics for a notebook"""
        transactions = self.fetch_transactions(start_date, end_date, notebook_id)
        
        total_expenses = sum(t["amount"] for t in transactions if t["amount"] < 0)
        total_earnings = sum(t["amount"] for t in transactions if t["amount"] > 0)
        
        # Group transactions by category
        categories = {}
        for t in transactions:
            category = t.get("category", "Uncategorized")
            if category not in categories:
                categories[category] = {"expenses": 0, "earnings": 0}
            
            if t["amount"] < 0:
                categories[category]["expenses"] += abs(t["amount"])
            else:
                categories[category]["earnings"] += t["amount"]
        
        return {
            "total_expenses": abs(total_expenses),
            "total_earnings": total_earnings,
            "net": total_earnings + total_expenses,  # total_expenses is negative
            "categories": categories,
            "transaction_count": len(transactions)
        }
