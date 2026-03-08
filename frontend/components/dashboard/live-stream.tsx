'use client';

import { useTranslations, useLocale } from 'next-intl';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Radio, Tv } from 'lucide-react';

export function LiveStream() {
  const t = useTranslations('liveStream');
  const locale = useLocale();

  return (
    <Card className="h-full bg-slate-800/50 border-slate-700 backdrop-blur-sm overflow-hidden">
      <CardHeader className="pb-3 border-b border-slate-700">
        <CardTitle className="flex items-center gap-2 text-lg text-white">
          <div className="relative">
            <Tv className="h-5 w-5 text-red-500" />
            <Radio className="h-3 w-3 text-red-500 absolute -top-1 -right-1 animate-pulse" />
          </div>
          {t('title')}
          <span className="flex items-center gap-1 text-xs font-normal text-red-400 ml-auto">
            <span className="inline-block w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
            {t('live')}
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <div className="relative w-full" style={{ paddingBottom: '56.25%' }}>
          <iframe
            className="absolute top-0 left-0 w-full h-full"
            src="https://www.youtube.com/embed/live_stream_id?autoplay=1&mute=1&controls=1&modestbranding=1&rel=0"
            title={locale === 'ar' ? 'البث المباشر - الشرق' : 'Live Stream - Al Sharq'}
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
            style={{
              border: 'none',
              background: '#000'
            }}
          />
        </div>
        <div className="p-3 bg-slate-900/50 border-t border-slate-700">
          <p className="text-xs text-slate-400 text-center">
            {locale === 'ar' 
              ? '📡 البث المباشر من قناة الشرق - تغطية مستمرة للأحداث'
              : '📡 Live from Al Sharq - Continuous Event Coverage'
            }
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
