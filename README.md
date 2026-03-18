# 🛒 Walmart Analytics Dashboard — Streamlit App

## 📁 Folder Setup

Place these files in the SAME folder:
```
walmart_dashboard/
├── app.py
├── requirements.txt
└── Walmart.csv        ← your data file
```

---

## ⚙️ Step-by-Step Setup in VS Code

### Step 1 — Install Python
Download from https://python.org (3.9 or higher)

### Step 2 — Open folder in VS Code
```
File → Open Folder → select walmart_dashboard/
```

### Step 3 — Open Terminal in VS Code
```
Terminal → New Terminal  (or Ctrl + `)
```

### Step 4 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 5 — Run the app
```bash
streamlit run app.py
```

The app will open automatically at: http://localhost:8501

---

## 🤖 AI Assistant Setup

1. Go to https://console.anthropic.com
2. Create an account and generate an API key
3. Paste the key into the "Enter your Anthropic API Key" field in the app

---

## 🎛️ Features

- **KPI Cards** — Revenue, Transactions, Rating, Top Branch
- **Sidebar Filters** — Filter by Category, Payment Method, City
- **Overview Tab** — Revenue by category, payment pie chart, top branches, ratings
- **Categories Tab** — Bubble chart + summary table
- **Trends Tab** — Monthly revenue line chart, city revenue, profit margin histogram
- **AI Assistant Tab** — Chat with Claude about your data

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` again |
| `FileNotFoundError: Walmart.csv` | Make sure Walmart.csv is in the same folder as app.py |
| App not opening | Go to http://localhost:8501 manually |
| API key error | Check your key at console.anthropic.com |
