# i18n (Internationalization) System

This document explains the lightweight translation system implemented for the FrenchCoach landing page.

## Overview

The i18n system provides:
- **Lightweight**: No heavy libraries (no i18n-js, react-intl, etc.)
- **Client-side**: Dynamic language switching without page refresh
- **Persistent**: Language selection saved to `localStorage`
- **Fallback**: Default to English if not found
- **Scoped**: Currently limited to landing page and shared layout

## Architecture

### Core Files

1. **`frontend/i18n/translations.ts`**
   - Central dictionary containing all UI strings for `en`, `fr`, `de`, `zh`
   - Structure: `Record<string, Record<string, string>>`
   - Export: `default` (translations object)

2. **`frontend/i18n/LanguageProvider.tsx`**
   - React Context provider for client-side translation
   - Hook: `useTranslation()` returns `{ t, lang, setLang }`
   - `t(key)`: Lookup function with fallback to English
   - `lang`: Current language code
   - `setLang(value)`: Update language and persist to localStorage
   - Storage key: `fc_ui_lang`

3. **`frontend/app/layout.tsx`**
   - Wraps app in `<LanguageProvider>` for layout + children

4. **`frontend/app/page.tsx`**
   - Landing page consuming translations via `useTranslation()`
   - Language selector in navbar with flag emojis
   - All user-facing strings use `t("key_name")`

## Usage

### In a Component

```tsx
import { useTranslation } from "../i18n/LanguageProvider"

function MyComponent() {
  const { t, lang, setLang } = useTranslation()

  return (
    <div>
      <p>{t("nav_your_journey")}</p>
      <select value={lang} onChange={(e) => setLang(e.target.value as any)}>
        <option value="en">{t("lang_en")}</option>
        <option value="fr">{t("lang_fr")}</option>
      </select>
    </div>
  )
}
```

### Adding a New Translation

1. Open `frontend/i18n/translations.ts`
2. Add the key to all four language sections:
   ```typescript
   en: {
     my_new_key: "English text",
   },
   fr: {
     my_new_key: "Texte français",
   },
   // ... de, zh
   ```
3. Use it in a component: `{t("my_new_key")}`

## Supported Languages

| Code | Language | Locale |
|------|----------|--------|
| `en` | English | 🇬🇧 |
| `fr` | Français | 🇫🇷 |
| `de` | Deutsch | 🇩🇪 |
| `zh` | 中文 | 🇨🇳 |

## Language Selector UI

The language selector in the navbar displays:
- Flag emoji (e.g., 🇬🇧 English, 🇫🇷 Français)
- Localized language name from translations
- Smooth transition with hover effects
- Persists selection on reload

```tsx
<select value={lang} onChange={(e) => setLang(e.target.value as any)}>
  <option value="en">🇬🇧 {t("lang_en")}</option>
  <option value="fr">🇫🇷 {t("lang_fr")}</option>
  <option value="de">🇩🇪 {t("lang_de")}</option>
  <option value="zh">🇨🇳 {t("lang_zh")}</option>
</select>
```

## Persistence

Language is stored in `localStorage` under the key `fc_ui_lang`:

```typescript
// Get current language
const lang = localStorage.getItem("fc_ui_lang") || "en"

// Set language
localStorage.setItem("fc_ui_lang", "fr")
```

### Fallback Logic

On `LanguageProvider` mount:
1. Try to read from `localStorage.fc_ui_lang`
2. If not found, try `navigator.language` for `fr`, `de`, `zh`
3. Default to `en`

## Testing

Run tests to validate translations:

```bash
npm test -- __tests__/translations.test.ts
npm test -- __tests__/LanguageProvider.test.tsx
```

### What Tests Validate

- ✅ All languages exist
- ✅ All required keys exist in all languages
- ✅ Translations are not empty
- ✅ Translations are unique per language
- ✅ Language names are localized
- ✅ No placeholder/untranslated strings

## Key Translation Categories

### Navigation (`nav_*`)
- `nav_your_journey`
- `nav_skills`
- `nav_how_to_play`
- `nav_start_journey`

### Hero Section (`hero_*`)
- `hero_begin_your`
- `hero_highlight`
- `hero_adventure`
- `hero_subtitle`

### Learning Path (`level_*`)
- `level_A0` through `level_C2`

### Features (`feature_*`)
- Speaking, Listening, Reading, Writing titles and descriptions

### Testimonials (`testimonial_*`)
- `testimonial_sarah_quote`, `testimonial_james_quote`, `testimonial_emma_quote`
- Names, levels, XP, badges in each language

### Language Names (`lang_*`)
- `lang_en`, `lang_fr`, `lang_de`, `lang_zh`

### CTA & Misc
- `cta_begin_adventure`
- `free_forever`
- `footer_*` entries

## Performance Considerations

- **Bundle Size**: Translations object ~25KB (gzipped ~5KB)
- **Runtime**: O(1) lookup via object key access
- **No Network Calls**: All translations bundled at build time
- **Client-Side**: No server round-trip for language switching

## Known Limitations

- **SSR/Hydration**: No server-side rendering of localized content
- **Date/Number Formatting**: Not handled (would require additional library)
- **Pluralization**: Not handled (would require additional logic)
- **RTL Languages**: Not supported (layout assumes LTR)
- **Scope**: Only landing page + shared layout

## Future Enhancements

1. **Server-Side Rendering**: Localize `<html lang>` attribute and meta tags
2. **Pluralization**: Add plural form support
3. **Date/Number Formatting**: Add locale-aware formatting
4. **Dynamic Loading**: Load translations from API for easy updates
5. **Fallback Chain**: Support multiple fallback languages
6. **Missing Key Handling**: Log warnings for undefined keys
7. **Interpolation**: Support `{name}` style variable substitution

## Migration Path

If you need a full-featured i18n solution later:

1. **Option 1 (Recommended)**: Migrate to `next-intl` for Next.js app router
   - Server-side rendering support
   - More advanced features
   - Better SEO

2. **Option 2**: Migrate to `i18next` for more flexibility
   - Larger ecosystem
   - More plugins

To migrate, map your current `translations.ts` keys to the target library's format.

## Related Files

- [LanguageProvider Implementation](./LanguageProvider.tsx)
- [Translations Dictionary](./translations.ts)
- [Landing Page Usage](../app/page.tsx)
- [Tests](../__tests__/translations.test.ts)
