'use client';

import { useQuery } from '@tanstack/react-query';
import { useTranslations } from 'next-intl';
import { fetchNewsByLocation } from '@/lib/api-services';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { X, Newspaper, Calendar, MapPin, TrendingUp, Loader } from 'lucide-react';
import type { GeographicLocationListItem } from '@/types';

interface LocationNewsModalProps {
  location: GeographicLocationListItem | null;
  onClose: () => void;
}

export function LocationNewsModal({ location, onClose }: LocationNewsModalProps) {
  const t = useTranslations('news');
  
  const { data: news, isLoading, error } = useQuery({
    queryKey: ['location-news', location?.id],
    queryFn: () => location ? fetchNewsByLocation(location.id) : Promise.resolve([]),
    enabled: !!location,
  });

  if (!location) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none">
        <Card className="w-full max-w-2xl max-h-[80vh] bg-slate-900 border-slate-700 flex flex-col shadow-2xl pointer-events-auto">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-slate-700 flex-shrink-0">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-red-500/10 rounded-lg border border-red-500/20">
                <MapPin className="h-5 w-5 text-red-500" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-white">{location.name}</h2>
                <p className="text-xs text-slate-400">
                  {location.events_count} {t('events')}
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-slate-800 rounded-lg transition-colors flex-shrink-0"
            >
              <X className="h-5 w-5 text-slate-400 hover:text-white" />
            </button>
          </div>

          {/* Content - Scrollable */}
          <div className="flex-1 overflow-y-auto p-6">
            {isLoading ? (
              <div className="flex items-center justify-center h-32">
                <Loader className="h-6 w-6 text-red-500 animate-spin" />
              </div>
            ) : error ? (
              <div className="flex items-center justify-center h-32">
                <p className="text-sm text-red-400">خطأ في تحميل الأخبار</p>
              </div>
            ) : news && news.length > 0 ? (
              <div className="space-y-4">
                {news.map((article) => (
                  <div
                    key={article.id}
                    onClick={() => article.url && window.open(article.url, '_blank')}
                    className="border-l-2 border-red-500/50 pl-4 pb-4 hover:border-red-500 hover:bg-slate-800/30 p-3 rounded-r-lg transition-all cursor-pointer group"
                  >
                    <h3 className="font-semibold text-sm mb-2 line-clamp-2 text-white group-hover:text-red-400 transition-colors">
                      {article.title}
                    </h3>
                    {article.content_preview && (
                      <p className="text-xs text-slate-400 mb-3 line-clamp-2">
                        {article.content_preview}
                      </p>
                    )}
                    <div className="flex flex-wrap gap-2 items-center text-xs text-slate-500 mb-2">
                      {article.published_at && (
                        <span className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          {new Date(article.published_at).toLocaleDateString()}
                        </span>
                      )}
                      {article.source_name && (
                        <span className="text-slate-400">
                          📰 {article.source_name}
                        </span>
                      )}
                    </div>
                    <div className="flex gap-2">
                      {article.events_count > 0 && (
                        <Badge variant="outline" className="text-xs border-blue-500/50 text-blue-400">
                          <MapPin className="h-3 w-3 mr-1" />
                          {article.events_count}
                        </Badge>
                      )}
                      {article.metrics_count > 0 && (
                        <Badge variant="outline" className="text-xs border-orange-500/50 text-orange-400">
                          <TrendingUp className="h-3 w-3 mr-1" />
                          {article.metrics_count}
                        </Badge>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex items-center justify-center h-32">
                <p className="text-sm text-slate-400">{t('noData')}</p>
              </div>
            )}
          </div>
        </Card>
      </div>
    </>
  );
}
