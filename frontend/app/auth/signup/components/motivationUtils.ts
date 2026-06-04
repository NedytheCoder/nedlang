export const CJK = /[一-鿿぀-ゟ゠-ヿ가-힯]/

export const MOTIVATION_KEY_MAP: Record<string, string> = {
  "Career growth":                     "onb_motiv_ex_career",
  "Travel":                            "onb_motiv_ex_travel",
  "Relocating abroad":                 "onb_motiv_ex_reloc",
  "University studies":                "onb_motiv_ex_study",
  "Business communication":            "onb_motiv_ex_biz",
  "Watching movies without subtitles": "onb_motiv_ex_movies",
  "Speaking with family":              "onb_motiv_ex_family",
  "Personal interest":                 "onb_motiv_ex_personal",
}

export function isMotivationValid(text: string): boolean {
  const trimmed = text.trim()
  if (!trimmed) return false
  if (CJK.test(trimmed)) return trimmed.length >= 5
  return trimmed.split(/\s+/).filter(Boolean).length >= 3
}
