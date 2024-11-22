from langchain.chains import RetrievalQA
from langchain_openai.chat_models import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

my_key = ""

def load_vectorstore(load_path):
    embeddings = OpenAIEmbeddings(api_key=my_key)
    vectorstore = FAISS.load_local(load_path, embeddings, allow_dangerous_deserialization=True)
    return vectorstore

# Retrieval
vectorstore = load_vectorstore("vectorstore")
retriever = vectorstore.as_retriever()
query = "Which chart is suitable for comparing different categories over time?"
qa_chain = RetrievalQA.from_llm(
    ChatOpenAI(api_key=my_key), retriever=retriever
)

response = qa_chain(query)
print("Generated Response:", response)