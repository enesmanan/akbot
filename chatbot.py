import os
import openai
import warnings
import pandas as pd 
from dotenv import load_dotenv
from pandasai.llm import OpenAI
from pandasai import SmartDataframe
from pandasai.connectors import PandasConnector
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import ChatPromptTemplate

warnings.filterwarnings('ignore')
os.environ['G_ENABLE_DIAGNOSTIC'] = '0'
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Set your OpenAI API Key
load_dotenv()
openai.api_key = os.environ['OPENAI_API_KEY']

llm = OpenAI(api_token=os.environ['OPENAI_API_KEY'])

# Constants for OpenAI Chatbot
CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
Soruyu yalnızca aşağıdaki bağlama dayanarak cevapla:

{context}

Yukarıdaki bağlama dayanarak soruyu cevapla: {question}
"""

# Load your data
data = pd.read_csv('Data/harcama_gecmisi.csv')

# Field descriptions for the data
field_descriptions = {
    'Yıl': 'Harcamanın yapıldığı yıl. (Örneğin: 2024)',
    'Ay': 'Harcamanın yapıldığı ay. (Örneğin: Ocak)',
    'Gün': 'Harcamanın yapıldığı gün. (Örneğin: 15)',
    'Tarih': 'Harcamanın yapıldığı tarih. (Örneğin: 2024-01-15)',
    'İşlem Türü': 'Harcamanın türü. Bu, harcamanın hangi kategoriye girdiğini belirtir. (Örneğin: Alışveriş, Fatura Ödemesi, ATM Çekimi, Restoran, Ulaşım)',
    'Tutar': 'Harcamanın parasal değeri. (Örneğin: 150.75)',
    'Harcama Kategorisi': 'Harcamanın yapıldığı genel kategori. (Örneğin: Market, Elektrik, Su, İnternet, ATM, Restoran, Ulaşım)',
    'Açıklama': 'Harcama hakkında daha spesifik bilgi veren açıklama. Genellikle mağaza adı veya fatura türü gibi detaylar içerir. (Örneğin: Migros, Kebapçı, Otobüs)',
}

# PandasAI configuration
config = {
    'llm': llm,
    'save_charts': True,
    'save_charts_path': 'exports/charts',
    'open_charts': False,
    'max_retries': 2
}

# Create the connector and SmartDataframe
connector = PandasConnector(
    {"original_df": data},
    field_descriptions=field_descriptions
)

df = SmartDataframe(connector,
    description="Kişinin banka hesabından yaptığı harcama kayıtları",
    config=config
)

# Function to handle PandasAI prompts
def tr_promts(df, prompt):
    tr_promt = " Cevabı Türkçe olarak 1 kez döndür. Eğer grafik istiyorsam sadece 1 kez grafiği çiz."
    full_prompt = prompt + tr_promt
    response = df.chat(full_prompt)
    return response


# Function to handle OpenAI chatbot queries
def main(query_text):
    embedding_function = OpenAIEmbeddings(openai_api_key=os.environ['OPENAI_API_KEY'])
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    results = db.similarity_search_with_relevance_scores(query_text, k=3)
    if len(results) == 0 or results[0][1] < 0.7:
        print("Mesajınızı anlayamadım, size yardımcı olabilmemiz için 444 25 25 Telefon Bankacılığımızdan bize ulaşabilirsiniz.")
        return

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    model = ChatOpenAI(openai_api_key=os.environ['OPENAI_API_KEY'])
    response_text = model.invoke(prompt)
    print(response_text.content)

# Main function to switch between chatbots
def chatbot(query_text):
    if query_text.startswith('/'):
        pandas_response = tr_promts(df, query_text[1:])
        print(pandas_response)
    else:
        main(query_text)

if __name__ == "__main__":
    user_input = input("Size nasıl yardımcı olabilirim: ")
    chatbot(user_input)
