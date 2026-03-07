# 🤖 Agentic Social Media Manager

A FastAPI-powered backend that automates social media post creation using AI — from generating captions and images to scheduling and managing posts across platforms.

🌐 **Live Demo:** [agentic-social-media-manager.vercel.app](https://agentic-social-media-manager.vercel.app)

---

## ✨ Features

- **AI-Generated Captions** — Automatically generate engaging post captions using large language models
- **AI Image Generation** — Create visuals for posts via AI image generation APIs
- **Post Management** — Create, view, update, and delete social media posts
- **Email Notifications** — Integrated with Brevo (formerly Sendinblue) for email workflows
- **REST API** — Clean, documented FastAPI endpoints with automatic Swagger UI
- **Vercel Deployment** — Ready to deploy serverlessly on Vercel

---

## 🗂️ Project Structure

```
Agentic-social-media-manager/
├── app/                  # Core application (routes, models, services)
├── run.py                # Application entry point
├── requirements.txt      # Python dependencies
├── vercel.json           # Vercel deployment configuration
├── test.py               # Test scripts
├── test2.py
└── testBrevo.py          # Brevo email integration tests
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- pip

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/HareemShaikh01/Agentic-social-media-manager.git
   cd Agentic-social-media-manager
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate        # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   Create a `.env` file in the root directory and add your API keys:

   ```env
   OPENAI_API_KEY=your_openai_api_key
   BREVO_API_KEY=your_brevo_api_key
   # Add any other required keys
   ```

5. **Run the application**

   ```bash
   python run.py
   ```

   The API will be available at `http://localhost:8000`. Visit `http://localhost:8000/docs` for the interactive Swagger UI.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Language | Python |
| AI / LLM | OpenAI API |
| Email | Brevo (Sendinblue) |
| Deployment | Vercel |

---

## 📡 API Endpoints

Once running, the full API reference is auto-generated and available at:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

---

## ☁️ Deployment

This project is configured for deployment on **Vercel** via `vercel.json`.

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel
```

---

## 🧪 Testing

```bash
python test.py
python test2.py
python testBrevo.py   # Test Brevo email integration
```

---

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## 📄 License

This project is open source. See the repository for details.

---

*Built with ❤️ by [HareemShaikh01](https://github.com/HareemShaikh01)*
