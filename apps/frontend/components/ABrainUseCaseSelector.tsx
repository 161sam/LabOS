'use client';

import { ABrainReasoningMode, abrainReasoningModeOptions } from '../lib/lab-resources';

type ABrainUseCaseSelectorProps = {
  value: ABrainReasoningMode;
  onChange: (mode: ABrainReasoningMode) => void;
  disabled?: boolean;
};

export function ABrainUseCaseSelector({ value, onChange, disabled = false }: ABrainUseCaseSelectorProps) {
  return (
    <div className="useCaseSelector">
      {abrainReasoningModeOptions.map((option) => {
        const active = option.value === value;
        return (
          <button
            key={option.value}
            type="button"
            className={`button ${active ? '' : 'buttonSecondary'} buttonCompact useCaseTab`}
            onClick={() => onChange(option.value)}
            disabled={disabled}
            aria-pressed={active}
          >
            <span>{option.label}</span>
            <span className="muted useCaseTabDescription">{option.description}</span>
          </button>
        );
      })}
    </div>
  );
}
