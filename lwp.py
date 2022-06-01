import re
import sys

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from lwp_ui import Ui_Form

from lwp_cmd import *
from bubble_tip import BubbleTip
from console_ctrl import ConsoleCtrl

NAME = "LoRaWAN协议解析工具"
VERSION = "V1.0.0"
DATE = "2022-06-01"


class Form(QWidget, Ui_Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        ConsoleCtrl.hide_console()

        self.setWindowTitle(f"{NAME} {VERSION} {DATE}")
        self.setWindowIcon(QIcon("res/icon.ico"))

        self.labelPic.setPixmap(QPixmap("res/LoRaWAN-logo.png"))

        self.log_init()

        version = LwpCmd.get_ver().replace("\r", "").replace("\n", "")
        self.labelLwpVer.setText(f"内核版本 v{version}")

        self.radioButtonMac.toggled.connect(self.on_select_item_changed)
        self.radioButtonPayload.toggled.connect(self.on_select_item_changed)
        self.radioButtonJRJA.toggled.connect(self.on_select_item_changed)

        self.radioButtonDownlink.toggled.connect(lambda: self.on_maccmd_changed(self.lineEditMaccmd.text()))
        self.radioButtonUplink.toggled.connect(lambda: self.on_maccmd_changed(self.lineEditMaccmd.text()))

        self.radioButtonJRJA.setChecked(True)
        self.radioButtonDownlink.setChecked(True)

        self.lineEditJoinRequest.textChanged.connect(self.on_jr_ja_appkey_changed)
        self.lineEditJoinAnswer.textChanged.connect(self.on_jr_ja_appkey_changed)
        self.lineEditAppkey.textChanged.connect(self.on_jr_ja_appkey_changed)

        self.lineEditMaccmd.textChanged.connect(self.on_maccmd_changed)

        self.lineEditAppkey.textChanged.connect(self.on_payload_changed)
        self.lineEditPayload.textChanged.connect(self.on_payload_changed)
        self.lineEditPayload.textChanged.connect(self.on_payload_changed)

        self.resize(1320, 800)

        self.bubble_tip = BubbleTip(self)

    def log_init(self):
        logger.add("./log/client_{time:YYYY-MM-DD}.log", rotation="00:00", encoding="utf-8")

    def on_select_item_changed(self, checked):
        if not checked:
            return
        item_map = {
            self.radioButtonJRJA: 0,
            self.radioButtonPayload: 1,
            self.radioButtonMac: 2,
        }
        radio: QRadioButton = self.sender()
        if radio in item_map:
            self.stackedWidget.setCurrentIndex(item_map.get(radio))

    def on_maccmd_changed(self, data):
        if not data:
            return
        if self.radioButtonDownlink.isChecked():
            self.textEditAck.setText(LwpCmd.parse_dl_maccmd(data))
        else:
            self.textEditAck.setText(LwpCmd.parse_ul_maccmd(data))
        self.bubble_tip.start_show(BubbleTip.TYPE_OK, "解析Mac指令完成", 3000)

    def on_jr_ja_appkey_changed(self, changed_text: str):
        jr = self.lineEditJoinRequest.text()
        ja = self.lineEditJoinAnswer.text()
        appkey = self.lineEditAppkey.text()
        if not (jr and ja and appkey):
            return

        parse_res = LwpCmd.parse_jr_ja(jr, ja, appkey)
        self.textEditAck.setText(parse_res)
        if "Error" in parse_res:
            return
        nwkskey = ""
        appskey = ""
        for d in parse_res.splitlines():
            if "NWKSKEY" in d:
                nwkskey = d.split(":")[-1].strip()
                self.lineEditNwkskey.setText(nwkskey)
                continue
            if "APPSKEY" in d:
                appskey = d.split(":")[-1].strip()
                self.lineEditAppskey.setText(appskey)
                continue
        if nwkskey and appskey:
            self.bubble_tip.start_show(BubbleTip.TYPE_OK, '解析成功，NWKSKEY、APPSKEY已复制到"解析Payload"', 3000)

    def on_payload_changed(self, changed_text: str):
        appskey = self.lineEditAppskey.text()
        nwkskey = self.lineEditNwkskey.text()
        payload = self.lineEditPayload.text()
        if not (appskey and nwkskey and payload):
            return

        parse_res = LwpCmd.parse_payload(payload, appskey, nwkskey)
        self.textEditAck.setText(parse_res)
        self.bubble_tip.start_show(BubbleTip.TYPE_OK, "解析Payload完成", 3000)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    f = Form()
    f.show()
    sys.exit(app.exec())
