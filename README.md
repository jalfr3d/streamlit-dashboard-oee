# 📊 Streamlit OEE Dashboard

A multi-page **Streamlit dashboard** designed for monitoring operational performance through key industrial metrics such as **OEE (Overall Equipment Effectiveness)**, productivity, and working hours. The application includes authentication, role-based access, and interactive analytics powered by an Excel data source.

<img width="1921" height="951" alt="dashboard" src="https://github.com/user-attachments/assets/8845aad5-0983-40d3-852b-470a40ebe9bb" />

---

## 🚀 Features

### 🔐 Authentication System

* Login page with **multi-role support**
* Role-based access control (customizable)
* Secure session handling
* Logout functionality

---

### 📈 Dashboard Pages

#### 1. OEE Overview

* Displays key **OEE KPIs**
* Interactive visualizations
* Performance breakdown (Availability, Performance, Quality)

#### 2. Hours Analysis

* KPIs related to working hours
* Graphs for time distribution and trends
* Useful for identifying inefficiencies in time usage

#### 3. Productivity Analysis

* Productivity-focused KPIs
* Comparative and trend-based charts
* Helps evaluate operational output

---

### 📅 Date Filtering

* Available across all dashboard pages
* Select:

  * A specific month
  * Or aggregate across **all months**

---

### 📬 Contact Page

* Built-in **contact form**
* Includes **CAPTCHA verification**
* Configurable to send messages using your own **Gmail account**

---

### 📂 Data Source

* Uses an **Excel file** as the database
* Easy to update and maintain without needing a full database system

---

## 🛠️ Tech Stack

* **Python**
* **Streamlit**
* **Pandas**
* **Plotly / Matplotlib** (depending on implementation)
* **OpenPyXL** (Excel handling)

---

## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/jalfr3d/streamlit-dashboard-oee.git
```

### 2. Create virtual environment (recommended)

```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows
# or
source .venv/bin/activate      # macOS/Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the App

```bash
streamlit run app.py
```

---

## ⚙️ Configuration

### 📧 Gmail Setup (for Contact Form)

To enable email sending:

1. Use a Gmail account
2. Enable **App Passwords** (recommended)
3. Add credentials to your environment variables or config file:

```bash
sender = os.getenv("GMAIL_SENDER")
secret = os.getenv("APP_PASS_GMAIL")
recipient = os.getenv("RECIPIENT_EMAIL")
```

---

### 📊 Excel Data

* Place your Excel file in the project directory
* Ensure it follows the expected schema (columns used by the dashboard)
* Update file path in the code if needed

---

## 🔐 Roles Configuration

* Roles can be defined in:

  * A config file
  * Hardcoded dictionary
  * External source (optional)

Example:

```python
users = {
    "admin": {"password": "1234", "role": "admin"},
    "user": {"password": "abcd", "role": "viewer"}
}
```

---

## 📁 Project Structure 

```
├── app.py
├── DataBaseProduction.xlsx
├── users.json
├── images/
|   └── logo.jpg
├── pages/
│   ├── account.py
│   ├── contact.py
│   ├── hours.py
|   ├── oee.py
│   └── productivity.py
├── utils/
│   ├── auth.py│   
│   └── data_loader.py
├── requirements.txt
└── README.md
```

---

## 🧩 Notes

* The app is designed to be **modular and extensible**
* Excel-based backend makes it easy to prototype and deploy quickly
* Suitable for **internal dashboards** or lightweight analytics tools

---

## 📌 Future Improvements

* Replace Excel with SQL database
* Add user registration system
* Improve role granularity
* Deploy to cloud (Streamlit Cloud / AWS / Azure)

---

## 👨‍💻 Author

Developed as a custom Streamlit analytics solution.

---

## 📄 License

This project is open-source and available under the MIT License.
