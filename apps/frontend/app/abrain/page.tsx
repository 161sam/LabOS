import { ABrainAdapterConsole } from '../../components/ABrainAdapterConsole';
import { ABrainAssistant } from '../../components/ABrainAssistant';
import { ABrainDecisionSurface } from '../../components/ABrainDecisionSurface';
import { abrainReasoningModeOptions, ABrainReasoningMode } from '../../lib/lab-resources';

type ABrainPageProps = {
  searchParams?: { mode?: string };
};

function resolveInitialMode(raw: string | undefined): ABrainReasoningMode | undefined {
  if (!raw) {
    return undefined;
  }
  const match = abrainReasoningModeOptions.find((option) => option.value === raw);
  return match?.value;
}

export default function ABrainPage({ searchParams }: ABrainPageProps) {
  const initialMode = resolveInitialMode(searchParams?.mode);
  return (
    <div className="grid" style={{ gap: 32 }}>
      <ABrainDecisionSurface initialMode={initialMode} />
      <details>
        <summary>Adapter Console (V1)</summary>
        <div style={{ marginTop: 16 }}>
          <ABrainAdapterConsole />
        </div>
      </details>
      <details>
        <summary>ABrain Assistant (V1 Legacy)</summary>
        <div style={{ marginTop: 16 }}>
          <ABrainAssistant />
        </div>
      </details>
    </div>
  );
}
