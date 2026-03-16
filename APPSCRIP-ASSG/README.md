# TradeIQ India: Trade Opportunities Intelligence Platform

TradeIQ India is a full-stack web application that provides AI-powered trade opportunity analysis for various sectors in the Indian market. It combines a robust FastAPI backend with a dynamic, pure HTML/CSS/JS frontend to deliver real-time insights.

## Features

- **Real-time Data Scraping**: Gathers live data from multiple sources including DuckDuckGo, Google News, and government websites.
- **AI-Powered Analysis**: Uses Google's Gemini AI to generate comprehensive trade reports.
- **Interactive Dashboard**: A modern, responsive UI for searching sectors and viewing session statistics.
- **Secure Authentication**: JWT-based authentication with a demo user.
- **Rate Limiting**: Protects the API from abuse.
- **In-Memory Caching**: Caches reports for faster responses.

## Architecture

```
+----------------+      +-----------------+      +----------------+
|   Frontend     |----->|   FastAPI       |----->|   Web Scraper  |
| (HTML/CSS/JS)  |      |   Backend       |      | (httpx, bs4)   |
+----------------+      +-------+---------+      +-------+--------+
      ^                       |
      |                       v
      |               +-------+--------+
      +---------------|   Gemini AI      |
                      |   (Analysis)   |
                      +----------------+
```

## Prerequisites

- Python 3.11+
- A Google Gemini API Key

To get a free Gemini API key, visit [aistudio.google.com](https://aistudio.google.com).

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/trade-opportunities-platform.git
    cd trade-opportunities-platform
    ```

2.  **Set up the backend:**
    ```bash
    cd backend
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3.  **Configure environment variables:**
    Create a `.env` file in the `backend` directory by copying the example:
    ```bash
    cp .env.example .env
    ```
    Open the `.env` file and add your `GEMINI_API_KEY` and a `SECRET_KEY`.

4.  **Run the backend server:**
    ```bash
    uvicorn main:app --reload
    ```
    The backend will be running at `http://localhost:8000`.

5.  **Set up the frontend:**
    Open a new terminal and navigate to the `frontend` directory:
    ```bash
    cd ../frontend
    python -m http.server 3000
    ```
    Alternatively, you can use the "Live Server" extension in VS Code.

6.  **Access the application:**
    Open your browser and go to `http://localhost:3000`. You will be redirected to the login page.

## API Endpoints

### Authentication

-   **`POST /auth/token`**: Login to get an access token.
    ```bash
    curl -X POST http://localhost:8000/auth/token -H "Content-Type: application/json" -d '{"username": "demo", "password": "demo123"}'
    ```

### Analysis

-   **`GET /analyze/{sector}`**: Get a trade analysis report for a sector.
    ```bash
    curl -X GET http://localhost:8000/analyze/pharmaceuticals -H "Authorization: Bearer <YOUR_TOKEN>"
    ```

### Session

-   **`GET /session/stats`**: Get statistics for the current session.
-   **`GET /session/history`**: Get the query history for the current session.

## Troubleshooting

-   **CORS Errors**: Ensure the `CORS_ORIGINS` in `backend/config.py` includes the URL of your frontend.
-   **401 Unauthorized**: Make sure you are sending the correct JWT token in the `Authorization` header.
-   **500 Internal Server Error**: Check the backend logs for tracebacks. This could be due to a missing API key or an issue with one of the scraped websites.
