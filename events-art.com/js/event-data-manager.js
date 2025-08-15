/**
 * Стабільна система управління даними для виставок
 * Запобігає збитку даних при навігації між сторінками
 */

class EventDataManager {
  constructor(config) {
    this.config = {
      index: config.index || 1,
      name: config.name || 'Event',
      defaultDuration: config.defaultDuration || '3 hours',
      apiEndpoint: config.apiEndpoint || '/api/event_data'
    };
    
    this.pageCode = null;
    this.eventData = null;
    this.isInitialized = false;
    this.cacheTimeout = 5 * 60 * 1000; // 5 хвилин
    
    this.init();
  }
  
  init() {
    try {
      this.extractPageCode();
      this.setupEventListeners();
      this.loadEventData();
      this.updatePageLinks();
      this.isInitialized = true;
      
      console.log(`[EventDataManager:${this.config.name}] Initialized successfully`);
    } catch (error) {
      console.error(`[EventDataManager:${this.config.name}] Initialization failed:`, error);
    }
  }
  
  extractPageCode() {
    // Спочатку перевіряємо URL
    const urlParams = new URLSearchParams(window.location.search);
    this.pageCode = urlParams.get('page');
    
    if (this.pageCode) {
      // Якщо page_code є в URL, зберігаємо його
      sessionStorage.setItem('page_code', this.pageCode);
      console.log(`[EventDataManager:${this.config.name}] Page code from URL:`, this.pageCode);
    } else {
      // Якщо page_code немає в URL, очищаємо застарілі дані
      this.clearStaleData();
    }
  }
  
  clearStaleData() {
    // Очищаємо тільки дані, пов'язані з цією подією
    const cacheKey = `event_data_${this.pageCode}_${this.config.index}`;
    sessionStorage.removeItem(cacheKey);
    
    // Очищаємо загальні дані тільки якщо немає page_code
    if (!this.pageCode) {
      sessionStorage.removeItem('page_code');
      sessionStorage.removeItem('ticket_price');
      sessionStorage.removeItem('ticket_currency');
    }
    
    console.log(`[EventDataManager:${this.config.name}] Cleared stale session data`);
  }
  
  setupEventListeners() {
    // Слухаємо зміни в URL (навігація назад/вперед)
    window.addEventListener('popstate', () => {
      this.handleUrlChange();
    });
    
    // Слухаємо кліки по посиланнях для автоматичного додавання page_code
    document.addEventListener('click', (e) => {
      if (e.target.tagName === 'A' && e.target.href) {
        this.handleLinkClick(e.target);
      }
    });
    
    // Слухаємо зміни в sessionStorage (якщо змінюється з іншої вкладки)
    window.addEventListener('storage', (e) => {
      if (e.key === 'page_code' && e.newValue !== this.pageCode) {
        this.handlePageCodeChange(e.newValue);
      }
    });
  }
  
  handleUrlChange() {
    const urlParams = new URLSearchParams(window.location.search);
    const newPageCode = urlParams.get('page');
    
    if (newPageCode !== this.pageCode) {
      this.handlePageCodeChange(newPageCode);
    }
  }
  
  handlePageCodeChange(newPageCode) {
    this.pageCode = newPageCode;
    
    if (this.pageCode) {
      sessionStorage.setItem('page_code', this.pageCode);
      this.loadEventData();
      this.updatePageLinks();
    } else {
      this.clearStaleData();
    }
  }
  
  handleLinkClick(link) {
    if (link.href && link.href.includes(location.hostname) && this.pageCode) {
      const url = new URL(link.href);
      if (!url.searchParams.has('page')) {
        url.searchParams.set('page', this.pageCode);
        link.href = url.toString();
      }
    }
  }
  
  async loadEventData() {
    if (!this.pageCode) {
      console.log(`[EventDataManager:${this.config.name}] No page code, skipping data load`);
      return;
    }
    
    try {
      const response = await fetch(
        `${this.config.apiEndpoint}?page=${encodeURIComponent(this.pageCode)}&event=${this.config.index}&_cb=${Date.now()}`
      );
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      this.eventData = data;
      this.updateUI(data);
      this.cacheEventData(data);
      
      console.log(`[EventDataManager:${this.config.name}] Event data loaded successfully:`, data);
    } catch (error) {
      console.error(`[EventDataManager:${this.config.name}] Error loading event data:`, error);
      this.loadCachedData();
    }
  }
  
  updateUI(data) {
    // Оновлюємо адресу
    if (data.address) {
      const addressEl = document.getElementById('event-address');
      if (addressEl) addressEl.textContent = data.address;
    }
    
    // Оновлюємо дату
    if (data.date) {
      const dateEl = document.getElementById('event-date');
      if (dateEl) dateEl.textContent = data.date;
    }
    
    // Оновлюємо час
    if (data.time) {
      const timeEl = document.getElementById('event-time');
      if (timeEl) timeEl.textContent = data.time;
    }
    
    // Оновлюємо кількість місць
    if (data.places !== undefined && data.places !== null) {
      const placesEl = document.getElementById('event-places');
      if (placesEl) placesEl.textContent = `${data.places} ticket left`;
    }
    
    // Оновлюємо ціну
    if (data.price) {
      const priceEl = document.querySelector('.event-price');
      if (priceEl) priceEl.textContent = data.price;
    }
    
    // Викликаємо подію для додаткових оновлень
    this.dispatchEvent('dataUpdated', { data, manager: this });
  }
  
  cacheEventData(data) {
    if (this.pageCode) {
      const cacheKey = `event_data_${this.pageCode}_${this.config.index}`;
      const cacheData = {
        data: data,
        timestamp: Date.now(),
        version: '1.0'
      };
      
      try {
        sessionStorage.setItem(cacheKey, JSON.stringify(cacheData));
      } catch (error) {
        console.warn(`[EventDataManager:${this.config.name}] Failed to cache data:`, error);
      }
    }
  }
  
  loadCachedData() {
    if (this.pageCode) {
      const cacheKey = `event_data_${this.pageCode}_${this.config.index}`;
      const cached = sessionStorage.getItem(cacheKey);
      
      if (cached) {
        try {
          const parsed = JSON.parse(cached);
          const age = Date.now() - parsed.timestamp;
          
          // Використовуємо кеш тільки якщо він не старіший за встановлений час
          if (age < this.cacheTimeout) {
            this.eventData = parsed.data;
            this.updateUI(parsed.data);
            console.log(`[EventDataManager:${this.config.name}] Loaded cached event data (age: ${Math.round(age/1000)}s)`);
            return;
          } else {
            console.log(`[EventDataManager:${this.config.name}] Cache expired (age: ${Math.round(age/1000)}s)`);
          }
        } catch (e) {
          console.warn(`[EventDataManager:${this.config.name}] Failed to parse cached data:`, e);
        }
      }
    }
    
    // Якщо кеш недоступний або застарів, встановлюємо значення за замовчуванням
    this.setDefaultValues();
  }
  
  setDefaultValues() {
    const placesEl = document.getElementById('event-places');
    if (placesEl) placesEl.textContent = '0 ticket left';
    
    const dateEl = document.getElementById('event-date');
    if (dateEl) dateEl.textContent = 'TBD';
    
    const timeEl = document.getElementById('event-time');
    if (timeEl) timeEl.textContent = 'TBD';
    
    console.log(`[EventDataManager:${this.config.name}] Set default values`);
  }
  
  updatePageLinks() {
    if (!this.pageCode) return;
    
    // Оновлюємо всі посилання на сторінці
    document.querySelectorAll('a[href]').forEach(link => {
      if (link.href && link.href.includes(location.hostname)) {
        const url = new URL(link.href);
        if (!url.searchParams.has('page')) {
          url.searchParams.set('page', this.pageCode);
          link.href = url.toString();
        }
      }
    });
    
    // Оновлюємо посилання в меню
    document.querySelectorAll('.menu-header .nav-link[href]').forEach(link => {
      if (link.href && link.href.includes(location.hostname)) {
        const url = new URL(link.href);
        if (!url.searchParams.has('page')) {
          url.searchParams.set('page', this.pageCode);
          link.href = url.toString();
        }
      }
    });
    
    // Оновлюємо кнопку покупки квитка
    const buyBtn = document.querySelector(`a[href*="/buy-tickets/?event=${this.config.index}"]`);
    if (buyBtn) {
      buyBtn.href = `/buy-tickets/?event=${this.config.index}&page=${encodeURIComponent(this.pageCode)}`;
    }
    
    console.log(`[EventDataManager:${this.config.name}] Updated page links`);
  }
  
  // Методи для зовнішнього керування
  refresh() {
    if (this.pageCode) {
      this.loadEventData();
    }
  }
  
  getPageCode() {
    return this.pageCode;
  }
  
  getEventData() {
    return this.eventData;
  }
  
  // Система подій для розширення функціональності
  dispatchEvent(name, detail) {
    const event = new CustomEvent(`eventDataManager:${name}`, { detail });
    window.dispatchEvent(event);
  }
  
  // Статичні методи для глобального керування
  static getInstance(eventName) {
    return window[`eventDataManager_${eventName}`] || null;
  }
  
  static getAllInstances() {
    return Object.keys(window).filter(key => key.startsWith('eventDataManager_'));
  }
  
  static clearAllCaches() {
    const keys = Object.keys(sessionStorage).filter(key => key.startsWith('event_data_'));
    keys.forEach(key => sessionStorage.removeItem(key));
    console.log('[EventDataManager] Cleared all caches');
  }
}

// Глобальна функція для створення менеджера події
window.createEventDataManager = function(config) {
  const eventName = config.name.replace(/\s+/g, '_').toLowerCase();
  const instanceName = `eventDataManager_${eventName}`;
  
  // Захист від дублювання ініціалізації
  if (window[instanceName]) {
    console.warn(`[EventDataManager] ${instanceName} already exists, returning existing instance`);
    return window[instanceName];
  }
  
  try {
    const manager = new EventDataManager(config);
    window[instanceName] = manager;
    
    // Автоматична ініціалізація після завантаження DOM
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => {
        if (!manager.isInitialized) {
          manager.init();
        }
      });
    }
    
    return manager;
  } catch (error) {
    console.error(`[EventDataManager] Failed to create manager for ${config.name}:`, error);
    return null;
  }
};

// Автоматичне очищення застарілих даних при завантаженні сторінки
window.addEventListener('load', () => {
  // Очищаємо кеш старіший 1 години
  const oneHour = 60 * 60 * 1000;
  const keys = Object.keys(sessionStorage).filter(key => key.startsWith('event_data_'));
  
  keys.forEach(key => {
    try {
      const cached = sessionStorage.getItem(key);
      if (cached) {
        const parsed = JSON.parse(cached);
        const age = Date.now() - parsed.timestamp;
        
        if (age > oneHour) {
          sessionStorage.removeItem(key);
          console.log(`[EventDataManager] Removed old cache: ${key} (age: ${Math.round(age/1000)}s)`);
        }
      }
    } catch (e) {
      // Якщо не можемо розпарсити, видаляємо
      sessionStorage.removeItem(key);
    }
  });
});

console.log('[EventDataManager] Library loaded successfully'); 