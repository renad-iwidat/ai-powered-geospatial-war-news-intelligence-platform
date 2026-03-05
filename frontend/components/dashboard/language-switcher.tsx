'use client';

import { useLocale, useTranslations } from 'next-intl';
import { usePathname, useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Languages } from 'lucide-react';

export function LanguageSwitcher() {
  const t = useTranslations('language');
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();

  const switchLanguage = () => {
    const newLocale = locale === 'en' ? 'ar' : 'en';
    const newPath = pathname.replace(`/${locale}`, `/${newLocale}`);
    router.push(newPath);
  };

  return (
    <Button
      variant="outline"
      size="sm"
      onClick={switchLanguage}
      className="gap-2 bg-slate-800 border-slate-700 text-white hover:bg-slate-700 hover:text-white"
    >
      <Languages className="h-4 w-4" />
      {t('switch')}
    </Button>
  );
}
