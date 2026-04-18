import type { Metadata } from "next";
import { Inter, Raleway } from "next/font/google";
import { Toaster } from "react-hot-toast";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600"],
});

const raleway = Raleway({
  variable: "--font-raleway",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "Retain AI — Retention Intelligence",
  description:
    "AI-powered retention analysis. Upload your data, answer a few questions, and get actionable insights to reduce churn.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${raleway.variable} dark h-full antialiased`}
    >
      <body className="min-h-full flex flex-col font-[family-name:var(--font-inter)]">
        <Toaster 
          position="bottom-center" 
          toastOptions={{
            style: { background: "#18181b", color: "#fafafa", border: "1px solid rgba(255,255,255,0.1)" },
            success: { iconTheme: { primary: "#34d399", secondary: "#18181b" } },
            error: { iconTheme: { primary: "#ef4444", secondary: "#18181b" } },
          }} 
        />
        {children}
      </body>
    </html>
  );
}
