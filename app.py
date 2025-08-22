from flask import Flask, render_template, request, jsonify, session
from datetime import timedelta
from gmina_bot import GminaBot
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'gmina_ai_secret_key_2024')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# NAPRAWKA: Dodaj konfigurację sesji
app.config['SESSION_COOKIE_SECURE'] = False  # Dla HTTP (localhost)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_PERMANENT'] = False

# NAPRAWKA: Inicjalizacja bota jako zmienna globalna
bot = GminaBot()

@app.route('/')
def index():
    """Strona główna z interfejsem bota Gmina-AI"""
    return render_template('index.html')

@app.route('/gmina-bot/start', methods=['POST'])
def gmina_bot_start():
    """
    ENDPOINT 1: Inicjalizuje sesję bota dla wybranej gminy
    NAPRAWKA: Dodano szczegółowe logowanie i walidację
    """
    try:
        data = request.get_json()
        print(f"[DEBUG] Otrzymane dane: {data}")  # NAPRAWKA: Dodano logowanie

        if not data:
            print("[ERROR] Brak danych JSON")
            return jsonify({'error': 'Brak danych JSON'}), 400

        gmina_name = data.get('gmina')
        print(f"[DEBUG] Nazwa gminy: {gmina_name}")  # NAPRAWKA: Dodano logowanie

        if not gmina_name:
            print("[ERROR] Brak nazwy gminy")
            return jsonify({'error': 'Brak nazwy gminy'}), 400

        # NAPRAWKA: Sprawdzenie czy sesja działa
        session.permanent = True
        print(f"[DEBUG] Session ID przed: {session.get('_id', 'BRAK')}")

        # NAPRAWKA: Ustawienie kontekstu gminy z dodatkową walidacją
        context = {'gmina': gmina_name}
        bot.set_gmina_context(context)

        # NAPRAWKA: Sprawdzenie czy kontekst został zapisany
        if 'gmina_context' not in session:
            print("[ERROR] Kontekst nie został zapisany w sesji")
            return jsonify({'error': 'Błąd zapisu kontekstu'}), 500

        print(f"[DEBUG] Kontekst zapisany: {session.get('gmina_context')}")

        # Zwrócenie wiadomości powitalnej
        initial_response = bot.get_initial_greeting()
        print(f"[DEBUG] Odpowiedź bota: {initial_response}")

        return jsonify({'reply': initial_response})

    except Exception as e:
        print(f"[BŁĄD KRYTYCZNY w gmina_bot_start]: {e}")
        import traceback
        traceback.print_exc()  # NAPRAWKA: Pełny stack trace
        return jsonify({
            'reply': {
                'text_message': f'Wystąpił błąd podczas inicjalizacji: {str(e)}',
                'buttons': [
                    {'text': 'Spróbuj ponownie', 'action': 'restart'}
                ]
            }
        }), 500

@app.route('/gmina-bot/send', methods=['POST'])
def gmina_bot_send():
    """
    ENDPOINT 2: Obsługuje wiadomości użytkownika w ramach aktywnej sesji
    NAPRAWKA: Dodano walidację kontekstu
    """
    try:
        # NAPRAWKA: Sprawdzenie kontekstu na początku
        if 'gmina_context' not in session:
            print("[ERROR] Brak kontekstu gminy w sesji")
            return jsonify({
                'reply': {
                    'text_message': 'Sesja wygasła. Proszę wybrać gminę ponownie.',
                    'buttons': [
                        {'text': 'Powrót do wyboru gminy', 'action': 'restart'}
                    ]
                }
            }), 400

        data = request.get_json()
        user_message = data.get('message', '')
        button_action = data.get('button_action', '')

        print(f"[DEBUG] Wiadomość: {user_message}, Akcja: {button_action}")

        if not user_message and not button_action:
            return jsonify({'error': 'Brak wiadomości lub akcji przycisku'}), 400

        # Obsługa akcji przycisków lub wiadomości tekstowych
        if button_action:
            reply = bot.handle_button_action(button_action)
        else:
            reply = bot.get_bot_response(user_message)

        return jsonify({'reply': reply})

    except Exception as e:
        print(f"[BŁĄD KRYTYCZNY w gmina_bot_send]: {e}")
        import traceback
        traceback.print_exc()
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
        'version': '2.1',
        'session_active': 'gmina_context' in session
    })

# NAPRAWKA: Endpoint do debugowania sesji
@app.route('/debug/session')
def debug_session():
    """Endpoint do debugowania sesji (tylko dla developmentu)"""
    if app.debug:
        return jsonify({
            'session_data': dict(session),
            'session_id': session.get('_id', 'BRAK'),
            'gmina_context': session.get('gmina_context', 'BRAK')
        })
    return jsonify({'error': 'Dostępne tylko w trybie debug'}), 403

if __name__ == '__main__':
    with app.app_context():
        # Inicjalizacja danych bota
        bot.initialize_data()
        print("🏛️ Gmina-AI Bot uruchomiony!")
        print("📍 Dostępny pod adresem: http://localhost:5000")
        print("🔧 Debug endpoint: http://localhost:5000/debug/session")

    app.run(debug=True, port=5000)
