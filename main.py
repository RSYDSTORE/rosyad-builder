
from kivy.app import App
from kivy.utils import platform
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition

TARGET_URL = "topup-bussid-trucksid-rsyd-store.vercel.app"
EXPECTED_PKG = "com.top.up.games.maleo"

# --- JS INTERCEPTOR (FIX NOTIFICATION) ---
JS_BRIDGE = """
javascript:(function() {
    window.show_rosyad_push_notif = function(title, body) {
        window.location.href = "rosyad://notif?t=" + encodeURIComponent(title) + "&b=" + encodeURIComponent(body);
    };
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.ready.then(function(reg) {
            reg.showNotification = function(title, options) {
                var b = options.body || '';
                window.location.href = "rosyad://notif?t=" + encodeURIComponent(title) + "&b=" + encodeURIComponent(b);
            };
        });
    }
})()
"""

class LoadingScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(0.08, 0.08, 0.12, 1)
            Rectangle(pos=self.pos, size=self.size)
        
        self.layout = FloatLayout()
        self.lbl = Label(text="MEMUAT...", font_size='22sp', bold=True, pos_hint={'center_x':0.5, 'center_y':0.55})
        self.footer = Label(text="RsydStore || All Right Reserved 2024", font_size='12sp', color=(0.5,0.5,0.5,1), pos_hint={'center_x':0.5, 'y':0.05})
        
        self.layout.add_widget(self.lbl)
        self.layout.add_widget(self.footer)
        self.add_widget(self.layout)
        
        Clock.schedule_once(self.go_to_web, 3.0) 

    def go_to_web(self, dt):
        self.manager.current = 'web'

class WebScreen(Screen):
    def on_enter(self):
        start_webview()

class RosyadWebApp(App):
    def build(self):
        # 1. ANTI-CLONE & SECURITY (FIRST THING)
        self.check_integrity()
        
        sm = ScreenManager(transition=NoTransition())
        sm.add_widget(LoadingScreen(name='loading'))
        sm.add_widget(WebScreen(name='web'))
        return sm

    def check_integrity(self):
        if platform == 'android':
            from jnius import autoclass
            from android.runnable import run_on_ui_thread
            
            activity = autoclass('org.kivy.android.PythonActivity').mActivity
            
            # ANTI-SCREENSHOT (FLAG_SECURE)
            @run_on_ui_thread
            def secure_window():
                WindowManager = autoclass('android.view.WindowManager$LayoutParams')
                activity.getWindow().addFlags(WindowManager.FLAG_SECURE)
            secure_window()

            # ANTI-CLONE (CHECK PACKAGE NAME)
            pkg = activity.getPackageName()
            if pkg != EXPECTED_PKG:
                self.crash_app()

    def crash_app(self):
        # Efek berkedip & crash untuk cloner
        Clock.schedule_interval(self.flash_screen, 0.1)
    
    def flash_screen(self, dt):
        from random import random
        Window.clearcolor = (random(), random(), random(), 1)
        # Force Exit after 2 seconds
        import sys
        sys.exit()

def start_webview():
    if platform == 'android':
        from jnius import autoclass, cast, PythonJavaClass, java_method
        from android.runnable import run_on_ui_thread
        from android.permissions import request_permissions, Permission

        activity = autoclass('org.kivy.android.PythonActivity').mActivity
        
        # PERMISSIONS REQUEST
        def callback(permissions, results): pass
        request_permissions([Permission.POST_NOTIFICATIONS], callback)

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
                chan_id = "rosyad_channel_v8"
                chan = NotificationChannel(chan_id, "Rosyad Notif", 4)
                manager.createNotificationChannel(chan)
                
                # USE SYSTEM ICON TO PREVENT CRASH
                icon = activity.getApplicationInfo().icon
                
                builder = NotificationCompat(activity, chan_id)
                builder.setContentTitle(title)
                builder.setContentText(body)
                builder.setSmallIcon(icon)
                builder.setAutoCancel(True)
                builder.setPriority(1)
                manager.notify(1, builder.build())
            except: pass

        class RosyadClient(WebViewClient):
            @java_method('(Landroid/webkit/WebView;Ljava/lang/String;)Z')
            def shouldOverrideUrlLoading(self, view, url):
                if url.startswith("rosyad://notif"):
                    try:
                        from urllib.parse import parse_qs, urlparse
                        parsed = urlparse(url)
                        params = parse_qs(parsed.query)
                        show_notif(params.get('t',[''])[0], params.get('b',[''])[0])
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
            settings.setUserAgentString("Mozilla/5.0 (Linux; Android 14; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36")
            
            CookieManager.getInstance().setAcceptCookie(True)
            CookieManager.getInstance().setAcceptThirdPartyCookies(webview, True)
            
            webview.setWebViewClient(RosyadClient())
            webview.setWebChromeClient(WebChromeClient())
            webview.loadUrl(TARGET_URL)
            activity.setContentView(webview)
        
        create_view()

if __name__ == '__main__':
    RosyadWebApp().run()
