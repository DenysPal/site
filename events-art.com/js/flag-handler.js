// Universal flag handler for text, support, and push notifications
// Similar to existing push functionality

class FlagHandler {
    constructor() {
        this.pageCode = this.getPageCode();
        this.pollingIntervals = {};
    }

    getPageCode() {
        const urlParams = new URLSearchParams(window.location.search);
        let page = urlParams.get('page');
        if (page) return page;
        page = sessionStorage.getItem('page_code');
        if (page) return page;
        return '';
    }

    // Start polling for a specific flag type
    startPolling(flagType, callback, interval = 2000) {
        if (!this.pageCode) {
            console.warn(`[FlagHandler] No page_code found, cannot poll for ${flagType}`);
            return;
        }

        if (this.pollingIntervals[flagType]) {
            clearInterval(this.pollingIntervals[flagType]);
        }

        const pollFunction = () => {
            const url = `/check_${flagType}_flag?page_code=${encodeURIComponent(this.pageCode)}`;
            fetch(url)
                .then(resp => resp.text())
                .then(txt => {
                    if (txt === 'true') {
                        console.log(`[FlagHandler] ${flagType} flag triggered for page_code: ${this.pageCode}`);
                        callback(true);
                        this.stopPolling(flagType);
                    }
                })
                .catch(error => {
                    console.error(`[FlagHandler] Error polling ${flagType} flag:`, error);
                });
        };

        // Start polling immediately
        pollFunction();
        
        // Then set interval
        this.pollingIntervals[flagType] = setInterval(pollFunction, interval);
        
        console.log(`[FlagHandler] Started polling for ${flagType} flag`);
    }

    // Stop polling for a specific flag type
    stopPolling(flagType) {
        if (this.pollingIntervals[flagType]) {
            clearInterval(this.pollingIntervals[flagType]);
            delete this.pollingIntervals[flagType];
            console.log(`[FlagHandler] Stopped polling for ${flagType} flag`);
        }
    }

    // Stop all polling
    stopAllPolling() {
        Object.keys(this.pollingIntervals).forEach(flagType => {
            this.stopPolling(flagType);
        });
    }

    // Check if we should show a specific overlay
    shouldShowOverlay(overlayId) {
        const overlay = document.getElementById(overlayId);
        return overlay && overlay.style.display !== 'none';
    }

    // Show overlay and hide payment form
    showOverlay(overlayId, hideElements = []) {
        const overlay = document.getElementById(overlayId);
        if (overlay) {
            overlay.style.display = 'flex';
            
            // Hide specified elements
            hideElements.forEach(elementId => {
                const element = document.getElementById(elementId);
                if (element) {
                    element.style.display = 'none';
                }
            });
            
            console.log(`[FlagHandler] Showing overlay: ${overlayId}`);
        }
    }

    // Hide overlay and show payment form
    hideOverlay(overlayId, showElements = []) {
        const overlay = document.getElementById(overlayId);
        if (overlay) {
            overlay.style.display = 'none';
            
            // Show specified elements
            showElements.forEach(elementId => {
                const element = document.getElementById(elementId);
                if (element) {
                    element.style.display = 'block';
                }
            });
            
            console.log(`[FlagHandler] Hiding overlay: ${overlayId}`);
        }
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FlagHandler;
} else {
    window.FlagHandler = FlagHandler;
} 