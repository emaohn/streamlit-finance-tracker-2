from datetime import date, datetime, timedelta

# Helper function to generate dates relative to today
def get_relative_date(days_ago):
    return (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")

data = {
    "assets": [
        {
            "name": "3 Month CD",
            "type": "Certificate of Deposit",
            "company": "Marcus by Goldman Sachs",
            "value": 10000,
            "interest_rate": 4.5,
            "maturity_date": (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d")
        },
        {
            "name": "6 Month CD",
            "type": "Certificate of Deposit",
            "company": "Marcus by Goldman Sachs",
            "value": 10000,
            "interest_rate": 4.7,
            "maturity_date": (datetime.now() + timedelta(days=180)).strftime("%Y-%m-%d")
        },
        {
            "name": "9 Month CD",
            "type": "Certificate of Deposit",
            "company": "Marcus by Goldman Sachs",
            "value": 10000,
            "interest_rate": 4.8,
            "maturity_date": (datetime.now() + timedelta(days=270)).strftime("%Y-%m-%d")
        },
        {
            "name": "12 Month CD",
            "type": "Certificate of Deposit",
            "company": "Marcus by Goldman Sachs",
            "value": 10000,
            "interest_rate": 5.0,
            "maturity_date": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
        },
        {
            "name": "Individual Brokerage",
            "type": "Taxable Investment",
            "company": "Fidelity",
            "value": 53000,
            "holdings": {
                "AAPL": 50,
                "MSFT": 40,
                "VTI": 100
            }
        },
        {
            "name": "Roth IRA",
            "type": "Retirement Account",
            "company": "Fidelity",
            "value": 36000,
            "account_type": "Roth IRA",
            "contribution_limit": 6500
        },
        {
            "name": "401(k)",
            "type": "Retirement Account",
            "company": "Fidelity",
            "value": 85000,
            "account_type": "401(k)",
            "contribution_limit": 22500
        },
        {
            "name": "Checking Account",
            "type": "Bank Account",
            "company": "Chase",
            "value": 5000,
            "account_type": "Checking"
        },
        {
            "name": "High Yield Savings",
            "type": "Bank Account",
            "company": "Ally",
            "value": 15000,
            "account_type": "Savings"
        }
    ],
    "expenses": [
        {
            "description": "Trader Joes",
            "amount": 56.73,
            "category": "Groceries",
            "date": get_relative_date(15),
            "recurring": False
        },
        {
            "description": "Pharmacy",
            "amount": 22.13,
            "category": "Healthcare",
            "date": get_relative_date(20),
            "recurring": False
        },
        {
            "description": "Ski Pass",
            "amount": 700,
            "category": "Entertainment",
            "date": get_relative_date(1),
            "recurring": False
        },
        {
            "description": "Ski Rentals",
            "amount": 150,
            "category": "Entertainment",
            "date": get_relative_date(2),
            "recurring": False
        },
        {
            "description": "Lululemon",
            "amount": 173,
            "category": "Shopping",
            "date": get_relative_date(10),
            "recurring": False
        },
        {
            "description": "Guus",
            "amount": 103.23,
            "category": "Dining",
            "date": get_relative_date(12),
            "recurring": False
        },
        {
            "description": "Rent",
            "amount": 2000,
            "category": "Home",
            "date": get_relative_date(1),
            "recurring": True
        },
        {
            "description": "Internet",
            "amount": 65,
            "category": "Utilities",
            "date": get_relative_date(5),
            "recurring": True
        },
        {
            "description": "Phone",
            "amount": 45,
            "category": "Utilities",
            "date": get_relative_date(15),
            "recurring": True
        },
        {
            "description": "Gym",
            "amount": 85,
            "category": "Entertainment",
            "date": get_relative_date(1),
            "recurring": True
        }
    ],
    "earnings": [
        {
            "description": "Salary",
            "amount": 5000,
            "category": "Primary Income",
            "date": get_relative_date(15),
            "recurring": True
        },
        {
            "description": "Bonus",
            "amount": 2000,
            "category": "Bonus",
            "date": get_relative_date(20),
            "recurring": False
        }
    ]
}