/**
 * Main Application JavaScript
 * Handles core application logic and initialization
 */

// Global state
const AppState = {
    selectedFiles: [],
    isProcessing: false,
    debugEnabled: false
};

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing eBay Auto Parts Lister...');
    
    // Initialize modules
    UploadHandler.init();
    DebugPanel.init();
    
    // Setup event listeners
    setupEventListeners();
    
    // Check for debug mode
    AppState.debugEnabled = document.getElementById('debugPanel') !== null;
    
    console.log('Application initialized successfully');
});

/**
 * Setup global event listeners
 */
function setupEventListeners() {
    // Process button
    const processBtn = document.getElementById('processBtn');
    if (processBtn) {
        processBtn.addEventListener('click', handleProcessImages);
    }
    
    // Clear button
    const clearBtn = document.getElementById('clearBtn');
    if (clearBtn) {
        clearBtn.addEventListener('click', handleClearFiles);
    }
    
    // Test eBay button
    const testEbayBtn = document.getElementById('testEbayBtn');
    if (testEbayBtn) {
        testEbayBtn.addEventListener('click', handleTestEbay);
    }
}

/**
 * Handle process images button click
 */
async function handleProcessImages() {
    if (AppState.selectedFiles.length === 0) {
        alert('Please select at least one image');
        return;
    }
    
    // Show loading overlay
    showLoading(true);
    AppState.isProcessing = true;
    
    // Prepare form data
    const formData = new FormData();
    AppState.selectedFiles.forEach(file => {
        formData.append('files', file);
    });
    
    try {
        // Send to server
        const response = await fetch('/process-images', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        // Debug logging
        console.log('API Response:', result);
        if (result.results && result.results.length > 0) {
            console.log('First result:', result.results[0]);
            console.log('Part name type:', typeof result.results[0].part_name);
            console.log('Part name value:', result.results[0].part_name);
        }
        
        if (result.success) {
            displayResults(result.results);
            
            // Update debug panel if enabled
            if (AppState.debugEnabled && result.debug_output) {
                DebugPanel.update(result.debug_output);
            }
        } else {
            alert('Error processing images: ' + (result.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to process images: ' + error.message);
    } finally {
        showLoading(false);
        AppState.isProcessing = false;
    }
}

/**
 * Handle clear files button click
 */
function handleClearFiles() {
    AppState.selectedFiles = [];
    UploadHandler.clearDisplay();
    updateButtonStates();
}

/**
 * Handle test eBay connection
 */
async function handleTestEbay() {
    try {
        const response = await fetch('/test-ebay');
        const result = await response.json();
        
        if (result.success) {
            alert('✅ eBay Connection Successful!\n\n' + result.message);
        } else {
            alert('❌ eBay Connection Failed\n\n' + result.message);
        }
    } catch (error) {
        alert('Error testing eBay connection: ' + error.message);
    }
}

/**
 * Display processing results
 */
function displayResults(results) {
    const resultsDiv = document.getElementById('results');
    if (!resultsDiv) return;
    
    let html = '<h2>Processing Results</h2>';
    html += '<div class="results-grid">';
    
    results.forEach((result, index) => {
        html += `
            <div class="result-card">
                <h3>Image ${index + 1}: ${result.filename}</h3>
                <div class="result-details">
                    <p><strong>Part Name:</strong> ${result.part_name}</p>
                    <p><strong>Part Number:</strong> ${result.part_number}</p>
                    <p><strong>Category:</strong> ${result.category}</p>
                    <p><strong>Condition:</strong> ${result.condition}</p>
                    <p><strong>Description:</strong> ${result.description}</p>
                    ${result.compatibility && result.compatibility.length > 0 ? 
                        `<p><strong>Compatible With:</strong><br>${result.compatibility.join('<br>')}</p>` : ''}
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    resultsDiv.innerHTML = html;
    resultsDiv.style.display = 'block';
}

/**
 * Update button states based on selected files
 */
function updateButtonStates() {
    const processBtn = document.getElementById('processBtn');
    const clearBtn = document.getElementById('clearBtn');
    
    if (processBtn) {
        processBtn.disabled = AppState.selectedFiles.length === 0 || AppState.isProcessing;
    }
    
    if (clearBtn) {
        clearBtn.style.display = AppState.selectedFiles.length > 0 ? 'inline-block' : 'none';
    }
}

/**
 * Show/hide loading overlay
 */
function showLoading(show) {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.display = show ? 'flex' : 'none';
    }
}
