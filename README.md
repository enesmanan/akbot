# AKbot

This project was developed as the final project for the 7-week Bootcamp jointly organized by Akbank and Patika. 

**Features:**
- **RAG:** Provides answers to all your Akbank questions
- **PandasAI:** Delivers the analysis you need from your spending history
- **Machine Learning:** Predicts next month's prices by category
- **Campaign Recommendations:** Combines GenAI and rule-based systems to suggest personalized campaigns

## Technologies Used

- **Frontend:** HTML, CSS, JavaScript, Streamlit
- **GenAI:** LangChain, OpenAI, PandasAI
- **Machine Learning:** scikit-learn, XGboost
- **Database:** SQLite, Chroma


## Architecture
![akbank_patika_mimari](https://github.com/user-attachments/assets/0b12fd25-6a71-4a7b-9e2e-6dc77b717e79)

---

## Requirements

### Environment

Ensure that your Python version is set to `3.10.12` (pip version is `24.1.2`):

```bash
python --version
```
- Setting up Virtualenv:

```bash
pip install virtualenv
```
- Creating a Virtual Environment:
```bash
virtualenv venv
```
- Activating the Virtual Environment:
```bash
source venv/bin/activate
```
- Installing the necessary libraries:
```bash
pip install -r requirements.txt
```

### Configuration

- Set up your .env file:

```bash
cd <project-directory>
```

```bash
- Create the .env file and add your OPENAI_API_KEY:

    OPENAI_API_KEY='key' # .env file

```
### Create VectorDB

```bash
python3 create_database.py
```

### Create ML Model

```bash
python3 model.py
```

### Run

- Launch the Streamlit app in terminal:
```bash
streamlit run akbot_streamlit.py
```
---


https://github.com/user-attachments/assets/f309b9db-99c0-49ad-9c1c-f63e4cda4329


