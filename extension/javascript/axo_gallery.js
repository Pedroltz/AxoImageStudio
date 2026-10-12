/* Refresh when the library becomes visible, without interrupting selections. */
(() => {
    let wasVisible = false;
    let lastRefresh = 0;
    onUiUpdate(() => {
        const root = gradioApp();
        const panel = root.querySelector('#tab_axo_studio');
        const visible = Boolean(panel && panel.getClientRects().length);
        if (visible && !wasVisible && Date.now() - lastRefresh > 1500) {
            lastRefresh = Date.now();
            root.querySelector('#axo-refresh')?.click();
        }
        wasVisible = visible;
    });
})();
