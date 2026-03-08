'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useTranslations } from 'next-intl';
import dynamic from 'next/dynamic';
import { fetchLocations } from '@/lib/api-services';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Map as MapIcon } from 'lucide-react';
import { LocationNewsModal } from './location-news-modal';
import type { GeographicLocationListItem } from '@/types';

const MapComponent = dynamic(() => import('./map-component'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full flex items-center justify-center bg-slate-900/50">
      <div className="text-sm text-slate-400">Loading map...</div>
    </div>
  ),
});

export function MapSection() {
  const t = useTranslations('map');
  const [selectedLocation, setSelectedLocation] = useState<GeographicLocationListItem | null>(null);

  const { data: locations, isLoading } = useQuery({
    queryKey: ['locations'],
    queryFn: fetchLocations,
  });

  return (
    <>
      <Card className="h-full flex flex-col bg-slate-800/50 border-slate-700 backdrop-blur-sm overflow-hidden">
        <CardHeader className="pb-3 border-b border-slate-700">
          <CardTitle className="flex items-center gap-2 text-lg text-white">
            <MapIcon className="h-5 w-5 text-red-500" />
            {t('title')}
            {locations && locations.length > 0 && (
              <span className="text-xs font-normal text-slate-400 ml-2">
                ({locations.length} locations)
              </span>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent className="flex-1 p-0 overflow-hidden">
          <MapComponent 
            locations={locations || []} 
            isLoading={isLoading}
            onLocationClick={setSelectedLocation}
          />
        </CardContent>
      </Card>
      
      {/* Modal - Outside of map container */}
      <LocationNewsModal 
        location={selectedLocation}
        onClose={() => setSelectedLocation(null)}
      />
    </>
  );
}
