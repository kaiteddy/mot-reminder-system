// Parts Management
let parts = [];
let categories = [];
let suppliers = [];

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    loadParts();
    loadCategories();
    loadSuppliers();
    
    // Add event listeners
    document.getElementById('searchInput').addEventListener('input', debounce(filterParts, 300));
    document.getElementById('categoryFilter').addEventListener('change', filterParts);
    document.getElementById('supplierFilter').addEventListener('change', filterParts);
    document.getElementById('stockFilter').addEventListener('change', filterParts);
});

// Load parts
async function loadParts() {
    showLoading(true);
    try {
        const response = await fetch('/api/parts/');
        if (response.ok) {
            parts = await response.json();
            displayParts(parts);
            updatePartsStats();
        } else {
            showError('Failed to load parts');
        }
    } catch (error) {
        console.error('Error loading parts:', error);
        showError('Error loading parts');
    } finally {
        showLoading(false);
    }
}

// Load categories for filter
async function loadCategories() {
    try {
        const response = await fetch('/api/parts/categories');
        if (response.ok) {
            categories = await response.json();
            populateCategoryFilter();
        }
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

// Load suppliers for filter
async function loadSuppliers() {
    try {
        const response = await fetch('/api/parts/suppliers');
        if (response.ok) {
            suppliers = await response.json();
            populateSupplierFilter();
        }
    } catch (error) {
        console.error('Error loading suppliers:', error);
    }
}

// Populate category filter dropdown
function populateCategoryFilter() {
    const select = document.getElementById('categoryFilter');
    select.innerHTML = '<option value="">All Categories</option>';
    
    categories.forEach(category => {
        const option = document.createElement('option');
        option.value = category;
        option.textContent = category;
        select.appendChild(option);
    });
}

// Populate supplier filter dropdown
function populateSupplierFilter() {
    const select = document.getElementById('supplierFilter');
    select.innerHTML = '<option value="">All Suppliers</option>';
    
    suppliers.forEach(supplier => {
        const option = document.createElement('option');
        option.value = supplier;
        option.textContent = supplier;
        select.appendChild(option);
    });
}

// Update parts statistics
function updatePartsStats() {
    const totalParts = parts.length;
    const lowStockParts = parts.filter(part => part.is_low_stock).length;
    const totalStockValue = parts.reduce((sum, part) => sum + (part.stock_quantity * part.cost_price), 0);
    const uniqueCategories = [...new Set(parts.map(part => part.category).filter(cat => cat))].length;
    
    document.getElementById('totalParts').textContent = totalParts;
    document.getElementById('lowStockCount').textContent = lowStockParts;
    document.getElementById('totalStockValue').textContent = `£${totalStockValue.toFixed(2)}`;
    document.getElementById('totalCategories').textContent = uniqueCategories;
}

// Display parts in table
function displayParts(partsToShow) {
    const tbody = document.getElementById('partsTableBody');
    const noPartsMessage = document.getElementById('noPartsMessage');
    
    if (partsToShow.length === 0) {
        tbody.innerHTML = '';
        noPartsMessage.style.display = 'block';
        return;
    }
    
    noPartsMessage.style.display = 'none';
    
    tbody.innerHTML = partsToShow.map(part => `
        <tr>
            <td>
                <strong>${part.part_number}</strong>
                ${part.supplier_part_number ? `<br><small class="text-muted">Supplier: ${part.supplier_part_number}</small>` : ''}
            </td>
            <td>
                <div title="${part.description}">
                    ${truncateText(part.description, 40)}
                </div>
            </td>
            <td>${part.category || 'N/A'}</td>
            <td>${part.supplier || 'N/A'}</td>
            <td>£${part.cost_price.toFixed(2)}</td>
            <td>£${part.sell_price.toFixed(2)}</td>
            <td>
                <span class="badge ${getStockBadgeClass(part)}">${part.stock_quantity}</span>
                ${part.minimum_stock > 0 ? `<br><small class="text-muted">Min: ${part.minimum_stock}</small>` : ''}
            </td>
            <td>
                ${getPartStatusBadges(part)}
            </td>
            <td>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-primary" onclick="viewPart(${part.id})" title="View Details">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-outline-secondary" onclick="editPart(${part.id})" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-outline-danger" onclick="deletePart(${part.id})" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

// Get stock badge class based on stock level
function getStockBadgeClass(part) {
    if (part.stock_quantity === 0) return 'bg-danger';
    if (part.is_low_stock) return 'bg-warning';
    return 'bg-success';
}

// Get part status badges
function getPartStatusBadges(part) {
    let badges = [];
    
    if (!part.is_active) {
        badges.push('<span class="badge bg-secondary">Inactive</span>');
    }
    
    if (part.is_low_stock) {
        badges.push('<span class="badge bg-warning">Low Stock</span>');
    }
    
    if (part.stock_quantity === 0) {
        badges.push('<span class="badge bg-danger">Out of Stock</span>');
    }
    
    if (badges.length === 0) {
        badges.push('<span class="badge bg-success">Active</span>');
    }
    
    return badges.join(' ');
}

// Apply filters
function applyFilters() {
    filterParts();
}

// Filter parts based on search and filters
function filterParts() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const categoryFilter = document.getElementById('categoryFilter').value;
    const supplierFilter = document.getElementById('supplierFilter').value;
    const stockFilter = document.getElementById('stockFilter').value;
    
    let filteredParts = parts.filter(part => {
        // Search filter
        if (searchTerm) {
            const searchableText = [
                part.part_number,
                part.description,
                part.supplier,
                part.supplier_part_number,
                part.category
            ].join(' ').toLowerCase();
            
            if (!searchableText.includes(searchTerm)) {
                return false;
            }
        }
        
        // Category filter
        if (categoryFilter && part.category !== categoryFilter) {
            return false;
        }
        
        // Supplier filter
        if (supplierFilter && part.supplier !== supplierFilter) {
            return false;
        }
        
        // Stock filter
        if (stockFilter) {
            switch (stockFilter) {
                case 'low':
                    if (!part.is_low_stock) return false;
                    break;
                case 'in_stock':
                    if (part.stock_quantity === 0) return false;
                    break;
                case 'out_of_stock':
                    if (part.stock_quantity > 0) return false;
                    break;
            }
        }
        
        return true;
    });
    
    displayParts(filteredParts);
}

// Clear all filters
function clearFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('categoryFilter').value = '';
    document.getElementById('supplierFilter').value = '';
    document.getElementById('stockFilter').value = '';
    
    displayParts(parts);
}

// Show low stock parts
function showLowStockParts() {
    const lowStockParts = parts.filter(part => part.is_low_stock);
    displayParts(lowStockParts);
    
    // Update filter to show low stock
    document.getElementById('stockFilter').value = 'low';
}

// Save new part
async function savePart() {
    const form = document.getElementById('addPartForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const partData = {
        part_number: document.getElementById('partNumber').value,
        description: document.getElementById('description').value,
        category: document.getElementById('category').value,
        supplier: document.getElementById('supplier').value,
        supplier_part_number: document.getElementById('supplierPartNumber').value,
        cost_price: parseFloat(document.getElementById('costPrice').value) || 0,
        sell_price: parseFloat(document.getElementById('sellPrice').value) || 0,
        stock_quantity: parseInt(document.getElementById('stockQuantity').value) || 0,
        minimum_stock: parseInt(document.getElementById('minimumStock').value) || 0,
        warranty_months: parseInt(document.getElementById('warrantyMonths').value) || 12,
        warranty_mileage: parseInt(document.getElementById('warrantyMileage').value) || null,
        location: document.getElementById('location').value,
        notes: document.getElementById('notes').value
    };
    
    try {
        const response = await fetch('/api/parts/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(partData)
        });
        
        if (response.ok) {
            const newPart = await response.json();
            parts.unshift(newPart);
            displayParts(parts);
            updatePartsStats();
            loadCategories(); // Refresh categories
            loadSuppliers(); // Refresh suppliers
            
            // Close modal and reset form
            const modal = bootstrap.Modal.getInstance(document.getElementById('addPartModal'));
            modal.hide();
            form.reset();
            
            showSuccess('Part added successfully');
        } else {
            const error = await response.json();
            showError(error.error || 'Failed to add part');
        }
    } catch (error) {
        console.error('Error saving part:', error);
        showError('Error saving part');
    }
}

// View part details
async function viewPart(partId) {
    try {
        const response = await fetch(`/api/parts/${partId}`);
        if (response.ok) {
            const part = await response.json();
            showPartDetails(part);
        } else {
            showError('Failed to load part details');
        }
    } catch (error) {
        console.error('Error loading part details:', error);
        showError('Error loading part details');
    }
}

// Show part details modal
function showPartDetails(part) {
    const markup = `
        <strong>Part Number:</strong> ${part.part_number}<br>
        <strong>Description:</strong> ${part.description}<br>
        <strong>Category:</strong> ${part.category || 'N/A'}<br>
        <strong>Supplier:</strong> ${part.supplier || 'N/A'}<br>
        <strong>Cost Price:</strong> £${part.cost_price.toFixed(2)}<br>
        <strong>Sell Price:</strong> £${part.sell_price.toFixed(2)}<br>
        <strong>Stock:</strong> ${part.stock_quantity} (Min: ${part.minimum_stock})<br>
        <strong>Warranty:</strong> ${part.warranty_months} months<br>
        <strong>Location:</strong> ${part.location || 'N/A'}<br>
        <strong>Markup:</strong> ${part.markup_percentage.toFixed(1)}%
    `;
    
    alert(`Part Details:\n\n${markup.replace(/<br>/g, '\n').replace(/<strong>|<\/strong>/g, '')}`);
}

// Edit part
function editPart(partId) {
    // This would open the part in edit mode
    alert('Edit functionality would be implemented here');
}

// Delete part
async function deletePart(partId) {
    if (!confirm('Are you sure you want to delete this part?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/parts/${partId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            parts = parts.filter(p => p.id !== partId);
            displayParts(parts);
            updatePartsStats();
            showSuccess('Part deleted successfully');
        } else {
            showError('Failed to delete part');
        }
    } catch (error) {
        console.error('Error deleting part:', error);
        showError('Error deleting part');
    }
}

// Utility functions
function showLoading(show) {
    document.getElementById('loadingSpinner').style.display = show ? 'block' : 'none';
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
    alert('Success: ' + message);
}

function showError(message) {
    alert('Error: ' + message);
}
