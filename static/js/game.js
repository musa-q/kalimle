/**
 * kalimle - Enhanced JavaScript with AJAX
 * Handles: countdown timer, share functionality, AJAX form submission, keyboard interactions, and modals
 * Game logic is server-side, but UI updates without page refresh
 */

// Help Modal functionality
function initModal() {
    const helpBtn = document.getElementById('help-btn');
    const modal = document.getElementById('help-modal');
    const closeBtn = document.getElementById('close-modal');

    if (!helpBtn || !modal || !closeBtn) return;

    // Open modal
    helpBtn.addEventListener('click', () => {
        modal.classList.add('show');
        document.body.style.overflow = 'hidden'; // Prevent background scroll
    });

    // Close modal
    closeBtn.addEventListener('click', () => {
        modal.classList.remove('show');
        document.body.style.overflow = ''; // Restore scroll
    });

    // Close modal when clicking outside
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('show');
            document.body.style.overflow = '';
        }
    });

    // Close modal on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.classList.contains('show')) {
            modal.classList.remove('show');
            document.body.style.overflow = '';
        }
    });
}

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

    const shareText = `kalimle ${today}
${isWin ? attempts : 'X'}/${maxAttempts}

${emojiGrid}
🔤 Play at: ${window.location.origin}`;

    // Try to use native share API, fall back to clipboard
    if (navigator.share) {
        navigator.share({
            title: 'kalimle',
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
        // Fallback for older browsers
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
    // Remove existing toast if any
    const existingToast = document.querySelector('.toast');
    if (existingToast) {
        existingToast.remove();
    }

    // Create toast element
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 80px;
        left: 50%;
        transform: translateX(-50%);
        background: #ffffff;
        color: #121213;
        padding: 16px 28px;
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.95rem;
        z-index: 1000;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
        animation: toastIn 0.3s ease;
        pointer-events: none;
    `;

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

// Add animation keyframes dynamically
const style = document.createElement('style');
style.textContent = `
    @keyframes toastIn {
        from {
            opacity: 0;
            transform: translateX(-50%) translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateX(-50%) translateY(0);
        }
    }
    @keyframes toastOut {
        from {
            opacity: 1;
            transform: translateX(-50%) translateY(0);
        }
        to {
            opacity: 0;
            transform: translateX(-50%) translateY(20px);
        }
    }
`;
document.head.appendChild(style);

// Focus input on page load
document.addEventListener('DOMContentLoaded', function () {
    // Initialize modal
    initModal();

    const input = document.getElementById('guess-input');
    if (input) {
        // Focus input
        input.focus();

        // Handle form submission with AJAX
        const form = document.getElementById('guess-form');
        if (form) {
            form.addEventListener('submit', function (e) {
                e.preventDefault(); // Prevent default form submission

                if (!input.value.trim()) {
                    showToast('⚠️ Please enter a word');
                    return;
                }

                // Submit via AJAX
                submitGuess(input.value.trim());
            });
        }
    }

    // Initialize keyboard
    initKeyboard();

    // Add smooth scroll behavior
    document.documentElement.style.scrollBehavior = 'smooth';
});

// Submit guess via AJAX
async function submitGuess(guess) {
    const input = document.getElementById('guess-input');
    const submitBtn = document.querySelector('.btn-submit');

    // Disable input during submission
    if (input) input.disabled = true;
    if (submitBtn) submitBtn.disabled = true;

    try {
        const formData = new FormData();
        formData.append('guess', guess);

        const response = await fetch('/api/guess', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            // Show error message
            showError(data.error || 'An error occurred');
            return;
        }

        // Update the UI with the response
        updateGameUI(data);

        // Clear input
        if (input) input.value = '';

    } catch (error) {
        console.error('Error submitting guess:', error);
        showError('Failed to submit guess. Please try again.');
    } finally {
        // Re-enable input
        if (input) {
            input.disabled = false;
            input.focus();
        }
        if (submitBtn) submitBtn.disabled = false;
    }
}

// Update the game UI with new data
function updateGameUI(data) {
    // Add new guess row
    addGuessRow(data.feedback);

    // Update remaining guesses
    const remainingEl = document.querySelector('.remaining');
    if (remainingEl) {
        remainingEl.textContent = `📊 ${data.remaining_guesses} guesses remaining`;
    }

    // Update keyboard colors
    updateKeyboardColors();

    // Clear any error messages
    const errorEl = document.querySelector('.error-message');
    if (errorEl) {
        errorEl.remove();
    }

    // Check if game is over
    if (data.game_over) {
        showGameResult(data);
    }
}

// Add a new guess row to the display
function addGuessRow(feedback) {
    const guessesContainer = document.querySelector('.guesses-container');
    if (!guessesContainer) return;

    // Find the first empty row
    const emptyRow = guessesContainer.querySelector('.guess-row.empty');
    if (!emptyRow) return;

    // Remove empty class and add submitted class
    emptyRow.classList.remove('empty');
    emptyRow.classList.add('submitted');

    // Clear existing tiles
    emptyRow.innerHTML = '';

    // Add feedback tiles with animation
    feedback.forEach((tile, index) => {
        const tileEl = document.createElement('div');
        tileEl.className = `tile ${tile.status}`;
        tileEl.textContent = tile.letter;
        tileEl.style.animationDelay = `${index * 0.1}s`;
        emptyRow.appendChild(tileEl);
    });
}

// Show error message
function showError(message) {
    // Remove existing error if any
    const existingError = document.querySelector('.error-message');
    if (existingError) {
        existingError.remove();
    }

    // Create new error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;

    // Insert after sentence card
    const sentenceCard = document.querySelector('.sentence-card');
    if (sentenceCard) {
        sentenceCard.insertAdjacentElement('afterend', errorDiv);
    }
}

// Show game result (win/lose)
function showGameResult(data) {
    const main = document.querySelector('main');
    if (!main) return;

    // Hide form and keyboard
    const form = document.querySelector('.guess-form');
    const keyboard = document.querySelector('.keyboard');
    if (form) form.style.display = 'none';
    if (keyboard) keyboard.style.display = 'none';

    // Create result section
    const resultDiv = document.createElement('div');
    resultDiv.className = `game-result ${data.won ? 'win' : 'lose'}`;

    const guessCount = document.querySelectorAll('.guess-row.submitted').length;

    resultDiv.innerHTML = `
        ${data.won ? '<h2>🎉 Congratulations!</h2>' : '<h2>😔 Game Over</h2>'}
        ${data.won ? `<p>You guessed it in ${guessCount} ${guessCount === 1 ? 'try' : 'tries'}!</p>` : '<p>Better luck tomorrow!</p>'}

        <div class="answer-reveal">
            <h3>The Answer</h3>
            <div class="answer-word" dir="rtl">${data.target}</div>
            <p class="pronunciation">${data.pronunciation} - "${data.meaning}"</p>
            <p class="example" dir="rtl">${data.example}</p>
        </div>

        <div class="share-section">
            <button id="share-btn" class="btn btn-share" onclick="shareResult()" aria-label="Share your result">
                📤 Share Result
            </button>
            <p class="next-puzzle-info">⏰ Next puzzle in: <span id="countdown"></span></p>
        </div>
    `;

    // Insert result after guesses container
    const guessesContainer = document.querySelector('.guesses-container');
    if (guessesContainer) {
        guessesContainer.insertAdjacentElement('afterend', resultDiv);
    }

    // Start countdown timer
    updateCountdown();
    setInterval(updateCountdown, 1000);
}

// On-screen keyboard functionality
function initKeyboard() {
    const keyboard = document.getElementById('keyboard');
    const input = document.getElementById('guess-input');
    const form = document.getElementById('guess-form');

    if (!keyboard || !input) return;

    // Handle keyboard clicks
    keyboard.addEventListener('click', function (e) {
        const key = e.target.closest('.key');
        if (!key) return;

        const keyValue = key.dataset.key;

        // Add visual feedback
        key.style.transform = 'scale(0.95)';
        setTimeout(() => {
            key.style.transform = '';
        }, 100);

        if (keyValue === 'ENTER') {
            // Submit the form via AJAX
            if (input.value.trim()) {
                submitGuess(input.value.trim());
            } else {
                showToast('⚠️ Please enter a word');
            }
        } else if (keyValue === 'BACKSPACE') {
            // Remove last character
            input.value = input.value.slice(0, -1);
        } else {
            // Add the letter
            input.value += keyValue;
            // Add subtle animation to input
            input.style.transform = 'scale(1.02)';
            setTimeout(() => {
                input.style.transform = '';
            }, 100);
        }

        // Keep focus on input
        input.focus();
    });

    // Handle physical keyboard
    input.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !input.value.trim()) {
            e.preventDefault();
            showToast('⚠️ Please enter a word');
        }
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
