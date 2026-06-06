export const fmtInt = (n: number): string => n.toLocaleString('en-US')
export const fmtPct = (n: number, digits = 0): string => `${n.toFixed(digits)}%`
