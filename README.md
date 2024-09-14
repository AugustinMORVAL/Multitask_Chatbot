# Multitask Chatbot Project

## Overview

This AI-powered chatbot operates seamlessly on any computer setup, incorporating text-based interaction, document processing, and file management. Built on Groq's API, it leverages powerful language models for efficient and accurate natural language processing.

## 🚀 Features

### Core Functionalities

- 💬 **Text-based Interaction**: Understands and responds to queries effectively
- 🧠 **Context Awareness**: Maintains conversation context for relevant responses
- 🔄 **Multiple Language Models**: Supports various LLM models for diverse use cases

### Document Management

- 📄 **PDF Processing**: Reads, analyzes, and answers questions based on PDF documents
- 📝 **Text Extraction**: Extracts text from uploaded documents for analysis
- 📁 **Multi-format Support**: Handles PDFs, text files, and potentially other formats

## 🛠️ Run Locally

1. Clone the project
   ```bash
   git clone https://github.com/AugustinMORVAL/Chatbot_with_Groq.git
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

Create a `.env` file in the root directory to store your API keys:

| API Key | Type | Description | Get API Key |
|---------|------|-------------|-------------|
| `GROQ_API_KEY` | `string` | **Required** | [Create Groq API Key](https://console.groq.com/keys) |

## 🔮 Future Enhancements

- 📊 **Advanced Analytics**: User interaction insights
- 🌐 **Web Navigation**: Browse and search web content
- 🖼️ **Multi-modal Interactions**: Combine text and visual inputs

## 🧰 Development Tools and Technologies

### Available LLM Models

- 🧠 **Gemma Model 2 - 9B**: Advanced comprehensive language understanding
- 🚀 **Gemma Model - 7B**: Efficient for various NLP tasks
- 🐑 **LLaMA 3 - 70B**: Robust large-scale language understanding
- 🐑 **LLaMA 3 - 8B**: Quick and efficient responses
- 🔄 **Mixtral - 8x7B**: Powerful ensemble model for superior performance

### Additional Tools

- 🎙️ **Whisper Large V3**: Advanced spoken language processing

## 🚧 Ongoing Work

- Enhancing document processing capabilities
- Expanding supported file types
- Improving user interface and experience

## 🤝 Contributing

Contributions are welcome! Fork the repository and submit pull requests for features, bug fixes, or improvements.
