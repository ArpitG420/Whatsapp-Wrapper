import ctypes
import os
import sys
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices, QIcon, QPixmap
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSystemTrayIcon, QSizeGrip, QFileDialog
)
def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        return os.path.join(sys._MEIPASS, relative_path)
    
    # In development: relative_path is relative to the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(project_root, relative_path)
if sys.platform == "win32":
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("WhatsApp.Desktop.App")
    except Exception:
        pass

# Performance flags to force GPU hardware acceleration
sys.argv.append("--enable-gpu")
sys.argv.append("--ignore-gpu-blocklist")
sys.argv.append("--enable-smooth-scrolling")
sys.argv.append("--enable-zero-copy")


class CustomWebPage(QWebEnginePage):
    def __init__(self, profile, parent=None):
        super().__init__(profile, parent)

    def acceptNavigationRequest(self, url, nav_type, is_main_frame):
        if nav_type == QWebEnginePage.NavigationType.NavigationTypeLinkClicked:
            QDesktopServices.openUrl(url)
            return False
        return super().acceptNavigationRequest(url, nav_type, is_main_frame)

    def createWindow(self, window_type):
        new_page = ExternalBrowserPage(self.profile(), self)
        return new_page


class ExternalBrowserPage(QWebEnginePage):
    def acceptNavigationRequest(self, url, nav_type, is_main_frame):
        QDesktopServices.openUrl(url)
        return False


class CustomTitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(12, 0, 0, 0)
        self.layout.setSpacing(8)
        
        self.setStyleSheet("background-color: #202c33; color: #aebac1;")
        self.setFixedHeight(40)
        
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(18, 18)
        self.icon_label.setScaledContents(True)
        self.icon_label.setStyleSheet("background: transparent;")
        
        self.title_label = QLabel("WhatsApp")
        self.title_label.setStyleSheet("font-weight: 670; font-family: 'Segoe UI', sans-serif; font-size: 14pt; color: #e9edef; background: transparent;")
        
        self.min_btn = QPushButton("—")
        self.max_btn = QPushButton("🗖")
        self.close_btn = QPushButton("✕")
        
        for btn in [self.min_btn, self.max_btn, self.close_btn]:
            btn.setFixedSize(46, 40)
            btn.setStyleSheet("""
                QPushButton { border: none; background-color: transparent; color: #aebac1; font-family: 'Segoe UI'; font-size: 9pt; }
                QPushButton:hover { background-color: #374248; color: #ffffff; }
            """)
            
        self.close_btn.setStyleSheet("""
            QPushButton { border: none; background-color: transparent; color: #aebac1; font-family: 'Segoe UI'; font-size: 10pt; }
            QPushButton:hover { background-color: #e81123; color: #ffffff; }
        """)
            
        self.layout.addWidget(self.icon_label)
        self.layout.addWidget(self.title_label)
        self.layout.addStretch()
        self.layout.addWidget(self.min_btn)
        self.layout.addWidget(self.max_btn)
        self.layout.addWidget(self.close_btn)
        
        self.min_btn.clicked.connect(self.parent.showMinimized)
        self.max_btn.clicked.connect(self.parent.toggle_maximized_state)
        self.close_btn.clicked.connect(self.parent.close)
        
        self.start_pos = None

    def toggle_max(self):
        self.parent.toggle_maximized_state()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.start_pos and not self.parent.isMaximized():
            delta = event.globalPosition().toPoint() - self.start_pos
            self.parent.move(self.parent.pos() + delta)
            self.start_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.start_pos = None


class WhatsAppApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WhatsApp")
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setGeometry(100, 100, 1200, 800)

        # Resolve icon path across dev and PyInstaller environments
        icon_path = get_resource_path(os.path.join("assets", "whatsapp.ico"))

        self.app_icon = QIcon(icon_path)
        self.setWindowIcon(self.app_icon)

        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(self.app_icon)
        self.tray.show()

        profile_path = os.path.join(os.path.expanduser("~"), ".whatsapp_app_profile")
        self.profile = QWebEngineProfile("WhatsAppProfile", self)
        self.profile.setPersistentStoragePath(profile_path)
        self.profile.setCachePath(profile_path)
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
        self.profile.setHttpUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")
        
        # Keep tracking downloads safely to prevent C++ garbage-collection crashes
        self.active_downloads = set()
        self.profile.downloadRequested.connect(self.handle_download_requested)

        self.browser = QWebEngineView(self)
        self.web_page = CustomWebPage(self.profile, self.browser)
        
        self.web_page.featurePermissionRequested.connect(self.handle_feature_permission)
        self.browser.setPage(self.web_page)

        settings = self.browser.settings()
        settings.setAttribute(settings.WebAttribute.ScrollAnimatorEnabled, True)
        self.browser.loadFinished.connect(self.inject_scroll_fix)

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.title_bar = CustomTitleBar(self)
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                self.title_bar.icon_label.setPixmap(pixmap.scaled(18, 18, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            
        layout.addWidget(self.title_bar)
        layout.addWidget(self.browser)
        self.setCentralWidget(central_widget)
        
        self.grip = QSizeGrip(self)
        self.grip.resize(15, 15)

        self.browser.setUrl(QUrl("https://web.whatsapp.com"))

    def handle_download_requested(self, download):
        path, _ = QFileDialog.getSaveFileName(self, "Save File", download.suggestedFileName())
        if path:
            download.setDownloadDirectory(os.path.dirname(path))
            download.setDownloadFileName(os.path.basename(path))
            
            # Prevent C++ object premature garbage collection by storing pointer
            self.active_downloads.add(download)
            
            # Connect using stateChanged (PyQt6 native signal)
            def on_state_changed(state):
                if state == download.DownloadState.DownloadCompleted:
                    if download in self.active_downloads:
                        self.active_downloads.remove(download)
                    QDesktopServices.openUrl(QUrl.fromLocalFile(path))
                elif state == download.DownloadState.DownloadCancelled or state == download.DownloadState.DownloadInterrupted:
                    if download in self.active_downloads:
                        self.active_downloads.remove(download)

            download.stateChanged.connect(on_state_changed)
            download.accept()
        else:
            download.cancel()

    def showEvent(self, event):
        super().showEvent(event)
        self.set_window_rounded_corners(True)

    def toggle_maximized_state(self):
        if self.isMaximized():
            self.showNormal()
            self.set_window_rounded_corners(True)
            self.grip.show()
        else:
            self.showMaximized()
            self.set_window_rounded_corners(False)
            self.grip.hide()

    def set_window_rounded_corners(self, enable: bool):
        try:
            hwnd = int(self.winId())
            DWMWA_WINDOW_CORNER_PREFERENCE = 33
            preference = 2 if enable else 1
            value = ctypes.c_int(preference)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, 
                DWMWA_WINDOW_CORNER_PREFERENCE, 
                ctypes.byref(value), 
                ctypes.sizeof(value)
            )
        except Exception:
            pass

    def resizeEvent(self, event):
        self.grip.move(self.width() - 15, self.height() - 15)
        super().resizeEvent(event)

    def handle_feature_permission(self, origin, feature):
        if feature == QWebEnginePage.Feature.Notifications:
            self.web_page.setFeaturePermission(origin, feature, QWebEnginePage.PermissionPolicy.PermissionGrantedByUser)

    def inject_scroll_fix(self, ok):
        if ok:
            scroll_fix_js = """
                const style = document.createElement('style');
                style.innerHTML = `
                    * { -webkit-overflow-scrolling: touch; }
                    div[data-testid="conversation-panel-messages"] {
                        transform: translateZ(0);
                        will-change: scroll-position;
                    }
                `;
                document.head.appendChild(style);
            """
            self.browser.page().runJavaScript(scroll_fix_js)


app = QApplication(sys.argv)
window = WhatsAppApp()
window.show()
sys.exit(app.exec())
