from kivy.app import App
from kivy.utils import platform
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle

# URL WEBSITE UTAMA
TARGET_URL = "https://topup-bussid-trucksid-rsyd-store.vercel.app"

# SCRIPT JEMBATAN (INJECT) - IEU NU MAKSA NOTIFIKASI MUNCUL
JS_BRIDGE = """
javascript:(function() {
    console.log("Rosyad Bridge V3 Active");
    // Override Notification System
    window.show_rosyad_push_notif = function(title, body) {
        window.location.href = "rosyad://notif?t=" + encodeURIComponent(title) + "&b=" + encodeURIComponent(body);
    };
    // Override Service Worker
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.ready.then(function(reg) {
            reg.showNotification = function(title, options) {
                var body = options.body || '';
                window.location.href = "rosyad://notif?t=" + encodeURIComponent(title) + "&b=" + encodeURIComponent(body);
            };
        });
    }
})()
"""

class RosyadWebApp(App):
    def build(self):
        self.title = "TOP UP GAME MALEO"
        self.layout = FloatLayout()
        
        # Background Hideung (Loading)
        with self.layout.canvas.before:
            Color(0.08, 0.08, 0.12, 1)
            Rectangle(pos=self.layout.pos, size=Window.size)

        self.loading = Label(text="MEMUAT...", font_size='20sp', bold=True, color=(1,1,1,1))
        self.layout.add_widget(self.loading)

        if platform == 'android':
            from jnius import autoclass
            from android.permissions import request_permissions, Permission
            
            # Request Permissions (Tanpa Service Background nu bikin crash)
            def callback(permissions, results): pass
            request_permissions([
                Permission.POST_NOTIFICATIONS, 
                Permission.INTERNET, 
                Permission.READ_MEDIA_IMAGES
            ], callback)

            # Start Webview
            Clock.schedule_once(self.start_android_webview, 1.5)
            
        return self.layout

    def start_android_webview(self, dt):
        from jnius import autoclass, cast, PythonJavaClass, java_method
        from android.runnable import run_on_ui_thread

        activity = autoclass('org.kivy.android.PythonActivity').mActivity
        WebView = autoclass('android.webkit.WebView')
        WebViewClient = autoclass('android.webkit.WebViewClient')
        WebChromeClient = autoclass('android.webkit.WebChromeClient')
        CookieManager = autoclass('android.webkit.CookieManager')
        Context = autoclass('android.content.Context')
        NotificationManager = autoclass('android.app.NotificationManager')
        NotificationChannel = autoclass('android.app.NotificationChannel')
        NotificationCompat = autoclass('androidx.core.app.NotificationCompat$Builder')

        # Fungsi Notifikasi Native Android
        def show_native_notif(title, body):
            try:
                service = activity.getSystemService(Context.NOTIFICATION_SERVICE)
                manager = cast(NotificationManager, service)
                
                # Channel Wajib buat Android 8+
                chan_id = "rosyad_channel_id"
                chan = NotificationChannel(chan_id, "Rosyad Notif", 4) 
                manager.createNotificationChannel(chan)
                
                icon = activity.getApplicationInfo().icon
                builder = NotificationCompat(activity, chan_id)
                builder.setContentTitle(title)
                builder.setContentText(body)
                builder.setSmallIcon(icon)
                builder.setAutoCancel(True)
                builder.setPriority(1)
                
                manager.notify(1, builder.build())
            except Exception as e:
                print(f"Error Notif: {e}")

        # Interceptor (Penangkap Sinyal)
        class RosyadClient(WebViewClient):
            @java_method('(Landroid/webkit/WebView;Ljava/lang/String;)Z')
            def shouldOverrideUrlLoading(self, view, url):
                if url.startswith("rosyad://notif"):
                    try:
                        from urllib.parse import parse_qs, urlparse
                        parsed = urlparse(url)
                        params = parse_qs(parsed.query)
                        t = params.get('t', ['Info'])[0]
                        b = params.get('b', ['Pesan Baru'])[0]
                        show_native_notif(t, b)
                    except: pass
                    return True
                return False

            @java_method('(Landroid/webkit/WebView;Ljava/lang/String;)V')
            def onPageFinished(self, view, url):
                view.loadUrl(JS_BRIDGE) # Suntik JS
                super(RosyadClient, self).onPageFinished(view, url)

        @run_on_ui_thread
        def create_view():
            webview = WebView(activity)
            settings = webview.getSettings()
            settings.setJavaScriptEnabled(True)
            settings.setDomStorageEnabled(True)
            settings.setMixedContentMode(0) 
            settings.setUserAgentString("Mozilla/5.0 (Linux; Android 13; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36")
            
            CookieManager.getInstance().setAcceptCookie(True)
            CookieManager.getInstance().setAcceptThirdPartyCookies(webview, True)
            
            webview.setWebViewClient(RosyadClient())
            webview.setWebChromeClient(WebChromeClient())
            webview.loadUrl(TARGET_URL)
            activity.setContentView(webview)

        create_view()

if __name__ == '__main__':
    RosyadWebApp().run()
