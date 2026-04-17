import './globals.css';
import type { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'LabOS',
  description: 'Labor-Betriebssystem für Chargen, Reaktoren, Sensoren und Wiki'
};

const navItems = [
  ['Dashboard', '/'],
  ['Chargen', '/charges'],
  ['Reaktoren', '/reactors'],
  ['Sensoren', '/sensors'],
  ['Fotos', '/photos'],
  ['Aufgaben', '/tasks'],
  ['Alerts', '/alerts'],
  ['Wiki', '/wiki'],
  ['ABrain', '/abrain']
] as const;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="de">
      <body>
        <div className="shell">
          <aside className="sidebar">
            <div>
              <div className="brand">LabOS</div>
              <div className="muted">V1 Operations</div>
            </div>
            <nav>
              {navItems.map(([label, href]) => (
                <Link key={href} href={href} className="navLink">
                  {label}
                </Link>
              ))}
            </nav>
          </aside>
          <main className="content">{children}</main>
        </div>
      </body>
    </html>
  );
}
