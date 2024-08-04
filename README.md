
# Multitask Chatbot Project
![Logo](https://github.com/AugustinMORVAL/Chatbot_with_Groq/blob/main/img/logo-Cyy6uKYt.png)


## Overview

This project aims to develop an AI-powered chatbot that operates seamlessly on any computer setup. The project includes basic functionalities and additional features such as audio processing and file management.
## Features

### Core Functionalities

- **Text-based Interaction**: The chatbot can understand and respond to text-based queries effectively.
- **Context Awareness**: The chatbot maintains the context of the conversation to provide relevant responses.

### Additional Features

- **Audio Processing**:
  - **Speech Recognition**: Converts spoken language into text to enable voice-based interaction.
  - **Text-to-Speech**: Converts text responses into speech, providing a more natural and interactive user experience.
- **File Management**:
  - **File Upload/Download**: Users can upload and download files through the chatbot interface.
  - **File Processing**: The chatbot can read, understand, and manipulate the content of various file types (e.g., text, PDF).

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
  streamlit run app/feature_you_want_to_run.py
```


## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

### Necessary API keys
Create a `.env` file in the root directory of your project. This file will store your API keys and other environment variables.

| API keys     | Type     | Description                | Link to Create API Key |
| :------------| :------- | :------------------------- | :--------------------- |
| `HF_TOKEN`   | `string` | **Required**. Your API key | [Create Hugging Face API Key](https://huggingface.co/settings/tokens) |
| `GROQ_API_KEY` | `string` | **Required**. Your API key | [Create Groq API Key](https://console.groq.com/keys) |


### (Additionnal) Loading Environment Variables in Your Python Code

Install the `python-dotenv` package:

```sh
pip install python-dotenv
```

Load the environment variables by using the `load_dotenv` function from the `dotenv` package.

**Example of usage:**
```python
from dotenv import load_dotenv
import os

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
```
## Future Enhancements
- **Proccessed files**: Enhancing the ability to handle a variety of file types.
- **Advanced Analytics**: Providing users with analytics and insights based on their interactions.
- **Web navigation**: Enabling the chatbot to browse and search web content.
- And more !
## Development Tools and Technologies

### General overview

**Programming Languages**: Python

**Frameworks**: Streamlit for Web-based Interface

**APIs**: Groq, Hugging Face 


### Available LLM models
- **Gemma Model 2 - 9B**: A highly advanced model designed for comprehensive language understanding and generation tasks.

- **Gemma Model - 7B**: An efficient model suitable for various natural language processing tasks with a balance of performance and computational efficiency.

- **LLaMA 3 - 70B**: A robust model known for its large-scale language understanding capabilities, ideal for complex queries and detailed responses.

- **LLaMA 3 - 8B**: A smaller version of the LLaMA model that provides quick and efficient responses while maintaining high accuracy.

- **Mixtral - 8x7B**: A powerful ensemble model that combines multiple models to deliver superior performance and accuracy in language tasks.

### Additionnal tools 

- **Whisper Large V3**: An advanced model optimized for understanding and generating spoken language, making it ideal for audio processing tasks.

- **Pyannote**: A powerful open-source toolkit for speaker diarization by distinguishing and recognizing multiple speakers in audio recordings.


## Contributing

Contributions are always welcome! You can fork the repository and submit pull requests for any features, bug fixes, or improvements.
