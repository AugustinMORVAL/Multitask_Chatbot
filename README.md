# Multitask Chatbot Project

## Overview

This AI-powered chatbot operates seamlessly on any computer setup, incorporating text-based interaction, document processing, and file management. Built on Groq's API, it leverages powerful language models for efficient and accurate natural language processing.

## Table of Contents
- [Overview](#overview)
- [Features](#-features)
  - [Core Functionalities](#core-functionalities)
  - [Document Management](#document-management)
- [Run Locally](#️-run-locally)
- [Environment Variables](#-environment-variables)
- [Development Tools and Technologies](#-development-tools-and-technologies)
  - [Available LLM Models](#available-llm-models)
  - [Chain of Thought (CoT) Reasoning](#-chain-of-thought-cot-reasoning)
  - [Additional Tools](#additional-tools)
- [Future Enhancements](#-future-enhancements)
- [Contributing](#-contributing)

## 🚀 Features

### Core Functionalities

- 💬 **Text-based Interaction**: Understands and responds to queries effectively
- 🧠 **Context Awareness**: Maintains conversation context for relevant responses
- 🔄 **Multiple Language Models**: Supports various LLM models for diverse use cases
- 🤔 **Chain of Thought (CoT) Reasoning**: Enables step-by-step reasoning for complex queries

### Document Management

- 📄 **PDF Processing**: Reads, analyzes, and answers questions based on PDF documents
- 📝 **Text Extraction**: Extracts text from uploaded documents for analysis
- 📁 **Multi-format Support**: Handles PDFs, text files, images, PowerPoint, and Excel files (IN PROGRESS)

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

## 🧰 Development Tools and Technologies

### Available LLM Models

- 🧠 **Gemma Model 2 - 9B**: Google's open-source model, optimized for efficiency and performance
- 🚀 **Gemma Model - 7B**: Smaller variant of Gemma, balancing speed and capability
- 🐑 **LLaMA 3 - 70B**: Meta's largest model, excelling in complex reasoning and generation tasks
- 🐑 **LLaMA 3 - 8B**: Compact LLaMA variant, suitable for resource-constrained environments
- 🔄 **Mixtral - 8x7B**: Mistral AI's mixture-of-experts model, combining multiple specialized sub-models

### 🧠 Chain of Thought (CoT) Reasoning

This chatbot now supports Chain of Thought reasoning, allowing for more transparent and step-by-step problem-solving. When enabled, the chatbot will:

1. 🤔 **Think**: Analyze the query and break it down into steps
2. 📝 **Plan**: Outline a strategy to address the question
3. 🔍 **Research**: Gather relevant information from its knowledge base
4. 💡 **Reason**: Apply logical reasoning to the gathered information
5. 🎯 **Conclude**: Formulate a final answer based on the reasoning process

### Additional Tools

- 🎙️ **Whisper Large V3**: Advanced spoken language processing

## 🔮 Future Enhancements

- 📊 **Advanced Analytics**: User interaction insights
- 🌐 **Web Navigation**: Browse and search web content
- 🖼️ **Multi-modal Interactions**: Combine text and visual inputs
- 🗄️ **Database Integration**: 
  - Connect to external databases for expanded knowledge access
  - Support local file storage for personalized document management

## 🤝 Contributing

Contributions are welcome! Fork the repository and submit pull requests for features, bug fixes, or improvements.
