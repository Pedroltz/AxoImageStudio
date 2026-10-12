const vm = require('node:vm');
const fs = require('node:fs');
const assert = require('node:assert/strict');
let visible=false, calls=0, now=10000, update;
const panel={getClientRects:()=>visible?[{}]:[]};
const root={querySelector:s=>s==='#tab_axo_studio'?panel:{click:()=>calls++}};
vm.runInNewContext(fs.readFileSync(require('node:path').join(__dirname,'../extension/javascript/axo_gallery.js'),'utf8'),{
 onUiUpdate:fn=>{update=fn},gradioApp:()=>root,Date:{now:()=>now}
});
update();assert.equal(calls,0);
visible=true;update();assert.equal(calls,1);
update();update();assert.equal(calls,1);
visible=false;update();now+=2000;visible=true;update();assert.equal(calls,2);
console.log('Tab refresh: open, stable selection, return — passed');
