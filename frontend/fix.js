const fs = require('fs');

let path = 'src/app/(dashboard)/page.tsx';
let content = fs.readFileSync(path, 'utf-8');

content = "import { useSettings } from '@/contexts/SettingsContext';\n" + content;
content = content.replace("export default function DashboardOverview() {", "export default function DashboardOverview() {\n  const { currency, powerScale } = useSettings();");

content = content.replace('value="₹2,840"', 'value={`\\${currency}2,840`}');
content = content.replace('subValue="Projected: ₹3,240"', 'subValue={`Projected: \\${currency}3,240`}');
content = content.replace('value="116 MW"', 'value={`116 \\${powerScale}`}');
content = content.replace('subValue="Peak: 184 MW"', 'subValue={`Peak: 184 \\${powerScale}`}');
content = content.replace(/84 MW/g, '84 ${powerScale}');
content = content.replace(/36 MW/g, '36 ${powerScale}');
content = content.replace(/18 MW/g, '18 ${powerScale}');
content = content.replace(/-22 MW/g, '-22 ${powerScale}');
content = content.replace(/116 MW/g, '116 ${powerScale}');
content = content.replace(/24 MW/g, '24 ${powerScale}');

content = content.replace(/>84 \$\{powerScale\}</g, '>{`84 ${powerScale}`}<');
content = content.replace(/>36 \$\{powerScale\}</g, '>{`36 ${powerScale}`}<');
content = content.replace(/>18 \$\{powerScale\}</g, '>{`18 ${powerScale}`}<');
content = content.replace(/>-22 \$\{powerScale\}</g, '>{`-22 ${powerScale}`}<');
content = content.replace(/>116 \$\{powerScale\}</g, '>{`116 ${powerScale}`}<');
content = content.replace(/>24 \$\{powerScale\}</g, '>{`24 ${powerScale}`}<');

content = "'use client';\n" + content;

fs.writeFileSync(path, content, 'utf-8');
