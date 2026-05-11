type NutritionBarProps = {
  protein: number;
  carbs: number;
  fat: number;
  showLabels?: boolean;
};

export default function NutritionBar({ protein, carbs, fat, showLabels = false }: NutritionBarProps) {
  const total = protein + carbs + fat || 1;
  const proteinPct = (protein / total) * 100;
  const carbsPct = (carbs / total) * 100;
  const fatPct = (fat / total) * 100;

  return (
    <div>
      <div className="nutrition-track">
        <span
          className="nutrition-segment"
          style={{ width: `${proteinPct}%`, background: "#e85d04" }}
          title={`Protein: ${protein}g`}
        />
        <span
          className="nutrition-segment"
          style={{ width: `${carbsPct}%`, background: "#f59e0b" }}
          title={`Carbs: ${carbs}g`}
        />
        <span
          className="nutrition-segment"
          style={{ width: `${fatPct}%`, background: "#a16207" }}
          title={`Fat: ${fat}g`}
        />
      </div>
      {showLabels && (
        <div className="mt-2 flex gap-4 text-xs text-muted">
          <span className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full" style={{ background: "#e85d04" }} />
            Protein {protein}g
          </span>
          <span className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full" style={{ background: "#f59e0b" }} />
            Carbs {carbs}g
          </span>
          <span className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full" style={{ background: "#a16207" }} />
            Fat {fat}g
          </span>
        </div>
      )}
    </div>
  );
}
