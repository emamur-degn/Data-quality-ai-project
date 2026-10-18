# DataQualityAI — বাংলা সেটআপ গাইড

## প্রজেক্টে কী আছে?
- CSV upload
- Missing value, duplicate row ও blank string checks
- Isolation Forest দিয়ে numerical anomaly detection
- Plotly charts
- SQLite analysis history
- ঐচ্ছিক OpenAI API দিয়ে root-cause explanation
- JSON report ও anomaly CSV download

## ১) প্রয়োজনীয় সফটওয়্যার
Python 3.11 বা 3.12 এবং VS Code ইনস্টল করুন।

## ২) প্রজেক্ট ফোল্ডারে Terminal খুলুন
Windows PowerShell:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```
যদি PowerShell activation policy error দেয়, নতুন Command Prompt খুলে চালান:
```bat
.venv\Scripts\activate.bat
```

## ৩) অ্যাপ চালান
```powershell
streamlit run app.py
```
Browser-এ Streamlit-এর দেওয়া local URL খুলুন। সাধারণত `http://localhost:8501`।

## ৪) প্রথম পরীক্ষা
- Sidebar থেকে **Upload & Analyze** নির্বাচন করুন।
- `sample_data.csv` ফাইল আপলোড করুন।
- **Run quality checks** চাপুন।
- quality metrics, issue table, anomaly records এবং report দেখুন।
- Dashboard ও Run History পেজও পরীক্ষা করুন।

## ৫) AI analysis চালু করতে (ঐচ্ছিক)
প্রজেক্ট ফোল্ডারে `.env.example` কপি করে `.env` নাম দিতে পারেন, কিন্তু এই starter app স্বয়ংক্রিয়ভাবে `.env` লোড করে না। সহজ পদ্ধতি: PowerShell-এ environment variable সেট করুন:
```powershell
$env:OPENAI_API_KEY="আপনার_API_KEY"
$env:OPENAI_MODEL="gpt-4.1-mini"
streamlit run app.py
```
API key কখনও GitHub-এ commit করবেন না। API ব্যবহার করলে খরচ হতে পারে। AI checkbox না দিলে API কল হবে না।

## ৬) ফোল্ডার কাঠামো
```text
dataquality_ai_project/
├── app.py
├── data_quality.py
├── storage.py
├── llm_analysis.py
├── requirements.txt
├── sample_data.csv
├── .env.example
└── README_BN.md
```

## গুরুত্বপূর্ণ সীমাবদ্ধতা
- Quality score এখানে একটি সরল heuristic; এটি শিল্প-মানের পূর্ণাঙ্গ score নয়।
- Isolation Forest-এর anomaly ফলাফল সম্ভাব্য অস্বাভাবিকতা, নিশ্চিত ভুল নয়।
- প্রথম সংস্করণে email/Slack alerts এবং Airflow scheduler নেই; পরের ধাপে যোগ করা যাবে।
- সংবেদনশীল/ব্যক্তিগত ডেটা বাইরের AI API-তে পাঠাবেন না। এই কোড aggregate findings পাঠায়, raw records নয়।
