// script.js - Frontend logic dla Gmina-AI
// Adaptacja z aquabot.js na potrzeby systemu Adept

class GminaBotUI {
    constructor() {
        this.currentGmina = null;
        this.isWaitingForInput = false;
        this.inputContext = null;
        
        // Referencje do elementów DOM
        this.initPanel = document.getElementById('init-panel');
        this.chatInterface = document.getElementById('chat-interface');
        this.messagesContainer = document.getElementById('messages-container');
        this.buttonContainer = document.getElementById('button-container');
        this.textInputContainer = document.getElementById('text-input-container');
        this.userInput = document.getElementById('user-input');
        this.sendBtn = document.getElementById('send-btn');
        this.loadingOverlay = document.getElementById('loading-overlay');
        this.errorModal = document.getElementById('error-modal');
        
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Przycisk start
        const startBtn = document.getElementById('start-bot-btn');
        const gminaInput = document.getElementById('gmina-input');
        
        startBtn.addEventListener('click', () => {
            const gminaName = gminaInput.value.trim();
            if (gminaName) {
                this.startBotSession(gminaName);
            } else {
                this.showError('Proszę wprowadzić nazwę gminy.');
            }
        });

        // Enter w polu gminy
        gminaInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                startBtn.click();
            }
        });

        // Przyciski wyboru gminy
        const gminaButtons = document.querySelectorAll('.gmina-btn');
        gminaButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const gminaName = btn.dataset.gmina;
                this.startBotSession(gminaName);
            });
        });

        // Przycisk reset
        const resetBtn = document.getElementById('reset-btn');
        resetBtn.addEventListener('click', () => {
            this.resetSession();
        });

        // Wysyłanie wiadomości tekstowych
        this.sendBtn.addEventListener('click', () => {
            this.sendTextMessage();
        });

        this.userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.sendTextMessage();
            }
        });

        // Zamykanie modali
        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.target.closest('.modal').style.display = 'none';
            });
        });

        // Retry button w error modal
        document.getElementById('error-retry-btn').addEventListener('click', () => {
            this.errorModal.style.display = 'none';
            if (this.currentGmina) {
                this.startBotSession(this.currentGmina);
            }
        });
    }

    async startBotSession(gminaName) {
        this.showLoading(true);
        
        try {
            const response = await fetch('/gmina-bot/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ gmina: gminaName })
            });

            if (!response.ok) {
                throw new Error(`Błąd serwera: ${response.status}`);
            }

            const data = await response.json();
            
            // Przełączenie na interfejs chatu
            this.currentGmina = gminaName;
            this.switchToChatInterface(gminaName);
            this.displayBotMessage(data.reply);
            
        } catch (error) {
            console.error('Błąd podczas inicjalizacji sesji:', error);
            this.showError('Nie udało się nawiązać połączenia z systemem. Sprawdź połączenie internetowe i spróbuj ponownie.');
        } finally {
            this.showLoading(false);
        }
    }

    switchToChatInterface(gminaName) {
        this.initPanel.style.display = 'none';
        this.chatInterface.style.display = 'flex';
        
        // Aktualizacja nagłówka
        document.getElementById('current-gmina').innerHTML = `Połączony z: <strong>${gminaName}</strong>`;
        
        // Wyczyść poprzednie wiadomości
        this.messagesContainer.innerHTML = '';
        this.buttonContainer.innerHTML = '';
    }

    displayBotMessage(reply) {
        if (!reply) return;

        // Usuń wskaźnik pisania, jeśli istnieje
        this.removeTypingIndicator();

        const messageElement = document.createElement('div');
        messageElement.className = 'message bot-message';

        let messageContent = `
            <div class="message-avatar">🤖</div>
            <div class="message-content">
        `;

        // Główny tekst wiadomości
        if (reply.text_message) {
            messageContent += `<div class="message-text">${reply.text_message.replace(/\n/g, '<br>')}</div>`;
        }

        // Wskaźniki statusu (adaptacja z parametrów AquaBot)
        if (reply.status_indicators && reply.status_indicators.length > 0) {
            messageContent += '<div class="status-indicators"><ul>';
            reply.status_indicators.forEach(indicator => {
                messageContent += `<li><span class="dot ${indicator.color}"></span> ${indicator.name}: ${indicator.value}</li>`;
            });
            messageContent += '</ul></div>';
        }

        messageContent += '</div>';
        messageElement.innerHTML = messageContent;
        
        this.messagesContainer.appendChild(messageElement);

        // Wyświetl przyciski, jeśli są dostępne
        if (reply.buttons && reply.buttons.length > 0) {
            this.displayButtons(reply.buttons);
            this.textInputContainer.style.display = 'none';
        }

        // Sprawdź czy oczekuje na input tekstowy
        if (reply.input_expected) {
            this.isWaitingForInput = true;
            this.inputContext = reply.input_context;
            this.textInputContainer.style.display = 'block';
            this.buttonContainer.innerHTML = '';
            this.userInput.focus();
        }

        this.scrollToBottom();
    }

    displayButtons(buttons) {
        this.buttonContainer.innerHTML = '';
        
        buttons.forEach(button => {
            const buttonElement = document.createElement('button');
            buttonElement.className = 'action-btn';
            buttonElement.textContent = button.text;
            
            buttonElement.addEventListener('click', () => {
                this.handleButtonClick(button.action, button.text);
            });
            
            this.buttonContainer.appendChild(buttonElement);
        });
    }

    displayTypingIndicator() {
        const typingElement = document.createElement('div');
        typingElement.className = 'typing-indicator';
        typingElement.id = 'typing-indicator';
        typingElement.innerHTML = `
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
        `;
        this.messagesContainer.appendChild(typingElement);
        this.scrollToBottom();
    }

    removeTypingIndicator() {
        const typingElement = document.getElementById('typing-indicator');
        if (typingElement) {
            typingElement.remove();
        }
    }

    async handleButtonClick(action, buttonText) {
        // Pokaż wiadomość użytkownika (kliknięty przycisk)
        this.displayUserMessage(`📌 ${buttonText}`);
        
        // Wyczyść przyciski
        this.buttonContainer.innerHTML = '';
        
        // Pokaż wskaźnik pisania
        this.displayTypingIndicator();
        
        this.showLoading(true);
        
        try {
            const response = await fetch('/gmina-bot/send', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ button_action: action })
            });

            if (!response.ok) {
                throw new Error(`Błąd serwera: ${response.status}`);
            }

            const data = await response.json();
            this.displayBotMessage(data.reply);
            
        } catch (error) {
            console.error('Błąd podczas obsługi przycisku:', error);
            this.showError('Nie udało się przetworzyć żądania. Spróbuj ponownie.');
        } finally {
            this.showLoading(false);
        }
    }

    async sendTextMessage() {
        const message = this.userInput.value.trim();
        if (!message) return;

        // Pokaż wiadomość użytkownika
        this.displayUserMessage(message);
        this.userInput.value = '';
        
        // Ukryj input jeśli nie jest już potrzebny
        if (this.isWaitingForInput) {
            this.textInputContainer.style.display = 'none';
            this.isWaitingForInput = false;
            this.inputContext = null;
        }

        // Pokaż wskaźnik pisania
        this.displayTypingIndicator();

        this.showLoading(true);

        try {
            const response = await fetch('/gmina-bot/send', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: message })
            });

            if (!response.ok) {
                throw new Error(`Błąd serwera: ${response.status}`);
            }

            const data = await response.json();
            this.displayBotMessage(data.reply);

        } catch (error) {
            console.error('Błąd podczas wysyłania wiadomości:', error);
            this.showError('Nie udało się wysłać wiadomości. Sprawdź połączenie i spróbuj ponownie.');
        } finally {
            this.showLoading(false);
        }
    }

    displayUserMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.className = 'message user-message';
        
        messageElement.innerHTML = `
            <div class="message-content">
                <div class="message-text">${message}</div>
            </div>
            <div class="message-avatar">👤</div>
        `;
        
        this.messagesContainer.appendChild(messageElement);
        this.scrollToBottom();
    }

    resetSession() {
        // Powrót do ekranu inicjalizacji
        this.chatInterface.style.display = 'none';
        this.initPanel.style.display = 'flex';
        
        // Wyczyść stan
        this.currentGmina = null;
        this.isWaitingForInput = false;
        this.inputContext = null;
        this.messagesContainer.innerHTML = '';
        this.buttonContainer.innerHTML = '';
        this.textInputContainer.style.display = 'none';
        
        // Wyczyść pole input
        document.getElementById('gmina-input').value = '';
    }

    showLoading(show) {
        this.loadingOverlay.style.display = show ? 'flex' : 'none';
    }

    showError(message) {
        document.getElementById('error-message').textContent = message;
        this.errorModal.style.display = 'flex';
    }

    scrollToBottom() {
        setTimeout(() => {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }, 100);
    }
}

// Auto-complete dla nazw gmin
class GminaAutocomplete {
    constructor() {
        this.gminaInput = document.getElementById('gmina-input');
        this.suggestions = [
            'Przykładowa Gmina',
            'Demo Gmina',
            'Warszawa',
            'Kraków', 
            'Gdańsk',
            'Wrocław',
            'Poznań',
            'Łódź'
        ];
        
        this.initAutoComplete();
    }

    initAutoComplete() {
        let suggestionList = null;

        this.gminaInput.addEventListener('input', (e) => {
            const value = e.target.value.toLowerCase();
            
            // Usuń poprzednie sugestie
            if (suggestionList) {
                suggestionList.remove();
                suggestionList = null;
            }

            if (value.length < 2) return;

            const matches = this.suggestions.filter(gmina => 
                gmina.toLowerCase().includes(value)
            );

            if (matches.length > 0) {
                suggestionList = document.createElement('div');
                suggestionList.className = 'autocomplete-suggestions';
                
                matches.forEach(match => {
                    const suggestion = document.createElement('div');
                    suggestion.className = 'autocomplete-item';
                    suggestion.textContent = match;
                    
                    suggestion.addEventListener('click', () => {
                        this.gminaInput.value = match;
                        suggestionList.remove();
                        suggestionList = null;
                    });
                    
                    suggestionList.appendChild(suggestion);
                });

                this.gminaInput.parentNode.appendChild(suggestionList);
            }
        });

        // Ukryj sugestie po kliknięciu poza pole
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.gmina-selector') && suggestionList) {
                suggestionList.remove();
                suggestionList = null;
            }
        });
    }
}

// Inicjalizacja aplikacji po załadowaniu DOM
document.addEventListener('DOMContentLoaded', () => {
    console.log('🏛️ Gmina-AI Frontend initialized');
    console.log('🤖 Adept Engine ready');
    
    // Inicjalizuj główny interfejs
    window.gminaBotUI = new GminaBotUI();
    
    // Inicjalizuj auto-complete
    window.gminaAutocomplete = new GminaAutocomplete();
    
    // Easter egg - konami code dla trybu deweloperskiego
    let konamiCode = '';
    document.addEventListener('keydown', (e) => {
        konamiCode += e.code;
        if (konamiCode.includes('ArrowUpArrowUpArrowDownArrowDownArrowLeftArrowRightArrowLeftArrowRight')) {
            console.log('🎮 Developer mode activated!');
            console.log('🔧 Gozaru Labs Debug Console Ready');
            konamiCode = '';
        }
        if (konamiCode.length > 50) konamiCode = '';
    });
});