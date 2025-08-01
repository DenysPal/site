// Універсальний скрипт для діагностики та виправлення проблем з даними івентів

(function() {
    'use strict';
    
    // Функція для очистки кешу та sessionStorage
    function clearEventCache() {
        console.log('[EVENT-DEBUG] Clearing event cache...');
        
        // Очищаємо sessionStorage від старих даних
        const keysToRemove = ['ticket_price', 'ticket_currency', 'event_data_cache'];
        keysToRemove.forEach(key => {
            if (sessionStorage.getItem(key)) {
                console.log(`[EVENT-DEBUG] Removing ${key} from sessionStorage:`, sessionStorage.getItem(key));
                sessionStorage.removeItem(key);
            }
        });
        
        // Додаємо timestamp для запобігання кешуванню
        window.eventCacheBuster = Date.now();
    }
    
    // Функція для отримання правильного page_code
    function getPageCode() {
        const urlParams = new URLSearchParams(window.location.search);
        const pageCodeFromUrl = urlParams.get('page');
        const pageCodeFromStorage = sessionStorage.getItem('page_code');
        
        console.log('[EVENT-DEBUG] Page code sources:');
        console.log('  From URL:', pageCodeFromUrl);
        console.log('  From sessionStorage:', pageCodeFromStorage);
        
        const pageCode = pageCodeFromUrl || pageCodeFromStorage;
        console.log('  Selected page_code:', pageCode);
        
        return pageCode;
    }
    
    // Функція для завантаження даних з діагностикою
    function loadEventDataWithDebug(eventIndex, eventName) {
        console.log(`[EVENT-DEBUG] Loading data for ${eventName} (index: ${eventIndex})`);
        
        const pageCode = getPageCode();
        if (!pageCode) {
            console.error('[EVENT-DEBUG] No page_code available!');
            return;
        }
        
        // Очищаємо кеш перед завантаженням
        clearEventCache();
        
        // Завантажуємо дані з cache buster
        const cacheBuster = `&_cb=${Date.now()}`;
        
        // Завантажуємо дату
        console.log(`[EVENT-DEBUG] Fetching date for event ${eventIndex}...`);
        fetch(`/api/event_date?page=${encodeURIComponent(pageCode)}&event=${eventIndex}${cacheBuster}`)
            .then(r => r.json())
            .then(data => {
                console.log(`[EVENT-DEBUG] Date response for ${eventName}:`, data);
                if (data.date) {
                    const dateEl = document.getElementById('event-date');
                    if (dateEl) {
                        dateEl.textContent = data.date;
                        console.log(`[EVENT-DEBUG] Updated date element with: ${data.date}`);
                    }
                }
            })
            .catch(err => console.error(`[EVENT-DEBUG] Error loading date:`, err));
        
        // Завантажуємо час
        console.log(`[EVENT-DEBUG] Fetching time for event ${eventIndex}...`);
        fetch(`/api/event_time?page=${encodeURIComponent(pageCode)}&event=${eventIndex}${cacheBuster}`)
            .then(r => r.json())
            .then(data => {
                console.log(`[EVENT-DEBUG] Time response for ${eventName}:`, data);
                if (data.time) {
                    const timeEl = document.getElementById('event-time');
                    if (timeEl) {
                        timeEl.textContent = data.time;
                        console.log(`[EVENT-DEBUG] Updated time element with: ${data.time}`);
                    }
                }
            })
            .catch(err => console.error(`[EVENT-DEBUG] Error loading time:`, err));
        
        // Завантажуємо кількість місць
        console.log(`[EVENT-DEBUG] Fetching places for event ${eventIndex}...`);
        fetch(`/api/event_places?page=${encodeURIComponent(pageCode)}&event=${eventIndex}${cacheBuster}`)
            .then(r => r.json())
            .then(data => {
                console.log(`[EVENT-DEBUG] Places response for ${eventName}:`, data);
                if (data.places !== undefined) {
                    const placesEl = document.getElementById('event-places');
                    if (placesEl) {
                        placesEl.textContent = data.places;
                        console.log(`[EVENT-DEBUG] Updated places element with: ${data.places}`);
                    }
                }
            })
            .catch(err => console.error(`[EVENT-DEBUG] Error loading places:`, err));
    }
    
    // Експортуємо функції для використання на сторінках
    window.EventDebug = {
        clearCache: clearEventCache,
        getPageCode: getPageCode,
        loadEventData: loadEventDataWithDebug
    };
    
    console.log('[EVENT-DEBUG] Debug utilities loaded');
})();
