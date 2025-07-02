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

function loadEvent() {
    const eventId = getEventIdFromUrl();
    const item = getItemFromUrl();
    if (!eventId || !item) return;
    
    // Виправляємо шлях до events.json
    fetch('/events.json')
        .then(res => res.json())
        .then(events => {
            if (events[eventId]) {
                updateEventInfo(events[eventId], parseInt(item));
            }
        })
        .catch(error => {
            console.error('Помилка завантаження подій:', error);
        });
}

window.addEventListener('DOMContentLoaded', function() {
    loadEvent();
    // Динамічно підставляємо дати/час у прев'ю на головній
    fetch('/events.json')
        .then(res => res.json())
        .then(events => {
            const eventIds = Object.keys(events);
            if (!eventIds.length) return;
            const eventId = eventIds[eventIds.length - 1];
            const event = events[eventId];
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
        });
});

function sendVisitLog(extra) {
    fetch('/log_visit', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            url: window.location.pathname + window.location.search,
            uniq: Date.now() + '_' + Math.random(),
            ...extra
        })
    });
}

// Надсилає лог лише при завантаженні сторінки (без дублювання)
if (window.performance && performance.navigation.type !== 2) { // не логувати при back/forward
    fetch('/log_visit', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            page: window.location.pathname + window.location.search,
            link: window.location.href,
            uniq: Date.now() + '_' + Math.random()
        })
    });
}

// 2. SPA-навігація (pushState/replaceState/popstate)
(function(history){
    var pushState = history.pushState;
    history.pushState = function(state) {
        var ret = pushState.apply(history, arguments);
        sendVisitLog();
        return ret;
    };
    var replaceState = history.replaceState;
    history.replaceState = function(state) {
        var ret = replaceState.apply(history, arguments);
        sendVisitLog();
        return ret;
    };
})(window.history);

window.addEventListener('popstate', function() {
    sendVisitLog();
});

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