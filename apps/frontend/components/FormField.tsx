export function FormField({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <label className="formField">
      <span className="formLabel">{label}</span>
      {children}
    </label>
  );
}
