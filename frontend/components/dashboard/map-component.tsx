'use client';

import { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { useTranslations, useLocale } from 'next-intl';
import type { GeographicLocationListItem } from '@/types';
import { getCountryName } from '@/lib/country-names';

// Fix Leaflet default marker icon issue
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

interface MapComponentProps {
  locations: GeographicLocationListItem[];
  isLoading: boolean;
}

export default function MapComponent({ locations, isLoading }: MapComponentProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<L.Map | null>(null);
  const markers = useRef<L.Marker[]>([]);
  const t = useTranslations('map');
  const locale = useLocale() as 'en' | 'ar';

  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    // Initialize map
    map.current = L.map(mapContainer.current, {
      center: [32.0, 35.5], // Middle East center
      zoom: 5,
      zoomControl: true,
      attributionControl: true,
    });

    // Add dark tile layer (CartoDB Dark Matter - free)
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
      subdomains: 'abcd',
      maxZoom: 19
    }).addTo(map.current);

    return () => {
      if (map.current) {
        map.current.remove();
        map.current = null;
      }
    };
  }, []);

  useEffect(() => {
    if (!map.current || isLoading) return;

    // Clear existing markers
    markers.current.forEach(marker => marker.remove());
    markers.current = [];

    // Add new markers
    locations.forEach(location => {
      if (!map.current) return;

      // Create custom icon based on event count
      const eventCount = location.events_count;
      let iconColor = '#ef4444'; // red-500
      let iconSize = 25;

      if (eventCount > 50) {
        iconColor = '#dc2626'; // red-600
        iconSize = 35;
      } else if (eventCount > 20) {
        iconColor = '#ef4444'; // red-500
        iconSize = 30;
      } else if (eventCount > 10) {
        iconColor = '#f97316'; // orange-500
        iconSize = 25;
      } else {
        iconColor = '#fb923c'; // orange-400
        iconSize = 20;
      }

      const customIcon = L.divIcon({
        className: 'custom-marker',
        html: `
          <div style="
            width: ${iconSize}px;
            height: ${iconSize}px;
            background: ${iconColor};
            border: 3px solid rgba(255, 255, 255, 0.8);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: ${iconSize > 25 ? '12px' : '10px'};
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.5);
            cursor: pointer;
            transition: transform 0.2s;
          " onmouseover="this.style.transform='scale(1.2)'" onmouseout="this.style.transform='scale(1)'">
            ${eventCount}
          </div>
        `,
        iconSize: [iconSize, iconSize],
        iconAnchor: [iconSize / 2, iconSize / 2],
      });

      const marker = L.marker([location.latitude, location.longitude], {
        icon: customIcon,
      }).addTo(map.current);

      // Create popup content
      const countryName = getCountryName(location.country_code, locale);
      const popupContent = `
        <div style="
          background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
          padding: 12px;
          border-radius: 8px;
          border: 2px solid #ef4444;
          min-width: 200px;
          color: white;
          font-family: system-ui, -apple-system, sans-serif;
        ">
          <div style="
            font-size: 16px;
            font-weight: bold;
            color: #ef4444;
            margin-bottom: 8px;
            border-bottom: 1px solid #334155;
            padding-bottom: 6px;
          ">
            📍 ${location.name}
          </div>
          <div style="font-size: 13px; color: #cbd5e1; margin-bottom: 4px;">
            <span style="color: #94a3b8;">🌍 ${locale === 'ar' ? 'الدولة:' : 'Country:'}</span>
            <span style="color: #e2e8f0; font-weight: 600;"> ${countryName}</span>
          </div>
          <div style="font-size: 13px; color: #cbd5e1; margin-bottom: 4px;">
            <span style="color: #94a3b8;">🔥 ${locale === 'ar' ? 'الأحداث:' : 'Events:'}</span>
            <span style="color: #fbbf24; font-weight: bold; font-size: 15px;"> ${eventCount}</span>
          </div>
          <div style="font-size: 11px; color: #64748b; margin-top: 8px; padding-top: 6px; border-top: 1px solid #334155;">
            📊 ${locale === 'ar' ? 'منطقة نشاط عالي' : 'High Activity Zone'}
          </div>
        </div>
      `;

      marker.bindPopup(popupContent, {
        maxWidth: 300,
        className: 'custom-popup',
      });

      // Open popup on hover
      marker.on('mouseover', function(this: L.Marker) {
        this.openPopup();
      });

      markers.current.push(marker);
    });

    // Fit bounds to show all markers
    if (locations.length > 0) {
      const bounds = L.latLngBounds(
        locations.map(loc => [loc.latitude, loc.longitude] as [number, number])
      );
      map.current.fitBounds(bounds, { padding: [50, 50], maxZoom: 7 });
    }
  }, [locations, isLoading, locale]);

  return (
    <>
      <div 
        ref={mapContainer} 
        className="w-full h-full rounded-lg"
        style={{ background: '#0f172a' }}
      />
      <style jsx global>{`
        .leaflet-popup-content-wrapper {
          background: transparent !important;
          box-shadow: none !important;
          padding: 0 !important;
        }
        .leaflet-popup-tip {
          background: #1e293b !important;
          border: 2px solid #ef4444 !important;
        }
        .leaflet-container {
          background: #0f172a !important;
        }
        .leaflet-control-zoom a {
          background: #1e293b !important;
          color: #ef4444 !important;
          border: 1px solid #334155 !important;
        }
        .leaflet-control-zoom a:hover {
          background: #334155 !important;
          color: #f87171 !important;
        }
        .leaflet-control-attribution {
          background: rgba(15, 23, 42, 0.8) !important;
          color: #64748b !important;
          font-size: 10px !important;
        }
        .leaflet-control-attribution a {
          color: #94a3b8 !important;
        }
      `}</style>
    </>
  );
}
