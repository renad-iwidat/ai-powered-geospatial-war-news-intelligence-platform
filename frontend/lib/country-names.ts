/**
 * Country Code to Full Name Mapping
 * ISO 3166-1 alpha-2 codes
 */

export const countryNames: Record<string, { en: string; ar: string }> = {
  // Middle East
  PS: { en: 'Palestine', ar: 'فلسطين' },
  IL: { en: 'Israel', ar: 'إسرائيل' },
  LB: { en: 'Lebanon', ar: 'لبنان' },
  SY: { en: 'Syria', ar: 'سوريا' },
  JO: { en: 'Jordan', ar: 'الأردن' },
  IQ: { en: 'Iraq', ar: 'العراق' },
  SA: { en: 'Saudi Arabia', ar: 'السعودية' },
  AE: { en: 'United Arab Emirates', ar: 'الإمارات' },
  YE: { en: 'Yemen', ar: 'اليمن' },
  OM: { en: 'Oman', ar: 'عمان' },
  KW: { en: 'Kuwait', ar: 'الكويت' },
  QA: { en: 'Qatar', ar: 'قطر' },
  BH: { en: 'Bahrain', ar: 'البحرين' },
  TR: { en: 'Turkey', ar: 'تركيا' },
  IR: { en: 'Iran', ar: 'إيران' },
  EG: { en: 'Egypt', ar: 'مصر' },
  
  // North Africa
  LY: { en: 'Libya', ar: 'ليبيا' },
  TN: { en: 'Tunisia', ar: 'تونس' },
  DZ: { en: 'Algeria', ar: 'الجزائر' },
  MA: { en: 'Morocco', ar: 'المغرب' },
  SD: { en: 'Sudan', ar: 'السودان' },
  
  // Europe
  UA: { en: 'Ukraine', ar: 'أوكرانيا' },
  RU: { en: 'Russia', ar: 'روسيا' },
  FR: { en: 'France', ar: 'فرنسا' },
  DE: { en: 'Germany', ar: 'ألمانيا' },
  GB: { en: 'United Kingdom', ar: 'بريطانيا' },
  IT: { en: 'Italy', ar: 'إيطاليا' },
  ES: { en: 'Spain', ar: 'إسبانيا' },
  
  // Americas
  US: { en: 'United States', ar: 'الولايات المتحدة' },
  CA: { en: 'Canada', ar: 'كندا' },
  MX: { en: 'Mexico', ar: 'المكسيك' },
  BR: { en: 'Brazil', ar: 'البرازيل' },
  
  // Asia
  CN: { en: 'China', ar: 'الصين' },
  JP: { en: 'Japan', ar: 'اليابان' },
  KR: { en: 'South Korea', ar: 'كوريا الجنوبية' },
  IN: { en: 'India', ar: 'الهند' },
  PK: { en: 'Pakistan', ar: 'باكستان' },
  AF: { en: 'Afghanistan', ar: 'أفغانستان' },
  
  // Africa
  SO: { en: 'Somalia', ar: 'الصومال' },
  ET: { en: 'Ethiopia', ar: 'إثيوبيا' },
  KE: { en: 'Kenya', ar: 'كينيا' },
  NG: { en: 'Nigeria', ar: 'نيجيريا' },
  ZA: { en: 'South Africa', ar: 'جنوب أفريقيا' },
};

/**
 * Get country full name by code and locale
 */
export function getCountryName(code: string, locale: 'en' | 'ar' = 'en'): string {
  const country = countryNames[code.toUpperCase()];
  if (country) {
    return country[locale];
  }
  // Return code if not found
  return code;
}

/**
 * Get all country names for a locale
 */
export function getAllCountryNames(locale: 'en' | 'ar' = 'en'): Record<string, string> {
  const result: Record<string, string> = {};
  Object.entries(countryNames).forEach(([code, names]) => {
    result[code] = names[locale];
  });
  return result;
}
