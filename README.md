# ML Document Processing Application

A full-stack machine learning application for document processing, analysis, and intelligent querying using IBM Granite SDK.

## Features

- **Document Processing**: Upload and parse PDF, TXT, CSV, and Markdown files
- **Speech Recognition**: Convert audio to text using IBM Granite ASR
- **Intelligent Querying**: RAG-powered document search and Q&A
- **Anomaly Detection**: Automated detection of unusual document patterns
- **Real-time Analytics**: Dashboard with processing metrics and alerts
- **Background Processing**: Celery-powered asynchronous tasks

## Tech Stack

### Backend
- **FastAPI** - Modern, fast web framework
- **IBM Granite SDK** - AI/ML capabilities
- **Pinecone** - Vector database for semantic search
- **Celery + Redis** - Background job processing
- **Auth0** - Authentication (JWT)
- **Docker** - Containerization

### Frontend
- **React + TypeScript** - Modern UI framework
- **Vite** - Fast build tool
- **TanStack Query** - Server state management
- **Tailwind CSS** - Utility-first styling
- **Recharts** - Data visualization

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Environment Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd ml-document-processor
```

2. Copy environment files:
```bash
cp backend/.env.example backend/.env
```

3. Update the `.env` file with your API keys:
```env
GRANITE_API_KEY=your_granite_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
AUTH0_DOMAIN=your-domain.auth0.com
# ... other configuration
```

### Running with Docker

1. Build and start all services:
```bash
docker-compose up --build
```

2. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Local Development

#### Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

#### Start Redis (for background jobs)
```bash
docker run -d -p 6379:6379 redis:7-alpine
```

#### Start Celery Worker
```bash
cd backend
celery -A app.tasks worker --loglevel=info
```

## API Endpoints

### Document Processing
- `POST /api/parse` - Upload and parse documents
- `POST /api/asr` - Convert speech to text
- `POST /api/query` - Query documents with RAG

### Analytics & Alerts
- `GET /api/alerts` - Get anomaly alerts
- `GET /api/dashboard/stats` - Get dashboard statistics

### Health & Monitoring
- `GET /health` - Health check
- `GET /` - API info

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GRANITE_API_KEY` | IBM Granite API key | Yes |
| `PINECONE_API_KEY` | Pinecone vector database key | Yes |
| `AUTH0_DOMAIN` | Auth0 domain | No (demo mode) |
| `REDIS_URL` | Redis connection URL | Yes |
| `SECRET_KEY` | JWT secret key | Yes |

### File Upload Limits
- Maximum file size: 10MB
- Supported formats: PDF, TXT, CSV, MD
- Audio formats: WAV, MP3, M4A

## Development

### Running Tests

Backend tests:
```bash
cd backend
pytest tests/ -v
```

Frontend tests:
```bash
cd frontend
npm test
```

### Code Quality

Backend linting:
```bash
cd backend
flake8 app/ --count --select=E9,F63,F7,F82 --show-source --statistics
```

Frontend linting:
```bash
cd frontend
npm run lint
```

## Deployment

### Production Build

1. Build Docker images:
```bash
docker-compose -f docker-compose.prod.yml build
```

2. Deploy with orchestration platform (Kubernetes, Docker Swarm, etc.)

### CI/CD

GitHub Actions workflow is configured for:
- Automated testing
- Docker image building
- Deployment to staging/production

## Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Frontend  │────│   Backend   │────│   Granite   │
│   (React)   │    │  (FastAPI)  │    │     AI      │
└─────────────┘    └─────────────┘    └─────────────┘
                          │
                          ├─────────────┐
                          │             │
                   ┌─────────────┐ ┌─────────────┐
                   │   Pinecone  │ │    Redis    │
                   │  (Vectors)  │ │  (Queue)    │
                   └─────────────┘ └─────────────┘
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- Create an issue on GitHub
- Check the documentation
- Review API docs at `/docs` endpoint