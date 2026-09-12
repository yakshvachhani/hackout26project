const fs = require('fs');

let path = 'src/app/(dashboard)/page.tsx';
let content = fs.readFileSync(path, 'utf-8');

// The file might have "84 MW" or "84 {powerScale}" or "{`84 ${powerScale}`}". Let's safely replace all hardcoded text values to use {powerScale} string concatenation in JSX!
content = content.replace(/>84 MW</g, '>{84 + " " + powerScale}<');
content = content.replace(/>36 MW</g, '>{36 + " " + powerScale}<');
content = content.replace(/>18 MW</g, '>{18 + " " + powerScale}<');
content = content.replace(/>-22 MW</g, '>{-22 + " " + powerScale}<');
content = content.replace(/>116 MW</g, '>{116 + " " + powerScale}<');
content = content.replace(/>24 MW</g, '>{24 + " " + powerScale}<');

// If there are {powerScale} literal texts from earlier bugs:
content = content.replace(/>84 \{powerScale\}</g, '>{84 + " " + powerScale}<');
content = content.replace(/>36 \{powerScale\}</g, '>{36 + " " + powerScale}<');
content = content.replace(/>18 \{powerScale\}</g, '>{18 + " " + powerScale}<');
content = content.replace(/>-22 \{powerScale\}</g, '>{-22 + " " + powerScale}<');
content = content.replace(/>116 \{powerScale\}</g, '>{116 + " " + powerScale}<');
content = content.replace(/>24 \{powerScale\}</g, '>{24 + " " + powerScale}<');

fs.writeFileSync(path, content, 'utf-8');
