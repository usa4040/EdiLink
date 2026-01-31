import { formatDate } from "../utils/date";

describe("formatDate", () => {
  it("correctly formats a valid date", () => {
    expect(formatDate("2024-03-15")).toBe("2024-03-15");
    expect(formatDate("2024-12-01")).toBe("2024-12-01");
    expect(formatDate("2023-06-30T00:00:00Z")).toMatch(/\d{4}-\d{2}-\d{2}/);
  });

  it('returns "-" for null input', () => {
    expect(formatDate(null)).toBe("-");
  });

  it("handles edge cases", () => {
    expect(formatDate("")).toBe("-");
    expect(formatDate(undefined as unknown as null)).toBe("-");
    expect(formatDate("invalid-date")).toBe("Invalid Date");
    expect(formatDate("0000-00-00")).toBe("Invalid Date");
  });
});
