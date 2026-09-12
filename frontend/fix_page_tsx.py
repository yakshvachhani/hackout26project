import os

path = 'src/app/(dashboard)/page.tsx'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('value={116 \3}', 'value={116 }')
content = content.replace('subValue={Peak: 184 \3}', 'subValue={Peak: 184 }')
content = content.replace(r'value={\2}', 'value={${currency}2,840}')
content = content.replace('subValue="Projected: {currency}3,240"', 'subValue={Projected: 3,240}')

# Also fix the inner text variables
content = content.replace('84 {powerScale}', '84 ')
content = content.replace('36 {powerScale}', '36 ')
content = content.replace('18 {powerScale}', '18 ')
content = content.replace('-22 {powerScale}', '-22 ')
content = content.replace('116 {powerScale}', '116 ')
content = content.replace('24 {powerScale}', '24 ')

# Convert those to JSX evaluated properly if they are not in a template literal yet
content = content.replace('>84 <', '>{84 }<')
content = content.replace('>36 <', '>{36 }<')
content = content.replace('>18 <', '>{18 }<')
content = content.replace('>-22 <', '>{-22 }<')
content = content.replace('>116 <', '>{116 }<')
content = content.replace('>24 <', '>{24 }<')

# Remove duplicate {currency} if it got messed up
content = content.replace('{currency}{currency}', '{currency}')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
