/**
 * Debug Panel Module
 * Handles debug output display and formatting
 */

const DebugPanel = {
    /**
     * Initialize debug panel
     */
    init() {
        const panel = document.getElementById('debugPanel');
        if (panel) {
            console.log('Debug panel initialized');
            panel.style.display = 'block';
        }
    },
    
    /**
     * Update debug panel with new data
     */
    update(debugData) {
        const content = document.getElementById('debugContent');
        if (!content) return;
        
        let html = '';
        
        if (Array.isArray(debugData)) {
            debugData.forEach((item, index) => {
                html += this.formatDebugItem(item, index);
            });
        } else {
            html = this.formatDebugItem(debugData, 0);
        }
        
        content.innerHTML = html;
    },
    
    /**
     * Format a single debug item
     */
    formatDebugItem(item, index) {
        let html = `<div class="debug-section">`;
        html += `<h4>Image ${index + 1}</h4>`;
        
        // Vision API results
        if (item.vision_labels) {
            html += `<div class="debug-item">`;
            html += `<span class="debug-key">Vision Labels:</span>`;
            html += `<span class="debug-value">${item.vision_labels.join(', ')}</span>`;
            html += `</div>`;
        }
        
        if (item.vision_text) {
            html += `<div class="debug-item">`;
            html += `<span class="debug-key">Detected Text:</span>`;
            html += `<span class="debug-value">${item.vision_text}</span>`;
            html += `</div>`;
        }
        
        // Gemini prompt and response
        if (item.gemini_prompt) {
            html += `<div class="debug-item">`;
            html += `<span class="debug-key">AI Prompt:</span>`;
            html += `<span class="debug-value">${this.truncate(item.gemini_prompt, 200)}</span>`;
            html += `</div>`;
        }
        
        if (item.gemini_response) {
            html += `<div class="debug-item">`;
            html += `<span class="debug-key">AI Response:</span>`;
            html += `<span class="debug-value">${this.truncate(item.gemini_response, 500)}</span>`;
            html += `</div>`;
        }
        
        // Error information
        if (item.error_type) {
            html += `<div class="debug-item error">`;
            html += `<span class="debug-key">Error Type:</span>`;
            html += `<span class="debug-value">${item.error_type}</span>`;
            html += `</div>`;
        }
        
        if (item.error_message) {
            html += `<div class="debug-item error">`;
            html += `<span class="debug-key">Error Message:</span>`;
            html += `<span class="debug-value">${item.error_message}</span>`;
            html += `</div>`;
        }
        
        html += `</div>`;
        return html;
    },
    
    /**
     * Truncate long strings
     */
    truncate(str, maxLength) {
        if (!str) return 'N/A';
        if (str.length <= maxLength) return str;
        return str.substring(0, maxLength) + '...';
    },
    
    /**
     * Clear debug panel
     */
    clear() {
        const content = document.getElementById('debugContent');
        if (content) {
            content.innerHTML = '<p class="debug-placeholder">Debug information will appear here after processing...</p>';
        }
    }
};
