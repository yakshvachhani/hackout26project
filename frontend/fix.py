import os
import re

for root, _, files in os.walk('src/app/(dashboard)'):
    for file in files:
        if file.endswith('page.tsx'):
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove duplicated hook
            content = content.replace("const { currency, powerScale } = useSettings();\\n  const { currency, powerScale } = useSettings();", "const { currency, powerScale } = useSettings();")
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
