// Main JavaScript file for PDF Tools Website

// Initialize tooltips if Bootstrap is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Add fade-in animation to elements with fade-in class
    const fadeInElements = document.querySelectorAll('.fade-in');
    fadeInElements.forEach((element, index) => {
        setTimeout(() => {
            element.style.opacity = '0';
            element.style.transform = 'translateY(30px)';
            element.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            
            setTimeout(() => {
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }, 100);
        }, index * 100);
    });
});

// Common utility functions
const Utils = {
    // Format file size
    formatFileSize: function(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    
    // Show loading state
    showLoading: function(element, text = 'Processing...') {
        element.innerHTML = `
            <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
            ${text}
        `;
        element.disabled = true;
    },
    
    // Hide loading state
    hideLoading: function(element, originalText) {
        element.innerHTML = originalText;
        element.disabled = false;
    },
    
    // Show alert
    showAlert: function(message, type = 'info') {
        const alertContainer = document.getElementById('alert-container');
        if (alertContainer) {
            const alert = document.createElement('div');
            alert.className = `alert alert-${type} alert-dismissible fade show`;
            alert.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;
            alertContainer.appendChild(alert);
            
            // Auto remove after 5 seconds
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.remove();
                }
            }, 5000);
        }
    }
};

// File upload utilities
const FileUpload = {
    // Validate file type
    validateFileType: function(file, allowedTypes) {
        return allowedTypes.includes(file.type);
    },
    
    // Validate file size
    validateFileSize: function(file, maxSize) {
        return file.size <= maxSize;
    },
    
    // Create file preview element
    createFilePreview: function(file, index) {
        const fileItem = document.createElement('div');
        fileItem.className = 'list-group-item';
        fileItem.innerHTML = `
            <div class="d-flex justify-content-between align-items-center py-2">
                <div class="d-flex align-items-center">
                    <i class="bi bi-file-earmark-pdf text-danger me-3 fs-4"></i>
                    <div>
                        <h6 class="mb-0">${file.name}</h6>
                        <small class="text-muted">${Utils.formatFileSize(file.size)}</small>
                    </div>
                </div>
                <div class="d-flex align-items-center">
                    <span class="badge bg-light text-dark me-2">#${index + 1}</span>
                    <button type="button" class="btn btn-outline-danger btn-sm" onclick="removeFile(${index})">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
        `;
        return fileItem;
    }
};

// Drag and drop functionality
const DragDrop = {
    // Initialize drag and drop for an element
    init: function(element, onDrop) {
        element.addEventListener('dragover', function(e) {
            e.preventDefault();
            element.classList.add('dragover');
        });
        
        element.addEventListener('dragleave', function(e) {
            e.preventDefault();
            element.classList.remove('dragover');
        });
        
        element.addEventListener('drop', function(e) {
            e.preventDefault();
            element.classList.remove('dragover');
            if (onDrop && typeof onDrop === 'function') {
                onDrop(e.dataTransfer.files);
            }
        });
    }
};

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add active class to current navigation item
const currentLocation = location.pathname;
const menuItems = document.querySelectorAll('.navbar-nav .nav-link');
menuItems.forEach(item => {
    if(item.getAttribute('href') === currentLocation) {
        item.classList.add('active');
    }
});