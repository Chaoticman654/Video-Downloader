let isDownloading = false;

async function download() {
    const url = document.getElementById('url').value.trim();
    const status = document.getElementById('status');
    
    if (!url) {
        showStatus('Please enter a URL!', 'error');
        return;
    }
    
    if (isDownloading) return;
    
    isDownloading = true;
    status.className = 'status loading';
    showStatus(`
        <div class="progress-container">
            <div class="progress-bar">
                <div class="progress-fill"></div>
            </div>
            <div class="progress-text">Analyzing video...</div>
        </div>
    `, 'loading');
    
    try {
        const response = await fetch('/download', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({url})
        });
        
        if (!response.ok) throw new Error(await response.text());
        
        const data = await response.json();
        showStatus(`${data.title || 'Video'} downloaded successfully!`, 'success');
        loadFiles();
        document.getElementById('url').value = '';
    } catch (error) {
        showStatus(` ${error.message}`, 'error');
    } finally {
        isDownloading = false;
    }
}

function showStatus(message, type) {
    const status = document.getElementById('status');
    status.innerHTML = message;
    status.className = `status ${type}`;
}

async function loadFiles() {
    try {
        const response = await fetch('/files');
        const data = await response.json();
        renderFiles(data.files);
    } catch (error) {
        console.error('Failed to load files:', error);
    }
}

function renderFiles(files) {
    const container = document.getElementById('files');
    
    if (!files || files.length === 0) {
        container.innerHTML = '<div class="empty-state"><p>No downloads yet.</p></div>';
        return;
    }
    
    container.innerHTML = files.map(file => `
        <div class="file-item">
            <div class="file-name">${file.name}</div>
            <button class="auto-download" data-url="${file.url}">
                <i class="fas fa-download"></i> Download to Device
            </button>
        </div>
    `).join('');
    
    // Auto-trigger downloads
    document.querySelectorAll('.auto-download').forEach(btn => {
        btn.addEventListener('click', function() {
            const url = this.dataset.url;
            const a = document.createElement('a');
            a.href = url;
            a.download = '';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        });
    });
}

document.getElementById('url').addEventListener('keypress', e => {
    if (e.key === 'Enter') download();
});

loadFiles();
setInterval(loadFiles, 5000);
