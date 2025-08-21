"""
gmina_bot.py - Silnik bota "Adept" dla Gmina-AI
Wersja 2.1 - Naprawiono logikę hybrydową i dodano brakujące funkcje
"""
import json
import os
import re
from flask import session

class GminaBot:
    def __init__(self):
        """
        Inicjalizacja bota z naprawioną architekturą hybrydową
        """
        self.gmina_data = {}
        self.contacts_data = {}
        self.forms_data = {}

        # Mapowanie kategorii spraw na kolory statusu
        self.status_colors = {
            'dostepne_online': 'green-dot',
            'wymaga_wizyty': 'orange-dot',
            'skomplikowane': 'red-dot',
            'brak_danych': 'grey-dot'
        }

        # Rozszerzony słownik kategorii spraw (NAPRAWKA LOGIKI HYBRYDOWEJ)
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
        """
        Rozszerzone dane testowe - uzupełniono brakujące kategorie
        """
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
                    'odpady': {
                        'name': 'Referat Gospodarki Komunalnej',
                        'phone': '+48 123 456 790',
                        'email': 'odpady@przykladowa.pl',
                        'status': 'dostepne_online'
                    },
                    'podatki': {
                        'name': 'Referat Finansowy',
                        'phone': '+48 123 456 791',
                        'email': 'finanse@przykladowa.pl',
                        'status': 'wymaga_wizyty'
                    },
                    'budownictwo': {
                        'name': 'Referat Architektury',
                        'phone': '+48 123 456 792',
                        'email': 'architektura@przykladowa.pl',
                        'status': 'skomplikowane'
                    },
                    'drogi': {
                        'name': 'Referat Infrastruktury',
                        'phone': '+48 123 456 793',
                        'email': 'infrastruktura@przykladowa.pl',
                        'status': 'dostepne_online'
                    },
                    'działalność': {
                        'name': 'Referat Rozwoju Gospodarczego',
                        'phone': '+48 123 456 794',
                        'email': 'gospodarka@przykladowa.pl',
                        'status': 'wymaga_wizyty'
                    }
                },
                'forms': {
                    'deklaracja_smieciowa': {
                        'name': 'Deklaracja odpadów komunalnych',
                        'link': 'https://przykladowa.pl/formularze/odpady.pdf',
                        'status': 'dostepne_online'
                    },
                    'pozwolenie_budowlane': {
                        'name': 'Wniosek o pozwolenie na budowę',
                        'link': 'https://przykladowa.pl/formularze/budowa.pdf',
                        'status': 'skomplikowane'
                    },
                    'wycinka_drzew': {
                        'name': 'Wniosek o zezwolenie na usunięcie drzewa',
                        'link': 'https://przykladowa.pl/formularze/wycinka.pdf',
                        'status': 'dostepne_online'
                    },
                    'rejestracja_firmy': {
                        'name': 'Zgłoszenie działalności gospodarczej',
                        'link': 'https://przykladowa.pl/formularze/firma.pdf',
                        'status': 'wymaga_wizyty'
                    }
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
                    'odpady': {
                        'name': 'Wydział Ekologii',
                        'phone': '+48 987 654 322',
                        'email': 'ekologia@demo.pl',
                        'status': 'dostepne_online'
                    }
                },
                'forms': {}
            }
        }

    def set_gmina_context(self, context):
        """
        Ustawia kontekst gminy w sesji
        """
        gmina_name = context.get('gmina')
        if gmina_name and gmina_name in self.gmina_data:
            session['gmina_context'] = context
            session['chat_history'] = []
            session['current_path'] = 'start'
            session['input_context'] = None
            session.modified = True
            print(f"[DEBUG] Kontekst ustawiony dla gminy: {gmina_name}")
        else:
            print(f"[ERROR] Brak danych dla gminy: {gmina_name}")

    def get_initial_greeting(self):
        """
        ZMIANA: Nowe menu główne z przyciskiem "Zgłoś Problem"
        """
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
        """
        NAPRAWKA: Poprawiona obsługa akcji przycisków z zachowaniem kontekstu
        """
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
                'text_message': 'Nie rozpoznaję tej opcji. Wybierz jedną z dostępnych opcji.',
                'buttons': [
                    {'text': 'Powrót do menu', 'action': 'main_menu'}
                ]
            }

    def _handle_znajdz_kontakt(self):
        """Obsługuje ścieżkę "Znajdź Kontakt" """
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
        """ZMIANA: Dodano więcej kategorii formularzy"""
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
        """NOWA FUNKCJA: Obsługuje zgłaszanie problemów"""
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
        """Obsługuje ścieżkę "Sprawdź Gminę" """
        session['input_context'] = 'sprawdz_gmine'
        session.modified = True
        return {
            'text_message': 'Podaj nazwę gminy, którą chcesz zweryfikować.',
            'input_expected': True,
            'input_context': 'sprawdz_gmine'
        }

    def _handle_kontakt_subaction(self, action):
        """Obsługuje podakcje w sekcji kontaktów"""
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
                status_text = dept_data.get('status', 'brak_danych').replace('_', ' ').title()
                contact_card = f"""
🏢 {dept_data.get('name', 'Wydział')}
📞 Telefon: {dept_data.get('phone', 'Brak danych')}
✉️ E-mail: {dept_data.get('email', 'Brak danych')}
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
            'text_message': 'Nie znaleziono informacji o tym kontakcie.',
            'buttons': [{'text': 'Powrót do menu', 'action': 'main_menu'}]
        }

    def _handle_formularz_subaction(self, action):
        """Obsługuje podakcje w sekcji formularzy z funkcją upsell"""
        gmina_data = self.gmina_data.get(session['gmina_context']['gmina'], {})

        if action == 'formularz_srodowisko':
            session['input_context'] = 'formularz_srodowisko_szczegoly'
            session.modified = True
            return {
                'text_message': 'OK. Wpisz, czego konkretnie szukasz (np. "wycinka drzew", "deklaracja śmieciowa").',
                'input_expected': True,
                'input_context': 'formularz_srodowisko_szczegoly'
            }

        elif action == 'formularz_budownictwo':
            form_data = gmina_data.get('forms', {}).get('pozwolenie_budowlane', {})
            return {
                'text_message': f"""
📋 **{form_data.get('name', 'Wniosek o pozwolenie na budowę')}**

🔗 Link: {form_data.get('link', 'Brak linku')}

⚠️ **Uwaga:** To skomplikowana procedura. Zalecamy konsultację z wydziałem przed złożeniem wniosku.

💡 **Potrzebujesz pomocy z wypełnieniem?** Możemy Cię połączyć z odpowiednim wydziałem.
""",
                'buttons': [
                    {'text': 'Kontakt do wydziału', 'action': 'kontakt_wydzial_budownictwo'},
                    {'text': 'Inne formularze', 'action': 'pobierz_formularz'},
                    {'text': 'Powrót do menu', 'action': 'main_menu'}
                ]
            }

        elif action == 'formularz_dzialalnosc':
            form_data = gmina_data.get('forms', {}).get('rejestracja_firmy', {})
            return {
                'text_message': f"""
📋 **{form_data.get('name', 'Zgłoszenie działalności gospodarczej')}**

🔗 Link: {form_data.get('link', 'Brak linku')}

📝 **Wymagane dokumenty:**
• Wypełniony formularz CEIDG-1
• Kopia dowodu osobistego
• Oświadczenie o niekaralności

💼 **Potrzebujesz wsparcia?** Nasz wydział pomoże Ci przejść przez proces rejestracji.
""",
                'buttons': [
                    {'text': 'Kontakt do wydziału', 'action': 'kontakt_wydzial_działalność'},
                    {'text': 'Inne formularze', 'action': 'pobierz_formularz'},
                    {'text': 'Powrót do menu', 'action': 'main_menu'}
                ]
            }

        elif action == 'formularz_odpady':
            form_data = gmina_data.get('forms', {}).get('deklaracja_smieciowa', {})
            return {
                'text_message': f"""
📋 **{form_data.get('name', 'Deklaracja odpadów komunalnych')}**

🔗 Link: {form_data.get('link', 'Brak linku')}

✅ **Dostępne online** - możesz wypełnić i wysłać elektronicznie

📅 **Termin składania:** Do 31 stycznia każdego roku
""",
                'buttons': [
                    {'text': 'Inne formularze', 'action': 'pobierz_formularz'},
                    {'text': 'Kontakt ws. odpadów', 'action': 'kontakt_wydzial_odpady'},
                    {'text': 'Powrót do menu', 'action': 'main_menu'}
                ]
            }

        return {
            'text_message': 'Ta kategoria jest w trakcie przygotowywania.',
            'buttons': [
                {'text': 'Wybierz inną kategorię', 'action': 'pobierz_formularz'},
                {'text': 'Powrót do menu', 'action': 'main_menu'}
            ]
        }

    def _handle_problem_subaction(self, action):
        """Obsługuje zgłaszanie różnych typów problemów"""
        if action == 'problem_drogi':
            session['input_context'] = 'problem_drogi_szczegoly'
            session.modified = True
            return {
                'text_message': """
🚧 **Zgłaszanie uszkodzeń dróg i chodników**

Opisz lokalizację i rodzaj uszkodzenia (np. "dziura na ul. Głównej przed nr 15").

📞 **Pilne zgłoszenia:** +48 123 456 793
✉️ **Email:** infrastruktura@przykladowa.pl

💡 **Tip:** Dołącz zdjęcie, jeśli to możliwe.
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
✉️ **Email:** odpady@przykladowa.pl
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
✉️ **Email:** oswietlenie@przykladowa.pl
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
✉️ **Email:** kontakt@przykladowa.pl
""",
                'input_expected': True,
                'input_context': 'problem_inne_szczegoly'
            }

        return {
            'text_message': 'Nie rozpoznaję tego typu problemu.',
            'buttons': [
                {'text': 'Powrót do zgłoszeń', 'action': 'zglos_problem'},
                {'text': 'Powrót do menu', 'action': 'main_menu'}
            ]
        }

    def get_bot_response(self, user_message):
        """
        NAPRAWKA KRYTYCZNA: Poprawione przetwarzanie wiadomości tekstowych
        """
        if 'gmina_context' not in session:
            return {'text_message': 'Proszę, najpierw wybierz gminę.'}

        current_context = session.get('input_context', '')
        print(f"[DEBUG] Kontekst wejściowy: {current_context}")
        print(f"[DEBUG] Wiadomość użytkownika: {user_message}")

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
        """Lepsza weryfikacja gmin"""
        gmina_name = message.strip()

        if gmina_name.lower() in ['biała', 'biala']:
            return {
                'text_message': 'W Polsce jest kilkanaście gmin o tej nazwie. Aby wskazać właściwą, podaj kod pocztowy lub miasto powiatowe.',
                'input_expected': True,
                'input_context': 'sprawdz_gmine_szczegoly'
            }
        elif 'gorzow' in gmina_name.lower():
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
                'text_message': f'❌ Nie znalazłem gminy "{gmina_name}" w bazie danych. Sprawdź pisownię i spróbuj ponownie.',
                'buttons': [
                    {'text': 'Spróbuj ponownie', 'action': 'sprawdz_gmine'},
                    {'text': 'Powrót do menu', 'action': 'main_menu'}
                ]
            }

    def _process_formularz_srodowisko(self, message):
        """Poprawione rozpoznawanie słów kluczowych"""
        message_lower = message.lower()

        if 'wycinka' in message_lower or 'drzewo' in message_lower:
            return {
                'text_message': """
🌳 **Wniosek o zezwolenie na usunięcie drzewa**

🔗 **Link do formularza:** https://przykladowa.pl/formularze/wycinka.pdf

📋 **Wymagane dokumenty:**
• Wypełniony wniosek
• Mapa z zaznaczeniem drzewa
• Uzasadnienie usunięcia

💡 **Pamiętaj:** Dla drzew młodszych niż 5 lat zezwolenie nie jest wymagane.

🏢 **Potrzebujesz pomocy?** Skontaktuj się z wydziałem środowiska.
""",
                'buttons': [
                    {'text': 'Kontakt do wydziału', 'action': 'kontakt_wydzial_środowisko'},
                    {'text': 'Inne formularze środowiskowe', 'action': 'formularz_srodowisko'},
                    {'text': 'Powrót do menu', 'action': 'main_menu'}
                ]
            }
        elif 'deklaracja' in message_lower and 'śmiec' in message_lower:
            form_data = self.gmina_data.get(session['gmina_context']['gmina'], {}).get('forms', {}).get('deklaracja_smieciowa', {})
            return {
                'text_message': f"""
📋 **{form_data.get('name', 'Deklaracja odpadów komunalnych')}**

🔗 **Link:** {form_data.get('link', 'Brak linku')}

✅ **Status:** Dostępne online
📅 **Termin:** Do 31 stycznia każdego roku

💡 **Potrzebujesz pomocy z wypełnieniem?**
""",
                'buttons': [
                    {'text': 'Kontakt ws. odpadów', 'action': 'kontakt_wydzial_odpady'},
                    {'text': 'Inne formularze', 'action': 'pobierz_formularz'},
                    {'text': 'Powrót do menu', 'action': 'main_menu'}
                ]
            }
        else:
            return {
                'text_message': 'Nie znalazłem formularza dla tego zapytania. Spróbuj użyć innych słów kluczowych (np. "wycinka drzew", "deklaracja śmieciowa").',
                'buttons': [
                    {'text': 'Spróbuj ponownie', 'action': 'formularz_srodowisko'},
                    {'text': 'Inne kategorie', 'action': 'pobierz_formularz'},
                    {'text': 'Powrót do menu', 'action': 'main_menu'}
                ]
            }

    def _process_kontakt_osoba(self, message):
        """Wyszukiwanie kontaktu do konkretnej osoby"""
        person_name = message.strip()

        mock_contacts = {
            'jan kowalski': {'stanowisko': 'Kierownik Referatu Finansowego', 'telefon': '+48 123 456 801', 'email': 'j.kowalski@przykladowa.pl'},
            'anna nowak': {'stanowisko': 'Specjalista ds. Środowiska', 'telefon': '+48 123 456 802', 'email': 'a.nowak@przykladowa.pl'},
            'marek': {'stanowisko': 'Kierownik Referatu Infrastruktury', 'telefon': '+48 123 456 803', 'email': 'marek@przykladowa.pl'}
        }

        contact = mock_contacts.get(person_name.lower())

        if contact:
            return {
                'text_message': f"""
👤 **{person_name.title()}**
🏢 Stanowisko: {contact['stanowisko']}
📞 Telefon: {contact['telefon']}
✉️ E-mail: {contact['email']}
""",
                'buttons': [
                    {'text': 'Szukaj innej osoby', 'action': 'kontakt_osoba'},
                    {'text': 'Powrót do menu', 'action': 'main_menu'}
                ]
            }
        else:
            return {
                'text_message': f'❌ Nie znaleziono kontaktu do osoby "{person_name}". Sprawdź pisownię lub skontaktuj się z centralą urzędu.',
                'buttons': [
                    {'text': 'Spróbuj ponownie', 'action': 'kontakt_osoba'},
                    {'text': 'Kontakt do centrali', 'action': 'kontakt_urzad'},
                    {'text': 'Powrót do menu', 'action': 'main_menu'}
                ]
            }

    def _process_problem_details(self, context, message):
        """Przetwarzanie szczegółów zgłoszeń problemów"""
        problem_type = context.replace('problem_', '').replace('_szczegoly', '')

        confirmation_msg = f"""
✅ **Zgłoszenie przyjęte**

📝 **Opis problemu:** {message}

📋 **Numer zgłoszenia:** ZGL-{hash(message) % 10000:04d}

📞 **Status:** Przekazano do odpowiedniego wydziału
⏰ **Czas realizacji:** 3-5 dni roboczych

📧 **Potwierdzenie zostanie wysłane na Twój adres email.**

💡 **Potrzebujesz pilnej pomocy?** Zadzwoń bezpośrednio do wydziału.
"""

        return {
            'text_message': confirmation_msg,
            'buttons': [
                {'text': 'Zgłoś kolejny problem', 'action': 'zglos_problem'},
                {'text': 'Kontakt do wydziału', 'action': f'kontakt_wydzial_{problem_type}'},
                {'text': 'Powrót do menu', 'action': 'main_menu'}
            ]
        }

    def _process_smart_intent(self, message):
        """Inteligentne rozpoznawanie intencji użytkownika"""
        message_lower = message.lower()

        for category, keywords in self.category_map.items():
            if any(keyword in message_lower for keyword in keywords):
                if category == 'drogi':
                    return {
                        'text_message': f'🚧 Rozpoznałem, że Twoje pytanie dotyczy **dróg/infrastruktury**.\n\nTwoje zapytanie: "{message}"\n\nCzy chcesz:',
                        'buttons': [
                            {'text': 'Zgłosić uszkodzenie', 'action': 'problem_drogi'},
                            {'text': 'Znaleźć kontakt', 'action': 'kontakt_wydzial_drogi'},
                            {'text': 'Powrót do menu', 'action': 'main_menu'}
                        ]
                    }
                elif category == 'odpady':
                    return {
                        'text_message': f'🗑️ Rozpoznałem, że Twoje pytanie dotyczy **odpadów**.\n\nTwoje zapytanie: "{message}"\n\nCzy chcesz:',
                        'buttons': [
                            {'text': 'Pobrać formularz', 'action': 'formularz_odpady'},
                            {'text': 'Znaleźć kontakt', 'action': 'kontakt_wydzial_odpady'},
                            {'text': 'Zgłosić problem', 'action': 'problem_odpady'},
                            {'text': 'Powrót do menu', 'action': 'main_menu'}
                        ]
                    }
                elif category == 'środowisko':
                    return {
                        'text_message': f'🌳 Rozpoznałem, że Twoje pytanie dotyczy **ochrony środowiska**.\n\nTwoje zapytanie: "{message}"\n\nCzy chcesz:',
                        'buttons': [
                            {'text': 'Pobrać formularz', 'action': 'formularz_srodowisko'},
                            {'text': 'Znaleźć kontakt', 'action': 'kontakt_wydzial_środowisko'},
                            {'text': 'Powrót do menu', 'action': 'main_menu'}
                        ]
                    }

        return {
            'text_message': f'🤔 Otrzymałem Twoją wiadomość: "{message}"\n\nNie jestem pewien, jak najlepiej Ci pomóc. Wybierz jedną z opcji poniżej lub skorzystaj z menu głównego.',
            'buttons': [
                {'text': 'Znajdź Kontakt', 'action': 'znajdz_kontakt'},
                {'text': 'Pobierz Formularz', 'action': 'pobierz_formularz'},
                {'text': 'Zgłoś Problem', 'action': 'zglos_problem'},
                {'text': 'Powrót do menu', 'action': 'main_menu'}
            ]
        }
