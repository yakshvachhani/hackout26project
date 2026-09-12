import os
import re

for root, _, files in os.walk('src/app'):
    for file in files:
        if file.endswith('.tsx'):
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            original = content
            
            # Fix attributes like value="{currency}2,840" -> value={\2,840}
            content = re.sub(r'(\w+)="\{currency\}([^"]+)"', r'\1={\\2}', content)
            
            # Fix attributes like value="116 {powerScale}" -> value={116 \}
            content = re.sub(r'(\w+)="([^"]*)\{powerScale\}([^"]*)"', r'\1={\2\\3}', content)
            
            # SubValue
            content = re.sub(r'subValue="\{currency\}([^"]+)"', r'subValue={\\1}', content)

            if content != original:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
