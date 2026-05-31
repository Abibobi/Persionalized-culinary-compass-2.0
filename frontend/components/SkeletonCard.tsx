export default function SkeletonCard() {
  return (
    <div className="card overflow-hidden">
      <div className="h-1.5 w-full skeleton" />
      <div className="p-5 space-y-4">
        <div className="flex justify-between">
          <div className="space-y-2 flex-1">
            <div className="h-4 w-3/4 skeleton" />
            <div className="h-3 w-1/2 skeleton" />
          </div>
          <div className="h-6 w-12 skeleton rounded-full" />
        </div>
        <div className="h-3 w-full skeleton" />
        <div className="h-2 w-full skeleton rounded-full" />
        <div className="flex justify-between pt-2">
          <div className="h-3 w-20 skeleton" />
          <div className="flex gap-2">
            <div className="h-6 w-12 skeleton rounded-full" />
            <div className="h-6 w-12 skeleton rounded-full" />
          </div>
        </div>
      </div>
    </div>
  );
}
