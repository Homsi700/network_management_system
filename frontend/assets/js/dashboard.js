class Dashboard {
    constructor() {
        this.ws = null;
        this.alertsContainer = document.getElementById('alertsContainer');
        this.setupWebSocket();
        this.setupEventListeners();
    }

    setupWebSocket() {
        const token = localStorage.getItem('token');
        if (!token) {
            window.location.href = '/';
            return;
        }

        this.ws = new WebSocket(`ws://${window.location.host}/ws?token=${token}`);
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };

        this.ws.onclose = () => {
            // Try to reconnect after 5 seconds
            setTimeout(() => this.setupWebSocket(), 5000);
        };
    }

    setupEventListeners() {
        // Setup notification click handler
        document.querySelector('.fa-bell').parentElement.addEventListener('click', () => {
            // TODO: Show notifications panel
        });

        // Setup alert close buttons
        this.alertsContainer.addEventListener('click', (e) => {
            if (e.target.closest('.fa-times')) {
                const alert = e.target.closest('.max-w-md');
                alert.classList.add('opacity-0', 'scale-95');
                setTimeout(() => alert.remove(), 300);
            }
        });
    }

    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'stats':
                this.updateStats(data.data);
                break;
            case 'alert':
                this.showAlert(data.data);
                break;
            case 'server_status':
                this.updateServerStatus(data.data);
                break;
            case 'tower_status':
                this.updateTowerStatus(data.data);
                break;
        }
    }

    updateStats(stats) {
        // Update dashboard stats
        const selectors = {
            servers: '[data-stat="servers"]',
            towers: '[data-stat="towers"]',
            users: '[data-stat="users"]',
            status: '[data-stat="status"]'
        };

        for (const [key, selector] of Object.entries(selectors)) {
            const element = document.querySelector(selector);
            if (element && stats[key] !== undefined) {
                element.textContent = stats[key];
            }
        }
    }

    showAlert({ title, message, type = 'info' }) {
        const colors = {
            info: 'blue',
            success: 'green',
            warning: 'yellow',
            error: 'red'
        };
        
        const icons = {
            info: 'info-circle',
            success: 'check-circle',
            warning: 'exclamation-triangle',
            error: 'exclamation-circle'
        };

        const color = colors[type];
        const icon = icons[type];

        const alertHTML = `
            <div class="max-w-md bg-white rounded-lg shadow-lg p-4 flex items-start border-r-4 border-${color}-500 transform transition-all hover:scale-102 opacity-0 translate-y-2">
                <div class="flex-shrink-0 w-8 h-8 bg-${color}-100 rounded-lg flex items-center justify-center ml-4">
                    <i class="fas fa-${icon} text-${color}-600"></i>
                </div>
                <div class="flex-1">
                    <h4 class="font-bold text-gray-800 mb-1">${title}</h4>
                    <p class="text-gray-600 text-sm">${message}</p>
                </div>
                <button class="text-gray-400 hover:text-gray-600 mr-2">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        const alertElement = new DOMParser().parseFromString(alertHTML, 'text/html').body.firstChild;
        this.alertsContainer.prepend(alertElement);

        // Animate in
        requestAnimationFrame(() => {
            alertElement.classList.remove('opacity-0', 'translate-y-2');
        });

        // Auto remove after 5 seconds
        setTimeout(() => {
            alertElement.classList.add('opacity-0', 'scale-95');
            setTimeout(() => alertElement.remove(), 300);
        }, 5000);
    }

    updateServerStatus(serverData) {
        const serverCard = document.querySelector(`[data-server-id="${serverData.id}"]`);
        if (!serverCard) return;

        const statusBadge = serverCard.querySelector('.status-badge');
        const statusText = serverCard.querySelector('.status-text');
        
        // Update status indicators
        if (statusBadge && statusText) {
            const { color, text } = this.getStatusDetails(serverData.status);
            statusBadge.className = `px-2 py-1 bg-${color}-100 text-${color}-600 text-sm rounded-full status-badge`;
            statusText.textContent = text;
        }

        // Update other server metrics
        const userCount = serverCard.querySelector('.user-count');
        if (userCount) {
            userCount.textContent = serverData.users;
        }
    }

    updateTowerStatus(towerData) {
        const towerCard = document.querySelector(`[data-tower-id="${towerData.id}"]`);
        if (!towerCard) return;

        // Update signal strength
        const signalStrength = towerCard.querySelector('.signal-strength');
        if (signalStrength) {
            signalStrength.textContent = `${towerData.signal_strength} dBm`;
        }

        // Update status badge
        const statusBadge = towerCard.querySelector('.status-badge');
        if (statusBadge) {
            const { color, text } = this.getStatusDetails(towerData.status);
            statusBadge.className = `px-2 py-1 bg-${color}-100 text-${color}-600 text-sm rounded-full status-badge`;
            statusBadge.textContent = text;
        }

        // Update client count
        const clientCount = towerCard.querySelector('.client-count');
        if (clientCount) {
            clientCount.textContent = towerData.clients;
        }
    }

    getStatusDetails(status) {
        const statusMap = {
            active: { color: 'green', text: 'نشط' },
            warning: { color: 'yellow', text: 'تحذير' },
            error: { color: 'red', text: 'خطأ' },
            inactive: { color: 'gray', text: 'غير نشط' }
        };

        return statusMap[status] || statusMap.inactive;
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new Dashboard();
});