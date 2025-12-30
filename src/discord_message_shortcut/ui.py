from __future__ import annotations

import os
import threading
import subprocess
from dataclasses import dataclass
from typing import Optional, List, Dict

import keyboard

from PySide6 import QtCore, QtGui, QtWidgets

from discord_message_shortcut.dms_manager import DMS_Manager


@dataclass(frozen=True)
class FieldSpec:
    key: str
    label: str
    required: bool


class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent: Optional[QtWidgets.QWidget], ui: "DmsUI") -> None:
        super().__init__(parent)
        self.ui = ui

        self.setWindowTitle("DMS Info")
        self.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint, True)

        # Refresh colors/values whenever config changes
        self.ui.configChanged.connect(self.refresh)

        layout = QtWidgets.QVBoxLayout(self)

        title = QtWidgets.QLabel("General Info")
        title.setStyleSheet("font-size: 16px; font-weight: 700;")
        layout.addWidget(title)

        grid = QtWidgets.QGridLayout()
        layout.addLayout(grid)

        grid.addWidget(self._hdr("Field"), 0, 0)
        grid.addWidget(self._hdr("Status"), 0, 1)
        grid.addWidget(self._hdr("Value"), 0, 2)
        grid.addWidget(self._hdr(""), 0, 3)

        self._rows: Dict[str, Dict[str, QtWidgets.QWidget]] = {}

        row = 1
        for spec in self.ui.fields:
            lbl = QtWidgets.QLabel(spec.label)
            status = QtWidgets.QLabel("")
            value = QtWidgets.QLabel("")
            value.setTextInteractionFlags(
                QtCore.Qt.TextInteractionFlag.TextSelectableByMouse
            )

            btn = QtWidgets.QPushButton("Edit")
            btn.clicked.connect(lambda _, s=spec: self.ui.edit_field(s))

            grid.addWidget(lbl, row, 0)
            grid.addWidget(status, row, 1)
            grid.addWidget(value, row, 2)
            grid.addWidget(btn, row, 3)

            self._rows[spec.key] = {"status": status, "value": value}
            row += 1

        layout.addSpacing(6)
        self.status_line = QtWidgets.QLabel("")
        self.status_line.setStyleSheet("font-weight: 700;")
        layout.addWidget(self.status_line)

        btns = QtWidgets.QHBoxLayout()
        layout.addLayout(btns)

        self.toggle_btn = QtWidgets.QPushButton("Toggle Active")
        self.toggle_btn.clicked.connect(self.ui.toggle_active)
        btns.addWidget(self.toggle_btn)

        btns.addStretch(1)

        self.setWindowFlag(QtCore.Qt.WindowType.Tool, True)
        self.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint, True)

        self.refresh()

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        # Do not quit the program when closing this window.
        event.ignore()
        self.hide()

    def _hdr(self, txt: str) -> QtWidgets.QLabel:
        w = QtWidgets.QLabel(txt)
        w.setStyleSheet("font-weight: 700;")
        return w

    def refresh(self) -> None:
        mgr = self.ui.manager

        for spec in self.ui.fields:
            val = (getattr(mgr, spec.key) or "").strip()
            ready = bool(val)

            status_lbl = self._rows[spec.key]["status"]
            value_lbl = self._rows[spec.key]["value"]

            if ready:
                status_lbl.setText("READY")
                status_lbl.setStyleSheet("color: #0a7a0a; font-weight: 700;")  # green
            else:
                status_lbl.setText("NOT SET")
                status_lbl.setStyleSheet("color: #b00020; font-weight: 700;")  # red

            shown = val
            if spec.key == "discord_token" and val:
                shown = (val[:4] + "..." + val[-4:]) if len(val) > 10 else "***"
            if spec.key == "latest_message" and len(shown) > 90:
                shown = shown[:87] + "..."
            value_lbl.setText(shown)

        # Bottom status line with color
        if self.ui.active:
            self.status_line.setText("Status: Active")
            self.status_line.setStyleSheet("color: #0a7a0a; font-weight: 800;")
        else:
            if self.ui.config_ready():
                self.status_line.setText("Status: Inactive (Config OK)")
                self.status_line.setStyleSheet("color: #b36b00; font-weight: 800;")
            else:
                self.status_line.setText("Status: Inactive (Missing Config)")
                self.status_line.setStyleSheet(
                    "color: #b00020; font-weight: 800;"
                )  # red


class DmsUI(QtCore.QObject):
    configChanged = QtCore.Signal()

    def __init__(
        self, manager: Optional[DMS_Manager] = None, icon_path: Optional[str] = None
    ) -> None:
        super().__init__()
        self.manager = manager or DMS_Manager()
        self.icon_path = icon_path

        self.active = False
        self._settings: Optional[SettingsDialog] = None

        self.fields: List[FieldSpec] = [
            FieldSpec("discord_token", "Discord Token", True),
            FieldSpec("discord_user_id", "Discord User Id", True),
            FieldSpec("latest_server_id", "Server Id", True),
            FieldSpec("latest_channel_id", "Channel Id", True),
            FieldSpec("latest_shortcut", "Shortcut", True),
            FieldSpec("latest_message", "Message", True),
        ]

        self._app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
        self._app.setQuitOnLastWindowClosed(False)

        self._tray = QtWidgets.QSystemTrayIcon()
        self._tray.setToolTip("DMS - Discord Message Shortcut")

        self._menu = QtWidgets.QMenu()

        # Whenever config changes, refresh everything (menu icons, tray badge, settings colors)
        self.configChanged.connect(self._refresh_everything)

        self._build_menu()
        self._tray.setContextMenu(self._menu)
        self._refresh_tray_icon()
        self._tray.show()

    # -------------------------
    # Public
    # -------------------------

    def run(self) -> None:
        self._app.exec()

    # -------------------------
    # Settings window
    # -------------------------

    def open_settings(self) -> None:
        if self._settings is None:
            self._settings = SettingsDialog(None, self)

        # Ensure window flags are applied (Windows can be finicky from tray)
        self._settings.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint, True)
        self._settings.setWindowFlag(
            QtCore.Qt.WindowType.Tool, True
        )  # helps staying above from tray
        self._settings.setWindowModality(QtCore.Qt.WindowModality.NonModal)

        self._settings.refresh()
        self._settings.show()
        self._settings.showNormal()

        # First attempt
        self._settings.raise_()
        self._settings.activateWindow()
        self._settings.setFocus()

        # Second attempt shortly after (works around Windows focus restrictions)
        def _force_front() -> None:
            if self._settings is None:
                return
            self._settings.raise_()
            self._settings.activateWindow()
            self._settings.setFocus()
            QtWidgets.QApplication.setActiveWindow(self._settings)

        QtCore.QTimer.singleShot(80, _force_front)
        QtCore.QTimer.singleShot(200, _force_front)

    def _refresh_settings(self) -> None:
        if self._settings is not None and self._settings.isVisible():
            self._settings.refresh()

    # -------------------------
    # Menu building
    # -------------------------

    def _open_env_location(self) -> None:
        path = os.path.abspath(self.manager.env_path)
        folder = os.path.dirname(path)
        try:
            subprocess.Popen(["explorer", folder], shell=True)
        except Exception as e:
            self._error("DMS", f"Failed to open env folder:\n\n{e}")

    def _build_menu(self) -> None:
        self._menu.clear()

        # Settings
        settings_action = QtGui.QAction("Open Settings...", self._menu)
        settings_action.triggered.connect(self.open_settings)
        self._menu.addAction(settings_action)

        self._menu.addSeparator()

        # General info submenu (click-to-edit)
        general = self._menu.addMenu("General info")
        for spec in self.fields:
            action = QtGui.QAction(self._field_menu_text(spec), self._menu)
            action.setIcon(self._status_icon(self._is_ready(spec.key)))
            action.triggered.connect(lambda _, s=spec: self.edit_field(s))
            general.addAction(action)

        general.addSeparator()

        env_action = QtGui.QAction("Open env folder", self._menu)
        env_action.triggered.connect(self._open_env_location)
        general.addAction(env_action)

        self._menu.addSeparator()

        # Status action
        status_action = QtGui.QAction(self._status_label(), self._menu)
        status_action.setIcon(
            self._status_icon(
                ok=self.active if self.active else self.config_ready(),
                missing=(not self.config_ready()) and (not self.active),
            )
        )
        status_action.triggered.connect(self.toggle_active)
        self._menu.addAction(status_action)

        self._menu.addSeparator()

        exit_action = QtGui.QAction("Exit", self._menu)
        exit_action.triggered.connect(self.exit_app)
        self._menu.addAction(exit_action)

    def _field_menu_text(self, spec: FieldSpec) -> str:
        if spec.key == "latest_shortcut":
            return f"{spec.label}: {self.manager.latest_shortcut}"
        if spec.key == "latest_message":
            msg = (self.manager.latest_message or "").strip()
            if len(msg) > 40:
                msg = msg[:37] + "..."
            return f"{spec.label}: {msg}"
        return f"{spec.label}: {'READY' if self._is_ready(spec.key) else 'NOT SET'}"

    def _status_label(self) -> str:
        if self.active:
            return "Status: Active"
        if self.config_ready():
            return "Status: Inactive (Config OK)"
        return "Status: Inactive (Missing Config)"

    # -------------------------
    # Editing
    # -------------------------

    def edit_field(self, spec: FieldSpec) -> None:
        current = (getattr(self.manager, spec.key) or "").strip()

        parent = (
            self._settings
            if (self._settings is not None and self._settings.isVisible())
            else None
        )

        value, ok = QtWidgets.QInputDialog.getText(
            parent,
            "DMS",
            f"Set {spec.label}:",
            QtWidgets.QLineEdit.EchoMode.Normal,
            current,
        )
        if not ok:
            return

        value = value.strip()
        old_shortcut = (self.manager.latest_shortcut or "").strip()

        self._persist_field(spec.key, value)

        # Rebind hotkey only if shortcut changed and we are active
        if self.active and spec.key == "latest_shortcut":
            new_shortcut = (self.manager.latest_shortcut or "").strip()
            if new_shortcut != old_shortcut:
                self._bind_hotkey()

        # If config becomes invalid while active -> deactivate
        if self.active and not self.config_ready():
            self._unbind_hotkey()
            self.active = False
            self._error("DMS", "Config changed and became invalid. Deactivating.")

        # One single refresh trigger (updates READY colors immediately)
        self.configChanged.emit()

    def _persist_field(self, key: str, value: str) -> None:
        if key == "discord_token":
            self.manager.save_to_env(discord_token=value)
        elif key == "discord_user_id":
            self.manager.save_to_env(discord_user_id=value)
        elif key == "latest_server_id":
            self.manager.save_to_env(server_id=value)
        elif key == "latest_channel_id":
            self.manager.save_to_env(channel_id=value)
        elif key == "latest_shortcut":
            self.manager.save_to_env(latest_shortcut=value)
        elif key == "latest_message":
            self.manager.save_to_env(latest_message=value)

        # Reload first, then signal refresh so READY/NOT SET reflects the new value immediately
        self.manager.reload_from_env()

    # -------------------------
    # Active / Inactive
    # -------------------------

    def toggle_active(self) -> None:
        if keyboard is None:
            self._error(
                "DMS",
                "Global hotkey backend not available.\n\nInstall:\n  pip install keyboard\n\n"
                "Note: on some systems it may require admin privileges.",
            )
            return

        if not self.active:
            missing = self.missing_required_fields()
            if missing:
                self._error(
                    "DMS",
                    "Cannot activate. Missing required configuration:\n\n"
                    + "\n".join(f"- {m}" for m in missing),
                )
                return
            self.active = True
            self._bind_hotkey()
        else:
            self.active = False
            self._unbind_hotkey()

        self.configChanged.emit()

    def _bind_hotkey(self) -> None:
        if keyboard is None:
            return

        self._unbind_hotkey()

        shortcut = (self.manager.latest_shortcut or "").strip()
        if not shortcut:
            self.active = False
            self._error("DMS", "Shortcut is empty.")
            return

        def _callback() -> None:
            threading.Thread(
                target=self._send_current_message_safely, daemon=True
            ).start()

        try:
            keyboard.add_hotkey(shortcut, _callback)
        except Exception as e:
            self.active = False
            self._error("DMS", f"Failed to register hotkey '{shortcut}':\n\n{e}")

    def _unbind_hotkey(self) -> None:
        if keyboard is None:
            return
        try:
            keyboard.clear_all_hotkeys()
        except Exception:
            pass

    def _send_current_message_safely(self) -> None:
        try:
            self.manager.send_message(self.manager.latest_message)
        except Exception as e:
            self._error("DMS", f"Failed to send message:\n\n{e}")

    # -------------------------
    # Validation / status
    # -------------------------

    def _is_ready(self, attr: str) -> bool:
        return bool((getattr(self.manager, attr) or "").strip())

    def missing_required_fields(self) -> List[str]:
        missing: List[str] = []
        for spec in self.fields:
            if spec.required and not self._is_ready(spec.key):
                missing.append(spec.label)
        return missing

    def config_ready(self) -> bool:
        return len(self.missing_required_fields()) == 0

    # -------------------------
    # Tray icon visuals
    # -------------------------

    def _refresh_tray_icon(self) -> None:
        base = (
            self._load_base_pixmap(self.icon_path)
            if self.icon_path
            else self._default_base_pixmap()
        )

        if self.active:
            badge = QtGui.QColor(10, 122, 10)  # green
        else:
            badge = (
                QtGui.QColor(176, 0, 32)
                if not self.config_ready()
                else QtGui.QColor(179, 107, 0)
            )  # red/amber

        icon = self._pixmap_with_badge(base, badge)
        self._tray.setIcon(QtGui.QIcon(icon))

    def _status_icon(self, ok: bool, missing: bool = False) -> QtGui.QIcon:
        if missing:
            color = QtGui.QColor(176, 0, 32)
        else:
            color = QtGui.QColor(10, 122, 10) if ok else QtGui.QColor(176, 0, 32)
        pix = QtGui.QPixmap(14, 14)
        pix.fill(QtCore.Qt.GlobalColor.transparent)
        p = QtGui.QPainter(pix)
        p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
        p.setBrush(QtGui.QBrush(color))
        p.setPen(QtCore.Qt.PenStyle.NoPen)
        p.drawEllipse(1, 1, 12, 12)
        p.end()
        return QtGui.QIcon(pix)

    def _load_base_pixmap(self, path: str) -> QtGui.QPixmap:
        pm = QtGui.QPixmap(path)
        if pm.isNull():
            return self._default_base_pixmap()
        return pm.scaled(
            64,
            64,
            QtCore.Qt.AspectRatioMode.KeepAspectRatio,
            QtCore.Qt.TransformationMode.SmoothTransformation,
        )

    def _default_base_pixmap(self) -> QtGui.QPixmap:
        pm = QtGui.QPixmap(64, 64)
        pm.fill(QtCore.Qt.GlobalColor.transparent)
        p = QtGui.QPainter(pm)
        p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
        p.setBrush(QtGui.QBrush(QtGui.QColor(60, 60, 60)))
        p.setPen(QtCore.Qt.PenStyle.NoPen)
        p.drawEllipse(4, 4, 56, 56)
        p.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255)))
        f = QtGui.QFont("Segoe UI", 24, 700)
        p.setFont(f)
        p.drawText(pm.rect(), QtCore.Qt.AlignmentFlag.AlignCenter, "D")
        p.end()
        return pm

    def _pixmap_with_badge(
        self, base: QtGui.QPixmap, badge_color: QtGui.QColor
    ) -> QtGui.QPixmap:
        pm = QtGui.QPixmap(64, 64)
        pm.fill(QtCore.Qt.GlobalColor.transparent)

        p = QtGui.QPainter(pm)
        p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)

        p.drawPixmap(
            0,
            0,
            base.scaled(
                64,
                64,
                QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                QtCore.Qt.TransformationMode.SmoothTransformation,
            ),
        )

        p.setBrush(QtGui.QBrush(badge_color))
        p.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255), 2))
        p.drawEllipse(44, 44, 16, 16)

        p.end()
        return pm

    # -------------------------
    # Refresh / Exit
    # -------------------------

    def _refresh_everything(self) -> None:
        self._build_menu()
        self._tray.setContextMenu(
            self._menu
        )  # helps Windows apply updates consistently
        self._refresh_tray_icon()
        self._refresh_settings()
        QtWidgets.QApplication.processEvents()

    def exit_app(self) -> None:
        self.active = False
        self._unbind_hotkey()
        self._tray.hide()
        self._app.quit()

    # -------------------------
    # Dialog helpers
    # -------------------------

    def _error(self, title: str, text: str) -> None:
        QtWidgets.QMessageBox.critical(None, title, text)
