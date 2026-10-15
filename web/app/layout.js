import "./globals.css";

export const metadata = {
  title: "Marksheet AI — Apple Document Intelligence",
  description: "Extract marksheet data quickly and accurately with Apple macOS UI and AI-powered OCR.",
  icons: {
    icon: "data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>📄</text></svg>",
  },
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="antialiased select-none">
        <div className="apple-ambient-bg" />
        {children}
      </body>
    </html>
  );
}
