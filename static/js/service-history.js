// Service History Management
let services = [];
let vehicles = [];

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    loadVehicles();
    loadServices();
    loadServiceStats();
    
    // Set default date to today
    document.getElementById('serviceDate').value = new Date().toISOString().split('T')[0];
    
    // Add event listeners
    document.getElementById('searchInput').addEventListener('input', debounce(filterServices, 300));
    document.getElementById('serviceTypeFilter').addEventListener('change', filterServices);
    document.getElementById('statusFilter').addEventListener('change', filterServices);
});

// Load vehicles for dropdown
async function loadVehicles() {
    try {
        const response = await fetch('/api/vehicles/');
        if (response.ok) {
            vehicles = await response.json();
            populateVehicleSelect();
        }
    } catch (error) {
        console.error('Error loading vehicles:', error);
    }
}

// Populate vehicle select dropdown
function populateVehicleSelect() {
    const select = document.getElementById('vehicleSelect');
    select.innerHTML = '<option value="">Select Vehicle...</option>';
    
    vehicles.forEach(vehicle => {
        const option = document.createElement('option');
        option.value = vehicle.id;
        option.textContent = `${vehicle.registration} - ${vehicle.make} ${vehicle.model}`;
        if (vehicle.customer_name) {
            option.textContent += ` (${vehicle.customer_name})`;
        }
        select.appendChild(option);
    });
}

// Load services
async function loadServices() {
    showLoading(true);
    try {
        const response = await fetch('/api/services/');
        if (response.ok) {
            services = await response.json();
            displayServices(services);
        } else {
            showError('Failed to load services');
        }
    } catch (error) {
        console.error('Error loading services:', error);
        showError('Error loading services');
    } finally {
        showLoading(false);
    }
}

// Load service statistics
async function loadServiceStats() {
    try {
        const response = await fetch('/api/services/stats');
        if (response.ok) {
            const stats = await response.json();
            updateStatsDisplay(stats);
        }
    } catch (error) {
        console.error('Error loading service stats:', error);
    }
}

// Update statistics display
function updateStatsDisplay(stats) {
    document.getElementById('totalServices').textContent = stats.total_services || 0;
    document.getElementById('totalRevenue').textContent = `£${(stats.total_revenue || 0).toFixed(2)}`;
    document.getElementById('totalLabourHours').textContent = (stats.total_labour_hours || 0).toFixed(1);
    document.getElementById('avgServiceValue').textContent = `£${(stats.average_service_value || 0).toFixed(2)}`;
}

// Display services in table
function displayServices(servicesToShow) {
    const tbody = document.getElementById('servicesTableBody');
    const noServicesMessage = document.getElementById('noServicesMessage');

    if (servicesToShow.length === 0) {
        tbody.innerHTML = '';
        noServicesMessage.style.display = 'block';
        return;
    }

    noServicesMessage.style.display = 'none';

    // Add vehicle information to services for display
    const servicesWithVehicleInfo = servicesToShow.map(service => {
        const vehicle = vehicles.find(v => v.id === service.vehicle_id);
        return {
            ...service,
            vehicle: vehicle || {}
        };
    });

    tbody.innerHTML = servicesWithVehicleInfo.map(service => `
        <tr>
            <td>${formatDate(service.service_date)}</td>
            <td>
                <strong>${service.vehicle?.registration || 'N/A'}</strong><br>
                <small class="text-muted">${service.vehicle?.make || ''} ${service.vehicle?.model || ''}</small>
            </td>
            <td>${service.vehicle?.customer_name || 'N/A'}</td>
            <td><span class="badge bg-primary">${service.service_type}</span></td>
            <td>
                <div class="service-description" title="${service.description || ''}">
                    ${truncateText(service.description || '', 50)}
                </div>
            </td>
            <td>${service.technician || 'N/A'}</td>
            <td><strong>£${service.total_cost.toFixed(2)}</strong></td>
            <td>${getStatusBadge(service.status)}</td>
            <td>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-primary" onclick="viewService(${service.id})" title="View Details">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-outline-secondary" onclick="editService(${service.id})" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-outline-danger" onclick="deleteService(${service.id})" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

// Get status badge HTML
function getStatusBadge(status) {
    const badges = {
        'completed': 'bg-success',
        'pending': 'bg-warning',
        'in_progress': 'bg-info',
        'cancelled': 'bg-danger'
    };
    
    const badgeClass = badges[status] || 'bg-secondary';
    return `<span class="badge ${badgeClass}">${status.replace('_', ' ').toUpperCase()}</span>`;
}

// Apply filters
function applyFilters() {
    filterServices();
}

// Filter services based on search and filters
function filterServices() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const serviceTypeFilter = document.getElementById('serviceTypeFilter').value;
    const statusFilter = document.getElementById('statusFilter').value;
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    
    let filteredServices = services.filter(service => {
        // Search filter
        if (searchTerm) {
            const searchableText = [
                service.vehicle?.registration,
                service.vehicle?.customer_name,
                service.description,
                service.technician,
                service.service_type
            ].join(' ').toLowerCase();
            
            if (!searchableText.includes(searchTerm)) {
                return false;
            }
        }
        
        // Service type filter
        if (serviceTypeFilter && service.service_type !== serviceTypeFilter) {
            return false;
        }
        
        // Status filter
        if (statusFilter && service.status !== statusFilter) {
            return false;
        }
        
        // Date range filter
        if (startDate && service.service_date < startDate) {
            return false;
        }
        
        if (endDate && service.service_date > endDate) {
            return false;
        }
        
        return true;
    });
    
    displayServices(filteredServices);
}

// Clear all filters
function clearFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('serviceTypeFilter').value = '';
    document.getElementById('statusFilter').value = '';
    document.getElementById('startDate').value = '';
    document.getElementById('endDate').value = '';
    
    displayServices(services);
}

// Save new service
async function saveService() {
    const form = document.getElementById('addServiceForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const serviceData = {
        vehicle_id: parseInt(document.getElementById('vehicleSelect').value),
        service_date: document.getElementById('serviceDate').value,
        service_type: document.getElementById('serviceType').value,
        description: document.getElementById('description').value,
        labour_hours: parseFloat(document.getElementById('labourHours').value) || 0,
        labour_rate: parseFloat(document.getElementById('labourRate').value) || 0,
        technician: document.getElementById('technician').value,
        mileage: parseInt(document.getElementById('mileage').value) || null,
        advisories: document.getElementById('advisories').value,
        invoice_number: document.getElementById('invoiceNumber').value,
        payment_status: document.getElementById('paymentStatus').value
    };
    
    try {
        const response = await fetch('/api/services/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(serviceData)
        });
        
        if (response.ok) {
            const newService = await response.json();
            services.unshift(newService);
            displayServices(services);
            loadServiceStats(); // Refresh stats
            
            // Close modal and reset form
            const modal = bootstrap.Modal.getInstance(document.getElementById('addServiceModal'));
            modal.hide();
            form.reset();
            
            showSuccess('Service record added successfully');
        } else {
            const error = await response.json();
            showError(error.error || 'Failed to add service record');
        }
    } catch (error) {
        console.error('Error saving service:', error);
        showError('Error saving service record');
    }
}

// View service details
async function viewService(serviceId) {
    try {
        const response = await fetch(`/api/services/${serviceId}`);
        if (response.ok) {
            const service = await response.json();
            showServiceDetails(service);
        } else {
            showError('Failed to load service details');
        }
    } catch (error) {
        console.error('Error loading service details:', error);
        showError('Error loading service details');
    }
}

// Show service details modal
function showServiceDetails(service) {
    // Create and show a detailed view modal
    // This would be implemented with a detailed modal showing all service information
    alert(`Service Details:\n\nDate: ${formatDate(service.service_date)}\nType: ${service.service_type}\nTotal: £${service.total_cost.toFixed(2)}\nDescription: ${service.description || 'N/A'}`);
}

// Edit service
function editService(serviceId) {
    // This would open the service in edit mode
    alert('Edit functionality would be implemented here');
}

// Delete service
async function deleteService(serviceId) {
    if (!confirm('Are you sure you want to delete this service record?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/services/${serviceId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            services = services.filter(s => s.id !== serviceId);
            displayServices(services);
            loadServiceStats(); // Refresh stats
            showSuccess('Service record deleted successfully');
        } else {
            showError('Failed to delete service record');
        }
    } catch (error) {
        console.error('Error deleting service:', error);
        showError('Error deleting service record');
    }
}

// Utility functions
function showLoading(show) {
    document.getElementById('loadingSpinner').style.display = show ? 'block' : 'none';
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-GB');
}

function truncateText(text, maxLength) {
    if (!text || text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function showSuccess(message) {
    // Simple alert for now - could be replaced with toast notifications
    alert('Success: ' + message);
}

function showError(message) {
    // Simple alert for now - could be replaced with toast notifications
    alert('Error: ' + message);
}
