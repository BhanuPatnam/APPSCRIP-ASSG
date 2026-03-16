document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const loginButton = document.getElementById('login-button');

    // Redirect if already logged in
    if (localStorage.getItem('tradeiq_token')) {
        window.location.href = 'dashboard.html';
    }

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        loginButton.textContent = 'Logging in...';
        loginButton.disabled = true;

        try {
            const data = await apiRequest('/auth/token', 'POST', {
                username: usernameInput.value,
                password: passwordInput.value,
            });

            if (data.access_token) {
                localStorage.setItem('tradeiq_token', data.access_token);
                showToast('Login successful! Redirecting...', 'success');
                setTimeout(() => {
                    window.location.href = 'dashboard.html';
                }, 1500);
            } else {
                throw new Error('Login failed, no token received.');
            }
        } catch (error) {
            showToast(error.message || 'Invalid credentials', 'error');
            loginButton.textContent = 'Login';
            loginButton.disabled = false;
        }
    });
});

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
}
