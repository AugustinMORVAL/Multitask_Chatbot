import fitz  # PyMuPDF
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from pydantic import ConfigDict

class PDFManager:
    def __init__(self, db_directory="./pdf_db"):
        self.database = db_directory
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.vector_store = None

    def process_pdf(self, pdf_file):
        # Extract text from PDF
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()

        # Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_text(text)

        # Create or update vector store
        if self.vector_store is None:
            self.vector_store = Chroma.from_texts(chunks, self.embeddings, persist_directory=self.database)
        else:
            self.vector_store.add_texts(chunks)

        self.vector_store.persist()

    def query_pdf(self, chatbot_manager, model, question, temperature):
        if self.vector_store is None:
            raise ValueError("No PDFs have been processed yet.")

        qa_chain = RetrievalQA.from_chain_type(
            llm=chatbot_manager,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever()
        )

        return qa_chain.run(question)
