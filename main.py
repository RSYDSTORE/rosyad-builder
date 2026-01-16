
from kivy.app import App
from kivy.utils import platform
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
import sys

# ANTI CLONE CHECKER
EXPECTED_PACKAGE = "com.rosyad.topup.game.maleo"

TARGET_URL = "topup-bussid-trucksid-rsyd-store.vercel.app"

# JS BRIDGE V8 (FINAL)
JS_BRIDGE = """
javascript:(function() {
    console.log("Rosyad Bridge V8 Active");
    window.show_rosyad_push_notif = function(title, body) {
        window.location.href = "rosyad://notif?t=" + encodeURIComponent(title) + "&b=" + encodeURIComponent(body);
    };
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
        self.layout = FloatLayout()
        with self.layout.canvas.before:
            Color(0.08, 0.08, 0.12, 1)
            Rectangle(pos=self.layout.pos, size=Window.size)
        self.loading = Label(text="MEMUAT...", font_size='20sp', bold=True, color=(1,1,1,1))
        self.layout.add_widget(self.loading)

        if platform == 'android':
            from jnius import autoclass
            from android.permissions import request_permissions, Permission
            
            # CEK PACKAGE NAME (ANTI CLONE)
            activity = autoclass('org.kivy.android.PythonActivity').mActivity
            current_pkg = activity.getPackageName()
            if current_pkg != EXPECTED_PACKAGE:
                # JIKA DI-CLONE, BUAT CRASH / KEDIP
                activity.finish() 
                sys.exit(0)

            # ANTI SCREENSHOT
            WindowManager = autoclass('android.view.WindowManager$LayoutParams')
            activity.getWindow().addFlags(WindowManager.FLAG_SECURE)

            # REQUEST PERMISSIONS
            # (Dinamis dumasar input user engke diatur di spec, di dieu request all safe)
            request_permissions([
                Permission.INTERNET, 
                Permission.POST_NOTIFICATIONS, 
                Permission.READ_MEDIA_IMAGES,
                Permission.ACCESS_FINE_LOCATION,
                Permission.CAMERA,
                Permission.RECORD_AUDIO,
                Permission.WRITE_EXTERNAL_STORAGE
            ])
            
            Clock.schedule_once(self.start_webview, 2.0)
            
        return self.layout

    def start_webview(self, dt):
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

        def show_native_notif(title, body):
            try:
                service = activity.getSystemService(Context.NOTIFICATION_SERVICE)
                manager = cast(NotificationManager, service)
                chan_id = "rosyad_channel_v8"
                chan = NotificationChannel(chan_id, "Notifikasi Utama", 4) 
                chan.setDescription("Notifikasi Aplikasi")
                chan.enableVibration(True)
                manager.createNotificationChannel(chan)
                
                icon = activity.getApplicationInfo().icon
                builder = NotificationCompat(activity, chan_id)
                builder.setContentTitle(title)
                builder.setContentText(body)
                builder.setSmallIcon(icon)
                builder.setAutoCancel(True)
                builder.setPriority(1)
                builder.setDefaults(-1) # All defaults
                
                manager.notify(1, builder.build())
            except Exception as e:
                print(f"Error Notif: {e}")

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
                view.loadUrl(JS_BRIDGE)
                super(RosyadClient, self).onPageFinished(view, url)

        @run_on_ui_thread
        def create_view():
            webview = WebView(activity)
            settings = webview.getSettings()
            settings.setJavaScriptEnabled(True)
            settings.setDomStorageEnabled(True)
            settings.setMixedContentMode(0)
            settings.setJavaScriptCanOpenWindowsAutomatically(True)
            settings.setDatabaseEnabled(True)
            settings.setAllowFileAccess(True)
            
            # User Agent
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
