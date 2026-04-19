export type InlineMessageTone = 'info' | 'success' | 'warning' | 'error';

export function InlineMessage({
  tone = 'info',
  children,
}: {
  tone?: InlineMessageTone;
  children: React.ReactNode;
}) {
  return <div className={`inlineMessage inlineMessage-${tone}`}>{children}</div>;
}
