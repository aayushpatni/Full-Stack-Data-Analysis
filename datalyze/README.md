# 🧬 Datalyze — Intelligent Full-Stack Data Analysis Platform

A beautiful, full-featured web application for uploading datasets and generating automatic AI-powered dashboards with PDF reports.

---

## ✨ Features

| Feature | Details |
|---|---|
| 🔐 Auth | Email + OTP two-factor login & registration |
| 🔥 Streaks | Daily streak counter — gain +1 for each upload day |
| 📊 Auto Dashboard | Histograms, correlation heatmaps, pie charts, box plots, scatter, time-series |
| 🧹 Data Cleaning | Detects missing values, outliers, duplicates automatically |
| 📋 Statistics | Full descriptive stats table for all numeric columns |
| 🤖 AI Insights | Written insights about skewness, outliers, correlations, date ranges |
| ⏱ Live Timer | Animated timer shows real analysis time |
| ⬇ PDF Report | Download a beautiful multi-page PDF with all charts + insights |
| 📁 Formats | CSV, Excel (.xlsx/.xls), JSON |

---

## 🚀 Quick Start

### 1. Install Python dependencies

```bash
pip install flask pandas numpy matplotlib seaborn scipy reportlab openpyxl
```

> Note: `plotly` is optional and not required. All charts are rendered server-side via matplotlib.

### 2. Run the application

```bash
cd datalyze
python app.py
```

### 3. Open in browser

```
http://localhost:5000
```

---

## 🗂 Project Structure

```
datalyze/
├── app.py              # Flask backend (auth, analysis, PDF report)
├── templates/
│   └── index.html      # Full single-page frontend
├── uploads/            # Temporary dataset uploads (auto-created)
├── reports/            # Generated PDF reports (auto-created)
└── README.md
```

---

## 🔐 Authentication Flow

1. **Register**: Enter name, email, password → OTP sent to email → Verify OTP → Account created
2. **Login**: Enter email + password → OTP sent → Verify OTP → Logged in
3. **Session**: Managed server-side via Flask sessions

> **Demo Mode**: Since no SMTP is configured by default, the OTP is shown in the response message and printed to the terminal. To enable real email delivery, configure `MAIL_SERVER`, `MAIL_USERNAME`, `MAIL_PASSWORD` in `app.py` and use Flask-Mail.

---

## 📊 Analysis Engine

The backend automatically:

1. **Reads** CSV / Excel / JSON datasets
2. **Cleans** — handles nulls, infinities, type coercion
3. **Detects** numeric, categorical, and date columns
4. **Generates charts**:
   - Missing values heatmap
   - Numeric distribution histograms
   - Correlation matrix heatmap
   - Categorical bar charts
   - Pie chart (top categorical column)
   - Box plots with outlier detection
   - Time series (if date columns found)
   - Scatter + regression line
5. **Computes** descriptive statistics (mean, std, percentiles, etc.)
6. **Writes insights** about skewness, correlations, outliers, coverage
7. **Exports** a fully styled PDF report via ReportLab

---

## 🛡 Security Notes

- Passwords are SHA-256 hashed before storage
- OTPs expire after 5–10 minutes
- Sessions are signed with a secret key
- File size limit: 50 MB
- Only CSV / Excel / JSON accepted (extension + parse validation)

> For production: use PostgreSQL/MongoDB instead of in-memory dicts, configure HTTPS, use proper secret key management, and set up SMTP.

---

## 📦 Tech Stack

| Layer | Tech |
|---|---|
| Backend | Python + Flask |
| Data | pandas, numpy, scipy |
| Charts | matplotlib, seaborn |
| PDF | reportlab |
| Frontend | Vanilla HTML/CSS/JS (zero dependencies) |
| Fonts | Syne + DM Sans (Google Fonts) |

---

Made with ❤️ — Datalyze
