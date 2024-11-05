import tempfile
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

class DocumentProcessor:
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name
        )
    
    def initialize_session_state(self):
        pass

    def chunk_pdf(self, pdf_files):
        """Process the uploaded PDF file, create chunks, and store them."""
        all_chunks = []
        for pdf_file in pdf_files:
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                    temp_file.write(pdf_file.read())
                    temp_file_path = temp_file.name

                # Load and extract text from the PDF
                loader = PyPDFLoader(temp_file_path)
                pages = loader.load()
                document_text = "".join([page.page_content for page in pages])

                # Split the document into chunks
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=300,
                    chunk_overlap=40
                )
                chunks = text_splitter.create_documents([document_text])
                
                # Add document information to each chunk
                for chunk in chunks:
                    chunk.metadata.update({
                        "file_name": pdf_file.name,
                        "file_type": pdf_file.type,
                    })
                all_chunks.extend(chunks)

            except Exception as e:
                print(f"Error processing {pdf_file.name}: {e}")
        return all_chunks