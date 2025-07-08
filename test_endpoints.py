import requests

BASE = 'http://127.0.0.1:8080'
API = 'http://127.0.0.1:8081/api'

# Тестові page_code (замінити на існуючі у вашій БД)
TEST_PAGE = '1-14'

endpoints = [
    ('Головна', f'{BASE}/'),
    ('З page', f'{BASE}/?page={TEST_PAGE}'),
    ('event_links', f'{API}/event_links?page={TEST_PAGE}'),
    ('user_id_by_page_code', f'{API}/user_id_by_page_code?page={TEST_PAGE}'),
    ('event_links (no page)', f'{API}/event_links'),
    ('user_id_by_page_code (no page)', f'{API}/user_id_by_page_code'),
    ('check_wrong_card', f'{BASE}/check_wrong_card?ip=8.8.8.8'),
    ('check_code_redirect', f'{BASE}/check_code_redirect?ip=8.8.8.8'),
]

for name, url in endpoints:
    print(f'--- {name} ---')
    try:
        r = requests.get(url, timeout=5)
        print(f'URL: {url}')
        print(f'Status: {r.status_code}')
        print(f'Content: {r.text[:300]}')
    except Exception as e:
        print(f'Error: {e}')
    print('') 