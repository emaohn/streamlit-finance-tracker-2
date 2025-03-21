from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import date


# Base class for common fields
class Asset(BaseModel):
    name: str  # Name of the asset (e.g., "Fidelity CD", "Capital One Bank Account")
    type: str  # Type of asset (e.g., "Certificate of Deposit", "Bank Account")
    company: Optional[str] = None  # Company or bank associated with the asset (e.g., "Fidelity", "Capital One")
    value: float  # Current value of the asset


# Certificate of Deposit Asset
class CertificateOfDeposit(Asset):
    type: str = "Certificate of Deposit"  # Type is fixed for this class
    interest_rate: float  # Interest rate (e.g., 3.5 for 3.5%)
    maturity_date: date  # Maturity date (when the CD expires)

    class Config:
        schema_extra = {
            "example": {
                "name": "Fidelity CD",
                "type": "Certificate of Deposit",
                "company": "Fidelity",
                "value": 10000.0,
                "interest_rate": 3.5,
                "maturity_date": "2025-12-31",
            }
        }


# Liquid / Bank Account Asset
class BankAccount(Asset):
    type: str = "Bank Account"  # Type is fixed for this class
    account_type: Literal["Checking", "Savings"]  # Type of bank account

    class Config:
        schema_extra = {
            "example": {
                "name": "Capital One Checking",
                "type": "Bank Account",
                "company": "Capital One",
                "value": 5000.0,
                "account_type": "Checking",
            }
        }


# Taxable Investment Asset (e.g., brokerage accounts)
class TaxableInvestment(Asset):
    type: str = "Taxable Investment"  # Type is fixed for this class
    holdings: dict[str, int]  # Dictionary of asset holdings in the account (e.g., {"AAPL": 50, "TSLA": 100})

    class Config:
        schema_extra = {
            "example": {
                "name": "Fidelity Brokerage",
                "type": "Taxable Investment",
                "company": "Fidelity",
                "value": 15000.0,
                "holdings": {"AAPL": 50, "TSLA": 100},
            }
        }


# Retirement Account Asset (e.g., 401(k), IRA)
class RetirementAccount(Asset):
    type: str = "Retirement Account"  # Type is fixed for this class
    account_type: Literal["401(k)", "IRA", "Roth IRA"]  # Type of retirement account
    contribution_limit: Optional[float] = None  # Contribution limit for the year (if applicable)

    class Config:
        schema_extra = {
            "example": {
                "name": "Fidelity 401(k)",
                "type": "Retirement Account",
                "company": "Fidelity",
                "value": 20000.0,
                "account_type": "401(k)",
                "contribution_limit": 19500.0,
            }
        }


# Main class to handle all asset types
class Portfolio(BaseModel):
    assets: list[Asset]

    class Config:
        schema_extra = {
            "example": {
                "assets": [
                    {
                        "name": "Fidelity CD",
                        "type": "Certificate of Deposit",
                        "company": "Fidelity",
                        "value": 10000.0,
                        "interest_rate": 3.5,
                        "maturity_date": "2025-12-31",
                    },
                    {
                        "name": "Capital One Checking",
                        "type": "Bank Account",
                        "company": "Capital One",
                        "value": 5000.0,
                        "account_type": "Checking",
                    },
                    {
                        "name": "Fidelity Brokerage",
                        "type": "Taxable Investment",
                        "company": "Fidelity",
                        "value": 15000.0,
                        "holdings": {"AAPL": 50, "TSLA": 100},
                    },
                    {
                        "name": "Fidelity 401(k)",
                        "type": "Retirement Account",
                        "company": "Fidelity",
                        "value": 20000.0,
                        "account_type": "401(k)",
                        "contribution_limit": 19500.0,
                    }
                ]
            }
        }
