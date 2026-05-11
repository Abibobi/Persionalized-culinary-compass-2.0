type WarningBadgeProps = {
  severity: "info" | "warning" | "danger";
  label?: string;
};

const config: Record<WarningBadgeProps["severity"], { className: string; icon: string }> = {
  info: { className: "badge-info", icon: "ℹ️" },
  warning: { className: "badge-warning", icon: "⚠️" },
  danger: { className: "badge-danger", icon: "🚫" },
};

export default function WarningBadge({ severity, label }: WarningBadgeProps) {
  const { className, icon } = config[severity];

  return (
    <span className={`badge ${className} gap-1`}>
      <span className="text-[10px]">{icon}</span>
      {label ?? severity}
    </span>
  );
}
