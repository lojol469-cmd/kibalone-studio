// API Client for Kibalone Studio
const API_BASE_URL = 'http://localhost:8080';

class APIClient {
    async request(endpoint, options = {}) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            return { error: true, message: error.message };
        }
    }

    // Chat API
    async sendMessage(message, context = {}) {
        return this.request('/api/chat/message', {
            method: 'POST',
            body: JSON.stringify({ message, context })
        });
    }

    async analyzePrompt(prompt) {
        return this.request('/api/chat/analyze', {
            method: 'POST',
            body: JSON.stringify({ prompt })
        });
    }

    // MiDaS API
    async createSession() {
        return this.request('/api/midas/create_session', { method: 'POST' });
    }

    async uploadImage(sessionId, imageFile) {
        const formData = new FormData();
        formData.append('image', imageFile);
        formData.append('session_id', sessionId);

        try {
            const response = await fetch(`${API_BASE_URL}/api/midas/upload_image`, {
                method: 'POST',
                body: formData
            });
            return await response.json();
        } catch (error) {
            return { error: true, message: error.message };
        }
    }

    async reconstruct(sessionId) {
        return this.request('/api/midas/reconstruct', {
            method: 'POST',
            body: JSON.stringify({ session_id: sessionId })
        });
    }

    // Health check
    async healthCheck() {
        return this.request('/health');
    }
}

const api = new APIClient();
