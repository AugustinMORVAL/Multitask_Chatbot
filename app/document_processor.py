import tempfile
import os
from datetime import datetime
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

@dataclass
class ProcessingResult:
    """Data class to hold document processing results"""
    success: bool
    chunks: List[Document]
    error: Optional[str] = None
    metadata: Dict[str, Any] = None

class DocumentProcessor:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """Initialize the DocumentProcessor with specified embedding model."""
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            encode_kwargs={'normalize_embeddings': True} 
        )
        self.vector_store = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", ".", "!", "?", " ", ""],
            length_function=len,
        )
        self._initialize_session_state()

    def _initialize_session_state(self) -> None:
        """Initialize session state for document tracking."""
        if "document_stats" not in st.session_state:
            st.session_state.document_stats = {
                "total_documents": 0,
                "total_chunks": 0,
                "processed_files": set(),
                "last_update": None,
                "file_details": {}
            }

        if "local_database" in st.session_state and st.session_state.local_database:
            self.vector_store = st.session_state.local_database

    def chunk_pdf(self, pdf_files: List[Any]) -> Tuple[List[Document], Optional[FAISS]]:
        """Process multiple PDF files and create/update vector store."""
        if not pdf_files:
            return [], self.vector_store

        all_chunks = []
        processing_stats = {
            "successful": 0,
            "failed": 0,
            "total_chunks": 0
        }

        with st.spinner("Processing documents..."):
            for pdf_file in pdf_files:
                if self._is_file_processed(pdf_file):
                    st.info(f"📝 {pdf_file.name} was already processed, skipping...")
                    continue

                result = self._process_single_file(pdf_file)
                
                if result.success:
                    all_chunks.extend(result.chunks)
                    processing_stats["successful"] += 1
                    processing_stats["total_chunks"] += len(result.chunks)
                    self._update_stats(pdf_file, result)
                    st.success(f"✅ Successfully processed {pdf_file.name}")
                else:
                    processing_stats["failed"] += 1
                    st.error(f"❌ Failed to process {pdf_file.name}: {result.error}")

        if all_chunks:
            try:
                self.vector_store = self._update_vector_store(all_chunks)
                self._save_processing_stats(processing_stats)
            except Exception as e:
                st.error(f"Failed to update vector store: {str(e)}")
                return all_chunks, self.vector_store

        return all_chunks, self.vector_store

    def _process_single_file(self, pdf_file: Any) -> ProcessingResult:
        """Process a single PDF file with enhanced error handling."""
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(pdf_file.read())
                temp_path = Path(temp_file.name)

            loader = PyPDFLoader(str(temp_path))
            pages = loader.load()
            
            chunks = self.text_splitter.split_documents(pages)
            
            for i, chunk in enumerate(chunks):
                chunk.metadata.update({
                    "file_name": pdf_file.name,
                    "file_type": pdf_file.type,
                    "page_number": chunk.metadata.get("page", 0),
                    "chunk_index": i,
                    "chunk_size": len(chunk.page_content),
                    "processing_timestamp": datetime.now().isoformat(),
                    "total_chunks": len(chunks)
                })

            return ProcessingResult(
                success=True,
                chunks=chunks,
                metadata={
                    "total_pages": len(pages),
                    "total_chunks": len(chunks),
                    "average_chunk_size": sum(len(c.page_content) for c in chunks) / len(chunks) if chunks else 0
                }
            )

        except Exception as e:
            return ProcessingResult(
                success=False,
                chunks=[],
                error=str(e)
            )
        finally:
            if temp_path and temp_path.exists():
                try:
                    os.unlink(temp_path)
                except Exception as e:
                    st.warning(f"Failed to clean up temporary file: {str(e)}")

    def _update_vector_store(self, chunks: List[Document]) -> FAISS:
        """Update or create vector store with new chunks."""
        try:
            if self.vector_store is None:
                return FAISS.from_documents(chunks, self.embeddings)
            
            self.vector_store.add_documents(chunks)
            return self.vector_store
        except Exception as e:
            st.error(f"Error updating vector store: {str(e)}")
            raise

    def _is_file_processed(self, pdf_file: Any) -> bool:
        """Check if a file has already been processed."""
        return pdf_file.name in st.session_state.document_stats["processed_files"]

    def _update_stats(self, pdf_file: Any, result: ProcessingResult) -> None:
        """Update session state with processing statistics."""
        stats = st.session_state.document_stats
        stats["total_documents"] += 1
        stats["total_chunks"] += len(result.chunks)
        stats["processed_files"].add(pdf_file.name)
        stats["last_update"] = datetime.now().isoformat()
        
        if not hasattr(stats, "file_details"):
            stats["file_details"] = {}
            
        stats["file_details"][pdf_file.name] = {
            "chunks": len(result.chunks),
            "processed_at": datetime.now().isoformat(),
            **result.metadata
        } if result.metadata else {}

    def _save_processing_stats(self, stats: Dict[str, int]) -> None:
        """Save processing statistics and display summary."""
        if stats["successful"] > 0:
            st.success(
                f"✅ Successfully processed {stats['successful']} files "
                f"({stats['total_chunks']} total chunks created)"
            )
        if stats["failed"] > 0:
            st.warning(f"⚠️ Failed to process {stats['failed']} files")