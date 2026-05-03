// Configuration
// Detect if we're in Codespaces or local development
const API_BASE_URL = window.location.hostname.includes('github.dev') || window.location.hostname.includes('app.github.dev')
    ? window.location.origin  // Use same origin in Codespaces
    : 'http://localhost:8000';  // Use localhost for local dev

// State management
let currentUser = null;
let authToken = null;
let pins = [];

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    console.log('Pinterest Style Matcher initialized');
    checkAPIStatus();
    checkAuthStatus();
});

// Check if API is running
async function checkAPIStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        
        const statusElement = document.getElementById('apiStatus');
        if (data.status === 'healthy') {
            statusElement.innerHTML = '🟢 Online';
            statusElement.style.color = '#28a745';
        }
    } catch (error) {
        const statusElement = document.getElementById('apiStatus');
        statusElement.innerHTML = '🔴 Offline';
        statusElement.style.color = '#dc3545';
        console.error('API is not responding:', error);
    }
}

// Check if user is already authenticated
function checkAuthStatus() {
    // Check URL for token (from OAuth callback)
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    
    if (token) {
        // Store token
        authToken = token;
        localStorage.setItem('authToken', token);
        
        // Clean URL
        window.history.replaceState({}, document.title, window.location.pathname);
        
        // Show authenticated view
        showDashboard();
    } else {
        // Check if token exists in localStorage
        const storedToken = localStorage.getItem('authToken');
        if (storedToken) {
            authToken = storedToken;
            showDashboard();
        } else {
            showLanding();
        }
    }
}

// Login with Pinterest
function loginWithPinterest() {
    console.log('Initiating Pinterest OAuth...');
    showLoading();
    // Redirect to Pinterest OAuth
    window.location.href = `${API_BASE_URL}/auth/pinterest/login`;
}

// Logout
function logout() {
    localStorage.removeItem('authToken');
    authToken = null;
    currentUser = null;
    pins = [];
    showLanding();
}

// Show/Hide sections
function showLanding() {
    hideAllSections();
    document.getElementById('landingSection').style.display = 'block';
}

function showLoading() {
    hideAllSections();
    document.getElementById('loadingSection').style.display = 'block';
}

function showDashboard() {
    hideAllSections();
    document.getElementById('dashboardSection').style.display = 'block';
    document.getElementById('userInfo').style.display = 'flex';
    
    // Load user data
    loadUserPins();
}

function showError(message) {
    hideAllSections();
    document.getElementById('errorSection').style.display = 'block';
    document.getElementById('errorText').textContent = message;
}

function hideAllSections() {
    document.getElementById('landingSection').style.display = 'none';
    document.getElementById('loadingSection').style.display = 'none';
    document.getElementById('dashboardSection').style.display = 'none';
    document.getElementById('errorSection').style.display = 'none';
}

// Load user's Pinterest pins (mock for now - needs backend endpoint)
async function loadUserPins() {
    try {
        // TODO: Replace with actual API call when endpoint is ready
        // For now, show placeholder message
        
        document.getElementById('username').textContent = 'Pinterest User';
        document.getElementById('pinsCount').textContent = '0';
        document.getElementById('boardsCount').textContent = '0';
        
        // Show empty state
        document.getElementById('emptyState').classList.add('show');
        document.getElementById('pinsGallery').innerHTML = '';
        
        // Uncomment when backend endpoint is ready:
        /*
        const response = await fetch(`${API_BASE_URL}/pins`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to load pins');
        }
        
        const data = await response.json();
        pins = data.pins || [];
        
        renderPins(pins);
        updateStats(data.stats);
        */
        
    } catch (error) {
        console.error('Error loading pins:', error);
        showError('Failed to load your Pinterest pins. Please try again.');
    }
}

// Render pins in gallery
function renderPins(pinsData) {
    const gallery = document.getElementById('pinsGallery');
    const emptyState = document.getElementById('emptyState');
    
    if (!pinsData || pinsData.length === 0) {
        emptyState.classList.add('show');
        gallery.innerHTML = '';
        return;
    }
    
    emptyState.classList.remove('show');
    
    gallery.innerHTML = pinsData.map(pin => `
        <div class="pin-card" onclick="openPinModal('${pin.id}')">
            <img src="${pin.image_url}" alt="${pin.title || 'Pin'}" class="pin-image">
            <div class="pin-info">
                <div class="pin-title">${pin.title || 'Untitled Pin'}</div>
                <div class="pin-board">${pin.board_name || 'Board'}</div>
            </div>
        </div>
    `).join('');
}

// Update dashboard stats
function updateStats(stats) {
    document.getElementById('pinsCount').textContent = stats.pins_count || 0;
    document.getElementById('boardsCount').textContent = stats.boards_count || 0;
}

// Open pin detail modal
function openPinModal(pinId) {
    const pin = pins.find(p => p.id === pinId);
    if (!pin) return;
    
    document.getElementById('modalImage').src = pin.image_url;
    document.getElementById('modalTitle').textContent = pin.title || 'Untitled Pin';
    document.getElementById('modalDescription').textContent = pin.description || 'No description available.';
    document.getElementById('pinModal').style.display = 'flex';
}

// Close modal
function closeModal() {
    document.getElementById('pinModal').style.display = 'none';
}

// Shop similar (placeholder)
function shopSimilar() {
    alert('🚀 Visual AI matching coming soon! This will find products similar to your pin.');
}

// Close modal on background click
window.onclick = function(event) {
    const modal = document.getElementById('pinModal');
    if (event.target === modal) {
        closeModal();
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeModal();
    }
});
