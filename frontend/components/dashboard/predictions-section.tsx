'use client';

import { useQuery } from '@tanstack/react-query';
import { useLocale } from 'next-intl';
import { fetchAIIntelligenceForecast, fetchAITrendAnalysis } from '@/lib/api-services';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { TrendingUp, TrendingDown, Minus, AlertTriangle, Brain, Info, Sparkles, Target, Shield } from 'lucide-react';

export function PredictionsSection() {
  const locale = useLocale() as 'en' | 'ar';
  
  const { data: aiData, isLoading: aiLoading, error: aiError } = useQuery({
    queryKey: ['ai-intelligence-forecast'],
    queryFn: () => fetchAIIntelligenceForecast(7),
    retry: 1,
  });

  const { data: aiTrendData, error: aiTrendError } = useQuery({
    queryKey: ['ai-trend-analysis'],
    queryFn: fetchAITrendAnalysis,
    retry: 1,
  });

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'escalating':
        return <TrendingUp className="h-5 w-5 text-red-500" />;
      case 'de-escalating':
      case 'de_escalating':
        return <TrendingDown className="h-5 w-5 text-green-500" />;
      case 'stable':
        return <Minus className="h-5 w-5 text-yellow-500" />;
      default:
        return <AlertTriangle className="h-5 w-5 text-slate-500" />;
    }
  };

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'escalating':
        return 'bg-red-600/20 border-red-500';
      case 'de-escalating':
      case 'de_escalating':
        return 'bg-green-600/20 border-green-500';
      case 'stable':
        return 'bg-yellow-600/20 border-yellow-500';
      default:
        return 'bg-slate-600/20 border-slate-500';
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'critical':
        return 'text-red-500 bg-red-900/30';
      case 'high':
        return 'text-orange-500 bg-orange-900/30';
      case 'medium':
        return 'text-yellow-500 bg-yellow-900/30';
      case 'low':
        return 'text-green-500 bg-green-900/30';
      default:
        return 'text-slate-500 bg-slate-900/30';
    }
  };

  return (
    <div className="space-y-4">
      {/* Error State */}
      {(aiError || aiTrendError) && (
        <Card className="bg-yellow-900/20 border-yellow-500/50 backdrop-blur-sm">
          <CardContent className="pt-4">
            <div className="flex items-start gap-3">
              <AlertTriangle className="h-5 w-5 text-yellow-400 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-sm font-semibold text-yellow-300">
                  {locale === 'ar' ? 'بيانات محدودة أو خطأ في API' : 'Limited Data or API Error'}
                </p>
                <p className="text-xs text-yellow-200/80 mt-1">
                  {locale === 'ar' 
                    ? 'لا توجد بيانات كافية أو حدث خطأ في الاتصال بخدمة الذكاء الاصطناعي.'
                    : 'Not enough data available or error connecting to AI service.'}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* AI Trend Analysis */}
      {aiTrendData && aiTrendData.interpretation && (
        <Card className={`border-2 ${getTrendColor(aiTrendData.overall_trend)} backdrop-blur-sm`}>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-lg text-white">
              {getTrendIcon(aiTrendData.overall_trend)}
              {locale === 'ar' ? '🎯 تحليل الاتجاه بالذكاء الاصطناعي' : '🎯 AI Trend Analysis'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <p className="text-sm text-slate-300 leading-relaxed">
                {aiTrendData.interpretation[locale]}
              </p>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-slate-900/50 rounded-lg p-3">
                  <div className="text-xs text-slate-400 mb-1">
                    {locale === 'ar' ? 'قوة الاتجاه' : 'Trend Strength'}
                  </div>
                  <div className="text-2xl font-bold text-white">
                    {aiTrendData.trend_strength}%
                  </div>
                  <div className="text-xs text-slate-500">
                    {locale === 'ar' ? 'مستوى الثقة' : 'confidence level'}
                  </div>
                </div>
                
                <div className="bg-slate-900/50 rounded-lg p-3">
                  <div className="text-xs text-slate-400 mb-1">
                    {locale === 'ar' ? 'نسبة التغيير' : 'Change Rate'}
                  </div>
                  <div className={`text-2xl font-bold ${aiTrendData.change_percentage > 0 ? 'text-red-400' : 'text-green-400'}`}>
                    {aiTrendData.change_percentage > 0 ? '+' : ''}{aiTrendData.change_percentage.toFixed(1)}%
                  </div>
                  <div className="text-xs text-slate-500">
                    {locale === 'ar' ? 'التغيير الأخير' : 'recent change'}
                  </div>
                </div>
              </div>

              {/* Key Indicators */}
              {aiTrendData.key_indicators && aiTrendData.key_indicators.length > 0 && (
                <div className="bg-slate-900/30 rounded-lg p-3">
                  <h4 className="text-xs font-semibold text-slate-400 mb-2">
                    {locale === 'ar' ? 'المؤشرات الرئيسية' : 'Key Indicators'}
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {aiTrendData.key_indicators.map((indicator, idx) => (
                      <span key={idx} className="text-xs bg-purple-900/30 text-purple-300 px-2 py-1 rounded">
                        {indicator}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* 7-Day Outlook */}
              {aiTrendData.next_7_days_outlook && (
                <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-3">
                  <h4 className="text-xs font-semibold text-blue-300 mb-2">
                    {locale === 'ar' ? '📊 توقعات الأيام السبعة القادمة' : '📊 Next 7 Days Outlook'}
                  </h4>
                  <p className="text-xs text-blue-200/80 leading-relaxed">
                    {aiTrendData.next_7_days_outlook[locale]}
                  </p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* AI Intelligence Forecast */}
      <Card className="bg-slate-800/50 border-slate-700 backdrop-blur-sm">
        <CardHeader className="pb-3 border-b border-slate-700">
          <CardTitle className="flex items-center gap-2 text-lg text-white">
            <Brain className="h-5 w-5 text-purple-500" />
            {locale === 'ar' ? '🔮 التوقعات الذكية' : '🔮 Intelligence Forecast'}
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-4">
          {aiLoading ? (
            <div className="h-80 flex flex-col items-center justify-center gap-3">
              <Brain className="h-12 w-12 text-purple-500 animate-pulse" />
              <div className="text-slate-400">
                {locale === 'ar' ? 'جاري التحليل بالذكاء الاصطناعي...' : 'AI is analyzing data...'}
              </div>
            </div>
          ) : aiData && aiData.forecast ? (
            <div className="space-y-4">
              {/* AI Summary */}
              <div className="bg-gradient-to-r from-purple-900/30 to-blue-900/30 rounded-lg p-4 border border-purple-500/30">
                <h3 className="text-sm font-semibold text-purple-300 mb-3 flex items-center gap-2">
                  <Sparkles className="h-4 w-4" />
                  {locale === 'ar' ? 'ملخص التحليل الذكي' : 'AI Analysis Summary'}
                </h3>
                <div className="space-y-3 text-sm text-slate-300 leading-relaxed">
                  <p className="text-slate-200">
                    {aiData.summary[locale]}
                  </p>
                  
                  {/* Risk Level */}
                  <div className="flex items-center gap-3">
                    <Shield className="h-4 w-4 text-slate-400" />
                    <span className="text-xs text-slate-400">
                      {locale === 'ar' ? 'مستوى المخاطر:' : 'Risk Level:'}
                    </span>
                    <span className={`text-xs font-semibold px-3 py-1 rounded-full ${getRiskColor(aiData.risk_level)}`}>
                      {aiData.risk_level.toUpperCase()}
                    </span>
                    <span className="text-xs text-slate-400">
                      {locale === 'ar' ? 'ثقة:' : 'Confidence:'}
                    </span>
                    <span className="text-xs font-semibold text-purple-400">
                      {aiData.confidence_overall}%
                    </span>
                  </div>
                </div>
              </div>

              {/* Detailed Insights */}
              <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700">
                <h3 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
                  <Target className="h-4 w-4 text-blue-400" />
                  {locale === 'ar' ? 'رؤى تفصيلية' : 'Detailed Insights'}
                </h3>
                <p className="text-xs text-slate-300 leading-relaxed">
                  {aiData.insights[locale]}
                </p>
              </div>

              {/* Next 7 Days Predictions */}
              <div className="bg-slate-900/30 rounded-lg p-3 space-y-2">
                <h4 className="text-xs font-semibold text-slate-400 mb-3">
                  {locale === 'ar' ? '📅 توقعات الأيام السبعة القادمة' : '📅 Next 7 Days Predictions'}
                </h4>
                {aiData.forecast.map((pred, idx) => (
                  <div key={idx} className="flex items-center justify-between bg-slate-800/50 rounded p-2">
                    <span className="text-xs text-slate-400">
                      {new Date(pred.date).toLocaleDateString(locale === 'ar' ? 'ar-EG' : 'en-US', { 
                        weekday: 'short', 
                        month: 'short', 
                        day: 'numeric' 
                      })}
                    </span>
                    <div className="flex items-center gap-3">
                      <span className="text-sm font-semibold text-purple-400">
                        ~{pred.predicted_events} {locale === 'ar' ? 'حدث' : 'events'}
                      </span>
                      <span className="text-xs text-slate-500">
                        {pred.confidence}% {locale === 'ar' ? 'ثقة' : 'conf'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              {/* Key Factors */}
              {aiData.key_factors && aiData.key_factors.length > 0 && (
                <div className="bg-slate-900/30 rounded-lg p-3">
                  <h4 className="text-xs font-semibold text-slate-400 mb-2">
                    {locale === 'ar' ? 'العوامل الرئيسية المؤثرة' : 'Key Influencing Factors'}
                  </h4>
                  <div className="space-y-1">
                    {aiData.key_factors.map((factor, idx) => (
                      <div key={idx} className="text-xs text-slate-300 flex items-start gap-2">
                        <span className="text-purple-400">•</span>
                        <span>{factor}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* High/Low Days */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {aiData.highest_risk_day && (
                  <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-3">
                    <div className="flex items-center gap-2 mb-2">
                      <TrendingUp className="h-4 w-4 text-red-400" />
                      <h4 className="text-xs font-semibold text-red-300">
                        {locale === 'ar' ? 'أعلى يوم خطورة' : 'Highest Risk Day'}
                      </h4>
                    </div>
                    <div className="text-sm font-bold text-red-400 mb-1">
                      {new Date(aiData.highest_risk_day.date).toLocaleDateString(locale === 'ar' ? 'ar-EG' : 'en-US')}
                    </div>
                    <div className="text-xs text-red-200/80">
                      {aiData.highest_risk_day.reason}
                    </div>
                  </div>
                )}

                {aiData.lowest_activity_day && (
                  <div className="bg-green-900/20 border border-green-500/30 rounded-lg p-3">
                    <div className="flex items-center gap-2 mb-2">
                      <TrendingDown className="h-4 w-4 text-green-400" />
                      <h4 className="text-xs font-semibold text-green-300">
                        {locale === 'ar' ? 'أقل يوم نشاطاً' : 'Lowest Activity Day'}
                      </h4>
                    </div>
                    <div className="text-sm font-bold text-green-400 mb-1">
                      {new Date(aiData.lowest_activity_day.date).toLocaleDateString(locale === 'ar' ? 'ar-EG' : 'en-US')}
                    </div>
                    <div className="text-xs text-green-200/80">
                      {aiData.lowest_activity_day.reason}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="h-80 flex items-center justify-center text-slate-400">
              {locale === 'ar' ? 'لا توجد بيانات كافية للتنبؤ' : 'Not enough data for forecasting'}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
