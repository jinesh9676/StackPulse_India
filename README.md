# 📈 StackPulse India

A realtime Stock Portfolio, Profit/Loss, and Recovery Management System built with Python, Streamlit, SQLite, Plotly and Yahoo Finance.
Users can securely manage their stock investments, track profit & loss, monitor stock recovery progress, and receive intelligent portfolio insights through an interactive dashboard.

## 🚀 Features

Authentication
  User Registration
  Secure Login
  Logout
  Password Hashing (bcrypt)
  Password Reset Token
  Session Management

### 👥 Roles

## 1. Admin (Owner)

Default Administrator Account
Username: owner
Password: jineshah
Role: admin

## Admin Permissions

✅ View all users
✅ View all portfolios
✅ View application statistics
✅ Manage stocks
✅ Manage alerts
✅ Manage user accounts
✅ Reset user passwords
✅ Activate/Deactivate users
✅ View system logs
✅ Report errors
✅ Manage application settings

### 2. User

## User Permissions

✅ Register account
✅ Login
✅ Edit profile
✅ Change password
✅ Add stocks
✅ Update stocks
✅ Delete stocks
✅ Track profit/loss
✅ Recovery tracker
✅ Portfolio dashboard
✅ Create alerts
✅ Download reports
❌ Cannot view other users
❌ Cannot access admin pages
❌ Cannot modify application settings

## 📊 Portfolio Management

Users can:
  Add new stock holdings
  Edit holdings
  Remove holdings
  View total investments
  Monitor portfolio value

## 💹 Profit & Loss Tracking

Automatic calculation:

Investment Amount
Current Value
Profit
Loss
ROI %
Net Portfolio Value

## 🎯 Recovery Tracker

If stock price falls below purchase price:
Example

Buy Price = ₹3000
Current Price = ₹2500
Recovery Needed = ₹500

Recovery Progress:

83.33%

Shows:
  Recovery Percentage
  Breakeven Price
  Distance to Recovery

## 📈 Interactive Dashboard

Charts:
  Portfolio Allocation
  Profit vs Loss
  Top Gainers
  Top Losers
  Sector Analysis
  Recovery Progress
Powered by Plotly.

## 🔔 Alerts

Users can create:
  Profit Target Alert
  Loss Alert
  Recovery Alert

## 🛠 Technology Stack

Frontend  Streamlit
Backend  Python
Database  SQLite
Security  bcrypt,secrets
Analytics  pandas,numpy
Visualization  plotly
Live Stock Data  yfinance
Source Control  Git,GitHub
Deployment in Streamlit Community Cloud

## 🗄 Database

Database File at stockpulse.db

Database tables:
users
portfolio
alerts
settings
logs

## Database Schema

## Users

sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name  NOT NULL,
    username  UNIQUE NOT NULL,
    email  UNIQUE NOT NULL,
    mobile ,
    password_hash  NOT NULL,
    role  DEFAULT 'user',
    status  DEFAULT 'active',
    recovery_token ,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

## Portfolio

sql
CREATE TABLE portfolio (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    stock_symbol ,
    quantity INTEGER,
    buy_price REAL,
    buy_date DATE,
    FOREIGN KEY(user_id)
    REFERENCES users(id)
);

## 🔐 Privacy Policy

## For Users

StackPulse India stores:
  Name
  Username
  Email
  Mobile Number
  Portfolio Data

StackPulse India does NOT store:
  Bank Account Details
  Trading Account Credentials
  UPI PIN
  Credit Card Information
  Broker Passwords
Passwords are encrypted using bcrypt hashing.
Users can only access their own data.

## For Admin (Owner)

Administrator access is restricted.
The Owner can:
 View registered users
 View portfolio information
 Manage platform operations

Owner responsibilities:
 Protect user data
 Never share login credentials
 Never disclose portfolio information
 Maintain system security

## ⚠ Error Handling

Admin Error Panel:
Dashboard Errors
Database Errors
Login Errors
API Errors
Portfolio Errors

Errors are stored in: logs table

Example Log:
Error ID
Date
User
Error Type
Description

## 📂 Project Structure

StackPulse_India/
│
├── app.py
├── requirements.txt
├── README.md
├── stockpulse.db
│
├── auth/
│   ├── login.py
│   ├── register.py
│   ├── security.py
│
├── database/
│   ├── db.py
│   ├── init_db.py
│
├── pages/
│   ├── Dashboard.py
│   ├── Portfolio.py
│   ├── Profit_Loss.py
│   ├── Recovery_Tracker.py
│   ├── Profile.py
│   └── Admin.py
│
├── utils/
│   ├── stock_api.py
│   ├── calculations.py
│   ├── alerts.py
│
├── assets/
│
└── env/

## 📦 requirements.txt

streamlit
pandas
numpy
plotly
yfinance
bcrypt
sqlalchemy
requests

## ⚙ Installation

Clone repository
bash
git clone <https://github.com/jinesh9676/StackPulse_India.git>

Navigate
bash
cd StackPulse_India

Create virtual environment
bash
python m venv env

Activate
Windows
bash
env\Scripts\activate

Install packages
bash
pip install r requirements.txt

Run application
bash
streamlit run app.py

Open port <http://localhost:8501>

## 🌐 Deployment

GitHub Repository path <https://github.com/jinesh9676/StackPulse_India>

## Streamlit Cloud

Deploy directly using:

Repository:
jinesh9676/StackPulse_India
Branch:
main
Main File:
app.py

## 🗺 Data Flow Diagram

User/Admin
     |
     v
Authentication
     |
     v
SQLite Database
     |
     v
Portfolio Manager
     |
     v
Yahoo Finance API
     |
     v
Profit/Loss Engine
     |
     ++
     |             |
     v             v
Dashboard   Recovery Tracker
     |
     v
Alerts & Reports

## 👨‍💻 Author

Jinesh Paras Shah
GitHub: <https://github.com/jinesh9676>
Repository: <https://github.com/jinesh9676/StackPulse_India>

## License

MIT License

⭐ Please Star this Repository if you find it useful.
Demo Account (owner/jineshah) in Admin:

## 👑 Default Admin Account

A default administrator account is created during the first application startup.

Username: owner
Password: jineshah
Role: Admin

Admin permissions:
 View all users
 View all portfolios
 Manage stocks
 Manage alerts
 View system statistics
 Manage application settings
 Create/Delete users
 Reset user passwords
⚠️ Security Notice
For production deployment, change the default admin password immediately after first login.
The admin password is stored as a bcrypt hash in the SQLite database and is never stored in plain .

## StackPulse India v1.0.0

Indian stock portfolio analytics; no trade execution.

## Windows

Extract to your project directory (back up existing files first). Run `python app.py` in CMD. This creates env and installs requirements on first run. `python app.py update` refreshes dependencies. If Python is absent use start.bat (winget, then reopen CMD). Open <http://localhost:8501>. In another CMD run `env\Scripts\python create_admin.py` to create the owner. No default password.

## Cloud

Push source to GitHub, excluding env, database and secrets. Deploy app.py in Streamlit Community Cloud; dependencies install from requirements.txt. Configure Google OIDC using .streamlit/secrets.toml.example in local secrets.toml or cloud secrets; change redirect URI to deployed URL plus /oauth2callback. Generate a random cookie secret. SQLite cloud storage is ephemeral: use durable hosting/storage before production. Admin provisioning on cloud requires a trusted shell or preconfigured persistent database; never commit a populated database.

## Design

User/Admin > authentication > SQLite > portfolio > Yahoo Finance > P/L > dashboard/recovery/alerts. Users have onetomany holdings and alerts. Admin manages user status, reset tokens, stock catalog, alerts and announcement. Google accounts are not automatically linked to existing email accounts. Password reset is adminassisted, not email delivery. Alerts run on page visits only. Prices are latest daily close; no guaranteed recovery or realtime feed. No brokerage assumed; taxes excluded. Recovery ratio = current/buy*100 capped at 100; required gain = (buy/current1)*100. Reports are CSV. Stock catalog is a starter list, not all Indian companies. Non-listed companies are not assigned fictitious tickers.

## Limitations

MVP: no automated email alerts, trade execution, rate limiting, audit grade logs, admin user deletion, or persistent cloud database provisioning. Production needs these security/operations reviews, licensed market data if required, backups and integration testing. Streamlit native widgets used rather than Bootstrap to avoid conflicting layouts. Views folder avoids automatic unprotected Streamlit page discovery. Existing databases require migration; do not overwrite them.

## Tests

`python m unittest discover s tests`.
