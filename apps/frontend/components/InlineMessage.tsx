export function InlineMessage({
  tone = 'info',
  children,
}: {
  tone?: 'info' | 'success' | 'error';
  children: React.ReactNode;
}) {
  return <div className={`inlineMessage inlineMessage-${tone}`}>{children}</div>;
}
