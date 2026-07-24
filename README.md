# 🔐 Secure Record Access Portal

![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![Flask](https://img.shields.io/badge/Flask-2.x-black)
![SQLite](https://img.shields.io/badge/SQLite-Database-blue)
![Security](https://img.shields.io/badge/Security-SQL_Injection_Prevention-green)
![bcrypt](https://img.shields.io/badge/bcrypt-Password_Hashing-orange)

## 📌 Project Overview

A secure institutional portal demonstrating essential security practices for protecting sensitive records. The application implements secure authentication, server-side authorization, and defenses against common web attacks.

## 🎯 Objectives

- Store passwords using bcrypt (slow salted hashing)
- Prevent SQL Injection using parameterized queries
- Enforce server-side role-based access control
- Restrict users to their own records
- Demonstrate security controls through attack simulations

## ✨ Features

- Secure Login & Registration
- bcrypt Password Hashing
- SQLite Database
- Role-Based Access Control
- Record Management
- SQL Injection Protection
- User Isolation
- Attack Demonstration Page

## 🛠 Technology Stack

| Component | Technology |
|---|---|
| Backend | Flask |
| Language | Python |
| Database | SQLite3 |
| Authentication | Flask Sessions |
| Password Storage | bcrypt |
| Frontend | HTML, CSS |

## 📂 Project Structure

```text
secure-portal/
├── app.py
├── portal.db
├── requirements.txt
├── README.md
├── .gitignore
└── screenshots/
```

## 🛡 Security Features

| Threat | Defense |
|---|---|
| SQL Injection | Parameterized Queries |
| Password Theft | bcrypt Hashing |
| Unauthorized Access | Server-side RBAC |
| Cross-user Access | Ownership Validation |

## 🚨 Attack Demonstration

### 1. SQL Injection
Attempt:
```
admin' OR '1'='1
```
Expected Result: Login blocked.

### 2. Unauthorized Admin Access
Regular users attempting admin routes are denied by server-side authorization.

### 3. Cross-user Access
Users can only view and manage records they own.

## 🚀 Installation

```bash
git clone <repository-url>
cd secure-portal
python -m venv venv
```

Windows

```bash
venv\Scripts\activate
```

Linux/macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run

```bash
python app.py
```

Open:

```
http://localhost:5000
```

## 🔑 Default Accounts

| Username | Password | Role |
|---|---|---|
| admin | admin123 | Administrator |
| user1 | user123 | User |
| user2 | user123 | User |

## 📸 Screenshots

Add screenshots inside the `screenshots/` folder.

- login.png
- register.png
- user_dashboard.png
- admin_dashboard.png
- attack_test.png
- database_view.png

## 🎥 Demonstration Video

Record and include:
1. Registration
2. Login
3. SQL Injection attempt
4. Role-based access test
5. User isolation
6. Admin features
7. Attack test page

## 📈 Future Improvements

- Multi-factor Authentication
- JWT Authentication
- Audit Logs
- Docker Deployment
- HTTPS
- Email Verification

## 📜 License

Created for educational purposes as part of the SIH 2026 Skill Assessment.

---
⭐ If you found this project useful, consider giving the repository a star.
