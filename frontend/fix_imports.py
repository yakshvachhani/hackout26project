import os

path = 'src/app/(dashboard)/page.tsx'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("'use client';\nimport { useSettings } from '@/contexts/SettingsContext';\n// Flow Diagram Component", "'use client';\nimport { useSettings } from '@/contexts/SettingsContext';\nimport React, { useEffect, useState } from 'react';\nimport { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';\nimport { Leaf, Droplet, Zap, Battery, CircleDollarSign, Wind, Sun, CloudRain } from 'lucide-react';\nimport { cn } from '@/lib/utils';\n\n// Flow Diagram Component")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
