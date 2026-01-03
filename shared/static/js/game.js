/**
 * Shared Game JavaScript for Multi-Language Wordle
 * Contains common functionality used across all language versions.
 * Language-specific code (keyboard layouts, etc.) should be in language-specific files.
 */

// ============================================================================
// MODAL FUNCTIONALITY
// ============================================================================

function initModal() {
    const helpBtn = document.getElementById('help-btn');
    const modal = document.getElementById('help-modal');
    const closeBtn = document.getElementById('close-modal');

    if (!helpBtn || !modal || !closeBtn) return;

    helpBtn.addEventListener('click', () => {
        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
    });

    closeBtn.addEventListener('click', () => {
        modal.classList.remove('show');
        document.body.style.overflow = '';
    });

    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('show');
            document.body.style.overflow = '';
        }
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.classList.contains('show')) {
            modal.classList.remove('show');
            document.body.style.overflow = '';
        }
    });
}

// ============================================================================
// COUNTDOWN TIMER
// ============================================================================

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

function initCountdown() {
    if (document.getElementById('countdown')) {
        updateCountdown();
        setInterval(updateCountdown, 1000);
    }
}

// ============================================================================
// SHARE FUNCTIONALITY
// ============================================================================

/**
 * Share game result
 * @param {string} appName - The app name to use in share text
 */
function shareResult(appName = 'Wordle') {
    const guessRows = document.querySelectorAll('.guess-row.submitted');
    const gameResult = document.querySelector('.game-result');
    const isWin = gameResult && gameResult.classList.contains('win');

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

    const shareText = `${appName} ${today}
${isWin ? attempts : 'X'}/${maxAttempts}

${emojiGrid}
🔤 Play at: ${window.location.origin}`;

    if (navigator.share) {
        navigator.share({
            title: appName,
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
        showToast('✓ Result copied to clipboard!');
    }).catch(() => {
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        try {
            document.execCommand('copy');
            showToast('✓ Result copied to clipboard!');
        } catch (err) {
            showToast('❌ Failed to copy');
        }
        document.body.removeChild(textarea);
    });
}

function showToast(message) {
    const existingToast = document.querySelector('.toast');
    if (existingToast) {
        existingToast.remove();
    }

    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    toast.style.animation = 'toastIn 0.3s ease';

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'toastOut 0.3s ease';
        setTimeout(() => {
            if (document.body.contains(toast)) {
                document.body.removeChild(toast);
            }
        }, 300);
    }, 2500);
}

// ============================================================================
// KEYBOARD FUNCTIONALITY
// ============================================================================

/**
 * Initialize keyboard with given letter statuses
 * @param {Object} letterStatuses - Map of letter -> status (correct, present, absent)
 */
function updateKeyboardStatuses(letterStatuses) {
    const keys = document.querySelectorAll('.key[data-key]');
    keys.forEach(key => {
        const letter = key.dataset.key;
        if (letterStatuses[letter]) {
            // Priority: correct > present > absent
            const currentStatus = key.classList.contains('correct') ? 'correct' :
                                  key.classList.contains('present') ? 'present' :
                                  key.classList.contains('absent') ? 'absent' : null;
            const newStatus = letterStatuses[letter];
            
            if (currentStatus !== 'correct') {
                if (newStatus === 'correct' || 
                    (newStatus === 'present' && currentStatus !== 'present') ||
                    (newStatus === 'absent' && !currentStatus)) {
                    key.classList.remove('correct', 'present', 'absent');
                    key.classList.add(newStatus);
                }
            }
        }
    });
}

/**
 * Initialize on-screen keyboard events
 */
function initKeyboard() {
    const keyboard = document.getElementById('keyboard');
    const guessInput = document.getElementById('guess-input');
    const guessForm = document.getElementById('guess-form');
    
    if (!keyboard || !guessInput) return;

    keyboard.addEventListener('click', (e) => {
        const key = e.target.closest('.key');
        if (!key) return;

        const keyValue = key.dataset.key;
        
        if (keyValue === 'ENTER') {
            if (guessForm) {
                guessForm.submit();
            }
        } else if (keyValue === 'BACKSPACE') {
            guessInput.value = guessInput.value.slice(0, -1);
            guessInput.focus();
        } else if (keyValue) {
            guessInput.value += keyValue;
            guessInput.focus();
        }
    });

    // Initialize keyboard colors from existing guesses
    initKeyboardColorsFromGuesses();
}

/**
 * Read existing guess feedback and update keyboard colors
 */
function initKeyboardColorsFromGuesses() {
    const letterStatuses = {};
    const guessRows = document.querySelectorAll('.guess-row.submitted');
    
    guessRows.forEach(row => {
        const tiles = row.querySelectorAll('.tile');
        tiles.forEach(tile => {
            const letter = tile.textContent.trim();
            if (!letter) return;
            
            const status = tile.classList.contains('correct') ? 'correct' :
                          tile.classList.contains('present') ? 'present' :
                          tile.classList.contains('absent') ? 'absent' : null;
            
            if (status) {
                // Only upgrade status (correct > present > absent)
                const currentStatus = letterStatuses[letter];
                if (!currentStatus || 
                    status === 'correct' || 
                    (status === 'present' && currentStatus === 'absent')) {
                    letterStatuses[letter] = status;
                }
            }
        });
    });
    
    updateKeyboardStatuses(letterStatuses);
}

// ============================================================================
// AJAX FORM SUBMISSION (Optional enhancement)
// ============================================================================

/**
 * Initialize AJAX form submission for smoother UX
 * Falls back to regular form submission if needed
 */
function initAjaxForm() {
    const form = document.getElementById('guess-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(form);
        const guessInput = document.getElementById('guess-input');
        
        try {
            const response = await fetch('/api/guess', {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                const data = await response.json();
                
                if (data.success) {
                    // Update UI with response
                    updateGameUI(data);
                    guessInput.value = '';
                } else if (data.error) {
                    showToast(data.error);
                }
            } else {
                // Fallback to regular submission
                form.submit();
            }
        } catch (err) {
            // Fallback to regular submission on error
            form.submit();
        }
    });
}

/**
 * Update game UI after AJAX response
 * @param {Object} data - Response data from /api/guess
 */
function updateGameUI(data) {
    // This is a simplified version - the full implementation would update
    // the guess grid, game status, etc. For now, we reload for simplicity.
    window.location.reload();
}

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    initModal();
    initCountdown();
    initKeyboard();
    // Optionally enable AJAX form:
    // initAjaxForm();
});

// Export functions for use by language-specific scripts
window.WordleShared = {
    shareResult,
    showToast,
    updateKeyboardStatuses,
    initKeyboardColorsFromGuesses
};
