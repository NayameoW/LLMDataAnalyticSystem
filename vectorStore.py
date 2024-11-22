import json
from langchain.docstore.document import Document
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

my_key = ""

# Read files from doc
chart_info = json.load(open("info/chart_info.json"))
word_info = json.load(open("info/word_info.json"))

docs = [
    Document(page_content=f"{k}: {v}") for k, v in {**chart_info, **word_info}.items()
]

# Store
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
all_splits = text_splitter.split_documents(docs)
vectorstore = FAISS.from_documents(documents=all_splits, embedding=OpenAIEmbeddings(api_key=my_key))

# output
vectorstore.save_local("vectorstore")
