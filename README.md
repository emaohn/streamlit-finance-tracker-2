# Finance Tracker

A modern personal finance tracking application built with Streamlit and Firebase. Track your expenses, earnings, budgets, and financial goals with an intuitive and responsive interface.

## Features

- **Comprehensive Dashboard**: Monitor your financial health with key metrics and visualizations
- **Transaction Management**: Track both expenses and earnings with detailed categorization
- **Notebooks**: Organize transactions into dedicated notebooks for specific events or purposes
- **Budget Tracking**: Set and monitor monthly and annual budgets by category
- **Financial Analysis**: View spending patterns, trends, and category breakdowns
- **Secure Authentication**: Firebase-powered user authentication and data storage

## Project Structure

```
src/
├── components/      # Reusable UI components
├── models/         # Data models (Transaction, Notebook)
├── services/       # Firebase and authentication services
├── ui/            # Main UI components and forms
└── utils/         # Utility functions
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up Firebase:
- Create a Firebase project at [Firebase Console](https://console.firebase.google.com)
- Enable Email/Password authentication
- Create a Firestore database
- Download service account key and save as `firestore-key.json`

3. Run the application:
```bash
streamlit run app.py
```

## Firebase Configuration

The application requires the following Firebase configuration:
- Project ID: `streamlit-finance-tracker-2`
- Web API Key: Configure in `src/services/auth.py`
- Auth Domain: Configure in `src/services/auth.py`
- Service Account Key: Save as `firestore-key.json` in project root

## Data Model

### Transactions
- Description
- Amount (negative for expenses, positive for earnings)
- Category
- Date
- Notebook (optional)
- Recurring flag
- Notes (optional)

### Notebooks
- Name
- Description (optional)
- Category
- Budget (optional)
- Date range (optional)

### Budgets
- Monthly and annual budgets
- Category-specific allocations
- Progress tracking

## Development

The application follows these design principles:
- Clean separation of concerns (models, services, UI)
- Type hints for better code maintainability
- Comprehensive error handling
- Responsive and intuitive UI
- Efficient Firestore queries with proper indexing

## Dependencies

Core dependencies:
- `streamlit`: Web application framework
- `firebase-admin`: Firebase Admin SDK
- `google-cloud-firestore`: Firestore client
- `pandas`: Data manipulation
- `altair`: Data visualization

See `requirements.txt` for complete list of dependencies.