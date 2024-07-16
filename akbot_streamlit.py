import os
import glob
import openai
import warnings  
import pandas as pd
import streamlit as st   
from datetime import datetime
from dotenv import load_dotenv
from streamlit_chat import message
from pandasai.llm import OpenAI
from pandasai import SmartDataframe
from pandasai.connectors import PandasConnector
from streamlit_extras.colored_header import colored_header
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import ChatPromptTemplate
#from rulebased_campaign import handle_campaign_query_rule
from genai_campaign import handle_campaign_query
from model import load_model, predict_next_month, visualize_results, load_and_preprocess_data, engineer_features

warnings.filterwarnings('ignore')
os.environ['G_ENABLE_DIAGNOSTIC'] = '0'
warnings.filterwarnings("ignore", category=DeprecationWarning)

st.set_page_config(page_title="AkBot", page_icon="")


# OpenAI API key and Chroma DB path
load_dotenv()
openai.api_key = os.environ['OPENAI_API_KEY']

CHROMA_PATH = "chroma"

# Chat Prompt Template
PROMPT_TEMPLATE = """
Soruyu yalnızca aşağıdaki Akbank ile ilgili bağlama dayanarak cevapla:

{context}

Yukarıdaki bağlama dayanarak soruyu cevapla: {question}

Cevabı Türkçe olarak, samimi ve ikna edici bir dille yaz.

"""

# Initialize PandasAI and SmartDataframe
llm = OpenAI(api_token=os.environ['OPENAI_API_KEY'])

data = pd.read_csv('harcama_verisi.csv')

field_descriptions = {
    'Yıl': 'Harcamanın yapıldığı yıl. (Örneğin: 2024)',
    'Ay': 'Harcamanın yapıldığı ay. (Örneğin: Ocak)',
    'Gün': 'Harcamanın yapıldığı gün. (Örneğin: 15)',
    'Tarih': 'Harcamanın yapıldığı tarih. (Örneğin: 2024-01-15)',
    'Saat': 'Harcamanın yapıldığı saat. (Örneğin: 15:30)',
    'İşlem Türü': 'Harcamanın türü. Bu, harcamanın hangi kategoriye girdiğini belirtir. (Örneğin: Giyim, Ulaşım, Fatura, Restoran)',
    'Harcama Kategorisi': 'Harcamanın yapıldığı genel kategori. (Örneğin: Zara, Benzin, Elektrik, Kebapçı)',
    'Şehir': 'Harcamanın yapıldığı şehir. (Örneğin: İstanbul, Ankara, İzmir)',
    'Tutar': 'Harcamanın parasal değeri. (Örneğin: 150.75)'        
}


config = {
    'llm': llm,
    'save_charts': True,
    'save_charts_path': 'exports/charts',
    'open_charts': False,
    'max_retries': 2}


connector = PandasConnector(
    {"original_df": data},
    field_descriptions=field_descriptions)


df = SmartDataframe(connector,
    description="Kişinin banka hesabından yaptığı harcama kayıtları",
    config=config
    )

# Load the trained model
model = load_model("model.pkl")

def get_latest_chart_file(directory):
    list_of_files = glob.glob(os.path.join(directory, '*.png'))
    if not list_of_files:
        return None
    
    latest_file = max(list_of_files, key=os.path.getctime)  
    return latest_file

def tr_promts(df, prompt):
    tr_promt = " Cevabı Türkçe olarak 1 kez döndür. Eğer grafik istiyorsam sadece 1 kez grafiği çiz."
    full_prompt = prompt + tr_promt
    response = df.chat(full_prompt)    
    latest_chart = get_latest_chart_file('exports/charts')
    return response, latest_chart

def handle_next_month_prediction():
    next_month = datetime.now().month + 1
    next_year = datetime.now().year
    if next_month > 12:
        next_month = 1
        next_year += 1

    df = load_and_preprocess_data('harcama_verisi.csv')
    df = engineer_features(df)
    
    predictions = predict_next_month(model, df, next_year, next_month)
    save_path = f"exports/model_charts/next_month_spending.png"
    chart_path, category_totals, total_spending = visualize_results(predictions, save_path)

    response = f"Gelecek ay (Ay: {next_month}, Yıl: {next_year}) için harcama tahminlerinizi hazırladım.\n\n"
    response += f"Toplam tahmini harcama: {total_spending:,.2f} TL\n\n"
    response += "Harcama kategorilerine göre dağılım:\n"
    for category, total in category_totals.items():
        response += f"{category}: {total:,.2f} TL\n"
    
    return response, chart_path


def handle_query(query_text):
    if query_text.lower() == "gelecek ay harcamalarım ne olur":
        response, chart_path = handle_next_month_prediction()
        return response, chart_path, "model"
    elif query_text.startswith('/'):
        # Process query using PandasAI
        response, chart_path = tr_promts(df, query_text[1:])
        return response, chart_path, "pandasai"
    else:
        # campaign check
        campaign_response = handle_campaign_query(data, query_text)
        if campaign_response:
            return campaign_response, None, None
        response = generate_response(query_text)
        return response, None, None

def generate_response(query_text):
    # Handle regular queries as before
    embedding_function = OpenAIEmbeddings(openai_api_key=os.environ['OPENAI_API_KEY'])
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search the DB.
    results = db.similarity_search_with_relevance_scores(query_text, k=3)
    if len(results) == 0 or results[0][1] < 0.7:
        return "Mesajınızı anlayamadım, size yardımcı olabilmemiz için 444 25 25 Telefon Bankacılığımızdan bize ulaşabilirsiniz."

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    model = ChatOpenAI(openai_api_key=os.environ['OPENAI_API_KEY'])
    response_text = model.invoke(prompt)

    return response_text.content

# Streamlit UI setup
st.markdown("<h1 style='color: red;'>AkBot</h1>", unsafe_allow_html=True)

#colored_header(label='', description='', color_name='red-70')


# Custom CSS for the background and message colors
st.markdown(
    """
    <style>
    .stApp {
        background-color: white;
    }
    .user-message {
        background-color: #EEEEEE;
        border-radius: 8px;
        padding: 10px;
        margin: 5px 0;
        margin-left: auto;
        color: black;
        width: fit-content;
        max-width: 80%;
    }
    .bot-message {
        background-color: #DC1410;
        border-radius: 8px;
        padding: 10px;
        margin: 5px 0;
        color: white;
        width: fit-content;
        max-width: 80%;
    }
    .bot-message img {
    position: absolute;
    bottom: 10px;
    left: -60px; 
    width: 50px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state variables
if 'user_responses' not in st.session_state:
    st.session_state['user_responses'] = ["Merhaba"]
if 'bot_responses' not in st.session_state:
    st.session_state['bot_responses'] = ["Merhaba, ben akıl küpü chat asistanınız Akbot. Size nasıl yardımcı olabilirim?"]
if 'chart_paths' not in st.session_state:
    st.session_state['chart_paths'] = [None]
if 'chart_types' not in st.session_state:
    st.session_state['chart_types'] = [None]

input_container = st.container()
response_container = st.container()

# Capture user input and display bot responses
user_input = st.text_input("Mesaj yazın: ", "", key="input")

with response_container:
    if user_input:
        response, chart_path, chart_type = handle_query(user_input)
        st.session_state.user_responses.append(user_input)
        st.session_state.bot_responses.append(response)
        st.session_state.chart_paths.append(chart_path)
        st.session_state.chart_types.append(chart_type)

    if st.session_state['bot_responses']:
        for i in range(len(st.session_state['bot_responses'])):
            st.markdown(f'<div class="user-message">{st.session_state["user_responses"][i]}</div>', unsafe_allow_html=True)
            col1, col2 = st.columns([1, 8])
            with col1:
                st.image("images/logo2.png", width=50, use_column_width=True, clamp=True, output_format='auto')
            with col2:
                bot_response = st.session_state["bot_responses"][i]
                st.markdown(f'<div class="bot-message">{bot_response}</div>', unsafe_allow_html=True)
                if st.session_state['chart_paths'][i]:
                    if st.session_state['chart_types'][i] == "pandasai":
                        # PandasAI 
                        st.image(st.session_state['chart_paths'][i], use_column_width=True)
                    elif st.session_state['chart_types'][i] == "model":
                        # model.py 
                        st.image(st.session_state['chart_paths'][i], use_column_width=True)


with input_container:
    display_input = user_input
