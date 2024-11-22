import { defineConfig } from 'vite';

export default defineConfig({
    build: {
        rollupOptions: {
            input: './static/javascript/calendar.js',
            output: {
                dir: './static/javascript/dist',
                format: 'es',
            },
        },
    },
});
