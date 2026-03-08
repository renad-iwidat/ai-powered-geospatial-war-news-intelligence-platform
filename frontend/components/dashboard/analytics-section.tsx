'use client';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart3, Globe, TrendingUp, MapPin, DollarSign } from 'lucide-react';
import { useLocale } from 'next-intl';
import { getCountryName } from '@/lib/country-names';
import {
  fetchCountryStatistics,
  fetchDateStatistics,
  fetchTopMetricsByCountry,
  fetchHotLocations,
  fetchMarketData,
} from '@/lib/api-services';
import type { DateStatistics } from '@/types';

export function AnalyticsSection() {
  const locale = useLocale() as 'en' | 'ar';

  const { data: countries } = useQuery({
    queryKey: ['country-stats'],
    queryFn: fetchCountryStatistics,
  });

  const { data: timeline } = useQuery({
    queryKey: ['date-stats'],
    queryFn: () => fetchDateStatistics(14),
  });

  const { data: metrics } = useQuery({
    queryKey: ['metrics-by-country'],
    queryFn: () => fetchTopMetricsByCountry(10), // Get more to filter duplicates
  });

  const { data: hotspots } = useQuery({
    queryKey: ['hot-locations'],
    queryFn: () => fetchHotLocations(50), // Fetch more to ensure all priority countries
  });

  const { data: marketData } = useQuery({
    queryKey: ['market-data'],
    queryFn: fetchMarketData,
    refetchInterval: 300000, // Refresh every 5 minutes
  });

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      {/* Market Data - Oil & Gold */}
      <Card className="bg-slate-800/50 border-slate-700 backdrop-blur-sm lg:col-span-2">
        <CardHeader className="pb-3 border-b border-slate-700">
          <CardTitle className="flex items-center gap-2 text-base text-white">
            <DollarSign className="h-4 w-4 text-yellow-500" />
            {locale === 'ar' ? 'أسعار النفط والذهب' : 'Oil & Gold Prices'}
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-4">
          {marketData ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Oil Price */}
              <div className="space-y-4">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="text-xs text-slate-400 uppercase mb-1">
                      {locale === 'ar' ? 'نفط خام WTI' : 'WTI Crude Oil'}
                    </div>
                    <div className="text-4xl font-bold text-orange-400">
                      ${marketData.oil.current?.price.toFixed(2)}
                    </div>
                    <div className="text-xs text-slate-500 mt-1">{marketData.oil.unit}</div>
                  </div>
                  <div className={`text-right px-4 py-2 rounded-lg ${
                    marketData.oil.change_7d && marketData.oil.change_7d > 0 
                      ? 'bg-green-500/20' 
                      : 'bg-red-500/20'
                  }`}>
                    <div className={`text-2xl font-bold ${
                      marketData.oil.change_7d && marketData.oil.change_7d > 0 
                        ? 'text-green-400' 
                        : 'text-red-400'
                    }`}>
                      {marketData.oil.change_7d ? `${marketData.oil.change_7d > 0 ? '↑' : '↓'} ${Math.abs(marketData.oil.change_7d).toFixed(1)}%` : 'N/A'}
                    </div>
                    <div className="text-xs text-slate-400 mt-1">
                      {locale === 'ar' ? '7 أيام' : '7 days'}
                    </div>
                  </div>
                </div>
                
                {/* Oil Trend Chart */}
                {marketData.oil.trend.length > 0 && (
                  <div className="bg-slate-700/30 p-4 rounded-lg border border-slate-600">
                    <div className="text-xs text-slate-400 mb-3 font-medium">
                      {locale === 'ar' ? 'اتجاه السعر (7 أيام)' : 'Price Trend (7 Days)'}
                    </div>
                    <div className="relative" style={{ height: '160px' }}>
                      <svg className="w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
                        <defs>
                          {/* Gradient for area fill */}
                          <linearGradient id="areaGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                            <stop offset="0%" stopColor={marketData.oil.change_7d && marketData.oil.change_7d > 0 ? "#4ade80" : "#f87171"} stopOpacity="0.3" />
                            <stop offset="100%" stopColor={marketData.oil.change_7d && marketData.oil.change_7d > 0 ? "#4ade80" : "#f87171"} stopOpacity="0.05" />
                          </linearGradient>
                        </defs>
                        
                        {/* Grid lines */}
                        <line x1="0" y1="25" x2="100" y2="25" stroke="#475569" strokeWidth="0.2" opacity="0.5" />
                        <line x1="0" y1="50" x2="100" y2="50" stroke="#475569" strokeWidth="0.2" opacity="0.5" />
                        <line x1="0" y1="75" x2="100" y2="75" stroke="#475569" strokeWidth="0.2" opacity="0.5" />
                        
                        {(() => {
                          const prices = marketData.oil.trend; // Don't reverse - keep original order
                          const maxPrice = Math.max(...prices.map(p => p.price));
                          const minPrice = Math.min(...prices.map(p => p.price));
                          const range = maxPrice - minPrice || 1;
                          
                          // Create smooth path points - reversed for RTL display
                          const points = prices.slice().reverse().map((point, idx) => {
                            const x = (idx / (prices.length - 1)) * 100;
                            const y = 100 - ((point.price - minPrice) / range) * 80 - 10; // 10% padding top/bottom
                            return { x, y, price: point.price, date: point.date };
                          });
                          
                          // Create smooth curve path using quadratic bezier
                          let pathD = `M ${points[0].x} ${points[0].y}`;
                          for (let i = 0; i < points.length - 1; i++) {
                            const current = points[i];
                            const next = points[i + 1];
                            const midX = (current.x + next.x) / 2;
                            pathD += ` Q ${current.x} ${current.y}, ${midX} ${(current.y + next.y) / 2}`;
                            if (i === points.length - 2) {
                              pathD += ` Q ${next.x} ${next.y}, ${next.x} ${next.y}`;
                            }
                          }
                          
                          // Area path (same as line but closed to bottom)
                          const areaPath = pathD + ` L ${points[points.length - 1].x} 100 L ${points[0].x} 100 Z`;
                          
                          return (
                            <>
                              {/* Area fill */}
                              <path
                                d={areaPath}
                                fill="url(#areaGradient)"
                              />
                              
                              {/* Line */}
                              <path
                                d={pathD}
                                fill="none"
                                stroke={marketData.oil.change_7d && marketData.oil.change_7d > 0 ? "#4ade80" : "#f87171"}
                                strokeWidth="0.5"
                                strokeLinecap="round"
                                strokeLinejoin="round"
                              />
                              
                              {/* Data points */}
                              {points.map((point, idx) => (
                                <g key={idx}>
                                  <circle
                                    cx={point.x}
                                    cy={point.y}
                                    r="0.8"
                                    fill={marketData.oil.change_7d && marketData.oil.change_7d > 0 ? "#4ade80" : "#f87171"}
                                    className="cursor-pointer"
                                  />
                                  <title>${point.price.toFixed(2)} - {point.date}</title>
                                </g>
                              ))}
                            </>
                          );
                        })()}
                      </svg>
                      
                      {/* Y-axis labels */}
                      <div className="absolute left-0 top-0 bottom-0 flex flex-col justify-between text-[10px] text-slate-500 pr-2" style={{ width: '45px' }}>
                        <span>${Math.max(...marketData.oil.trend.map(p => p.price)).toFixed(0)}</span>
                        <span>${((Math.max(...marketData.oil.trend.map(p => p.price)) + Math.min(...marketData.oil.trend.map(p => p.price))) / 2).toFixed(0)}</span>
                        <span>${Math.min(...marketData.oil.trend.map(p => p.price)).toFixed(0)}</span>
                      </div>
                    </div>
                    
                    {/* X-axis labels */}
                    <div className="flex justify-between mt-2 text-[9px] text-slate-500 px-12">
                      {(() => {
                        const filteredIndices = [0, Math.floor(marketData.oil.trend.length / 2), marketData.oil.trend.length - 1];
                        return filteredIndices.map((idx) => {
                          const point = marketData.oil.trend[idx];
                          return (
                            <span key={idx}>
                              {new Date(point.date).toLocaleDateString(locale === 'ar' ? 'ar-EG' : 'en-US', { day: 'numeric', month: 'short' })}
                            </span>
                          );
                        });
                      })()}
                    </div>
                  </div>
                )}
              </div>

              {/* Gold Price & Analysis */}
              <div className="space-y-4">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="text-xs text-slate-400 uppercase mb-1">
                      {locale === 'ar' ? 'الذهب (XAU/USD)' : 'Gold (XAU/USD)'}
                    </div>
                    <div className="text-4xl font-bold text-yellow-400">
                      ${marketData.gold.current?.price.toFixed(2)}
                    </div>
                    <div className="text-xs text-slate-500 mt-1">{marketData.gold.unit}</div>
                  </div>
                </div>
                
                {/* Analysis */}
                <div className="bg-slate-700/40 p-4 rounded-lg border border-slate-600">
                  <div className="flex items-center gap-2 mb-3">
                    <div className="w-1 h-4 bg-orange-500 rounded"></div>
                    <div className="text-xs text-slate-400 uppercase font-bold">
                      {locale === 'ar' ? 'التحليل الجيوسياسي' : 'Geopolitical Analysis'}
                    </div>
                  </div>
                  <p className="text-sm text-slate-300 leading-relaxed">
                    {locale === 'ar' ? marketData.analysis.ar : marketData.analysis.en}
                  </p>
                </div>

                {/* Market Indicators */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-slate-700/30 p-3 rounded-lg border border-slate-600">
                    <div className="text-xs text-slate-400 mb-1">
                      {locale === 'ar' ? 'حالة السوق' : 'Market Status'}
                    </div>
                    <div className={`text-sm font-bold ${
                      marketData.oil.change_7d && marketData.oil.change_7d > 0 
                        ? 'text-red-400' 
                        : 'text-green-400'
                    }`}>
                      {marketData.oil.change_7d && marketData.oil.change_7d > 0 
                        ? (locale === 'ar' ? 'توتر متزايد' : 'Rising Tension')
                        : (locale === 'ar' ? 'استقرار نسبي' : 'Relative Stability')
                      }
                    </div>
                  </div>
                  <div className="bg-slate-700/30 p-3 rounded-lg border border-slate-600">
                    <div className="text-xs text-slate-400 mb-1">
                      {locale === 'ar' ? 'مؤشر المخاطر' : 'Risk Index'}
                    </div>
                    <div className={`text-sm font-bold ${
                      marketData.oil.change_7d && Math.abs(marketData.oil.change_7d) > 5 
                        ? 'text-red-400' 
                        : 'text-yellow-400'
                    }`}>
                      {marketData.oil.change_7d && Math.abs(marketData.oil.change_7d) > 5 
                        ? (locale === 'ar' ? 'عالي' : 'High')
                        : (locale === 'ar' ? 'متوسط' : 'Medium')
                      }
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-slate-400">
              {locale === 'ar' ? 'جاري تحميل بيانات السوق...' : 'Loading market data...'}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Top Countries */}
      <Card className="bg-slate-800/50 border-slate-700 backdrop-blur-sm">
        <CardHeader className="pb-3 border-b border-slate-700">
          <CardTitle className="flex items-center gap-2 text-base text-white">
            <Globe className="h-4 w-4 text-blue-500" />
            {locale === 'ar' ? 'أكثر الدول نشاطاً' : 'Most Active Countries'}
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-4">
          <div className="space-y-3">
            {countries?.slice(0, 5).map((country, idx) => (
              <div key={idx} className="p-3 bg-slate-700/30 rounded-lg border border-slate-600 hover:border-slate-500 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center">
                      <span className="text-blue-400 font-bold text-sm">#{idx + 1}</span>
                    </div>
                    <div>
                      <div className="text-white font-bold text-base">{getCountryName(country.country_code, locale)}</div>
                      <div className="text-xs text-slate-400">
                        {country.locations_count} {locale === 'ar' ? 'موقع' : 'locations'}
                      </div>
                    </div>
                  </div>
                  <div className="flex gap-4">
                    <div className="text-right">
                      <div className="text-purple-400 font-bold text-lg">{country.events_count}</div>
                      <div className="text-xs text-slate-400">{locale === 'ar' ? 'أحداث' : 'events'}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-red-400 font-bold text-lg">{country.metrics_count}</div>
                      <div className="text-xs text-slate-400">{locale === 'ar' ? 'مؤشرات' : 'metrics'}</div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Recent Activity Timeline */}
      <Card className="bg-slate-800/50 border-slate-700 backdrop-blur-sm">
        <CardHeader className="pb-3 border-b border-slate-700">
          <CardTitle className="flex items-center gap-2 text-base text-white">
            <TrendingUp className="h-4 w-4 text-purple-500" />
            {locale === 'ar' ? 'النشاط الأخير (14 يوم)' : 'Recent Activity (14 Days)'}
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-4">
          <div className="space-y-3">
            {timeline?.slice(0, 7).map((day: DateStatistics, idx: number) => {
              const total = day.articles_count + day.events_count;
              const articlesPercent = total > 0 ? (day.articles_count / total) * 100 : 0;
              const eventsPercent = total > 0 ? (day.events_count / total) * 100 : 0;
              
              return (
                <div key={idx} className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-slate-300 font-medium text-sm">
                      {new Date(day.date).toLocaleDateString(locale === 'ar' ? 'ar-EG' : 'en-US', { 
                        month: 'short', 
                        day: 'numeric',
                        weekday: 'short'
                      })}
                    </span>
                    <div className="flex gap-3 text-xs">
                      <span className="text-blue-400">
                        {day.articles_count} {locale === 'ar' ? 'مقال' : 'articles'}
                      </span>
                      <span className="text-purple-400">
                        {day.events_count} {locale === 'ar' ? 'حدث' : 'events'}
                      </span>
                    </div>
                  </div>
                  <div className="h-10 flex rounded-lg overflow-hidden border border-slate-600">
                    {day.articles_count > 0 && (
                      <div 
                        className="bg-gradient-to-r from-blue-600 to-blue-500 flex items-center justify-center text-white font-bold text-sm transition-all hover:opacity-90"
                        style={{ width: `${articlesPercent}%` }}
                        title={`${day.articles_count} articles`}
                      >
                        {day.articles_count}
                      </div>
                    )}
                    {day.events_count > 0 && (
                      <div 
                        className="bg-gradient-to-r from-purple-600 to-purple-500 flex items-center justify-center text-white font-bold text-sm transition-all hover:opacity-90"
                        style={{ width: `${eventsPercent}%` }}
                        title={`${day.events_count} events`}
                      >
                        {day.events_count}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
          <div className="flex gap-4 mt-4 pt-3 border-t border-slate-700">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-blue-500 rounded"></div>
              <span className="text-xs text-slate-300">{locale === 'ar' ? 'مقالات' : 'Articles'}</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-purple-500 rounded"></div>
              <span className="text-xs text-slate-300">{locale === 'ar' ? 'أحداث' : 'Events'}</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Top Metrics */}
      <Card className="bg-slate-800/50 border-slate-700 backdrop-blur-sm">
        <CardHeader className="pb-3 border-b border-slate-700">
          <CardTitle className="flex items-center gap-2 text-base text-white">
            <BarChart3 className="h-4 w-4 text-red-500" />
            {locale === 'ar' ? 'أهم المؤشرات' : 'Top Metrics'}
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-4">
          <div className="space-y-4">
            {(() => {
              // Filter out duplicate metrics (keep airstrikes_count, remove airstrikes)
              const filteredMetrics = metrics?.metrics?.filter(m => 
                m.metric_type !== 'airstrikes' // Remove duplicate, keep airstrikes_count
              ).slice(0, 5);
              
              return filteredMetrics?.map((metric, idx) => {
                // Parse countries JSON string to array
                const countries = typeof metric.countries === 'string' 
                  ? JSON.parse(metric.countries) 
                  : metric.countries;
                
                // Translate metric names
                const metricNames: Record<string, { en: string; ar: string }> = {
                  'missiles_launched': { en: 'Missiles Launched', ar: 'صواريخ أُطلقت' },
                  'injured': { en: 'Injured', ar: 'جرحى' },
                  'drones_launched': { en: 'Drones Launched', ar: 'طائرات مسيرة أُطلقت' },
                  'airstrikes_count': { en: 'Airstrikes Count', ar: 'عدد الغارات الجوية' },
                  'airstrikes': { en: 'Airstrikes', ar: 'غارات جوية' },
                  'killed': { en: 'Killed', ar: 'قتلى' },
                  'military_operations': { en: 'Military Operations', ar: 'عمليات عسكرية' },
                };
                
                const metricName = metricNames[metric.metric_type] 
                  ? (locale === 'ar' ? metricNames[metric.metric_type].ar : metricNames[metric.metric_type].en)
                  : metric.metric_type;
                
                return (
                  <div key={idx} className="p-4 bg-slate-700/30 rounded-lg border border-slate-600">
                    {/* Header */}
                    <div className="flex justify-between items-center mb-3">
                      <div className="text-white font-bold text-base">{metricName}</div>
                      <div className="px-3 py-1 bg-red-500/20 rounded-full">
                        <span className="text-red-400 font-bold text-sm">
                          {metric.total_occurrences} {locale === 'ar' ? 'مرة' : 'times'}
                        </span>
                      </div>
                    </div>
                    
                    {/* Stats */}
                    <div className="grid grid-cols-2 gap-3 mb-3">
                      <div className="bg-slate-600/30 p-2 rounded">
                        <div className="text-xs text-slate-400 mb-1">
                          {locale === 'ar' ? 'المتوسط' : 'Average'}
                        </div>
                        <div className="text-orange-400 font-bold text-lg">
                          {metric.overall_avg?.toFixed(0)}
                        </div>
                      </div>
                      <div className="bg-slate-600/30 p-2 rounded">
                        <div className="text-xs text-slate-400 mb-1">
                          {locale === 'ar' ? 'الحد الأقصى' : 'Maximum'}
                        </div>
                        <div className="text-red-400 font-bold text-lg">
                          {metric.overall_max}
                        </div>
                      </div>
                    </div>
                    
                    {/* Countries */}
                    <div className="pt-3 border-t border-slate-600">
                      <div className="text-xs text-slate-400 mb-2">
                        {locale === 'ar' ? 'الدول المتأثرة:' : 'Affected Countries:'}
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {countries?.slice(0, 4).map((country: any, cidx: number) => (
                          <div key={cidx} className="px-3 py-1.5 bg-slate-600/50 rounded-lg border border-slate-500">
                            <div className="flex items-center gap-2">
                              <span className="text-blue-300 font-bold text-sm">{country.country_code}</span>
                              <span className="text-slate-400">→</span>
                              <span className="text-orange-300 font-medium text-sm">
                                {country.occurrences} {locale === 'ar' ? 'مرة' : 'times'}
                              </span>
                            </div>
                          </div>
                        ))}
                        {countries && countries.length > 4 && (
                          <div className="px-3 py-1.5 text-xs text-slate-400 flex items-center">
                            +{countries.length - 4} {locale === 'ar' ? 'أخرى' : 'more'}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              });
            })()}
          </div>
        </CardContent>
      </Card>

      {/* Hot Locations */}
      <Card className="bg-slate-800/50 border-slate-700 backdrop-blur-sm">
        <CardHeader className="pb-3 border-b border-slate-700">
          <CardTitle className="flex items-center gap-2 text-base text-white">
            <MapPin className="h-4 w-4 text-orange-500" />
            {locale === 'ar' ? 'المناطق الساخنة' : 'Hot Locations'}
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-4">
          <div className="space-y-3">
            {(() => {
              // Priority countries to show (Arab countries + key players)
              const priorityCountries = ['IR', 'IL', 'SA', 'AE', 'PS', 'YE', 'BH', 'KW', 'QA', 'IQ', 'LB', 'SY'];
              
              // Filter to show only one location per country
              const seenCountries = new Set<string>();
              const uniqueLocations = hotspots?.locations?.filter(location => {
                if (seenCountries.has(location.country_code)) {
                  return false;
                }
                seenCountries.add(location.country_code);
                return true;
              });

              // Sort by priority countries first, then by events count
              const sortedLocations = uniqueLocations?.sort((a, b) => {
                const aPriority = priorityCountries.indexOf(a.country_code);
                const bPriority = priorityCountries.indexOf(b.country_code);
                
                // If both are priority countries, sort by their priority order
                if (aPriority !== -1 && bPriority !== -1) {
                  return aPriority - bPriority;
                }
                // If only one is priority, it comes first
                if (aPriority !== -1) return -1;
                if (bPriority !== -1) return 1;
                
                // Otherwise sort by events count
                return b.events_count - a.events_count;
              }).slice(0, 8);

              return sortedLocations?.map((location, idx) => (
                <div key={idx} className="p-3 bg-slate-700/30 rounded-lg border border-slate-600 hover:border-slate-500 transition-colors">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="text-white font-bold text-sm mb-1">{location.location_name}</div>
                      <div className="text-xs text-slate-400">{getCountryName(location.country_code, locale)}</div>
                    </div>
                    <div className="flex gap-3">
                      <div className="text-center px-2">
                        <div className="text-orange-400 font-bold text-base">{location.events_count}</div>
                        <div className="text-[10px] text-slate-500">{locale === 'ar' ? 'أحداث' : 'events'}</div>
                      </div>
                      <div className="text-center px-2">
                        <div className="text-red-400 font-bold text-base">{location.metrics_count}</div>
                        <div className="text-[10px] text-slate-500">{locale === 'ar' ? 'مؤشرات' : 'metrics'}</div>
                      </div>
                    </div>
                  </div>
                </div>
              ));
            })()}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
