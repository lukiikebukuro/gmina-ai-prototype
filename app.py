from flask import Flask, render_template, request, jsonify, session
from datetime import timedelta
from gmina_bot import GminaBot
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'gmina_ai_secret_key_2024')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Inicjalizacja bota
bot = GminaBot()

@app.route('/')
def index():
    """Strona główna z interfejsem bota Gmina-AI"""
    return render_template('index.html')

@app.route('/gmina-bot/start', methods=['POST'])
def gmina_bot_start():
    """
    ENDPOINT 1: Inicjalizuje sesję bota dla wybranej gminy
    Zgodny z architekturą silnika Adept
    """
    data = request.get_json()
    gmina_name = data.get('gmina')
    
    if not gmina_name:
        return jsonify({'error': 'Brak nazwy gminy'}), 400
    
    try:
        # Ustawienie kontekstu gminy (analogicznie do set_station_context)
        bot.set_gmina_context({'gmina': gmina_name})
        
        # Zwrócenie wiadomości powitalnej
        initial_response = bot.get_initial_greeting()
        return jsonify({'reply': initial_response})
    except Exception as e:
        print(f"[BŁĄD KRYTYCZNY w gmina_bot_start]: {e}")
        return jsonify({
            'reply': {
                'text_message': 'Nie udało mi się znaleźć informacji o tej gminie. Spróbuj ponownie.',
                'buttons': [
                    {'text': 'Spróbuj ponownie', 'action': 'restart'}
                ]
            }
        }), 500

@app.route('/gmina-bot/send', methods=['POST'])
def gmina_bot_send():
    """
    ENDPOINT 2: Obsługuje wiadomości użytkownika w ramach aktywnej sesji
    Implementuje logikę drzewa dialogowego
    """
    data = request.get_json()
    user_message = data.get('message', '')
    button_action = data.get('button_action', '')
    
    if not user_message and not button_action:
        return jsonify({'error': 'Brak wiadomości lub akcji przycisku'}), 400
    
    try:
        # Obsługa akcji przycisków lub wiadomości tekstowych
        if button_action:
            reply = bot.handle_button_action(button_action)
        else:
            reply = bot.get_bot_response(user_message)
            
        return jsonify({'reply': reply})
    except Exception as e:
        print(f"[BŁĄD KRYTYCZNY w gmina_bot_send]: {e}")
        return jsonify({
            'reply': {
                'text_message': 'Wystąpił błąd podczas przetwarzania zapytania. Spróbuj ponownie.',
                'buttons': [
                    {'text': 'Powrót do menu', 'action': 'main_menu'}
                ]
            }
        }), 500

@app.route('/health')
def health_check():
    """Endpoint sprawdzający status aplikacji"""
    return jsonify({
        'status': 'OK',
        'service': 'Gmina-AI Bot',
        'version': '1.0'
    })

if __name__ == '__main__':
    with app.app_context():
        # Inicjalizacja danych bota
        bot.initialize_data()
        print("🏛️ Gmina-AI Bot uruchomiony!")
        print("📍 Dostępny pod adresem: http://localhost:5000")
    
    app.run(debug=True, port=5000)