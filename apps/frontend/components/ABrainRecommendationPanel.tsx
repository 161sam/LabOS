'use client';

import Link from 'next/link';

import { ABrainActionRiskLevel, ABrainAdapterRecommendedAction } from '../lib/lab-resources';
import { InlineMessage } from './InlineMessage';

const riskTone: Record<ABrainActionRiskLevel, 'info' | 'warning' | 'error'> = {
  low: 'info',
  medium: 'warning',
  high: 'error',
  critical: 'error',
};

type RecommendationTone = 'recommend' | 'approval' | 'blocked';

type ABrainRecommendationPanelProps = {
  title: string;
  tone: RecommendationTone;
  items: ABrainAdapterRecommendedAction[];
  empty: string;
  onExecute?: (action: ABrainAdapterRecommendedAction) => void;
  executingAction?: string | null;
};

export function ABrainRecommendationPanel({
  title,
  tone,
  items,
  empty,
  onExecute,
  executingAction,
}: ABrainRecommendationPanelProps) {
  if (items.length === 0) {
    return (
      <div className="stackCompact">
        <strong>{title}</strong>
        <InlineMessage tone={tone === 'blocked' ? 'error' : undefined}>{empty}</InlineMessage>
      </div>
    );
  }
  return (
    <div className="stackCompact">
      <strong>{title}</strong>
      <ul className="recommendationList">
        {items.map((item, index) => {
          const key = `${item.action}-${index}`;
          const canExecute = tone !== 'blocked' && !item.blocked && Boolean(onExecute);
          const isExecuting = executingAction === key;
          return (
            <li key={key} className="recommendationItem">
              <div className="recommendationHeader">
                <strong>{item.action}</strong>
                {item.target ? <span className="muted"> → {item.target}</span> : null}
                <span className={`badge badge-${riskTone[item.risk_level]}`}>{item.risk_level}</span>
                {tone === 'approval' || item.requires_approval ? (
                  <span className="badge badge-warning">approval</span>
                ) : null}
                {item.blocked ? (
                  <span className="badge badge-error">
                    blocked{item.blocked_reason ? `: ${item.blocked_reason}` : ''}
                  </span>
                ) : null}
              </div>
              {item.reason ? <div className="muted">{item.reason}</div> : null}
              <div className="recommendationActions">
                {canExecute ? (
                  <button
                    type="button"
                    className="button buttonCompact"
                    onClick={() => onExecute?.(item)}
                    disabled={isExecuting}
                  >
                    {isExecuting ? 'Ausfuehrung…' : tone === 'approval' ? 'Approval anfragen' : 'Ausfuehren'}
                  </button>
                ) : null}
                <Link href="/approvals" className="buttonSecondary buttonCompact button">
                  Approvals
                </Link>
                <Link href="/executions" className="buttonSecondary buttonCompact button">
                  Executions
                </Link>
                <Link href="/traces" className="buttonSecondary buttonCompact button">
                  Traces
                </Link>
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
