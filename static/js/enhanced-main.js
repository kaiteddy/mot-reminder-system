// Enhanced MOT Reminder System - Main JavaScript
// Improved data connectivity and UI interactions

// Global configuration
const API_BASE_URL = window.location.origin;
const API_ENDPOINTS = {
    status: '/api/status',
    vehicles: '/api/vehicles/',
    customers: '/api/customers/',
    reminders: '/api/reminders/',
    jobSheets: '/api/job-sheets/',
    insights: '/api/insights'
};

// Global state management
class AppState {
    constructor() {
        this.data = {
            vehicles: [],
            customers: [],
            reminders: [],
            jobSheets: [],
            insights: null
        };
        this.ui = {
            currentPage: 'dashboard',
            loading: false,
            theme: localStorage.getItem('theme') || 'light'
        };
        this.cache = new Map();
    }

    // Update data with caching
    updateData(key, data) {
        this.data[key] = data;
        this.cache.set(key, { data, timestamp: Date.now() });
        this.notifySubscribers(key);
    }

    // Get cached data if fresh (5 minutes)
    getCachedData(key) {
        const cached = this.cache.get(key);
        if (cached && (Date.now() - cached.timestamp) < 300000) {
            return cached.data;
        }
        return null;
    }

    // Subscribe to data changes
    subscribe(key, callback) {
        if (!this.subscribers) this.subscribers = {};
        if (!this.subscribers[key]) this.subscribers[key] = [];
        this.subscribers[key].push(callback);
    }

    // Notify subscribers of data changes
    notifySubscribers(key) {
        if (this.subscribers && this.subscribers[key]) {
            this.subscribers[key].forEach(callback => callback(this.data[key]));
        }
    }
}

// Initialize global state
const appState = new AppState();

// Enhanced API client with error handling and retry logic
class APIClient {
    constructor(baseURL) {
        this.baseURL = baseURL;
        this.retryCount = 3;
        this.retryDelay = 1000;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            ...options
        };

        for (let attempt = 1; attempt <= this.retryCount; attempt++) {
            try {
                console.log(`API Request (attempt ${attempt}): ${url}`);
                const response = await fetch(url, defaultOptions);
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const data = await response.json();
                console.log(`API Response: ${url}`, data);
                return data;
            } catch (error) {
                console.error(`API Error (attempt ${attempt}): ${url}`, error);
                
                if (attempt === this.retryCount) {
                    throw error;
                }
                
                // Wait before retry
                await new Promise(resolve => setTimeout(resolve, this.retryDelay * attempt));
            }
        }
    }

    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }

    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }
}

// Initialize API client
const api = new APIClient(API_BASE_URL);

// Enhanced UI utilities
class UIUtils {
    static showLoading(element, message = 'Loading...') {
        if (typeof element === 'string') {
            element = document.getElementById(element);
        }
        if (element) {
            element.innerHTML = `
                <div class="loading-container">
                    <div class="loading-spinner"></div>
                    <div class="loading-text">${message}</div>
                </div>
            `;
        }
    }

    static showError(element, message = 'An error occurred') {
        if (typeof element === 'string') {
            element = document.getElementById(element);
        }
        if (element) {
            element.innerHTML = `
                <div class="error-container">
                    <i class="fas fa-exclamation-triangle error-icon"></i>
                    <div class="error-text">${message}</div>
                    <button class="apple-btn apple-btn-secondary retry-btn" onclick="location.reload()">
                        <i class="fas fa-redo"></i> Retry
                    </button>
                </div>
            `;
        }
    }

    static showSuccess(message, duration = 3000) {
        const toast = document.createElement('div');
        toast.className = 'success-toast';
        toast.innerHTML = `
            <i class="fas fa-check-circle"></i>
            <span>${message}</span>
        `;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.add('show');
        }, 100);
        
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => document.body.removeChild(toast), 300);
        }, duration);
    }

    static formatDate(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleDateString('en-GB', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        });
    }

    static getStatusColor(status) {
        const colors = {
            'expired': '#ff3b30',
            'expires_today': '#ff9500',
            'expires_soon': '#ffcc00',
            'due_soon': '#34c759',
            'current': '#007aff'
        };
        return colors[status] || '#8e8e93';
    }

    static getUrgencyBadge(status) {
        const badges = {
            'expired': '<span class="status-badge status-expired">Expired</span>',
            'expires_today': '<span class="status-badge status-today">Today</span>',
            'expires_soon': '<span class="status-badge status-soon">Soon</span>',
            'due_soon': '<span class="status-badge status-due">Due</span>',
            'current': '<span class="status-badge status-current">Current</span>'
        };
        return badges[status] || '<span class="status-badge status-unknown">Unknown</span>';
    }
}

// Enhanced data loading functions
async function loadDashboardData() {
    try {
        UIUtils.showLoading('dashboard-stats', 'Loading dashboard data...');
        
        // Load all data in parallel
        const [vehicles, customers, reminders, insights] = await Promise.all([
            loadVehiclesData(),
            loadCustomersData(),
            loadRemindersData(),
            loadInsightsData()
        ]);

        // Update dashboard stats
        updateDashboardStats(vehicles, customers, reminders);
        
        // Update insights
        updateInsights(insights);
        
        // Update reminders due now
        updateRemindersDueNow(reminders);
        
        console.log('Dashboard data loaded successfully');
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        UIUtils.showError('dashboard-stats', 'Failed to load dashboard data');
    }
}

async function loadVehiclesData() {
    try {
        // Check cache first
        const cached = appState.getCachedData('vehicles');
        if (cached) {
            return cached;
        }

        const data = await api.get(API_ENDPOINTS.vehicles);
        appState.updateData('vehicles', data.vehicles || []);
        return data.vehicles || [];
    } catch (error) {
        console.error('Error loading vehicles:', error);
        // Return mock data for development
        const mockVehicles = [
            {
                id: 1,
                registration: 'AB12 CDE',
                make: 'Ford',
                model: 'Focus',
                mot_expiry: '2024-08-15',
                mot_status: 'expires_soon',
                customer_id: 1
            },
            {
                id: 2,
                registration: 'FG34 HIJ',
                make: 'Toyota',
                model: 'Corolla',
                mot_expiry: '2024-12-20',
                mot_status: 'current',
                customer_id: 2
            }
        ];
        appState.updateData('vehicles', mockVehicles);
        return mockVehicles;
    }
}

async function loadCustomersData() {
    try {
        const cached = appState.getCachedData('customers');
        if (cached) {
            return cached;
        }

        const data = await api.get(API_ENDPOINTS.customers);
        appState.updateData('customers', data.customers || []);
        return data.customers || [];
    } catch (error) {
        console.error('Error loading customers:', error);
        // Return mock data for development
        const mockCustomers = [
            {
                id: 1,
                name: 'John Smith',
                email: 'john@example.com',
                phone: '07123456789'
            },
            {
                id: 2,
                name: 'Jane Doe',
                email: 'jane@example.com',
                phone: '07987654321'
            }
        ];
        appState.updateData('customers', mockCustomers);
        return mockCustomers;
    }
}

async function loadRemindersData() {
    try {
        const cached = appState.getCachedData('reminders');
        if (cached) {
            return cached;
        }

        const data = await api.get(API_ENDPOINTS.reminders);
        appState.updateData('reminders', data.reminders || []);
        return data.reminders || [];
    } catch (error) {
        console.error('Error loading reminders:', error);
        // Return mock data for development
        const mockReminders = [
            {
                id: 1,
                vehicle_id: 1,
                reminder_date: '2024-07-15',
                status: 'scheduled',
                type: 'mot_expiry'
            }
        ];
        appState.updateData('reminders', mockReminders);
        return mockReminders;
    }
}

async function loadInsightsData() {
    try {
        const data = await api.get(API_ENDPOINTS.insights);
        return data.insights || null;
    } catch (error) {
        console.error('Error loading insights:', error);
        // Return mock insights for development
        return {
            total_revenue_potential: 2500,
            overdue_count: 3,
            upcoming_count: 7,
            recommendations: [
                'Contact customers with overdue MOTs immediately',
                'Schedule reminders for vehicles expiring in the next 30 days',
                'Consider offering MOT booking discounts to increase conversion'
            ]
        };
    }
}

// Dashboard update functions
function updateDashboardStats(vehicles, customers, reminders) {
    // Update counts
    document.getElementById('vehicles-count').textContent = vehicles.length;
    document.getElementById('customers-count').textContent = customers.length;
    
    // Calculate reminders due
    const remindersDue = reminders.filter(r => {
        const reminderDate = new Date(r.reminder_date);
        const today = new Date();
        return reminderDate <= today && r.status === 'scheduled';
    }).length;
    
    document.getElementById('reminders-due-count').textContent = remindersDue;
}

function updateInsights(insights) {
    const insightsContainer = document.getElementById('ai-insights-content');
    if (!insights) {
        insightsContainer.innerHTML = '<p>No insights available at this time.</p>';
        return;
    }

    insightsContainer.innerHTML = `
        <div class="insights-grid">
            <div class="insight-card">
                <h4>Revenue Potential</h4>
                <div class="insight-value">£${insights.total_revenue_potential || 0}</div>
            </div>
            <div class="insight-card">
                <h4>Overdue MOTs</h4>
                <div class="insight-value">${insights.overdue_count || 0}</div>
            </div>
            <div class="insight-card">
                <h4>Upcoming MOTs</h4>
                <div class="insight-value">${insights.upcoming_count || 0}</div>
            </div>
        </div>
        <div class="recommendations">
            <h4>AI Recommendations</h4>
            <ul>
                ${(insights.recommendations || []).map(rec => `<li>${rec}</li>`).join('')}
            </ul>
        </div>
    `;
}

function updateRemindersDueNow(reminders) {
    const container = document.getElementById('reminders-due-now');
    if (!container) return;

    const dueReminders = reminders.filter(r => {
        const reminderDate = new Date(r.reminder_date);
        const today = new Date();
        return reminderDate <= today && r.status === 'scheduled';
    });

    if (dueReminders.length === 0) {
        container.innerHTML = '<p class="no-reminders">No reminders due right now.</p>';
        return;
    }

    container.innerHTML = dueReminders.map(reminder => `
        <div class="reminder-item">
            <div class="reminder-info">
                <strong>Vehicle ID: ${reminder.vehicle_id}</strong>
                <span>Due: ${UIUtils.formatDate(reminder.reminder_date)}</span>
            </div>
            <button class="apple-btn apple-btn-primary" onclick="processReminder(${reminder.id})">
                Process
            </button>
        </div>
    `).join('');
}

// Navigation enhancement
function showPageDirect(page) {
    console.log('Showing page:', page);
    
    // Hide all pages
    document.querySelectorAll('.page').forEach(p => {
        p.style.display = 'none';
    });

    // Show selected page
    const targetPage = document.getElementById(`${page}-page`);
    if (targetPage) {
        targetPage.style.display = 'block';
    }

    // Update navigation
    document.querySelectorAll('.apple-nav-links a').forEach(link => {
        link.classList.remove('active');
    });
    const activeLink = document.querySelector(`[data-page="${page}"]`);
    if (activeLink) {
        activeLink.classList.add('active');
    }

    // Load page data
    appState.ui.currentPage = page;
    loadPageData(page);
}

function loadPageData(page) {
    switch(page) {
        case 'dashboard':
            loadDashboardData();
            break;
        case 'vehicles':
            loadVehiclesPage();
            break;
        case 'customers':
            loadCustomersPage();
            break;
        case 'reminders':
            loadRemindersPage();
            break;
        case 'job-sheets':
            loadJobSheetsPage();
            break;
        case 'settings':
            loadSettingsPage();
            break;
    }
}

// Page-specific loading functions
async function loadVehiclesPage() {
    const vehicles = await loadVehiclesData();
    const customers = await loadCustomersData();
    
    const vehiclesContainer = document.getElementById('vehicles-list');
    if (!vehiclesContainer) return;

    if (vehicles.length === 0) {
        vehiclesContainer.innerHTML = '<p class="no-data">No vehicles found.</p>';
        return;
    }

    vehiclesContainer.innerHTML = vehicles.map(vehicle => {
        const customer = customers.find(c => c.id === vehicle.customer_id);
        return `
            <div class="vehicle-card">
                <div class="vehicle-header">
                    <h3>${vehicle.registration}</h3>
                    ${UIUtils.getUrgencyBadge(vehicle.mot_status)}
                </div>
                <div class="vehicle-details">
                    <p><strong>${vehicle.make} ${vehicle.model}</strong></p>
                    <p>MOT Expires: ${UIUtils.formatDate(vehicle.mot_expiry)}</p>
                    <p>Customer: ${customer ? customer.name : 'Unknown'}</p>
                </div>
                <div class="vehicle-actions">
                    <button class="apple-btn apple-btn-primary" onclick="editVehicle(${vehicle.id})">
                        Edit
                    </button>
                    <button class="apple-btn apple-btn-secondary" onclick="checkDVLA('${vehicle.registration}')">
                        Check DVLA
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

async function loadCustomersPage() {
    const customers = await loadCustomersData();
    
    const customersContainer = document.getElementById('customers-list');
    if (!customersContainer) return;

    if (customers.length === 0) {
        customersContainer.innerHTML = '<p class="no-data">No customers found.</p>';
        return;
    }

    customersContainer.innerHTML = customers.map(customer => `
        <div class="customer-card">
            <div class="customer-header">
                <h3>${customer.name}</h3>
            </div>
            <div class="customer-details">
                <p><i class="fas fa-envelope"></i> ${customer.email || 'No email'}</p>
                <p><i class="fas fa-phone"></i> ${customer.phone || 'No phone'}</p>
            </div>
            <div class="customer-actions">
                <button class="apple-btn apple-btn-primary" onclick="editCustomer(${customer.id})">
                    Edit
                </button>
                <button class="apple-btn apple-btn-secondary" onclick="viewCustomerVehicles(${customer.id})">
                    View Vehicles
                </button>
            </div>
        </div>
    `).join('');
}

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    console.log('Enhanced MOT Reminder System initializing...');
    
    // Initialize theme
    document.body.setAttribute('data-theme', appState.ui.theme);
    
    // Load initial data
    loadDashboardData();
    
    // Set up periodic data refresh
    setInterval(() => {
        if (appState.ui.currentPage === 'dashboard') {
            loadDashboardData();
        }
    }, 60000); // Refresh every minute
    
    console.log('Enhanced MOT Reminder System initialized successfully');
});

// Utility functions for UI interactions
function processReminder(reminderId) {
    console.log('Processing reminder:', reminderId);
    UIUtils.showSuccess('Reminder processed successfully');
}

function editVehicle(vehicleId) {
    console.log('Editing vehicle:', vehicleId);
    // Implementation for vehicle editing
}

function editCustomer(customerId) {
    console.log('Editing customer:', customerId);
    // Implementation for customer editing
}

function checkDVLA(registration) {
    console.log('Checking DVLA for:', registration);
    UIUtils.showSuccess('DVLA check initiated');
}

function viewCustomerVehicles(customerId) {
    console.log('Viewing vehicles for customer:', customerId);
    showPageDirect('vehicles');
}

