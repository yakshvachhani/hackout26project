import os

path = 'src/app/(dashboard)/page.tsx'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('', '$')
content = content.replace('\', '$')
content = content.replace('value={$2,840}', 'value=",840"')
content = content.replace('subValue={Projected: ,240}', 'subValue="Projected: ,240"')
content = content.replace('{currency}', '$')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
