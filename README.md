# TradeIQ India: Trade Opportunities Intelligence Platform

TradeIQ India is a full-stack web application designed to identify trade opportunities in Indian markets using live web scraping and AI-powered analysis (Google Gemini).

## 📁 Project Structure

The project is organized in the `APPSCRIP-ASSG/` directory:

- `backend/`: FastAPI server, multi-source web scraper, and Gemini AI integration.
- `frontend/`: Responsive dashboard and report UI built with pure HTML, CSS, and Vanilla JS.

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Google Gemini API Key (Get it at [aistudio.google.com](https://aistudio.google.com))

### 1. Backend Setup
1. Navigate to the backend folder:
   ```bash
   cd APPSCRIP-ASSG/backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment:
   - Copy `.env.example` to `.env`.
   - Add your `GEMINI_API_KEY`.
5. Run the server:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

### 2. Frontend Setup
1. Open a new terminal and navigate to the frontend folder:
   ```bash
   cd APPSCRIP-ASSG/frontend
   ```
2. Serve the files (using Python's built-in server or Live Server):
   ```bash
   python3 -m http.server 3000
   ```
3. Open [http://localhost:3000](http://localhost:3000) in your browser.

## 🔑 Login Credentials (Demo)
- **Username**: `demo`
- **Password**: `demo123`

## ✨ Features
- **Live Scraper**: Collects data from DuckDuckGo, Google News, Economic Times, Wikipedia, and Data.gov.in.
- **AI Analysis**: Generates professional trade reports using `gemini-flash-latest`.
- **Modern UI**: Bloomberg-style dark theme with interactive charts and real-time logs.
- **Security**: JWT Authentication and API rate limiting.
