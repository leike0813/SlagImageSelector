import warnings
from typing import Union, List, Optional, Sequence
import PySide2.QtWidgets as QtW, PySide2.QtCore as QtC


__all__ = ['QCustomMessageBox']


class QCustomMessageBox(QtW.QMessageBox):
    @classmethod
    def flexible(
            cls,
            icon: QtW.QMessageBox.Icon,
            title: str,
            text: str,
            buttons: Union[Sequence[Union[str, QtW.QAbstractButton]], QtW.QMessageBox.StandardButton],
            roles: Optional[Sequence[QtW.QMessageBox.ButtonRole]] = [],
            escape: Optional[int] = -1,
            execute: Optional[bool] = True,
            parent: Optional[QtC.QObject] = None,
    ):
        """
        Open a custom message box in a flexible manner
        :param icon: Window icon, QtW.QMessagebox.Icon enums
        :param title: Window title, str
        :param text: Window text, str
        :param buttons: Sequence of button texts or QAbstractButton, or QMessageBox.StandardButton flag
        :param roles: Sequence of QMessageBox.ButtonRole or None, optional, default is None
                      If empty, set role of last button to 'DestructiveRole' while other buttons to 'YesRole'
        :param escape: Index of button to be bound to escape behavior, default is -1
        :param execute: Whether to execute immediately after method call, default is True
        :param parent: Parent
        :return: - None if error occurs
                 - messageBox otherwise
        """
        messageBox = cls()

        if isinstance (buttons, QtW.QMessageBox.StandardButton):
            if QtW.QMessageBox.StandardButton(buttons) in QtW.QMessageBox.StandardButton:
                messageBox.setStandardButtons(buttons)
            else:
                warnings.warn('Buttons must be valid QMessageBox.StandardButton flag', category=RuntimeWarning)
                return None
        elif isinstance(buttons, Sequence):
            if len(buttons) > 0:
                if not isinstance(roles, Sequence):
                    warnings.warn('Invalid roles, use default roles instead')
                    roles = []
                if len(roles) == len(buttons):
                    for i in range(len(buttons)):
                        messageBox.addButton(buttons[i], roles[i])
                else:
                    if len(roles) != 0:
                        warnings.warn('Roles must be the same length of buttons, use default roles instead')
                    for i in range(len(buttons) - 1):
                        messageBox.addButton(buttons[i], QtW.QMessageBox.YesRole)
                    messageBox.addButton(buttons[-1], QtW.QMessageBox.DestructiveRole)
        else:
            warnings.warn('Invalid buttons', category=RuntimeWarning)
            return None

        if not isinstance(escape, int):
            warnings.warn('Invalid escape button index, use default instead', category=RuntimeWarning)
            escape = -1
        messageBox.setEscapeButton(messageBox.buttons()[escape])

        messageBox.setWindowTitle(title)
        messageBox.setText(text)
        messageBox.setIcon(icon)

        if execute:
            messageBox.exec()

        return messageBox

    def buttonTexts(self):
        return {button.text(): button for button in self.buttons()}