const API_BASE_URL = 'http://localhost:8000';

async function apiRequest(endpoint, method = 'GET', body = null) {
    const token = localStorage.getItem('tradeiq_token');
    const headers = {
        'Content-Type': 'application/json',
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const config = {
        method,
        headers,
    };

    if (body) {
        config.body = JSON.stringify(body);
    }

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
        if (response.status === 401) {
            // Token expired or invalid, redirect to login
            localStorage.removeItem('tradeiq_token');
            window.location.href = 'login.html';
            return;
        }
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'An API error occurred');
        }
        return await response.json();
    } catch (error) {
        console.error('API Request Error:', error);
        throw error;
    }
}
