import os

path = 'src/app/(dashboard)/page.tsx'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('value={\\2,840}', 'value={${currency}2,840}')
content = content.replace('subValue={Projected: \\3,240}', 'subValue={Projected: 3,240}')

content = content.replace('value="116 kW"', 'value={116 }')
content = content.replace('subValue="Peak: 184 kW"', 'subValue={Peak: 184 }')

content = content.replace('84 kW', '{84 }')
content = content.replace('36 kW', '{36 }')
content = content.replace('18 kW', '{18 }')
content = content.replace('-22 kW', '{-22 }')
content = content.replace('116 kW', '{116 }')
content = content.replace('24 kW', '{24 }')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
