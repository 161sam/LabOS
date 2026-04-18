import './globals.css';
import type { Metadata } from 'next';
import { AppShell } from '../components/AppShell';

export const metadata: Metadata = {
  title: 'LabOS',
  description: 'Labor-Betriebssystem fuer Charges, Assets, Inventory, Labels, Sensoren, Aufgaben, Rollen und Wiki'
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="de">
      <body>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
