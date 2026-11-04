import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "Axo.Starter",
    async setup() {
        const response = await fetch(new URL("./initial.json", import.meta.url));
        if (!response.ok) return;
        const graph = await response.json();
        const key = `axo.starter.${graph.extra.axo_family}`;
        if (!localStorage.getItem(key) && !app.graph._nodes.length) {
            await app.loadGraphData(graph);
            localStorage.setItem(key, "1");
        }
    },
});
