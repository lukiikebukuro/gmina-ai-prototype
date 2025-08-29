"""gmina_bot.py - Silnik bota Adept dla Gmina-AI ENTERPRISE v3.0"""
import json
import os
import re
from flask import session
from datetime import datetime
import random
from fuzzywuzzy import fuzz


class GminaBot:
    def __init__(self):
        self.gmina_data = {}
        self.search_database = {}
        self.initialize_search_database()
        
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

    def initialize_search_database(self):
        """Inicjalizuje rozbudowaną bazę danych dla wyszukiwania predykcyjnego"""
        self.search_database = {
            'contacts': {
                'persons': [
                    {'name': 'Jan Kowalski', 'position': 'Wójt Gminy', 'phone': '+48 123 456 701', 'email': 'wojt@gmina.pl', 'department': 'Zarząd'},
                    {'name': 'Anna Nowak', 'position': 'Sekretarz Gminy', 'phone': '+48 123 456 702', 'email': 'sekretarz@gmina.pl', 'department': 'Sekretariat'},
                    {'name': 'Piotr Wiśniewski', 'position': 'Skarbnik Gminy', 'phone': '+48 123 456 703', 'email': 'skarbnik@gmina.pl', 'department': 'Finanse'},
                    {'name': 'Maria Zielińska', 'position': 'Kierownik USC', 'phone': '+48 123 456 704', 'email': 'usc@gmina.pl', 'department': 'Urząd Stanu Cywilnego'},
                    {'name': 'Tomasz Kamiński', 'position': 'Inspektor ds. Budownictwa', 'phone': '+48 123 456 705', 'email': 'budownictwo@gmina.pl', 'department': 'Architektura'},
                    {'name': 'Ewa Lewandowska', 'position': 'Podinspektor ds. Ochrony Środowiska', 'phone': '+48 123 456 706', 'email': 'srodowisko@gmina.pl', 'department': 'Ochrona Środowiska'},
                    {'name': 'Krzysztof Wójcik', 'position': 'Kierownik Referatu Podatkowego', 'phone': '+48 123 456 707', 'email': 'podatki@gmina.pl', 'department': 'Finanse'},
                    {'name': 'Magdalena Kozłowska', 'position': 'Inspektor ds. Gospodarki Komunalnej', 'phone': '+48 123 456 708', 'email': 'komunalna@gmina.pl', 'department': 'Gospodarka Komunalna'},
                    {'name': 'Robert Jankowski', 'position': 'Kierownik GOPS', 'phone': '+48 123 456 709', 'email': 'gops@gmina.pl', 'department': 'Pomoc Społeczna'},
                    {'name': 'Agnieszka Mazur', 'position': 'Informatyk', 'phone': '+48 123 456 710', 'email': 'it@gmina.pl', 'department': 'IT'},
                    {'name': 'Paweł Krawczyk', 'position': 'Inspektor ds. Inwestycji', 'phone': '+48 123 456 711', 'email': 'inwestycje@gmina.pl', 'department': 'Rozwój i Inwestycje'},
                    {'name': 'Joanna Piotrowska', 'position': 'Radca Prawny', 'phone': '+48 123 456 712', 'email': 'prawnik@gmina.pl', 'department': 'Obsługa Prawna'},
                    {'name': 'Stanisław Dąbrowski', 'position': 'Inspektor ds. Zamówień Publicznych', 'phone': '+48 123 456 713', 'email': 'zamowienia@gmina.pl', 'department': 'Zamówienia Publiczne'},
                    {'name': 'Katarzyna Szymańska', 'position': 'Specjalista ds. Funduszy UE', 'phone': '+48 123 456 714', 'email': 'fundusze@gmina.pl', 'department': 'Rozwój i Inwestycje'},
                    {'name': 'Marek Pawłowski', 'position': 'Kierownik Referatu Oświaty', 'phone': '+48 123 456 715', 'email': 'oswiata@gmina.pl', 'department': 'Oświata'},
                    {'name': 'Beata Michalska', 'position': 'Inspektor ds. Ewidencji Ludności', 'phone': '+48 123 456 716', 'email': 'ewidencja@gmina.pl', 'department': 'Ewidencja Ludności'},
                    {'name': 'Andrzej Nowakowski', 'position': 'Geodeta Gminny', 'phone': '+48 123 456 717', 'email': 'geodeta@gmina.pl', 'department': 'Geodezja'},
                    {'name': 'Alicja Wróblewska', 'position': 'Inspektor ds. Promocji', 'phone': '+48 123 456 718', 'email': 'promocja@gmina.pl', 'department': 'Promocja i Kultura'},
                    {'name': 'Rafał Kaczmarek', 'position': 'Komendant Straży Gminnej', 'phone': '+48 123 456 719', 'email': 'straz@gmina.pl', 'department': 'Straż Gminna'},
                    {'name': 'Dorota Grabowska', 'position': 'Kierownik OPS', 'phone': '+48 123 456 720', 'email': 'ops@gmina.pl', 'department': 'Pomoc Społeczna'}
                ],
                'departments': [
                    {'name': 'Sekretariat', 'phone': '+48 123 456 700', 'email': 'sekretariat@gmina.pl', 'hours': 'Pon-Pt: 7:30-15:30'},
                    {'name': 'Referat Finansowy', 'phone': '+48 123 456 720', 'email': 'finanse@gmina.pl', 'hours': 'Pon-Pt: 8:00-16:00'},
                    {'name': 'Referat Architektury i Budownictwa', 'phone': '+48 123 456 730', 'email': 'architektura@gmina.pl', 'hours': 'Pon, Śr, Pt: 8:00-15:00'},
                    {'name': 'Referat Gospodarki Komunalnej', 'phone': '+48 123 456 740', 'email': 'komunalna@gmina.pl', 'hours': 'Pon-Pt: 7:00-15:00'},
                    {'name': 'Urząd Stanu Cywilnego', 'phone': '+48 123 456 750', 'email': 'usc@gmina.pl', 'hours': 'Pon-Pt: 8:00-16:00, Śr: do 18:00'},
                    {'name': 'Referat Ochrony Środowiska', 'phone': '+48 123 456 760', 'email': 'srodowisko@gmina.pl', 'hours': 'Pon-Pt: 7:30-15:30'},
                    {'name': 'Gminny Ośrodek Pomocy Społecznej', 'phone': '+48 123 456 770', 'email': 'gops@gmina.pl', 'hours': 'Pon-Pt: 7:30-15:30'},
                    {'name': 'Referat Rozwoju i Inwestycji', 'phone': '+48 123 456 780', 'email': 'rozwoj@gmina.pl', 'hours': 'Pon-Pt: 8:00-16:00'},
                    {'name': 'Referat Oświaty', 'phone': '+48 123 456 790', 'email': 'oswiata@gmina.pl', 'hours': 'Pon-Pt: 8:00-16:00'},
                    {'name': 'Referat Geodezji', 'phone': '+48 123 456 800', 'email': 'geodezja@gmina.pl', 'hours': 'Pon, Śr: 8:00-16:00'},
                    {'name': 'Straż Gminna', 'phone': '+48 123 456 810', 'email': 'straz@gmina.pl', 'hours': '24/7 - dyżury'},
                    {'name': 'Biuro Promocji i Kultury', 'phone': '+48 123 456 820', 'email': 'promocja@gmina.pl', 'hours': 'Pon-Pt: 9:00-17:00'}
                ]
            },
            'forms': [
                {'name': 'Deklaracja o wysokości opłaty za gospodarowanie odpadami', 'category': 'odpady', 'code': 'DO-1', 'online': True},
                {'name': 'Wniosek o wydanie pozwolenia na budowę', 'category': 'budownictwo', 'code': 'PB-1', 'online': False},
                {'name': 'Zgłoszenie robót budowlanych', 'category': 'budownictwo', 'code': 'ZRB-1', 'online': True},
                {'name': 'Wniosek o wydanie wypisu z miejscowego planu', 'category': 'budownictwo', 'code': 'WMP-1', 'online': True},
                {'name': 'Wniosek o ustalenie numeru porządkowego', 'category': 'budownictwo', 'code': 'NP-1', 'online': False},
                {'name': 'Wniosek o wycinkę drzew', 'category': 'srodowisko', 'code': 'WD-1', 'online': True},
                {'name': 'Zgłoszenie zamiaru usunięcia drzewa', 'category': 'srodowisko', 'code': 'ZUD-1', 'online': True},
                {'name': 'Wniosek o wydanie zezwolenia na sprzedaż alkoholu', 'category': 'dzialalnosc', 'code': 'ZA-1', 'online': False},
                {'name': 'Wniosek o wpis do ewidencji działalności gospodarczej', 'category': 'dzialalnosc', 'code': 'EDG-1', 'online': True},
                {'name': 'Deklaracja podatkowa od nieruchomości', 'category': 'podatki', 'code': 'DN-1', 'online': True},
                {'name': 'Informacja o nieruchomościach i obiektach budowlanych', 'category': 'podatki', 'code': 'IN-1', 'online': True},
                {'name': 'Wniosek o zwrot podatku akcyzowego', 'category': 'podatki', 'code': 'PA-1', 'online': False},
                {'name': 'Wniosek o wydanie zaświadczenia o niezaleganiu', 'category': 'podatki', 'code': 'ZN-1', 'online': True},
                {'name': 'Zgłoszenie szkody drogowej', 'category': 'drogi', 'code': 'SD-1', 'online': True},
                {'name': 'Wniosek o zajęcie pasa drogowego', 'category': 'drogi', 'code': 'ZPD-1', 'online': False},
                {'name': 'Wniosek o wydanie dowodu osobistego', 'category': 'usc', 'code': 'DO-1', 'online': True},
                {'name': 'Zgłoszenie urodzenia dziecka', 'category': 'usc', 'code': 'UD-1', 'online': False},
                {'name': 'Wniosek o sporządzenie aktu małżeństwa', 'category': 'usc', 'code': 'AM-1', 'online': False},
                {'name': 'Wniosek o przyznanie dodatku mieszkaniowego', 'category': 'pomoc', 'code': 'DM-1', 'online': True},
                {'name': 'Wniosek o przyznanie zasiłku rodzinnego', 'category': 'pomoc', 'code': 'ZR-1', 'online': True},
                {'name': 'Wniosek o wydanie Karty Dużej Rodziny', 'category': 'pomoc', 'code': 'KDR-1', 'online': True},
                {'name': 'Wniosek o dotację na wymianę pieca', 'category': 'srodowisko', 'code': 'WP-1', 'online': True},
                {'name': 'Zgłoszenie imprez masowej', 'category': 'kultura', 'code': 'IM-1', 'online': False},
                {'name': 'Wniosek o udostępnienie informacji publicznej', 'category': 'inne', 'code': 'IP-1', 'online': True},
                {'name': 'Skarga na działalność organu gminy', 'category': 'inne', 'code': 'SK-1', 'online': True}
            ],
            'problems': [
                'Dziura w drodze',
                'Nieodebrane śmieci',
                'Awaria oświetlenia ulicznego',
                'Przepełniony kontener na odpady',
                'Uszkodzony chodnik',
                'Nielegalne wysypisko śmieci',
                'Hałas z budowy',
                'Zanieczyszczenie środowiska',
                'Problem z kanalizacją',
                'Uszkodzone oznakowanie drogowe',
                'Wyciek wody',
                'Niebezpieczne drzewo',
                'Dewastacja mienia publicznego',
                'Bezpańskie zwierzęta',
                'Zła organizacja ruchu',
                'Brak koszy na śmieci',
                'Uszkodzona wiata przystankowa',
                'Zalane tereny po deszczu',
                'Graffiti na budynkach',
                'Niedziałający hydrant',
                'Zarośnięte pobocze drogi',
                'Uszkodzone barierki ochronne',
                'Brak przejścia dla pieszych',
                'Niebezpieczny plac zabaw',
                'Zapchana studzienka kanalizacyjna'
            ]
        }

    def initialize_data(self):
        """Inicjalizuje dane gminy z rozszerzoną bazą"""
        self.gmina_data = {
            'Przykładowa Gmina': {
                'basic_info': {
                    'name': 'Urząd Gminy Przykładowa',
                    'address': 'ul. Główna 1, 00-001 Przykładowa',
                    'phone': '+48 123 456 789',
                    'email': 'kontakt@przykladowa.pl',
                    'nip': '1234567890',
                    'regon': '123456789',
                    'bip': 'https://bip.przykladowa.pl',
                    'epuap': '/ugprzykladowa/skrytka'
                },
                'departments': self.search_database['contacts']['departments'],
                'forms': self.search_database['forms']
            },
            'Demo Gmina': {
                'basic_info': {
                    'name': 'Urząd Gminy Demo',
                    'address': 'ul. Testowa 5, 00-002 Demo',
                    'phone': '+48 987 654 321',
                    'email': 'kontakt@demo.pl',
                    'nip': '9876543210',
                    'regon': '987654321',
                    'bip': 'https://bip.demo.pl',
                    'epuap': '/ugdemo/skrytka'
                },
                'departments': self.search_database['contacts']['departments'],
                'forms': self.search_database['forms']
            }
        }

    def set_gmina_context(self, context):
        """Ustawia kontekst gminy w sesji"""
        try:
            gmina_name = context.get('gmina')
            
            if not gmina_name:
                return False

            # Tworzenie pełnych danych dla nowej gminy
            if gmina_name not in self.gmina_data:
                self.gmina_data[gmina_name] = {
                    'basic_info': {
                        'name': f'Urząd Gminy {gmina_name}',
                        'address': f'ul. Główna 1, {gmina_name}',
                        'phone': '+48 123 456 789',
                        'email': f'kontakt@{gmina_name.lower().replace(" ", "")}.pl',
                        'nip': '1234567890',
                        'regon': '123456789',
                        'bip': f'https://bip.{gmina_name.lower().replace(" ", "")}.pl',
                        'epuap': f'/ug{gmina_name.lower().replace(" ", "")}/skrytka'
                    },
                    'departments': self.search_database['contacts']['departments'],
                    'forms': self.search_database['forms']
                }

            session['gmina_context'] = context
            session['chat_history'] = []
            session['current_path'] = 'start'
            session['input_context'] = None
            session['search_mode'] = False
            session.permanent = True
            session.modified = True

            return True

        except Exception as e:
            print(f"[ERROR] Błąd podczas ustawiania kontekstu: {e}")
            return False

    def get_initial_greeting(self):
        """Zwraca powitanie z menu głównym"""
        if 'gmina_context' not in session:
            return {'text_message': 'Error: Kontekst gminy nie został ustawiony.'}

        gmina_name = session['gmina_context']['gmina']
        greeting_text = f"""🤖 Witaj! Jestem **Adept**, Twój inteligentny asystent.
        
Obsługuję sprawy gminy **{gmina_name}** z wykorzystaniem zaawansowanego wyszukiwania predykcyjnego.

Wybierz jedną z opcji lub zacznij pisać, aby skorzystać z inteligentnego wyszukiwania:"""

        return {
            'text_message': greeting_text,
            'buttons': [
                {'text': '🔍 Znajdź Kontakt', 'action': 'znajdz_kontakt'},
                {'text': '📋 Pobierz Formularz', 'action': 'pobierz_formularz'},
                {'text': '⚠️ Zgłoś Problem', 'action': 'zglos_problem'},
                {'text': '↩️ Menu główne', 'action': 'main_menu'}
            ]
        }
    
        

    def handle_button_action(self, action):
        """Obsługuje akcje przycisków z aktywacją trybu wyszukiwania"""
        if 'gmina_context' not in session:
            return {
                'text_message': 'Sesja wygasła. Proszę wybrać gminę ponownie.',
                'buttons': [{'text': 'Powrót do wyboru gminy', 'action': 'restart'}]
            }

        session['current_path'] = action
        session['search_mode'] = False
        session.modified = True

        # Główne akcje z aktywacją wyszukiwania
        if action == 'znajdz_kontakt':
            return self._handle_znajdz_kontakt_enterprise()
        elif action == 'pobierz_formularz':
            return self._handle_pobierz_formularz_enterprise()
        elif action == 'zglos_problem':
            return self._handle_zglos_problem_enterprise()
        elif action == 'sprawdz_gmine':
            return self._handle_sprawdz_gmine()
        elif action == 'main_menu':
            return self.get_initial_greeting()
        else:
            return self._handle_default_action(action)

    def _handle_znajdz_kontakt_enterprise(self):
        """Obsługa kontaktów z wyszukiwaniem predykcyjnym"""
        session['search_mode'] = True
        session['search_context'] = 'contacts'
        session.modified = True
        
        return {
            'text_message': """🔍 **Wyszukiwarka Kontaktów - Tryb Inteligentny**

Zacznij wpisywać:
• Imię i nazwisko osoby (np. "Jan Kowalski")
• Nazwę wydziału (np. "Referat Finansowy")
• Stanowisko (np. "Skarbnik")
• Tematykę sprawy (np. "podatki", "śmieci")

System automatycznie podpowie najlepsze wyniki.""",
            'enable_search': True,
            'search_placeholder': 'Wpisz nazwisko, wydział lub temat sprawy...',
            'search_context': 'contacts',
            'quick_buttons': [
                {'text': '📞 Sekretariat', 'action': 'quick_sekretariat'},
                {'text': '💰 Sprawy Finansowe', 'action': 'quick_finanse'},
                {'text': '🏗️ Budownictwo', 'action': 'quick_budownictwo'},
                {'text': '↩️ Menu główne', 'action': 'main_menu'}
            ]
        }

    def _handle_pobierz_formularz_enterprise(self):
        """Obsługa formularzy z wyszukiwaniem predykcyjnym"""
        session['search_mode'] = True
        session['search_context'] = 'forms'
        session.modified = True
        
        return {
            'text_message': """📋 **Inteligentna Wyszukiwarka Formularzy**

Wpisz czego szukasz:
• Nazwę formularza (np. "pozwolenie na budowę")
• Kategorię (np. "podatki", "środowisko")
• Kod formularza (np. "PB-1", "DO-1")

✅ Formularze oznaczone zieloną kropką są dostępne online.""",
            'enable_search': True,
            'search_placeholder': 'Szukaj formularza po nazwie, kategorii lub kodzie...',
            'search_context': 'forms',
            'quick_buttons': [
                {'text': '🗑️ Odpady', 'action': 'quick_form_odpady'},
                {'text': '🏠 Budownictwo', 'action': 'quick_form_budownictwo'},
                {'text': '🌳 Środowisko', 'action': 'quick_form_srodowisko'},
                {'text': '↩️ Menu główne', 'action': 'main_menu'}
            ]
        }

    def _handle_zglos_problem_enterprise(self):
        """Obsługa zgłoszeń z możliwością wpisania własnego problemu"""
        session['search_mode'] = True
        session['search_context'] = 'problems'
        session.modified = True
        
        return {
            'text_message': """⚠️ **System Zgłaszania Problemów**

Opisz swój problem:
• Możesz wybrać z listy sugestii
• Lub wpisać własny, szczegółowy opis
• System automatycznie kategoryzuje zgłoszenie

Przykłady: "dziura na ul. Głównej", "nieodebrane śmieci", "awaria oświetlenia" """,
            'enable_search': True,
            'search_placeholder': 'Opisz problem (lokalizacja, rodzaj usterki)...',
            'search_context': 'problems',
            'allow_custom': True,
            'quick_buttons': [
                {'text': '🚧 Drogi', 'action': 'quick_problem_drogi'},
                {'text': '💡 Oświetlenie', 'action': 'quick_problem_oswietlenie'},
                {'text': '🗑️ Odpady', 'action': 'quick_problem_odpady'},
                {'text': '↩️ Menu główne', 'action': 'main_menu'}
            ]
        }

    def calculate_match_score(self, query, text):
        """Oblicza wynik dopasowania używając fuzzy matching"""
        # Konwersja do lowercase dla porównania
        query_lower = query.lower().strip()
        text_lower = text.lower()
        
        # Różne typy dopasowania z wagami
        ratio = fuzz.ratio(query_lower, text_lower)  # Podstawowe podobieństwo
        partial_ratio = fuzz.partial_ratio(query_lower, text_lower)  # Częściowe dopasowanie
        token_sort = fuzz.token_sort_ratio(query_lower, text_lower)  # Sortowanie tokenów
        token_set = fuzz.token_set_ratio(query_lower, text_lower)  # Zbiór tokenów
        
        # Weighted average z preferencją dla partial_ratio (najlepsze dla wyszukiwania)
        weighted_score = (
            ratio * 0.2 +
            partial_ratio * 0.4 +
            token_sort * 0.2 +
            token_set * 0.2
        )
        
        return int(weighted_score)

    def search_suggestions(self, query, context):
        """Generuje sugestie dla wyszukiwania predykcyjnego z fuzzy matching"""
        query = query.lower().strip()
        suggestions = []
        
        if not query or len(query) < 2:
            return []
        
        if context == 'contacts':
            # Szukanie w osobach
            for person in self.search_database['contacts']['persons']:
                # Łączymy wszystkie pola do przeszukiwania
                searchable_text = f"{person['name']} {person['position']} {person['department']}"
                score = self.calculate_match_score(query, searchable_text)
                
                if score > 40:  # Próg minimalnego dopasowania
                    suggestions.append({
                        'type': 'person',
                        'icon': '👤',
                        'title': person['name'],
                        'subtitle': f"{person['position']} - {person['department']}",
                        'details': f"📞 {person['phone']} | ✉️ {person['email']}",
                        'data': person,
                        'score': score
                    })
            
            # Szukanie w wydziałach
            for dept in self.search_database['contacts']['departments']:
                score = self.calculate_match_score(query, dept['name'])
                
                if score > 40:
                    suggestions.append({
                        'type': 'department',
                        'icon': '🏢',
                        'title': dept['name'],
                        'subtitle': dept['hours'],
                        'details': f"📞 {dept['phone']} | ✉️ {dept['email']}",
                        'data': dept,
                        'score': score
                    })
        
        elif context == 'forms':
            # Szukanie w formularzach
            for form in self.search_database['forms']:
                searchable_text = f"{form['name']} {form['category']} {form['code']}"
                score = self.calculate_match_score(query, searchable_text)
                
                if score > 40:
                    status_icon = '✅' if form['online'] else '📄'
                    suggestions.append({
                        'type': 'form',
                        'icon': status_icon,
                        'title': form['name'],
                        'subtitle': f"Kod: {form['code']} | Kategoria: {form['category']}",
                        'details': 'Dostępny online' if form['online'] else 'Wymaga wizyty w urzędzie',
                        'data': form,
                        'score': score
                    })
        
        elif context == 'problems':
            # Szukanie w typowych problemach
            for problem in self.search_database['problems']:
                score = self.calculate_match_score(query, problem)
                
                if score > 40:
                    suggestions.append({
                        'type': 'problem',
                        'icon': '⚠️',
                        'title': problem,
                        'subtitle': 'Kliknij aby zgłosić',
                        'details': 'Zgłoszenie zostanie automatycznie skategoryzowane',
                        'data': {'problem': problem},
                        'score': score
                    })
        
        # KLUCZOWE: Sortowanie według score malejąco (najlepsze dopasowanie na górze)
        suggestions.sort(key=lambda x: x['score'], reverse=True)
        
        # Ograniczenie do 8 sugestii
        return suggestions[:8]

    def process_search_selection(self, selection_data):
        """Przetwarza wybór z listy sugestii"""
        selection_type = selection_data.get('type')
        data = selection_data.get('data')
        
        if selection_type == 'person':
            return {
                'text_message': f"""✅ **Znaleziono kontakt:**

👤 **{data['name']}**
📋 {data['position']}
🏢 {data['department']}

📞 Telefon: {data['phone']}
✉️ Email: {data['email']}

💡 Możesz również skontaktować się przez ePUAP lub odwiedzić urząd osobiście.""",
                'buttons': [
                    {'text': '🔍 Szukaj innej osoby', 'action': 'znajdz_kontakt'},
                    {'text': '📞 Kontakt do sekretariatu', 'action': 'quick_sekretariat'},
                    {'text': '↩️ Menu główne', 'action': 'main_menu'}
                ]
            }
        
        elif selection_type == 'department':
            return {
                'text_message': f"""✅ **Informacje o wydziale:**

🏢 **{data['name']}**
⏰ Godziny pracy: {data['hours']}

📞 Telefon: {data['phone']}
✉️ Email: {data['email']}

💡 W sprawach pilnych możesz również skorzystać z ePUAP.""",
                'buttons': [
                    {'text': '🔍 Szukaj innego wydziału', 'action': 'znajdz_kontakt'},
                    {'text': '↩️ Menu główne', 'action': 'main_menu'}
                ]
            }
        
        elif selection_type == 'form':
            online_info = "🌐 **Formularz dostępny online!** Możesz go wypełnić przez ePUAP." if data['online'] else "📍 **Formularz wymaga wizyty w urzędzie.**"
            
            return {
                'text_message': f"""✅ **Formularz znaleziony:**

📋 **{data['name']}**
🔖 Kod: {data['code']}
📁 Kategoria: {data['category'].title()}

{online_info}

🔗 Link do pobrania: https://gmina.pl/formularze/{data['code']}.pdf

💡 **Wskazówka:** Przed złożeniem upewnij się, że masz wszystkie wymagane załączniki.""",
                'buttons': [
                    {'text': '📥 Pobierz formularz', 'action': f'download_{data["code"]}'},
                    {'text': '🔍 Szukaj innego formularza', 'action': 'pobierz_formularz'},
                    {'text': '↩️ Menu główne', 'action': 'main_menu'}
                ]
            }
        
        elif selection_type == 'problem':
            problem_id = f"ZGL-{random.randint(10000, 99999)}"
            return {
                'text_message': f"""✅ **Zgłoszenie przyjęte!**

📝 **Problem:** {data['problem']}
🔖 **Numer zgłoszenia:** {problem_id}
📅 **Data:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

⏱️ **Przewidywany czas realizacji:** 3-5 dni roboczych

📧 Potwierdzenie zostało wysłane na adres email przypisany do Twojego konta.

💡 **Co dalej?**
• Możesz śledzić status zgłoszenia pod numerem {problem_id}
• W przypadku pytań kontakt: 📞 +48 123 456 799""",
                'buttons': [
                    {'text': '➕ Zgłoś kolejny problem', 'action': 'zglos_problem'},
                    {'text': '📊 Sprawdź status zgłoszenia', 'action': 'status_zgloszenia'},
                    {'text': '↩️ Menu główne', 'action': 'main_menu'}
                ]
            }
        
        return {
            'text_message': 'Wybrano element z listy.',
            'buttons': [{'text': '↩️ Menu główne', 'action': 'main_menu'}]
        }

    def process_custom_problem(self, problem_description):
        """Przetwarza niestandardowe zgłoszenie problemu"""
        problem_id = f"ZGL-{random.randint(10000, 99999)}"
        
        # Analiza tekstu do kategoryzacji
        category = "Inne"
        if any(word in problem_description.lower() for word in ['droga', 'dziura', 'chodnik', 'asfalt', 'jezdnia']):
            category = "Infrastruktura drogowa"
        elif any(word in problem_description.lower() for word in ['śmieci', 'odpady', 'kontener', 'kosz', 'wywóz']):
            category = "Gospodarka odpadami"
        elif any(word in problem_description.lower() for word in ['lampa', 'oświetlenie', 'światło', 'latarnia']):
            category = "Oświetlenie"
        elif any(word in problem_description.lower() for word in ['woda', 'kanalizacja', 'wyciek', 'rura', 'studzienka']):
            category = "Wodno-kanalizacyjne"
        elif any(word in problem_description.lower() for word in ['drzewo', 'gałęzie', 'krzew', 'zieleń', 'trawnik']):
            category = "Zieleń miejska"
        
        return {
            'text_message': f"""✅ **Zgłoszenie przyjęte!**

📝 **Twój opis problemu:** 
_{problem_description}_

🏷️ **Automatyczna kategoryzacja:** {category}
🔖 **Numer zgłoszenia:** {problem_id}
📅 **Data:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

⏱️ **Przewidywany czas realizacji:** 
• Problemy krytyczne: 24-48h
• Standardowe naprawy: 3-5 dni roboczych
• Prace planowe: 7-14 dni

📧 **Co dalej?**
• Potwierdzenie wysłano na email
• SMS gdy inspektor przejmie sprawę
• Powiadomienie o zakończeniu

💡 **Status możesz sprawdzić:**
• Online: gmina.pl/status/{problem_id}
• SMS: STAN {problem_id} na nr 799-123-456
• Telefon: +48 123 456 799""",
            'buttons': [
                {'text': '➕ Zgłoś kolejny problem', 'action': 'zglos_problem'},
                {'text': '📊 Sprawdź status', 'action': 'status_zgloszenia'},
                {'text': '📸 Dodaj zdjęcie', 'action': 'add_photo'},
                {'text': '↩️ Menu główne', 'action': 'main_menu'}
            ],
            'enable_search': False  # Ważne - wyłącza tryb wyszukiwania
        }

    def _handle_sprawdz_gmine(self):
        """Sprawdzanie gminy z inteligentnym wyszukiwaniem"""
        session['search_mode'] = True
        session['search_context'] = 'gmina_check'
        session.modified = True
        
        return {
            'text_message': """🏛️ **Weryfikacja Gminy - System Centralny**

Wpisz nazwę gminy, którą chcesz zweryfikować. System przeszuka:
• Centralną Ewidencję Gmin
• Bazę TERYT GUS
• Rejestr JST

Możesz wpisać pełną nazwę lub jej fragment.""",
            'enable_search': True,
            'search_placeholder': 'Wpisz nazwę gminy (np. Warszawa, Kraków)...',
            'search_context': 'gmina_check',
            'quick_buttons': [
                {'text': '🏛️ Gminy wojewódzkie', 'action': 'gminy_wojewodzkie'},
                {'text': '↩️ Menu główne', 'action': 'main_menu'}
            ]
        }

    def _handle_default_action(self, action):
        """Obsługa domyślnych akcji"""
        # Quick actions dla kontaktów
        if action == 'quick_sekretariat':
            return {
                'text_message': """📞 **Sekretariat Urzędu Gminy**

🏢 Sekretariat - pierwszy kontakt
⏰ Godziny pracy: Pon-Pt: 7:30-15:30

📞 Telefon: +48 123 456 700
✉️ Email: sekretariat@gmina.pl
📠 Fax: +48 123 456 701

💡 Sekretariat pomoże w przekierowaniu do właściwego wydziału.""",
                'buttons': [
                    {'text': '🔍 Znajdź inny kontakt', 'action': 'znajdz_kontakt'},
                    {'text': '↩️ Menu główne', 'action': 'main_menu'}
                ]
            }
        
        elif action == 'quick_finanse':
            return {
                'text_message': """💰 **Referat Finansowy**

Zakres spraw:
• Podatki lokalne
• Opłaty za gospodarowanie odpadami
• Windykacja należności
• Zaświadczenia o niezaleganiu

📞 Telefon: +48 123 456 720
✉️ Email: finanse@gmina.pl
⏰ Godziny: Pon-Pt: 8:00-16:00

🏦 Kasa urzędu: Pon-Pt: 8:00-14:00""",
                'buttons': [
                    {'text': '📋 Formularze podatkowe', 'action': 'quick_form_podatki'},
                    {'text': '🔍 Znajdź inny kontakt', 'action': 'znajdz_kontakt'},
                    {'text': '↩️ Menu główne', 'action': 'main_menu'}
                ]
            }
        
        elif action == 'quick_budownictwo':
            return {
                'text_message': """🏗️ **Referat Architektury i Budownictwa**

📋 **Najczęstsze sprawy:**
• Pozwolenia na budowę
• Zgłoszenia robót budowlanych
• Wypisy z planu zagospodarowania
• Warunki zabudowy

📞 Telefon: +48 123 456 730
✉️ Email: architektura@gmina.pl
⏰ Przyjęcia: Pon, Śr, Pt: 8:00-15:00

⚠️ **UWAGA:** Dokumenty składaj minimum 30 dni przed planowanym rozpoczęciem prac!""",
                'buttons': [
                    {'text': '📥 Pobierz wniosek PB-1', 'action': 'download_PB-1'},
                    {'text': '📋 Wszystkie formularze', 'action': 'pobierz_formularz'},
                    {'text': '↩️ Menu główne', 'action': 'main_menu'}
                ]
            }
        
        # Quick actions dla formularzy
        elif action == 'quick_form_odpady':
            forms = [f for f in self.search_database['forms'] if f['category'] == 'odpady']
            form_list = '\n'.join([f"• {f['name']} ({f['code']})" for f in forms])
            
            return {
                'text_message': f"""🗑️ **Formularze - Gospodarka Odpadami**

Dostępne formularze:
{form_list}

✅ Wszystkie formularze z tej kategorii są dostępne online!

💡 Pamiętaj o terminach składania deklaracji.""",
                'buttons': [
                    {'text': '📥 Pobierz deklarację DO-1', 'action': 'download_DO-1'},
                    {'text': '🔍 Szukaj innych formularzy', 'action': 'pobierz_formularz'},
                    {'text': '↩️ Menu główne', 'action': 'main_menu'}
                ]
            }
        
        elif action == 'quick_form_budownictwo':
            return {
                'text_message': """🏠 **Formularze Budowlane - TOP 3**

1️⃣ **Pozwolenie na budowę (PB-1)**
   ⚠️ Wymaga wizyty w urzędzie
   
2️⃣ **Zgłoszenie robót (ZRB-1)**
   ✅ Dostępne online przez ePUAP
   
3️⃣ **Wypis z planu (WMP-1)**
   ✅ Złóż online, odbierz za 14 dni

📞 Konsultacje: +48 123 456 730
💡 **PORADA:** Najpierw sprawdź plan zagospodarowania!""",
                'buttons': [
                    {'text': '📥 Pobierz formularze', 'action': 'pobierz_formularz'},
                    {'text': '☎️ Kontakt do wydziału', 'action': 'quick_budownictwo'},
                    {'text': '↩️ Menu główne', 'action': 'main_menu'}
                ]
            }
        
        elif action == 'quick_form_srodowisko':
            return {
                'text_message': """🌳 **Formularze Środowiskowe**

🌲 **Wycinka drzew (WD-1)**
✅ Online | Termin: 30 dni

♻️ **Dotacja na wymianę pieca (WP-1)**
✅ Online | Dofinansowanie do 5000 zł!

🍃 **Zgłoszenie zanieczyszczenia**
✅ Formularz interwencyjny 24/7

📞 Ekodoradca: +48 123 456 760
💚 Dbamy o środowisko razem!""",
                'buttons': [
                    {'text': '🌲 Wniosek o wycinkę', 'action': 'download_WD-1'},
                    {'text': '♻️ Dotacja na piec', 'action': 'download_WP-1'},
                    {'text': '↩️ Menu główne', 'action': 'main_menu'}
                ]
            }
        
        # Quick actions dla problemów
        elif action == 'quick_problem_drogi':
            return {
                'text_message': """🚧 **Zgłaszanie Problemów Drogowych**

📱 **SZYBKIE ZGŁOSZENIE:**
Wyślij SMS na numer: 799-123-456
Format: DZIURA [ulica] [nr domu]

📧 **EMAIL Z FOTO:**
drogi@gmina.pl (załącz zdjęcie!)

☎️ **TELEFON 24/7:**
+48 123 456 793 (awarie pilne)

⚡ **Średni czas naprawy:**
• Dziury: 3-5 dni
• Chodniki: 7-14 dni
• Oznakowanie: 24-48h""",
                'enable_search': True,
                'search_placeholder': 'Opisz problem (np. "dziura na Głównej 15")...',
                'search_context': 'problems',
                'buttons': [
                    {'text': '📸 Wyślij ze zdjęciem', 'action': 'send_with_photo'},
                    {'text': '🗺️ Pokaż na mapie', 'action': 'show_map'},
                    {'text': '↩️ Menu główne', 'action': 'main_menu'}
                ]
            }
        
        elif action == 'quick_problem_oswietlenie':
            return {
                'text_message': """💡 **Awarie Oświetlenia - EKSPRESOWA NAPRAWA**

🔴 **ZGŁOŚ AWARIĘ W 30 SEKUND:**

1️⃣ Wyślij SMS: 799-456-789
2️⃣ Wpisz: LAMPA [ulica] [nr słupa]
3️⃣ Otrzymasz SMS z nr zgłoszenia

⚡ **Czas reakcji:**
• Pojedyncza lampa: 24h
• Cała ulica: 2-4h
• Skrzyżowanie: NATYCHMIAST

🔧 Ekipa dyżurna 24/7/365
📞 Dyspozytor: +48 123 456 799""",
                'enable_search': True,
                'search_placeholder': 'Podaj lokalizację awarii (ulica, nr słupa)...',
                'search_context': 'problems',
                'buttons': [
                    {'text': '🆘 Zgłoś pilną awarię', 'action': 'urgent_lighting'},
                    {'text': '📱 Status napraw', 'action': 'repair_status'},
                    {'text': '↩️ Menu główne', 'action': 'main_menu'}
                ]
            }
        
        elif action == 'quick_problem_odpady':
            return {
                'text_message': """🗑️ **Problemy z Odpadami - SZYBKA INTERWENCJA**

📅 **Harmonogram wywozu:**
• Zmieszane: PONIEDZIAŁKI
• Segregowane: ŚRODY
• BIO: PIĄTKI
• Wielkogabaryty: 1. sobota miesiąca

🚨 **ZGŁOŚ PROBLEM:**
☎️ Infolinia: 800-123-456 (bezpłatna!)
📱 SMS: ŚMIECI [adres] [problem]

⏱️ **Czas reakcji:**
• Nieodebrane: do 24h
• Przepełniony kontener: do 48h
• Dzikie wysypisko: do 72h""",
                'enable_search': True,
                'search_placeholder': 'Opisz problem ze śmieciami...',
                'search_context': 'problems',
                'buttons': [
                    {'text': '📅 Harmonogram', 'action': 'waste_schedule'},
                    {'text': '♻️ Punkty PSZOK', 'action': 'pszok_locations'},
                    {'text': '↩️ Menu główne', 'action': 'main_menu'}
                ]
            }
        
        # Status zgłoszenia
        elif action == 'status_zgloszenia':
            return {
                'text_message': """📊 **Sprawdzanie Statusu Zgłoszenia**

Aby sprawdzić status, potrzebuję numeru zgłoszenia (format: ZGL-XXXXX).

Możesz również:
• Zalogować się do ePUAP
• Zadzwonić: +48 123 456 799
• Odwiedzić urząd osobiście""",
                'enable_search': True,
                'search_placeholder': 'Wpisz numer zgłoszenia (np. ZGL-12345)...',
                'search_context': 'status_check',
                'buttons': [
                    {'text': '➕ Nowe zgłoszenie', 'action': 'zglos_problem'},
                    {'text': '↩️ Menu główne', 'action': 'main_menu'}
                ]
            }
        
        # Dodatkowe akcje dla formularzy podatkowych
        elif action == 'quick_form_podatki':
            return {
                'text_message': """💰 **Formularze Podatkowe - E-DEKLARACJE**

📊 **Najważniejsze terminy 2024:**
• Do 31.01 - Deklaracja od nieruchomości
• Do 15.02 - Podatek od środków transportu
• Do 15.03 - Podatek rolny/leśny

✅ **WSZYSTKO ONLINE przez ePUAP!**

🎯 **NOWOŚĆ:** Kalkulator podatku online!
💡 **ULGA:** 20% dla e-deklaracji!

📞 Konsultant: +48 123 456 707
💬 Czat online: pon-pt 8-16""",
                'buttons': [
                    {'text': '🧮 Kalkulator podatku', 'action': 'tax_calculator'},
                    {'text': '📥 Pobierz deklarację', 'action': 'download_DN-1'},
                    {'text': '↩️ Menu główne', 'action': 'main_menu'}
                ]
            }
        
        return {
            'text_message': 'Wybrana opcja jest już dostępna. Skorzystaj z wyszukiwania lub wybierz inną opcję.',
            'buttons': [{'text': '↩️ Menu główne', 'action': 'main_menu'}]
        }

    def get_bot_response(self, user_message):
        """Przetwarza wiadomość tekstową użytkownika"""
        if 'gmina_context' not in session:
            return {'text_message': 'Proszę najpierw wybrać gminę.'}
        
        # Sprawdzenie kontekstu wyszukiwania
        search_context = session.get('search_context', '')
        
        if search_context == 'gmina_check':
            return self._process_gmina_verification(user_message)
        elif search_context == 'status_check':
            return self._process_status_check(user_message)
        elif search_context in ['contacts', 'forms', 'problems']:
            # Dla problemów - sprawdzenie czy to custom input
            if search_context == 'problems' and len(user_message) > 20:
                return self.process_custom_problem(user_message)
            
            # Standardowe wyszukiwanie
            suggestions = self.search_suggestions(user_message, search_context)
            if suggestions:
                return {
                    'text_message': f'Znaleziono {len(suggestions)} wyników dla "{user_message}".',
                    'suggestions': suggestions
                }
            else:
                return {
                    'text_message': f'Brak wyników dla "{user_message}". Spróbuj innych słów kluczowych.',
                    'enable_search': True,
                    'search_context': search_context
                }
        
        # Domyślna inteligentna odpowiedź
        return self._process_smart_intent(user_message)

    def _process_gmina_verification(self, gmina_name):
        """Weryfikacja gminy"""
        gmina_name = gmina_name.strip()
        
        # Symulacja weryfikacji w bazie
        known_gminas = [
            {'name': 'Warszawa', 'type': 'miasto stołeczne', 'voivodeship': 'mazowieckie'},
            {'name': 'Kraków', 'type': 'miasto na prawach powiatu', 'voivodeship': 'małopolskie'},
            {'name': 'Gdańsk', 'type': 'miasto na prawach powiatu', 'voivodeship': 'pomorskie'},
            {'name': 'Wrocław', 'type': 'miasto na prawach powiatu', 'voivodeship': 'dolnośląskie'},
            {'name': 'Poznań', 'type': 'miasto na prawach powiatu', 'voivodeship': 'wielkopolskie'},
            {'name': 'Gorzów Wielkopolski', 'type': 'miasto na prawach powiatu', 'voivodeship': 'lubuskie'},
        ]
        
        found = None
        for gmina in known_gminas:
            if gmina_name.lower() in gmina['name'].lower():
                found = gmina
                break
        
        if found:
            return {
                'text_message': f"""✅ **Gmina zweryfikowana pomyślnie!**

🏛️ **{found['name']}**
📍 Typ: {found['type'].title()}
🗺️ Województwo: {found['voivodeship'].title()}

📊 **Dane z Centralnej Ewidencji:**
• Status: Aktywna
• Kod TERYT: {random.randint(100000, 999999)}
• Liczba mieszkańców: {random.randint(10000, 500000):,}
• Powierzchnia: {random.randint(50, 500)} km²

🔗 Więcej informacji: https://stat.gov.pl/teryt/""",
                'buttons': [
                    {'text': '🔍 Sprawdź inną gminę', 'action': 'sprawdz_gmine'},
                    {'text': '↩️ Menu główne', 'action': 'main_menu'}
                ]
            }
        else:
            return {
                'text_message': f"""⚠️ **Nie znaleziono gminy "{gmina_name}"**

Sprawdź pisownię lub spróbuj:
• Wpisać pełną nazwę gminy
• Użyć nazwy bez polskich znaków
• Sprawdzić w bazie TERYT

💡 Możesz też skontaktować się z GUS.""",
                'buttons': [
                    {'text': '🔍 Spróbuj ponownie', 'action': 'sprawdz_gmine'},
                    {'text': '↩️ Menu główne', 'action': 'main_menu'}
                ]
            }

    def _process_status_check(self, ticket_number):
        """Sprawdzanie statusu zgłoszenia"""
        if ticket_number.upper().startswith('ZGL-'):
            statuses = ['W trakcie analizy', 'Przekazano do realizacji', 'W toku', 'Częściowo zrealizowane']
            status = random.choice(statuses)
            progress = random.randint(20, 80)
            
            return {
                'text_message': f"""📊 **Status zgłoszenia {ticket_number.upper()}**

🔄 **Status:** {status}
📈 **Postęp:** {progress}%
👷 **Przydzielony do:** Zespół Infrastruktury
📅 **Ostatnia aktualizacja:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

📝 **Historia:**
• {(datetime.now()).strftime('%Y-%m-%d')} - Zgłoszenie przyjęte
• {(datetime.now()).strftime('%Y-%m-%d')} - Przekazano do wydziału
• {(datetime.now()).strftime('%Y-%m-%d')} - Inspekcja terenowa

⏳ **Przewidywane zakończenie:** 2-3 dni robocze""",
                'buttons': [
                    {'text': '🔄 Odśwież status', 'action': 'status_zgloszenia'},
                    {'text': '➕ Nowe zgłoszenie', 'action': 'zglos_problem'},
                    {'text': '↩️ Menu główne', 'action': 'main_menu'}
                ]
            }
        else:
            return {
                'text_message': f"""❌ **Nieprawidłowy format numeru zgłoszenia**

Podany numer: {ticket_number}

Prawidłowy format: ZGL-XXXXX (np. ZGL-12345)

Sprawdź numer w emailu potwierdzającym zgłoszenie.""",
                'buttons': [
                    {'text': '🔍 Spróbuj ponownie', 'action': 'status_zgloszenia'},
                    {'text': '↩️ Menu główne', 'action': 'main_menu'}
                ]
            }

    # Końcówka pliku gmina_bot.py powinna wyglądać tak:

    def _process_smart_intent(self, message):
        """Inteligentne rozpoznawanie intencji"""
        message_lower = message.lower()
        
        # Rozpoznawanie intencji
        if any(word in message_lower for word in ['kontakt', 'telefon', 'email', 'numer']):
            return self._handle_znajdz_kontakt_enterprise()
        elif any(word in message_lower for word in ['formularz', 'wniosek', 'dokument', 'pobierz']):
            return self._handle_pobierz_formularz_enterprise()
        elif any(word in message_lower for word in ['problem', 'zgłoś', 'zgłoszenie', 'awaria']):
            return self._handle_zglos_problem_enterprise()
        elif any(word in message_lower for word in ['gmina', 'sprawdź', 'weryfikuj']):
            return self._handle_sprawdz_gmine()
        
        # Domyślna odpowiedź z sugestią
        return {
            'text_message': f"""🤔 Otrzymałem: "{message}"

Nie jestem pewien, czego szukasz. Wybierz jedną z opcji poniżej lub sprecyzuj swoje pytanie.""",
            'buttons': [
                {'text': '🔍 Znajdź Kontakt', 'action': 'znajdz_kontakt'},
                {'text': '📋 Pobierz Formularz', 'action': 'pobierz_formularz'},
                {'text': '⚠️ Zgłoś Problem', 'action': 'zglos_problem'},
                {'text': '↩️ Menu główne', 'action': 'main_menu'}
            ]
        }
    
    def send_ga4_no_results_event(self, query, search_type):
        """Wysyła event do GA4 Measurement Protocol gdy nie ma wyników"""
        try:
            # Placeholder dla integracji z GA4
            # W produkcji należy dodać właściwy endpoint i measurement_id
            print(f"[GA4 Event] No results for query: '{query}' in {search_type}")
            return True
        except Exception as e:
            print(f"[GA4 Error] Failed to send event: {e}")
            return False
        
    

# KONIEC KLASY GminaBot - nie powinno być tu żadnych dodatkowych znaków