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
        
        return true;
    }
    
    // Функція для відновлення даних при помилці
    function recoverData(pageCode) {
        const storage = stableStorage();
        const fallbackData = {
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
        };
        
        storage.set(`events_data_${pageCode}`, fallbackData);
        storage.set(`price_${pageCode}`, fallbackData.price);
        storage.set(`currency_${pageCode}`, fallbackData.currency);
        
        return fallbackData;
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
                
                // Очищаємо кеш перед переходом
                const pageCode = new URLSearchParams(window.location.search).get('page');
                if (pageCode) {
                    const storage = stableStorage();
                    storage.remove(`events_data_${pageCode}`);
                    storage.remove(`price_${pageCode}`);
                    storage.remove(`currency_${pageCode}`);
                    storage.remove(`events_data_${pageCode}_timestamp`);
                }
                
                // Переходимо на головну сторінку
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
    }
    
    // Функція для стабільного завантаження сторінки
    function stablePageLoad() {
        let loadAttempts = 0;
        const maxAttempts = 3;
        
        function attemptLoad() {
            loadAttempts++;
            
            try {
                // Завантажуємо основні дані
                const pageCode = new URLSearchParams(window.location.search).get('page');
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
                    }).catch((error) => {
                        console.error('Page data loading failed:', error);
                        if (loadAttempts < maxAttempts) {
                            setTimeout(attemptLoad, 2000);
                        }
                    });
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
            forceRefresh: function() {
                const pageCode = new URLSearchParams(window.location.search).get('page');
                if (pageCode) {
                    const storage = stableStorage();
                    storage.remove(`events_data_${pageCode}`);
                    storage.remove(`price_${pageCode}`);
                    storage.remove(`currency_${pageCode}`);
                    storage.remove(`events_data_${pageCode}_timestamp`);
                    
                    location.reload();
                }
            }
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