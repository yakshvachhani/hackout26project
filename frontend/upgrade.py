import os
import re

def premium_upgrade(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Apply SettingsContext if not present
    if 'useSettings' not in content:
        if 'import React' in content:
            content = content.replace("import React", "import { useSettings } from '@/contexts/SettingsContext';\nimport React")
        else:
            content = "import { useSettings } from '@/contexts/SettingsContext';\n" + content
        
        # Inject hook inside component - need to handle both empty args and props
        # Usually it's `export default function OverviewPage() {`
        content = re.sub(r'export default function (\w+)\(\) \{', r'export default function \1() {\n  const { currency, powerScale } = useSettings();', content)
        content = re.sub(r'export default function (\w+)\([^)]*\) \{', r'export default function \1() {\n  const { currency, powerScale } = useSettings();', content)

        # Fix specific JSX syntax vs Template literals for currency and kW
        # We'll just replace ₹ with {currency} or `${currency}` where appropriate.
        # This regex replaces ₹ inside string templates first
        content = re.sub(r'`₹', r'`${currency}', content)
        # Replaces ₹ in JSX children
        content = re.sub(r'₹', r'{currency}', content)
        
        # Power scale
        # Replace hardcoded kW with {powerScale}
        content = re.sub(r'\bkW\b', r'{powerScale}', content)

    # Upgrade UI classes
    content = content.replace('bg-slate-900', 'bg-[#0f172a]')
    content = content.replace('bg-slate-800', 'bg-[#1e293b]/50')
    content = content.replace('border-slate-800', 'border-slate-800/50')
    
    # Try to add better card styles
    content = content.replace('className="bg-[#0f172a] border-slate-800/50"', 'className="bg-[#0f172a] border-slate-800/50 rounded-xl overflow-hidden"')
    content = content.replace('rounded-lg', 'rounded-xl')
    
    # Text colors
    content = content.replace('text-slate-50', 'text-white')
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

for root, _, files in os.walk('src/app/(dashboard)'):
    for file in files:
        if file.endswith('page.tsx') and not file.startswith('layout'):
            # Skip the ones I already perfected manually to avoid messing them up
            if 'settings' in root or 'optimizer' in root or 'battery' in root or 'cost' in root:
                continue
            premium_upgrade(os.path.join(root, file))

print("Upgrade complete.")
