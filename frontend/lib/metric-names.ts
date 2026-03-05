/**
 * Metric Type to Human-Readable Name Mapping
 */

export const metricNames: Record<string, { en: string; ar: string; icon: string }> = {
  missiles_launched: { 
    en: 'Missiles Launched', 
    ar: 'صواريخ أطلقت',
    icon: '🚀'
  },
  missiles_intercepted: { 
    en: 'Missiles Intercepted', 
    ar: 'صواريخ اعترضت',
    icon: '🛡️'
  },
  missiles_hit_target: { 
    en: 'Missiles Hit Target', 
    ar: 'صواريخ أصابت الهدف',
    icon: '🎯'
  },
  drones_launched: { 
    en: 'Drones Launched', 
    ar: 'طائرات مسيرة أطلقت',
    icon: '✈️'
  },
  drones_intercepted: { 
    en: 'Drones Intercepted', 
    ar: 'طائرات مسيرة اعترضت',
    icon: '🛡️'
  },
  aircraft_downed: { 
    en: 'Aircraft Downed', 
    ar: 'طائرات أسقطت',
    icon: '💥'
  },
  airstrikes: { 
    en: 'Airstrikes', 
    ar: 'غارات جوية',
    icon: '💣'
  },
  airstrikes_count: { 
    en: 'Airstrikes Count', 
    ar: 'عدد الغارات',
    icon: '💣'
  },
  killed: { 
    en: 'Casualties (Killed)', 
    ar: 'قتلى',
    icon: '⚰️'
  },
  injured: { 
    en: 'Casualties (Injured)', 
    ar: 'جرحى',
    icon: '🏥'
  },
  civilians_killed: { 
    en: 'Civilians Killed', 
    ar: 'مدنيون قتلوا',
    icon: '👥'
  },
  soldiers_killed: { 
    en: 'Soldiers Killed', 
    ar: 'جنود قتلوا',
    icon: '🪖'
  },
  military_operations: { 
    en: 'Military Operations', 
    ar: 'عمليات عسكرية',
    icon: '⚔️'
  },
  targets_hit: { 
    en: 'Targets Hit', 
    ar: 'أهداف أصيبت',
    icon: '🎯'
  },
  forces_deployed: { 
    en: 'Forces Deployed', 
    ar: 'قوات منتشرة',
    icon: '🪖'
  },
  evacuations: { 
    en: 'Evacuations', 
    ar: 'عمليات إجلاء',
    icon: '🚨'
  },
};

/**
 * Get metric display name by type and locale
 */
export function getMetricName(type: string, locale: 'en' | 'ar' = 'en'): string {
  const metric = metricNames[type];
  if (metric) {
    return metric[locale];
  }
  // Fallback: capitalize and replace underscores
  return type.split('_').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ');
}

/**
 * Get metric icon
 */
export function getMetricIcon(type: string): string {
  const metric = metricNames[type];
  return metric?.icon || '📊';
}
