import common from "./common"
import landing from "./landing"
import auth from "./auth"
import onboarding from "./onboarding"
import dashboard from "./dashboard"
import reception from "./reception"

const LANGS = ["en", "fr", "de", "zh"] as const

const translations: Record<string, Record<string, string>> = {}

for (const lang of LANGS) {
  translations[lang] = {
    ...landing[lang],
    ...auth[lang],
    ...onboarding[lang],
    ...dashboard[lang],
    ...reception[lang],
    ...common[lang],
  }
}

export default translations
