// vite.config.js
import { fileURLToPath, URL } from "node:url";
import { defineConfig } from "file:///Users/andrewjohnson/git/keeper-helper/node_modules/vite/dist/node/index.js";
import vue from "file:///Users/andrewjohnson/git/keeper-helper/node_modules/@vitejs/plugin-vue/dist/index.mjs";
import tailwindcss from "file:///Users/andrewjohnson/git/keeper-helper/node_modules/@tailwindcss/vite/dist/index.mjs";
var __vite_injected_original_import_meta_url = "file:///Users/andrewjohnson/git/keeper-helper/vite.config.js";
var vite_config_default = defineConfig({
  base: "/keeper-helper/",
  assetsInclude: ["**/*.csv", "**/*.json"],
  plugins: [
    vue(),
    tailwindcss()
  ],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", __vite_injected_original_import_meta_url))
    }
  }
});
export {
  vite_config_default as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsidml0ZS5jb25maWcuanMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCIvVXNlcnMvYW5kcmV3am9obnNvbi9naXQva2VlcGVyLWhlbHBlclwiO2NvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9maWxlbmFtZSA9IFwiL1VzZXJzL2FuZHJld2pvaG5zb24vZ2l0L2tlZXBlci1oZWxwZXIvdml0ZS5jb25maWcuanNcIjtjb25zdCBfX3ZpdGVfaW5qZWN0ZWRfb3JpZ2luYWxfaW1wb3J0X21ldGFfdXJsID0gXCJmaWxlOi8vL1VzZXJzL2FuZHJld2pvaG5zb24vZ2l0L2tlZXBlci1oZWxwZXIvdml0ZS5jb25maWcuanNcIjtpbXBvcnQgeyBmaWxlVVJMVG9QYXRoLCBVUkwgfSBmcm9tICdub2RlOnVybCdcblxuaW1wb3J0IHsgZGVmaW5lQ29uZmlnIH0gZnJvbSAndml0ZSdcbmltcG9ydCB2dWUgZnJvbSAnQHZpdGVqcy9wbHVnaW4tdnVlJ1xuaW1wb3J0IHRhaWx3aW5kY3NzIGZyb20gXCJAdGFpbHdpbmRjc3Mvdml0ZVwiO1xuXG4vLyBodHRwczovL3ZpdGVqcy5kZXYvY29uZmlnL1xuZXhwb3J0IGRlZmF1bHQgZGVmaW5lQ29uZmlnKHtcbiAgYmFzZTogXCIva2VlcGVyLWhlbHBlci9cIixcbiAgYXNzZXRzSW5jbHVkZTogWycqKi8qLmNzdicsICcqKi8qLmpzb24nXSxcbiAgcGx1Z2luczogW1xuICAgIHZ1ZSgpLCAgICB0YWlsd2luZGNzcygpXG4gIF0sXG4gIHJlc29sdmU6IHtcbiAgICBhbGlhczoge1xuICAgICAgJ0AnOiBmaWxlVVJMVG9QYXRoKG5ldyBVUkwoJy4vc3JjJywgaW1wb3J0Lm1ldGEudXJsKSlcbiAgICB9XG4gIH1cbn0pXG4iXSwKICAibWFwcGluZ3MiOiAiO0FBQW9TLFNBQVMsZUFBZSxXQUFXO0FBRXZVLFNBQVMsb0JBQW9CO0FBQzdCLE9BQU8sU0FBUztBQUNoQixPQUFPLGlCQUFpQjtBQUo0SixJQUFNLDJDQUEyQztBQU9yTyxJQUFPLHNCQUFRLGFBQWE7QUFBQSxFQUMxQixNQUFNO0FBQUEsRUFDTixlQUFlLENBQUMsWUFBWSxXQUFXO0FBQUEsRUFDdkMsU0FBUztBQUFBLElBQ1AsSUFBSTtBQUFBLElBQU0sWUFBWTtBQUFBLEVBQ3hCO0FBQUEsRUFDQSxTQUFTO0FBQUEsSUFDUCxPQUFPO0FBQUEsTUFDTCxLQUFLLGNBQWMsSUFBSSxJQUFJLFNBQVMsd0NBQWUsQ0FBQztBQUFBLElBQ3REO0FBQUEsRUFDRjtBQUNGLENBQUM7IiwKICAibmFtZXMiOiBbXQp9Cg==
