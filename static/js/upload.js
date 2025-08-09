/**
 * Upload Handler Module
 * Manages file uploads, drag & drop, and image preview
 */

const UploadHandler = {
    /**
     * Initialize upload handler
     */
    init() {
        this.setupUploadArea();
        this.setupFileInput();
        this.setupDragAndDrop();
    },
    
    /**
     * Setup upload area click handler
     */
    setupUploadArea() {
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        
        if (uploadArea && fileInput) {
            uploadArea.addEventListener('click', function(e) {
                e.preventDefault();
                console.log('Upload area clicked - triggering file input');
                fileInput.click();
            });
        }
    },
    
    /**
     * Setup file input change handler
     */
    setupFileInput() {
        const fileInput = document.getElementById('fileInput');
        
        if (fileInput) {
            fileInput.addEventListener('change', function(e) {
                const files = Array.from(e.target.files);
                console.log(`${files.length} files selected`);
                UploadHandler.handleFiles(files);
            });
        }
    },
    
    /**
     * Setup drag and drop handlers
     */
    setupDragAndDrop() {
        const uploadArea = document.getElementById('uploadArea');
        
        if (!uploadArea) return;
        
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, preventDefaults, false);
            document.body.addEventListener(eventName, preventDefaults, false);
        });
        
        // Highlight drop area when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, unhighlight, false);
        });
        
        // Handle dropped files
        uploadArea.addEventListener('drop', handleDrop, false);
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        function highlight(e) {
            uploadArea.classList.add('dragover');
        }
        
        function unhighlight(e) {
            uploadArea.classList.remove('dragover');
        }
        
        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = Array.from(dt.files);
            console.log(`${files.length} files dropped`);
            UploadHandler.handleFiles(files);
        }
    },
    
    /**
     * Handle selected/dropped files
     */
    handleFiles(files) {
        // Filter for image files only
        const imageFiles = files.filter(file => file.type.startsWith('image/'));
        
        if (imageFiles.length !== files.length) {
            alert('Only image files are allowed');
        }
        
        // Check file count limit
        const maxFiles = 24;
        if (imageFiles.length > maxFiles) {
            alert(`Maximum ${maxFiles} files allowed. You selected ${imageFiles.length}`);
            return;
        }
        
        // Update global state
        AppState.selectedFiles = imageFiles;
        
        // Display selected files
        this.displaySelectedFiles(imageFiles);
        
        // Update button states
        updateButtonStates();
    },
    
    /**
     * Display selected files with previews
     */
    displaySelectedFiles(files) {
        const uploadArea = document.getElementById('uploadArea');
        const fileCount = document.getElementById('fileCount');
        
        if (!uploadArea) return;
        
        // Update file count
        if (fileCount) {
            fileCount.textContent = `${files.length} file(s) selected`;
        }
        
        // Create image grid
        let html = '<div class="image-grid">';
        
        files.forEach((file, index) => {
            const url = URL.createObjectURL(file);
            html += `
                <div class="image-box">
                    <img src="${url}" alt="${file.name}" title="${file.name}">
                    <div class="image-name">${file.name}</div>
                </div>
            `;
        });
        
        html += '</div>';
        html += '<p class="upload-hint">Click to add more or drag & drop</p>';
        
        uploadArea.innerHTML = html;
        
        // Re-attach click handler to the new content
        uploadArea.addEventListener('click', function(e) {
            // Don't trigger if clicking on an image
            if (e.target.tagName !== 'IMG') {
                document.getElementById('fileInput').click();
            }
        });
    },
    
    /**
     * Clear file display
     */
    clearDisplay() {
        const uploadArea = document.getElementById('uploadArea');
        const fileCount = document.getElementById('fileCount');
        const fileInput = document.getElementById('fileInput');
        
        if (uploadArea) {
            uploadArea.innerHTML = `
                <p><strong>🖱️ CLICK HERE TO SELECT IMAGES</strong></p>
                <p>📁 Select up to 24 auto part images</p>
                <p class="upload-hint">Click to browse or drag & drop images here</p>
            `;
        }
        
        if (fileCount) {
            fileCount.textContent = '';
        }
        
        if (fileInput) {
            fileInput.value = '';
        }
        
        // Clear results
        const results = document.getElementById('results');
        if (results) {
            results.innerHTML = '';
            results.style.display = 'none';
        }
    }
};
