import AMapLoader from '@amap/amap-jsapi-loader';

declare global {
  interface Window {
    _AMapSecurityConfig?: {
      securityJsCode?: string;
      serviceHost?: string;
    };
  }
}

export function hasAmapConfig() {
  return Boolean(import.meta.env.VITE_AMAP_JS_API_KEY && import.meta.env.VITE_AMAP_JS_SECURITY_JSCODE);
}

export async function loadAmap() {
  if (!hasAmapConfig()) {
    throw new Error('缺少 VITE_AMAP_JS_API_KEY 或 VITE_AMAP_JS_SECURITY_JSCODE');
  }

  window._AMapSecurityConfig = {
    securityJsCode: import.meta.env.VITE_AMAP_JS_SECURITY_JSCODE,
  };

  return AMapLoader.load({
    key: import.meta.env.VITE_AMAP_JS_API_KEY,
    version: '2.0',
    plugins: ['AMap.Scale', 'AMap.ToolBar', 'AMap.MarkerCluster'],
  });
}
