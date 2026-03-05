'use client';

import { useQuery } from '@tanstack/react-query';
import { useTranslations } from 'next-intl';
import { fetchAnalyticsOverview } from '@/lib/api-services';
import { Card } from '@/components/ui/card';
import { TrendingUp, MapPin, FileText, Activity, Target, AlertCircle } from 'lucide-react';

export function MetricsOverview() {
  const t = useTranslations('analytics');
  
  const { data: overview, isLoading } = useQuery({
    queryKey: ['analytics-overview'],
    queryFn: fetchAnalyticsOverview,
  });

  if (isLoading) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        {[...Array(6)].map((_, i) => (
          <Card key={i} className="p-4 animate-pulse bg-slate-800/50 border-slate-700">
            <div className="h-4 bg-slate-700 rounded w-3/4 mb-2"></div>
            <div className="h-8 bg-slate-700 rounded w-1/2"></div>
          </Card>
        ))}
      </div>
    );
  }

  if (!overview) return null;

  const metrics = [
    {
      label: t('totalArticles'),
      value: overview.total_news_articles,
      icon: FileText,
      color: 'from-blue-500 to-blue-600',
      bgColor: 'bg-blue-500/10',
      borderColor: 'border-blue-500/20',
    },
    {
      label: t('totalEvents'),
      value: overview.total_events,
      icon: Activity,
      color: 'from-red-500 to-red-600',
      bgColor: 'bg-red-500/10',
      borderColor: 'border-red-500/20',
    },
    {
      label: t('totalLocations'),
      value: overview.total_locations,
      icon: MapPin,
      color: 'from-purple-500 to-purple-600',
      bgColor: 'bg-purple-500/10',
      borderColor: 'border-purple-500/20',
    },
    {
      label: t('totalMetrics'),
      value: overview.total_metrics,
      icon: TrendingUp,
      color: 'from-orange-500 to-orange-600',
      bgColor: 'bg-orange-500/10',
      borderColor: 'border-orange-500/20',
    },
    {
      label: 'Countries',
      value: overview.total_countries,
      icon: Target,
      color: 'from-green-500 to-green-600',
      bgColor: 'bg-green-500/10',
      borderColor: 'border-green-500/20',
    },
    {
      label: 'With Metrics',
      value: overview.events_with_metrics,
      icon: AlertCircle,
      color: 'from-yellow-500 to-yellow-600',
      bgColor: 'bg-yellow-500/10',
      borderColor: 'border-yellow-500/20',
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
      {metrics.map((metric, index) => {
        const Icon = metric.icon;
        return (
          <Card
            key={index}
            className={`p-4 ${metric.bgColor} border ${metric.borderColor} backdrop-blur-sm hover:scale-105 transition-transform duration-200`}
          >
            <div className="flex items-start justify-between mb-2">
              <div className={`p-2 rounded-lg bg-gradient-to-br ${metric.color}`}>
                <Icon className="h-4 w-4 text-white" />
              </div>
            </div>
            <div>
              <p className="text-2xl font-bold text-white mb-1">
                {metric.value.toLocaleString()}
              </p>
              <p className="text-xs text-slate-400">{metric.label}</p>
            </div>
          </Card>
        );
      })}
    </div>
  );
}
