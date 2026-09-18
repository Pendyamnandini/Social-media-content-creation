# PostCraft AI 🚀

**PostCraft AI** is an all-in-one, AI-powered platform designed to revolutionize the way individuals and businesses create content for social media. 

If you've ever struggled with writer's block, spent hours trying to edit the perfect image, or found it tedious to manage posts across platforms like LinkedIn, this project is built for you. PostCraft AI acts as your personal marketing assistant, helping you ideate, create, edit, and publish engaging social media content in a fraction of the time.

## 💡 What Does This Project Do?

For anyone stumbling across this repository, here is a quick breakdown of what you can accomplish with PostCraft AI:

1. **Intelligent Text Generation**: Instead of staring at a blank page, simply give the AI a topic or a prompt. It uses powerful Large Language Models (like Mistral) to instantly draft highly engaging, platform-specific captions and articles.
2. **Advanced Image Generation & Editing**: Need a graphic to go with your post? PostCraft AI integrates with Stable Diffusion models to generate images from text. It even offers advanced features like *inpainting*, allowing you to intelligently edit out or replace specific parts of an image.
3. **Direct Social Media Publishing**: Once your content (text and image) is crafted to perfection, you can push it directly to platforms like LinkedIn straight from the dashboard. No need to switch tabs or download/upload files manually.
4. **All-in-One Dashboard**: Everything is tied together in a sleek, modern React-based web interface where you can manage your digital footprint efficiently.

---

## ✨ Key Features

- **AI Content Generation**: Generate high-quality text content and captions tailored for specific social media platforms.
- **AI Image Editing & Generation**: Create and edit images directly within the platform using stable diffusion inpainting and various Hugging Face models.
- **Social Media Integration**: Connect your social media accounts (like LinkedIn) and post directly via integrated APIs.
- **Interactive UI**: A modern, responsive React-based dashboard built with Tailwind CSS and Radix UI.
- **Robust Backend**: A fast, scalable FastAPI backend handling AI orchestration, secure API integrations, and user management.

## 🛠️ Tech Stack

### Frontend
- **Framework**: React 19 + TypeScript + Vite
- **Styling**: Tailwind CSS, Radix UI, Framer Motion
- **Routing**: React Router DOM
- **Data Visualization**: Recharts

### Backend
- **Framework**: FastAPI (Python)
- **Database**: SQLAlchemy with Alembic (Migrations), PostgreSQL / SQLite
- **Authentication**: JWT (JSON Web Tokens), Passlib
- **AI & ML**: Integration with Hugging Face Inference API (Mistral, Stable Diffusion), Scikit-Learn

---

## 🚀 Getting Started

Want to run PostCraft AI locally? Follow these steps:

### Prerequisites
- **Node.js** (v18+)
- **Python** (3.9+)
- **Hugging Face API Token** (You will need this to access the AI models)

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
   # Open .env and add your HF_TOKEN and other secrets

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

---

## 🏗️ Architecture Overview

Curious about how the code is organized? Here's a high-level view:

- **`backend/app/ai/`**: The core "brain" of the app. Contains modules for text generation, image generation pipelines, segmentation, and Natural Language Processing.
- **`backend/app/api/`**: FastAPI route handlers. This is where the frontend communicates with the backend for things like authentication, editing requests, and LinkedIn posting.
- **`frontend/src/pages/`**: The React pages that make up the user interface, including the main Dashboard, Authentication screens, and AI editing workspaces.
- **`frontend/src/components/`**: Reusable UI components (buttons, modals, forms) that keep the frontend code DRY and maintainable.

## 📄 License
MIT License
