from PySide6 import QtCore
import ctypes
import ctypes.wintypes


class SessionNotificationWindow(QtCore.QObject):
    """
    This class registers for session change notifications using the
    WTSRegisterSessionNotification API.
    """

    def __init__(self, app):
        super().__init__()
        self._widget = QtCore.QObject()
        self._window = QtCore.QCoreApplication.instance().allWindows()

        # Create a hidden QWidget to get a HWND
        from PySide6.QtWidgets import QWidget

        self.widget = QWidget()
        self.widget.setAttribute(QtCore.Qt.WidgetAttribute.WA_DontShowOnScreen)
        self.widget.show()

        hwnd = int(self.widget.winId())
        self._register(hwnd)

    def _register(self, hwnd: int):
        WTSRegisterSessionNotification = (
            ctypes.windll.wtsapi32.WTSRegisterSessionNotification
        )
        WTSRegisterSessionNotification.argtypes = [
            ctypes.wintypes.HWND,
            ctypes.wintypes.DWORD,
        ]
        WTSRegisterSessionNotification.restype = ctypes.wintypes.BOOL

        NOTIFY_FOR_THIS_SESSION = 0
        if not WTSRegisterSessionNotification(hwnd, NOTIFY_FOR_THIS_SESSION):
            raise ctypes.WinError()


class WindowsSessionEventFilter(QtCore.QAbstractNativeEventFilter):
    """
    A native event filter to detect Windows session lock and logoff events.
    This class will be used to fix keyboard input not being detected when the
    Windows session is locked and then unlocked.
    """

    def __init__(self, on_session_lost):
        super().__init__()
        self.on_session_lost = on_session_lost

    def nativeEventFilter(self, eventType, message):
        if eventType != "windows_generic_MSG":
            return False, 0

        msg = ctypes.wintypes.MSG.from_address(message.__int__())

        WM_WTSSESSION_CHANGE = 0x02B1
        WTS_SESSION_LOCK = 0x7
        WTS_SESSION_LOGOFF = 0x6

        if msg.message == WM_WTSSESSION_CHANGE:
            if msg.wParam in (WTS_SESSION_LOCK, WTS_SESSION_LOGOFF):
                self.on_session_lost()

        return False, 0
