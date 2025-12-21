// Smooth scrolling navigation
document.addEventListener('DOMContentLoaded', function() {
    // Navigation scroll effect
    const nav = document.querySelector('nav');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            nav.classList.add('scrolled');
        } else {
            nav.classList.remove('scrolled');
        }
    });

    // Active link highlighting
    const navLinks = document.querySelectorAll('.nav-links a');
    const currentPath = window.location.pathname;
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
});

// File upload with drag and drop
function initializeFileUpload(uploadAreaId, fileInputId, previewId) {
    const uploadArea = document.getElementById(uploadAreaId);
    const fileInput = document.getElementById(fileInputId);
    const preview = document.getElementById(previewId);

    if (!uploadArea || !fileInput) return;

    // Click to upload
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });

    // File selection
    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });

    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('drag-over');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('drag-over');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');
        handleFiles(e.dataTransfer.files);
    });

    function handleFiles(files) {
        if (files.length > 0) {
            const file = files[0];
            if (file.type.startsWith('image/')) {
                displayPreview(file);
            } else {
                showAlert('Please select an image file', 'danger');
            }
        }
    }

    function displayPreview(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            if (preview) {
                preview.innerHTML = `
                    <div class="result-image-container" style="animation: zoomIn 0.6s ease;">
                        <img src="${e.target.result}" alt="Preview">
                    </div>
                `;
            }
        };
        reader.readAsDataURL(file);
    }
}

// Image detection with AJAX
function detectImage(formId, resultsId) {
    const form = document.getElementById(formId);
    const resultsSection = document.getElementById(resultsId);

    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(form);
        const fileInput = form.querySelector('input[type="file"]');

        if (!fileInput.files.length) {
            showAlert('Please select an image first', 'warning');
            return;
        }

        // Show loading
        showLoading(resultsSection);

        try {
            const response = await fetch(form.action || window.location.href, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const data = await response.json();

            if (data.status === 'success') {
                displayResults(data, resultsSection);
                showAlert('Detection completed successfully!', 'success');
            } else {
                showAlert(data.message || 'Detection failed', 'danger');
            }
        } catch (error) {
            showAlert('Error processing image: ' + error.message, 'danger');
        } finally {
            hideLoading();
        }
    });
}

// Display detection results
function displayResults(data, resultsSection) {
    if (!resultsSection) return;

    let detectionsHTML = '';
    
    if (data.detections && data.detections.length > 0) {
        detectionsHTML = '<div class="detections-list">';
        data.detections.forEach((detection, index) => {
            const icon = detection.class.toLowerCase() === 'fire' ? '🔥' : '💨';
            const confidence = (detection.confidence * 100).toFixed(1);
            
            detectionsHTML += `
                <div class="detection-item" style="animation-delay: ${index * 0.1}s;">
                    <div class="detection-icon">${icon}</div>
                    <div class="detection-info">
                        <h4>${detection.class}</h4>
                        <p>${confidence}% confident</p>
                        <div class="confidence-bar">
                            <div class="confidence-fill" style="width: ${confidence}%"></div>
                        </div>
                    </div>
                </div>
            `;
        });
        detectionsHTML += '</div>';
    } else {
        detectionsHTML = '<p style="text-align: center; color: var(--success-color);">No fire or smoke detected ✓</p>';
    }

    resultsSection.innerHTML = `
        <div class="card">
            <div class="card-content">
                <h2>Detection Results</h2>
                ${data.result_image ? `
                    <div class="result-image-container">
                        <img src="${data.result_image}" alt="Detection Result">
                    </div>
                ` : ''}
                ${detectionsHTML}
            </div>
        </div>
    `;

    resultsSection.classList.add('show');

    // Trigger animations
    setTimeout(() => {
        const fills = resultsSection.querySelectorAll('.confidence-fill');
        fills.forEach(fill => {
            fill.style.width = fill.style.width;
        });
    }, 100);
}

// Video stream handling
function startVideoStream(videoFeedUrl, videoContainerId, statusId) {
    const videoContainer = document.getElementById(videoContainerId);
    const statusElement = document.getElementById(statusId);

    if (!videoContainer) return;

    videoContainer.innerHTML = `
        <img src="${videoFeedUrl}" alt="Live Video Feed" style="width: 100%; height: auto;">
    `;

    if (statusElement) {
        statusElement.innerHTML = '<span style="color: var(--success-color);">● Live</span>';
    }
}

function stopVideoStream(videoContainerId, statusId) {
    const videoContainer = document.getElementById(videoContainerId);
    const statusElement = document.getElementById(statusId);

    if (videoContainer) {
        videoContainer.innerHTML = '<p style="text-align: center; padding: 3rem;">Video stream stopped</p>';
    }

    if (statusElement) {
        statusElement.innerHTML = '<span style="color: var(--danger-color);">● Stopped</span>';
    }
}

// Alert notifications
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alert-container') || createAlertContainer();
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
        <strong>${type.charAt(0).toUpperCase() + type.slice(1)}:</strong> ${message}
    `;
    
    alertContainer.appendChild(alert);

    // Auto remove after 5 seconds
    setTimeout(() => {
        alert.style.animation = 'fadeOut 0.4s ease';
        setTimeout(() => alert.remove(), 400);
    }, 5000);
}

function createAlertContainer() {
    const container = document.createElement('div');
    container.id = 'alert-container';
    container.style.cssText = 'position: fixed; top: 80px; right: 20px; z-index: 1000; max-width: 400px;';
    document.body.appendChild(container);
    return container;
}

// Loading spinner
function showLoading(element) {
    if (!element) return;
    
    const loader = document.createElement('div');
    loader.className = 'loader';
    loader.id = 'main-loader';
    
    element.innerHTML = '';
    element.appendChild(loader);
    element.classList.add('show');
}

function hideLoading() {
    const loader = document.getElementById('main-loader');
    if (loader) {
        loader.remove();
    }
}

// Number counter animation
function animateCounter(element, target, duration = 2000) {
    const start = 0;
    const increment = target / (duration / 16);
    let current = start;

    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.textContent = target;
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current);
        }
    }, 16);
}

// Animate counters on page load
document.addEventListener('DOMContentLoaded', () => {
    const counters = document.querySelectorAll('.stat-value');
    counters.forEach(counter => {
        const target = parseInt(counter.textContent);
        if (!isNaN(target)) {
            counter.textContent = '0';
            animateCounter(counter, target);
        }
    });
});

// Intersection Observer for scroll animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.animation = 'fadeInUp 0.6s ease forwards';
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

document.addEventListener('DOMContentLoaded', () => {
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.style.opacity = '0';
        observer.observe(card);
    });
});

// Webcam access
async function startWebcam(videoElementId) {
    const video = document.getElementById(videoElementId);
    
    if (!video) return;

    try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
            video: { width: 1280, height: 720 } 
        });
        video.srcObject = stream;
        video.play();
        showAlert('Webcam started successfully', 'success');
    } catch (error) {
        showAlert('Error accessing webcam: ' + error.message, 'danger');
    }
}

function stopWebcam(videoElementId) {
    const video = document.getElementById(videoElementId);
    
    if (!video) return;

    const stream = video.srcObject;
    if (stream) {
        const tracks = stream.getTracks();
        tracks.forEach(track => track.stop());
        video.srcObject = null;
        showAlert('Webcam stopped', 'info');
    }
}

// Export functions for global access
window.FireDetection = {
    initializeFileUpload,
    detectImage,
    startVideoStream,
    stopVideoStream,
    showAlert,
    startWebcam,
    stopWebcam,
    animateCounter
};
