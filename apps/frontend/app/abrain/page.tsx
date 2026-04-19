import { ABrainAdapterConsole } from '../../components/ABrainAdapterConsole';
import { ABrainAssistant } from '../../components/ABrainAssistant';

export default function ABrainPage() {
  return (
    <div className="grid" style={{ gap: 32 }}>
      <ABrainAdapterConsole />
      <ABrainAssistant />
    </div>
  );
}
