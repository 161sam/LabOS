import type { CSSProperties, ReactNode } from 'react';

export function Card({
  title,
  children,
  style,
}: {
  title?: string;
  children: ReactNode;
  style?: CSSProperties;
}) {
  return (
    <section className="card" style={style}>
      {title ? <h3>{title}</h3> : null}
      {children}
    </section>
  );
}
