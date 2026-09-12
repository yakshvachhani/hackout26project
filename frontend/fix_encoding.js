const fs = require('fs');
let content = fs.readFileSync('src/app/(dashboard)/settings/page.tsx', 'utf8');

// The weird characters are because of UTF-8 misinterpretation of '₹', '€', '£' when user edited earlier.
content = content.replace(/,1/g, '₹');
content = content.replace(/,/g, '€');
content = content.replace(/A/g, '£');

// Import useSettings
if (!content.includes('useSettings')) {
  content = content.replace(
    "import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';",
    "import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';\nimport { useSettings } from '@/contexts/SettingsContext';"
  );
}

// Add to component top
if (!content.includes('const { setSettings } = useSettings();')) {
  content = content.replace(
    "export default function SettingsPage() {",
    "export default function SettingsPage() {\n  const { setSettings } = useSettings();"
  );
}

// Fix save to trigger global refresh
content = content.replace(
  "localStorage.setItem('microgrid_settings', JSON.stringify(config));",
  "setSettings(config);"
);

fs.writeFileSync('src/app/(dashboard)/settings/page.tsx', content, 'utf8');
console.log('Fixed settings save logic and currency encoding.');
