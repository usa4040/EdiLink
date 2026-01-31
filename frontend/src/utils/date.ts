export function formatDate(dateString: string | null): string {
  if (!dateString) return "-";
  const date = new Date(dateString);
  return date
    .toLocaleDateString("ja-JP", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
    })
    .replace(/\//g, "-");
}
