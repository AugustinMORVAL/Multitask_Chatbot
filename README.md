# Multitask Chatbot Project

## Overview

This project aims to develop an AI-powered chatbot that operates seamlessly on any computer setup. The chatbot incorporates various functionalities, including text-based interaction, document processing, and file management. The core of this project is built upon Groq's API, leveraging its powerful language models for efficient and accurate natural language processing.

## Features

### Core Functionalities

- **Text-based Interaction**: The chatbot understands and responds to text-based queries effectively.
- **Context Awareness**: Maintains conversation context for relevant responses.
- **Multiple Language Models**: Supports various LLM models for diverse use cases.

### Document Management

- **PDF Processing**: Ability to read, analyze, and answer questions based on PDF documents.
- **Text Extraction**: Extracts text from uploaded documents for analysis.
- **Multi-format Support**: Handles various file types including PDFs, text files, and potentially other document formats.

## Run Locally

Clone the project

```bash
  git clone https://github.com/AugustinMORVAL/Chatbot_with_Groq.git
```

Install dependencies

```bash
  pip install -r requirements.txt
```

Running the Chatbot

```bash
  streamlit run chatbot.py
```

## Environment Variables

### Necessary API keys
Create a `.env` file in the root directory of your project. This file will store your API keys and other environment variables.

| API keys     | Type     | Description                | Link to Create API Key |
| :------------| :------- | :------------------------- | :--------------------- |
| `GROQ_API_KEY` | `string` | **Required**. Your API key | [Create Groq API Key](https://console.groq.com/keys) |

## Future Enhancements
- **Proccessed files**: Enhancing the ability to handle a variety of file types.
- **Advanced Analytics**: Providing users with analytics and insights based on their interactions.
- **Web navigation**: Enabling the chatbot to browse and search web content.
- And more !

## Development Tools and Technologies

This project heavily relies on Groq's API and language models for its core functionality. Groq provides the backbone for our chatbot's natural language understanding and generation capabilities.

### Available LLM models
- **Gemma Model 2 - 9B**: A highly advanced model designed for comprehensive language understanding and generation tasks.

- **Gemma Model - 7B**: An efficient model suitable for various natural language processing tasks with a balance of performance and computational efficiency.

- **LLaMA 3 - 70B**: A robust model known for its large-scale language understanding capabilities, ideal for complex queries and detailed responses.

- **LLaMA 3 - 8B**: A smaller version of the LLaMA model that provides quick and efficient responses while maintaining high accuracy.

- **Mixtral - 8x7B**: A powerful ensemble model that combines multiple models to deliver superior performance and accuracy in language tasks.

### Additionnal tools 

- **Whisper Large V3**: An advanced model optimized for understanding and generating spoken language, making it ideal for audio processing tasks.

## Ongoing Work

- Enhancing document processing capabilities
- Expanding supported file types for upload and analysis
- Improving the user interface and experience

## Future Enhancements

- **Web Navigation**: Enable the chatbot to browse and search web content
- **Advanced Analytics**: Provide insights based on user interactions
- **Multi-modal Interactions**: Combine text and visual inputs

## Contributing

Contributions are welcome! Please fork the repository and submit pull requests for any features, bug fixes, or improvements.
