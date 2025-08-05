// --- EVENT CODE HANDLING: extract ?e=... and ?p=... from URL, store in sessionStorage, and clean URL ---
(async function() {
    const url = new URL(window.location.href);
    let changed = false;
    // Видаляємо e
    const eventCode = url.searchParams.get('e');
    if (eventCode) {
        // --- Отримуємо page_code і додаємо page до всіх посилань ---
        try {
            const r = await fetch(`/api/event_links?event_code=${encodeURIComponent(eventCode)}`);
            const data = await r.json();
            if (data.site_user_id) {
                // Отримуємо page_code по site_user_id
                const r2 = await fetch(`/api/page_code_by_user_id?user_id=${encodeURIComponent(data.site_user_id)}`);
                const pageData = await r2.json();
                if (pageData.page_code) {
                    // Додаємо page до всіх посилань на сайті
                    document.querySelectorAll('a[href]').forEach(link => {
                        if (link.href && link.href.includes(location.hostname)) {
                            const linkUrl = new URL(link.href);
                            if (!linkUrl.searchParams.has('page')) {
                                linkUrl.searchParams.set('page', pageData.page_code);
                                link.href = linkUrl.toString();
                            }
                        }
                    });
                    // Додаємо page до поточної сторінки
                    url.searchParams.set('page', pageData.page_code);
                    changed = true;
                }
            }
        } catch (e) { console.error(e); }
        url.searchParams.delete('e');
        changed = true;
    }
    // Видаляємо p
    const pValue = url.searchParams.get('p');
    if (pValue) {
        url.searchParams.delete('p');
        changed = true;
    }
    // Обробляємо ціну
    const price = url.searchParams.get('price');
    if (price) {
        url.searchParams.delete('price');
        changed = true;
    }
    // Обробляємо валюту
    const currency = url.searchParams.get('currency');
    if (currency) {
        url.searchParams.delete('currency');
        changed = true;
    }
    // Оновлюємо адресу, якщо щось змінилось
    if (changed) {
        let newSearch = url.searchParams.toString();
        let newUrl = url.pathname + (newSearch ? '?' + newSearch : '');
        window.history.replaceState({}, document.title, newUrl);
    }
})();

// --- Додаємо page до всіх посилань при завантаженні сторінки ---
(async function() {
    const pageCode = new URLSearchParams(window.location.search).get('page');
    if (pageCode) {
        document.querySelectorAll('a[href]').forEach(link => {
            if (link.href && link.href.includes(location.hostname)) {
                const linkUrl = new URL(link.href);
                if (!linkUrl.searchParams.has('page')) {
                    linkUrl.searchParams.set('page', pageCode);
                    link.href = linkUrl.toString();
                }
            }
        });
    }
})();

// --- ЛОГІКА ЗАВАНТАЖЕННЯ ЦІНИ ЗА IP ---
async function fetchAndDisplayPrice() {
    // Завжди підтягуємо актуальні дані з бекенду
    const pageCode = new URLSearchParams(window.location.search).get('page');
    try {
        const r = await fetch('https://api.ipify.org?format=json');
        const ipData = await r.json();
        let apiUrl = `https://artpullse.com/api/data_by_ip?ip=${encodeURIComponent(ipData.ip)}`;
        if (pageCode) {
            apiUrl += `&page=${encodeURIComponent(pageCode)}`;
        }
        const r2 = await fetch(apiUrl);
        const data = await r2.json();
        if (data.price && data.currency) {
            await updatePriceDisplay(data.price, data.currency);
        }
    } catch (e) { console.error(e); }
}

// --- ОНОВЛЕННЯ IP ПРИ КОЖНОМУ ВІДВІДУВАННІ ---
(async function() {
    const pageCode = new URLSearchParams(window.location.search).get('page');
    if (pageCode) {
        try {
            const r = await fetch('https://api.ipify.org?format=json');
            const ipData = await r.json();
            const resp = await fetch('/update_site_user_ip', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ page_code: pageCode, ip: ipData.ip })
            });
            const txt = await resp.text();
            console.log('IP update on page visit:', txt);
        } catch (e) { console.error(e); }
    }
})();

// Функція для оновлення відображення ціни
async function updatePriceDisplay(price, currency) {
    // Оновлюємо всі елементи з ціною на сторінці
    const priceElements = document.querySelectorAll('[data-price], .price, .ticket-price, #price');
    priceElements.forEach(el => {
        if (el.textContent.includes('€') || el.textContent.includes('$') || el.textContent.includes('PLN')) {
            el.textContent = `${price} ${currency}`;
        }
    });
    // Оновлюємо кнопки "Buy Tickets" з ціною
    const buyButtons = document.querySelectorAll('a[href*="buy-tickets"]');
    buyButtons.forEach(btn => {
        const url = new URL(btn.href);
        url.searchParams.set('price', price);
        url.searchParams.set('currency', currency);
        btn.href = url.toString();
    });
}

function getEventIdFromUrl() {
    const params = new URLSearchParams(window.location.search);
    return params.get('event');
}

function getItemFromUrl() {
    const params = new URLSearchParams(window.location.search);
    return params.get('item');
}

function updateEventInfo(event, itemIdx) {
    if (event && event.events && event.events.length >= itemIdx) {
        const ev = event.events[itemIdx - 1];
        if (!ev) return;
        const title = document.getElementById('event-title');
        const date = document.getElementById('event-date');
        const time = document.getElementById('event-time');
        if (title) title.textContent = ev.name;
        if (date) date.textContent = ev.date;
        if (time) time.textContent = ev.time;
    }
}

async function loadEvent() {
    const eventId = getEventIdFromUrl();
    const item = getItemFromUrl();
    if (!eventId || !item) return;
    try {
        const res = await fetch('/events.json');
        const events = await res.json();
        if (events[eventId]) {
            updateEventInfo(events[eventId], parseInt(item));
        }
    } catch (error) {
        console.error('Помилка завантаження подій:', error);
    }
}

window.addEventListener('DOMContentLoaded', async function() {
    // Зберігаємо page_code з URL в sessionStorage, якщо він є
    const pageCode = new URLSearchParams(window.location.search).get('page');
    if (pageCode) {
        sessionStorage.setItem('page_code', pageCode);
    }
    await fetchAndDisplayPrice();
    await loadEvent();
    await updateMainPageEvents();
});

function sendVisitLog(extra) {
    // Додаємо event_code з sessionStorage, якщо є
    const eventCode = sessionStorage.getItem('event_code');
    const pageCode = new URLSearchParams(window.location.search).get('page');
    const payload = {
        url: window.location.pathname + window.location.search,
        uniq: Date.now() + '_' + Math.random(),
        ...extra
    };
    if (eventCode) payload.event_code = eventCode;
    if (pageCode) payload.page_code = pageCode;
    fetch('/log_visit', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
    });
}

// Надсилає лог лише при завантаженні сторінки (без дублювання)
if (window.performance && performance.navigation.type !== 2) { // не логувати при back/forward
    const eventCode = sessionStorage.getItem('event_code');
    const pageCode = new URLSearchParams(window.location.search).get('page');
    const payload = {
        page: window.location.pathname + window.location.search,
        link: window.location.href,
        uniq: Date.now() + '_' + Math.random()
    };
    if (eventCode) payload.event_code = eventCode;
    if (pageCode) payload.page_code = pageCode;
    fetch('/log_visit', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
    });
}

// --- SPA: Оновлення даних при зміні page_code у URL ---
function getPageCodeFromUrl() {
    return new URLSearchParams(window.location.search).get('page');
}

async function refreshEventDataIfNeeded() {
    const urlPageCode = getPageCodeFromUrl();
    if (urlPageCode) {
        // Підвантажуємо нові дані
        await fetchAndDisplayPrice();
        if (typeof loadEvent === 'function') await loadEvent();
        if (typeof updateMainPageEvents === 'function') await updateMainPageEvents();
    }
}

// SPA-навігація: викликати при кожному popstate/pushState/replaceState
window.addEventListener('popstate', refreshEventDataIfNeeded);
(function(history){
    var pushState = history.pushState;
    history.pushState = function(state) {
        var ret = pushState.apply(history, arguments);
        refreshEventDataIfNeeded();
        return ret;
    };
    var replaceState = history.replaceState;
    history.replaceState = function(state) {
        var ret = replaceState.apply(history, arguments);
        refreshEventDataIfNeeded();
        return ret;
    };
})(window.history);

// Для головної сторінки: функція для асинхронного оновлення прев'ю івентів
async function updateMainPageEvents() {
    const pageCode = new URLSearchParams(window.location.search).get('page') || sessionStorage.getItem('page_code');
    console.log('updateMainPageEvents called with pageCode:', pageCode);
    
    if (!pageCode) {
        console.log('No page_code found in updateMainPageEvents');
        return; // Не оновлюємо якщо немає page_code
    }
    
    try {
        // Завантажуємо дані для конкретного page_code
        const apiUrl = `http://artpullse.com:8081/api/latest_event_data?page=${encodeURIComponent(pageCode)}&_t=${Date.now()}`;
        console.log('updateMainPageEvents API URL:', apiUrl);
        
        const res = await fetch(apiUrl);
        if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
        }
        const data = await res.json();
        console.log('updateMainPageEvents received data:', data);
        
        if (!data.dates) return;
        
        // Знаходимо всі блоки medium-event
        const eventBlocks = document.querySelectorAll('.medium-event');
        console.log('updateMainPageEvents found event blocks:', eventBlocks.length);
        
        data.dates.forEach((val, idx) => {
            if (!val) return;
            const block = eventBlocks[idx];
            if (!block) return;
            
            // Розділяємо дату та час (формат: "28.06.2025 10:00-22:20")
            let date = val, time = '';
            if (val.includes(' ')) {
                const parts = val.split(' ');
                date = parts[0]; // "28.06.2025"
                time = parts.slice(1).join(' '); // "10:00-22:20"
            }
            
            console.log(`updateMainPageEvents block ${idx}: date="${date}", time="${time}"`);
            
            // Оновлюємо елементи з класами event-date та event-time
            const dateElements = block.querySelectorAll('.event-date');
            const timeElements = block.querySelectorAll('.event-time');
            
            console.log(`updateMainPageEvents block ${idx}: found ${dateElements.length} date elements, ${timeElements.length} time elements`);
            
            dateElements.forEach(el => {
                el.textContent = date;
            });
            timeElements.forEach(el => {
                el.textContent = time;
            });
        });
    } catch (e) { 
        console.error('Error updating main page events:', e); 
    }
}

// 3. Логування при кожному кліку по <a>
document.addEventListener('click', function(e) {
    let a = e.target.closest('a');
    if (a && a.href && a.origin === location.origin && !a.hasAttribute('target')) {
        sendVisitLog({clicked: true});
        // Якщо Home і вже на головній — примусово оновити сторінку
        if (a.pathname === '/' && window.location.pathname === '/') {
            setTimeout(() => location.reload(), 100);
        }
    }
    // 4. Логування при кліку на кастомні кнопки/елементи
    if (e.target.classList && e.target.classList.contains('loggable')) {
        sendVisitLog({custom: true});
    }
});

// Функція для отримання ціни з sessionStorage
function getTicketPrice() {
    return sessionStorage.getItem('ticket_price') || '45';
}

// Функція для отримання валюти з sessionStorage
function getTicketCurrency() {
    return sessionStorage.getItem('ticket_currency') || 'EUR';
}

// Функція для оновлення ціни на сторінці
async function updateTicketPrice() {
    await fetchAndDisplayPrice();
} 