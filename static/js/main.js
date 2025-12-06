// Main Application
let uploadSession = null;

async function checkBackend() {
    const badge = document.getElementById('statusBadge');
    badge.textContent = '● Vérification...';
    badge.className = 'status-badge status-checking';
    
    try {
        const health = await api.healthCheck();
        if (health.status === 'healthy') {
            badge.textContent = '● En ligne';
            badge.className = 'status-badge status-online';
            addChatMessage('assistant', '✅ Backend connecté ! Kibalone Studio v2.0 prêt.');
        } else {
            badge.textContent = '● Hors ligne';
            badge.className = 'status-badge status-offline';
        }
    } catch (error) {
        badge.textContent = '● Hors ligne';
        badge.className = 'status-badge status-offline';
        addChatMessage('assistant', '⚠️ Backend hors ligne. Mode dégradé activé.');
    }
}

async function handleImageUpload(event) {
    const files = event.target.files;
    if (!files || files.length === 0) return;
    
    const progressBar = document.getElementById('uploadProgress');
    const progressFill = document.getElementById('progressFill');
    progressBar.style.display = 'block';
    progressFill.style.width = '0%';
    
    try {
        // Create session
        const sessionResponse = await api.createSession();
        uploadSession = sessionResponse.session_id;
        
        addChatMessage('assistant', `📤 Upload de ${files.length} image(s)...`);
        
        // Upload images
        for (let i = 0; i < files.length; i++) {
            await api.uploadImage(uploadSession, files[i]);
            const progress = ((i + 1) / files.length) * 50;
            progressFill.style.width = progress + '%';
        }
        
        addChatMessage('assistant', '🎨 Reconstruction 3D en cours...');
        
        // Reconstruct
        const result = await api.reconstruct(uploadSession);
        progressFill.style.width = '100%';
        
        addChatMessage('assistant', '✅ Reconstruction terminée !');
        
        setTimeout(() => {
            progressBar.style.display = 'none';
        }, 2000);
        
    } catch (error) {
        console.error('Upload error:', error);
        addChatMessage('assistant', '❌ Erreur lors de la reconstruction.', true);
        progressBar.style.display = 'none';
    }
    
    // Reset input
    event.target.value = '';
}

// Initialize on load
window.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Kibalone Studio v2.0 - Starting...');
    
    initScene();
    initGreasePencil();
    checkBackend();
    
    console.log('✅ Application ready!');
});
