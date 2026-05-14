**Vectorless RAG with Agno + Ollama**


A fully local Vectorless RAG (Retrieval-Augmented Generation) application built using Agno
, Ollama
, FastAPI
, and Streamlit

This project enables question answering over PDF and DOCX documents without using embeddings or vector databases. 
It uses BM25-based retrieval for fast local search and Ollama-hosted LLMs for answer generation.


**Features**
PDF and DOCX document upload
Vectorless RAG architecture
BM25-based document retrieval
Persistent BM25 index caching
Duplicate document detection using SHA256 hashing
Automatic index reuse for unchanged files
Automatic BM25 rebuild for updated files
Local LLM inference using Ollama
Streamlit-based UI
FastAPI REST APIs
Fully offline support
No OpenAI dependency
No vector database required


<img width="557" height="547" alt="image" src="https://github.com/user-attachments/assets/3979640d-5069-4b0e-8e54-a0c167a62471" />






**Tech Stack
**
| Component     | Technology  |
| ------------- | ----------- |
| Backend API   | FastAPI     |
| Frontend UI   | Streamlit   |
| LLM Framework | Agno        |
| Local LLM     | Ollama      |
| Retrieval     | BM25        |
| PDF Parsing   | PyMuPDF     |
| DOCX Parsing  | python-docx |


**Project Structure**

vectorless-rag/
│
├── backend/
│   ├── main.py
│   ├── rag_engine.py
│   ├── chunker.py
│   ├── document_loader.py
│   ├── uploads/
│   └── indexes/
│
├── frontend/
│   └── app.py
│
├── requirements.txt
└── README.md

**Installation**
1. Clone Repository
git clone <your-repo-url>cd vectorless-rag

2. Create Virtual Environment
Windows
python -m venv venvvenv\Scripts\activate
Linux/Mac
python3 -m venv venvsource venv/bin/activate

3. Install Dependencies
pip install -r requirements.txt

Install Ollama
Install Ollama locally.
Linux/Mac
curl -fsSL https://ollama.com/install.sh | sh
Windows
Download from:
Ollama Downloads

Pull Model
Recommended lightweight model:
ollama pull qwen2.5:3b

Alternative models:
ollama pull qwen3:8bollama pull mistral:7bollama pull gemma3:4b

Start Ollama
ollama serve
Verify model:
ollama list

Run Backend
cd backend uvicorn main:app
Backend runs on:
http://localhost:8000
Swagger UI:
http://localhost:8000/docs

Run Frontend
Open another terminal:
cd frontend   streamlit run app.py
Frontend runs on:
http://localhost:8501

How It Works
Document Upload
User uploads PDF/DOCX
SHA256 hash generated
Duplicate detection performed
Text extracted
Text chunked
BM25 index created
Index persisted to disk
Question Answering
User asks question
BM25 retrieves relevant chunks
Context sent to Ollama
LLM generates answer
Answer shown in UI



Persistent BM25 Cache
Indexes are stored on disk:
indexes/    sample.pdf/        metadata.json        chunks.pkl        bm25.pkl
Benefits:


No re-indexing after restart
Faster startup
Duplicate file reuse
Automatic overwrite for updated files

**Duplicate Detection
**The system uses SHA256 hashing.
ScenarioActionSame filename + same contentReuse existing BM25Same filename + updated contentRebuild BM25New filenameCreate new BM25

API Endpoints
Upload Document
POST /upload
Supported: PDF ,DOCX


Response:
{  "document_id": "sample.pdf",  "message": "Indexed successfully"}

Ask Question
POST /ask
Request:
{  "document_id": "sample.pdf",  "question": "What is the waiting period?"}
Response:
{  "answer": "The waiting period is 30 days."}

Performance Optimizations

**Implemented:**
BM25 reuse
Persistent caching
Chunk-based retrieval
Reduced context size
Top-K retrieval
In-memory indexes
Local inference
Recommended settings:
chunk_size=300overlap=50top_k=2

**Future Improvements**
Hybrid retrieval (BM25 + reranker)
OCR support for scanned PDFs
Multi-document search
Streaming responses
Authentication & RBAC
Redis caching
OpenSearch integration


Sample Screenshots

<img width="1320" height="957" alt="image" src="https://github.com/user-attachments/assets/c153e499-8095-4bbf-895b-87b65a6ac734" />



**Author
Mukesh Kumar**
