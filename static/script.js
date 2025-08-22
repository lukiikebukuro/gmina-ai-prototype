// script.js - Naprawiono problem z powrotem do menu
class GminaBotUI {
    constructor() {
        this.currentGmina = null;
        this.isWaitingForInput = false;
        this.inputContext = null;

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

        gminaInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                startBtn.click();
            }
        });

        const gminaButtons = document.querySelectorAll('.gmina-btn');
        gminaButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const gminaName = btn.dataset.gmina;
                this.startBotSession(gminaName);
            });
        });

        const resetBtn = document.getElementById('reset-btn');
        resetBtn.addEventListener('click', () => {
            this.resetSession();
        });

        this.sendBtn.addEventListener('click', () => {
            this.sendTextMessage();
        });

        this.userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.sendTextMessage();
            }
        });

        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.target.closest('.modal').style.display = 'none';
            });
        });

        document.getElementById('error-retry-btn').addEventListener('click', () => {
            this.errorModal.style.display = 'none';
            if (this.currentGmina) {
                this.startBotSession(this.currentGmina);
            }
        });
    }

    async startBotSession(gminaName) {
        console.log(`[DEBUG] Rozpoczynanie sesji dla gminy: ${gminaName}`);
        this.showLoading(true);

        try {
            if (!gminaName || gminaName.trim() === '') {
                throw new Error('Nazwa gminy nie może być pusta');
            }

            const requestData = { gmina: gminaName.trim() };
            console.log(`[DEBUG] Wysyłanie danych:`, requestData);

            const response = await fetch('/gmina-bot/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Cache-Control': 'no-cache',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin',
                body: JSON.stringify(requestData)
            });

            if (!response.ok) {
                throw new Error(`Błąd serwera: ${response.status}`);
            }

            const data = await response.json();

            if (data.error) {
                throw new Error(data.error);
            }

            if (!data.reply) {
                throw new Error('Brak odpowiedzi od serwera');
            }

            this.currentGmina = gminaName;
            this.switchToChatInterface(gminaName);
            this.displayBotMessage(data.reply);

        } catch (error) {
            console.error('[ERROR] Błąd podczas inicjalizacji sesji:', error);
            this.showError(`Nie udało się nawiązać połączenia: ${error.message}`);
        } finally {
            this.showLoading(false);
        }
    }

    switchToChatInterface(gminaName) {
        this.initPanel.style.display = 'none';
        this.chatInterface.style.display = 'flex';
        document.getElementById('current-gmina').innerHTML = `Połączony z: <strong>${gminaName}</strong>`;
        this.messagesContainer.innerHTML = '';
        this.buttonContainer.innerHTML = '';
    }

    displayBotMessage(reply) {
        if (!reply) return;

        this.removeTypingIndicator();

        const messageElement = document.createElement('div');
        messageElement.className = 'message bot-message';

        let messageContent = `
            <div class="message-avatar">🤖</div>
            <div class="message-content">
        `;

        if (reply.text_message) {
            messageContent += `<div class="message-text">${reply.text_message.replace(/\n/g, '<br>')}</div>`;
        }

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

        if (reply.buttons && reply.buttons.length > 0) {
            this.displayButtons(reply.buttons);
            this.textInputContainer.style.display = 'none';
        }

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
        if (action === 'restart' || action === 'reload') {
            this.resetSession();
            return;
        }

        this.displayUserMessage(`📌 ${buttonText}`);
        this.buttonContainer.innerHTML = '';
        this.displayTypingIndicator();
        this.showLoading(true);

        try {
            const response = await fetch('/gmina-bot/send', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Cache-Control': 'no-cache',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin',
                body: JSON.stringify({ button_action: action })
            });

            if (!response.ok) {
                throw new Error(`Błąd serwera: ${response.status}`);
            }

            const data = await response.json();

            if (data.reply && data.reply.text_message && data.reply.text_message.includes('Sesja wygasła')) {
                this.showError('Sesja wygasła. Zostaniesz przekierowany do wyboru gminy.');
                setTimeout(() => {
                    this.resetSession();
                }, 2000);
                return;
            }

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

        this.displayUserMessage(message);
        this.userInput.value = '';

        if (this.isWaitingForInput) {
            this.textInputContainer.style.display = 'none';
            this.isWaitingForInput = false;
            this.inputContext = null;
        }

        this.displayTypingIndicator();
        this.showLoading(true);

        try {
            const response = await fetch('/gmina-bot/send', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Cache-Control': 'no-cache',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin',
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
        console.log('[DEBUG] Resetowanie sesji');
        this.chatInterface.style.display = 'none';
        this.initPanel.style.display = 'flex';
        this.currentGmina = null;
        this.isWaitingForInput = false;
        this.inputContext = null;
        this.messagesContainer.innerHTML = '';
        this.buttonContainer.innerHTML = '';
        this.textInputContainer.style.display = 'none';
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
            'Łódź',
            'Gorzów Wielkopolski'
        ];

        this.initAutoComplete();
    }

    initAutoComplete() {
        let suggestionList = null;

        this.gminaInput.addEventListener('input', (e) => {
            const value = e.target.value.toLowerCase();

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

        document.addEventListener('click', (e) => {
            if (!e.target.closest('.gmina-selector') && suggestionList) {
                suggestionList.remove();
                suggestionList = null;
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('🏛️ Gmina-AI Frontend initialized v2.3');
    console.log('🤖 Adept Engine ready');

    window.gminaBotUI = new GminaBotUI();
    window.gminaAutocomplete = new GminaAutocomplete();

    fetch('/health')
        .then(response => response.json())
        .then(data => {
            console.log('[DEBUG] Status aplikacji:', data);
        })
        .catch(error => {
            console.log('[DEBUG] Błąd sprawdzania statusu:', error);
        });
});
