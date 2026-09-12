import os
import re

def apply_light_theme(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Layout background exception:
    if 'layout.tsx' in path:
        content = content.replace('bg-slate-950', 'bg-[#1a1a1a] bg-[radial-gradient(#333_1px,transparent_1px)] [background-size:16px_16px]')
        content = content.replace('bg-slate-900', 'bg-[#111111]')
        # Make the sidebar border dark orange? Or just keep it dark
        content = content.replace('border-slate-800', 'border-[#333]')
        # Change the active nav item
        content = content.replace('bg-emerald-900/40 text-emerald-400', 'bg-[#c2410c]/20 text-[#c2410c]')
        content = content.replace('text-emerald-400', 'text-[#c2410c]')
        content = content.replace('bg-emerald-500', 'bg-[#c2410c]')
        content = content.replace('text-emerald-500', 'text-[#c2410c]')
        content = content.replace('border-emerald-500/20', 'border-[#c2410c]/20')
        content = content.replace('bg-emerald-900/20', 'bg-[#c2410c]/20')
        content = content.replace('shadow-[0_0_8px_rgba(16,185,129,0.8)]', 'shadow-[0_0_8px_rgba(194,65,12,0.8)]')
        content = content.replace('text-slate-100', 'text-slate-200')
    else:
        # Standard pages
        content = content.replace('bg-slate-950', 'bg-transparent')
        content = content.replace('bg-[#0f172a]', 'bg-white')
        content = content.replace('bg-slate-900', 'bg-white')
        content = content.replace('bg-[#1e293b]/50', 'bg-slate-50')
        content = content.replace('bg-[#1e293b]/30', 'bg-slate-50')
        content = content.replace('bg-[#1e293b]', 'bg-slate-100')
        
        # Borders
        content = content.replace('border-slate-800/50', 'border-slate-200')
        content = content.replace('border-slate-800', 'border-slate-200')
        content = content.replace('border-slate-700', 'border-slate-300')
        
        # Text colors
        content = content.replace('text-white', 'text-slate-900')
        content = content.replace('text-slate-50', 'text-slate-900')
        content = content.replace('text-slate-200', 'text-slate-800')
        content = content.replace('text-slate-300', 'text-slate-700')
        content = content.replace('text-slate-400', 'text-slate-500')
        
        # Accents (Emerald -> Rust/Orange)
        content = content.replace('text-emerald-500', 'text-[#c2410c]')
        content = content.replace('text-emerald-400', 'text-[#c2410c]')
        content = content.replace('bg-emerald-500', 'bg-[#c2410c]')
        content = content.replace('bg-emerald-600', 'bg-[#ea580c]')
        content = content.replace('border-emerald-500/20', 'border-[#c2410c]/20')
        content = content.replace('bg-emerald-500/10', 'bg-[#c2410c]/10')
        content = content.replace('bg-emerald-950/30', 'bg-orange-50')
        content = content.replace('border-emerald-900/50', 'border-orange-200')
        
        # Fix Recharts styling for white background
        content = content.replace("backgroundColor: '#0f172a'", "backgroundColor: '#ffffff'")
        content = content.replace("borderColor: '#1e293b'", "borderColor: '#e2e8f0'")
        content = content.replace("color: '#f8fafc'", "color: '#0f172a'")
        content = content.replace('stroke="#94a3b8"', 'stroke="#64748b"')
        content = content.replace('stroke="#334155"', 'stroke="#e2e8f0"')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

for root, _, files in os.walk('src/app/(dashboard)'):
    for file in files:
        if file.endswith('.tsx'):
            apply_light_theme(os.path.join(root, file))

