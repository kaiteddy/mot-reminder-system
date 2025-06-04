// MOT Reminder System Main JavaScript

// Global variables
let currentPage = 'dashboard';
let vehicles = [];
let customers = [];
let reminders = [];
let jobSheets = [];
let vehicleCustomerMap = {};

// DOM Ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize AI theme
    initAITheme();

    // Initialize theme toggle
    initializeThemeToggle();

    // Initialize navigation
    initNavigation();

    // Load initial data
    loadDashboard();

    // Initialize event listeners
    initEventListeners();

    // Initialize Bootstrap components
    initBootstrapComponents();

    // Start AI animations
    startAIAnimations();
});

// Initialize navigation
function initNavigation() {
    console.log('Initializing navigation...');

    // Handle both old .nav-link and new Apple-style navigation
    const navLinks = document.querySelectorAll('.nav-link, .apple-nav-links a');
    console.log('Found navigation links:', navLinks.length);

    navLinks.forEach((link, index) => {
        const page = link.getAttribute('data-page');
        console.log(`Nav link ${index}: ${page}`);

        link.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Navigation clicked:', page);
            showPage(page);
        });
    });
}

// Show selected page
function showPage(page) {
    console.log('Showing page:', page);

    // Hide all pages
    document.querySelectorAll('.page').forEach(p => {
        p.style.display = 'none';
    });

    // Show selected page
    const targetPage = document.getElementById(`${page}-page`);
    if (targetPage) {
        targetPage.style.display = 'block';
        console.log('Successfully showed page:', page);
    } else {
        console.error('Page not found:', `${page}-page`);
    }

    // Update active nav link for both old and new navigation
    document.querySelectorAll('.nav-link, .apple-nav-links a').forEach(link => {
        link.classList.remove('active');
    });
    const activeLink = document.querySelector(`.nav-link[data-page="${page}"], .apple-nav-links a[data-page="${page}"]`);
    if (activeLink) {
        activeLink.classList.add('active');
        console.log('Updated active nav link for:', page);
    } else {
        console.warn('Nav link not found for page:', page);
    }

    // Load page data
    currentPage = page;
    switch(page) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'vehicles':
            loadVehicles();
            break;
        case 'customers':
            loadCustomers();
            break;
        case 'reminders':
            loadRemindersEnhanced();
            break;
        case 'job-sheets':
            loadJobSheets();
            break;
        case 'settings':
            loadSettings();
            break;
        default:
            console.warn('Unknown page:', page);
    }
}

// Initialize event listeners
function initEventListeners() {
    // Dashboard buttons
    document.getElementById('process-reminders-btn').addEventListener('click', processReminders);
    document.getElementById('schedule-reminders-btn').addEventListener('click', scheduleReminders);

    // Vehicle modal
    document.getElementById('add-vehicle-btn').addEventListener('click', () => showVehicleModal());
    document.getElementById('save-vehicle-btn').addEventListener('click', saveVehicle);
    document.getElementById('lookup-vehicle-btn').addEventListener('click', lookupVehicle);

    // Customer modal
    document.getElementById('add-customer-btn').addEventListener('click', () => showCustomerModal());
    document.getElementById('save-customer-btn').addEventListener('click', saveCustomer);

    // Reminder modal
    document.getElementById('add-reminder-btn').addEventListener('click', () => showReminderModal());
    document.getElementById('save-reminder-btn').addEventListener('click', saveReminder);

    // Settings forms
    document.getElementById('email-settings-form').addEventListener('submit', saveEmailSettings);
    document.getElementById('sms-settings-form').addEventListener('submit', saveSmsSettings);
    document.getElementById('email-template-form').addEventListener('submit', saveEmailTemplate);
    document.getElementById('sms-template-form').addEventListener('submit', saveSmsTemplate);
    document.getElementById('dvla-settings-form').addEventListener('submit', saveDvlaSettings);

    // Setup upload functionality
    setupOCRUpload();
    setupCSVUpload();
    setupJobSheetsUpload();

    // Clear all vehicles button (global)
    document.getElementById('clear-all-vehicles-btn')?.addEventListener('click', clearAllVehicles);

    // Job sheets buttons
    document.getElementById('upload-job-sheets-btn')?.addEventListener('click', () => {
        document.getElementById('job-sheets-upload-section').style.display = 'block';
    });
    document.getElementById('cancel-job-sheets-btn')?.addEventListener('click', () => {
        document.getElementById('job-sheets-upload-section').style.display = 'none';
        clearFileSelection();
    });
    document.getElementById('clear-files-btn')?.addEventListener('click', clearFileSelection);
    document.getElementById('link-job-data-btn')?.addEventListener('click', linkJobData);
    document.getElementById('dvla-lookup-all-btn')?.addEventListener('click', performDVLALookupAll);
    document.getElementById('clear-all-job-sheets-btn')?.addEventListener('click', clearAllJobSheets);
    document.getElementById('view-analytics-btn')?.addEventListener('click', showJobSheetsAnalytics);

    // Vehicle details modal buttons
    document.getElementById('edit-vehicle-from-details')?.addEventListener('click', function() {
        const vehicleId = this.getAttribute('data-vehicle-id');
        if (vehicleId) {
            bootstrap.Modal.getInstance(document.getElementById('vehicle-details-modal')).hide();
            showVehicleModal(vehicleId);
        }
    });

    document.getElementById('add-reminder-for-vehicle')?.addEventListener('click', function() {
        const vehicleId = this.getAttribute('data-vehicle-id');
        if (vehicleId) {
            bootstrap.Modal.getInstance(document.getElementById('vehicle-details-modal')).hide();
            showReminderModal(null, vehicleId);
        }
    });

    // Reminder details modal buttons
    document.getElementById('edit-reminder-from-details')?.addEventListener('click', function() {
        const reminderId = this.getAttribute('data-reminder-id');
        if (reminderId) {
            bootstrap.Modal.getInstance(document.getElementById('reminder-details-modal')).hide();
            showReminderModal(reminderId);
        }
    });

    document.getElementById('send-reminder-from-details')?.addEventListener('click', function() {
        const reminderId = this.getAttribute('data-reminder-id');
        if (reminderId) {
            performBulkAction('send', [reminderId]);
            bootstrap.Modal.getInstance(document.getElementById('reminder-details-modal')).hide();
        }
    });
}

// Initialize Bootstrap components
function initBootstrapComponents() {
    // Initialize all tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Initialize AI Theme
function initAITheme() {
    // Add AI loading states
    document.body.classList.add('ai-loading-complete');

    // Add typing effect to AI insights
    setTimeout(() => {
        typeAIInsights();
    }, 1000);

    // Add particle effects
    createParticleEffect();
}

// Start AI Animations
function startAIAnimations() {
    // Animate stat numbers
    animateStatNumbers();

    // Add hover effects to cards
    addCardHoverEffects();

    // Start AI avatar pulse
    startAvatarPulse();
}

// Type AI Insights with animation (legacy - now handled by loadAIInsights)
function typeAIInsights() {
    // This function is now handled by the dynamic AI insights loading
    // Keeping for compatibility but functionality moved to loadAIInsights()
}

// Type text with animation
function typeText(element, text, speed) {
    let i = 0;
    const timer = setInterval(() => {
        if (i < text.length) {
            element.innerHTML += text.charAt(i);
            i++;
        } else {
            clearInterval(timer);
        }
    }, speed);
}

// Animate stat numbers
function animateStatNumbers() {
    const statNumbers = document.querySelectorAll('.stat-number');
    statNumbers.forEach(stat => {
        const target = parseInt(stat.textContent) || 0;
        animateNumber(stat, 0, target, 2000);
    });
}

// Animate number counting
function animateNumber(element, start, end, duration) {
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        const current = Math.floor(start + (end - start) * easeOutQuart(progress));
        element.textContent = current;

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }

    requestAnimationFrame(update);
}

// Easing function
function easeOutQuart(t) {
    return 1 - (--t) * t * t * t;
}

// Add card hover effects
function addCardHoverEffects() {
    const cards = document.querySelectorAll('.card, .stat-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-8px) scale(1.02)';
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0) scale(1)';
        });
    });
}

// Start avatar pulse animation
function startAvatarPulse() {
    const avatar = document.querySelector('.ai-avatar');
    if (avatar) {
        setInterval(() => {
            avatar.style.boxShadow = '0 0 30px rgba(0, 212, 255, 0.8)';
            setTimeout(() => {
                avatar.style.boxShadow = '0 0 20px rgba(0, 212, 255, 0.3)';
            }, 500);
        }, 3000);
    }
}

// Create particle effect
function createParticleEffect() {
    const particleContainer = document.createElement('div');
    particleContainer.className = 'particle-container';
    particleContainer.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: -1;
    `;

    document.body.appendChild(particleContainer);

    // Create floating particles
    for (let i = 0; i < 20; i++) {
        createParticle(particleContainer);
    }
}

// Create individual particle
function createParticle(container) {
    const particle = document.createElement('div');
    particle.style.cssText = `
        position: absolute;
        width: 2px;
        height: 2px;
        background: rgba(0, 212, 255, 0.6);
        border-radius: 50%;
        animation: float ${Math.random() * 10 + 10}s linear infinite;
    `;

    particle.style.left = Math.random() * 100 + '%';
    particle.style.animationDelay = Math.random() * 10 + 's';

    container.appendChild(particle);

    // Add CSS animation
    if (!document.querySelector('#particle-styles')) {
        const style = document.createElement('style');
        style.id = 'particle-styles';
        style.textContent = `
            @keyframes float {
                0% {
                    transform: translateY(100vh) rotate(0deg);
                    opacity: 0;
                }
                10% {
                    opacity: 1;
                }
                90% {
                    opacity: 1;
                }
                100% {
                    transform: translateY(-100vh) rotate(360deg);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
}

// Enhanced toast with AI styling
function showAIToast(title, message, type = 'info') {
    const toast = document.getElementById('toast');
    const toastTitle = document.getElementById('toast-title');
    const toastMessage = document.getElementById('toast-message');

    // Add AI prefix
    toastTitle.innerHTML = `<i class="fas fa-robot"></i> AI Assistant`;
    toastMessage.innerHTML = `<strong>${title}:</strong> ${message}`;

    // Add type-specific styling
    toast.className = `toast ai-toast-${type}`;

    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
}

// Create UK number plate with DVLA check link
function createNumberPlateWithDVLALink(registration, size = 'normal') {
    const cleanReg = registration.replace(/\s+/g, '').toUpperCase();
    const displayReg = formatRegistrationForDisplay(registration);
    const dvlaUrl = `https://www.check-mot.service.gov.uk/results?registration=${encodeURIComponent(cleanReg)}`;

    const sizeClass = size === 'small' ? 'small' : '';

    return `
        <div class="registration-container">
            <span class="uk-number-plate ${sizeClass}" title="UK Registration: ${displayReg}">
                ${displayReg}
            </span>
            <a href="${dvlaUrl}" target="_blank" class="dvla-check-link" title="Check MOT history on DVLA website">
                <i class="fas fa-external-link-alt"></i>
                MOT Check
            </a>
        </div>
    `;
}

// Format registration for display (add spaces in appropriate places)
function formatRegistrationForDisplay(registration) {
    const clean = registration.replace(/\s+/g, '').toUpperCase();

    // Handle different UK registration formats
    if (clean.length === 7) {
        // Current format: AB12 CDE
        return `${clean.substring(0, 2)}${clean.substring(2, 4)} ${clean.substring(4)}`;
    } else if (clean.length === 6) {
        // Older formats: ABC 123 or A123 BCD
        if (/^[A-Z]{3}\d{3}$/.test(clean)) {
            // ABC 123 format
            return `${clean.substring(0, 3)} ${clean.substring(3)}`;
        } else if (/^[A-Z]\d{3}[A-Z]{3}$/.test(clean)) {
            // A123 BCD format
            return `${clean.substring(0, 4)} ${clean.substring(4)}`;
        }
    } else if (clean.length === 5) {
        // A123 BC format
        return `${clean.substring(0, 4)} ${clean.substring(4)}`;
    }

    // Return as-is if format not recognized
    return clean;
}

// Format date to DD-MM-YYYY format
function formatDateUK(dateString) {
    if (!dateString) return 'Not set';

    try {
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return 'Invalid date';

        const day = date.getDate().toString().padStart(2, '0');
        const month = (date.getMonth() + 1).toString().padStart(2, '0');
        const year = date.getFullYear();

        return `${day}-${month}-${year}`;
    } catch (error) {
        return 'Invalid date';
    }
}

// Fetch and display MOT history for a vehicle
function fetchMOTHistory(registration) {
    return fetch(`/api/vehicles/lookup/${encodeURIComponent(registration)}`)
        .then(response => response.json())
        .then(data => {
            if (data && data.registrationNumber) {
                return {
                    success: true,
                    data: data
                };
            } else {
                return {
                    success: false,
                    error: 'No MOT data found'
                };
            }
        })
        .catch(error => {
            console.error('Error fetching MOT history:', error);
            return {
                success: false,
                error: 'Failed to fetch MOT data'
            };
        });
}

// Create MOT history display HTML
function createMOTHistoryHTML(motData) {
    if (!motData || !motData.success) {
        return `
            <div class="alert alert-warning">
                <i class="fas fa-exclamation-triangle"></i>
                MOT history not available: ${motData?.error || 'Unknown error'}
            </div>
        `;
    }

    const data = motData.data;

    return `
        <div class="mot-history-container">
            <div class="row mb-3">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h6 class="mb-0"><i class="fas fa-car"></i> Vehicle Information</h6>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-sm-6"><strong>Registration:</strong></div>
                                <div class="col-sm-6">${createNumberPlateWithDVLALink(data.registrationNumber, 'small')}</div>
                            </div>
                            <div class="row">
                                <div class="col-sm-6"><strong>Make:</strong></div>
                                <div class="col-sm-6">${data.make || 'Not available'}</div>
                            </div>
                            <div class="row">
                                <div class="col-sm-6"><strong>Model:</strong></div>
                                <div class="col-sm-6">${data.model || 'Not available'}</div>
                            </div>
                            <div class="row">
                                <div class="col-sm-6"><strong>Colour:</strong></div>
                                <div class="col-sm-6">${data.primaryColour || 'Not available'}</div>
                            </div>
                            <div class="row">
                                <div class="col-sm-6"><strong>Fuel Type:</strong></div>
                                <div class="col-sm-6">${data.fuelType || 'Not available'}</div>
                            </div>
                            <div class="row">
                                <div class="col-sm-6"><strong>Engine Size:</strong></div>
                                <div class="col-sm-6">${data.engineCapacity ? data.engineCapacity + 'cc' : 'Not available'}</div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h6 class="mb-0"><i class="fas fa-clipboard-check"></i> Current MOT Status</h6>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-sm-6"><strong>MOT Status:</strong></div>
                                <div class="col-sm-6">
                                    <span class="badge ${data.motStatus === 'PASSED' ? 'bg-success' : 'bg-danger'}">
                                        ${data.motStatus || 'Unknown'}
                                    </span>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-sm-6"><strong>MOT Expiry:</strong></div>
                                <div class="col-sm-6">${formatDateUK(data.motExpiryDate)}</div>
                            </div>
                            <div class="row">
                                <div class="col-sm-6"><strong>Last Test Date:</strong></div>
                                <div class="col-sm-6">${formatDateUK(data.motTestDate)}</div>
                            </div>
                            <div class="row">
                                <div class="col-sm-6"><strong>Test Mileage:</strong></div>
                                <div class="col-sm-6">${data.motTestMileage ? Number(data.motTestMileage).toLocaleString() + ' miles' : 'Not available'}</div>
                            </div>
                            <div class="row">
                                <div class="col-sm-6"><strong>Test Number:</strong></div>
                                <div class="col-sm-6">${data.motTestNumber || 'Not available'}</div>
                            </div>
                            <div class="row">
                                <div class="col-sm-6"><strong>First Used:</strong></div>
                                <div class="col-sm-6">${formatDateUK(data.firstUsedDate)}</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <h6 class="mb-0"><i class="fas fa-external-link-alt"></i> Official DVLA Check</h6>
                </div>
                <div class="card-body text-center">
                    <p class="mb-3">For complete MOT history including advisories and failures, visit the official DVLA website:</p>
                    <a href="https://www.check-mot.service.gov.uk/results?registration=${encodeURIComponent(data.registrationNumber)}"
                       target="_blank" class="btn btn-primary btn-lg">
                        <i class="fas fa-external-link-alt"></i>
                        View Full MOT History on DVLA
                    </a>
                </div>
            </div>
        </div>
    `;
}

// Load dashboard data
function loadDashboard() {
    // Load counts
    fetch('/api/vehicles/')
        .then(response => response.json())
        .then(data => {
            vehicles = data;
            document.getElementById('vehicles-count').textContent = data.length;
            updateVehicleCustomerMap();
        })
        .catch(error => {
            console.error('Error loading dashboard data:', error);
            showToast('Error', 'Failed to load vehicle data');
        });

    fetch('/api/customers/')
        .then(response => response.json())
        .then(data => {
            customers = data;
            document.getElementById('customers-count').textContent = data.length;
            updateVehicleCustomerMap();
        })
        .catch(error => {
            console.error('Error loading dashboard data:', error);
            showToast('Error', 'Failed to load customer data');
        });

    // Load due reminders
    fetch('/api/reminders/due')
        .then(response => response.json())
        .then(data => {
            document.getElementById('reminders-due-count').textContent = data.length;
            renderDueRemindersTable(data);
        })
        .catch(error => {
            console.error('Error loading due reminders:', error);
            showToast('Error', 'Failed to load due reminders');
        });

    // Load AI insights
    loadAIInsights();
}

// Load AI insights
function loadAIInsights() {
    const insightsContainer = document.getElementById('ai-insights-content');

    // Show loading state
    insightsContainer.innerHTML = `
        <div class="ai-loading">
            <i class="fas fa-spinner fa-spin"></i> Analyzing your data to generate insights...
        </div>
    `;

    fetch('/api/insights')
        .then(response => response.json())
        .then(data => {
            renderAIInsights(data.insights, data.stats);
        })
        .catch(error => {
            console.error('Error loading AI insights:', error);
            insightsContainer.innerHTML = `
                <div class="ai-error">
                    <i class="fas fa-exclamation-triangle"></i> Unable to generate insights at this time.
                </div>
            `;
        });
}

// Render AI insights
function renderAIInsights(insights, stats) {
    const insightsContainer = document.getElementById('ai-insights-content');

    if (!insights || insights.length === 0) {
        insightsContainer.innerHTML = `
            <div class="ai-info">
                <strong>💡 Getting Started:</strong> Upload your vehicle data or job sheets to start receiving AI-powered insights and recommendations.
            </div>
        `;
        return;
    }

    let insightsHTML = '';
    insights.forEach((insight, index) => {
        const typeClass = getInsightTypeClass(insight.type);
        insightsHTML += `
            <div class="ai-insight ${typeClass}" style="animation-delay: ${index * 0.5}s">
                <strong>${insight.icon} ${insight.title}:</strong> ${insight.message}
            </div>
        `;
    });

    insightsContainer.innerHTML = insightsHTML;

    // Update stats if available
    if (stats) {
        updateDashboardStats(stats);
    }
}

// Get CSS class for insight type
function getInsightTypeClass(type) {
    switch(type) {
        case 'urgent': return 'ai-urgent';
        case 'warning': return 'ai-warning';
        case 'recommendation': return 'ai-recommendation';
        case 'success': return 'ai-success';
        case 'action': return 'ai-action';
        case 'prediction': return 'ai-prediction';
        case 'info':
        default: return 'ai-info';
    }
}

// Update dashboard stats
function updateDashboardStats(stats) {
    if (stats.overdue_mots !== undefined) {
        // Update the reminders count to show overdue MOTs
        const remindersCount = document.getElementById('reminders-due-count');
        if (remindersCount) {
            remindersCount.textContent = stats.overdue_mots + stats.expiring_soon;
        }
    }
}

// Update vehicle-customer mapping
function updateVehicleCustomerMap() {
    vehicleCustomerMap = {};
    vehicles.forEach(vehicle => {
        if (vehicle.customer_id) {
            const customer = customers.find(c => c.id === vehicle.customer_id);
            if (customer) {
                vehicleCustomerMap[vehicle.id] = customer;
            }
        }
    });
}

// Render due reminders table
function renderDueRemindersTable(dueReminders) {
    const tableBody = document.getElementById('due-reminders-table');
    tableBody.innerHTML = '';

    if (dueReminders.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td colspan="5" class="apple-empty-state" style="padding: var(--apple-spacing-lg);">
                <div class="apple-empty-state-icon">🎯</div>
                <div class="apple-empty-state-title">No Urgent Reminders</div>
                <div class="apple-empty-state-subtitle">All MOT reminders are up to date</div>
            </td>
        `;
        tableBody.appendChild(row);
        return;
    }

    dueReminders.forEach(reminder => {
        const vehicle = reminder.vehicle || {};
        const customer = reminder.customer || {};

        const row = document.createElement('tr');

        // Calculate days left
        let daysLeft = '';
        if (vehicle.mot_expiry) {
            const motExpiry = new Date(vehicle.mot_expiry);
            const today = new Date();
            const diffTime = motExpiry - today;
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            daysLeft = diffDays;
        }

        row.innerHTML = `
            <td class="registration-cell">${createNumberPlateWithDVLALink(vehicle.registration || '', 'small')}</td>
            <td class="customer-cell">${customer.name || ''}</td>
            <td class="date-cell">${formatDateUK(vehicle.mot_expiry)}</td>
            <td class="days-cell">${daysLeft}</td>
            <td class="actions-cell">
                <button class="apple-btn apple-btn-primary process-reminder-btn" data-id="${reminder.id}" style="padding: 6px 12px; min-height: auto; font-size: 13px;">
                    <i class="bi bi-envelope"></i> Send
                </button>
            </td>
        `;

        tableBody.appendChild(row);
    });

    // Add event listeners to process buttons
    document.querySelectorAll('.process-reminder-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const reminderId = this.getAttribute('data-id');
            processSingleReminder(reminderId);
        });
    });
}

// Process reminders
function processReminders() {
    fetch('/api/reminders/process', {
        method: 'POST'
    })
        .then(response => response.json())
        .then(data => {
            showToast('Success', `Processed ${data.reminders_processed} reminders`);
            loadDashboard();
        })
        .catch(error => {
            console.error('Error processing reminders:', error);
            showToast('Error', 'Failed to process reminders');
        });
}

// Process a single reminder
function processSingleReminder(reminderId) {
    fetch(`/api/reminders/${reminderId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            status: 'sent',
            sent_at: new Date().toISOString()
        })
    })
        .then(response => response.json())
        .then(data => {
            showToast('Success', 'Reminder sent successfully');
            loadDashboard();
        })
        .catch(error => {
            console.error('Error processing reminder:', error);
            showToast('Error', 'Failed to send reminder');
        });
}

// Schedule reminders
function scheduleReminders() {
    fetch('/api/reminders/schedule', {
        method: 'POST'
    })
        .then(response => response.json())
        .then(data => {
            showToast('Success', `Scheduled ${data.reminders_created} new reminders`);
            loadDashboard();
        })
        .catch(error => {
            console.error('Error scheduling reminders:', error);
            showToast('Error', 'Failed to schedule reminders');
        });
}

// Load vehicles
function loadVehicles() {
    fetch('/api/vehicles/')
        .then(response => response.json())
        .then(data => {
            vehicles = data;
            renderVehiclesTable(data);
            updateVehicleCustomerMap();
        })
        .catch(error => {
            console.error('Error loading vehicles:', error);
            showToast('Error', 'Failed to load vehicles');
        });
}

// Render vehicles table
function renderVehiclesTable(vehicles) {
    const tableBody = document.getElementById('vehicles-table');
    tableBody.innerHTML = '';

    if (vehicles.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = '<td colspan="6" class="text-center">No vehicles found</td>';
        tableBody.appendChild(row);
        return;
    }

    vehicles.forEach(vehicle => {
        const row = document.createElement('tr');

        // Find customer name
        let customerName = '';
        if (vehicle.customer_id) {
            const customer = customers.find(c => c.id === vehicle.customer_id);
            if (customer) {
                customerName = customer.name;
            }
        }

        row.innerHTML = `
            <td class="registration-cell">${createNumberPlateWithDVLALink(vehicle.registration, 'small')}</td>
            <td class="single-line">${vehicle.make || ''}</td>
            <td class="single-line">${vehicle.model || ''}</td>
            <td class="customer-cell single-line">${customerName}</td>
            <td class="date-cell">${formatDateUK(vehicle.mot_expiry)}</td>
            <td class="actions-cell">
                <button class="btn btn-sm btn-success view-vehicle-btn" data-id="${vehicle.id}" title="View Details">
                    <i class="bi bi-eye"></i>
                </button>
                <button class="btn btn-sm btn-primary edit-vehicle-btn" data-id="${vehicle.id}" title="Edit">
                    <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-danger delete-vehicle-btn" data-id="${vehicle.id}" title="Delete">
                    <i class="bi bi-trash"></i>
                </button>
                <button class="btn btn-sm btn-info check-vehicle-btn" data-id="${vehicle.id}" title="Check DVLA">
                    <i class="bi bi-check-circle"></i>
                </button>
            </td>
        `;

        tableBody.appendChild(row);
    });

    // Add event listeners to buttons
    document.querySelectorAll('.view-vehicle-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const vehicleId = this.getAttribute('data-id');
            showVehicleDetails(vehicleId);
        });
    });

    document.querySelectorAll('.edit-vehicle-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const vehicleId = this.getAttribute('data-id');
            showVehicleModal(vehicleId);
        });
    });

    document.querySelectorAll('.delete-vehicle-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const vehicleId = this.getAttribute('data-id');
            deleteVehicle(vehicleId);
        });
    });

    document.querySelectorAll('.check-vehicle-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const vehicleId = this.getAttribute('data-id');
            checkVehicle(vehicleId);
        });
    });
}

// Show vehicle modal
function showVehicleModal(vehicleId = null) {
    const modal = new bootstrap.Modal(document.getElementById('vehicle-modal'));
    const modalTitle = document.getElementById('vehicle-modal-title');
    const form = document.getElementById('vehicle-form');

    // Reset form
    form.reset();
    document.getElementById('vehicle-id').value = '';

    // Load customers for dropdown
    const customerSelect = document.getElementById('vehicle-customer');
    customerSelect.innerHTML = '<option value="">Select Customer</option>';
    customers.forEach(customer => {
        const option = document.createElement('option');
        option.value = customer.id;
        option.textContent = customer.name;
        customerSelect.appendChild(option);
    });

    if (vehicleId) {
        // Edit mode
        modalTitle.textContent = 'Edit Vehicle';
        const vehicle = vehicles.find(v => v.id === parseInt(vehicleId));
        if (vehicle) {
            document.getElementById('vehicle-id').value = vehicle.id;
            document.getElementById('vehicle-registration').value = vehicle.registration;
            document.getElementById('vehicle-make').value = vehicle.make || '';
            document.getElementById('vehicle-model').value = vehicle.model || '';
            document.getElementById('vehicle-color').value = vehicle.color || '';
            document.getElementById('vehicle-year').value = vehicle.year || '';
            if (vehicle.mot_expiry) {
                document.getElementById('vehicle-mot-expiry').value = vehicle.mot_expiry.split('T')[0];
            }
            if (vehicle.customer_id) {
                document.getElementById('vehicle-customer').value = vehicle.customer_id;
            }
        }
    } else {
        // Add mode
        modalTitle.textContent = 'Add Vehicle';
    }

    modal.show();
}

// Save vehicle
function saveVehicle() {
    const vehicleId = document.getElementById('vehicle-id').value;
    const registration = document.getElementById('vehicle-registration').value;
    const make = document.getElementById('vehicle-make').value;
    const model = document.getElementById('vehicle-model').value;
    const color = document.getElementById('vehicle-color').value;
    const year = document.getElementById('vehicle-year').value;
    const motExpiry = document.getElementById('vehicle-mot-expiry').value;
    const customerId = document.getElementById('vehicle-customer').value;

    if (!registration) {
        showToast('Error', 'Registration is required');
        return;
    }

    const vehicleData = {
        registration: registration,
        make: make,
        model: model,
        color: color,
        year: year ? parseInt(year) : null,
        mot_expiry: motExpiry,
        customer_id: customerId ? parseInt(customerId) : null
    };

    const url = vehicleId ? `/api/vehicles/${vehicleId}` : '/api/vehicles/';
    const method = vehicleId ? 'PUT' : 'POST';

    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(vehicleData)
    })
        .then(response => response.json())
        .then(data => {
            showToast('Success', `Vehicle ${vehicleId ? 'updated' : 'added'} successfully`);
            bootstrap.Modal.getInstance(document.getElementById('vehicle-modal')).hide();
            loadVehicles();
            if (currentPage === 'dashboard') {
                loadDashboard();
            }
        })
        .catch(error => {
            console.error('Error saving vehicle:', error);
            showToast('Error', `Failed to ${vehicleId ? 'update' : 'add'} vehicle`);
        });
}

// Delete vehicle
function deleteVehicle(vehicleId) {
    if (confirm('Are you sure you want to delete this vehicle?')) {
        fetch(`/api/vehicles/${vehicleId}`, {
            method: 'DELETE'
        })
            .then(response => response.json())
            .then(data => {
                showToast('Success', 'Vehicle deleted successfully');
                loadVehicles();
                if (currentPage === 'dashboard') {
                    loadDashboard();
                }
            })
            .catch(error => {
                console.error('Error deleting vehicle:', error);
                showToast('Error', 'Failed to delete vehicle');
            });
    }
}

// Check vehicle against DVLA
function checkVehicle(vehicleId) {
    fetch(`/api/vehicles/${vehicleId}/check`, {
        method: 'POST'
    })
        .then(response => response.json())
        .then(data => {
            if (data.has_discrepancies) {
                const discrepancyText = data.discrepancies.map(d =>
                    `${d.field}: ${d.garage_value || 'Not set'} → ${d.dvla_value}`
                ).join('\n');

                if (confirm(`Discrepancies found:\n\n${discrepancyText}\n\nUpdate vehicle with DVLA data?`)) {
                    updateVehicleFromDvla(vehicleId);
                }
            } else {
                showToast('Success', 'No discrepancies found');
            }
        })
        .catch(error => {
            console.error('Error checking vehicle:', error);
            showToast('Error', 'Failed to check vehicle against DVLA');
        });
}

// Update vehicle from DVLA
function updateVehicleFromDvla(vehicleId) {
    fetch(`/api/vehicles/${vehicleId}/update-from-dvla`, {
        method: 'POST'
    })
        .then(response => response.json())
        .then(data => {
            showToast('Success', 'Vehicle updated from DVLA data');
            loadVehicles();
        })
        .catch(error => {
            console.error('Error updating vehicle from DVLA:', error);
            showToast('Error', 'Failed to update vehicle from DVLA');
        });
}

// Lookup vehicle by registration
function lookupVehicle() {
    const registration = document.getElementById('vehicle-registration').value;

    if (!registration) {
        showToast('Error', 'Registration is required');
        return;
    }

    fetch(`/api/vehicles/lookup/${registration}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('vehicle-make').value = data.make || '';
            document.getElementById('vehicle-model').value = data.model || '';
            document.getElementById('vehicle-color').value = data.primaryColour || '';
            document.getElementById('vehicle-year').value = data.yearOfManufacture || '';

            if (data.motExpiryDate) {
                document.getElementById('vehicle-mot-expiry').value = data.motExpiryDate.split('T')[0];
            }

            showToast('Success', 'Vehicle details retrieved from DVLA');
        })
        .catch(error => {
            console.error('Error looking up vehicle:', error);
            showToast('Error', 'Failed to lookup vehicle details');
        });
}

// Load customers
function loadCustomers() {
    fetch('/api/customers/')
        .then(response => response.json())
        .then(data => {
            customers = data;
            renderCustomersTable(data);
        })
        .catch(error => {
            console.error('Error loading customers:', error);
            showToast('Error', 'Failed to load customers');
        });
}

// Render customers table
function renderCustomersTable(customers) {
    const tableBody = document.getElementById('customers-table');
    tableBody.innerHTML = '';

    if (customers.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = '<td colspan="5" class="text-center">No customers found</td>';
        tableBody.appendChild(row);
        return;
    }

    customers.forEach(customer => {
        const row = document.createElement('tr');

        // Count vehicles for this customer
        const customerVehicles = vehicles.filter(v => v.customer_id === customer.id);

        row.innerHTML = `
            <td class="customer-cell single-line">${customer.name}</td>
            <td class="single-line">${customer.email || ''}</td>
            <td class="single-line">${customer.phone || ''}</td>
            <td class="single-line">${customerVehicles.length}</td>
            <td>
                <button class="btn btn-sm btn-primary edit-customer-btn" data-id="${customer.id}">
                    <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-danger delete-customer-btn" data-id="${customer.id}">
                    <i class="bi bi-trash"></i>
                </button>
                <button class="btn btn-sm btn-info view-customer-vehicles-btn" data-id="${customer.id}">
                    <i class="bi bi-car-front"></i>
                </button>
            </td>
        `;

        tableBody.appendChild(row);
    });

    // Add event listeners to buttons
    document.querySelectorAll('.edit-customer-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const customerId = this.getAttribute('data-id');
            showCustomerModal(customerId);
        });
    });

    document.querySelectorAll('.delete-customer-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const customerId = this.getAttribute('data-id');
            deleteCustomer(customerId);
        });
    });

    document.querySelectorAll('.view-customer-vehicles-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const customerId = this.getAttribute('data-id');
            showPage('vehicles');
            // TODO: Filter vehicles by customer
        });
    });
}

// Show customer modal
function showCustomerModal(customerId = null) {
    const modal = new bootstrap.Modal(document.getElementById('customer-modal'));
    const modalTitle = document.getElementById('customer-modal-title');
    const form = document.getElementById('customer-form');

    // Reset form
    form.reset();
    document.getElementById('customer-id').value = '';

    if (customerId) {
        // Edit mode
        modalTitle.textContent = 'Edit Customer';
        const customer = customers.find(c => c.id === parseInt(customerId));
        if (customer) {
            document.getElementById('customer-id').value = customer.id;
            document.getElementById('customer-name').value = customer.name;
            document.getElementById('customer-email').value = customer.email || '';
            document.getElementById('customer-phone').value = customer.phone || '';
        }
    } else {
        // Add mode
        modalTitle.textContent = 'Add Customer';
    }

    modal.show();
}

// Save customer
function saveCustomer() {
    const customerId = document.getElementById('customer-id').value;
    const name = document.getElementById('customer-name').value;
    const email = document.getElementById('customer-email').value;
    const phone = document.getElementById('customer-phone').value;

    if (!name) {
        showToast('Error', 'Name is required');
        return;
    }

    const customerData = {
        name: name,
        email: email,
        phone: phone
    };

    const url = customerId ? `/api/customers/${customerId}` : '/api/customers/';
    const method = customerId ? 'PUT' : 'POST';

    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(customerData)
    })
        .then(response => response.json())
        .then(data => {
            showToast('Success', `Customer ${customerId ? 'updated' : 'added'} successfully`);
            bootstrap.Modal.getInstance(document.getElementById('customer-modal')).hide();
            loadCustomers();
            if (currentPage === 'dashboard') {
                loadDashboard();
            }
        })
        .catch(error => {
            console.error('Error saving customer:', error);
            showToast('Error', `Failed to ${customerId ? 'update' : 'add'} customer`);
        });
}

// Delete customer
function deleteCustomer(customerId) {
    // Check if customer has vehicles
    const customerVehicles = vehicles.filter(v => v.customer_id === parseInt(customerId));
    if (customerVehicles.length > 0) {
        showToast('Error', 'Cannot delete customer with associated vehicles');
        return;
    }

    if (confirm('Are you sure you want to delete this customer?')) {
        fetch(`/api/customers/${customerId}`, {
            method: 'DELETE'
        })
            .then(response => response.json())
            .then(data => {
                showToast('Success', 'Customer deleted successfully');
                loadCustomers();
                if (currentPage === 'dashboard') {
                    loadDashboard();
                }
            })
            .catch(error => {
                console.error('Error deleting customer:', error);
                showToast('Error', 'Failed to delete customer');
            });
    }
}

// Load reminders
function loadReminders() {
    fetch('/api/reminders/')
        .then(response => response.json())
        .then(data => {
            reminders = data;
            renderRemindersTable(data);
        })
        .catch(error => {
            console.error('Error loading reminders:', error);
            showToast('Error', 'Failed to load reminders');
        });
}

// Render reminders table
function renderRemindersTable(reminders) {
    const tableBody = document.getElementById('reminders-table');
    tableBody.innerHTML = '';

    if (reminders.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = '<td colspan="5" class="text-center">No reminders found</td>';
        tableBody.appendChild(row);
        return;
    }

    reminders.forEach(reminder => {
        const row = document.createElement('tr');

        // Find vehicle and customer
        let vehicleText = '';
        let customerText = '';

        const vehicle = vehicles.find(v => v.id === reminder.vehicle_id);
        if (vehicle) {
            vehicleText = `${vehicle.registration} (${vehicle.make || ''} ${vehicle.model || ''})`;

            if (vehicle.customer_id) {
                const customer = customers.find(c => c.id === vehicle.customer_id);
                if (customer) {
                    customerText = customer.name;
                }
            }
        }

        row.innerHTML = `
            <td>${vehicleText}</td>
            <td>${customerText}</td>
            <td>${reminder.reminder_date ? new Date(reminder.reminder_date).toLocaleDateString() : ''}</td>
            <td>
                <span class="badge ${getReminderStatusBadgeClass(reminder.status)}">
                    ${reminder.status}
                </span>
            </td>
            <td>
                <button class="btn btn-sm btn-primary edit-reminder-btn" data-id="${reminder.id}">
                    <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-danger delete-reminder-btn" data-id="${reminder.id}">
                    <i class="bi bi-trash"></i>
                </button>
                ${reminder.status === 'scheduled' ? `
                <button class="btn btn-sm btn-success process-single-reminder-btn" data-id="${reminder.id}">
                    <i class="bi bi-envelope"></i>
                </button>
                ` : ''}
            </td>
        `;

        tableBody.appendChild(row);
    });

    // Add event listeners to buttons
    document.querySelectorAll('.edit-reminder-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const reminderId = this.getAttribute('data-id');
            showReminderModal(reminderId);
        });
    });

    document.querySelectorAll('.delete-reminder-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const reminderId = this.getAttribute('data-id');
            deleteReminder(reminderId);
        });
    });

    document.querySelectorAll('.process-single-reminder-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const reminderId = this.getAttribute('data-id');
            processSingleReminder(reminderId);
        });
    });
}

// Get reminder status badge class
function getReminderStatusBadgeClass(status) {
    switch(status) {
        case 'scheduled':
            return 'bg-warning';
        case 'sent':
            return 'bg-success';
        case 'failed':
            return 'bg-danger';
        default:
            return 'bg-secondary';
    }
}

// Show reminder modal
function showReminderModal(reminderId = null, preselectedVehicleId = null) {
    const modal = new bootstrap.Modal(document.getElementById('reminder-modal'));
    const modalTitle = document.getElementById('reminder-modal-title');
    const form = document.getElementById('reminder-form');

    // Reset form
    form.reset();
    document.getElementById('reminder-id').value = '';

    // Load vehicles for dropdown
    const vehicleSelect = document.getElementById('reminder-vehicle');
    vehicleSelect.innerHTML = '<option value="">Select Vehicle</option>';
    vehicles.forEach(vehicle => {
        const option = document.createElement('option');
        option.value = vehicle.id;

        // Add customer name if available
        let vehicleText = vehicle.registration;
        if (vehicle.make || vehicle.model) {
            vehicleText += ` (${vehicle.make || ''} ${vehicle.model || ''})`;
        }

        if (vehicle.customer_id) {
            const customer = customers.find(c => c.id === vehicle.customer_id);
            if (customer) {
                vehicleText += ` - ${customer.name}`;
            }
        }

        option.textContent = vehicleText;
        vehicleSelect.appendChild(option);
    });

    if (reminderId) {
        // Edit mode
        modalTitle.textContent = 'Edit Reminder';
        const reminder = reminders.find(r => r.id === parseInt(reminderId));
        if (reminder) {
            document.getElementById('reminder-id').value = reminder.id;
            document.getElementById('reminder-vehicle').value = reminder.vehicle_id;
            if (reminder.reminder_date) {
                document.getElementById('reminder-date').value = reminder.reminder_date.split('T')[0];
            }
            document.getElementById('reminder-status').value = reminder.status;
        }
    } else {
        // Add mode
        modalTitle.textContent = 'Add Reminder';
        document.getElementById('reminder-status').value = 'scheduled';

        // Set default date to today
        const today = new Date();
        const yyyy = today.getFullYear();
        const mm = String(today.getMonth() + 1).padStart(2, '0');
        const dd = String(today.getDate()).padStart(2, '0');
        document.getElementById('reminder-date').value = `${yyyy}-${mm}-${dd}`;

        // Preselect vehicle if provided
        if (preselectedVehicleId) {
            document.getElementById('reminder-vehicle').value = preselectedVehicleId;
        }
    }

    modal.show();
}

// Save reminder
function saveReminder() {
    const reminderId = document.getElementById('reminder-id').value;
    const vehicleId = document.getElementById('reminder-vehicle').value;
    const reminderDate = document.getElementById('reminder-date').value;
    const status = document.getElementById('reminder-status').value;

    if (!vehicleId) {
        showToast('Error', 'Vehicle is required');
        return;
    }

    if (!reminderDate) {
        showToast('Error', 'Reminder date is required');
        return;
    }

    const reminderData = {
        vehicle_id: parseInt(vehicleId),
        reminder_date: reminderDate,
        status: status
    };

    const url = reminderId ? `/api/reminders/${reminderId}` : '/api/reminders/';
    const method = reminderId ? 'PUT' : 'POST';

    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(reminderData)
    })
        .then(response => response.json())
        .then(data => {
            showToast('Success', `Reminder ${reminderId ? 'updated' : 'added'} successfully`);
            bootstrap.Modal.getInstance(document.getElementById('reminder-modal')).hide();
            loadReminders();
            if (currentPage === 'dashboard') {
                loadDashboard();
            }
        })
        .catch(error => {
            console.error('Error saving reminder:', error);
            showToast('Error', `Failed to ${reminderId ? 'update' : 'add'} reminder`);
        });
}

// Delete reminder
function deleteReminder(reminderId) {
    if (confirm('Are you sure you want to delete this reminder?')) {
        fetch(`/api/reminders/${reminderId}`, {
            method: 'DELETE'
        })
            .then(response => response.json())
            .then(data => {
                showToast('Success', 'Reminder deleted successfully');
                loadReminders();
                if (currentPage === 'dashboard') {
                    loadDashboard();
                }
            })
            .catch(error => {
                console.error('Error deleting reminder:', error);
                showToast('Error', 'Failed to delete reminder');
            });
    }
}

// Load settings
function loadSettings() {
    // Load email and SMS settings
    fetch('/api/users/settings')
        .then(response => response.json())
        .then(data => {
            // Email settings
            if (data.email) {
                document.getElementById('smtp-server').value = data.email.smtp_server || '';
                document.getElementById('smtp-port').value = data.email.smtp_port || '';
                document.getElementById('smtp-username').value = data.email.smtp_username || '';
                document.getElementById('sender-email').value = data.email.sender_email || '';
            }

            // SMS settings
            if (data.sms) {
                document.getElementById('sms-api-url').value = data.sms.api_url || '';
                document.getElementById('sms-sender-id').value = data.sms.sender_id || '';
            }
        })
        .catch(error => {
            console.error('Error loading settings:', error);
            showToast('Error', 'Failed to load settings');
        });

    // Load email template
    fetch('/api/reminders/templates/email')
        .then(response => response.json())
        .then(data => {
            document.getElementById('email-template').value = data.template || '';
        })
        .catch(error => {
            console.error('Error loading email template:', error);
            showToast('Error', 'Failed to load email template');
        });

    // Load SMS template
    fetch('/api/reminders/templates/sms')
        .then(response => response.json())
        .then(data => {
            document.getElementById('sms-template').value = data.template || '';
        })
        .catch(error => {
            console.error('Error loading SMS template:', error);
            showToast('Error', 'Failed to load SMS template');
        });
}

// Save email settings
function saveEmailSettings(e) {
    e.preventDefault();

    const emailSettings = {
        smtp_server: document.getElementById('smtp-server').value,
        smtp_port: parseInt(document.getElementById('smtp-port').value),
        smtp_username: document.getElementById('smtp-username').value,
        smtp_password: document.getElementById('smtp-password').value,
        sender_email: document.getElementById('sender-email').value
    };

    fetch('/api/users/settings/email', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(emailSettings)
    })
        .then(response => response.json())
        .then(data => {
            showToast('Success', 'Email settings saved successfully');
        })
        .catch(error => {
            console.error('Error saving email settings:', error);
            showToast('Error', 'Failed to save email settings');
        });
}

// Save SMS settings
function saveSmsSettings(e) {
    e.preventDefault();

    const smsSettings = {
        api_url: document.getElementById('sms-api-url').value,
        api_key: document.getElementById('sms-api-key').value,
        sender_id: document.getElementById('sms-sender-id').value
    };

    fetch('/api/users/settings/sms', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(smsSettings)
    })
        .then(response => response.json())
        .then(data => {
            showToast('Success', 'SMS settings saved successfully');
        })
        .catch(error => {
            console.error('Error saving SMS settings:', error);
            showToast('Error', 'Failed to save SMS settings');
        });
}

// Save email template
function saveEmailTemplate(e) {
    e.preventDefault();

    const template = document.getElementById('email-template').value;

    fetch('/api/reminders/templates/email', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ template: template })
    })
        .then(response => response.json())
        .then(data => {
            showToast('Success', 'Email template saved successfully');
        })
        .catch(error => {
            console.error('Error saving email template:', error);
            showToast('Error', 'Failed to save email template');
        });
}

// Save SMS template
function saveSmsTemplate(e) {
    e.preventDefault();

    const template = document.getElementById('sms-template').value;

    fetch('/api/reminders/templates/sms', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ template: template })
    })
        .then(response => response.json())
        .then(data => {
            showToast('Success', 'SMS template saved successfully');
        })
        .catch(error => {
            console.error('Error saving SMS template:', error);
            showToast('Error', 'Failed to save SMS template');
        });
}

// Save DVLA settings
function saveDvlaSettings(e) {
    e.preventDefault();

    const dvlaSettings = {
        client_id: document.getElementById('dvla-client-id').value,
        client_secret: document.getElementById('dvla-client-secret').value,
        api_key: document.getElementById('dvla-api-key').value
    };

    // In a real implementation, this would save to database or environment variables
    showToast('Success', 'DVLA settings saved successfully');
}

// Show toast notification with AI styling
function showToast(title, message, type = 'info') {
    const toastEl = document.getElementById('toast');
    const toastTitle = document.getElementById('toast-title');
    const toastMessage = document.getElementById('toast-message');

    // Add AI prefix and styling
    toastTitle.innerHTML = `<i class="fas fa-robot"></i> AI Assistant`;
    toastMessage.innerHTML = `<strong>${title}:</strong> ${message}`;

    // Add type-specific styling
    toastEl.className = `toast ai-toast-${type.toLowerCase()}`;

    const toast = new bootstrap.Toast(toastEl);
    toast.show();
}

// OCR Image Upload Functions
function setupOCRUpload() {
    const uploadBtn = document.getElementById('upload-image-btn');
    const fileInput = document.getElementById('ocr-image-upload');

    if (uploadBtn && fileInput) {
        uploadBtn.addEventListener('click', () => {
            fileInput.click();
        });

        fileInput.addEventListener('change', handleOCRImageUpload);
    }
}

function handleOCRImageUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    // Show loading state
    const uploadBtn = document.getElementById('upload-image-btn');
    const originalText = uploadBtn.innerHTML;
    uploadBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Processing...';
    uploadBtn.disabled = true;

    fetch('/api/vehicles/ocr/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showToast('Error', data.error);
        } else {
            handleOCRResults(data);
        }
    })
    .catch(error => {
        console.error('Error uploading image:', error);
        showToast('Error', 'Failed to process image');
    })
    .finally(() => {
        // Restore button state
        uploadBtn.innerHTML = originalText;
        uploadBtn.disabled = false;
        // Clear file input
        event.target.value = '';
    });
}

function handleOCRResults(data) {
    if (data.verified_registrations && data.verified_registrations.length > 0) {
        // Use the first verified registration
        const registration = data.verified_registrations[0];
        document.getElementById('vehicle-registration').value = registration;

        // If we have vehicle data, populate the form
        if (data.best_match && data.best_match.vehicle_data) {
            const vehicleData = data.best_match.vehicle_data;
            document.getElementById('vehicle-make').value = vehicleData.make || '';
            document.getElementById('vehicle-model').value = vehicleData.model || '';
            document.getElementById('vehicle-color').value = vehicleData.primaryColour || '';
            document.getElementById('vehicle-year').value = vehicleData.yearOfManufacture || '';

            if (vehicleData.motExpiryDate) {
                document.getElementById('vehicle-mot-expiry').value = vehicleData.motExpiryDate.split('T')[0];
            }
        }

        showToast('Success', `Registration ${registration} extracted and verified!`);
    } else if (data.potential_registrations && data.potential_registrations.length > 0) {
        // Show potential registrations for user to choose
        const registration = data.potential_registrations[0];
        document.getElementById('vehicle-registration').value = registration;
        showToast('Warning', `Registration ${registration} extracted but not verified. Please check manually.`);
    } else {
        showToast('Warning', 'No registration numbers found in the image. Please try a clearer image or enter manually.');
    }
}

// CSV Upload Functions
function setupCSVUpload() {
    const uploadBtn = document.getElementById('upload-csv-btn');
    const cancelBtn = document.getElementById('cancel-csv-btn');
    const processBtn = document.getElementById('process-csv-btn');
    const downloadBtn = document.getElementById('download-template-btn');
    const uploadSection = document.getElementById('csv-upload-section');
    const fileInput = document.getElementById('csv-file-input');

    if (uploadBtn) {
        uploadBtn.addEventListener('click', () => {
            uploadSection.style.display = 'block';
        });
    }

    if (cancelBtn) {
        cancelBtn.addEventListener('click', () => {
            uploadSection.style.display = 'none';
            fileInput.value = '';
        });
    }

    if (processBtn) {
        processBtn.addEventListener('click', handleCSVUpload);
    }

    // Handle both CSV and Excel template downloads
    const downloadCSVBtn = document.getElementById('download-csv-template');
    const downloadExcelBtn = document.getElementById('download-excel-template');

    if (downloadCSVBtn) {
        downloadCSVBtn.addEventListener('click', (e) => {
            e.preventDefault();
            downloadCSVTemplate();
        });
    }

    if (downloadExcelBtn) {
        downloadExcelBtn.addEventListener('click', (e) => {
            e.preventDefault();
            downloadExcelTemplate();
        });
    }
}

function handleCSVUpload() {
    const fileInput = document.getElementById('csv-file-input');
    const file = fileInput.files[0];

    if (!file) {
        showToast('Error', 'Please select a file');
        return;
    }

    const fileName = file.name.toLowerCase();
    const isExcel = fileName.endsWith('.xlsx') || fileName.endsWith('.xls');
    const isCSV = fileName.endsWith('.csv');

    if (!isExcel && !isCSV) {
        showToast('Error', 'Please select a CSV or Excel file');
        return;
    }

    if (isExcel) {
        handleExcelFile(file);
    } else {
        handleCSVFile(file);
    }
}

function handleCSVFile(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        const csv = e.target.result;
        processFileData(csv, 'csv');
    };
    reader.readAsText(file);
}

function handleExcelFile(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            const data = new Uint8Array(e.target.result);
            const workbook = XLSX.read(data, { type: 'array' });

            // Get the first worksheet
            const firstSheetName = workbook.SheetNames[0];
            const worksheet = workbook.Sheets[firstSheetName];

            // Convert to CSV format
            const csv = XLSX.utils.sheet_to_csv(worksheet);

            processFileData(csv, 'excel');
        } catch (error) {
            console.error('Error reading Excel file:', error);
            showToast('Error', 'Failed to read Excel file. Please check the file format.');
        }
    };
    reader.readAsArrayBuffer(file);
}

function processFileData(fileContent, fileType) {
    const lines = fileContent.split('\n');
    if (lines.length < 2) {
        showToast('Error', `${fileType.toUpperCase()} file must have at least a header row and one data row`);
        return;
    }

    // Filter out comment lines (starting with #)
    const dataLines = lines.filter(line => !line.trim().startsWith('#'));

    if (dataLines.length < 2) {
        showToast('Error', `${fileType.toUpperCase()} file must have at least a header row and one data row`);
        return;
    }

    // Parse headers and normalize them
    const rawHeaders = dataLines[0].split(',').map(h => h.trim());
    const headers = rawHeaders.map(h => {
        const normalized = h.toLowerCase().replace(/\s+/g, '_');
        // Map your specific column names to standard names
        if (normalized === 'work_due') return 'work_due';
        if (normalized === 'customer') return 'customer';
        if (normalized === 'make') return 'make';
        if (normalized === 'registration') return 'registration';
        return normalized;
    });

    console.log('Raw headers:', rawHeaders);
    console.log('Normalized headers:', headers);

    const requiredHeaders = ['registration'];

    // Check for required headers
    const missingHeaders = requiredHeaders.filter(h => !headers.includes(h));
    if (missingHeaders.length > 0) {
        showToast('Error', `Missing required columns: ${missingHeaders.join(', ')}`);
        return;
    }

    const processBtn = document.getElementById('process-csv-btn');
    processBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Processing with DVLA lookup...';
    processBtn.disabled = true;

    // Parse file data
    const fileData = [];
    for (let i = 1; i < dataLines.length; i++) {
        const line = dataLines[i].trim();
        if (!line) continue;

        const values = line.split(',').map(v => v.trim());
        const rowData = {};

        headers.forEach((header, index) => {
            rowData[header] = values[index] || '';
        });

        if (rowData.registration) {
            fileData.push(rowData);
        }
    }

    // Send to enhanced backend endpoint
    fetch('/api/vehicles/csv/upload', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            csv_data: fileData,
            file_type: fileType
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showToast('Error', data.error);
            return;
        }

        // Show detailed results
        showFileResults(data, fileType);

        // Refresh the vehicles list
        loadVehicles();

        // Hide upload section
        document.getElementById('csv-upload-section').style.display = 'none';
        document.getElementById('csv-file-input').value = '';

        // Redirect to reminders review if batch_id is provided
        if (data.batch_id && data.redirect_to_review) {
            setTimeout(() => {
                showRemindersReview(data.batch_id);
            }, 2000); // Show results for 2 seconds, then redirect
        }
    })
    .catch(error => {
        console.error(`Error processing ${fileType} file:`, error);
        showToast('Error', `Failed to process ${fileType.toUpperCase()} file`);
    })
    .finally(() => {
        processBtn.innerHTML = 'Process File';
        processBtn.disabled = false;
    });
}

function showFileResults(data, fileType = 'file') {
    const { processed, errors, vehicles_created, customers_created, dvla_lookups, reminders_created } = data;

    // Count created vs updated vehicles
    const createdVehicles = vehicles_created.filter(v => !v.action || v.action === 'created').length;
    const updatedVehicles = vehicles_created.filter(v => v.action === 'updated').length;

    // Create detailed message
    let message = `Successfully processed ${processed} vehicles from ${fileType.toUpperCase()} file.`;

    if (createdVehicles > 0) {
        message += ` Created ${createdVehicles} new vehicles.`;
    }

    if (updatedVehicles > 0) {
        message += ` Updated ${updatedVehicles} existing vehicles.`;
    }

    if (customers_created.length > 0) {
        message += ` Created ${customers_created.length} new customers.`;
    }

    // Add reminder creation info
    if (reminders_created && reminders_created > 0) {
        message += ` Created ${reminders_created} reminders for vehicles needing MOT attention.`;
    }

    // Count DVLA lookups
    const dvlaFound = dvla_lookups.filter(lookup => lookup.dvla_found).length;
    const dvlaNotFound = dvla_lookups.filter(lookup => !lookup.dvla_found).length;

    if (dvlaFound > 0) {
        message += ` ${dvlaFound} vehicles verified with DVLA data.`;
    }

    if (dvlaNotFound > 0) {
        message += ` ${dvlaNotFound} vehicles used ${fileType.toUpperCase()} data only (not found in DVLA).`;
    }

    if (errors.length > 0) {
        message += ` ${errors.length} errors occurred.`;
        console.error(`${fileType.toUpperCase()} processing errors:`, errors);
    }

    // Show toast with appropriate type
    const toastType = errors.length > 0 ? 'Warning' : 'Success';
    showToast(toastType, message);

    // Show detailed results modal
    showFileResultsModal(data, fileType);

    // Log detailed results for debugging
    console.log(`${fileType.toUpperCase()} Upload Results:`, {
        processed,
        errors,
        vehicles_created,
        customers_created,
        dvla_lookups,
        reminders_created,
        createdVehicles,
        updatedVehicles
    });
}

// Keep backward compatibility
function showCSVResults(data) {
    showFileResults(data, 'csv');
}

function showFileResultsModal(data, fileType = 'file') {
    const { processed, errors, vehicles_created, customers_created, dvla_lookups } = data;
    const modal = new bootstrap.Modal(document.getElementById('csv-results-modal'));
    const content = document.getElementById('csv-results-content');

    // Update modal title
    const modalTitle = document.querySelector('#csv-results-modal .modal-title');
    modalTitle.textContent = `${fileType.toUpperCase()} Upload Results`;

    // Count DVLA lookups and vehicle actions
    const dvlaFound = dvla_lookups.filter(lookup => lookup.dvla_found).length;
    const dvlaNotFound = dvla_lookups.filter(lookup => !lookup.dvla_found).length;
    const createdVehicles = vehicles_created.filter(v => !v.action || v.action === 'created').length;
    const updatedVehicles = vehicles_created.filter(v => v.action === 'updated').length;

    let html = `
        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h6 class="mb-0">Summary</h6>
                    </div>
                    <div class="card-body">
                        <ul class="list-unstyled mb-0">
                            <li><strong>Vehicles Processed:</strong> ${processed}</li>
                            <li><strong>Vehicles Created:</strong> <span class="badge bg-success">${createdVehicles}</span></li>
                            <li><strong>Vehicles Updated:</strong> <span class="badge bg-info">${updatedVehicles}</span></li>
                            <li><strong>Customers Created:</strong> ${customers_created.length}</li>
                            <li><strong>DVLA Verified:</strong> ${dvlaFound}</li>
                            <li><strong>${fileType.toUpperCase()} Data Only:</strong> ${dvlaNotFound}</li>
                            <li><strong>Errors:</strong> <span class="badge bg-danger">${errors.length}</span></li>
                        </ul>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h6 class="mb-0">DVLA Lookup Status</h6>
                    </div>
                    <div class="card-body">
                        <div class="progress mb-2">
                            <div class="progress-bar bg-success" style="width: ${(dvlaFound / dvla_lookups.length * 100)}%"></div>
                            <div class="progress-bar bg-warning" style="width: ${(dvlaNotFound / dvla_lookups.length * 100)}%"></div>
                        </div>
                        <small class="text-muted">
                            <span class="badge bg-success">${dvlaFound} Found</span>
                            <span class="badge bg-warning">${dvlaNotFound} Not Found</span>
                        </small>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Show DVLA lookup details
    if (dvla_lookups.length > 0) {
        html += `
            <div class="mt-4">
                <h6>DVLA Lookup Details</h6>
                <div class="table-responsive">
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>Registration</th>
                                <th>Action</th>
                                <th>DVLA Status</th>
                                <th>Make/Model</th>
                                <th>Year</th>
                                <th>Color</th>
                                <th>MOT Expiry</th>
                            </tr>
                        </thead>
                        <tbody>
        `;

        dvla_lookups.forEach((lookup, index) => {
            const status = lookup.dvla_found ?
                '<span class="badge bg-success">Found</span>' :
                '<span class="badge bg-warning">Not Found</span>';

            // Determine action (created/updated) from vehicles_created array
            const vehicleInfo = vehicles_created[index];
            const action = vehicleInfo && vehicleInfo.action === 'updated' ?
                '<span class="badge bg-info">Updated</span>' :
                '<span class="badge bg-success">Created</span>';

            let makeModel = '';
            let year = '';
            let color = '';
            let motExpiry = '';

            if (lookup.dvla_found && lookup.dvla_data) {
                makeModel = `${lookup.dvla_data.make || ''} ${lookup.dvla_data.model || ''}`.trim();
                year = lookup.dvla_data.yearOfManufacture || '';
                color = lookup.dvla_data.primaryColour || '';
                motExpiry = lookup.dvla_data.motExpiryDate ?
                    new Date(lookup.dvla_data.motExpiryDate).toLocaleDateString() : '';
            } else if (lookup.csv_data) {
                makeModel = `${lookup.csv_data.make || ''} ${lookup.csv_data.model || ''}`.trim();
                year = lookup.csv_data.year || '';
                color = lookup.csv_data.color || '';
                motExpiry = lookup.csv_data.mot_expiry ?
                    new Date(lookup.csv_data.mot_expiry).toLocaleDateString() : '';
            }

            html += `
                <tr>
                    <td><strong>${lookup.registration}</strong></td>
                    <td>${action}</td>
                    <td>${status}</td>
                    <td>${makeModel}</td>
                    <td>${year}</td>
                    <td>${color}</td>
                    <td>${motExpiry}</td>
                </tr>
            `;
        });

        html += `
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }

    // Show errors if any
    if (errors.length > 0) {
        html += `
            <div class="mt-4">
                <h6 class="text-danger">Errors</h6>
                <div class="alert alert-danger">
                    <ul class="mb-0">
        `;

        errors.forEach(error => {
            html += `<li>${error}</li>`;
        });

        html += `
                    </ul>
                </div>
            </div>
        `;
    }

    content.innerHTML = html;
    modal.show();
}

// Backward compatibility
function showCSVResultsModal(data) {
    showFileResultsModal(data, 'csv');
}

function downloadCSVTemplate() {
    const csvContent = 'registration,make,model,color,year,mot_expiry,customer_name,customer_email,customer_phone\n' +
                      '# Enhanced CSV Template with DVLA Auto-Lookup\n' +
                      '# Only registration is required - all other fields are optional\n' +
                      '# System will automatically lookup vehicle details from DVLA database\n' +
                      '# DVLA data takes precedence over CSV data for accuracy\n' +
                      'AB12CDE,,,,,,John Smith,john@example.com,01234567890\n' +
                      'XY98ZAB,Toyota,Corolla,Red,2019,,Jane Doe,jane@example.com,09876543210\n' +
                      'CD34EFG,,,,,,,,\n' +
                      'GH56IJK,,,,,2024-12-31,Bob Wilson,bob@example.com,';

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'vehicle_template_enhanced.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

function downloadExcelTemplate() {
    // Create workbook and worksheet
    const wb = XLSX.utils.book_new();

    // Create data for the worksheet
    const data = [
        ['registration', 'make', 'model', 'color', 'year', 'mot_expiry', 'customer_name', 'customer_email', 'customer_phone'],
        ['AB12CDE', '', '', '', '', '', 'John Smith', 'john@example.com', '01234567890'],
        ['XY98ZAB', 'Toyota', 'Corolla', 'Red', '2019', '', 'Jane Doe', 'jane@example.com', '09876543210'],
        ['CD34EFG', '', '', '', '', '', '', '', ''],
        ['GH56IJK', '', '', '', '', '2024-12-31', 'Bob Wilson', 'bob@example.com', '']
    ];

    // Create worksheet
    const ws = XLSX.utils.aoa_to_sheet(data);

    // Set column widths
    ws['!cols'] = [
        { width: 12 }, // registration
        { width: 10 }, // make
        { width: 12 }, // model
        { width: 8 },  // color
        { width: 6 },  // year
        { width: 12 }, // mot_expiry
        { width: 15 }, // customer_name
        { width: 20 }, // customer_email
        { width: 15 }  // customer_phone
    ];

    // Add comments/notes
    if (!ws['!comments']) ws['!comments'] = [];

    // Add comment to the header row
    ws['A1'].c = [{
        a: 'System',
        t: 'Enhanced Excel Template with DVLA Auto-Lookup\n\n' +
           '• Only registration is required - all other fields are optional\n' +
           '• System will automatically lookup vehicle details from DVLA database\n' +
           '• DVLA data takes precedence over Excel data for accuracy\n' +
           '• Missing vehicle details will be auto-populated from DVLA'
    }];

    // Add worksheet to workbook
    XLSX.utils.book_append_sheet(wb, ws, 'Vehicles');

    // Create a second sheet with instructions
    const instructionsData = [
        ['Enhanced Vehicle Upload Template'],
        [''],
        ['Instructions:'],
        ['1. Only the "registration" column is required'],
        ['2. All other columns are optional'],
        ['3. The system will automatically lookup vehicle details from DVLA'],
        ['4. DVLA data takes precedence over your data for accuracy'],
        ['5. Missing details will be auto-populated from DVLA'],
        [''],
        ['Column Descriptions:'],
        ['registration - UK vehicle registration number (REQUIRED)'],
        ['make - Vehicle manufacturer (optional)'],
        ['model - Vehicle model (optional)'],
        ['color - Vehicle color (optional)'],
        ['year - Year of manufacture (optional)'],
        ['mot_expiry - MOT expiry date in YYYY-MM-DD format (optional)'],
        ['customer_name - Customer full name (optional)'],
        ['customer_email - Customer email address (optional)'],
        ['customer_phone - Customer phone number (optional)'],
        [''],
        ['Examples:'],
        ['AB12CDE - System will lookup all vehicle details from DVLA'],
        ['XY98ZAB with partial data - DVLA data will override your data'],
        ['CD34EFG with no customer - Vehicle will be created without customer'],
        ['GH56IJK with customer - Customer will be created or linked']
    ];

    const instructionsWs = XLSX.utils.aoa_to_sheet(instructionsData);
    instructionsWs['!cols'] = [{ width: 60 }];

    // Style the instructions sheet
    instructionsWs['A1'].s = {
        font: { bold: true, sz: 14 },
        fill: { fgColor: { rgb: "FFFF00" } }
    };

    XLSX.utils.book_append_sheet(wb, instructionsWs, 'Instructions');

    // Generate Excel file and download
    XLSX.writeFile(wb, 'vehicle_template_enhanced.xlsx');
}

// Enhanced Reminder Management Functions
function showRemindersReview(batchId) {
    // Switch to reminders page
    showPage('reminders');

    // Load review data
    fetch(`/api/reminders/review/${batchId}`)
        .then(response => response.json())
        .then(data => {
            displayRemindersReview(data);
        })
        .catch(error => {
            console.error('Error loading reminders review:', error);
            showToast('Error', 'Failed to load reminders for review');
        });
}

function displayRemindersReview(data) {
    const { vehicles_for_review, duplicates, batch_id } = data;

    // Show review mode message
    showToast('Info', `Review Mode: ${vehicles_for_review.length} vehicles need reminders, ${duplicates.length} duplicates found`);

    // Load all reminders with enhanced display
    loadRemindersEnhanced();

    // Highlight duplicates if any
    if (duplicates.length > 0) {
        setTimeout(() => {
            highlightDuplicates(duplicates);
        }, 1000);
    }
}

function loadRemindersEnhanced() {
    fetch('/api/reminders/')
        .then(response => response.json())
        .then(reminders => {
            console.log('Loaded reminders:', reminders);

            if (reminders.length === 0) {
                displayRemindersTable([], []);
                return;
            }

            // Get vehicle data for each reminder
            const vehiclePromises = reminders.map(reminder =>
                fetch(`/api/vehicles/${reminder.vehicle_id}`)
                    .then(r => {
                        if (!r.ok) {
                            console.warn(`Vehicle ${reminder.vehicle_id} not found`);
                            return null;
                        }
                        return r.json();
                    })
                    .catch(error => {
                        console.warn(`Error loading vehicle ${reminder.vehicle_id}:`, error);
                        return null;
                    })
            );

            Promise.all(vehiclePromises)
                .then(vehicles => {
                    // Filter out null vehicles
                    const validVehicles = vehicles.filter(v => v !== null);
                    console.log('Loaded vehicles:', validVehicles);

                    // Load customer data for vehicles that have customer_id
                    const customerPromises = validVehicles
                        .filter(vehicle => vehicle.customer_id)
                        .map(vehicle =>
                            fetch(`/api/customers/${vehicle.customer_id}`)
                                .then(response => {
                                    if (!response.ok) {
                                        console.warn(`Customer ${vehicle.customer_id} not found`);
                                        return null;
                                    }
                                    return response.json();
                                })
                                .then(customer => ({ vehicle_id: vehicle.id, customer }))
                                .catch(error => {
                                    console.warn(`Error loading customer ${vehicle.customer_id}:`, error);
                                    return null;
                                })
                        );

                    Promise.all(customerPromises)
                        .then(customerData => {
                            // Create customer map
                            const customerMap = {};
                            customerData.filter(c => c !== null).forEach(item => {
                                customerMap[item.vehicle_id] = item.customer;
                            });

                            // Add customer info to vehicles
                            validVehicles.forEach(vehicle => {
                                if (vehicle.customer_id && customerMap[vehicle.id]) {
                                    vehicle.customer_name = customerMap[vehicle.id].name;
                                } else {
                                    vehicle.customer_name = null;
                                }
                            });

                            displayRemindersTable(reminders, validVehicles);
                        })
                        .catch(error => {
                            console.error('Error loading customer data:', error);
                            // Still display reminders without customer info
                            displayRemindersTable(reminders, validVehicles);
                        });
                })
                .catch(error => {
                    console.error('Error loading vehicle data:', error);
                    displayRemindersTable(reminders, []);
                });
        })
        .catch(error => {
            console.error('Error loading reminders:', error);
            showToast('Error', 'Failed to load reminders');
        });
}

function displayRemindersTable(reminders, vehicles) {
    const tableBody = document.getElementById('reminders-table');

    if (!tableBody) {
        console.error('Reminders table body not found');
        return;
    }

    // Create a map of vehicle data for quick lookup
    const vehicleMap = {};
    vehicles.forEach(vehicle => {
        if (vehicle && vehicle.id) {
            vehicleMap[vehicle.id] = vehicle;
        }
    });

    console.log('Vehicle map:', vehicleMap);
    console.log('Reminders to display:', reminders);

    // Clear table
    tableBody.innerHTML = '';

    if (reminders.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td colspan="10" class="apple-empty-state" style="padding: var(--apple-spacing-xl);">
                <div class="apple-empty-state-icon">🔔</div>
                <div class="apple-empty-state-title">No Reminders Found</div>
                <div class="apple-empty-state-subtitle">Upload vehicles with MOT dates to create reminders automatically</div>
            </td>
        `;
        tableBody.appendChild(row);
        return;
    }

    // Filter reminders that have valid vehicles
    const validReminders = reminders.filter(reminder => {
        const vehicle = vehicleMap[reminder.vehicle_id];
        if (!vehicle) {
            console.warn(`No vehicle found for reminder ${reminder.id} (vehicle_id: ${reminder.vehicle_id})`);
            return false;
        }
        return true;
    });

    if (validReminders.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td colspan="10" class="apple-empty-state" style="padding: var(--apple-spacing-xl);">
                <div class="apple-empty-state-icon">⚠️</div>
                <div class="apple-empty-state-title">No Valid Reminders</div>
                <div class="apple-empty-state-subtitle">Vehicles may have been deleted. Try the DVLA cleanup to refresh data.</div>
            </td>
        `;
        tableBody.appendChild(row);
        return;
    }

    // Sort reminders by urgency (most urgent first)
    const sortedReminders = validReminders.sort((a, b) => {
        const vehicleA = vehicleMap[a.vehicle_id];
        const vehicleB = vehicleMap[b.vehicle_id];

        const daysA = vehicleA.days_until_mot_expiry || 999;
        const daysB = vehicleB.days_until_mot_expiry || 999;

        return daysA - daysB;
    });

    sortedReminders.forEach(reminder => {
        const vehicle = vehicleMap[reminder.vehicle_id];
        const row = createReminderRow(reminder, vehicle);
        tableBody.appendChild(row);
    });

    // Setup event listeners
    setupReminderEventListeners();

    console.log(`Displayed ${sortedReminders.length} reminders`);
}

function createReminderRow(reminder, vehicle) {
    const row = document.createElement('tr');
    const motStatus = vehicle.mot_status;
    const daysUntil = vehicle.days_until_mot_expiry;

    // Add urgency class to row
    row.classList.add(`urgency-${motStatus.urgency}`);

    // Format days display
    let daysDisplay = 'Unknown';
    let daysClass = '';

    if (daysUntil !== null) {
        if (daysUntil < 0) {
            daysDisplay = `${Math.abs(daysUntil)} days ago`;
            daysClass = 'apple-status-critical';
        } else if (daysUntil === 0) {
            daysDisplay = 'Today';
            daysClass = 'apple-status-critical';
        } else {
            daysDisplay = `${daysUntil} days`;
            if (daysUntil <= 7) daysClass = 'apple-status-critical';
            else if (daysUntil <= 30) daysClass = 'apple-status-high';
            else daysClass = 'apple-status-low';
        }
    }

    // Urgency badge
    const urgencyBadge = getUrgencyBadgeApple(motStatus.urgency);

    // Status badge
    const statusBadge = getStatusBadgeApple(reminder.status);

    row.innerHTML = `
        <td>
            <input type="checkbox" class="reminder-checkbox" value="${reminder.id}" style="margin: 0;">
        </td>
        <td class="clickable-cell registration-cell" data-reminder-id="${reminder.id}">${createNumberPlateWithDVLALink(vehicle.registration, 'small')}</td>
        <td class="clickable-cell" data-reminder-id="${reminder.id}">${trimVehicleInfo(vehicle.make, vehicle.model)}</td>
        <td class="clickable-cell date-cell" data-reminder-id="${reminder.id}">${formatDateUK(vehicle.mot_expiry)}</td>
        <td class="clickable-cell days-cell" data-reminder-id="${reminder.id}"><span class="${daysClass}">${daysDisplay}</span></td>
        <td class="clickable-cell" data-reminder-id="${reminder.id}">${urgencyBadge}</td>
        <td class="clickable-cell customer-cell" data-reminder-id="${reminder.id}">${trimCustomerName(vehicle.customer_name) || 'No customer'}</td>
        <td class="clickable-cell date-cell" data-reminder-id="${reminder.id}">${formatDateUK(reminder.reminder_date)}</td>
        <td class="clickable-cell status-cell" data-reminder-id="${reminder.id}">${statusBadge}</td>
        <td class="actions-cell">
            <div style="display: flex; gap: 4px; justify-content: center;">
                <button class="apple-btn apple-btn-secondary view-reminder-btn" data-id="${reminder.id}" title="View Details" style="padding: 6px 10px; min-height: auto;">
                    <i class="bi bi-eye"></i>
                </button>
                <button class="apple-btn apple-btn-success send-reminder-btn" data-id="${reminder.id}" title="Send Reminder" style="padding: 6px 10px; min-height: auto;">
                    <i class="bi bi-send"></i>
                </button>
                <button class="apple-btn apple-btn-warning archive-reminder-btn" data-id="${reminder.id}" title="Archive" style="padding: 6px 10px; min-height: auto;">
                    <i class="bi bi-archive"></i>
                </button>
                <button class="apple-btn apple-btn-danger delete-reminder-btn" data-id="${reminder.id}" title="Delete" style="padding: 6px 10px; min-height: auto;">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
        </td>
    `;

    return row;
}

function getUrgencyBadge(urgency) {
    const badges = {
        'critical': '<span class="badge bg-danger">Critical</span>',
        'high': '<span class="badge bg-warning">High</span>',
        'medium': '<span class="badge bg-info">Medium</span>',
        'low': '<span class="badge bg-success">Low</span>',
        'none': '<span class="badge bg-secondary">Unknown</span>'
    };
    return badges[urgency] || badges['none'];
}

function getStatusBadge(status) {
    const badges = {
        'scheduled': '<span class="badge bg-primary">Scheduled</span>',
        'sent': '<span class="badge bg-success">Sent</span>',
        'failed': '<span class="badge bg-danger">Failed</span>',
        'archived': '<span class="badge bg-secondary">Archived</span>'
    };
    return badges[status] || '<span class="badge bg-light">Unknown</span>';
}

function getUrgencyBadgeApple(urgency) {
    const badges = {
        'critical': '<span class="apple-badge apple-badge-danger">🔴 Critical</span>',
        'high': '<span class="apple-badge apple-badge-warning">🟠 High</span>',
        'medium': '<span class="apple-badge apple-badge-warning">🟡 Medium</span>',
        'low': '<span class="apple-badge apple-badge-success">🟢 Low</span>',
        'none': '<span class="apple-badge apple-badge-secondary">❓ Unknown</span>'
    };
    return badges[urgency] || badges['none'];
}

function getStatusBadgeApple(status) {
    const badges = {
        'scheduled': '<span class="apple-badge apple-badge-warning">📅 Scheduled</span>',
        'sent': '<span class="apple-badge apple-badge-success">✅ Sent</span>',
        'failed': '<span class="apple-badge apple-badge-danger">❌ Failed</span>',
        'archived': '<span class="apple-badge apple-badge-secondary">📁 Archived</span>'
    };
    return badges[status] || '<span class="apple-badge apple-badge-secondary">❓ Unknown</span>';
}

function setupReminderEventListeners() {
    // Select all checkbox
    const selectAllCheckbox = document.getElementById('select-all-reminders');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const checkboxes = document.querySelectorAll('.reminder-checkbox');
            checkboxes.forEach(cb => cb.checked = this.checked);
            updateBulkActionsVisibility();
        });
    }

    // Individual checkboxes
    document.querySelectorAll('.reminder-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', updateBulkActionsVisibility);
    });

    // Bulk action buttons
    document.getElementById('bulk-send-btn')?.addEventListener('click', () => performBulkAction('send'));
    document.getElementById('bulk-archive-btn')?.addEventListener('click', () => performBulkAction('archive'));
    document.getElementById('bulk-delete-btn')?.addEventListener('click', () => performBulkAction('delete'));
    document.getElementById('clear-selection-btn')?.addEventListener('click', clearSelection);

    // Individual action buttons
    document.querySelectorAll('.view-reminder-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const reminderId = e.target.closest('button').dataset.id;
            showReminderDetails(reminderId);
        });
    });

    document.querySelectorAll('.send-reminder-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const reminderId = e.target.closest('button').dataset.id;
            performBulkAction('send', [reminderId]);
        });
    });

    document.querySelectorAll('.archive-reminder-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const reminderId = e.target.closest('button').dataset.id;
            performBulkAction('archive', [reminderId]);
        });
    });

    document.querySelectorAll('.delete-reminder-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const reminderId = e.target.closest('button').dataset.id;
            if (confirm('Are you sure you want to delete this reminder?')) {
                performBulkAction('delete', [reminderId]);
            }
        });
    });

    // Clickable cells to show reminder details
    document.querySelectorAll('.clickable-cell').forEach(cell => {
        cell.addEventListener('click', (e) => {
            const reminderId = e.target.closest('td').dataset.reminderId;
            if (reminderId) {
                showReminderDetails(reminderId);
            }
        });

        // Add cursor pointer style
        cell.style.cursor = 'pointer';
        cell.title = 'Click to view reminder details';
    });

    // Filters and search
    document.getElementById('urgency-filter')?.addEventListener('change', applyFilters);
    document.getElementById('status-filter')?.addEventListener('change', applyFilters);
    document.getElementById('sort-by')?.addEventListener('change', applyFilters);
    document.getElementById('search-vehicles')?.addEventListener('input', applyFilters);
    document.getElementById('clear-search')?.addEventListener('click', clearSearch);

    // Clear all reminders button
    document.getElementById('clear-all-reminders-btn')?.addEventListener('click', clearAllReminders);

    // Cleanup invalid reminders button
    document.getElementById('cleanup-invalid-reminders-btn')?.addEventListener('click', cleanupInvalidReminders);
}

function updateBulkActionsVisibility() {
    const selectedCheckboxes = document.querySelectorAll('.reminder-checkbox:checked');
    const bulkActions = document.getElementById('bulk-actions');
    const selectedCount = document.getElementById('selected-count');

    if (selectedCheckboxes.length > 0) {
        bulkActions.style.display = 'block';
        selectedCount.textContent = `${selectedCheckboxes.length} selected`;
    } else {
        bulkActions.style.display = 'none';
    }
}

function performBulkAction(action, reminderIds = null) {
    if (!reminderIds) {
        const selectedCheckboxes = document.querySelectorAll('.reminder-checkbox:checked');
        reminderIds = Array.from(selectedCheckboxes).map(cb => cb.value);
    }

    if (reminderIds.length === 0) {
        showToast('Warning', 'No reminders selected');
        return;
    }

    // Confirm destructive actions
    if (action === 'delete' && !confirm(`Are you sure you want to delete ${reminderIds.length} reminder(s)?`)) {
        return;
    }

    fetch('/api/reminders/bulk-action', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            reminder_ids: reminderIds,
            action: action
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showToast('Error', data.error);
        } else {
            showToast('Success', data.message);
            loadRemindersEnhanced(); // Reload the table
            clearSelection();
        }
    })
    .catch(error => {
        console.error('Error performing bulk action:', error);
        showToast('Error', `Failed to ${action} reminders`);
    });
}

function clearSelection() {
    document.querySelectorAll('.reminder-checkbox').forEach(cb => cb.checked = false);
    document.getElementById('select-all-reminders').checked = false;
    updateBulkActionsVisibility();
}

function applyFilters() {
    const urgencyFilter = document.getElementById('urgency-filter').value;
    const statusFilter = document.getElementById('status-filter').value;
    const sortBy = document.getElementById('sort-by').value;
    const searchTerm = document.getElementById('search-vehicles').value.toLowerCase();

    const rows = document.querySelectorAll('#reminders-table tr');

    rows.forEach(row => {
        let show = true;

        // Apply urgency filter
        if (urgencyFilter && !row.classList.contains(`urgency-${urgencyFilter}`)) {
            show = false;
        }

        // Apply status filter
        if (statusFilter) {
            const statusBadge = row.querySelector('td:nth-child(9)');
            if (!statusBadge || !statusBadge.textContent.toLowerCase().includes(statusFilter)) {
                show = false;
            }
        }

        // Apply search filter
        if (searchTerm) {
            const rowText = row.textContent.toLowerCase();
            if (!rowText.includes(searchTerm)) {
                show = false;
            }
        }

        row.style.display = show ? '' : 'none';
    });

    // Apply sorting (simplified - would need more complex logic for full implementation)
    // This is a basic implementation
}

function clearSearch() {
    document.getElementById('search-vehicles').value = '';
    applyFilters();
}

function highlightDuplicates(duplicates) {
    duplicates.forEach(duplicate => {
        const vehicleId = duplicate.vehicle.id;
        const rows = document.querySelectorAll('#reminders-table tr');

        rows.forEach(row => {
            const checkbox = row.querySelector('.reminder-checkbox');
            if (checkbox && checkbox.dataset.vehicleId == vehicleId) {
                row.classList.add('table-warning');
                row.title = 'Duplicate reminder detected';
            }
        });
    });

    if (duplicates.length > 0) {
        showToast('Warning', `${duplicates.length} duplicate reminders found and highlighted`);
    }
}

function clearAllReminders() {
    if (!confirm('Are you sure you want to clear ALL reminders? This action cannot be undone.')) {
        return;
    }

    fetch('/api/reminders/clear-all', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showToast('Error', data.error);
        } else {
            showToast('Success', data.message);
            loadRemindersEnhanced(); // Reload the table
        }
    })
    .catch(error => {
        console.error('Error clearing reminders:', error);
        showToast('Error', 'Failed to clear reminders');
    });
}

// Cleanup invalid reminders with DVLA verification
function cleanupInvalidReminders() {
    if (!confirm('This will verify all reminders against DVLA data and remove any that are invalid (e.g., MOT not actually due). This may take a few minutes. Continue?')) {
        return;
    }

    const btn = document.getElementById('cleanup-invalid-reminders-btn');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Verifying with DVLA...';
    btn.disabled = true;

    fetch('/api/reminders/cleanup-invalid', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showToast('Error', data.error);
        } else {
            let message = `DVLA Cleanup Complete!\n\n`;
            message += `• Invalid reminders removed: ${data.invalid_reminders_removed}\n`;
            message += `• Vehicle MOT dates updated: ${data.vehicles_updated}\n`;
            message += `• New reminders created: ${data.new_reminders_created}\n`;
            if (data.dvla_errors > 0) {
                message += `• DVLA lookup errors: ${data.dvla_errors}`;
            }

            showToast('Success', message);
            loadReminders();

            // Also refresh dashboard if we're on it
            if (currentPage === 'dashboard') {
                loadDashboard();
            }
        }
    })
    .catch(error => {
        console.error('Error cleaning up reminders:', error);
        showToast('Error', 'Failed to cleanup reminders');
    })
    .finally(() => {
        btn.innerHTML = originalText;
        btn.disabled = false;
    });
}

function clearAllVehicles() {
    if (!confirm('Are you sure you want to clear ALL vehicles? This will also remove all related reminders. This action cannot be undone.')) {
        return;
    }

    fetch('/api/vehicles/clear-all', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showToast('Error', data.error);
        } else {
            showToast('Success', data.message);
            loadVehicles(); // Reload vehicles table
            loadRemindersEnhanced(); // Reload reminders as they may have been cleared too
            if (currentPage === 'dashboard') {
                loadDashboard(); // Refresh dashboard counts
            }
        }
    })
    .catch(error => {
        console.error('Error clearing vehicles:', error);
        showToast('Error', 'Failed to clear vehicles');
    });
}

// Show vehicle details modal
function showVehicleDetails(vehicleId) {
    fetch(`/api/vehicles/${vehicleId}/details`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showToast('Error', data.error);
                return;
            }

            populateVehicleDetailsModal(data);
            const modal = new bootstrap.Modal(document.getElementById('vehicle-details-modal'));
            modal.show();
        })
        .catch(error => {
            console.error('Error loading vehicle details:', error);
            showToast('Error', 'Failed to load vehicle details');
        });
}

// Populate vehicle details modal
function populateVehicleDetailsModal(data) {
    const { vehicle, customer, dvla_data, reminders } = data;

    // Set modal title with number plate styling
    document.getElementById('vehicle-details-title').innerHTML = `Vehicle Details - ${createNumberPlateWithDVLALink(vehicle.registration, 'normal')}`;

    // Fetch and display MOT history
    fetchMOTHistory(vehicle.registration).then(motData => {
        const motHistoryContainer = document.getElementById('vehicle-mot-history');
        if (motHistoryContainer) {
            motHistoryContainer.innerHTML = createMOTHistoryHTML(motData);
        }
    });

    // Populate vehicle information
    const vehicleInfo = document.getElementById('vehicle-info');
    vehicleInfo.innerHTML = `
        <div class="row">
            <div class="col-sm-4"><strong>Registration:</strong></div>
            <div class="col-sm-8">${createNumberPlateWithDVLALink(vehicle.registration, 'normal')}</div>
        </div>
        <div class="row">
            <div class="col-sm-4"><strong>Make:</strong></div>
            <div class="col-sm-8">${vehicle.make || 'Not set'}</div>
        </div>
        <div class="row">
            <div class="col-sm-4"><strong>Model:</strong></div>
            <div class="col-sm-8">${vehicle.model || 'Not set'}</div>
        </div>
        <div class="row">
            <div class="col-sm-4"><strong>Color:</strong></div>
            <div class="col-sm-8">${vehicle.color || 'Not set'}</div>
        </div>
        <div class="row">
            <div class="col-sm-4"><strong>Year:</strong></div>
            <div class="col-sm-8">${vehicle.year || 'Not set'}</div>
        </div>
        <div class="row">
            <div class="col-sm-4"><strong>MOT Expiry:</strong></div>
            <div class="col-sm-8">${vehicle.mot_expiry || 'Not set'}</div>
        </div>
        <div class="row">
            <div class="col-sm-4"><strong>Added:</strong></div>
            <div class="col-sm-8">${vehicle.created_at || 'Unknown'}</div>
        </div>
        <div class="row">
            <div class="col-sm-4"><strong>Last Updated:</strong></div>
            <div class="col-sm-8">${vehicle.updated_at || 'Unknown'}</div>
        </div>
    `;

    // Populate customer information
    const customerInfo = document.getElementById('customer-info');
    if (customer) {
        customerInfo.innerHTML = `
            <div class="row">
                <div class="col-sm-4"><strong>Name:</strong></div>
                <div class="col-sm-8">${customer.name}</div>
            </div>
            <div class="row">
                <div class="col-sm-4"><strong>Email:</strong></div>
                <div class="col-sm-8">${customer.email || 'Not provided'}</div>
            </div>
            <div class="row">
                <div class="col-sm-4"><strong>Phone:</strong></div>
                <div class="col-sm-8">${customer.phone || 'Not provided'}</div>
            </div>
        `;
    } else {
        customerInfo.innerHTML = '<p class="text-muted">No customer assigned to this vehicle.</p>';
    }

    // Populate DVLA information
    const dvlaInfo = document.getElementById('dvla-info');
    if (dvla_data) {
        dvlaInfo.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <div class="row">
                        <div class="col-sm-6"><strong>Make:</strong></div>
                        <div class="col-sm-6">${dvla_data.make || 'N/A'}</div>
                    </div>
                    <div class="row">
                        <div class="col-sm-6"><strong>Model:</strong></div>
                        <div class="col-sm-6">${dvla_data.model || 'N/A'}</div>
                    </div>
                    <div class="row">
                        <div class="col-sm-6"><strong>Colour:</strong></div>
                        <div class="col-sm-6">${dvla_data.colour || 'N/A'}</div>
                    </div>
                    <div class="row">
                        <div class="col-sm-6"><strong>Year:</strong></div>
                        <div class="col-sm-6">${dvla_data.year || 'N/A'}</div>
                    </div>
                    <div class="row">
                        <div class="col-sm-6"><strong>Fuel Type:</strong></div>
                        <div class="col-sm-6">${dvla_data.fuel_type || 'N/A'}</div>
                    </div>
                    <div class="row">
                        <div class="col-sm-6"><strong>Engine Capacity:</strong></div>
                        <div class="col-sm-6">${dvla_data.engine_capacity || 'N/A'}</div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="row">
                        <div class="col-sm-6"><strong>MOT Status:</strong></div>
                        <div class="col-sm-6">
                            <span class="badge ${getMOTStatusBadgeClass(dvla_data.mot_status)}">
                                ${dvla_data.mot_status || 'N/A'}
                            </span>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-sm-6"><strong>MOT Expiry:</strong></div>
                        <div class="col-sm-6">${formatDVLADate(dvla_data.mot_expiry) || 'N/A'}</div>
                    </div>
                    <div class="row">
                        <div class="col-sm-6"><strong>Last MOT Test:</strong></div>
                        <div class="col-sm-6">${formatDVLADate(dvla_data.mot_test_date) || 'N/A'}</div>
                    </div>
                    <div class="row">
                        <div class="col-sm-6"><strong>MOT Test Number:</strong></div>
                        <div class="col-sm-6">${dvla_data.mot_test_number || 'N/A'}</div>
                    </div>
                    <div class="row">
                        <div class="col-sm-6"><strong>Test Mileage:</strong></div>
                        <div class="col-sm-6">${dvla_data.mot_test_mileage ? dvla_data.mot_test_mileage.toLocaleString() + ' miles' : 'N/A'}</div>
                    </div>
                    <div class="row">
                        <div class="col-sm-6"><strong>CO2 Emissions:</strong></div>
                        <div class="col-sm-6">${dvla_data.co2_emissions ? dvla_data.co2_emissions + ' g/km' : 'N/A'}</div>
                    </div>
                    <div class="row">
                        <div class="col-sm-6"><strong>First Used:</strong></div>
                        <div class="col-sm-6">${formatDVLADate(dvla_data.first_used_date) || 'N/A'}</div>
                    </div>
                </div>
            </div>
        `;
    } else {
        dvlaInfo.innerHTML = '<p class="text-muted">DVLA data not available or could not be retrieved.</p>';
    }

    // Populate reminders table
    const remindersTable = document.getElementById('vehicle-reminders-table');
    if (reminders && reminders.length > 0) {
        remindersTable.innerHTML = reminders.map(reminder => `
            <tr>
                <td>${formatDateUK(reminder.reminder_date)}</td>
                <td>
                    <span class="badge ${getReminderStatusBadgeClass(reminder.status)}">
                        ${reminder.status}
                    </span>
                </td>
                <td>${formatDateUK(reminder.created_at)}</td>
                <td>${formatDateUK(reminder.sent_at)}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary edit-reminder-btn" data-id="${reminder.id}">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger delete-reminder-btn" data-id="${reminder.id}">
                        <i class="bi bi-trash"></i>
                    </button>
                    ${reminder.status === 'scheduled' ? `
                        <button class="btn btn-sm btn-outline-success send-reminder-btn" data-id="${reminder.id}">
                            <i class="bi bi-send"></i>
                        </button>
                    ` : ''}
                </td>
            </tr>
        `).join('');
    } else {
        remindersTable.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No reminders found for this vehicle.</td></tr>';
    }

    // Store vehicle ID for potential actions
    document.getElementById('edit-vehicle-from-details').setAttribute('data-vehicle-id', vehicle.id);
    document.getElementById('add-reminder-for-vehicle').setAttribute('data-vehicle-id', vehicle.id);
}

// Format DVLA date to DD-MM-YYYY
function formatDVLADate(dateString) {
    if (!dateString) return null;
    try {
        const date = new Date(dateString);
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const year = date.getFullYear();
        return `${day}-${month}-${year}`;
    } catch (error) {
        return dateString; // Return original if parsing fails
    }
}

// Get badge class for MOT status
function getMOTStatusBadgeClass(status) {
    if (!status) return 'bg-secondary';

    const statusLower = status.toLowerCase();
    if (statusLower.includes('pass') || statusLower.includes('valid')) {
        return 'bg-success';
    } else if (statusLower.includes('fail') || statusLower.includes('expired')) {
        return 'bg-danger';
    } else if (statusLower.includes('advisory')) {
        return 'bg-warning';
    } else {
        return 'bg-secondary';
    }
}

// Show reminder details modal
function showReminderDetails(reminderId) {
    fetch(`/api/reminders/${reminderId}/details`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showToast('Error', data.error);
                return;
            }

            populateReminderDetailsModal(data);
            const modal = new bootstrap.Modal(document.getElementById('reminder-details-modal'));
            modal.show();
        })
        .catch(error => {
            console.error('Error loading reminder details:', error);
            showToast('Error', 'Failed to load reminder details');
        });
}

// Populate reminder details modal
function populateReminderDetailsModal(data) {
    const { reminder, vehicle, customer, dvla_data } = data;

    // Set modal title with number plate styling
    document.getElementById('reminder-details-title').innerHTML = `Reminder Details - ${createNumberPlateWithDVLALink(vehicle.registration, 'normal')}`;

    // Fetch and display MOT history
    fetchMOTHistory(vehicle.registration).then(motData => {
        const motHistoryContainer = document.getElementById('reminder-mot-history');
        if (motHistoryContainer) {
            motHistoryContainer.innerHTML = createMOTHistoryHTML(motData);
        }
    });

    // Populate reminder information
    const reminderInfo = document.getElementById('reminder-details-info');
    const reminderDate = formatDateUK(reminder.reminder_date);
    const createdDate = formatDateUK(reminder.created_at);
    const sentDate = formatDateUK(reminder.sent_at);

    // Calculate days until/since MOT expiry
    let motExpiryInfo = '';
    if (vehicle.mot_expiry) {
        const today = new Date();
        const motDate = new Date(vehicle.mot_expiry);
        const diffTime = motDate - today;
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

        if (diffDays > 0) {
            motExpiryInfo = `<span class="text-warning"><strong>${diffDays} days until MOT expiry</strong></span>`;
        } else if (diffDays === 0) {
            motExpiryInfo = `<span class="text-danger"><strong>MOT expires TODAY</strong></span>`;
        } else {
            motExpiryInfo = `<span class="text-danger"><strong>MOT expired ${Math.abs(diffDays)} days ago</strong></span>`;
        }
    }

    reminderInfo.innerHTML = `
        <div class="row">
            <div class="col-md-3">
                <strong>Reminder Date:</strong><br>
                <span class="text-primary">${reminderDate}</span>
            </div>
            <div class="col-md-3">
                <strong>Status:</strong><br>
                <span class="badge ${getReminderStatusBadgeClass(reminder.status)}">${reminder.status}</span>
            </div>
            <div class="col-md-3">
                <strong>Created:</strong><br>
                ${createdDate}
            </div>
            <div class="col-md-3">
                <strong>Sent:</strong><br>
                ${sentDate}
            </div>
        </div>
        ${motExpiryInfo ? `<div class="row mt-3"><div class="col-12 text-center">${motExpiryInfo}</div></div>` : ''}
    `;

    // Populate vehicle information
    const vehicleInfo = document.getElementById('reminder-vehicle-info');

    // Determine which MOT expiry date to display (DVLA takes precedence)
    let motExpiryDisplay = '';
    let motExpiryClass = 'text-muted';

    if (dvla_data && dvla_data.motExpiryDate) {
        // Use DVLA MOT expiry date
        const dvlaMotExpiry = formatDateUK(dvla_data.motExpiryDate);
        const vehicleMotExpiry = formatDateUK(vehicle.mot_expiry);

        if (vehicleMotExpiry && dvlaMotExpiry !== vehicleMotExpiry) {
            // Dates differ - show both with warning and update button
            motExpiryDisplay = `
                <span class="text-success"><strong>${dvlaMotExpiry}</strong> (DVLA)</span><br>
                <small class="text-muted">Database: ${vehicleMotExpiry}</small>
                <br><small class="text-warning"><i class="fas fa-exclamation-triangle"></i> Dates differ - DVLA is authoritative</small>
                <br><button class="btn btn-sm btn-warning mt-1" onclick="updateVehicleMotFromDvla(${vehicle.id}, '${dvla_data.motExpiryDate}')">
                    <i class="fas fa-sync"></i> Update Database
                </button>
            `;
            motExpiryClass = '';
        } else {
            // Use DVLA date
            motExpiryDisplay = `<span class="text-success"><strong>${dvlaMotExpiry}</strong> (DVLA verified)</span>`;
            motExpiryClass = '';
        }
    } else if (vehicle.mot_expiry) {
        // Use database MOT expiry date
        motExpiryDisplay = `<span class="text-warning">${formatDateUK(vehicle.mot_expiry)}</span><br><small class="text-muted">From database - not DVLA verified</small>`;
        motExpiryClass = '';
    } else {
        motExpiryDisplay = 'Not set';
    }

    vehicleInfo.innerHTML = `
        <div class="row mb-1">
            <div class="col-md-6">
                <strong>Registration:</strong><br>
                ${createNumberPlateWithDVLALink(vehicle.registration, 'small')}
            </div>
            <div class="col-md-6">
                <strong>MOT Expiry:</strong><br>
                <span class="${motExpiryClass}">${motExpiryDisplay}</span>
            </div>
        </div>
        <div class="row mb-1">
            <div class="col-md-6">
                <strong>Make:</strong><br>
                ${vehicle.make || 'Not specified'}
            </div>
            <div class="col-md-6">
                <strong>Model:</strong><br>
                ${vehicle.model || 'Not specified'}
            </div>
        </div>
        <div class="row mb-1">
            <div class="col-md-6">
                <strong>Color:</strong><br>
                ${vehicle.color || 'Not specified'}
            </div>
            <div class="col-md-6">
                <strong>Year:</strong><br>
                ${vehicle.year || 'Not specified'}
            </div>
        </div>
    `;

    // Populate customer information
    const customerInfo = document.getElementById('reminder-customer-info');
    if (customer) {
        customerInfo.innerHTML = `
            <div class="row mb-1">
                <div class="col-md-12">
                    <strong>Name:</strong><br>
                    <span class="text-primary fs-6">${customer.name}</span>
                </div>
            </div>
            <div class="row mb-1">
                <div class="col-md-6">
                    <strong>Phone:</strong><br>
                    <a href="tel:${customer.phone}" class="text-decoration-none">${customer.phone}</a>
                </div>
                <div class="col-md-6">
                    <strong>Email:</strong><br>
                    <a href="mailto:${customer.email}" class="text-decoration-none">${customer.email}</a>
                </div>
            </div>
            <div class="row mb-1">
                <div class="col-md-12">
                    <strong>Address:</strong><br>
                    ${customer.address || 'Not provided'}
                </div>
            </div>
        `;
    } else {
        customerInfo.innerHTML = '<p class="text-muted">No customer information available</p>';
    }

    // Populate DVLA information
    const dvlaInfo = document.getElementById('reminder-dvla-info');
    if (dvla_data && Object.keys(dvla_data).length > 0) {
        const motExpiry = dvla_data.motExpiryDate ? formatDVLADate(dvla_data.motExpiryDate) : 'Not available';
        const taxExpiry = dvla_data.taxDueDate ? formatDVLADate(dvla_data.taxDueDate) : 'Not available';

        dvlaInfo.innerHTML = `
            <div class="row mb-1">
                <div class="col-md-3">
                    <strong>Make:</strong><br>
                    ${dvla_data.make || 'Not available'}
                </div>
                <div class="col-md-3">
                    <strong>Model:</strong><br>
                    ${dvla_data.model || 'Not available'}
                </div>
                <div class="col-md-3">
                    <strong>Color:</strong><br>
                    ${dvla_data.colour || 'Not available'}
                </div>
                <div class="col-md-3">
                    <strong>Year:</strong><br>
                    ${dvla_data.yearOfManufacture || 'Not available'}
                </div>
            </div>
            <div class="row mb-1">
                <div class="col-md-3">
                    <strong>Engine Size:</strong><br>
                    ${dvla_data.engineCapacity || 'Not available'}
                </div>
                <div class="col-md-3">
                    <strong>Fuel Type:</strong><br>
                    ${dvla_data.fuelType || 'Not available'}
                </div>
                <div class="col-md-3">
                    <strong>MOT Status:</strong><br>
                    <span class="badge ${getMOTStatusBadgeClass(dvla_data.motStatus)}">
                        ${dvla_data.motStatus || 'Unknown'}
                    </span>
                </div>
                <div class="col-md-3">
                    <strong>Tax Status:</strong><br>
                    <span class="badge ${dvla_data.taxStatus === 'Taxed' ? 'bg-success' : 'bg-danger'}">
                        ${dvla_data.taxStatus || 'Unknown'}
                    </span>
                </div>
            </div>
            <div class="row mb-1">
                <div class="col-md-6">
                    <strong>MOT Expiry:</strong><br>
                    <span class="text-warning">${motExpiry}</span>
                </div>
                <div class="col-md-6">
                    <strong>Tax Due:</strong><br>
                    <span class="text-info">${taxExpiry}</span>
                </div>
            </div>
        `;
    } else {
        dvlaInfo.innerHTML = '<p class="text-muted">DVLA data not available</p>';
    }

    // Store reminder ID for potential actions
    document.getElementById('edit-reminder-from-details').setAttribute('data-reminder-id', reminder.id);
    document.getElementById('send-reminder-from-details').setAttribute('data-reminder-id', reminder.id);
}

// Update vehicle MOT expiry date from DVLA data
function updateVehicleMotFromDvla(vehicleId, dvlaMotExpiry) {
    if (!confirm('Update the database MOT expiry date with the DVLA date? This will ensure accurate reminder scheduling.')) {
        return;
    }

    fetch(`/api/vehicles/${vehicleId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            mot_expiry: dvlaMotExpiry
        })
    })
    .then(response => response.json())
    .then(data => {
        showToast('Success', 'Vehicle MOT expiry date updated from DVLA data');
        // Refresh the modal to show updated information
        const currentReminderId = document.getElementById('edit-reminder-from-details').getAttribute('data-reminder-id');
        if (currentReminderId) {
            showReminderDetails(currentReminderId);
        }
        // Refresh reminders list if on reminders page
        if (currentPage === 'reminders') {
            loadReminders();
        }
    })
    .catch(error => {
        console.error('Error updating vehicle MOT expiry:', error);
        showToast('Error', 'Failed to update vehicle MOT expiry date');
    });
}

// Theme toggle functionality
function initializeThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    const body = document.body;
    const icon = themeToggle.querySelector('i');

    // Load saved theme preference
    const savedTheme = localStorage.getItem('theme') || 'dark';
    if (savedTheme === 'light') {
        body.classList.add('light-theme');
        icon.className = 'fas fa-moon';
    }

    // Theme toggle event listener
    themeToggle.addEventListener('click', function() {
        body.classList.toggle('light-theme');

        if (body.classList.contains('light-theme')) {
            icon.className = 'fas fa-moon';
            localStorage.setItem('theme', 'light');
        } else {
            icon.className = 'fas fa-sun';
            localStorage.setItem('theme', 'dark');
        }
    });
}

// Utility function to trim customer names for compact display
function trimCustomerName(customerName) {
    if (!customerName) return '';

    // Remove common prefixes
    let trimmed = customerName.replace(/^(Mr|Mrs|Ms|Dr|Miss)\s+/i, '');

    // Remove common suffixes
    trimmed = trimmed.replace(/\s+(Ltd|Limited|Inc|Corp|Company)$/i, '');

    // If still too long, truncate more aggressively
    if (trimmed.length > 12) {
        // Try to keep first name and first letter of last name
        const parts = trimmed.split(' ');
        if (parts.length > 1) {
            trimmed = parts[0] + ' ' + parts[1].charAt(0) + '.';
        } else {
            trimmed = trimmed.substring(0, 10) + '...';
        }
    }

    return trimmed;
}

// Utility function to trim vehicle info for compact display
function trimVehicleInfo(make, model) {
    if (!make && !model) return '';

    let info = '';

    // Shorten common make names
    const makeShortcuts = {
        'Mercedes-Benz': 'Merc',
        'Mercedes': 'Merc',
        'Volkswagen': 'VW',
        'Hyundai': 'Hyun',
        'Nissan': 'Niss',
        'Toyota': 'Toy',
        'Honda': 'Hon',
        'Ford': 'Ford'
    };

    if (make) {
        info += makeShortcuts[make] || make;
    }

    if (model) {
        if (info) info += ' ';
        // Truncate model if needed
        let shortModel = model;
        if (model.length > 6) {
            shortModel = model.substring(0, 5) + '.';
        }
        info += shortModel;
    }

    // Final truncation if still too long
    if (info.length > 12) {
        info = info.substring(0, 10) + '...';
    }

    return info;
}

// ===== JOB SHEETS FUNCTIONALITY =====

// Load job sheets
function loadJobSheets() {
    // Load analytics first
    loadJobSheetsAnalytics();

    // Load job sheets data
    fetch('/api/job-sheets/')
        .then(response => response.json())
        .then(data => {
            jobSheets = data.job_sheets || [];
            renderJobSheetsTable(jobSheets);
        })
        .catch(error => {
            console.error('Error loading job sheets:', error);
            showToast('Error', 'Failed to load job sheets');
        });
}

// Load job sheets analytics
function loadJobSheetsAnalytics() {
    fetch('/api/job-sheets/analytics')
        .then(response => response.json())
        .then(data => {
            document.getElementById('total-jobs-count').textContent = data.total_jobs || 0;
            document.getElementById('total-revenue').textContent = `£${(data.total_revenue || 0).toFixed(2)}`;
            document.getElementById('mot-jobs-count').textContent = data.mot_jobs || 0;
            document.getElementById('payment-rate').textContent = `${(data.payment_rate || 0).toFixed(1)}%`;
        })
        .catch(error => {
            console.error('Error loading analytics:', error);
        });
}

// Render job sheets table
function renderJobSheetsTable(jobSheets) {
    const tableBody = document.getElementById('job-sheets-table');
    tableBody.innerHTML = '';

    if (jobSheets.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td colspan="9" class="apple-empty-state" style="padding: var(--apple-spacing-lg);">
                <div class="apple-empty-state-icon">📄</div>
                <div class="apple-empty-state-title">No Job Sheets Found</div>
                <div class="apple-empty-state-subtitle">Upload job sheets to get started with analytics and tracking</div>
            </td>
        `;
        tableBody.appendChild(row);
        return;
    }

    jobSheets.forEach(jobSheet => {
        const row = document.createElement('tr');

        // Status badge
        const statusBadge = jobSheet.date_paid ?
            '<span class="apple-badge apple-badge-success">✅ Paid</span>' :
            '<span class="apple-badge apple-badge-warning">⏳ Unpaid</span>';

        // Link indicators
        const customerLink = jobSheet.linked_customer_id ?
            '<i class="fas fa-link text-success" title="Linked to customer"></i>' :
            '<i class="fas fa-unlink text-muted" title="Not linked"></i>';

        const vehicleLink = jobSheet.linked_vehicle_id ?
            '<i class="fas fa-link text-success" title="Linked to vehicle"></i>' :
            '<i class="fas fa-unlink text-muted" title="Not linked"></i>';

        const links = `${customerLink} ${vehicleLink}`;

        row.innerHTML = `
            <td>${jobSheet.doc_no}</td>
            <td class="date-cell">${formatDateUK(jobSheet.date_created)}</td>
            <td class="customer-cell">${trimCustomerName(jobSheet.customer_name) || 'No customer'}</td>
            <td>${trimVehicleInfo(jobSheet.make, jobSheet.model)}</td>
            <td class="registration-cell">${jobSheet.vehicle_reg ? createNumberPlateWithDVLALink(jobSheet.vehicle_reg, 'small') : 'N/A'}</td>
            <td style="font-weight: var(--apple-font-weight-semibold);">£${(jobSheet.grand_total || 0).toFixed(2)}</td>
            <td class="status-cell">${statusBadge}</td>
            <td style="text-align: center;">${links}</td>
            <td class="actions-cell">
                <button class="apple-btn apple-btn-secondary view-job-sheet-btn" data-id="${jobSheet.id}" title="View Details" style="padding: 6px 10px; min-height: auto;">
                    <i class="bi bi-eye"></i>
                </button>
            </td>
        `;

        tableBody.appendChild(row);
    });

    // Add event listeners for view buttons
    document.querySelectorAll('.view-job-sheet-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation(); // Prevent row click
            const jobSheetId = e.target.closest('button').dataset.id;
            showJobSheetDetails(jobSheetId);
        });
    });

    // Make table rows clickable (GA4 style)
    document.querySelectorAll('#job-sheets-table tr').forEach(row => {
        if (row.querySelector('.view-job-sheet-btn')) {
            row.style.cursor = 'pointer';
            row.classList.add('table-row-clickable');
            row.addEventListener('click', function(e) {
                // Don't trigger if clicking on buttons or links
                if (e.target.tagName === 'BUTTON' || e.target.tagName === 'I' || e.target.closest('button') || e.target.closest('a')) {
                    return;
                }
                const jobSheetId = this.querySelector('.view-job-sheet-btn').getAttribute('data-id');
                showJobSheetDetails(jobSheetId);
            });
        }
    });
}

// Setup job sheets upload
function setupJobSheetsUpload() {
    const processBtn = document.getElementById('process-job-sheets-btn');
    const fileInput = document.getElementById('job-sheets-file-input');

    if (processBtn && fileInput) {
        // Handle file selection display
        fileInput.addEventListener('change', handleFileSelection);

        processBtn.addEventListener('click', () => {
            const files = fileInput.files;
            if (!files || files.length === 0) {
                showToast('Error', 'Please select at least one file to upload');
                return;
            }

            uploadMultipleFiles(files);
        });
    }
}

// Handle file selection and display
function handleFileSelection(event) {
    const files = event.target.files;
    const filesList = document.getElementById('selected-files-list');
    const filesPreview = document.getElementById('files-preview');
    const clearBtn = document.getElementById('clear-files-btn');

    if (files.length > 0) {
        filesList.style.display = 'block';
        clearBtn.style.display = 'inline-block';

        let html = '';
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            const fileType = detectFileType(file.name);
            const icon = getFileTypeIcon(fileType);
            const size = formatFileSize(file.size);

            html += `
                <div class="d-flex justify-content-between align-items-center mb-2 p-2 border rounded">
                    <div>
                        <i class="${icon}"></i>
                        <strong>${file.name}</strong>
                        <span class="badge bg-secondary ms-2">${fileType}</span>
                    </div>
                    <div class="text-muted">${size}</div>
                </div>
            `;
        }

        filesPreview.innerHTML = html;
    } else {
        filesList.style.display = 'none';
        clearBtn.style.display = 'none';
    }
}

// Clear file selection
function clearFileSelection() {
    const fileInput = document.getElementById('job-sheets-file-input');
    const filesList = document.getElementById('selected-files-list');
    const clearBtn = document.getElementById('clear-files-btn');

    fileInput.value = '';
    filesList.style.display = 'none';
    clearBtn.style.display = 'none';
}

// Detect file type from filename
function detectFileType(filename) {
    const name = filename.toLowerCase();

    if (name.includes('customer')) return 'Customers';
    if (name.includes('vehicle') || name.includes('mot_due')) return 'Vehicles';
    if (name.includes('document') && !name.includes('summary')) return 'Job Sheets';
    if (name.includes('document_summary')) return 'Summary';
    if (name.includes('job_description')) return 'Job Details';
    if (name.includes('line_item')) return 'Line Items';
    if (name.includes('reminder')) return 'Reminders';

    return 'Data';
}

// Get icon for file type
function getFileTypeIcon(fileType) {
    switch (fileType) {
        case 'Customers': return 'fas fa-users text-primary';
        case 'Vehicles': return 'fas fa-car text-success';
        case 'Job Sheets': return 'fas fa-file-invoice text-warning';
        case 'Summary': return 'fas fa-chart-bar text-info';
        case 'Job Details': return 'fas fa-clipboard-list text-secondary';
        case 'Line Items': return 'fas fa-list text-dark';
        case 'Reminders': return 'fas fa-bell text-danger';
        default: return 'fas fa-file text-muted';
    }
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Upload multiple files
function uploadMultipleFiles(files) {
    const formData = new FormData();

    // Add all files to form data
    for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
    }

    // Add options
    const autoDvla = document.getElementById('auto-dvla-lookup').checked;
    const autoLink = document.getElementById('auto-link-data').checked;
    formData.append('auto_dvla_lookup', autoDvla);
    formData.append('auto_link_data', autoLink);

    // Show loading state
    const processBtn = document.getElementById('process-job-sheets-btn');
    const originalText = processBtn.textContent;
    const progressContainer = document.getElementById('upload-progress');
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');
    const progressPercentage = document.getElementById('progress-percentage');

    processBtn.textContent = 'Processing Files...';
    processBtn.disabled = true;
    progressContainer.style.display = 'block';

    // Simulate progress (since we can't get real progress from server)
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 90) progress = 90;

        progressBar.style.width = progress + '%';
        progressPercentage.textContent = Math.round(progress) + '%';
        progressText.textContent = `Processing ${files.length} files...`;
    }, 500);

    fetch('/api/job-sheets/upload-bulk', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        clearInterval(progressInterval);
        progressBar.style.width = '100%';
        progressPercentage.textContent = '100%';
        progressText.textContent = 'Complete!';

        // Show comprehensive results
        let message = `🎉 Bulk Upload Complete!\n\n`;
        message += `📁 Files processed: ${data.processed_files}/${data.total_files}\n`;

        if (data.customers_processed > 0) {
            message += `👥 Customers: ${data.customers_processed}\n`;
        }
        if (data.vehicles_processed > 0) {
            message += `🚗 Vehicles: ${data.vehicles_processed}\n`;
        }
        if (data.job_sheets_processed > 0) {
            message += `📋 Job Sheets: ${data.job_sheets_processed}\n`;
        }

        // Add DVLA lookup results if available
        if (data.dvla_lookups) {
            const dvla = data.dvla_lookups;
            message += `\n🔍 DVLA Lookup Results:\n`;
            message += `• Checked: ${dvla.checked} vehicles\n`;
            message += `• Found: ${dvla.found} in DVLA\n`;
            message += `• Created: ${dvla.created} new vehicles\n`;
            message += `• Updated: ${dvla.updated} existing vehicles\n`;

            if (dvla.errors && dvla.errors.length > 0) {
                message += `• Errors: ${dvla.errors.length} (check console)\n`;
                console.warn('DVLA lookup errors:', dvla.errors);
            }
        }

        // Add file-specific results
        if (data.file_results && data.file_results.length > 0) {
            message += `\n📄 File Details:\n`;
            data.file_results.forEach(result => {
                if (result.success) {
                    message += `✅ ${result.filename}: ${result.processed} records\n`;
                } else {
                    message += `❌ ${result.filename}: ${result.error}\n`;
                }
            });
        }

        if (data.errors && data.errors.length > 0) {
            message += `\n⚠️ Errors: ${data.errors.length} (check console)\n`;
            console.warn('Upload errors:', data.errors);
        }

        // Show results
        alert(message);
        showToast('Success', `Successfully processed ${data.processed_files} files with DVLA integration`);

        // Hide upload section and reload data
        document.getElementById('job-sheets-upload-section').style.display = 'none';
        clearFileSelection();
        loadJobSheets();

        // Also reload other pages to show new data
        if (currentPage === 'vehicles') {
            loadVehicles();
        } else if (currentPage === 'reminders') {
            loadRemindersEnhanced();
        } else if (currentPage === 'customers') {
            loadCustomers();
        }
    })
    .catch(error => {
        clearInterval(progressInterval);
        console.error('Error uploading files:', error);
        showToast('Error', 'Failed to upload files');
    })
    .finally(() => {
        // Restore button state
        processBtn.textContent = originalText;
        processBtn.disabled = false;

        // Hide progress after delay
        setTimeout(() => {
            progressContainer.style.display = 'none';
            progressBar.style.width = '0%';
        }, 2000);
    });
}

// Upload single job sheet file (legacy function)
function uploadJobSheets(file) {
    const formData = new FormData();
    formData.append('file', file);

    // Show loading state
    const processBtn = document.getElementById('process-job-sheets-btn');
    const originalText = processBtn.textContent;
    processBtn.textContent = 'Processing...';
    processBtn.disabled = true;

    fetch('/api/job-sheets/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        let message = `Successfully processed ${data.processed} job sheets. Created: ${data.created}, Updated: ${data.updated}`;

        // Add DVLA lookup results if available
        if (data.dvla_lookups) {
            const dvla = data.dvla_lookups;
            message += `\n\nDVLA Lookup Results:\n• Checked: ${dvla.checked} vehicles\n• Found: ${dvla.found} in DVLA\n• Created: ${dvla.created} new vehicles\n• Updated: ${dvla.updated} existing vehicles`;

            if (dvla.errors && dvla.errors.length > 0) {
                message += `\n• Errors: ${dvla.errors.length} (check console)`;
                console.warn('DVLA lookup errors:', dvla.errors);
            }
        }

        if (data.errors && data.errors.length > 0) {
            console.warn('Upload completed with errors:', data.errors);
            message += `\n\nUpload errors: ${data.errors.length} (check console)`;
        }

        // Show comprehensive results
        alert(message);
        showToast('Success', 'Job sheets processed successfully with DVLA lookup');

        // Hide upload section and reload data
        document.getElementById('job-sheets-upload-section').style.display = 'none';
        loadJobSheets();

        // Also reload vehicles and reminders to show new data
        if (currentPage === 'vehicles') {
            loadVehicles();
        } else if (currentPage === 'reminders') {
            loadRemindersEnhanced();
        }
    })
    .catch(error => {
        console.error('Error uploading job sheets:', error);
        showToast('Error', 'Failed to upload job sheets');
    })
    .finally(() => {
        // Restore button state
        processBtn.textContent = originalText;
        processBtn.disabled = false;
    });
}

// Link job data with existing customers and vehicles
function linkJobData() {
    const btn = document.getElementById('link-job-data-btn');
    const originalText = btn.textContent;
    btn.textContent = 'Linking...';
    btn.disabled = true;

    fetch('/api/job-sheets/link-data', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        showToast('Success', `Linked ${data.customers_linked} customers and ${data.vehicles_linked} vehicles`);
        loadJobSheets(); // Reload to show updated links
    })
    .catch(error => {
        console.error('Error linking data:', error);
        showToast('Error', 'Failed to link data');
    })
    .finally(() => {
        btn.textContent = originalText;
        btn.disabled = false;
    });
}

// Clear all job sheets
function clearAllJobSheets() {
    if (!confirm('Are you sure you want to clear all job sheets? This action cannot be undone.')) {
        return;
    }

    fetch('/api/job-sheets/clear-all', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        showToast('Success', 'All job sheets cleared successfully');
        loadJobSheets();
    })
    .catch(error => {
        console.error('Error clearing job sheets:', error);
        showToast('Error', 'Failed to clear job sheets');
    });
}

// Show job sheets analytics modal
function showJobSheetsAnalytics() {
    // For now, just show a simple alert with analytics
    // In a full implementation, this would open a detailed analytics modal
    fetch('/api/job-sheets/analytics')
        .then(response => response.json())
        .then(data => {
            const analyticsText = `
Job Sheets Analytics:

Total Jobs: ${data.total_jobs}
Total Revenue: £${(data.total_revenue || 0).toFixed(2)}
MOT Jobs: ${data.mot_jobs}
Payment Rate: ${(data.payment_rate || 0).toFixed(1)}%

Customer Linking:
Unique Customers: ${data.unique_customers}
Linked Customers: ${data.linked_customers}
Link Rate: ${(data.customer_link_rate || 0).toFixed(1)}%

Vehicle Linking:
Unique Vehicles: ${data.unique_vehicles}
Linked Vehicles: ${data.linked_vehicles}
Link Rate: ${(data.vehicle_link_rate || 0).toFixed(1)}%
            `;

            alert(analyticsText);
        })
        .catch(error => {
            console.error('Error loading analytics:', error);
            showToast('Error', 'Failed to load analytics');
        });
}

// Perform DVLA lookup for all vehicles
function performDVLALookupAll() {
    if (!confirm('This will check all vehicles against the DVLA database to update MOT expiry dates and vehicle details. This may take a few minutes. Continue?')) {
        return;
    }

    const btn = document.getElementById('dvla-lookup-all-btn');
    const originalText = btn.textContent;
    btn.textContent = 'Checking DVLA...';
    btn.disabled = true;

    // First trigger lookup for job sheet vehicles
    fetch('/api/job-sheets/link-data', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        // Then trigger lookup for all existing vehicles
        return fetch('/api/vehicles/dvla-lookup-all', {
            method: 'POST'
        });
    })
    .then(response => response.json())
    .then(data => {
        const message = `DVLA Lookup Complete!

Vehicles checked: ${data.checked || 0}
MOT dates updated: ${data.updated || 0}
New vehicles created: ${data.created || 0}
Errors: ${data.errors ? data.errors.length : 0}`;

        alert(message);
        showToast('Success', 'DVLA lookup completed');

        // Reload all data to show updates
        loadJobSheets();
        if (currentPage === 'vehicles') {
            loadVehicles();
        } else if (currentPage === 'reminders') {
            loadRemindersEnhanced();
        }
    })
    .catch(error => {
        console.error('Error performing DVLA lookup:', error);
        showToast('Error', 'Failed to perform DVLA lookup');
    })
    .finally(() => {
        btn.textContent = originalText;
        btn.disabled = false;
    });
}

// Show job sheet details in GA4-style modal
function showJobSheetDetails(jobSheetId) {
    fetch(`/api/job-sheets/${jobSheetId}`)
        .then(response => response.json())
        .then(jobSheet => {
            populateJobSheetModal(jobSheet);
            const modal = new bootstrap.Modal(document.getElementById('job-sheet-details-modal'));
            modal.show();
        })
        .catch(error => {
            console.error('Error loading job sheet details:', error);
            showToast('Error', 'Failed to load job sheet details');
        });
}

// Populate job sheet modal with data
function populateJobSheetModal(jobSheet) {
    // Header information
    document.getElementById('job-sheet-details-title').textContent = `Job Sheet ${jobSheet.doc_no}`;
    document.getElementById('job-doc-no').textContent = jobSheet.doc_no || 'N/A';
    document.getElementById('job-date-created').textContent = formatDateUK(jobSheet.date_created);
    document.getElementById('job-doc-type').textContent = jobSheet.doc_type || 'Job Sheet';

    // Status badge
    const statusBadge = document.getElementById('job-status-badge');
    if (jobSheet.date_paid) {
        statusBadge.innerHTML = '<span class="badge bg-success">Paid</span>';
    } else {
        statusBadge.innerHTML = '<span class="badge bg-warning">Unpaid</span>';
    }

    // Customer information
    const customerInfo = document.getElementById('job-customer-info');
    customerInfo.innerHTML = `
        <div class="row">
            <div class="col-md-12">
                <strong>Name:</strong> ${jobSheet.customer_name || 'Not specified'}<br>
                <strong>Phone:</strong> ${jobSheet.customer_phone || 'Not specified'}<br>
                <strong>Email:</strong> ${jobSheet.customer_email || 'Not specified'}<br>
                <strong>Address:</strong> ${jobSheet.customer_address || 'Not specified'}
            </div>
        </div>
    `;

    // Vehicle information
    const vehicleInfo = document.getElementById('job-vehicle-info');
    vehicleInfo.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <strong>Registration:</strong><br>
                ${jobSheet.vehicle_reg ? createNumberPlateWithDVLALink(jobSheet.vehicle_reg, 'medium') : 'Not specified'}
            </div>
            <div class="col-md-6">
                <strong>Make & Model:</strong><br>
                ${jobSheet.make || 'Unknown'} ${jobSheet.model || ''}
            </div>
        </div>
        <div class="row mt-2">
            <div class="col-md-6">
                <strong>Year:</strong> ${jobSheet.year || 'Unknown'}
            </div>
            <div class="col-md-6">
                <strong>Color:</strong> ${jobSheet.color || 'Unknown'}
            </div>
        </div>
    `;

    // Financial information
    const subtotal = parseFloat(jobSheet.sub_total || 0);
    const vat = parseFloat(jobSheet.vat_total || 0);
    const grandTotal = parseFloat(jobSheet.grand_total || 0);

    document.getElementById('job-subtotal').textContent = `£${subtotal.toFixed(2)}`;
    document.getElementById('job-vat').textContent = `£${vat.toFixed(2)}`;
    document.getElementById('job-grand-total').textContent = `£${grandTotal.toFixed(2)}`;

    document.getElementById('job-date-paid').textContent = jobSheet.date_paid ? formatDateUK(jobSheet.date_paid) : 'Not paid';
    document.getElementById('job-payment-method').textContent = jobSheet.payment_method || '-';

    const balance = jobSheet.date_paid ? 0 : grandTotal;
    document.getElementById('job-balance').textContent = `£${balance.toFixed(2)}`;

    // Parts & Labour tab
    populatePartsLabourTab(jobSheet);

    // MOT tab
    populateMOTTab(jobSheet);

    // History tab
    populateHistoryTab(jobSheet);
}

// Populate Parts & Labour tab
function populatePartsLabourTab(jobSheet) {
    const partsContent = document.getElementById('job-parts-labour-content');

    let content = '<div class="row">';

    // Labour section
    if (jobSheet.sub_labour_gross || jobSheet.sub_labour_net) {
        content += `
            <div class="col-md-6">
                <h6><i class="fas fa-wrench"></i> Labour</h6>
                <table class="table table-sm">
                    <tr><td>Labour (Net):</td><td class="text-end">£${(jobSheet.sub_labour_net || 0).toFixed(2)}</td></tr>
                    <tr><td>Labour (Gross):</td><td class="text-end">£${(jobSheet.sub_labour_gross || 0).toFixed(2)}</td></tr>
                </table>
            </div>
        `;
    }

    // Parts section
    if (jobSheet.sub_parts_gross || jobSheet.sub_parts_net) {
        content += `
            <div class="col-md-6">
                <h6><i class="fas fa-cog"></i> Parts</h6>
                <table class="table table-sm">
                    <tr><td>Parts (Net):</td><td class="text-end">£${(jobSheet.sub_parts_net || 0).toFixed(2)}</td></tr>
                    <tr><td>Parts (Gross):</td><td class="text-end">£${(jobSheet.sub_parts_gross || 0).toFixed(2)}</td></tr>
                </table>
            </div>
        `;
    }

    content += '</div>';

    if (!jobSheet.sub_labour_gross && !jobSheet.sub_parts_gross) {
        content = '<p class="text-muted">No detailed parts or labour information available.</p>';
    }

    partsContent.innerHTML = content;
}

// Populate MOT tab
function populateMOTTab(jobSheet) {
    const motContent = document.getElementById('job-mot-details');

    let content = '';

    if (jobSheet.sub_mot_gross || jobSheet.sub_mot_net) {
        content = `
            <div class="row">
                <div class="col-md-6">
                    <h6><i class="fas fa-certificate"></i> MOT Test</h6>
                    <table class="table table-sm">
                        <tr><td>MOT (Net):</td><td class="text-end">£${(jobSheet.sub_mot_net || 0).toFixed(2)}</td></tr>
                        <tr><td>MOT (Gross):</td><td class="text-end">£${(jobSheet.sub_mot_gross || 0).toFixed(2)}</td></tr>
                    </table>
                </div>
                <div class="col-md-6">
                    <h6><i class="fas fa-info-circle"></i> MOT Information</h6>
                    <p><strong>Test Date:</strong> ${formatDateUK(jobSheet.date_created)}</p>
                    <p><strong>Vehicle:</strong> ${jobSheet.make || ''} ${jobSheet.model || ''}</p>
                    <p><strong>Registration:</strong> ${jobSheet.vehicle_reg || 'N/A'}</p>
                </div>
            </div>
        `;
    } else {
        content = '<p class="text-muted">This job sheet does not contain MOT test information.</p>';
    }

    motContent.innerHTML = content;
}

// Populate History tab
function populateHistoryTab(jobSheet) {
    const historyContent = document.getElementById('job-history-content');

    const content = `
        <div class="timeline">
            <div class="timeline-item">
                <div class="timeline-marker bg-primary"></div>
                <div class="timeline-content">
                    <h6>Job Sheet Created</h6>
                    <p class="text-muted">${formatDateUK(jobSheet.date_created)}</p>
                    <small>Document ${jobSheet.doc_no} was created for ${jobSheet.customer_name || 'customer'}</small>
                </div>
            </div>
            ${jobSheet.date_paid ? `
                <div class="timeline-item">
                    <div class="timeline-marker bg-success"></div>
                    <div class="timeline-content">
                        <h6>Payment Received</h6>
                        <p class="text-muted">${formatDateUK(jobSheet.date_paid)}</p>
                        <small>Payment of £${(jobSheet.grand_total || 0).toFixed(2)} received</small>
                    </div>
                </div>
            ` : `
                <div class="timeline-item">
                    <div class="timeline-marker bg-warning"></div>
                    <div class="timeline-content">
                        <h6>Payment Pending</h6>
                        <p class="text-muted">Outstanding balance: £${(jobSheet.grand_total || 0).toFixed(2)}</p>
                        <small>Payment not yet received</small>
                    </div>
                </div>
            `}
        </div>
    `;

    historyContent.innerHTML = content;
}


