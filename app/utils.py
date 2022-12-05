import re

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QGraphicsDropShadowEffect, QFrame, QApplication


def apply_shadow(widget: QWidget, alpha, x=0, y=4, r=8):
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(r)
    shadow.setYOffset(y)
    shadow.setXOffset(x)
    shadow.setColor(QColor(0, 0, 0, alpha))
    widget.setGraphicsEffect(shadow)


def crop_string(string: str, max_size: int, end_string="..."):
    return string[:max_size].strip() + (end_string if max_size < len(string) else "")


def alphanumeric_sort(obj, key, reverse=False, ignore_case=True):
    convert = lambda text: int(text) if text.isdigit() else (text.lower() if ignore_case else text)
    alphanum_key = lambda inkey: [convert(c) for c in re.split('([0-9]+)', key(inkey))]
    return sorted(obj, key=alphanum_key, reverse=reverse)


def center_widget(app, widget):
    frameGm = widget.frameGeometry()
    frameGm.moveCenter(app.desktop().screenGeometry(app.desktop().screenNumber(app.desktop().cursor().pos())).center())
    widget.move(frameGm.topLeft())
