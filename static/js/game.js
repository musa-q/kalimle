/**
 * Arabic Wordle - Minimal Vanilla JavaScript
 * Only handles: countdown timer and share functionality
 * All game logic is server-side
 */

// Countdown timer until next puzzle
function updateCountdown() {
    const countdownEl = document.getElementById('countdown');
    if (!countdownEl) return;

    const now = new Date();
    const tomorrow = new Date(now);
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(0, 0, 0, 0);
    
    const diff = tomorrow - now;
    
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((diff % (1000 * 60)) / 1000);
    
    countdownEl.textContent = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}

// Start countdown if element exists
if (document.getElementById('countdown')) {
    updateCountdown();
    setInterval(updateCountdown, 1000);
}

// Share result function
function shareResult() {
    const guessRows = document.querySelectorAll('.guess-row.submitted');
    const gameResult = document.querySelector('.game-result');
    const isWin = gameResult && gameResult.classList.contains('win');
    
    // Build emoji grid
    let emojiGrid = '';
    guessRows.forEach(row => {
        const tiles = row.querySelectorAll('.tile');
        tiles.forEach(tile => {
            if (tile.classList.contains('correct')) {
                emojiGrid += '🟩';
            } else if (tile.classList.contains('present')) {
                emojiGrid += '🟨';
            } else if (tile.classList.contains('absent')) {
                emojiGrid += '⬛';
            }
        });
        emojiGrid += '\n';
    });
    
    const today = new Date().toISOString().split('T')[0];
    const attempts = guessRows.length;
    const maxAttempts = 6;
    
    const shareText = `Arabic Wordle ${today}
${isWin ? attempts : 'X'}/${maxAttempts}

${emojiGrid}
🔤 Play at: ${window.location.origin}`;
    
    // Try to use native share API, fall back to clipboard
    if (navigator.share) {
        navigator.share({
            title: 'Arabic Wordle',
            text: shareText
        }).catch(() => {
            copyToClipboard(shareText);
        });
    } else {
        copyToClipboard(shareText);
    }
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Result copied to clipboard!');
    }).catch(() => {
        // Fallback for older browsers
        const textarea = document.createElement('textarea');
        textarea.value = text;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        showToast('Result copied to clipboard!');
    });
}

function showToast(message) {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: #ffffff;
        color: #121213;
        padding: 16px 24px;
        border-radius: 8px;
        font-weight: 600;
        z-index: 1000;
        animation: fadeIn 0.3s ease;
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, 2000);
}

// Add animation keyframes dynamically
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeIn {
        from { opacity: 0; transform: translateX(-50%) translateY(20px); }
        to { opacity: 1; transform: translateX(-50%) translateY(0); }
    }
    @keyframes fadeOut {
        from { opacity: 1; transform: translateX(-50%) translateY(0); }
        to { opacity: 0; transform: translateX(-50%) translateY(20px); }
    }
`;
document.head.appendChild(style);

// Focus input on page load
document.addEventListener('DOMContentLoaded', function() {
    const input = document.getElementById('guess-input');
    if (input) {
        input.focus();
    }
    
    // Initialize keyboard
    initKeyboard();
});

// On-screen keyboard functionality
function initKeyboard() {
    const keyboard = document.getElementById('keyboard');
    const input = document.getElementById('guess-input');
    const form = document.getElementById('guess-form');
    
    if (!keyboard || !input) return;
    
    keyboard.addEventListener('click', function(e) {
        const key = e.target.closest('.key');
        if (!key) return;
        
        const keyValue = key.dataset.key;
        
        if (keyValue === 'ENTER') {
            // Submit the form
            if (input.value.trim()) {
                form.submit();
            }
        } else if (keyValue === 'BACKSPACE') {
            // Remove last character
            input.value = input.value.slice(0, -1);
        } else {
            // Add the letter
            input.value += keyValue;
        }
        
        // Keep focus on input
        input.focus();
    });
    
    // Update keyboard colors based on previous guesses
    updateKeyboardColors();
}

function updateKeyboardColors() {
    const keyboard = document.getElementById('keyboard');
    if (!keyboard) return;
    
    const keys = keyboard.querySelectorAll('.key');
    const guessRows = document.querySelectorAll('.guess-row.submitted');
    
    // Track letter statuses (correct > present > absent)
    const letterStatus = {};
    
    guessRows.forEach(row => {
        const tiles = row.querySelectorAll('.tile');
        tiles.forEach(tile => {
            const letter = tile.textContent.trim();
            const status = tile.classList.contains('correct') ? 'correct' :
                          tile.classList.contains('present') ? 'present' : 'absent';
            
            // Only upgrade status (correct > present > absent)
            if (!letterStatus[letter] || 
                (status === 'correct') ||
                (status === 'present' && letterStatus[letter] === 'absent')) {
                letterStatus[letter] = status;
            }
        });
    });
    
    // Apply colors to keyboard
    keys.forEach(key => {
        const keyLetter = key.dataset.key;
        if (letterStatus[keyLetter]) {
            key.classList.remove('correct', 'present', 'absent');
            key.classList.add(letterStatus[keyLetter]);
        }
    });
}
