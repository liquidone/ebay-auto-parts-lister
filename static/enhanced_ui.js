/**
 * Enhanced UI for Multi-Phase Part Identification
 * Provides smart fallback options and confidence indicators
 */

class EnhancedPartIdentifier {
    constructor() {
        this.currentResult = null;
        this.featureFlags = {};
        this.loadFeatureFlags();
    }

    async loadFeatureFlags() {
        try {
            const response = await fetch('/feature-flags');
            this.featureFlags = await response.json();
            this.updateUIBasedOnFlags();
        } catch (error) {
            console.error('Failed to load feature flags:', error);
        }
    }

    updateUIBasedOnFlags() {
        const enhancedFeaturesDiv = document.getElementById('enhanced-features');
        if (enhancedFeaturesDiv) {
            enhancedFeaturesDiv.style.display = this.featureFlags.enhanced_ui_enabled ? 'block' : 'none';
        }

        const browserFallbackDiv = document.getElementById('browser-fallback-section');
        if (browserFallbackDiv) {
            browserFallbackDiv.style.display = this.featureFlags.browser_fallback_enabled ? 'block' : 'none';
        }
    }

    async enhancedIdentify(file, forceFallback = false) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('force_fallback', forceFallback);

        try {
            this.showLoadingState('Analyzing with enhanced AI...');
            
            const response = await fetch('/enhanced-identify', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            this.currentResult = result;
            
            if (result.success) {
                this.displayEnhancedResult(result);
            } else {
                this.displayError(result.error, result.fallback_available);
            }

        } catch (error) {
            console.error('Enhanced identification failed:', error);
            this.displayError(error.message, false);
        }
    }

    displayEnhancedResult(result) {
        const resultData = result.result;
        const recommendations = result.recommendations;

        // Create enhanced result display
        const resultHTML = `
            <div class="enhanced-result-container">
                <div class="result-header">
                    <h3>🔍 Enhanced Analysis Results</h3>
                    <div class="confidence-indicator ${this.getConfidenceClass(resultData.confidence_score)}">
                        <span class="confidence-score">${Math.round(resultData.confidence_score * 100)}%</span>
                        <span class="confidence-label">${recommendations.confidence_level.toUpperCase()}</span>
                    </div>
                </div>

                <div class="result-details">
                    <div class="part-info">
                        <h4>Part Information</h4>
                        <p><strong>Name:</strong> ${resultData.part_name}</p>
                        <p><strong>Part Number:</strong> ${resultData.part_number || 'Not found'}</p>
                        <p><strong>Method:</strong> ${resultData.method_used}</p>
                        <p><strong>Description:</strong> ${resultData.description}</p>
                    </div>

                    ${this.createIssuesSection(resultData.issues)}
                    ${this.createRecommendationsSection(recommendations)}
                </div>

                ${this.createActionButtons(recommendations.needs_fallback)}
            </div>
        `;

        document.getElementById('enhanced-results').innerHTML = resultHTML;
        this.hideLoadingState();
    }

    getConfidenceClass(score) {
        if (score > 0.8) return 'confidence-high';
        if (score > 0.5) return 'confidence-medium';
        return 'confidence-low';
    }

    createIssuesSection(issues) {
        if (!issues || issues.length === 0) {
            return '<div class="issues-section success">✅ No issues detected</div>';
        }

        const issuesList = issues.map(issue => `<li>${issue}</li>`).join('');
        return `
            <div class="issues-section warning">
                <h4>⚠️ Issues Detected</h4>
                <ul>${issuesList}</ul>
            </div>
        `;
    }

    createRecommendationsSection(recommendations) {
        const actionsList = recommendations.suggested_actions.map(action => `<li>${action}</li>`).join('');
        return `
            <div class="recommendations-section">
                <h4>💡 Recommendations</h4>
                <ul>${actionsList}</ul>
            </div>
        `;
    }

    createActionButtons(needsFallback) {
        let buttons = `
            <div class="action-buttons">
                <button onclick="enhancedUI.useResult()" class="btn-primary">
                    ✅ Use This Result
                </button>
                <button onclick="enhancedUI.manualEntry()" class="btn-secondary">
                    ✏️ Manual Entry
                </button>
        `;

        if (needsFallback && this.featureFlags.browser_fallback_enabled) {
            buttons += `
                <button onclick="enhancedUI.tryBrowserFallback()" class="btn-fallback">
                    🔍 Try Enhanced Analysis
                </button>
            `;
        }

        buttons += '</div>';
        return buttons;
    }

    async tryBrowserFallback() {
        if (!this.currentFile) {
            alert('Please upload an image first');
            return;
        }

        const confirmed = confirm(
            'Enhanced analysis uses browser automation for better accuracy.\n' +
            'This may take longer. Continue?'
        );

        if (confirmed) {
            await this.enhancedIdentify(this.currentFile, true);
        }
    }

    useResult() {
        if (!this.currentResult) return;

        // Populate the main form with the enhanced result
        const resultData = this.currentResult.result;
        
        document.getElementById('part-name').value = resultData.part_name || '';
        document.getElementById('part-number').value = resultData.part_number || '';
        document.getElementById('description').value = resultData.description || '';
        
        // Show success message
        this.showMessage('Result applied to form!', 'success');
    }

    manualEntry() {
        // Clear form and focus on part name field
        document.getElementById('part-name').value = '';
        document.getElementById('part-number').value = '';
        document.getElementById('description').value = '';
        
        document.getElementById('part-name').focus();
        this.showMessage('Manual entry mode - please fill in the details', 'info');
    }

    showLoadingState(message) {
        const loadingHTML = `
            <div class="loading-state">
                <div class="spinner"></div>
                <p>${message}</p>
            </div>
        `;
        document.getElementById('enhanced-results').innerHTML = loadingHTML;
    }

    hideLoadingState() {
        // Loading state is replaced by results
    }

    displayError(error, fallbackAvailable) {
        const errorHTML = `
            <div class="error-state">
                <h3>❌ Analysis Failed</h3>
                <p>${error}</p>
                ${fallbackAvailable ? 
                    '<button onclick="enhancedUI.tryBrowserFallback()" class="btn-fallback">Try Browser Fallback</button>' : 
                    '<p>No fallback options available</p>'
                }
            </div>
        `;
        document.getElementById('enhanced-results').innerHTML = errorHTML;
    }

    showMessage(message, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        messageDiv.textContent = message;
        
        document.body.appendChild(messageDiv);
        
        setTimeout(() => {
            messageDiv.remove();
        }, 3000);
    }

    // Rollback functions
    async toggleFeature(featureName, enabled) {
        try {
            const response = await fetch('/toggle-feature', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    feature_name: featureName,
                    enabled: enabled
                })
            });

            const result = await response.json();
            
            if (result.success) {
                this.showMessage(result.message, 'success');
                await this.loadFeatureFlags(); // Reload flags
            } else {
                this.showMessage(result.error, 'error');
            }

        } catch (error) {
            console.error('Failed to toggle feature:', error);
            this.showMessage('Failed to toggle feature', 'error');
        }
    }

    // Emergency rollback - disable all enhanced features
    async emergencyRollback() {
        const confirmed = confirm(
            'This will disable all enhanced features and revert to basic mode.\n' +
            'Are you sure?'
        );

        if (confirmed) {
            await this.toggleFeature('enable_browser_fallback', false);
            await this.toggleFeature('enable_enhanced_prompts', false);
            await this.toggleFeature('enable_fallback_ui', false);
            
            this.showMessage('Emergency rollback completed - basic mode active', 'warning');
        }
    }
}

// Global instance
const enhancedUI = new EnhancedPartIdentifier();

// Enhanced file upload handler
function handleEnhancedUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    enhancedUI.currentFile = file;
    
    // Show preview
    const reader = new FileReader();
    reader.onload = function(e) {
        document.getElementById('image-preview').innerHTML = 
            `<img src="${e.target.result}" alt="Preview" style="max-width: 300px; max-height: 300px;">`;
    };
    reader.readAsDataURL(file);

    // Start enhanced analysis
    enhancedUI.enhancedIdentify(file);
}

// CSS Styles (to be added to the HTML)
const enhancedStyles = `
<style>
.enhanced-result-container {
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 20px;
    margin: 20px 0;
    background: #f9f9f9;
}

.result-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.confidence-indicator {
    padding: 8px 16px;
    border-radius: 20px;
    font-weight: bold;
}

.confidence-high { background: #d4edda; color: #155724; }
.confidence-medium { background: #fff3cd; color: #856404; }
.confidence-low { background: #f8d7da; color: #721c24; }

.issues-section.warning {
    background: #fff3cd;
    border: 1px solid #ffeaa7;
    padding: 15px;
    border-radius: 5px;
    margin: 10px 0;
}

.issues-section.success {
    background: #d4edda;
    border: 1px solid #c3e6cb;
    padding: 15px;
    border-radius: 5px;
    margin: 10px 0;
}

.recommendations-section {
    background: #e2f3ff;
    border: 1px solid #bee5eb;
    padding: 15px;
    border-radius: 5px;
    margin: 10px 0;
}

.action-buttons {
    display: flex;
    gap: 10px;
    margin-top: 20px;
}

.btn-primary { background: #007bff; color: white; }
.btn-secondary { background: #6c757d; color: white; }
.btn-fallback { background: #28a745; color: white; }

.loading-state {
    text-align: center;
    padding: 40px;
}

.spinner {
    border: 4px solid #f3f3f3;
    border-top: 4px solid #3498db;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
    margin: 0 auto 20px;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.error-state {
    background: #f8d7da;
    border: 1px solid #f5c6cb;
    padding: 20px;
    border-radius: 5px;
    text-align: center;
}

.message {
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 15px;
    border-radius: 5px;
    z-index: 1000;
}

.message.success { background: #d4edda; color: #155724; }
.message.error { background: #f8d7da; color: #721c24; }
.message.info { background: #d1ecf1; color: #0c5460; }
.message.warning { background: #fff3cd; color: #856404; }
</style>
`;

// Add styles to document
document.head.insertAdjacentHTML('beforeend', enhancedStyles);
