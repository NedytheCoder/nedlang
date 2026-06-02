export type Framework = "CEFR" | "HSK" | "JLPT" | "TOPIK"

export interface FrameworkInfo {
  id: Framework
  nameKey: string
  rangeKey: string
  descKey: string
  whyKey: string
  levels: string[]
  flag: string
  gradient: string
  accentColor: string
}

// Languages that use each framework
const HSK_LANGS = new Set(["zh", "zh-tw"])
const JLPT_LANGS = new Set(["ja"])
const TOPIK_LANGS = new Set(["ko"])

export function getFramework(targetLangCode: string): Framework {
  if (HSK_LANGS.has(targetLangCode)) return "HSK"
  if (JLPT_LANGS.has(targetLangCode)) return "JLPT"
  if (TOPIK_LANGS.has(targetLangCode)) return "TOPIK"
  return "CEFR"
}

export const FRAMEWORK_DATA: Record<Framework, FrameworkInfo> = {
  CEFR: {
    id: "CEFR",
    nameKey: "rec_framework_cefr_name",
    rangeKey: "rec_framework_cefr_range",
    descKey: "rec_framework_cefr_desc",
    whyKey: "rec_framework_cefr_why",
    levels: ["A1", "A2", "B1", "B2", "C1", "C2"],
    flag: "🇪🇺",
    gradient: "from-blue-500 to-indigo-600",
    accentColor: "indigo",
  },
  HSK: {
    id: "HSK",
    nameKey: "rec_framework_hsk_name",
    rangeKey: "rec_framework_hsk_range",
    descKey: "rec_framework_hsk_desc",
    whyKey: "rec_framework_hsk_why",
    levels: ["HSK1", "HSK2", "HSK3", "HSK4", "HSK5", "HSK6"],
    flag: "🇨🇳",
    gradient: "from-red-500 to-rose-600",
    accentColor: "rose",
  },
  JLPT: {
    id: "JLPT",
    nameKey: "rec_framework_jlpt_name",
    rangeKey: "rec_framework_jlpt_range",
    descKey: "rec_framework_jlpt_desc",
    whyKey: "rec_framework_jlpt_why",
    levels: ["N5", "N4", "N3", "N2", "N1"],
    flag: "🇯🇵",
    gradient: "from-rose-500 to-pink-600",
    accentColor: "pink",
  },
  TOPIK: {
    id: "TOPIK",
    nameKey: "rec_framework_topik_name",
    rangeKey: "rec_framework_topik_range",
    descKey: "rec_framework_topik_desc",
    whyKey: "rec_framework_topik_why",
    levels: ["Level 1", "Level 2", "Level 3", "Level 4", "Level 5", "Level 6"],
    flag: "🇰🇷",
    gradient: "from-blue-400 to-cyan-500",
    accentColor: "cyan",
  },
}
