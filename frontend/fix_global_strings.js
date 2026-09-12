const fs = require('fs');

// 1. Fix Reports Page
let reportsPath = 'src/app/(dashboard)/reports/page.tsx';
let reportsContent = fs.readFileSync(reportsPath, 'utf8');
reportsContent = reportsContent.replace('{activeData.cost}', '{activeData.cost.replace(/\\{currency\\}/g, currency)}');
reportsContent = reportsContent.replace('{activeData.saved}', '{activeData.saved.replace(/\\{currency\\}/g, currency)}');
reportsContent = reportsContent.replace('{row.cap}', '{row.cap.replace(/\\{powerScale\\}/g, powerScale)}');
fs.writeFileSync(reportsPath, reportsContent, 'utf8');

// 2. Fix Assets Page
let assetsPath = 'src/app/(dashboard)/assets/page.tsx';
let assetsContent = fs.readFileSync(assetsPath, 'utf8');
assetsContent = assetsContent.replace(/\{spec\.value\}/g, '{spec.value.replace(/\\{powerScale\\}/g, powerScale)}');
assetsContent = assetsContent.replace('`${val} {powerScale}`', '`${val} ${powerScale}`');
fs.writeFileSync(assetsPath, assetsContent, 'utf8');

// 3. Fix Scenarios Page
let scenariosPath = 'src/app/(dashboard)/scenarios/page.tsx';
let scenariosContent = fs.readFileSync(scenariosPath, 'utf8');
scenariosContent = scenariosContent.replace('{scenario.description}', '{scenario.description.replace(/\\{currency\\}/g, currency).replace(/\\{powerScale\\}/g, powerScale)}');
scenariosContent = scenariosContent.replace('{activeScenario.assessment}', '{activeScenario.assessment.replace(/\\{currency\\}/g, currency).replace(/\\{powerScale\\}/g, powerScale)}');
scenariosContent = scenariosContent.replace(/' \(x10 \{currency\}\)'/g, '` (x10 ${currency})`');
scenariosContent = scenariosContent.replace('prefix = "{currency}";', 'prefix = currency;');
fs.writeFileSync(scenariosPath, scenariosContent, 'utf8');

console.log("Fixes applied successfully.");
