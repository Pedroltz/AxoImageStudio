const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('comfy_backend/starter.js', 'utf8')
    .replace('import { app } from "../../scripts/app.js";', '')
    .replace('import.meta.url', '"https://localhost/extensions/axo_starter/starter.js"');

async function scenario({ occupied = false, visited = false, ok = true } = {}) {
    let extension, loads = 0, saved = false;
    const app = {
        registerExtension(value) { extension = value; },
        graph: { _nodes: occupied ? [{}] : [] },
        async loadGraphData(graph) { assert.equal(graph.extra.axo_family, 'Anima'); loads++; },
    };
    vm.runInNewContext(source, {
        app, URL,
        fetch: async () => ({ ok, json: async () => ({ extra: { axo_family: 'Anima' } }) }),
        localStorage: { getItem: () => visited, setItem: () => { saved = true; } },
    });
    await extension.setup();
    assert.equal(loads, !occupied && !visited && ok ? 1 : 0);
    assert.equal(saved, loads === 1);
}
(async () => {
    await scenario();
    await scenario({ occupied: true });
    await scenario({ visited: true });
    await scenario({ ok: false });
    console.log('Comfy starter: initial load, preserved graph, repeat visit and missing asset — passed');
})().catch(error => { console.error(error); process.exitCode = 1; });
