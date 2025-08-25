// script.js - GMINA-AI ENTERPRISE v3.0 with Predictive Search
class GminaBotUI {
    constructor() {
        this.currentGmina = null;
        this.isWaitingForInput = false;
        this.inputContext = null;
        this.searchContext = null;
        this.searchMode = false;
        this.currentSuggestions = [];
        this.selectedSuggestionIndex = -1;
        this.searchDebounceTimer = null;

        this.initPanel = document.getElementById('init-panel');
        this.chatInterface = document.getElementById('chat-interface');
        this.messagesContainer = document.getElementById('messages-container');
        this.buttonContainer = document.getElementById('button-container');
        this.textInputContainer = document.getElementById('text-input-container');
        this.userInput = document.getElementById('user-input');
        this.sendBtn = document.getElementById('send-btn');
        this.loadingOverlay = document.getElementById('loading-overlay');
        this.errorModal = document.getElementById('error-modal');

        // Bind all methods to this instance
        this.startBotSession = this.startBotSession.bind(this);
        this.showError = this.showError.bind(this);
        this.resetSession = this.resetSession.bind(this);
        this.sendTextMessage = this.sendTextMessage.bind(this);

        this.initializeEventListeners();
        this.initializePredictiveSearch();
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
                const gminaName = gminaInput.value.trim();
                if (gminaName) {
                    this.startBotSession(gminaName);
                }
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
            if (e.key === 'Enter' && !this.searchMode) {
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

    initializePredictiveSearch() {
        this.userInput.addEventListener('input', (e) => {
            if (this.searchMode) {
                this.handleSearchInput(e.target.value);
            }
        });

        this.userInput.addEventListener('keydown', (e) => {
            if (this.searchMode && this.currentSuggestions.length > 0) {
                if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    this.navigateSuggestions(1);
                } else if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    this.navigateSuggestions(-1);
                } else if (e.key === 'Enter') {
                    e.preventDefault();
                    if (this.selectedSuggestionIndex >= 0) {
                        this.selectSuggestion(this.currentSuggestions[this.selectedSuggestionIndex]);
                    } else if (this.searchContext === 'problems' && e.target.value.length > 20) {
                        this.sendCustomProblem(e.target.value);
                    }
                } else if (e.key === 'Escape') {
                    this.closeSuggestions();
                }
            }
        });

        document.addEventListener('click', (e) => {
            if (!e.target.closest('.text-input-container') && !e.target.closest('.suggestions-container')) {
                this.closeSuggestions();
            }
        });

        // Aktualizuj pozycję sugestii przy przewijaniu
        window.addEventListener('scroll', () => {
            if (document.getElementById('suggestions-container')) {
                this.updateSuggestionsPosition();
            }
        });

        // Aktualizuj pozycję przy zmianie rozmiaru okna
        window.addEventListener('resize', () => {
            if (document.getElementById('suggestions-container')) {
                this.updateSuggestionsPosition();
            }
        });
    }

    updateSuggestionsPosition() {
        const container = document.getElementById('suggestions-container');
        if (container && this.userInput) {
            const inputRect = this.userInput.getBoundingClientRect();
            container.style.top = `${inputRect.bottom + 5}px`;
            container.style.left = `${inputRect.left}px`;
            container.style.width = `${inputRect.width}px`;
        }
    }

    handleSearchInput(query) {
        clearTimeout(this.searchDebounceTimer);
        
        if (query.length < 2) {
            this.closeSuggestions();
            return;
        }

        this.searchDebounceTimer = setTimeout(() => {
            this.fetchSuggestions(query);
        }, 300);
    }

    async fetchSuggestions(query) {
        try {
            const response = await fetch('/gmina-bot/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    context: this.searchContext
                })
            });

            const data = await response.json();
            if (data.suggestions && data.suggestions.length > 0) {
                this.displaySuggestions(data.suggestions);
            } else {
                this.closeSuggestions();
                if (this.searchContext === 'problems' && query.length > 5) {
                    this.showCustomInputHint();
                }
            }
        } catch (error) {
            console.error('Błąd podczas pobierania sugestii:', error);
        }
    }

    displaySuggestions(suggestions) {
        this.currentSuggestions = suggestions;
        this.selectedSuggestionIndex = -1;

        this.closeSuggestions();

        const suggestionsContainer = document.createElement('div');
        suggestionsContainer.className = 'suggestions-container';
        suggestionsContainer.id = 'suggestions-container';

        const header = document.createElement('div');
        header.className = 'suggestions-header';
        header.innerHTML = `<span>🔍 Znaleziono ${suggestions.length} wyników</span>`;
        suggestionsContainer.appendChild(header);

        suggestions.forEach((suggestion, index) => {
            const suggestionElement = document.createElement('div');
            suggestionElement.className = 'suggestion-item';
            suggestionElement.dataset.index = index;

            suggestionElement.innerHTML = `
                <div class="suggestion-icon">${suggestion.icon}</div>
                <div class="suggestion-content">
                    <div class="suggestion-title">${suggestion.title}</div>
                    <div class="suggestion-subtitle">${suggestion.subtitle}</div>
                    ${suggestion.details ? `<div class="suggestion-details">${suggestion.details}</div>` : ''}
                </div>
            `;

            suggestionElement.addEventListener('click', () => {
                this.selectSuggestion(suggestion);
            });

            suggestionElement.addEventListener('mouseenter', () => {
                this.selectedSuggestionIndex = index;
                this.updateSuggestionSelection();
            });

            suggestionsContainer.appendChild(suggestionElement);
        });

        // Pozycjonowanie względem pola input
        const inputRect = this.userInput.getBoundingClientRect();
        suggestionsContainer.style.position = 'fixed';
        suggestionsContainer.style.top = `${inputRect.bottom + 5}px`;
        suggestionsContainer.style.left = `${inputRect.left}px`;
        suggestionsContainer.style.width = `${inputRect.width}px`;

        // Dodaj do body zamiast do kontenera
        document.body.appendChild(suggestionsContainer);
    }

    showCustomInputHint() {
        const suggestionsContainer = document.createElement('div');
        suggestionsContainer.className = 'suggestions-container custom-hint';
        suggestionsContainer.id = 'suggestions-container';

        suggestionsContainer.innerHTML = `
            <div class="custom-input-hint">
                <div class="hint-icon">✏️</div>
                <div class="hint-text">
                    Nie znalazłeś swojego problemu? Opisz go szczegółowo i naciśnij Enter.
                    <small>Minimum 20 znaków dla niestandardowego zgłoszenia</small>
                </div>
            </div>
        `;

        // Pozycjonowanie względem pola input
        const inputRect = this.userInput.getBoundingClientRect();
        suggestionsContainer.style.position = 'fixed';
        suggestionsContainer.style.top = `${inputRect.bottom + 5}px`;
        suggestionsContainer.style.left = `${inputRect.left}px`;
        suggestionsContainer.style.width = `${inputRect.width}px`;

        // Dodaj do body zamiast do kontenera
        document.body.appendChild(suggestionsContainer);
    }

    navigateSuggestions(direction) {
        const maxIndex = this.currentSuggestions.length - 1;
        
        if (direction === 1) {
            this.selectedSuggestionIndex = this.selectedSuggestionIndex < maxIndex ? 
                this.selectedSuggestionIndex + 1 : 0;
        } else {
            this.selectedSuggestionIndex = this.selectedSuggestionIndex > 0 ? 
                this.selectedSuggestionIndex - 1 : maxIndex;
        }

        this.updateSuggestionSelection();
    }

    updateSuggestionSelection() {
        const items = document.querySelectorAll('.suggestion-item');
        items.forEach((item, index) => {
            if (index === this.selectedSuggestionIndex) {
                item.classList.add('selected');
            } else {
                item.classList.remove('selected');
            }
        });
    }

    selectSuggestion(suggestion) {
        console.log('Wybrano sugestię:', suggestion);
        
        this.userInput.value = '';
        this.closeSuggestions();
        
        this.sendSelectionToServer(suggestion);
    }

    async sendSelectionToServer(suggestion) {
        this.displayTypingIndicator();
        this.showLoading(true);

        try {
            const response = await fetch('/gmina-bot/send', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    selection_data: suggestion
                })
            });

            const data = await response.json();
            this.displayBotMessage(data.reply);

        } catch (error) {
            console.error('Błąd podczas wysyłania wyboru:', error);
            this.showError('Nie udało się przetworzyć wyboru.');
        } finally {
            this.showLoading(false);
        }
    }

    async sendCustomProblem(problemDescription) {
        this.closeSuggestions();
        this.userInput.value = '';
        this.displayUserMessage(`📝 ${problemDescription}`);
        this.displayTypingIndicator();
        this.showLoading(true);

        try {
            const response = await fetch('/gmina-bot/process-custom', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    custom_input: problemDescription,
                    type: 'problem'
                })
            });

            const data = await response.json();
            this.displayBotMessage(data.reply);

        } catch (error) {
            console.error('Błąd podczas wysyłania custom problem:', error);
            this.showError('Nie udało się przetworzyć zgłoszenia.');
        } finally {
            this.showLoading(false);
        }
    }

    closeSuggestions() {
        const container = document.getElementById('suggestions-container');
        if (container) {
            container.remove();
        }
        this.currentSuggestions = [];
        this.selectedSuggestionIndex = -1;
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
        document.getElementById('session-id').textContent = `Sesja: #AI-${Date.now().toString().slice(-6)}`;
        this.messagesContainer.innerHTML = '';
        this.buttonContainer.innerHTML = '';
        this.searchMode = false;
        this.searchContext = null;
    }

    displayBotMessage(reply) {
        if (!reply) return;

        this.removeTypingIndicator();
        this.closeSuggestions();

        const messageElement = document.createElement('div');
        messageElement.className = 'message bot-message';

        let messageContent = `
            <div class="message-avatar">🤖</div>
            <div class="message-content">
        `;

        if (reply.text_message) {
            let formattedMessage = reply.text_message
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\n/g, '<br>');
            messageContent += `<div class="message-text">${formattedMessage}</div>`;
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

        if (reply.enable_search) {
            this.enableSearchMode(reply);
        }

        if (reply.buttons && reply.buttons.length > 0) {
            this.displayButtons(reply.buttons);
            if (!reply.enable_search) {
                this.textInputContainer.style.display = 'none';
            }
        } else if (reply.quick_buttons && reply.quick_buttons.length > 0) {
            this.displayButtons(reply.quick_buttons);
        }

        if (reply.input_expected && !reply.enable_search) {
            this.isWaitingForInput = true;
            this.inputContext = reply.input_context;
            this.textInputContainer.style.display = 'block';
            this.buttonContainer.innerHTML = '';
            this.userInput.focus();
        }

        this.scrollToBottom();
    }

    enableSearchMode(config) {
        this.searchMode = true;
        this.searchContext = config.search_context || 'general';
        
        this.textInputContainer.style.display = 'block';
        
        if (config.search_placeholder) {
            this.userInput.placeholder = config.search_placeholder;
        }
        
        this.textInputContainer.classList.add('search-mode');
        
        setTimeout(() => {
            this.userInput.focus();
        }, 100);
        
        this.sendBtn.innerHTML = '<span>🔍 Szukaj</span>';
    }

    disableSearchMode() {
        this.searchMode = false;
        this.searchContext = null;
        this.textInputContainer.classList.remove('search-mode');
        this.userInput.placeholder = 'Wpisz swoją wiadomość...';
        this.sendBtn.innerHTML = '<span>Wyślij</span><span class="btn-icon" aria-hidden="true">📤</span>';
        this.closeSuggestions();
    }

    displayButtons(buttons) {
        this.buttonContainer.innerHTML = '';

        buttons.forEach(button => {
            const buttonElement = document.createElement('button');
            buttonElement.className = 'action-btn';
            
            if (button.text.includes('🔍') || button.text.includes('📋') || 
                button.text.includes('⚠️') || button.text.includes('🏛️')) {
                buttonElement.innerHTML = button.text;
            } else {
                buttonElement.textContent = button.text;
            }

            buttonElement.addEventListener('click', () => {
                this.handleButtonClick(button.action, button.text);
            });

            this.buttonContainer.appendChild(buttonElement);
        });
    }

    async handleButtonClick(action, buttonText) {
        if (action === 'restart' || action === 'reload') {
            this.resetSession();
            return;
        }

        if (this.searchMode && action === 'main_menu') {
            this.disableSearchMode();
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

        if (this.searchMode && this.searchContext === 'problems' && message.length > 20) {
            this.sendCustomProblem(message);
            return;
        }

        this.displayUserMessage(message);
        this.userInput.value = '';
        this.closeSuggestions();

        if (this.isWaitingForInput) {
            this.textInputContainer.style.display = 'none';
            this.isWaitingForInput = false;
            this.inputContext = null;
        }

        if (this.searchMode) {
            this.disableSearchMode();
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

    resetSession() {
        console.log('[DEBUG] Resetowanie sesji');
        this.chatInterface.style.display = 'none';
        this.initPanel.style.display = 'flex';
        this.currentGmina = null;
        this.isWaitingForInput = false;
        this.inputContext = null;
        this.searchMode = false;
        this.searchContext = null;
        this.messagesContainer.innerHTML = '';
        this.buttonContainer.innerHTML = '';
        this.textInputContainer.style.display = 'none';
        this.disableSearchMode();
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
            'Gorzów Wielkopolski',
            'Katowice',
            'Lublin',
            'Białystok',
            'Szczecin',
            'Bydgoszcz',
            'Gdynia',
            'Częstochowa',
            'Radom',
            'Sosnowiec',
            'Toruń',
            'Kielce'
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

// Inicjalizacja przy załadowaniu DOM
document.addEventListener('DOMContentLoaded', () => {
    console.log('=' .repeat(60));
    console.log('🏛️  GMINA-AI ENTERPRISE v3.0 - Frontend');
    console.log('🤖 Powered by Adept AI Engine');
    console.log('🔍 Predictive Search: ENABLED');
    console.log('=' .repeat(60));

    window.gminaBotUI = new GminaBotUI();
    window.gminaAutocomplete = new GminaAutocomplete();

    // Health check
    fetch('/health')
        .then(response => response.json())
        .then(data => {
            console.log('[DEBUG] Status aplikacji:', data);
            if (data.features) {
                console.log('[DEBUG] Aktywne funkcje:', data.features.join(', '));
            }
        })
        .catch(error => {
            console.log('[DEBUG] Błąd sprawdzania statusu:', error);
        });
});