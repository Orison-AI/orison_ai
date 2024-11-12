/** @type {import('next').NextConfig} */
const nextConfig = {
    output: 'export',
    distDir: 'build',
    images: {
        unoptimized: true, // Disable image optimization
    },
};

module.exports = nextConfig;
