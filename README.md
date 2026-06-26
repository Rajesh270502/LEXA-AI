# LEXA-AI: AI Legal Contract Intelligence Platform

An AI-powered Legal Contract Intelligence Platform that enables users to upload legal contracts, perform semantic question answering, and identify potential risks using Retrieval-Augmented Generation (RAG) with Large Language Models.

---
 
## Overview

LEXA-AI helps users analyze legal contracts without reading lengthy documents manually.

The platform:

- Uploads legal contracts (PDF)
- Extracts and chunks document text
- Generates embeddings
- Stores embeddings in Qdrant Vector Database
- Uses an LLM to answer legal questions
- Highlights important contract clauses and potential risks

---

## Features

- Secure User Authentication (JWT)
- PDF Contract Upload
- Automatic Text Extraction
- Semantic Search using Vector Embeddings
- Retrieval-Augmented Generation (RAG)
- AI-powered Legal Question Answering
- Risk Assessment of Contract Clauses
- Interactive Streamlit Frontend
- FastAPI Backend
- Qdrant Vector Database

---

## Tech Stack

### Backend

- FastAPI
- Python
- SQLAlchemy
- JWT Authentication
- Pydantic

### AI / LLM

- Google Gemini API
- Sentence Transformers
- Retrieval-Augmented Generation (RAG)

### Vector Database

- Qdrant

### Frontend

- Streamlit

### Database

- SQLite

---

## Project Structure

```
LEXA-AI/
│
├── backend/
│   ├── app/
│   │   ├── auth.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── utils.py
│   │   └── main.py
│   │
│   ├── tests/
│   ├── test_embedding.py
│   ├── test_models.py
│   └── test_openai.py
│
├── frontend/
│   └── app.py
│
├── requirements.txt
└── README.md
```

---

## System Workflow

```
User
   │
   ▼
Upload Contract (PDF)
   │
   ▼
Text Extraction
   │
   ▼
Chunking
   │
   ▼
Embedding Generation
   │
   ▼
Qdrant Vector Database
   │
   ▼
Relevant Context Retrieval
   │
   ▼
Google Gemini LLM
   │
   ▼
Answer + Risk Analysis
```

---

## Application Outputs

### Home Page

> <img width="940" height="419" alt="image" src="https://github.com/user-attachments/assets/1d9a6e3f-db61-4da4-950d-5f06bd2fe67d" />


### Upload Contract

> <img width="940" height="415" alt="image" src="https://github.com/user-attachments/assets/998272a8-54ff-40a9-827c-95c32cc5653b" />


### Semantic Query

> <img width="940" height="420" alt="image" src="https://github.com/user-attachments/assets/299b749e-3cba-43c2-90dd-bbad30952045" />


### Risk Assessment

> <img width="940" height="418" alt="image" src="https://github.com/user-attachments/assets/16b08940-b7ea-4bbb-8767-0c34bebe567d" />


---


## Future Improvements

- Multi-document Retrieval
- OCR Support
- Contract Comparison
- Citation-based Responses
- Docker Deployment
- PostgreSQL Support
- Cloud Deployment (AWS/Azure/GCP)
- Role-Based Access Control

---

## Author

**Rajesh Puligeti**

B.Tech Graduate | Machine Learning | Deep Learning | Generative AI | RAG | FastAPI | Vector Databases

LinkedIn:
www.linkedin.com/in/rajesh-puligeti-5a9228286

GitHub:
https://github.com/Rajesh270502

---

## If you found this project useful

Give this repository a to support future development.
