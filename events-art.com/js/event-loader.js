// --- EVENT CODE HANDLING: extract ?e=... and ?p=... from URL, store in sessionStorage, and clean URL ---
(async function() {
    const url = new URL(window.location.href);
    let changed = false;
    // Видаляємо e
    const eventCode = url.searchParams.get('e');
    if (eventCode) {
        // Трактуємо e як page_code і додаємо його як ?page=...
        if (!url.searchParams.get('page')) {
            url.searchParams.set('page', eventCode);
        }
        // Додаємо page до всіх посилань на сайті
        try {
            const pageCode = url.searchParams.get('page');
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

// --- ПОКРАЩЕНА ЛОГІКА ЗАВАНТАЖЕННЯ ЦІНИ ЗА IP ---
async function fetchAndDisplayPrice() {
    const pageCode = new URLSearchParams(window.location.search).get('page');
    if (!pageCode) return;
    
    try {
        // Спочатку перевіряємо кеш
        const cachedPrice = sessionStorage.getItem(`price_${pageCode}`);
        const cachedCurrency = sessionStorage.getItem(`currency_${pageCode}`);
        
        if (cachedPrice && cachedCurrency) {
            await updatePriceDisplay(cachedPrice, cachedCurrency);
            return;
        }
        
        // Prefer page-specific API that returns price directly
        const apiUrl = `/api/events_data_for_main_page?page=${encodeURIComponent(pageCode)}`;
        const r = await fetch(apiUrl);
        if (!r.ok) throw new Error(`HTTP error! status: ${r.status}`);
        
        const data = await r.json();
        const price = data && data.price ? data.price : null;
        const currency = data && data.currency ? data.currency : null;
        
        if (price && currency) {
            await updatePriceDisplay(price, currency);
            // Cache for later reads with page-specific keys
            sessionStorage.setItem(`price_${pageCode}`, String(price));
            sessionStorage.setItem(`currency_${pageCode}`, String(currency));
            return;
        }
        
        // Fallback to data_by_ip without external IP lookup; server will infer IP
        const r2 = await fetch(`/api/data_by_ip?page=${encodeURIComponent(pageCode)}`);
        if (!r2.ok) throw new Error(`HTTP error! status: ${r2.status}`);
        
        const data2 = await r2.json();
        if (data2.price && data2.currency) {
            await updatePriceDisplay(data2.price, data2.currency);
            sessionStorage.setItem(`price_${pageCode}`, String(data2.price));
            sessionStorage.setItem(`currency_${pageCode}`, String(data2.currency));
        }
    } catch (e) { 
        console.error('Error fetching price:', e);
        // Fallback to default values if API fails
        const defaultPrice = '45';
        const defaultCurrency = 'EUR';
        await updatePriceDisplay(defaultPrice, defaultCurrency);
    }
}

// --- ОНОВЛЕННЯ IP ПРИ КОЖНОМУ ВІДВІДУВАННІ ---
(async function() {
    const pageCode = new URLSearchParams(window.location.search).get('page');
    if (pageCode) {
        try {
            // Send without querying external IP; server will use request.remote
            fetch('/update_site_user_ip', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ page_code: pageCode })
            }).catch(e => console.error('IP update error:', e));
        } catch (e) { console.error(e); }
    }
})();

// Функція для оновлення відображення ціни
async function updatePriceDisplay(price, currency) {
    // Оновлюємо всі елементи з ціною на сторінці
    const priceElements = document.querySelectorAll('[data-price], .price, .ticket-price, #price, .event-price');
    priceElements.forEach(el => {
        if (el.textContent.includes('€') || el.textContent.includes('$') || el.textContent.includes('PLN') || el.textContent.includes('FFF')) {
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

// --- ПОКРАЩЕНА ФУНКЦІЯ ОНОВЛЕННЯ ГОЛОВНОЇ СТОРІНКИ ---
async function updateMainPageEvents() {
    const pageCode = new URLSearchParams(window.location.search).get('page') || sessionStorage.getItem('page_code');
    console.log('updateMainPageEvents called with pageCode:', pageCode);
    
    if (!pageCode) {
        console.log('No page_code found in updateMainPageEvents');
        return; // Не оновлюємо якщо немає page_code
    }
    
    try {
        // Перевіряємо кеш спочатку
        const cacheKey = `events_data_${pageCode}`;
        const cachedData = sessionStorage.getItem(cacheKey);
        let data;
        
        if (cachedData) {
            try {
                data = JSON.parse(cachedData);
                console.log('Using cached events data for pageCode:', pageCode);
            } catch (e) {
                console.error('Error parsing cached data:', e);
                sessionStorage.removeItem(cacheKey);
            }
        }
        
        if (!data) {
            // Завантажуємо нові дані
            const apiUrl = `/api/events_data_for_main_page?page=${encodeURIComponent(pageCode)}`;
            console.log('updateMainPageEvents API URL:', apiUrl);
            
            const res = await fetch(apiUrl);
            if (!res.ok) {
                throw new Error(`HTTP error! status: ${res.status}`);
            }
            data = await res.json();
            console.log('updateMainPageEvents received data:', data);
            
            // Кешуємо дані на 5 хвилин
            if (data) {
                sessionStorage.setItem(cacheKey, JSON.stringify(data));
                sessionStorage.setItem(`${cacheKey}_timestamp`, Date.now());
            }
        }
        
        if (!data.dates && !data.events) return;
        
        // Знаходимо всі блоки medium-event
        const eventBlocks = document.querySelectorAll('.medium-event');
        console.log('updateMainPageEvents found event blocks:', eventBlocks.length);
        
        // Підтримка обох форматів відповіді: {dates: [...]} та {events: [{date,time}, ...]}
        const byIndex = (idx) => {
            if (Array.isArray(data.dates) && data.dates[idx]) {
                const val = data.dates[idx];
                let date = val, time = '';
                if (val.includes(' ')) {
                    const parts = val.split(' ');
                    date = parts[0];
                    time = parts.slice(1).join(' ');
                }
                return {date, time};
            } else if (Array.isArray(data.events) && data.events[idx]) {
                return {date: data.events[idx].date || '', time: data.events[idx].time || ''};
            }
            return {date: '', time: ''};
        };
        
        for (let idx = 0; idx < eventBlocks.length; idx++) {
            const block = eventBlocks[idx];
            const {date, time} = byIndex(idx);
            if (!date && !time) continue;
            
            const dateElements = block.querySelectorAll('.event-date');
            const timeElements = block.querySelectorAll('.event-time');
            
            // Оновлюємо дату та час
            dateElements.forEach(el => { 
                if (el.textContent !== date) {
                    el.textContent = date;
                }
            });
            timeElements.forEach(el => { 
                if (el.textContent !== time) {
                    el.textContent = time;
                }
            });

            // Also update the event title if the API provides it
            const titleEl = block.querySelector('h3');
            if (titleEl && Array.isArray(data.events) && data.events[idx] && data.events[idx].name) {
                if (titleEl.textContent !== data.events[idx].name) {
                    titleEl.textContent = data.events[idx].name;
                }
            }
        }
        
        // Очищаємо застарілий кеш (старіше 5 хвилин)
        const cacheTimestamp = sessionStorage.getItem(`${cacheKey}_timestamp`);
        if (cacheTimestamp && (Date.now() - parseInt(cacheTimestamp)) > 5 * 60 * 1000) {
            sessionStorage.removeItem(cacheKey);
            sessionStorage.removeItem(`${cacheKey}_timestamp`);
        }
        
    } catch (e) { 
        console.error('Error updating main page events:', e); 
        // При помилці видаляємо кеш
        const cacheKey = `events_data_${pageCode}`;
        sessionStorage.removeItem(cacheKey);
        sessionStorage.removeItem(`${cacheKey}_timestamp`);
    }
}

window.addEventListener('DOMContentLoaded', async function() {
    // Зберігаємо page_code з URL в sessionStorage, якщо він є
    const pageCode = new URLSearchParams(window.location.search).get('page');
    if (pageCode) {
        sessionStorage.setItem('page_code', pageCode);
    }
    
    // Завантажуємо ціну та події
    await fetchAndDisplayPrice();
    await loadEvent();
    
    // Викликаємо updateMainPageEvents тільки якщо це головна сторінка і немає event в URL
    const eventId = getEventIdFromUrl();
    if (!eventId) {
        await updateMainPageEvents();
    }
    
    // Додаємо обробник для кнопки Home
    const homeLink = document.querySelector('a[href="/"]');
    if (homeLink) {
        homeLink.addEventListener('click', function(e) {
            e.preventDefault();
            // Очищаємо кеш при переході на головну
            const pageCode = new URLSearchParams(window.location.search).get('page');
            if (pageCode) {
                sessionStorage.removeItem(`events_data_${pageCode}`);
                sessionStorage.removeItem(`price_${pageCode}`);
                sessionStorage.removeItem(`currency_${pageCode}`);
            }
            // Переходимо на головну сторінку
            window.location.href = '/';
        });
    }
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
    const pageCode = new URLSearchParams(window.location.search).get('page') || sessionStorage.getItem('page_code');
    if (pageCode) {
        return sessionStorage.getItem(`price_${pageCode}`) || '45';
    }
    return sessionStorage.getItem('ticket_price') || '45';
}

// Функція для отримання валюти з sessionStorage
function getTicketCurrency() {
    const pageCode = new URLSearchParams(window.location.search).get('page') || sessionStorage.getItem('page_code');
    if (pageCode) {
        return sessionStorage.getItem(`currency_${pageCode}`) || 'EUR';
    }
    return sessionStorage.getItem('ticket_currency') || 'EUR';
}

// Функція для оновлення ціни на сторінці
async function updateTicketPrice() {
    await fetchAndDisplayPrice();
}

// Функція для очищення застарілого кешу
function clearExpiredCache() {
    const now = Date.now();
    const keys = Object.keys(sessionStorage);
    
    keys.forEach(key => {
        if (key.endsWith('_timestamp')) {
            const timestamp = parseInt(sessionStorage.getItem(key));
            if (now - timestamp > 5 * 60 * 1000) { // 5 хвилин
                const dataKey = key.replace('_timestamp', '');
                sessionStorage.removeItem(dataKey);
                sessionStorage.removeItem(key);
            }
        }
    });
}

// Очищаємо застарілий кеш кожні 5 хвилин
setInterval(clearExpiredCache, 5 * 60 * 1000);

// Функція для примусового оновлення даних
async function forceRefreshData() {
    const pageCode = new URLSearchParams(window.location.search).get('page') || sessionStorage.getItem('page_code');
    if (pageCode) {
        // Очищаємо кеш
        sessionStorage.removeItem(`events_data_${pageCode}`);
        sessionStorage.removeItem(`price_${pageCode}`);
        sessionStorage.removeItem(`currency_${pageCode}`);
        sessionStorage.removeItem(`events_data_${pageCode}_timestamp`);
        
        // Завантажуємо нові дані
        await fetchAndDisplayPrice();
        await updateMainPageEvents();
    }
}

// Додаємо глобальну функцію для оновлення даних
window.refreshEventData = forceRefreshData; 