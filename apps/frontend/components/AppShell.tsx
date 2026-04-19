'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useEffect } from 'react';

import { UserRole } from '../lib/lab-resources';
import { AuthProvider, useAuth } from './AuthProvider';
import { Card } from './Card';

const navItems: Array<{
  label: string;
  href: string;
  roles?: UserRole[];
}> = [
  { label: 'Dashboard', href: '/' },
  { label: 'Chargen', href: '/charges' },
  { label: 'Reaktoren', href: '/reactors' },
  { label: 'ReactorOps', href: '/reactor-ops' },
  { label: 'ReactorControl', href: '/reactor-control' },
  { label: 'Assets', href: '/assets' },
  { label: 'Inventory', href: '/inventory' },
  { label: 'Labels', href: '/labels' },
  { label: 'Sensoren', href: '/sensors' },
  { label: 'Fotos', href: '/photos' },
  { label: 'Aufgaben', href: '/tasks' },
  { label: 'Alerts', href: '/alerts' },
  { label: 'Safety', href: '/safety' },
  { label: 'Automation', href: '/rules' },
  { label: 'Scheduler', href: '/schedules' },
  { label: 'Wiki', href: '/wiki' },
  { label: 'ABrain', href: '/abrain' },
  { label: 'Benutzer', href: '/users', roles: ['admin'] },
];

function getRoleLabel(role: UserRole) {
  if (role === 'admin') {
    return 'Admin';
  }
  if (role === 'operator') {
    return 'Operator';
  }
  return 'Viewer';
}

function isActivePath(currentPath: string, targetPath: string) {
  if (targetPath === '/') {
    return currentPath === '/';
  }
  return currentPath === targetPath || currentPath.startsWith(`${targetPath}/`);
}

function AppShellContent({ children }: { children: React.ReactNode }) {
  const pathname = usePathname() ?? '/';
  const router = useRouter();
  const { status, user, logout } = useAuth();
  const isLoginRoute = pathname === '/login';
  const isAdminRoute = pathname === '/users' || pathname.startsWith('/users/');

  useEffect(() => {
    if (status === 'unauthenticated' && !isLoginRoute) {
      router.replace(`/login?next=${encodeURIComponent(pathname)}`);
    }
  }, [isLoginRoute, pathname, router, status]);

  useEffect(() => {
    if (status === 'authenticated' && user && isAdminRoute && user.role !== 'admin') {
      router.replace('/');
    }
  }, [isAdminRoute, router, status, user]);

  if (isLoginRoute) {
    return <div className="authPage">{children}</div>;
  }

  if (status === 'loading') {
    return (
      <div className="authPage">
        <Card title="Session wird geladen">
          <p className="muted">LabOS prueft gerade die lokale Anmeldung und Rollenberechtigung.</p>
        </Card>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="authPage">
        <Card title="Weiterleitung zum Login">
          <p className="muted">Geschuetzte LabOS-Bereiche werden ueber die lokale Session abgesichert.</p>
        </Card>
      </div>
    );
  }

  const visibleNavItems = navItems.filter((item) => !item.roles || item.roles.includes(user.role));

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="stackBlock">
          <div>
            <div className="brand">LabOS</div>
            <div className="muted">Auth / Rollen V1</div>
          </div>

          <div className="card sidebarCard">
            <div className="stackCompact">
              <strong>{user.display_name || user.username}</strong>
              <span className="muted">{user.username}</span>
            </div>
            <div className="buttonRow">
              <span className={`badge badge-${user.role}`}>{getRoleLabel(user.role)}</span>
              <span className={`badge badge-${user.is_active ? 'active' : 'inactive'}`}>
                {user.is_active ? 'aktiv' : 'inaktiv'}
              </span>
            </div>
            <button
              className="button buttonSecondary"
              type="button"
              onClick={() => {
                void logout().then(() => router.replace('/login'));
              }}
            >
              Logout
            </button>
          </div>
        </div>

        <nav>
          {visibleNavItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`navLink ${isActivePath(pathname, item.href) ? 'navLinkActive' : ''}`}
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </aside>

      <main className="content">{children}</main>
    </div>
  );
}

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <AppShellContent>{children}</AppShellContent>
    </AuthProvider>
  );
}
