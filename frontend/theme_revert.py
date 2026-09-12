import os

def revert_theme(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Layout exceptions
    if 'layout.tsx' in path:
        if 'src/app/layout.tsx' in path:
            content = content.replace('bg-slate-100', 'bg-slate-950')
            content = content.replace('text-slate-900', 'text-slate-50')
        else:
            content = content.replace('bg-[#1a1a1a] bg-[radial-gradient(#333_1px,transparent_1px)] [background-size:16px_16px]', 'bg-slate-950')
            content = content.replace('bg-[#111111]', 'bg-slate-900')
            content = content.replace('border-[#333]', 'border-slate-800')
            content = content.replace('bg-[#c2410c]/20 text-[#c2410c]', 'bg-emerald-900/40 text-emerald-400')
            content = content.replace('text-[#c2410c]', 'text-emerald-400')
            content = content.replace('bg-[#c2410c]', 'bg-emerald-500')
            content = content.replace('border-[#c2410c]/20', 'border-emerald-500/20')
            content = content.replace('bg-[#c2410c]/20', 'bg-emerald-900/20')
            content = content.replace('shadow-[0_0_8px_rgba(194,65,12,0.8)]', 'shadow-[0_0_8px_rgba(16,185,129,0.8)]')
            content = content.replace('text-slate-200', 'text-slate-100')
    else:
        # Standard pages
        content = content.replace('bg-transparent', 'bg-slate-950')
        content = content.replace('bg-white', 'bg-[#0f172a]')
        content = content.replace('bg-slate-50', 'bg-[#1e293b]/50')
        content = content.replace('bg-slate-100', 'bg-[#1e293b]')
        
        # Borders
        content = content.replace('border-slate-200', 'border-slate-800/50')
        content = content.replace('border-slate-300', 'border-slate-700')
        
        # Text colors
        content = content.replace('text-slate-900', 'text-white')
        content = content.replace('text-slate-800', 'text-slate-200')
        content = content.replace('text-slate-700', 'text-slate-300')
        content = content.replace('text-slate-500', 'text-slate-400')
        content = content.replace('text-slate-600', 'text-slate-300')
        
        # Accents (Rust/Orange -> Emerald)
        content = content.replace('text-[#c2410c]', 'text-emerald-500')
        content = content.replace('bg-[#c2410c]', 'bg-emerald-500')
        content = content.replace('bg-[#ea580c]', 'bg-emerald-600')
        content = content.replace('border-[#c2410c]/20', 'border-emerald-500/20')
        content = content.replace('bg-[#c2410c]/10', 'bg-emerald-500/10')
        content = content.replace('bg-orange-50', 'bg-emerald-950/30')
        content = content.replace('border-orange-200', 'border-emerald-900/50')
        content = content.replace('bg-orange-100', 'bg-emerald-900/40')
        content = content.replace('border-[#c2410c]', 'border-emerald-500')
        content = content.replace('text-[#d97706]', 'text-emerald-400')
        
        # Recharts styling
        content = content.replace("backgroundColor: '#ffffff'", "backgroundColor: '#0f172a'")
        content = content.replace("borderColor: '#e2e8f0'", "borderColor: '#1e293b'")
        content = content.replace("color: '#0f172a'", "color: '#f8fafc'")
        content = content.replace('stroke="#64748b"', 'stroke="#94a3b8"')
        content = content.replace('stroke="#e2e8f0"', 'stroke="#334155"')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

for root, _, files in os.walk('src/app'):
    for file in files:
        if file.endswith('.tsx'):
            apply_path = os.path.join(root, file)
            # Revert everything in dashboard and app root
            revert_theme(apply_path)

