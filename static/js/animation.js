// Animation System
let isPlaying = false;
let currentFrame = 0;
let totalFrames = 250;
let fps = 24;
let animationInterval = null;

function togglePlayPause() {
    isPlaying = !isPlaying;
    
    const playBtn = document.getElementById('playBtn');
    playBtn.textContent = isPlaying ? '⏸️' : '▶️';
    
    if (isPlaying) {
        startAnimation();
    } else {
        stopAnimation();
    }
}

function startAnimation() {
    if (animationInterval) return;
    
    const frameTime = 1000 / fps;
    animationInterval = setInterval(() => {
        currentFrame++;
        if (currentFrame > totalFrames) {
            currentFrame = 0;
        }
        updateFrameDisplay();
    }, frameTime);
}

function stopAnimation() {
    if (animationInterval) {
        clearInterval(animationInterval);
        animationInterval = null;
    }
}

function setFrame(frame) {
    currentFrame = parseInt(frame);
    updateFrameDisplay();
}

function resetFrame() {
    currentFrame = 0;
    updateFrameDisplay();
    stopAnimation();
    isPlaying = false;
    document.getElementById('playBtn').textContent = '▶️';
}

function updateFrameDisplay() {
    document.getElementById('currentFrame').textContent = currentFrame;
    document.getElementById('frameSlider').value = currentFrame;
    document.getElementById('frameInfo').textContent = `Frame: ${currentFrame} / ${totalFrames}`;
}
