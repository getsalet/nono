const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),crypto=require('node:crypto');
const panel='docs/status/';
test('Vazir original WOFF2 is embedded unchanged with variable weights and swap',()=>{
 const css=fs.readFileSync(panel+'fonts/vazir.css','utf8');
 const match=css.match(/data:font\/woff2;base64,([A-Za-z0-9+/=]+)/);assert(match);
 const bytes=Buffer.from(match[1],'base64');assert.equal(bytes.subarray(0,4).toString(),'wOF2');
 const readme=fs.readFileSync(panel+'fonts/README.md','utf8');assert(readme.includes(crypto.createHash('sha256').update(bytes).digest('hex')));
 assert(css.includes('font-family: "Vazir"'));assert(css.includes('font-weight: 100 900'));assert(css.includes('font-display: swap'));assert(!css.includes('https://'));
});
test('Persian UI and numeric font overrides use Vazir without letter spacing',()=>{
 const css=fs.readFileSync(panel+'styles.css','utf8');assert(css.includes('--font-ui:"Vazir"'));assert(css.includes('font-family:var(--font-ui)'));assert(css.includes('font:600 20px/2 var(--font-ui)'));assert(!css.includes('Noto Sans Arabic'));assert(!/letter-spacing:-/.test(css));
 const html=fs.readFileSync(panel+'index.html','utf8');assert(html.indexOf('fonts/vazir.css?v=30.1.0')<html.indexOf('styles.css?v=4'));assert(html.includes('fonts/vazir.css?v=30.1.0'));
});
test('full original open-font license is shipped and all panel fonts deploy with assets',()=>{
 const license=fs.readFileSync(panel+'fonts/OFL.txt','utf8');assert(license.includes('SIL OPEN FONT LICENSE Version 1.1'));assert(license.includes('Vazir Project Authors'));
 const w=fs.readFileSync('.github/workflows/afp-agri-v2-dashboard.yml','utf8');assert(w.includes('cp -R docs/status/. _site/status/'));assert(w.includes('tests/status_font.test.cjs'));
});
