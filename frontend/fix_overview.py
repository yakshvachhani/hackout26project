import os

path = 'src/app/(dashboard)/page.tsx'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

content = "import { useSettings } from '@/contexts/SettingsContext';\n" + content
content = content.replace("export default function DashboardOverview() {", "export default function DashboardOverview() {\n  const { currency, powerScale } = useSettings();")

content = content.replace('value="?2,840"', 'value={\2,840}')
content = content.replace('subValue="Projected: ?3,240"', 'subValue={Projected: \3,240}')
content = content.replace('value="116 MW"', 'value={116 \}')
content = content.replace('subValue="Peak: 184 MW"', 'subValue={Peak: 184 \}')
content = content.replace('84 MW', '84 \')
content = content.replace('36 MW', '36 \')
content = content.replace('18 MW', '18 \')
content = content.replace('-22 MW', '-22 \')
content = content.replace('116 MW', '116 \')
content = content.replace('24 MW', '24 \')

# Fix the tags so they are correctly wrapped if needed
content = content.replace('>84 \<', '>84 {powerScale}<')
content = content.replace('>36 \<', '>36 {powerScale}<')
content = content.replace('>18 \<', '>18 {powerScale}<')
content = content.replace('>-22 \<', '>-22 {powerScale}<')
content = content.replace('>116 \<', '>116 {powerScale}<')
content = content.replace('>24 \<', '>24 {powerScale}<')

# Also inject 'use client'
content = "'use client';\n" + content

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
