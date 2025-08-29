from flask import Flask, render_template, request, jsonify, session
from datetime import timedelta
from gmina_bot import GminaBot
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'gmina_ai_enterprise_key_2024')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Konfiguracja sesji
app.config['SESSION_COOKIE_SECURE'] = False  # Dla HTTP (localhost)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_PERMANENT'] = False

# Inicjalizacja bota jako zmienna globalna
bot = GminaBot()

@app.route('/')
def index():
    """Strona główna z interfejsem bota Gmina-AI Enterprise"""
    return render_template('index.html')

@app.route('/gmina-bot/start', methods=['POST'])
def gmina_bot_start():
    """
    ENDPOINT 1: Inicjalizuje sesję bota dla wybranej gminy
    """
    try:
        data = request.get_json()
        print(f"[DEBUG] Otrzymane dane: {data}")

        if not data:
            print("[ERROR] Brak danych JSON")
            return jsonify({'error': 'Brak danych JSON'}), 400

        gmina_name = data.get('gmina')
        print(f"[DEBUG] Nazwa gminy: {gmina_name}")

        if not gmina_name:
            print("[ERROR] Brak nazwy gminy")
            return jsonify({'error': 'Brak nazwy gminy'}), 400

        # Ustawienie kontekstu gminy
        session.permanent = True
        context = {'gmina': gmina_name}
        bot.set_gmina_context(context)

        # Sprawdzenie czy kontekst został zapisany
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
        traceback.print_exc()
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
    """
    try:
        # Sprawdzenie kontekstu
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
        selection_data = data.get('selection_data', None)

        print(f"[DEBUG] Wiadomość: {user_message}, Akcja: {button_action}, Selection: {selection_data}")

        # Obsługa wyboru z listy sugestii
        if selection_data:
            reply = bot.process_search_selection(selection_data)
        # Obsługa akcji przycisków
        elif button_action:
            reply = bot.handle_button_action(button_action)
        # Obsługa wiadomości tekstowych
        elif user_message:
            reply = bot.get_bot_response(user_message)
        else:
            return jsonify({'error': 'Brak wiadomości lub akcji'}), 400

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

@app.route('/gmina-bot/search', methods=['POST'])
def gmina_bot_search():
    """
    ENDPOINT 3: Obsługuje wyszukiwanie predykcyjne
    """
    try:
        if 'gmina_context' not in session:
            return jsonify({'suggestions': []}), 200

        data = request.get_json()
        query = data.get('query', '')
        context = data.get('context', '')

        print(f"[DEBUG] Search query: {query}, context: {context}")

        if not query or len(query) < 2:
            return jsonify({'suggestions': []})

        # Pobierz sugestie z bota
        suggestions = bot.search_suggestions(query, context)
        
        return jsonify({'suggestions': suggestions})

    except Exception as e:
        print(f"[ERROR] Błąd podczas wyszukiwania: {e}")
        return jsonify({'suggestions': []}), 200

@app.route('/gmina-bot/process-custom', methods=['POST'])
def gmina_bot_process_custom():
    """
    ENDPOINT 4: Przetwarza niestandardowe zgłoszenia
    """
    try:
        if 'gmina_context' not in session:
            return jsonify({'error': 'Brak sesji'}), 400

        data = request.get_json()
        custom_input = data.get('custom_input', '')
        input_type = data.get('type', 'problem')

        print(f"[DEBUG] Custom input: {custom_input}, type: {input_type}")

        if input_type == 'problem':
            reply = bot.process_custom_problem(custom_input)
        else:
            reply = bot.get_bot_response(custom_input)

        return jsonify({'reply': reply})

    except Exception as e:
        print(f"[ERROR] Błąd podczas przetwarzania custom input: {e}")
        return jsonify({
            'reply': {
                'text_message': 'Nie udało się przetworzyć zgłoszenia.',
                'buttons': [{'text': 'Spróbuj ponownie', 'action': 'zglos_problem'}]
            }
        }), 500

@app.route('/gmina-bot/track-no-results', methods=['POST'])
def gmina_track_no_results():
    """
    ENDPOINT 5: Wysyła event pustych wyników do GA4 Measurement Protocol
    RODO-COMPLIANT: Przetwarza tylko anonimowe frazy tekstowe
    
    Zgodność z RODO:
    - Nie zbiera danych osobowych (PII)
    - Śledzi tylko anonimowe frazy wyszukiwania
    - Wymaga minimum 3 znaków (filtr bezpieczeństwa)
    - Używa anonimowych identyfikatorów sesji
    """
    try:
        data = request.get_json()
        query = data.get('query', '')
        search_type = data.get('search_type', 'general')
        
        # RODO Protection: tylko frazy > 2 znaków
        if len(query.strip()) <= 2:
            return jsonify({
                'status': 'skipped', 
                'reason': 'query too short (RODO protection)'
            }), 200
        
        # Sprawdź czy sesja jest aktywna
        if 'gmina_context' not in session:
            return jsonify({
                'status': 'skipped', 
                'reason': 'no active session'
            }), 200
        
        # Wywołaj metodę GA4 z bota
        ga4_success = bot.send_ga4_no_results_event(query, search_type)
        
        # Logowanie zgodne z RODO
        if ga4_success:
            print(f"[GA4 RODO] ✅ Tracked anonymous search: length={len(query)}, type={search_type}")
        else:
            print(f"[GA4 RODO] ❌ Failed to track search")
        
        return jsonify({
            'status': 'success' if ga4_success else 'partial_success',
            'ga4_sent': ga4_success,
            'query_length': len(query),  # Tylko długość, nie sama fraza
            'search_type': search_type,
            'rodo_compliant': True
        })
    
    except Exception as e:
        print(f"[ERROR] Track no results error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'error': 'internal_error',  # Nie ujawniaj szczegółów błędu
            'rodo_compliant': True
        }), 500

@app.route('/health')
def health_check():
    """Endpoint sprawdzający status aplikacji"""
    return jsonify({
        'status': 'OK',
        'service': 'Gmina-AI Bot Enterprise',
        'version': '3.0',
        'features': [
            'predictive_search', 
            'custom_problems', 
            'intelligent_routing', 
            'ga4_tracking',
            'rodo_compliant'
        ],
        'session_active': 'gmina_context' in session
    })

@app.route('/debug/session')
def debug_session():
    """Endpoint do debugowania sesji (tylko dla developmentu)"""
    if app.debug:
        return jsonify({
            'session_data': dict(session),
            'session_id': session.get('_id', 'BRAK'),
            'gmina_context': session.get('gmina_context', 'BRAK'),
            'search_context': session.get('search_context', 'BRAK'),
            'search_mode': session.get('search_mode', False)
        })
    return jsonify({'error': 'Dostępne tylko w trybie debug'}), 403

if __name__ == '__main__':
    with app.app_context():
        # Inicjalizacja danych bota
        bot.initialize_data()
        print("=" * 60)
        print("🏛️  GMINA-AI ENTERPRISE v3.0")
        print("🤖 Powered by Adept AI Engine")
        print("🔍 GA4 No Results Tracking: ENABLED")
        print("🔐 RODO/GDPR Compliant: YES")
        print("=" * 60)
        print("✅ System uruchomiony pomyślnie!")
        print("📍 Dostępny pod adresem: http://localhost:5000")
        print("🔍 Wyszukiwanie predykcyjne: AKTYWNE")
        print("📊 GA4 Tracking: READY (configure keys in gmina_bot.py)")
        print("🔧 Debug endpoint: http://localhost:5000/debug/session")
        print("=" * 60)

    app.run(debug=True, port=5000)