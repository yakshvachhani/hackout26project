import os

path = 'src/app/(dashboard)/page.tsx'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if '<KpiCard title="Current Load"' in line:
        lines[i] = '        <KpiCard title="Current Load" value={116 } subValue={Peak: 184 } icon={Zap} colorClass="text-yellow-500" />\n'
    if '<KpiCard title="Operating Cost"' in line:
        lines[i] = '        <KpiCard title="Operating Cost" value={${currency}2,840} subValue={Projected: 3,240} icon={CircleDollarSign} colorClass="text-emerald-500" />\n'

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
