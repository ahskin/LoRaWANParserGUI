from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
"""
    2022-05-24 加入图标
"""
class BubbleTip(QWidget):

    TYPE_OK = 0
    TYPE_ONGOING = 1
    TYPE_ERR = 2
    TYPE_WARNING = 3

    def __init__(self, attach_form: QWidget, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.WindowTransparentForInput | Qt.WindowType.ToolTip)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.attach_form = attach_form

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(7, 3, 7, 3)

        self.label_tip = QLabel("")
        self.label_tip.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter)

        self.label_icon = QLabel()

        base_style = """
            font-family: 微软雅黑;
            font-weight: bold;
            font-size: 15pt;
            padding: 0px;
        """

        self.type_map = {
            BubbleTip.TYPE_OK: {
                "style": "QLabel{" + f"{base_style}color: #67c23a; background-color: none;" + "}",
                "frame_bg_color": QColor(0xf0, 0xf9, 0xeb),
                "icon": "./res/ok_32.png"
            },
            BubbleTip.TYPE_ONGOING: {
                "style": "QLabel{" + f"{base_style}color: #e6a23c; background-color: none;" + "}",
                "frame_bg_color": QColor(0xfd, 0xf6, 0xec),
                "icon": "./res/ongoing_32.png"
            },
            BubbleTip.TYPE_ERR: {
                "style": "QLabel{" + f"{base_style}color: #f56c6c; background-color: none; " + "}",
                "frame_bg_color": QColor(0xfe, 0xf0, 0xf0),
                "icon": "./res/error_32.png"
            },
            BubbleTip.TYPE_WARNING: {
                "style": "QLabel{" + f"{base_style}color: #e6a23c; background-color: none;" + "}",
                "frame_bg_color": QColor(0xfd, 0xf6, 0xec),
                "icon": "./res/warning_32.png"
            }
        }
        # 背景色
        self.frame_background_color = self.type_map.get(BubbleTip.TYPE_OK).get("frame_bg_color")

        self.layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.layout.addWidget(self.label_icon)
        self.layout.addWidget(self.label_tip)
        self.layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.timer_hide = None

        self.hide()

    def paintEvent(self, e: QPaintEvent):
        p = QPainter(self)
        p.setRenderHint(p.RenderHint.Antialiasing)
        p.setBrush(QBrush(self.frame_background_color))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(self.rect(), 9, 9)

    def start_show(self, bubble_type, tip, timeout=0):
        self.frame_background_color = self.type_map.get(bubble_type).get("frame_bg_color")
        self.label_icon.setPixmap(QPixmap(self.type_map.get(bubble_type).get("icon")))
        self.setStyleSheet(self.type_map.get(bubble_type).get("style"))

        self.label_tip.setText(tip)

        # 设置初始位置在附着的窗口中部
        # 需要先show，self.width()的值才能正常更新
        self.show()
        center_x = round(self.attach_form.x() + (self.attach_form.width() / 2) - (self.width() / 2))
        self.move(center_x, self.attach_form.y() + 20)


        # 设置动画 从上往下移动
        self.animation = QPropertyAnimation(self)
        self.animation.setTargetObject(self)
        self.animation.setPropertyName(b"pos")
        self.animation.setDuration(500)
        self.animation.setStartValue(QPoint(self.x(), self.y()))
        self.animation.setEndValue(QPoint(self.x(), self.y() + 70))
        self.animation.start()

        # 定时关闭窗口
        if timeout != 0:
            self.timer_hide = QTimer()
            self.timer_hide.timeout.connect(self.on_timeout_to_hide)
            self.timer_hide.start(timeout)
        else:
            if self.timer_hide:
                self.timer_hide.stop()

    def on_timeout_to_hide(self):
        self.timer_hide.stop()
        self.hide()




