# Intelligent Code Documentation Generator

A cutting-edge RAG-based system that automatically generates comprehensive, context-aware documentation for entire codebases.

## Project Overview

The Intelligent Code Documentation Generator is a full-stack application that analyzes code structure, relationships, and patterns using an advanced RAG (Retrieval-Augmented Generation) pipeline to generate interactive, intelligent documentation with contextual examples and explanations.

## Features

- **Repository Ingestion**: Support for GitHub repositories and ZIP file uploads
- **Multi-level Code Analysis**: Function → class → module → project
- **Semantic Code Understanding**: Analyzes code relationships and patterns
- **Context-aware Documentation**: Generates comprehensive documentation
- **Interactive UI**: Modern, responsive interface for exploring documentation

## Tech Stack

### Backend
- **Framework**: FastAPI with Pydantic
- **Database**: ChromaDB for vector storage
- **AI/ML**: Mock embeddings (can be replaced with CodeBERT/GraphCodeBERT)
- **Code Analysis**: Python AST parser

### Frontend
- **Framework**: React with TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Hooks
- **Routing**: React Router
- **API Integration**: Axios

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints/
│   │   │   │   └── repository.py
│   │   │   └── api.py
│   │   ├── core/
│   │   │   └── config.py
│   │   ├── models/
│   │   │   └── repository.py
│   │   ├── services/
│   │   │   ├── code_parser_service.py
│   │   │   ├── documentation_service.py
│   │   │   ├── embedding_service.py
│   │   │   ├── repository_service.py
│   │   │   └── vector_store_service.py
│   │   └── main.py
│   └── requirements.txt
└── frontend/
    ├── public/
    ├── src/
    │   ├── components/
    │   │   ├── Header.tsx
    │   │   ├── RepositoryInput.tsx
    │   │   └── RepositoryStatus.tsx
    │   ├── App.tsx
    │   ├── index.tsx
    │   └── index.css
    ├── package.json
    ├── tsconfig.json
    ├── tailwind.config.js
    └── postcss.config.js
```

## Setup Instructions

### Using the Provided Scripts

The easiest way to run the application is to use the provided scripts:

1. Start the backend server:
   ```
   ./start_backend.sh
   ```

2. In a new terminal window, start the frontend server:
   ```
   ./start_frontend.sh
   ```

The backend API will be available at http://localhost:8000, and the frontend will be available at http://localhost:3000.

### Manual Setup

#### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the server:
   ```
   uvicorn app.main:app --reload
   ```

The backend API will be available at http://localhost:8000. You can access the API documentation at http://localhost:8000/docs.

#### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Run the development server:
   ```
   npm start
   ```

The frontend will be available at http://localhost:3000.

## Usage

1. Open the application in your browser at http://localhost:3000
2. Choose between providing a GitHub repository URL or uploading a ZIP file
3. Submit the repository for processing
4. Monitor the processing status
5. View and download the generated documentation when complete

## API Endpoints

- `POST /api/v1/repositories`: Create a new repository from GitHub URL
- `POST /api/v1/repositories/upload`: Upload a repository as a ZIP file
- `GET /api/v1/repositories/{repo_id}/status`: Check the status of a repository
- `GET /api/v1/repositories/{repo_id}/documentation`: Get the generated documentation
- `GET /api/v1/repositories/{repo_id}/documentation/download`: Download the documentation

## Future Enhancements

- Multi-language support (JavaScript, TypeScript, Java, etc.)
- Integration with real embedding models (CodeBERT, GraphCodeBERT)
- Relationship visualization with D3.js
- Local LLM integration with Ollama
- User authentication and project management

## License

MIT
