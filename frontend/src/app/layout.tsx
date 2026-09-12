import type { Metadata } from "next";
import { Inter, IBM_Plex_Mono, IBM_Plex_Serif } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: '--font-sans' });
const plexMono = IBM_Plex_Mono({ weight: ['400', '500', '600', '700'], subsets: ["latin"], variable: '--font-mono' });
const plexSerif = IBM_Plex_Serif({ weight: ['400', '500', '600', '700'], subsets: ["latin"], variable: '--font-serif' });

export const metadata: Metadata = {
  title: "Microgrid Energy Intelligence",
  description: "Advanced Microgrid Operations and Intelligence Platform",
};





























































































































export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.variable} ${plexMono.variable} ${plexSerif.variable} bg-slate-950 font-sans text-slate-50 antialiased`}>
        {children}
      </body>
    </html>
  );
}   
