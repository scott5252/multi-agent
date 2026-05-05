import type { UsageReactFilterOption, UsageReactGroupBy } from "../../api/generated/reactAdminApi";

interface UsageGroupSelectorProps {
  options: UsageReactFilterOption[];
  value: UsageReactGroupBy;
  onChange: (value: UsageReactGroupBy) => void;
}

export function UsageGroupSelector({ options, value, onChange }: UsageGroupSelectorProps) {
  return (
    <label className="usage-field">
      <span>Group by</span>
      <select
        value={value}
        onChange={(event) => onChange(event.target.value as UsageReactGroupBy)}
      >
        {options.map((option) => (
          <option disabled={option.disabled} key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </label>
  );
}
