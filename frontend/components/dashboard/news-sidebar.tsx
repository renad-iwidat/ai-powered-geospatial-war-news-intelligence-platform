'use client';

import { useQuery } from '@tanstack/react-query';
import { useTranslations } from 'next-intl';
import { fetchLatestNews } from '@/lib/api-services';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Newspaper, Calendar, MapPin, TrendingUp } from 'lucide-react';

export function NewsSidebar() {
  const t = useTranslations('news');
  
  const { data: news, isLoading } = useQuery({
    queryKey: ['latest-news'],
    queryFn: () => fetchLatestNews(30),
    refetchInterval: 60000,
  });

  if (isLoading) {
    return (
      <Card className="h-full bg-slate-800/50 border-slate-700">
        <CardHeader className="border-b border-slate-700">
          <CardTitle className="flex items-center gap-2 text-white">
            <Newspaper className="h-5 w-5 text-red-500" />
            {t('title')}
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-4">
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="animate-pulse">
                <div className="h-4 bg-slate-700 rounded w-3/4 mb-2"></div>
                <div className="h-3 bg-slate-700 rounded w-1/2"></div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="h-full flex flex-col bg-slate-800/50 border-slate-700 backdrop-blur-sm">
      <CardHeader className="pb-3 border-b border-slate-700">
        <CardTitle className="flex items-center gap-2 text-lg text-white">
          <div className="relative">
            <Newspaper className="h-5 w-5 text-red-500" />
            <span className="absolute -top-1 -right-1 flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span>
            </span>
          </div>
          {t('title')}
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1 overflow-hidden p-0">
        <ScrollArea className="h-full px-4 pb-4">
          <div className="space-y-3 pt-4">
            {news && news.length > 0 ? (
              news.map((article) => (
                <div
                  key={article.id}
                  className="border-l-2 border-red-500/50 pl-3 pb-3 hover:border-red-500 hover:bg-slate-700/30 p-2 rounded-r-lg transition-all cursor-pointer group"
                >
                  <h3 className="font-semibold text-sm mb-2 line-clamp-2 text-white group-hover:text-red-400 transition-colors">
                    {article.title}
                  </h3>
                  {article.content && (
                    <p className="text-xs text-slate-400 mb-2 line-clamp-3">
                      {article.content}
                    </p>
                  )}
                  <div className="flex flex-wrap gap-2 items-center text-xs text-slate-500">
                    {article.published_at && (
                      <span className="flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        {new Date(article.published_at).toLocaleDateString()}
                      </span>
                    )}
                  </div>
                  <div className="flex gap-2 mt-2">
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
              ))
            ) : (
              <p className="text-sm text-slate-400 text-center py-8">
                {t('noData')}
              </p>
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
