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
  - [Agent and Tools](#agent-and-tools)
  - [Additional Tools](#additional-tools)
- [Future Enhancements](#-future-enhancements)
- [Contributing](#-contributing)

## 🚀 Features

### Core Functionalities

- 💬 **Text-based Interaction**: Understands and responds to queries effectively
- 🧠 **Context Awareness**: Maintains conversation context for relevant responses
- 🔄 **Multiple Language Models**: Supports various LLM models for diverse use cases
- 🤖 **Agent-based Architecture**: Utilizes LangChain's React agent for advanced reasoning and tool use

### Document Management

- 📄 **PDF Processing**: Reads, analyzes, and answers questions based on PDF documents
- 📝 **Text Extraction**: Extracts text from uploaded documents for analysis
- 📁 **Database Integration**: Supports both local file storage and external database connections

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

You can set up your environment variables using either a `.env` file or Streamlit secrets:

### Option 1: Using a .env file

Create a `.env` file in the root directory to store your API keys:

| API Key | Type | Description | Get API Key |
|---------|------|-------------|-------------|
| `GROQ_API_KEY` | `string` | **Required** | [Create Groq API Key](https://console.groq.com/keys) |

### Option 2: Using Streamlit Secrets (Recommended for Streamlit Cloud)

If you're deploying your app on Streamlit Cloud, you can use Streamlit secrets to securely store your API keys:

1. Create a file named `.streamlit/secrets.toml` in your project directory.
2. Add your API key to this file:

```toml
groq_api_key = "your-api-key-here"
```

3. If deploying to Streamlit Cloud, add these secrets in the app settings.

The chatbot will automatically use the API key from Streamlit secrets if available, falling back to prompting the user for input if not found.

> Note: Never commit your `.env` file or `.streamlit/secrets.toml` to version control. Add them to your `.gitignore` file to prevent accidental exposure of your API keys.

## 🧰 Development Tools and Technologies

### Available LLM Models

- 🐑 **LLaMA 3 - 70B**: Meta's largest model, excelling in complex reasoning and generation tasks
- 🔄 **Mixtral - 8x7B**: Mistral AI's mixture-of-experts model, combining multiple specialized sub-models
- 🔹 **Gemma 2 - 9B**: Google's instruction-tuned variant of the Gemma model family

### Agent and Tools

The chatbot now uses LangChain's React agent with the following tools:

- 🌐 **Web Search**: Utilizes DuckDuckGo for current events and online information
- 🧮 **Calculator**: Performs mathematical calculations
- 💬 **Ask for Information**: Prompts the user for additional details when needed
- 🗃️ **Database Query**: Executes SQL queries on connected databases (when available)

### Additional Tools

- 🎙️ **Whisper Large V3**: Advanced spoken language processing (planned integration)

## 🔮 Future Enhancements

- 📊 **Advanced Analytics**: User interaction insights
- 🌐 **Web Navigation**: Improved web content browsing and search
- 🖼️ **Multi-modal Interactions**: Combine text and visual inputs
- 🗄️ **Enhanced Database Integration**: 
  - Improved support for external databases
  - Advanced querying and data analysis capabilities

## 🤝 Contributing

Contributions are welcome! Fork the repository and submit pull requests for features, bug fixes, or improvements.
