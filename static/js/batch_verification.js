/**
 * Batch DVLA Verification Interface
 * Handles real-time status updates and user interactions
 */

class BatchVerificationManager {
    constructor() {
        this.selectedType = null;
        this.statusInterval = null;
        this.isRunning = false;
        
        this.initializeEventListeners();
        this.loadInitialStatus();
        this.loadVehicleCounts();
    }
    
    initializeEventListeners() {
        // Verification option selection
        document.querySelectorAll('.verification-option').forEach(option => {
            option.addEventListener('click', (e) => {
                this.selectVerificationType(e.currentTarget.dataset.type);
            });
        });
        
        // Start/Stop buttons
        document.getElementById('start-btn').addEventListener('click', () => {
            this.startVerification();
        });
        
        document.getElementById('stop-btn').addEventListener('click', () => {
            this.stopVerification();
        });
        
        // Clear errors button
        document.getElementById('clear-errors-btn').addEventListener('click', () => {
            this.clearErrors();
        });
    }
    
    selectVerificationType(type) {
        // Remove previous selection
        document.querySelectorAll('.verification-option').forEach(option => {
            option.classList.remove('selected');
        });
        
        // Add selection to clicked option
        document.querySelector(`[data-type="${type}"]`).classList.add('selected');
        
        this.selectedType = type;
        document.getElementById('start-btn').disabled = false;
    }
    
    async loadInitialStatus() {
        try {
            const response = await fetch('/api/vehicles/dvla-batch-status');
            const data = await response.json();
            
            this.updateStatusDisplay(data);
            
            if (data.is_running) {
                this.startStatusPolling();
            }
        } catch (error) {
            console.error('Error loading initial status:', error);
        }
    }
    
    async loadVehicleCounts() {
        try {
            // Load counts for each verification type
            const counts = await Promise.all([
                this.getVehicleCount('all'),
                this.getVehicleCount('missing_mot'),
                this.getVehicleCount('unverified'),
                this.getVehicleCount('job_sheets')
            ]);
            
            document.getElementById('count-all').textContent = counts[0];
            document.getElementById('count-missing-mot').textContent = counts[1];
            document.getElementById('count-unverified').textContent = counts[2];
            document.getElementById('count-job-sheets').textContent = counts[3];
            
        } catch (error) {
            console.error('Error loading vehicle counts:', error);
        }
    }
    
    async getVehicleCount(type) {
        try {
            const response = await fetch(`/api/vehicles/count?type=${type}`);
            const data = await response.json();
            return data.count || 0;
        } catch (error) {
            console.error(`Error getting count for ${type}:`, error);
            return 0;
        }
    }
    
    async startVerification() {
        if (!this.selectedType) {
            alert('Please select a verification type first');
            return;
        }
        
        try {
            const response = await fetch('/api/vehicles/dvla-batch-start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    type: this.selectedType
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.isRunning = true;
                this.updateUIForRunning();
                this.startStatusPolling();
                this.showNotification('Batch verification started successfully', 'success');
            } else {
                this.showNotification(data.message || 'Failed to start verification', 'error');
            }
            
        } catch (error) {
            console.error('Error starting verification:', error);
            this.showNotification('Error starting verification', 'error');
        }
    }
    
    async stopVerification() {
        try {
            const response = await fetch('/api/vehicles/dvla-batch-stop', {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showNotification('Stop request sent', 'info');
            } else {
                this.showNotification(data.message || 'Failed to stop verification', 'error');
            }
            
        } catch (error) {
            console.error('Error stopping verification:', error);
            this.showNotification('Error stopping verification', 'error');
        }
    }
    
    startStatusPolling() {
        if (this.statusInterval) {
            clearInterval(this.statusInterval);
        }
        
        this.statusInterval = setInterval(async () => {
            try {
                const response = await fetch('/api/vehicles/dvla-batch-status');
                const data = await response.json();
                
                this.updateStatusDisplay(data);
                
                // Stop polling if process is no longer running
                if (!data.is_running) {
                    this.stopStatusPolling();
                    this.updateUIForStopped();
                }
                
            } catch (error) {
                console.error('Error polling status:', error);
            }
        }, 2000); // Poll every 2 seconds
    }
    
    stopStatusPolling() {
        if (this.statusInterval) {
            clearInterval(this.statusInterval);
            this.statusInterval = null;
        }
    }
    
    updateStatusDisplay(data) {
        const { status, progress } = data;
        
        // Update status badge
        const statusBadge = document.getElementById('status-badge');
        statusBadge.className = `status-badge status-${status}`;
        statusBadge.textContent = status.charAt(0).toUpperCase() + status.slice(1);
        
        if (data.is_running && progress) {
            // Show progress container
            document.getElementById('progress-container').style.display = 'block';
            document.getElementById('idle-message').style.display = 'none';
            
            // Update progress bar
            const percentage = progress.total_vehicles > 0 
                ? (progress.processed / progress.total_vehicles) * 100 
                : 0;
            
            document.getElementById('progress-bar').style.width = `${percentage}%`;
            document.getElementById('progress-text').textContent = 
                `${progress.processed} / ${progress.total_vehicles}`;
            
            // Update stats
            document.getElementById('stat-total').textContent = progress.total_vehicles;
            document.getElementById('stat-processed').textContent = progress.processed;
            document.getElementById('stat-successful').textContent = progress.successful;
            document.getElementById('stat-failed').textContent = progress.failed;
            document.getElementById('stat-skipped').textContent = progress.skipped;
            document.getElementById('stat-customers-linked').textContent = progress.customers_linked || 0;
            document.getElementById('stat-customers-created').textContent = progress.customers_created || 0;
            
            // Update current vehicle
            if (progress.current_registration) {
                document.getElementById('current-vehicle').style.display = 'block';
                document.getElementById('current-reg').textContent = progress.current_registration;
            } else {
                document.getElementById('current-vehicle').style.display = 'none';
            }
            
            // Update estimated completion
            if (progress.estimated_completion) {
                document.getElementById('estimated-completion').style.display = 'block';
                const completionTime = new Date(progress.estimated_completion);
                document.getElementById('completion-time').textContent = 
                    completionTime.toLocaleTimeString();
            } else {
                document.getElementById('estimated-completion').style.display = 'none';
            }
            
            // Update errors
            if (progress.errors && progress.errors.length > 0) {
                this.updateErrorLog(progress.errors);
            }
            
        } else {
            // Hide progress container
            document.getElementById('progress-container').style.display = 'none';
            document.getElementById('idle-message').style.display = 'block';
        }
    }
    
    updateErrorLog(errors) {
        const errorLog = document.getElementById('error-log');
        const clearBtn = document.getElementById('clear-errors-btn');
        
        if (errors.length > 0) {
            errorLog.innerHTML = errors.map(error => 
                `<div class="text-danger mb-1">${this.escapeHtml(error)}</div>`
            ).join('');
            clearBtn.style.display = 'block';
        } else {
            errorLog.innerHTML = '<div class="text-muted text-center">No errors to display</div>';
            clearBtn.style.display = 'none';
        }
        
        // Auto-scroll to bottom
        errorLog.scrollTop = errorLog.scrollHeight;
    }
    
    clearErrors() {
        const errorLog = document.getElementById('error-log');
        const clearBtn = document.getElementById('clear-errors-btn');
        
        errorLog.innerHTML = '<div class="text-muted text-center">No errors to display</div>';
        clearBtn.style.display = 'none';
    }
    
    updateUIForRunning() {
        document.getElementById('start-btn').style.display = 'none';
        document.getElementById('stop-btn').style.display = 'inline-block';
        
        // Disable verification options
        document.querySelectorAll('.verification-option').forEach(option => {
            option.style.pointerEvents = 'none';
            option.style.opacity = '0.6';
        });
    }
    
    updateUIForStopped() {
        document.getElementById('start-btn').style.display = 'inline-block';
        document.getElementById('stop-btn').style.display = 'none';
        
        // Re-enable verification options
        document.querySelectorAll('.verification-option').forEach(option => {
            option.style.pointerEvents = 'auto';
            option.style.opacity = '1';
        });
        
        this.isRunning = false;
        
        // Reload vehicle counts
        this.loadVehicleCounts();
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new BatchVerificationManager();
});
