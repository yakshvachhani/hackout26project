import os

for root, _, files in os.walk('src/app/(dashboard)'):
    for file in files:
        if file.endswith('page.tsx'):
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if it has use client
            if "'use client'" not in content and '"use client"' not in content:
                content = "'use client';\n\n" + content
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
