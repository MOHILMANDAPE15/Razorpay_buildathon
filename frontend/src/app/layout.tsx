import type { Metadata } from 'next';
import './globals.css';
import { Sidebar } from '@/components/Sidebar';
import { JudgeChatbotWidget } from '@/components/JudgeChatbotWidget';

export const metadata: Metadata = {
  title: 'Aegis-RTO | Autonomous COD Fraud Defense Engine',
  description:
    'Self-evolving return-to-origin and cash-on-delivery fraud defense system with live knowledge graph lineage tracking and 3-way decision routing.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="min-h-screen bg-slate-50 text-slate-900 font-sans antialiased flex">
        <Sidebar />
        <main className="flex-1 min-h-screen overflow-y-auto">
          <div className="max-w-6xl mx-auto px-6 lg:px-10 py-8">
            {children}
          </div>
        </main>
        <JudgeChatbotWidget />
      </body>
    </html>
  );
}

