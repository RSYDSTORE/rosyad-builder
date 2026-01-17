
from kivy.app import App
from kivy.utils import platform
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle

TARGET_URL = "https://topup-bussid-trucksid-rsyd-store.vercel.app"

JS_BRIDGE = """
javascript:(function() {
    window.show_rosyad_push_notif = function(t, b) {
        window.location.href = "rosyad://notif?t=" + encodeURIComponent(t) + "&b=" + encodeURIComponent(b);
    };
})()
"""

class RosyadWebApp(App):
    def build(self):
        self.layout = FloatLayout()
        with self.layout.canvas.before:
            Color(0.08, 0.08, 0.12, 1)
            Rectangle(pos=self.layout.pos, size=Window.size)
        self.loading = Label(text="MEMUAT...", font_size='22sp', bold=True, pos_hint={'center_x':0.5, 'center_y':0.5})
        self.layout.add_widget(self.loading)

        if platform == 'android':
            from android.permissions import request_permissions, Permission
            # REQUEST ALL PERMISSIONS AT STARTUP
            perms = [Permission.INTERNET, Permission.POST_NOTIFICATIONS,Permission.ACCESS_FINE_LOCATION,Permission.READ_MEDIA_IMAGES,Permission.WRITE_EXTERNAL_STORAGE]
            request_permissions(perms)
            Clock.schedule_once(self.start_webview, 2.5)
        return self.layout

    def start_webview(self, dt):
        try:
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

            def show_notif(title, body):
                try:
                    service = activity.getSystemService(Context.NOTIFICATION_SERVICE)
                    manager = cast(NotificationManager, service)
                    chan = NotificationChannel("default", "Notifikasi", 4)
                    manager.createNotificationChannel(chan)
                    builder = NotificationCompat(activity, "default")
                    builder.setContentTitle(title)
                    builder.setContentText(body)
                    builder.setSmallIcon(activity.getApplicationInfo().icon)
                    builder.setAutoCancel(True)
                    manager.notify(1, builder.build())
                except: pass

            class RosyadClient(WebViewClient):
                @java_method('(Landroid/webkit/WebView;Ljava/lang/String;)Z')
                def shouldOverrideUrlLoading(self, view, url):
                    if url.startswith("rosyad://notif"):
                        try:
                            from urllib.parse import parse_qs, urlparse
                            parsed = urlparse(url)
                            t = parse_qs(parsed.query).get('t', ['Info'])[0]
                            b = parse_qs(parsed.query).get('b', ['Pesan'])[0]
                            show_notif(t, b)
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
                settings.setUserAgentString("Mozilla/5.0 (Linux; Android 14; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36")
                CookieManager.getInstance().setAcceptCookie(True)
                webview.setWebViewClient(RosyadClient())
                webview.setWebChromeClient(WebChromeClient())
                webview.loadUrl(TARGET_URL)
                activity.setContentView(webview)
            create_view()
        except: pass

if __name__ == '__main__':
    RosyadWebApp().run()
