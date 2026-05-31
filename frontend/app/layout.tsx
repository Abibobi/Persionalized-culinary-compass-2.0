import "./globals.css";

import { AuthProvider } from "@/lib/auth";
import { ThemeProvider } from "@/components/ThemeProvider";
import Navbar from "@/components/Navbar";

export const metadata = {
  title: "Personalized Culinary Compass | AI Nutrition Assistant",
  description:
    "AI-powered nutrition recommendation platform with hybrid search, safety-aware personalization, and automated meal planning. Built with Django, Next.js, and NLP.",
  keywords: ["nutrition", "meal planning", "AI", "recipe search", "personalized diet"],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
      </head>
      <body>
        <ThemeProvider>
          <AuthProvider>
            <div className="page-shell">
              <Navbar />
              {children}
            </div>
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
