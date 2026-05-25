import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata = {
  title: "JURY-AI | Legal Intelligence Platform",
  description: "AI-powered legal document risk analysis using Retrieval-Augmented Generation and Google Gemini LLMs. Upload contracts, detect risky clauses, and get instant legal insights.",
  keywords: "legal AI, contract analysis, risk scoring, RAG, document intelligence",
  authors: [
    { name: "Gaurav Jha" },
    { name: "Kalash Verma" },
    { name: "Komal Raj" },
    { name: "Krish Patel" },
  ],
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable}`} suppressHydrationWarning>
      <body suppressHydrationWarning>{children}</body>
    </html>
  );
}
