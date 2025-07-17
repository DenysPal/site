import json
import os
import re

# Шляхи до файлів
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EVENTS_JSON = os.path.join(BASE_DIR, 'events.json')

# Відповідність івентів до папок
EVENTS = [
    ('terroir-and-traditions', 'Terroir and Traditions'),
    ('collection-co–selection', 'Collection Co–selection'),
    ('snucie', 'Snucie'),
    ('art-that-saves-lives', 'Art that saves lives'),
    ('gotong-royong', 'Gotong Royong'),
    ('anna-konik', 'Anna Konik'),
    ('uncensored', 'Uncensored'),
    ('jacek-adamas', 'Jacek Adamas'),
]

def load_events():
    with open(EVENTS_JSON, encoding='utf-8') as f:
        return json.load(f)

def update_html(event_dir, event_data, idx):
    html_path = os.path.join(BASE_DIR, event_dir, 'index.html')
    if not os.path.exists(html_path):
        print(f"[WARN] {html_path} not found!")
        return
    with open(html_path, encoding='utf-8') as f:
        html = f.read()
    # Підставляємо дату
    date = event_data['events'][idx]['date']
    time = event_data['events'][idx]['time']
    price = event_data.get('price', '')
    currency = event_data.get('currency', '')
    # id="event-date"
    html = re.sub(r'(<span[^>]*id=["\"]event-date["\"][^>]*>)(.*?)(</span>)', rf'\1{date}\3', html, flags=re.DOTALL)
    # id="event-time"
    html = re.sub(r'(<span[^>]*id=["\"]event-time["\"][^>]*>)(.*?)(</span>)', rf'\1{time}\3', html, flags=re.DOTALL)
    # .ticket-price або id="price"
    html = re.sub(r'(<span[^>]*class=["\"][^>]*ticket-price[^>]*["\"][^>]*>)(.*?)(</span>)', rf'\1{price} {currency}\3', html, flags=re.DOTALL)
    html = re.sub(r'(<span[^>]*id=["\"][Pp]rice["\"][^>]*>)(.*?)(</span>)', rf'\1{price} {currency}\3', html, flags=re.DOTALL)
    # Якщо є <div class="medium-event-about"> з <span class="badge badge-light"><img src="/image/date.svg"><span id="event-date" class="event-date"></span></span>
    # то підставити дату і час у відповідні span
    # (але це вже покривається вище)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"[OK] Updated {html_path}")

def main():
    events = load_events()
    # events.json — це dict, ключ — event_id, value — event_data
    for event_id, event_data in events.items():
        for idx, (event_dir, event_name) in enumerate(EVENTS):
            if event_data['title'].strip().lower() == event_name.strip().lower():
                update_html(event_dir, event_data, idx)

if __name__ == '__main__':
    main() 