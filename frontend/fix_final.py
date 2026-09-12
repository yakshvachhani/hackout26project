import re

path = 'src/app/(dashboard)/page.tsx'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix KpiCards section manually using regex replacing the whole block
new_kpi = '''        <KpiCard title="Renewable Share" value="74.8%" subValue="Target: 80%" icon={Leaf} colorClass="text-emerald-500" />
        <KpiCard title="Diesel Dependency" value="12.4%" subValue="-2.1% from yesterday" icon={Droplet} colorClass="text-red-500" />
        <KpiCard title="Current Load" value={116 } subValue={Peak: 184 } icon={Zap} colorClass="text-yellow-500" />
        <KpiCard title="Battery SOC" value="68%" subValue="Charging (340 kWh)" icon={Battery} colorClass="text-indigo-500" />
        <KpiCard title="Operating Cost" value={${currency}2,840} subValue={Projected: 3,240} icon={CircleDollarSign} colorClass="text-emerald-500" />
        <KpiCard title="Carbon Avoided" value="126 kg" subValue="Equivalent to 5 trees" icon={CloudRain} colorClass="text-blue-400" />'''

content = re.sub(r'<KpiCard title="Renewable Share".*?colorClass="text-blue-400" />', new_kpi, content, flags=re.DOTALL)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)


path2 = 'src/app/(dashboard)/dispatch/page.tsx'
with open(path2, 'r', encoding='utf-8') as f:
    content2 = f.read()

content2 = content2.replace('  const { currency, powerScale } = useSettings();\n  const { currency, powerScale } = useSettings();', '  const { currency, powerScale } = useSettings();')

with open(path2, 'w', encoding='utf-8') as f:
    f.write(content2)

