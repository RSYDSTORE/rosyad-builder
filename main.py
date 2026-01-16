
from kivy.app import App
from kivy.utils import platform
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle

TARGET_URL = "https://www.topupbussidrsydstore.my.id"

class RosyadWebApp(App):
    def build(self):
        self.layout = FloatLayout()
        with self.layout.canvas.before:
            Color(0.08, 0.08, 0.12, 1)
            Rectangle(pos=self.layout.pos, size=Window.size)
        self.loading = Label(text="MEMUAT...", font_size='20sp', bold=True, color=(1,1,1,1))
        self.layout.add_widget(self.loading)

        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.INTERNET, Permission.POST_NOTIFICATIONS, Permission.READ_MEDIA_IMAGES])
            Clock.schedule_once(self.start_webview, 1.5)
        return self.layout

    def start_webview(self, dt):
        from jnius import autoclass
        from android.runnable import run_on_ui_thread
        activity = autoclass('org.kivy.android.PythonActivity').mActivity
        WebView = autoclass('android.webkit.WebView')
        WebViewClient = autoclass('android.webkit.WebViewClient')
        WebChromeClient = autoclass('android.webkit.WebChromeClient')
        CookieManager = autoclass('android.webkit.CookieManager')
        
        @run_on_ui_thread
        def create_view():
            webview = WebView(activity)
            settings = webview.getSettings()
            settings.setJavaScriptEnabled(True)
            settings.setDomStorageEnabled(True)
            settings.setMixedContentMode(0)
            settings.setUserAgentString("Mozilla/5.0 (Linux; Android 13; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36")
            CookieManager.getInstance().setAcceptCookie(True)
            webview.setWebViewClient(WebViewClient())
            webview.setWebChromeClient(WebChromeClient())
            webview.loadUrl(TARGET_URL)
            activity.setContentView(webview)
        create_view()

if __name__ == '__main__':
    RosyadWebApp().run()
