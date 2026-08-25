"use client"
import { Geist, Geist_Mono } from "next/font/google";
import { Toaster } from "react-hot-toast";
import { AuthProvider } from "@/contexts/AuthContext";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable}`} suppressHydrationWarning>
      <head>
        <title>JURY-AI | Legal Intelligence Platform</title>
        <meta name="description" content="AI-powered legal document risk analysis using RAG and Google Gemini." />
      </head>
      <body suppressHydrationWarning>
        <AuthProvider>
          {children}
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#1E293B',
                color: '#E2E8F0',
                border: '1px solid rgba(255,255,255,0.1)',
                backdropFilter: 'blur(12px)',
              },
              success: {
                iconTheme: { primary: '#10B981', secondary: '#020617' },
              },
              error: {
                iconTheme: { primary: '#F43F5E', secondary: '#020617' },
              },
            }}
          />
        </AuthProvider>
      </body>
    </html>
  );
}
