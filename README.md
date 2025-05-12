# ScholarAI SaaS

ScholarAI is a modern SaaS platform that leverages advanced AI and LLMs to help students and educators interact with academic content in new ways. Upload textbooks, lecture notes, images, or videos and get contextual, AI-powered answers and study support.

---

## 🚀 Core Functionality

- **Document Q&A:** Upload PDFs and ask questions about their content. ScholarAI retrieves relevant context and provides accurate, cited answers.
- **Image Q&A:** Upload images (e.g., diagrams, charts) or provide image URLs. Ask questions about the image content and get detailed, AI-generated explanations.
- **Video Q&A:** Upload lecture videos or provide YouTube links. ScholarAI transcribes, processes, and enables Q&A over the video content.
- **Contextual Retrieval:** Uses vector search and embeddings to find the most relevant content for your queries.
- **User Authentication:** Secure login and access control via Supabase.
- **Modern UI:** Responsive, animated frontend with beautiful backgrounds and smooth user experience.

---

## 🛠️ Tech Stack

### Frontend

- **React 18** with **TypeScript**
- **Vite** for fast development and builds
- **Tailwind CSS** for utility-first styling
- **Framer Motion** for smooth animations
- **Lucide React** for icons
- **Supabase JS** for authentication and user management

### Backend

- **FastAPI** (Python) for high-performance APIs
- **LangChain** for LLM orchestration and chaining
- **Sentence Transformers** for embeddings
- **FAISS** for vector search
- **Qdrant** and **Weaviate** (optional) for scalable vector storage
- **Python-dotenv** for environment management

---

## 🤖 LLM & AI Providers

- **Groq (Llama 70B):** Used for document and video Q&A via `langchain-groq`.
- **Google Gemini (Gemini 2.0 Flash):** Used for image Q&A via `langchain-google-genai`.
- **HuggingFace Transformers:** Used for text and image embeddings.
- **Whisper:** Used for video/audio transcription.

---

## 📦 Key Dependencies

### Frontend

- `react`, `react-dom`, `react-router-dom`
- `framer-motion`
- `tailwindcss`
- `@supabase/supabase-js`
- `lucide-react`

### Backend

- `fastapi`
- `langchain`, `langchain-huggingface`, `langchain-google-genai`, `langchain-groq`
- `sentence-transformers`
- `faiss`
- `qdrant-client`, `weaviate-client`
- `python-dotenv`
- `whisper` (for video/audio)

---

## 🏗️ Project Structure

```
/Frontend
  - src/
    - components/
    - pages/
    - App.tsx
    - main.tsx
  - package.json
  - tailwind.config.js

/fastapi-backend
  - main.py
  - routes/
    - document_qa_route.py
    - visual_qa_route.py
    - video_qa_route.py
  - Models/
  - requirements.txt
```

---

## 🔐 Authentication

- User authentication and authorization are handled via Supabase.
- API endpoints are protected using a Supabase JWT bearer middleware.

---

## 🌐 Deployment

- **Frontend:** Deployable on Vercel, Netlify, or any static hosting.
- **Backend:** Deployable on any cloud VM, Docker, or Kubernetes.
- **Docker:** Both frontend and backend have Dockerfiles for containerized deployment.

---

## 📝 API Overview

- `/document-qa/upload` — Upload a PDF document.
- `/document-qa/ask` — Ask a question about an uploaded document.
- `/image-qa/upload` — Upload an image or provide a URL.
- `/image-qa/ask` — Ask a question about an uploaded image.
- `/video-qa/upload` — Upload a video file.
- `/video-qa/process-youtube` — Process a YouTube video.
- `/video-qa/ask` — Ask a question about an uploaded or processed video.

All endpoints require authentication.

---

## 🧠 How It Works

1. **Upload** your academic material (PDF, image, or video).
2. **Ask** any question about the content.
3. **Retrieve** contextual, AI-generated answers with references to your material.
4. **Save** or export answers for later study.

---

## 📄 License

MIT License

---

## 🙏 Acknowledgements

- OpenAI, HuggingFace, Google, Groq, and the open-source community for LLMs and vector search.
- [LangChain](https://www.langchain.com/) for orchestration.
- [Supabase](https://supabase.com/) for authentication.
