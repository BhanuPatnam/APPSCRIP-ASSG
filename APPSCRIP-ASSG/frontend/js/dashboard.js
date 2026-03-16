document.addEventListener('DOMContentLoaded', () => {
    if (!localStorage.getItem('tradeiq_token')) {
        window.location.href = 'login.html';
        return;
    }

    const logoutButton = document.getElementById('logout-button');
    const searchButton = document.getElementById('search-button');
    const searchInput = document.getElementById('sector-search-input');
    const loader = document.getElementById('loader');
    const requestLog = document.getElementById('request-log');

    logoutButton.addEventListener('click', () => {
        localStorage.removeItem('tradeiq_token');
        window.location.href = 'login.html';
    });

    searchButton.addEventListener('click', performSearch);
    searchInput.addEventListener('keyup', (e) => {
        if (e.key === 'Enter') performSearch();
    });

    async function performSearch() {
        const sector = searchInput.value.trim();
        if (!sector) {
            showToast('Please enter a sector name.', 'error');
            return;
        }

        loader.classList.remove('hidden');
        logRequest(`Analyzing "${sector}"...`);

        try {
            const report = await apiRequest(`/analyze/${sector}`);
            // Store report and redirect to report page
            sessionStorage.setItem('current_report', JSON.stringify(report));
            
            // Immediately update stats before redirecting to ensure the search is recorded
            await updateSessionStats();
            
            window.location.href = 'report.html';
        } catch (error) {
            showToast(error.message, 'error');
            logRequest(`Failed: ${error.message}`);
        } finally {
            loader.classList.add('hidden');
        }
    }

    function logRequest(message) {
        const li = document.createElement('li');
        li.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
        requestLog.prepend(li);
    }

    // Sector button clicks
    document.querySelectorAll('.sector-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            // Extract text only, excluding icon
            searchInput.value = btn.innerText.trim();
            performSearch();
        });
    });

    async function updateSessionStats() {
        try {
            const stats = await apiRequest('/session/stats');
            const statsDiv = document.getElementById('session-stats');
            if (statsDiv) {
                statsDiv.innerHTML = `
                    <div class="stat-item"><span>Requests</span><span>${stats.requests_made}</span></div>
                    <div class="stat-item"><span>Sectors</span><span>${stats.sectors_queried.length}</span></div>
                    <div class="stat-item"><span>Cache Size</span><span>${stats.cache_stats.size}</span></div>
                    <div class="stat-item"><span>Rate Hits</span><span>${stats.rate_limit_hits}</span></div>
                `;
            }

            // Update recent searches
            const recentUl = document.getElementById('recent-searches');
            if (recentUl) {
                recentUl.innerHTML = '';
                // Only show unique sectors in history
                const uniqueSectors = [...new Set(stats.sectors_queried)];
                uniqueSectors.slice(-5).reverse().forEach(sector => {
                    const li = document.createElement('li');
                    li.innerHTML = `<i class="fas fa-search"></i> ${sector}`;
                    li.style.cursor = 'pointer';
                    li.addEventListener('click', () => {
                        searchInput.value = sector;
                        performSearch();
                    });
                    recentUl.appendChild(li);
                });
            }

            // Update rate limit counter
            const rateLimitCounter = document.getElementById('rate-limit-counter');
            if (rateLimitCounter) {
                // If the backend doesn't provide remaining directly, we show the limit
                rateLimitCounter.textContent = stats.rate_limit_remaining || '5';
            }
        } catch (error) {
            console.error('Failed to update stats:', error);
        }
    }

    updateSessionStats();
    setInterval(updateSessionStats, 10000);
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
