/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: [
      'i.pinimg.com',
      'pinimg.com',
      'images-na.ssl-images-amazon.com',
      'm.media-amazon.com',
      'via.placeholder.com',
    ],
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000',
    NEXT_PUBLIC_PINTEREST_CLIENT_ID: process.env.NEXT_PUBLIC_PINTEREST_CLIENT_ID ?? '',
  },
}

export default nextConfig
