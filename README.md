
# 🔐 Secure Record Access Portal

<p align="center">
<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&pause=1000&center=true&vCenter=true&width=900&lines=Secure+Record+Access+Portal;SIH+2026+Skill+Assessment;Flask+%7C+SQLite+%7C+bcrypt+%7C+Secure+Coding" />
</p>

<p align="center">

![Python](https://img.shields.io/badge/Python-3.7+-3776AB?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-2.3.2-black?style=for-the-badge&logo=flask)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite)
![bcrypt](https://img.shields.io/badge/bcrypt-Secure-orange?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Completed-success?style=for-the-badge)

</p>

---

# 📌 Overview

A secure institutional portal demonstrating secure authentication, authorization and protection against common attacks.

## ✨ Features

- Secure Login
- Registration
- bcrypt Password Hashing
- SQL Injection Protection
- Role Based Access Control
- User Isolation
- Attack Demonstration
- SQLite Database

## 🏗 Architecture

```mermaid
flowchart TD
A[Browser] --> B[Flask App]
B --> C[Authentication]
C --> D[Authorization]
D --> E[(SQLite)]
```

## 🔄 Login Workflow

```mermaid
sequenceDiagram
User->>Flask: Login
Flask->>SQLite: Parameterized Query
SQLite-->>Flask: User
Flask->>bcrypt: Verify Password
bcrypt-->>Flask: Valid
Flask-->>User: Dashboard
```

## 🛡 Security Dashboard

| Threat | Protection | Status |
|---|---|---|
| SQL Injection | Parameterized Queries | ✅ |
| Password Theft | bcrypt | ✅ |
| Unauthorized Access | RBAC | ✅ |
| Cross User Access | Ownership Checks | ✅ |

## 📂 Structure

```text
secure-portal/
├── app.py
├── portal.db
├── requirements.txt
├── README.md
├── screenshots/
└── .gitignore
```

## 🚀 Installation

```bash
git clone <repo>
cd secure-portal
python -m venv venv
```

Activate:

Windows

```bash
venv\Scripts\activate
```

Linux

```bash
source venv/bin/activate
```

Install:

```bash
pip install -r requirements.txt
python app.py
```

Open:

http://localhost:5000

## 🧪 Security Tests

<details>
<summary>SQL Injection</summary>

Attempt:
`admin' OR '1'='1`

Expected: Blocked

</details>

<details>
<summary>Admin Access</summary>

Normal user cannot access admin routes.

</details>

<details>
<summary>User Isolation</summary>

Users can only access their own records.

</details>

## 📸 Screenshots

Add screenshots:

- login.png
- register.png
- dashboard.png
- admin.png
- attack_test.png

## 🎥 Demo

Record:
1. Registration
2. Login
3. SQL Injection blocked
4. RBAC
5. User isolation
6. Admin panel

## 🗺 Roadmap

- MFA
- JWT
- Docker
- HTTPS
- Audit Logs

## 📜 License

Educational project for SIH 2026.

<p align="center">
⭐ If you like this project, consider giving it a star!
</p>
