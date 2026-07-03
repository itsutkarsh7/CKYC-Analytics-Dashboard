# 🏦 CKYC Analytics & Reconciliation Platform

> An enterprise-grade CKYC Reporting, Reconciliation & Analytics Dashboard built using **Python, Flask, Pandas, Plotly, Bootstrap**, and designed for large-scale banking operations.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Flask](https://img.shields.io/badge/Flask-3.x-black)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Engineering-orange)
![Status](https://img.shields.io/badge/Status-Under%20Development-yellow)
![License](https://img.shields.io/badge/License-MIT-green)

---

# 📌 Project Overview

The **CKYC Analytics & Reconciliation Platform** automates reconciliation between multiple CKYC reports, classifies records into operational buckets, calculates business KPIs, and generates an interactive analytics dashboard.

Instead of manually filtering and reconciling Excel reports, users can upload reports and receive real-time operational insights.

---

# 🎯 Objectives

- Automate CKYC reconciliation
- Eliminate manual Excel processing
- Generate real-time dashboards
- Calculate business KPIs
- Provide drill-down analytics
- Support export and reporting

---

# 🏗 Project Architecture

```
                Report A
                    │
                Report B
                    │
           Master Report C
                    │
                    ▼
          Processing Layer
                    │
                    ▼
        Reconciliation Engine
                    │
                    ▼
           MASTER DataFrame
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
      KPI      Product Pivot   WIP
        ▼           ▼           ▼
      Dashboard  Drill-down  Export
```

---

# ⚙️ Technology Stack

| Category | Technology |
|----------|------------|
| Backend | Flask |
| Language | Python 3.12 |
| Data Processing | Pandas, NumPy |
| Database | SQLite (PostgreSQL Ready) |
| Visualization | Plotly |
| Excel Processing | OpenPyXL |
| ORM | SQLAlchemy |
| Frontend | HTML, CSS, Bootstrap 5 |
| Environment | Python Virtual Environment |

---

# 📁 Project Structure

```
CKYC_Dashboard/
│
├── app/
│   ├── routes/
│   ├── processing/
│   ├── reconciliation/
│   ├── analytics/
│   ├── repository/
│   ├── models/
│   ├── templates/
│   ├── static/
│   └── utils/
│
├── uploads/
├── exports/
├── logs/
├── instance/
├── docs/
│
├── run.py
├── config.py
├── requirements.txt
└── README.md
```

---

# 📊 Operational Buckets

Every reconciled record is classified into **exactly one** operational bucket.

- ✅ CKYC Completed
- ⏳ Pending with CERSAI
- 🔄 Under Resolution with Ops
- 📤 CKYC Upload Pending
- 🤖 Auto Resolution
- ⚠️ Issue with CKYC
- 📝 Manually Reported by Ops

---

# 🔄 Data Flow

```
Report A

Report B

Master Report C

        │

        ▼

Upload

        ▼

Validation

        ▼

Cleaning

        ▼

Standardization

        ▼

Merge Reports

        ▼

Business Rule Engine

        ▼

Bucket Assignment

        ▼

MASTER_DF

        ▼

Analytics Engine

        ▼

Dashboard
```

---

# 📈 Dashboard Features

### Top KPI Cards

- Uploaded %
- Completed %
- Pending %
- Resolution %
- Upload Pending %
- Issue %
- Manual %

---

### Product-wise Matrix

Displays

```
Product × Bucket
```

with grand totals.

---

### WIP Dashboard

Displays

- Pending with CERSAI
- Under Resolution
- Upload Pending
- Auto Resolution

along with percentage calculations.

---

### Drill-down

Click any KPI or bucket to view underlying records.

---

# 📂 Input Reports

The application processes three reports.

### Report A

Customer Upload Report

---

### Report B

Operations Report

---

### Report C

Master CKYC Report

---

# 🚀 Current Development Status

## ✅ Completed

- Flask Project Setup
- Application Factory
- Upload Module
- Dashboard Skeleton
- Project Architecture
- Processing Layer
- Data Validation Framework
- Data Cleaning Framework
- Standardization Framework

---

## 🚧 In Progress

- Reconciliation Engine
- Mapping Engine
- Business Rule Engine

---

## 📅 Planned

- KPI Engine
- Product Pivot
- WIP Engine
- Drill-down
- Filters
- Charts
- Export to Excel
- Export to PDF
- Authentication
- Audit Logs
- PostgreSQL Support

---

# 🔮 Future Enhancements

- AI-assisted anomaly detection
- Trend analysis
- Predictive analytics
- Docker deployment
- Kubernetes support
- AWS / Azure deployment
- REST API
- Power BI Integration

---

# ▶️ Installation

Clone the repository

```bash
git clone https://github.com/itsutkarsh7/CKYC-Analytics-Dashboard.git
```

Go to project

```bash
cd CKYC_Dashboard
```

Create virtual environment

```bash
python3 -m venv venv
```

Activate

**macOS/Linux**

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run

```bash
python run.py
```

Application

```
http://127.0.0.1:5000
```

---

# 📌 Roadmap

- [x] Flask Setup
- [x] Upload Module
- [x] Dashboard Skeleton
- [x] Processing Layer
- [ ] Reconciliation Engine
- [ ] Rule Engine
- [ ] Mapping Engine
- [ ] Analytics Engine
- [ ] KPI Dashboard
- [ ] WIP Dashboard
- [ ] Drill-down
- [ ] Charts
- [ ] Export
- [ ] Authentication
- [ ] Deployment

---

# 👨‍💻 Author

**Utkarsh Singh**

Cyber Security | Python | Data Analytics | Flask | SIEM | SOC

GitHub: https://github.com/itsutkarsh7

---

# 📄 License

This project is licensed under the MIT License.

---

⭐ If you found this project interesting, consider giving it a star on GitHub.
