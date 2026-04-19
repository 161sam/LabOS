import type { CSSProperties, ReactNode } from 'react';

export function FormField({
  label,
  children,
  style,
}: {
  label: string;
  children: ReactNode;
  style?: CSSProperties;
}) {
  return (
    <label className="formField" style={style}>
      <span className="formLabel">{label}</span>
      {children}
    </label>
  );
}
