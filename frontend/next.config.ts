import type { NextConfig } from "next";
import createNextIntlPlugin from 'next-intl/plugin';

const withNextIntl = createNextIntlPlugin('./i18n/request.ts');

const nextConfig: NextConfig = {
  /* config options here */
  output: 'standalone', // For Docker deployment
  devIndicators: {
    buildActivity: false, // Disable build activity indicator
    buildActivityPosition: 'bottom-right',
  },
};

export default withNextIntl(nextConfig);
