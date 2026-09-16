
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"]
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains-mono",
  subsets: ["latin"]
});

export const metadata = {
  title: "ENERFLUX | Microgrid Energy Intelligence Platform",
  description: "Autonomous Dispatch Optimization, Predictive Telemetry, and Priority Community Load Management"
};

export default function RootLayout({
  children


}) {
  return (
    <html lang="en">
      <body className={`${inter.variable} ${jetbrainsMono.variable} antialiased bg-background text-on-background font-sans min-h-screen`}>
        {children}
      </body>
    </html>);

}