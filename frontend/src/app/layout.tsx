import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ORACLE — ML Stock Predictor",
  description: "Machine learning stock prediction engine",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh">
      <body className="bg-bg text-text min-h-screen antialiased">
        {children}
      </body>
    </html>
  );
}
