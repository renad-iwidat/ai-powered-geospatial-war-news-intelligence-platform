'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useTranslations } from 'next-intl';
import {
  AnalyticsSection,
  LanguageSwitcher,
  LiveStream,
  MapSection,
  MetricsOverview,
  NewsSidebar,
  PredictionsSection,
} from '@/components/dashboard';
import { Radio, Shield } from 'lucide-react';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function DashboardContent() {
  const t = useTranslations('app');

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Header */}
      <header className="border-b border-red-900/20 bg-slate-900/80 backdrop-blur-sm sticky top-0 z-50 shadow-lg shadow-red-900/10">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="relative p-2 bg-red-500/10 rounded-lg border border-red-500/20">
                <Shield className="h-7 w-7 text-red-500" />
                <Radio className="h-3 w-3 text-red-500 absolute -top-1 -right-1 animate-pulse" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white tracking-tight">{t('title')}</h1>
                <p className="text-xs text-red-400 flex items-center gap-1.5 mt-0.5">
                  <span className="inline-block w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
                  {t('subtitle')}
                </p>
              </div>
            </div>
            <LanguageSwitcher />
          </div>
        </div>
      </header>

      {/* Main Dashboard */}
      <main className="container mx-auto px-4 py-6 space-y-6">
        {/* Primary Intelligence Grid: Live Stream + Map */}
        <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Live News Stream */}
          <div className="h-[500px]">
            <LiveStream />
          </div>

          {/* Interactive Map */}
          <div className="h-[500px]">
            <MapSection />
          </div>
        </section>

        {/* Secondary Grid: News Feed + AI Predictions */}
        <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Breaking News Feed */}
          <div className="max-h-[600px]">
            <NewsSidebar />
          </div>

          {/* AI Predictions & Forecasts */}
          <div className="max-h-[600px] overflow-y-auto">
            <PredictionsSection />
          </div>
        </section>

        {/* Analytics & Statistics - Full Width */}
        <section>
          <AnalyticsSection />
        </section>

        {/* Bottom Section: Metrics Overview */}
        <section>
          <MetricsOverview />
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 bg-gradient-to-b from-slate-900/80 to-slate-950 backdrop-blur-sm mt-16">
        <div className="container mx-auto px-4 py-12">
          {/* About Section */}
          <div className="mb-10">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 bg-red-500/10 rounded-lg border border-red-500/20">
                <Shield className="h-5 w-5 text-red-500" />
              </div>
              <h2 className="text-lg font-bold text-white">{t('title')}</h2>
            </div>
            <p className="text-sm text-slate-300 leading-relaxed max-w-4xl">
              تم إنشاء هذا الموقع بالتعاون بين <span className="text-red-400 font-semibold">وحدة ليمينال (Liminal)</span> للحلول الرقمية الذكية و <span className="text-red-400 font-semibold">مركز الذكاء الاصطناعي</span> في <span className="text-red-400 font-semibold">جامعة النجاح الوطنية</span>، بهدف تطوير منصة رقمية تعتمد على تقنيات الذكاء الاصطناعي لجمع وتحليل وعرض المعلومات بشكل تفاعلي.
            </p>
          </div>

          {/* Divider */}
          <div className="border-t border-slate-700/50 my-8"></div>

          {/* Disclaimer Section */}
          <div className="mb-10">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-1 h-6 bg-red-500 rounded-full"></div>
              <h3 className="text-sm font-bold text-red-400 uppercase tracking-wider">إخلاء مسؤولية</h3>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed max-w-4xl">
              تعتمد المعلومات المعروضة في هذا الموقع جزئياً على تقنيات الذكاء الاصطناعي في جمع البيانات وتحليلها من مصادر متعددة. ولذلك فإن <span className="text-slate-300 font-semibold">جامعة النجاح الوطنية</span> و <span className="text-slate-300 font-semibold">مركز الذكاء الاصطناعي</span> و <span className="text-slate-300 font-semibold">وحدة ليمينال (Liminal)</span> للحلول الرقمية الذكية <span className="text-red-400">لا يتحملون أي مسؤولية</span> عن دقة أو اكتمال هذه المعلومات، وهي معروضة لأغراض إعلامية و تحليلية عامة فقط.
            </p>
          </div>

          {/* Divider */}
          <div className="border-t border-slate-700/50 my-8"></div>

          {/* Bottom Footer */}
          <div className="flex flex-col md:flex-row items-center justify-between gap-4 text-xs text-slate-500">
            <div className="flex items-center gap-2">
              <span className="inline-block w-2 h-2 bg-red-500 rounded-full"></span>
              <span>© 2026 GeoNews AI Platform</span>
            </div>
            <div className="text-center md:text-right">
              <p>جيونيوز AI - منصة الاستخبارات الجغرافية</p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default function Home() {
  return (
    <QueryClientProvider client={queryClient}>
      <DashboardContent />
    </QueryClientProvider>
  );
}
