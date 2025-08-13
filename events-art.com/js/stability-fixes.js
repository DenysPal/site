// Файл для покращення стабільності сайту
// Виправляє проблеми з кнопкою Home та збереженням даних

(function() {
    'use strict';
    
    // Функція для стабільного збереження даних
    function stableStorage() {
        const storage = {
            set: function(key, value) {
                try {
                    if (typeof value === 'object') {
                        value = JSON.stringify(value);
                    }
                    sessionStorage.setItem(key, value);
                    return true;
                } catch (e) {
                    console.error('Storage set error:', e);
                    return false;
                }
            },
            
            get: function(key, defaultValue = null) {
                try {
                    const value = sessionStorage.getItem(key);
                    if (value === null) return defaultValue;
                    
                    try {
                        return JSON.parse(value);
                    } catch (e) {
                        return value;
                    }
                } catch (e) {
                    console.error('Storage get error:', e);
                    return defaultValue;
                }
            },
            
            remove: function(key) {
                try {
                    sessionStorage.removeItem(key);
                    return true;
                } catch (e) {
                    console.error('Storage remove error:', e);
                    return false;
                }
            }
        };
        
        return storage;
    }
    
    // Функція для перевірки стабільності даних
    function validateData(data) {
        if (!data) return false;
        
        // Перевіряємо структуру даних
        if (data.dates && !Array.isArray(data.dates)) return false;
        if (data.events && !Array.isArray(data.events)) return false;
        if (data.price && typeof data.price !== 'string' && typeof data.price !== 'number') return false;
        if (data.currency && typeof data.currency !== 'string') return false;
        
        // Додаткова перевірка: якщо є dates, вони повинні містити валідні дати
        if (data.dates && Array.isArray(data.dates)) {
            for (let date of data.dates) {
                if (typeof date !== 'string' || date.trim().length === 0) {
                    return false;
                }
            }
        }
        
        // Додаткова перевірка: якщо є events, вони повинні мати правильну структуру
        if (data.events && Array.isArray(data.events)) {
            for (let event of data.events) {
                if (!event || typeof event !== 'object') return false;
                if (event.date && typeof event.date !== 'string') return false;
                if (event.time && typeof event.time !== 'string') return false;
            }
        }
        
        // НОВА ПЕРЕВІРКА: консистентність між dates та events
        if (data.dates && data.events && Array.isArray(data.dates) && Array.isArray(data.events)) {
            if (data.dates.length !== data.events.length) return false;
            
            // Перевіряємо що кожен event має відповідну дату
            for (let i = 0; i < data.dates.length; i++) {
                const dateStr = data.dates[i];
                const event = data.events[i];
                
                if (!event || !event.date) return false;
                
                // Перевіряємо що дата в event відповідає даті в dates
                if (dateStr.includes(' ')) {
                    const datePart = dateStr.split(' ')[0];
                    if (event.date !== datePart) return false;
                } else {
                    if (event.date !== dateStr) return false;
                }
            }
        }
        
        return true;
    }
    
    // НОВА ФУНКЦІЯ: перевірка консистентності даних
    function checkDataConsistency(data) {
        if (!data) return false;
        
        // Перевіряємо що якщо є dates, то має бути і events
        if (data.dates && !data.events) return false;
        if (data.events && !data.dates) return false;
        
        // Перевіряємо що кількість dates та events співпадає
        if (data.dates && data.events && data.dates.length !== data.events.length) return false;
        
        // Перевіряємо що кожен event має валідну структуру
        if (data.events && Array.isArray(data.events)) {
            for (let event of data.events) {
                if (!event || typeof event !== 'object') return false;
                if (!event.date || typeof event.date !== 'string') return false;
                if (event.time === undefined || (event.time !== null && typeof event.time !== 'string')) return false;
            }
        }
        
        return true;
    }
    
    // НОВА ФУНКЦІЯ: безпечне збереження даних з перевіркою консистентності
    function safeStoreData(pageCode, data) {
        if (!pageCode || !data) return false;
        
        const storage = stableStorage();
        
        // Перевіряємо чи не йде очищення кешу
        if (sessionStorage.getItem(`clearing_cache_${pageCode}`)) {
            console.log('Cache clearing in progress, skipping data storage for page_code:', pageCode);
            return false;
        }
        
        // Перевіряємо консистентність перед збереженням
        if (!checkDataConsistency(data)) {
            console.warn('Data consistency check failed, attempting to fix:', data);
            
            // Спроба виправити дані
            if (data.dates && !data.events) {
                data.events = data.dates.map((date, index) => {
                    if (date.includes(' ')) {
                        const [datePart, timePart] = date.split(' ', 2);
                        return { name: `Event ${index + 1}`, date: datePart, time: timePart };
                    } else {
                        return { name: `Event ${index + 1}`, date: date, time: '' };
                    }
                });
            } else if (data.events && !data.dates) {
                data.dates = data.events.map(event => {
                    if (event.time) {
                        return `${event.date} ${event.time}`;
                    } else {
                        return event.date;
                    }
                });
            }
            
            // Перевіряємо знову після виправлення
            if (!checkDataConsistency(data)) {
                console.error('Failed to fix data consistency, using fallback');
                return false;
            }
        }
        
        // Зберігаємо дані з timestamp
        storage.set(`events_data_${pageCode}`, data);
        storage.set(`events_data_${pageCode}_timestamp`, Date.now());
        
        // Зберігаємо окремі значення
        if (data.price) storage.set(`price_${pageCode}`, data.price);
        if (data.currency) storage.set(`currency_${pageCode}`, data.currency);
        
        console.log('Data safely stored for page_code:', pageCode);
        return true;
    }
    
    // Функція для перевірки чи можна завантажувати дані
    function canFetchData(pageCode) {
        if (sessionStorage.getItem(`clearing_cache_${pageCode}`)) {
            console.log('Cache clearing in progress, skipping data fetch for page_code:', pageCode);
            return false;
        }
        
        const lastFetchKey = `last_fetch_${pageCode}`;
        const lastFetch = sessionStorage.getItem(lastFetchKey);
        const now = Date.now();
        
        // Зменшуємо мінімальний інтервал між запитами до 500мс
        if (lastFetch && (now - parseInt(lastFetch)) < 500) { // Мінімум 500 мс
            console.log('Data fetch too frequent for page_code:', pageCode);
            return false;
        }
        
        // Встановлюємо timestamp останнього завантаження
        sessionStorage.setItem(lastFetchKey, now);
        return true;
    }
    
    // Функція для відновлення даних при помилці
    function recoverData(pageCode) {
        const storage = stableStorage();
        
        // Спочатку спробуємо відновити з backup даних
        const backupData = sessionStorage.getItem(`backup_events_data_${pageCode}`);
        const backupPrice = sessionStorage.getItem(`backup_price_${pageCode}`);
        const backupCurrency = sessionStorage.getItem(`backup_currency_${pageCode}`);
        
        if (backupData && backupPrice && backupCurrency) {
            try {
                const parsedData = JSON.parse(backupData);
                console.log(`Recovering data from backup for page_code: ${pageCode}`);
                
                // Відновлюємо основні дані
                storage.set(`events_data_${pageCode}`, parsedData);
                storage.set(`price_${pageCode}`, backupPrice);
                storage.set(`currency_${pageCode}`, backupCurrency);
                storage.set(`events_data_${pageCode}_timestamp`, Date.now());
                
                // Очищаємо backup після успішного відновлення
                sessionStorage.removeItem(`backup_events_data_${pageCode}`);
                sessionStorage.removeItem(`backup_price_${pageCode}`);
                sessionStorage.removeItem(`backup_currency_${pageCode}`);
                
                return parsedData;
            } catch (e) {
                console.error('Error parsing backup data:', e);
                // Якщо backup пошкоджений, видаляємо його
                sessionStorage.removeItem(`backup_events_data_${pageCode}`);
                sessionStorage.removeItem(`backup_price_${pageCode}`);
                sessionStorage.removeItem(`backup_currency_${pageCode}`);
            }
        }
        
        // Якщо backup недоступний, використовуємо fallback дані
        const fallbackOptions = [
            {
                dates: [
                    '28.06.2025 10:00-22:08',
                    '29.06.2025 10:00-22:07',
                    '30.06.2025 10:00-22:06',
                    '01.07.2025 10:00-22:05',
                    '02.07.2025 10:00-22:04',
                    '03.07.2025 10:00-22:03',
                    '04.07.2025 10:00-22:02',
                    '05.07.2025 10:00-22:01'
                ],
                price: '45',
                currency: 'EUR'
            },
            {
                dates: [
                    '28.06.2025 10:00-22:20',
                    '29.06.2025 10:00-22:30',
                    '30.06.2025 10:00-22:40',
                    '01.07.2025 10:00-22:00',
                    '02.07.2025 10:00-22:00',
                    '03.07.2025 10:00-22:00',
                    '04.07.2025 10:00-22:00',
                    '05.07.2025 10:00-22:01'
                ],
                price: '45',
                currency: 'EUR'
            }
        ];
        
        // Вибираємо fallback дані на основі page_code для різноманітності
        const fallbackIndex = pageCode ? (pageCode.charCodeAt(0) % fallbackOptions.length) : 0;
        const fallbackData = fallbackOptions[fallbackIndex];
        
        // Створюємо events масив з dates
        const events = fallbackData.dates.map((date, index) => {
            if (date.includes(' ')) {
                const [datePart, timePart] = date.split(' ', 1);
                return {
                    name: `Event ${index + 1}`,
                    date: datePart,
                    time: timePart
                };
            } else {
                return {
                    name: `Event ${index + 1}`,
                    date: date,
                    time: ''
                };
            }
        });
        
        const completeData = {
            ...fallbackData,
            events: events
        };
        
        storage.set(`events_data_${pageCode}`, completeData);
        storage.set(`price_${pageCode}`, completeData.price);
        storage.set(`currency_${pageCode}`, completeData.currency);
        
        console.log(`Recovered data for page_code: ${pageCode} using fallback option ${fallbackIndex}`);
        
        return completeData;
    }
    
    // Функція для стабільного оновлення UI
    function updateUIStably(selector, value, attribute = 'textContent') {
        try {
            const elements = document.querySelectorAll(selector);
            elements.forEach(el => {
                if (el && el[attribute] !== undefined) {
                    el[attribute] = value;
                }
            });
            return true;
        } catch (e) {
            console.error('UI update error:', e);
            return false;
        }
    }
    
    // Функція для автоматичного відновлення даних на головній сторінці
    function autoRecoverHomePageData() {
        const lastPageCode = sessionStorage.getItem('last_page_code');
        if (!lastPageCode) return;
        
        console.log('Auto-recovering data for home page with last_page_code:', lastPageCode);
        
        // Перевіряємо чи є дані для цього page_code
        const hasEventsData = sessionStorage.getItem(`events_data_${lastPageCode}`);
        const hasPriceData = sessionStorage.getItem(`price_${lastPageCode}`);
        const hasCurrencyData = sessionStorage.getItem(`currency_${lastPageCode}`);
        
        if (!hasEventsData || !hasPriceData || !hasCurrencyData) {
            console.log('Missing data detected, attempting recovery...');
            
            // Спробуємо відновити дані
            const recoveredData = recoverData(lastPageCode);
            
            if (recoveredData) {
                console.log('Data recovered successfully, updating UI...');
                
                // Оновлюємо UI з відновленими даними
                if (typeof updatePriceDisplay === 'function') {
                    updatePriceDisplay(recoveredData.price, recoveredData.currency);
                }
                
                if (typeof updateMainPageEvents === 'function') {
                    updateMainPageEvents();
                }
            }
        }
    }
    
    // Функція для перевірки стану сторінки
    function checkPageHealth() {
        const health = {
            homeButton: false,
            eventData: false,
            priceData: false,
            navigation: false
        };
        
        // Перевіряємо кнопку Home
        const homeLink = document.querySelector('a[href="/"]');
        health.homeButton = homeLink && homeLink.href === window.location.origin + '/';
        
        // Перевіряємо наявність даних подій
        const eventBlocks = document.querySelectorAll('.medium-event');
        health.eventData = eventBlocks.length > 0;
        
        // Перевіряємо наявність ціни
        const priceElements = document.querySelectorAll('.event-price, .price');
        health.priceData = priceElements.length > 0;
        
        // Перевіряємо навігацію
        const navLinks = document.querySelectorAll('.nav-link');
        health.navigation = navLinks.length > 0;
        
        return health;
    }
    
    // Функція для автоматичного відновлення
    function autoRecover() {
        const health = checkPageHealth();
        const pageCode = new URLSearchParams(window.location.search).get('page');
        
        if (!health.homeButton && pageCode) {
            // Відновлюємо кнопку Home
            const homeLink = document.querySelector('a[href="/"]');
            if (homeLink) {
                homeLink.href = '/';
                console.log('Home button restored');
            }
        }
        
        if (!health.eventData && pageCode) {
            // Відновлюємо дані подій
            const storage = stableStorage();
            const cachedData = storage.get(`events_data_${pageCode}`);
            if (cachedData && validateData(cachedData)) {
                updateMainPageEvents();
                console.log('Event data restored from cache');
            } else {
                // Використовуємо fallback дані
                const fallbackData = recoverData(pageCode);
                updateMainPageEvents();
                console.log('Event data restored from fallback');
            }
        }
        
        if (!health.priceData && pageCode) {
            // Відновлюємо ціну
            fetchAndDisplayPrice();
            console.log('Price data restored');
        }
    }
    
    // Функція для стабільної навігації
    function stableNavigation() {
        // Перехоплюємо всі кліки по посиланнях
        document.addEventListener('click', function(e) {
            const link = e.target.closest('a');
            if (!link || !link.href) return;
            
            // Спеціальна обробка для кнопки Home
            if (link.pathname === '/' || link.href.endsWith('/')) {
                e.preventDefault();
                
                // НОВА ЛОГІКА: запобігаємо race condition
                const pageCode = new URLSearchParams(window.location.search).get('page');
                if (pageCode) {
                    // Встановлюємо флаг що йде очищення кешу
                    sessionStorage.setItem(`clearing_cache_${pageCode}`, 'true');
                    
                    // Зберігаємо page_code для використання на головній сторінці
                    sessionStorage.setItem('last_page_code', pageCode);
                    
                    // Зберігаємо поточні дані як backup перед очищенням
                    const currentData = sessionStorage.getItem(`events_data_${pageCode}`);
                    const currentPrice = sessionStorage.getItem(`price_${pageCode}`);
                    const currentCurrency = sessionStorage.getItem(`currency_${pageCode}`);
                    
                    if (currentData) {
                        sessionStorage.setItem(`backup_events_data_${pageCode}`, currentData);
                    }
                    if (currentPrice) {
                        sessionStorage.setItem(`backup_price_${pageCode}`, currentPrice);
                    }
                    if (currentCurrency) {
                        sessionStorage.setItem(`backup_currency_${pageCode}`, currentCurrency);
                    }
                    
                    const storage = stableStorage();
                    // Очищаємо всі дані пов'язані з поточною сторінкою
                    storage.remove(`events_data_${pageCode}`);
                    storage.remove(`price_${pageCode}`);
                    storage.remove(`currency_${pageCode}`);
                    storage.remove(`events_data_${pageCode}_timestamp`);
                    
                    // Додатково очищаємо застарілі дані
                    const keys = Object.keys(sessionStorage);
                    keys.forEach(key => {
                        if (key.includes(pageCode) || key.includes('_timestamp')) {
                            sessionStorage.removeItem(key);
                        }
                    });
                    
                    // Видаляємо флаг очищення
                    sessionStorage.removeItem(`clearing_cache_${pageCode}`);
                    
                    console.log(`Cache cleared for page_code: ${pageCode}, saved as last_page_code with backup data`);
                }
                
                // Переходимо на головну сторінку з повним перезавантаженням
                window.location.href = '/';
                return;
            }
            
            // Додаємо page_code до всіх внутрішніх посилань
            const pageCode = new URLSearchParams(window.location.search).get('page');
            if (pageCode && link.href.includes(location.hostname)) {
                const linkUrl = new URL(link.href);
                if (!linkUrl.searchParams.has('page')) {
                    linkUrl.searchParams.set('page', pageCode);
                    link.href = linkUrl.toString();
                }
            }
        });
    }
    
    // Функція для періодичної перевірки стабільності
    function startHealthCheck() {
        setInterval(() => {
            const health = checkPageHealth();
            const issues = Object.entries(health).filter(([key, value]) => !value);
            
            if (issues.length > 0) {
                console.log('Page health issues detected:', issues.map(([key]) => key));
                autoRecover();
            }
        }, 10000); // Перевіряємо кожні 10 секунд
        
        // Додатково очищаємо застарілий кеш кожні 2 хвилини
        setInterval(() => {
            const now = Date.now();
            const keys = Object.keys(sessionStorage);
            let cleanedCount = 0;
            
            keys.forEach(key => {
                if (key.endsWith('_timestamp')) {
                    const timestamp = parseInt(sessionStorage.getItem(key));
                    if (now - timestamp > 5 * 60 * 1000) { // 5 хвилин
                        const dataKey = key.replace('_timestamp', '');
                        sessionStorage.removeItem(dataKey);
                        sessionStorage.removeItem(key);
                        cleanedCount++;
                    }
                }
            });
            
            if (cleanedCount > 0) {
                console.log(`Cleaned up ${cleanedCount} expired cache entries`);
            }
        }, 2 * 60 * 1000); // Кожні 2 хвилини
        
        // Додатково: перевіряємо та відновлюємо дані на головній сторінці кожні 30 секунд
        setInterval(() => {
            if (window.location.pathname === '/') {
                autoRecoverHomePageData();
            }
        }, 30 * 1000); // Кожні 30 секунд
    }
    
    // Функція для очищення last_page_code після успішного завантаження
    function clearLastPageCode() {
        const lastPageCode = sessionStorage.getItem('last_page_code');
        if (lastPageCode) {
            console.log('Clearing last_page_code after successful data load:', lastPageCode);
            sessionStorage.removeItem('last_page_code');
        }
    }
    
    // Функція для стабільного завантаження сторінки
    function stablePageLoad() {
        let loadAttempts = 0;
        const maxAttempts = 3;
        
        function attemptLoad() {
            loadAttempts++;
            
            try {
                // Завантажуємо основні дані
                let pageCode = new URLSearchParams(window.location.search).get('page');
                
                // Якщо немає page_code в URL, але ми на головній сторінці, використовуємо last_page_code
                if (!pageCode && window.location.pathname === '/') {
                    pageCode = sessionStorage.getItem('last_page_code');
                    if (pageCode) {
                        console.log('Using last_page_code from sessionStorage:', pageCode);
                    }
                }
                
                if (pageCode) {
                    // Зберігаємо page_code
                    const storage = stableStorage();
                    storage.set('page_code', pageCode);
                    
                    // Завантажуємо ціну та події
                    Promise.all([
                        fetchAndDisplayPrice(),
                        updateMainPageEvents()
                    ]).then(() => {
                        console.log('Page data loaded successfully');
                        clearLastPageCode(); // Очищаємо last_page_code після успішного завантаження
                    }).catch((error) => {
                        console.error('Page data loading failed:', error);
                        if (loadAttempts < maxAttempts) {
                            setTimeout(attemptLoad, 2000);
                        }
                    });
                } else if (window.location.pathname === '/') {
                    console.log('On home page without page_code, checking for cached data...');
                    // На головній сторінці без page_code - спробуємо завантажити дані з кешу
                    const lastPageCode = sessionStorage.getItem('last_page_code');
                    if (lastPageCode) {
                        console.log('Attempting to load data for last_page_code:', lastPageCode);
                        // Викликаємо функції завантаження з останнім page_code
                        if (typeof fetchAndDisplayPrice === 'function') {
                            fetchAndDisplayPrice();
                        }
                        if (typeof updateMainPageEvents === 'function') {
                            updateMainPageEvents();
                        }
                        
                        // Додатково: автоматично відновлюємо дані, якщо вони відсутні
                        setTimeout(() => {
                            autoRecoverHomePageData();
                        }, 1000);
                    }
                }
            } catch (error) {
                console.error('Page load attempt failed:', error);
                if (loadAttempts < maxAttempts) {
                    setTimeout(attemptLoad, 2000);
                }
            }
        }
        
        // Починаємо завантаження після повного завантаження DOM
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', attemptLoad);
        } else {
            attemptLoad();
        }
        
        // Додатково: відстежуємо зміни в URL для автоматичного оновлення даних
        let lastUrl = location.href;
        new MutationObserver(() => {
            const url = location.href;
            if (url !== lastUrl) {
                lastUrl = url;
                const pageCode = new URLSearchParams(location.search).get('page');
                if (pageCode) {
                    console.log('URL changed, refreshing data for page_code:', pageCode);
                    // Невелика затримка для забезпечення стабільності
                    setTimeout(() => {
                        if (typeof window.stabilityFixes !== 'undefined' && window.stabilityFixes.refreshData) {
                            window.stabilityFixes.refreshData();
                        }
                    }, 500);
                }
            }
        }).observe(document, {subtree: true, childList: true});
    }
    
    // Ініціалізація всіх функцій стабільності
    function initStability() {
        console.log('Initializing stability fixes...');
        
        // Запускаємо стабільну навігацію
        stableNavigation();
        
        // Запускаємо перевірку здоров'я сторінки
        startHealthCheck();
        
        // Запускаємо стабільне завантаження
        stablePageLoad();
        
        // Додаємо глобальні функції для відладки
        window.stabilityFixes = {
            checkHealth: checkPageHealth,
            autoRecover: autoRecover,
            autoRecoverHomePageData: autoRecoverHomePageData,
            clearLastPageCode: clearLastPageCode,
            forceRefresh: function() {
                let pageCode = new URLSearchParams(window.location.search).get('page');
                
                // Якщо немає page_code в URL, але ми на головній сторінці, використовуємо last_page_code
                if (!pageCode && window.location.pathname === '/') {
                    pageCode = sessionStorage.getItem('last_page_code');
                    if (pageCode) {
                        console.log('forceRefresh: Using last_page_code:', pageCode);
                    }
                }
                
                if (pageCode) {
                    const storage = stableStorage();
                    storage.remove(`events_data_${pageCode}`);
                    storage.remove(`price_${pageCode}`);
                    storage.remove(`currency_${pageCode}`);
                    storage.remove(`events_data_${pageCode}_timestamp`);
                    
                    location.reload();
                }
            },
            // Додаткова функція для примусового оновлення даних без перезавантаження
            refreshData: async function() {
                let pageCode = new URLSearchParams(window.location.search).get('page');
                
                // Якщо немає page_code в URL, але ми на головній сторінці, використовуємо last_page_code
                if (!pageCode && window.location.pathname === '/') {
                    pageCode = sessionStorage.getItem('last_page_code');
                    if (pageCode) {
                        console.log('refreshData: Using last_page_code:', pageCode);
                    }
                }
                
                if (pageCode) {
                    console.log('Forcing data refresh for page_code:', pageCode);
                    
                    // Перевіряємо чи можна завантажувати дані
                    if (!canFetchData(pageCode)) {
                        console.log('Data fetch blocked for page_code:', pageCode);
                        return;
                    }
                    
                    // Очищаємо кеш
                    const storage = stableStorage();
                    storage.remove(`events_data_${pageCode}`);
                    storage.remove(`price_${pageCode}`);
                    storage.remove(`currency_${pageCode}`);
                    storage.remove(`events_data_${pageCode}_timestamp`);
                    
                    // Завантажуємо нові дані
                    if (typeof fetchAndDisplayPrice === 'function') {
                        await fetchAndDisplayPrice();
                    }
                    if (typeof updateMainPageEvents === 'function') {
                        await updateMainPageEvents();
                    }
                }
            },
            // НОВІ ФУНКЦІЇ: безпечне збереження та перевірка даних
            safeStoreData: safeStoreData,
            canFetchData: canFetchData,
            checkDataConsistency: checkDataConsistency
        };
        
        console.log('Stability fixes initialized');
    }
    
    // Запускаємо ініціалізацію
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initStability);
    } else {
        initStability();
    }
    
})(); 