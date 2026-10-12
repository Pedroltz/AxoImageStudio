/* Refresh native extra-network cards when opening the LoRA panel. */
(() => {
    let lastRefresh = 0;
    const refresh = (tabname) => {
        const now = Date.now();
        if (now - lastRefresh < 2000) return;
        const root = gradioApp();
        const button = root.querySelector(`[id^="${tabname}_"][id$="_extra_refresh_internal"]`) || root.querySelector(`#${tabname}_extra_refresh`);
        if (button) {
            lastRefresh = now;
            button.click();
        }
    };
    onUiLoaded(() => {
        const original = window.extraNetworksTabSelected;
        if (typeof original !== 'function') return;
        window.extraNetworksTabSelected = function (...args) {
            const result = original.apply(this, args);
            if (args.some(value => typeof value === 'string' && /_lora$/i.test(value))) {
                setTimeout(() => refresh(args[0]), 100);
            }
            return result;
        };
    });
    let wasVisible = false;
    onUiUpdate(() => {
        const root = gradioApp();
        const visible = ['txt2img', 'img2img'].find(tab => {
            const panel = root.querySelector(`#${tab}_lora`);
            return panel && panel.getClientRects().length > 0;
        });
        if (visible && !wasVisible) setTimeout(() => refresh(visible), 100);
        wasVisible = Boolean(visible);
    });
})();
