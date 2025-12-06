// Chat System
let chatMessages = [];
let isProcessing = false;

function addChatMessage(role, content, isError = false) {
    const message = {
        role,
        content,
        timestamp: Date.now(),
        isError
    };
    
    chatMessages.push(message);
    renderChatMessages();
}

function renderChatMessages() {
    const container = document.getElementById('chatMessages');
    
    if (chatMessages.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <p>👋 Salut ! Je suis Kibali.</p>
                <p class="hint">Essayez:</p>
                <ul class="hint-list">
                    <li>"Crée un cube"</li>
                    <li>"Dessine un cercle"</li>
                    <li>"Reconstruction 3D"</li>
                    <li>"Anime l'objet"</li>
                </ul>
            </div>
        `;
        return;
    }
    
    container.innerHTML = '';
    
    chatMessages.forEach(msg => {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${msg.role}`;
        if (msg.isError) messageDiv.classList.add('message-error');
        
        messageDiv.innerHTML = `
            <div class="message-header">
                <span>${msg.role === 'user' ? '👤 Vous' : '🤖 Kibali'}</span>
            </div>
            <div class="message-content">${msg.content}</div>
        `;
        
        container.appendChild(messageDiv);
    });
    
    // Scroll to bottom
    container.scrollTop = container.scrollHeight;
}

async function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message || isProcessing) return;
    
    // Add user message
    addChatMessage('user', message);
    input.value = '';
    isProcessing = true;
    
    try {
        // Analyze intent
        const analysis = await api.analyzePrompt(message);
        
        // Send to chat
        const response = await api.sendMessage(message, { intent: analysis.intent });
        
        // Add assistant response
        addChatMessage('assistant', response.response || response.message || 'Commande exécutée');
        
        // Execute action
        await executeCommand(message, analysis.intent);
        
    } catch (error) {
        console.error('Chat error:', error);
        addChatMessage('assistant', 'Erreur lors du traitement de votre message.', true);
    } finally {
        isProcessing = false;
    }
}

async function executeCommand(message, intent) {
    const lowerMsg = message.toLowerCase();
    
    // CREATE_OBJECT
    if (lowerMsg.includes('cube') || lowerMsg.includes('boite')) {
        addObject('cube');
    } else if (lowerMsg.includes('sphere') || lowerMsg.includes('boule')) {
        addObject('sphere');
    } else if (lowerMsg.includes('cylinder') || lowerMsg.includes('cylindre')) {
        addObject('cylinder');
    }
    
    // DRAW
    if (lowerMsg.includes('dessin') || lowerMsg.includes('dessine')) {
        setDrawMode('draw');
        addChatMessage('assistant', '✏️ Mode dessin activé. Cliquez et faites glisser dans la scène.');
    }
    
    // RECONSTRUCTION
    if (lowerMsg.includes('reconstruction') || lowerMsg.includes('3d')) {
        addChatMessage('assistant', '🚀 Utilisez le panneau de droite pour uploader des images.');
    }
}

function handleChatKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

function clearChat() {
    chatMessages = [];
    renderChatMessages();
}
