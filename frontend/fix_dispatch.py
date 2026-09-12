import os
import re

path = 'src/app/(dashboard)/dispatch/page.tsx'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Apply SettingsContext if not present
if 'useSettings' not in content:
    if 'import React' in content:
        content = content.replace("import React", "import { useSettings } from '@/contexts/SettingsContext';\nimport React")
    else:
        content = "import { useSettings } from '@/contexts/SettingsContext';\n" + content
    
    if "'use client'" not in content and '"use client"' not in content:
        content = "'use client';\n\n" + content
        
    content = re.sub(r'export default function (\w+)\(\) \{', r'export default function \1() {\n  const { currency, powerScale } = useSettings();', content)
    content = re.sub(r'export default function (\w+)\([^)]*\) \{', r'export default function \1() {\n  const { currency, powerScale } = useSettings();', content)

    # Fix currency
    content = content.replace('?', '{currency}')
    # Fix kW -> {powerScale} inside texts
    content = re.sub(r'\bkW\b', '{powerScale}', content)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
