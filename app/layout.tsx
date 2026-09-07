import type { Metadata } from "next";
import { DM_Sans } from "next/font/google";
import "./globals.css";
import "./parts-sheet.css";
import "./guide-layout.css";
import "./assembly-lessons.css";
import "./wiring-workbench.css";

const font = DM_Sans({ subsets: ["latin"], variable: "--font-sans" });

export const metadata: Metadata = {
  title: "Codex Micro — a DIY build guide",
  description: "Explore the parts, play the assembly, and download the CAD for a printable Codex-inspired keypad. An independent hardware prototype.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body className={font.variable}>{children}</body></html>;
}
