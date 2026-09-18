# PostCraft AI

An AI-powered platform designed to automate and enhance social media content creation. The application helps users generate professional posts, edit images, and publish content seamlessly (e.g., to LinkedIn), utilizing the power of modern AI and machine learning tools.

## Features

- **AI Content Generation**: Generate high-quality text content and captions for social media platforms.
- **AI Image Editing & Generation**: Create and edit images directly within the platform using stable diffusion inpainting and various AI models.
- **Social Media Integration**: Connect your social media accounts (like LinkedIn) and post directly from the dashboard.
- **Interactive UI**: A modern, responsive React-based dashboard with a sleek design.
- **Robust Backend**: A FastAPI backend handling AI orchestration, API integrations, and user management.

## Tech Stack

### Frontend
- **Framework**: React 19 + TypeScript + Vite
- **Styling**: Tailwind CSS, Radix UI, Framer Motion
- **Routing**: React Router DOM
- **Data Visualization**: Recharts

### Backend
- **Framework**: FastAPI (Python)
- **Database**: SQLAlchemy with Alembic (Migrations), PostgreSQL / SQLite
- **Authentication**: JWT, Passlib
- **AI & ML**: Integration with Hugging Face (Mistral, Stable Diffusion), Scikit-Learn

## Getting Started

### Prerequisites
- Node.js (v18+)
- Python (3.9+)
- Hugging Face API Token (for AI models)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Pendyamnandini/Social-media-content-creation.git
   cd Social-media-content-creation
   ```

2. **Setup Backend:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   
   # Set up your environment variables
   cp .env.example .env
   # Add your HF_TOKEN and other secrets to the .env file

   # Run database migrations and start server
   alembic upgrade head
   uvicorn app.main:app --reload
   ```

3. **Setup Frontend:**
   ```bash
   cd ../frontend
   npm install
   npm run dev
   ```

4. **Access the application:**
   Open your browser and navigate to `http://localhost:5173`.

## Architecture Overview

- `backend/app/ai`: Contains modules for text generation, image pipelines, segmentation, and NLP processing.
- `backend/app/api`: FastAPI route handlers for content, auth, editing, and LinkedIn integration.
- `frontend/src/pages`: React pages including Dashboard, Authentication, and AI editing features.
- `frontend/src/components`: Reusable UI components.

## License
MIT License
