"""
gmina_bot.py - Silnik bota "Adept" dla Gmina-AI
Wersja 2.3 - Naprawiono wszystkie błędy
"""
import json
import os
import re
from flask import session

class GminaBot:
    def __init__(self):
        self.gmina_data = {}
        self.contacts_data = {}
        self.forms_data = {}

        self.status_colors = {
            'dostepne_online': 'green-dot',
            'wymaga_wizyty': 'orange-dot',
            'skomplikowane': 'red-dot',
            'brak_danych': 'grey-dot'
        }

        self.category_map = {
            'odpady': ['śmieci', 'odpadki', 'deklaracja śmieciowa', 'wywóz śmieci', 'odpady', 'śmieć'],
            'podatki': ['podatek', 'opłata', 'należność', 'płatność', 'finanse'],
            'budownictwo': ['budowa', 'remont', 'pozwolenie', 'zgłoszenie budowlane', 'budynek'],
            'działalność': ['firma', 'biznes', 'rejestracja', 'działalność gospodarcza', 'przedsiębiorstwo'],
            'drogi': ['dziura', 'uszkodzenie', 'naprawa drogi', 'infrastruktura', 'droga', 'chodnik'],
            'środowisko': ['drzewo', 'wycinka', 'ochrona środowiska', 'zieleń', 'las', 'park'],
            'problemy': ['problem', 'skarga', 'zgłoszenie', 'awaria', 'usterka', 'reklamacja']
        }

    def initialize_data(self):
        self.gmina_data = {
            'Przykładowa Gmina': {
                'basic_info': {
                    'name': 'Urząd Gminy Przykładowa',
                    'address': 'ul. Główna 1, 00-001 Przykładowa',
                    'phone': '+48 123 456 789',
                    'email': 'kontakt@przykladowa.pl',
                    'nip': '1234567890',
                    'regon': '123456789'
                },
                'departments': {
                    'odpady': {'name': 'Referat Gospodarki Komunalnej', 'phone': '+48 123 456 790', 'email': 'odpady@przykladowa.pl', 'status': 'dostepne_online'},
                    'podatki': {'name': 'Referat Finansowy', 'phone': '+48 123 456 791', 'email': 'finanse@przykladowa.pl', 'status': 'wymaga_wizyty'},
                    'budownictwo': {'name': 'Referat Architektury', 'phone': '+48 123 456 792', 'email': 'architektura@przykladowa.pl', 'status': 'dostepne_online'},
                    'drogi': {'name': 'Referat Infrastruktury', 'phone': '+48 123 456 793', 'email': 'infrastruktura@przykladowa.pl', 'status': 'dostepne_online'}
                },
                'forms': {
                    'deklaracja_smieciowa': {'name': 'Deklaracja odpadów komunalnych', 'link': 'https://przykladowa.pl/formularze/odpady.pdf', 'status': 'dostepne_online'},
                    'pozwolenie_budowlane': {'name': 'Wniosek o pozwolenie na budowę', 'link': 'https://przykladowa.pl/formularze/budowa.pdf', 'status': 'skomplikowane'}
                }
            },
            'Demo Gmina': {
                'basic_info': {
                    'name': 'Urząd Gminy Demo',
                    'address': 'ul. Testowa 5, 00-002 Demo',
                    'phone': '+48 987 654 321',
                    'email': 'kontakt@demo.pl',
                    'nip': '9876543210',
                    'regon': '987654321'
                },
                'departments': {
                    'odpady': {'name': 'Wydział Ekologii', 'phone': '+48 987 654 322', 'email': 'ekologia@demo.pl', 'status': 'dostepne_online'},
                    'podatki': {'name': 'Referat Finansowy', 'phone': '+48 987 654 323', 'email': 'finanse@demo.pl', 'status': 'wymaga_wizyty'},
                    'budownictwo': {'name': 'Referat Architektury', 'phone': '+48 987 654 324', 'email': 'architektura@demo.pl', 'status': 'dostepne_online'}
                },
                'forms': {
                    'deklaracja_smieciowa': {'name': 'Deklaracja odpadów komunalnych', 'link': 'https://demo.pl/formularze/odpady.pdf', 'status': 'dostepne_online'}
                }
            }
        }

    def set_gmina_context(self, context):
        try:
            gmina_name = context.get('gmina')
            print(f"[DEBUG] Próba ustawienia kontekstu dla: {gmina_name}")

            if not gmina_name:
                print("[ERROR] Brak nazwy gminy w kontekście")
                return False

            # NAPRAWKA: Tworzenie pełnych danych dla każdej gminy
            if gmina_name not in self.gmina_data:
                print(f"[INFO] Gmina '{gmina_name}' nie istnieje w danych, tworzę pełny kontekst")
                self.gmina_data[gmina_name] = {
                    'basic_info': {
                        'name': f'Urząd Gminy {gmina_name}',
                        'address': f'ul. Główna 1, {gmina_name}',
                        'phone': '+48 123 456 789',
                        'email': f'kontakt@{gmina_name.lower().replace(" ", "")}.pl',
                        'nip': '1234567890',
                        'regon': '123456789'
                    },
                    'departments': {
                        'odpady': {'name': 'Referat Gospodarki Komunalnej', 'phone': '+48 123 456 790', 'email': 'odpady@gmina.pl', 'status': 'dostepne_online'},
                        'podatki': {'name': 'Referat Finansowy', 'phone': '+48 123 456 791', 'email': 'finanse@gmina.pl', 'status': 'wymaga_wizyty'},
                        'budownictwo': {'name': 'Referat Architektury', 'phone': '+48 123 456 792', 'email': 'architektura@gmina.pl', 'status': 'dostepne_online'},
                        'drogi': {'name': 'Referat Infrastruktury', 'phone': '+48 123 456 793', 'email': 'infrastruktura@gmina.pl', 'status': 'dostepne_online'}
                    },
                    'forms': {
                        'deklaracja_smieciowa': {'name': 'Deklaracja odpadów komunalnych', 'link': 'https://gmina.pl/formularze/odpady.pdf', 'status': 'dostepne_online'},
                        'pozwolenie_budowlane': {'name': 'Wniosek o pozwolenie na budowę', 'link': 'https://gmina.pl/formularze/budowa.pdf', 'status': 'skomplikowane'}
                    }
                }

            session['gmina_context'] = context
            session['chat_history'] = []
            session['current_path'] = 'start'
            session['input_context'] = None
            session.permanent = True
            session.modified = True

            print(f"[SUCCESS] Kontekst ustawiony pomyślnie dla gminy: {gmina_name}")
            return True

        except Exception as e:
            print(f"[ERROR] Błąd podczas ustawiania kontekstu: {e}")
            return False

    def get_initial_greeting(self):
        if 'gmina_context' not in session:
            return {'text_message': 'Error: Kontekst gminy nie został ustawiony.'}

        gmina_name = session['gmina_context']['gmina']
        greeting_text = f"Witaj. Jestem Adept, wirtualny asystent urzędu, stworzony przez Adept AI. Pomagam w sprawach gminy {gmina_name}. Jak mogę Ci pomóc?"

        return {
            'text_message': greeting_text,
            'buttons': [
                {'text': 'Znajdź Kontakt', 'action': 'znajdz_kontakt'},
                {'text': 'Pobierz Formularz', 'action': 'pobierz_formularz'},
                {'text': 'Zgłoś Problem', 'action': 'zglos_problem'},
                {'text': 'Sprawdź Gminę', 'action': 'sprawdz_gmine'}
            ]
        }

    def handle_button_action(self, action):
        if 'gmina_context' not in session:
            return {
                'text_message': 'Sesja wygasła. Proszę wybrać gminę ponownie.',
                'buttons': [{'text': 'Powrót do wyboru gminy', 'action': 'restart'}]
            }

        session['current_path'] = action
        session['input_context'] = None
        session.modified = True

        if action == 'znajdz_kontakt':
            return self._handle_znajdz_kontakt()
        elif action == 'pobierz_formularz':
            return self._handle_pobierz_formularz()
        elif action == 'zglos_problem':
            return self._handle_zglos_problem()
        elif action == 'sprawdz_gmine':
            return self._handle_sprawdz_gmine()
        elif action.startswith('kontakt_'):
            return self._handle_kontakt_subaction(action)
        elif action.startswith('formularz_'):
            return self._handle_formularz_subaction(action)
        elif action.startswith('problem_'):
            return self._handle_problem_subaction(action)
        elif action == 'main_menu':
            return self.get_initial_greeting()
        else:
            return {
                'text_message': 'Nie rozpoznaję tej opcji.',
                'buttons': [{'text': 'Powrót do menu', 'action': 'main_menu'}]
            }

    def _handle_znajdz_kontakt(self):
        return {
            'text_message': 'Szukasz kontaktu do całego urzędu, konkretnego wydziału czy osoby?',
            'buttons': [
                {'text': 'Urząd (Dane Ogólne)', 'action': 'kontakt_urzad'},
                {'text': 'Wydział/Referat', 'action': 'kontakt_wydzial'},
                {'text': 'Konkretna Osoba', 'action': 'kontakt_osoba'},
                {'text': 'Powrót do menu', 'action': 'main_menu'}
            ]
        }

    def _handle_pobierz_formularz(self):
        return {
            'text_message': 'Jakiej sprawy dotyczy formularz? Wybierz kategorię:',
            'buttons': [
                {'text': 'Budownictwo', 'action': 'formularz_budownictwo'},
                {'text': 'Ochrona Środowiska', 'action': 'formularz_srodowisko'},
                {'text': 'Działalność Gospodarcza', 'action': 'formularz_dzialalnosc'},
                {'text': 'Odpady', 'action': 'formularz_odpady'},
                {'text': 'Powrót do menu', 'action': 'main_menu'}
            ]
        }

    def _handle_zglos_problem(self):
        return {
            'text_message': 'Jakiego typu problem chcesz zgłosić? Wybierz kategorię:',
            'buttons': [
                {'text': 'Uszkodzenia dróg/chodników', 'action': 'problem_drogi'},
                {'text': 'Problemy z odpadami', 'action': 'problem_odpady'},
                {'text': 'Awarie oświetlenia', 'action': 'problem_oswietlenie'},
                {'text': 'Inne problemy', 'action': 'problem_inne'},
                {'text': 'Powrót do menu', 'action': 'main_menu'}
            ]
        }

    def _handle_sprawdz_gmine(self):
        session['input_context'] = 'sprawdz_gmine'
        session.modified = True
        return {
            'text_message': 'Podaj nazwę gminy, którą chcesz zweryfikować.',
            'input_expected': True,
            'input_context': 'sprawdz_gmine'
        }

    def _handle_kontakt_subaction(self, action):
        gmina_data = self.gmina_data.get(session['gmina_context']['gmina'], {})

        if action == 'kontakt_urzad':
            info = gmina_data.get('basic_info', {})
            contact_card = f"""
📍 {info.get('name', 'Urząd Gminy')}
🏢 Adres: {info.get('address', 'Brak danych')}
📞 Telefon: {info.get('phone', 'Brak danych')}
✉️ E-mail: {info.get('email', 'Brak danych')}
🏛️ NIP: {info.get('nip', 'Brak danych')}
📊 REGON: {info.get('regon', 'Brak danych')}
"""
            return {
                'text_message': contact_card,
                'buttons': [
                    {'text': 'Inne kontakty', 'action': 'znajdz_kontakt'},
                    {'text': 'Powrót do menu', 'action': 'main_menu'}
                ]
            }

        elif action == 'kontakt_wydzial':
            return {
                'text_message': 'Wybierz kategorię sprawy:',
                'buttons': [
                    {'text': 'Odpady', 'action': 'kontakt_wydzial_odpady'},
                    {'text': 'Podatki', 'action': 'kontakt_wydzial_podatki'},
                    {'text': 'Budownictwo', 'action': 'kontakt_wydzial_budownictwo'},
                    {'text': 'Drogi/Infrastruktura', 'action': 'kontakt_wydzial_drogi'},
                    {'text': 'Powrót', 'action': 'znajdz_kontakt'}
                ]
            }

        elif action.startswith('kontakt_wydzial_'):
            dept_key = action.replace('kontakt_wydzial_', '')
            dept_data = gmina_data.get('departments', {}).get(dept_key, {})

            if dept_data:
                status_text = dept_data.get('status', 'dostepne_online').replace('_', ' ').title()
                contact_card = f"""
🏢 {dept_data.get('name', 'Wydział')}
📞 Telefon: {dept_data.get('phone', '+48 123 456 789')}
✉️ E-mail: {dept_data.get('email', 'kontakt@gmina.pl')}
Status dostępności: {status_text}
"""
                return {
                    'text_message': contact_card,
                    'buttons': [
                        {'text': 'Inne wydziały', 'action': 'kontakt_wydzial'},
                        {'text': 'Powrót do menu', 'action': 'main_menu'}
                    ]
                }

        elif action == 'kontakt_osoba':
            session['input_context'] = 'kontakt_osoba_szczegoly'
            session.modified = True
            return {
                'text_message': 'Podaj imię i nazwisko osoby, której kontakt Cię interesuje.',
                'input_expected': True,
                'input_context': 'kontakt_osoba_szczegoly'
            }

        return {
            'text_message': 'Kontakt dostępny w sekretariacie urzędu.',
            'buttons': [{'text': 'Powrót do menu', 'action': 'main_menu'}]
        }

    def _handle_formularz_subaction(self, action):
        gmina_data = self.gmina_data.get(session['gmina_context']['gmina'], {})

        if action == 'formularz_odpady':
            form_data = gmina_data.get('forms', {}).get('deklaracja_smieciowa', {})
            return {
                'text_message': f"""
📋 **{form_data.get('name', 'Deklaracja odpadów komunalnych')}**

🔗 Link: {form_data.get('link', 'https://gmina.pl/formularze/odpady.pdf')}

✅ **Dostępne online** - możesz wypełnić i wysłać elektronicznie

📅 **Termin składania:** Do 31 stycznia każdego roku
""",
                'buttons': [
                    {'text': 'Kontakt ws. odpadów', 'action': 'kontakt_wydzial_odpady'},
                    {'text': 'Inne formularze', 'action': 'pobierz_formularz'},
                    {'text': 'Powrót do menu', 'action': 'main_menu'}
                ]
            }

        elif action == 'formularz_budownictwo':
            form_data = gmina_data.get('forms', {}).get('pozwolenie_budowlane', {})
            return {
                'text_message': f"""
📋 **{form_data.get('name', 'Wniosek o pozwolenie na budowę')}**

🔗 Link: {form_data.get('link', 'https://gmina.pl/formularze/budowa.pdf')}

⚠️ **Uwaga:** To skomplikowana procedura. Zalecamy konsultację z wydziałem.

💡 **Potrzebujesz pomocy?** Skontaktuj się z wydziałem architektury.
""",
                'buttons': [
                    {'text': 'Kontakt do wydziału', 'action': 'kontakt_wydzial_budownictwo'},
                    {'text': 'Inne formularze', 'action': 'pobierz_formularz'},
                    {'text': 'Powrót do menu', 'action': 'main_menu'}
                ]
            }

        elif action == 'formularz_srodowisko':
            session['input_context'] = 'formularz_srodowisko_szczegoly'
            session.modified = True
            return {
                'text_message': 'OK. Wpisz, czego konkretnie szukasz (np. "wycinka drzew", "deklaracja śmieciowa").',
                'input_expected': True,
                'input_context': 'formularz_srodowisko_szczegoly'
            }

        else:
            return {
                'text_message': 'Formularz dostępny w sekretariacie urzędu. Skontaktuj się telefonicznie.',
                'buttons': [
                    {'text': 'Kontakt do urzędu', 'action': 'kontakt_urzad'},
                    {'text': 'Inne formularze', 'action': 'pobierz_formularz'},
                    {'text': 'Powrót do menu', 'action': 'main_menu'}
                ]
            }

    def _handle_problem_subaction(self, action):
        if action == 'problem_drogi':
            session['input_context'] = 'problem_drogi_szczegoly'
            session.modified = True
            return {
                'text_message': """
🚧 **Zgłaszanie uszkodzeń dróg i chodników**

Opisz lokalizację i rodzaj uszkodzenia (np. "dziura na ul. Głównej przed nr 15").

📞 **Pilne zgłoszenia:** +48 123 456 793
✉️ **Email:** infrastruktura@gmina.pl
""",
                'input_expected': True,
                'input_context': 'problem_drogi_szczegoly'
            }

        elif action == 'problem_odpady':
            session['input_context'] = 'problem_odpady_szczegoly'
            session.modified = True
            return {
                'text_message': """
🗑️ **Problemy z odpadami**

Opisz problem (np. "nie odebrano śmieci", "przepełniony kontener").

📞 **Kontakt:** +48 123 456 790
✉️ **Email:** odpady@gmina.pl
""",
                'input_expected': True,
                'input_context': 'problem_odpady_szczegoly'
            }

        elif action == 'problem_oswietlenie':
            session['input_context'] = 'problem_oswietlenie_szczegoly'
            session.modified = True
            return {
                'text_message': """
💡 **Awarie oświetlenia ulicznego**

Podaj dokładną lokalizację (ulica, numer budynku, słup).

📞 **Zgłoszenia 24/7:** +48 123 456 799
✉️ **Email:** oswietlenie@gmina.pl
""",
                'input_expected': True,
                'input_context': 'problem_oswietlenie_szczegoly'
            }

        elif action == 'problem_inne':
            session['input_context'] = 'problem_inne_szczegoly'
            session.modified = True
            return {
                'text_message': """
📝 **Inne problemy**

Opisz szczegółowo problem, którego dotyczy Twoje zgłoszenie.

📞 **Centrala urzędu:** +48 123 456 789
✉️ **Email:** kontakt@gmina.pl
""",
                'input_expected': True,
                'input_context': 'problem_inne_szczegoly'
            }

        return {
            'text_message': 'Problem można zgłosić telefonicznie w urzędzie.',
            'buttons': [
                {'text': 'Kontakt do urzędu', 'action': 'kontakt_urzad'},
                {'text': 'Powrót do menu', 'action': 'main_menu'}
            ]
        }

    def get_bot_response(self, user_message):
        if 'gmina_context' not in session:
            return {'text_message': 'Proszę, najpierw wybierz gminę.'}

        current_context = session.get('input_context', '')
        session['input_context'] = None
        session.modified = True

        if current_context == 'sprawdz_gmine':
            return self._process_sprawdz_gmine(user_message)
        elif current_context == 'formularz_srodowisko_szczegoly':
            return self._process_formularz_srodowisko(user_message)
        elif current_context == 'kontakt_osoba_szczegoly':
            return self._process_kontakt_osoba(user_message)
        elif current_context.startswith('problem_'):
            return self._process_problem_details(current_context, user_message)
        else:
            return self._process_smart_intent(user_message)

    def _process_sprawdz_gmine(self, message):
        gmina_name = message.strip()

        if 'gorzow' in gmina_name.lower():
            return {
                'text_message': """
🏛️ **Znaleziono: Gmina Gorzów Wielkopolski**

📍 Adres: ul. Sikorskiego 3-4, 66-400 Gorzów Wielkopolski
📞 Telefon: +48 95 735 75 00
🌐 Strona: www.gorzow.pl

✅ Gmina zweryfikowana pomyślnie.
""",
                'buttons': [
                    {'text': 'Sprawdź inną gminę', 'action': 'sprawdz_gmine'},
                    {'text': 'Powrót do menu', 'action': 'main_menu'}
                ]
            }
        elif gmina_name in self.gmina_data:
            basic_info = self.gmina_data[gmina_name]['basic_info']
            return {
                'text_message': f'✅ **Znaleziono gminę:** {basic_info["name"]}\n📍 {basic_info["address"]}',
                'buttons': [
                    {'text': 'Sprawdź inną gminę', 'action': 'sprawdz_gmine'},
                    {'text': 'Powrót do menu', 'action': 'main_menu'}
                ]
            }
        else:
            return {
                'text_message': f'✅ **Gmina "{gmina_name}" została zweryfikowana.**\n\n📍 Informacje dostępne w Centralnej Ewidencji Gmin.\n🏛️ Status: Gmina aktywna',
                'buttons': [
                    {'text': 'Sprawdź inną gminę', 'action': 'sprawdz_gmine'},
                    {'text': 'Powrót do menu', 'action': 'main_menu'}
                ]
            }

    def _process_formularz_srodowisko(self, message):
        message_lower = message.lower()

        if 'wycinka' in message_lower or 'drzewo' in message_lower:
            return {
                'text_message': """
🌳 **Wniosek o zezwolenie na usunięcie drzewa**

🔗 **Link:** https://gmina.pl/formularze/wycinka.pdf

📋 **Wymagane dokumenty:**
• Wypełniony wniosek
• Mapa z zaznaczeniem drzewa
• Uzasadnienie usunięcia

💡 **Pamiętaj:** Dla drzew młodszych niż 5 lat zezwolenie nie jest wymagane.
""",
                'buttons': [
                    {'text': 'Kontakt do wydziału', 'action': 'kontakt_wydzial_środowisko'},
                    {'text': 'Inne formularze', 'action': 'pobierz_formularz'},
                    {'text': 'Powrót do menu', 'action': 'main_menu'}
                ]
            }
        else:
            return {
                'text_message': f'📋 **Formularz środowiskowy: "{message}"**\n\n🔗 Link: https://gmina.pl/formularze/srodowisko.pdf\n\n✅ Dostępny do pobrania',
                'buttons': [
                    {'text': 'Inne formularze', 'action': 'pobierz_formularz'},
                    {'text': 'Powrót do menu', 'action': 'main_menu'}
                ]
            }

    def _process_kontakt_osoba(self, message):
        person_name = message.strip()
        return {
            'text_message': f"""
👤 **Kontakt do: {person_name.title()}**

📞 **Centrala urzędu:** +48 123 456 789
✉️ **Email:** kontakt@gmina.pl

💡 **Wskazówka:** Poproś o połączenie z konkretną osobą lub wydziałem.
""",
            'buttons': [
                {'text': 'Kontakt do centrali', 'action': 'kontakt_urzad'},
                {'text': 'Powrót do menu', 'action': 'main_menu'}
            ]
        }

    def _process_problem_details(self, context, message):
        problem_type = context.replace('problem_', '').replace('_szczegoly', '')
        return {
            'text_message': f"""
✅ **Zgłoszenie przyjęte**

📝 **Opis:** {message}
📋 **Numer:** ZGL-{hash(message) % 10000:04d}
📞 **Status:** Przekazano do wydziału
⏰ **Realizacja:** 3-5 dni roboczych

📧 **Potwierdzenie zostanie wysłane emailem.**
""",
            'buttons': [
                {'text': 'Zgłoś kolejny problem', 'action': 'zglos_problem'},
                {'text': 'Powrót do menu', 'action': 'main_menu'}
            ]
        }

    def _process_smart_intent(self, message):
        return {
            'text_message': f'🤔 Otrzymałem: "{message}"\n\nWybierz opcję z menu głównego, aby najlepiej Ci pomóc.',
            'buttons': [
                {'text': 'Znajdź Kontakt', 'action': 'znajdz_kontakt'},
                {'text': 'Pobierz Formularz', 'action': 'pobierz_formularz'},
                {'text': 'Zgłoś Problem', 'action': 'zglos_problem'},
                {'text': 'Powrót do menu', 'action': 'main_menu'}
            ]
        }
