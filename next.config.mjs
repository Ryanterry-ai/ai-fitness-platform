/** @type {import('next').NextConfig} */
const nextConfig = {
  // Static export: `npm run build` now emits a plain HTML/CSS/JS site into ./out
  // Copy the contents of ./out into Hostinger's public_html — no Node server required.
  output: 'export',
  trailingSlash: true, // so /shop resolves to /shop/index.html on Apache
  images: {
    unoptimized: true, // required for static export — next/image can't run its optimizer without a server
    remotePatterns: [
      { protocol: 'https', hostname: 'picsum.photos' },
      { protocol: 'https', hostname: 'images.unsplash.com' },
    ],
  },
};
export default nextConfig;
