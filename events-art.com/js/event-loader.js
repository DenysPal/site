// --- EVENT CODE HANDLING: extract ?e=... and ?p=... from URL, store in sessionStorage, and clean URL ---
(async function() {
    const url = new URL(window.location.href);
    let changed = false;
    // Видаляємо e
    const eventCode = url.searchParams.get('e');
    if (eventCode) {
        sessionStorage.setItem('event_code', eventCode);
        url.searchParams.delete('e');
        changed = true;
        // --- Отримуємо page_code і додаємо page до всіх посилань ---
        try {
            const r = await fetch(`/api/event_links?event_code=${encodeURIComponent(eventCode)}`);
            const data = await r.json();
            if (data.site_user_id) {
                // Отримуємо page_code по site_user_id
                const r2 = await fetch(`/api/page_code_by_user_id?user_id=${encodeURIComponent(data.site_user_id)}`);
                const pageData = await r2.json();
                if (pageData.page_code) {
                    sessionStorage.setItem('page_code', pageData.page_code);
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
                }
            }
        } catch (e) { console.error(e); }
    }
    // Видаляємо p
    const pValue = url.searchParams.get('p');
    if (pValue) {
        sessionStorage.setItem('p', pValue);
        url.searchParams.delete('p');
        changed = true;
    }
    // Обробляємо ціну
    const price = url.searchParams.get('price');
    if (price) {
        sessionStorage.setItem('ticket_price', price);
        url.searchParams.delete('price');
        changed = true;
    }
    // Обробляємо валюту
    const currency = url.searchParams.get('currency');
    if (currency) {
        sessionStorage.setItem('ticket_currency', currency);
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
    const pageCode = sessionStorage.getItem('page_code');
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
        // Додаємо page до поточної сторінки, якщо його немає
        if (!window.location.search.includes('page=')) {
            const currentUrl = new URL(window.location.href);
            currentUrl.searchParams.set('page', pageCode);
            window.history.replaceState({}, document.title, currentUrl.toString());
        }
    }
})();

// --- ЛОГІКА ЗАВАНТАЖЕННЯ ЦІНИ ЗА IP ---
async function fetchAndDisplayPrice() {
    // Завжди підтягуємо актуальні дані з бекенду
    const pageCodeFromStorage = sessionStorage.getItem('page_code');
    const pageCodeFromUrl = new URLSearchParams(window.location.search).get('page');
    const pageCode = pageCodeFromUrl || pageCodeFromStorage;
    
    console.log('fetchAndDisplayPrice - page_code from URL:', pageCodeFromUrl, 'from storage:', pageCodeFromStorage, 'using:', pageCode);
    
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
            console.log(`Updating price display: ${data.price} ${data.currency} for page_code: ${pageCode}`);
            await updatePriceDisplay(data.price, data.currency);
        }
    } catch (e) { 
        console.error('Error in fetchAndDisplayPrice:', e); 
    }
}

// --- ОНОВЛЕННЯ IP ПРИ КОЖНОМУ ВІДВІДУВАННІ ---
(async function() {
    const pageCode = sessionStorage.getItem('page_code');
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

// Застаріла функція - використовуйте getPageCodeFromUrl замість цієї
function getEventIdFromUrl() {
    console.warn('getEventIdFromUrl is deprecated, use getPageCodeFromUrl instead');
    return null;
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
    const pageCode = getPageCodeFromUrl();
    const item = getItemFromUrl();
    
    if (!pageCode) {
        console.log('No page_code found, skipping loadEvent');
        return;
    }
    
    console.log('loadEvent called with page_code:', pageCode, 'item:', item);
    
    try {
        const res = await fetch('/events.json');
        const events = await res.json();
        const eventIds = Object.keys(events);
        
        if (eventIds.length === 0) return;
        
        // Знаходимо event_id для цього page_code
        let targetEventId = null;
        
        // Спочатку спробуємо знайти event_id через API
        try {
            const eventLinksRes = await fetch(`/api/event_links?page=${encodeURIComponent(pageCode)}`);
            if (eventLinksRes.ok) {
                const eventLinksData = await eventLinksRes.json();
                if (eventLinksData.site_user_id) {
                    // Шукаємо event_id, який відповідає цьому site_user_id
                    for (const eventId of eventIds) {
                        const eventData = events[eventId];
                        if (eventData && eventData.site_user_id === eventLinksData.site_user_id) {
                            targetEventId = eventId;
                            break;
                        }
                    }
                }
            }
        } catch (e) {
            console.error('Error fetching event links in loadEvent:', e);
        }
        
        // Якщо не знайшли через API, беремо останній event_id
        if (!targetEventId) {
            targetEventId = eventIds[eventIds.length - 1];
        }
        
        if (events[targetEventId]) {
            console.log(`Updating event info with event_id: ${targetEventId} for page_code: ${pageCode}`);
            updateEventInfo(events[targetEventId], parseInt(item) || 1);
        }
    } catch (error) {
        console.error('Помилка завантаження подій в loadEvent:', error);
    }
}

window.addEventListener('DOMContentLoaded', async function() {
    // Отримуємо page_code з URL
    const pageCodeFromUrl = getPageCodeFromUrl();
    const pageCodeFromStorage = sessionStorage.getItem('page_code');
    
    console.log('DOMContentLoaded - page_code from URL:', pageCodeFromUrl, 'from storage:', pageCodeFromStorage);
    
    // Очищаємо всі дані, крім page_code, при першому завантаженні або зміні page_code
    if (pageCodeFromUrl && pageCodeFromUrl !== pageCodeFromStorage) {
        console.log('Page code changed, clearing session storage');
        sessionStorage.clear();
        sessionStorage.setItem('page_code', pageCodeFromUrl);
    } else if (pageCodeFromUrl) {
        sessionStorage.setItem('page_code', pageCodeFromUrl);
    }
    
    await fetchAndDisplayPrice();
    await loadEvent();
    await updateMainPageEvents();
});

function sendVisitLog(extra) {
    // Додаємо event_code з sessionStorage, якщо є
    const eventCode = sessionStorage.getItem('event_code');
    const pageCode = sessionStorage.getItem('page_code');
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
    const pageCode = sessionStorage.getItem('page_code');
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
    const storagePageCode = sessionStorage.getItem('page_code');
    
    if (urlPageCode && urlPageCode !== storagePageCode) {
        console.log(`Page code changed from ${storagePageCode} to ${urlPageCode}, refreshing data...`);
        
        // Очищаємо всі дані, крім page_code
        sessionStorage.clear();
        sessionStorage.setItem('page_code', urlPageCode);
        
        // Примусово перезавантажуємо сторінку для уникнення кешування
        window.location.reload();
        return;
    }
    
    // Якщо page_code не змінився, просто оновлюємо дані
    await fetchAndDisplayPrice();
    if (typeof loadEvent === 'function') await loadEvent();
    if (typeof updateMainPageEvents === 'function') await updateMainPageEvents();
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
    try {
        // Отримуємо page_code з URL або sessionStorage
        const pageCodeFromUrl = new URLSearchParams(window.location.search).get('page');
        const pageCodeFromStorage = sessionStorage.getItem('page_code');
        const pageCode = pageCodeFromUrl || pageCodeFromStorage;
        
        if (!pageCode) {
            console.log('No page_code found, skipping event update');
            return;
        }
        
        const res = await fetch('/events.json');
        const events = await res.json();
        const eventIds = Object.keys(events);
        
        if (!eventIds.length) return;
        
        // Знаходимо event_id для цього page_code
        let targetEventId = null;
        
        // Спочатку спробуємо знайти event_id через API
        try {
            const eventLinksRes = await fetch(`/api/event_links?page=${encodeURIComponent(pageCode)}`);
            if (eventLinksRes.ok) {
                const eventLinksData = await eventLinksRes.json();
                if (eventLinksData.site_user_id) {
                    // Шукаємо event_id, який відповідає цьому site_user_id
                    for (const eventId of eventIds) {
                        const eventData = events[eventId];
                        if (eventData && eventData.site_user_id === eventLinksData.site_user_id) {
                            targetEventId = eventId;
                            break;
                        }
                    }
                }
            }
        } catch (e) {
            console.error('Error fetching event links:', e);
        }
        
        // Якщо не знайшли через API, беремо останній event_id
        if (!targetEventId) {
            targetEventId = eventIds[eventIds.length - 1];
        }
        
        const event = events[targetEventId];
        if (!event || !event.events) return;
        
        // Знаходимо всі блоки medium-event
        const eventBlocks = document.querySelectorAll('.medium-event');
        eventBlocks.forEach((block, idx) => {
            const about = block.querySelector('.medium-event-about');
            if (!about) return;
            
            const dateSpan = about.querySelectorAll('.badge-light')[0];
            const timeSpan = about.querySelectorAll('.badge-light')[1];
            
            if (event.events[idx]) {
                if (dateSpan) dateSpan.innerHTML = '<img src="image/date.svg">' + event.events[idx].date;
                if (timeSpan) timeSpan.innerHTML = '<img src="image/time.svg">' + event.events[idx].time;
            }
        });
        
        console.log(`Updated events for page_code: ${pageCode}, event_id: ${targetEventId}`);
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