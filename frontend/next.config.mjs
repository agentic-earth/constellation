/** @type {import('next').NextConfig} */
const nextConfig = {
  transpilePackages: ['three', 'globe.gl'],
  webpack: (config) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      'lodash-es': 'lodash',
    };
    return config;
  },
};

export default nextConfig;
