# Multitask Chatbot Project

## Overview

This AI-powered chatbot is built with Streamlit and integrates with Groq's API. It provides a user-friendly interface for text-based interactions, document processing and database connectivity.

## Table of Contents
- [Overview](#overview)
- [Features](#-features)
  - [Core Functionalities](#core-functionalities)
  - [Document Management](#document-management)
- [Run Locally](#️-run-locally)
- [Environment Variables](#-environment-variables)
- [Development Tools and Technologies](#-development-tools-and-technologies)
- [Contributing](#-contributing)

## 🚀 Features

### Core Functionalities

- 💬 **Text-based Interaction**: Understands and responds to queries effectively
- 🧠 **Context Awareness**: Maintains conversation context for relevant responses
- 🎯 **Model Selection**: Automatically selects the appropriate model based on the query complexity
- 🤖 **Agent-based Architecture**: Utilizes LangChain's React agent for advanced reasoning and tool use

### Document Management

- 📄 **Document Processing**: Support for various document formats including:
  - PDF files (using PyMuPDF)
  - PowerPoint presentations (python-pptx)
  - Excel spreadsheets (openpyxl)
- 📝 **Text Extraction**: OCR capabilities using Tesseract
- 🔍 **Vector Search**: Document embeddings using sentence-transformers and FAISS

## 🛠️ Run Locally

1. Clone the project
   ```bash
   git clone https://github.com/AugustinMORVAL/Multitask_Chatbot.git
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Run the Chatbot
   ```bash
   streamlit run chatbot.py
   ```

## 🔑 Environment Variables

The application supports two methods for configuration:

### Option 1: Using a .env file

Create a `.env` file in the root directory with your API keys:

```env
GROQ_API_KEY=your-api-key-here
```

### Option 2: Using Streamlit Secrets

For Streamlit Cloud deployment, create `.streamlit/secrets.toml`:

```toml
groq_api_key = "your-api-key-here"
```

> Note: Both `.env` and `.streamlit/secrets.toml` are included in `.gitignore` for security.

## 🧰 Development Tools and Technologies

### Core Dependencies
- 🎯 **Streamlit**: Web interface and application framework
- 🤖 **LangChain**: LLM integration and chain management
- 🔍 **Vector Search**: FAISS for efficient similarity search
- 📄 **Document Processing**: 
  - PyMuPDF for PDF handling
  - python-pptx for PowerPoint files
  - openpyxl for Excel files
  - pytesseract for OCR
- 🔤 **Embeddings**: sentence-transformers for text embeddings
- 🌐 **Web Search**: DuckDuckGo integration
- 📊 **Database**: SQLAlchemy and MongoDB support

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.
