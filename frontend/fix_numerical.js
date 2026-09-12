const fs = require('fs');

function replaceInFile(filePath, replacements) {
  if (!fs.existsSync(filePath)) return;
  let content = fs.readFileSync(filePath, 'utf8');
  
  if (content.includes('useSettings()') && !content.includes('formatCurrency')) {
    content = content.replace(/const\s*{\s*([^}]+)\s*}\s*=\s*useSettings\(\);/g, (match, vars) => {
      let v = vars.split(',').map(s => s.trim());
      if (!v.includes('formatCurrency')) v.push('formatCurrency');
      if (!v.includes('formatPower')) v.push('formatPower');
      return `const { ${v.join(', ')} } = useSettings();`;
    });
  }

  replacements.forEach(([search, replace]) => {
    content = content.split(search).join(replace); // Simple global string replacement
  });
  
  // Undo previous string replacement exactly
  content = content.split("{activeData.cost.replace(/\\{currency\\}/g, currency)}").join('{formatCurrency(parseFloat(activeData.cost.replace(/[^0-9.-]+/g,"")))}');
  content = content.split("{activeData.saved.replace(/\\{currency\\}/g, currency)}").join('{formatCurrency(parseFloat(activeData.saved.replace(/[^0-9.-]+/g,"")))}');
  content = content.split("{row.cap.replace(/\\{powerScale\\}/g, powerScale)}").join('{formatPower(parseFloat(row.cap.replace(/[^0-9.-]+/g,"")))}');

  fs.writeFileSync(filePath, content, 'utf8');
}

// 1. Reports Page
replaceInFile('src/app/(dashboard)/reports/page.tsx', []);

// 2. Assets Page
replaceInFile('src/app/(dashboard)/assets/page.tsx', [
  ["{spec.value.replace(/\\{powerScale\\}/g, powerScale)}", '{spec.value.includes("{powerScale}") ? formatPower(parseFloat(spec.value.replace(/[^0-9.-]+/g,""))) : spec.value}'],
  ["`${val} ${powerScale}`", 'formatPower(val)']
]);

// Let's do Scenarios Page regex replacements manually in the script:
let scenariosPath = 'src/app/(dashboard)/scenarios/page.tsx';
if (fs.existsSync(scenariosPath)) {
  let sc = fs.readFileSync(scenariosPath, 'utf8');
  if (sc.includes('useSettings()') && !sc.includes('formatCurrency')) {
    sc = sc.replace(/const\s*{\s*([^}]+)\s*}\s*=\s*useSettings\(\);/g, (match, vars) => {
      let v = vars.split(',').map(s => s.trim());
      if (!v.includes('formatCurrency')) v.push('formatCurrency');
      if (!v.includes('formatPower')) v.push('formatPower');
      return `const { ${v.join(', ')} } = useSettings();`;
    });
  }
  
  sc = sc.split("{scenario.description.replace(/\\{currency\\}/g, currency).replace(/\\{powerScale\\}/g, powerScale)}").join( 
    `{scenario.description.replace(/\\{currency\\}([\\d,]+)/g, (m, num) => formatCurrency(parseFloat(num.replace(/,/g,'')))).replace(/([\\d,]+)\\s*\\{powerScale\\}/g, (m, num) => formatPower(parseFloat(num.replace(/,/g,''))))}`);
  
  sc = sc.split("{activeScenario.assessment.replace(/\\{currency\\}/g, currency).replace(/\\{powerScale\\}/g, powerScale)}").join( 
    `{activeScenario.assessment.replace(/\\{currency\\}([\\d,]+)/g, (m, num) => formatCurrency(parseFloat(num.replace(/,/g,'')))).replace(/([\\d,]+)\\s*\\{powerScale\\}/g, (m, num) => formatPower(parseFloat(num.replace(/,/g,''))))}`);

  fs.writeFileSync(scenariosPath, sc, 'utf8');
}

// 3. Overview Page
let overviewPath = 'src/app/(dashboard)/page.tsx';
if (fs.existsSync(overviewPath)) {
  let ov = fs.readFileSync(overviewPath, 'utf8');
  if (ov.includes('useSettings()') && !ov.includes('formatCurrency')) {
    ov = ov.replace(/const\s*{\s*([^}]+)\s*}\s*=\s*useSettings\(\);/g, (match, vars) => {
      let v = vars.split(',').map(s => s.trim());
      if (!v.includes('formatCurrency')) v.push('formatCurrency');
      if (!v.includes('formatPower')) v.push('formatPower');
      return `const { ${v.join(', ')} } = useSettings();`;
    });
  }
  
  ov = ov.split('value={currency + "2,840"}').join('value={formatCurrency(2840)}');
  ov = ov.split('value={currency + "12,450"}').join('value={formatCurrency(12450)}');
  ov = ov.split('value={currency + "98"}').join('value={formatCurrency(98)}');

  fs.writeFileSync(overviewPath, ov, 'utf8');
}


console.log("Numerical formatting fixes applied.");
