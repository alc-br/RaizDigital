import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    // Porta padrão do Vite. Ajustado para 5173 para alinhar com a documentação.
    port: 5173,
  },
});
