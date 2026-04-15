import sys

from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtGui import QColor, QKeyEvent, QMouseEvent, QPainter, QPaintEvent, QPen
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget


class CCircle:
    RADIUS = 25

    def __init__(self, center: QPoint) -> None:
        self._center = QPoint(center)
        self._selected = False

    def draw(self, painter: QPainter) -> None:
        border_color = QColor("#d64545") if self._selected else QColor("#1f3a60")
        fill_color = QColor("#f7d3d3") if self._selected else QColor("#cde3ff")

        painter.setPen(QPen(border_color, 2))
        painter.setBrush(fill_color)
        diameter = self.RADIUS * 2
        painter.drawEllipse(
            self._center.x() - self.RADIUS,
            self._center.y() - self.RADIUS,
            diameter,
            diameter,
        )

    def contains(self, point: QPoint) -> bool:
        dx = point.x() - self._center.x()
        dy = point.y() - self._center.y()
        return dx * dx + dy * dy <= self.RADIUS * self.RADIUS

    def set_selected(self, selected: bool) -> None:
        self._selected = selected

    def is_selected(self) -> bool:
        return self._selected


class CircleStorage:
    def __init__(self) -> None:
        self.__items: list[CCircle] = [] 

    def add(self, circle: CCircle) -> None:
        self.__items.append(circle)

    def all(self) -> list[CCircle]:
        return self.__items

    def hit_test_topmost(self, point: QPoint) -> list[CCircle] | None:
        res = []
        for circle in reversed(self.__items):
            if circle.contains(point):
                res.append(circle)
        return res

    def clear_selection(self) -> None:
        for circle in self.__items:
            circle.set_selected(False)

    def selected_count(self) -> int:
        return sum(1 for circle in self.__items if circle.is_selected())

    def remove_selected(self) -> int:
        before = len(self.__items)
        self.__items = [circle for circle in self.__items if not circle.is_selected()]
        return before - len(self.__items)


class CanvasWidget(QWidget):
    def __init__(self, storage: CircleStorage, status_label: QLabel) -> None:
        super().__init__()
        self._storage = storage
        self._status_label = status_label
        self.setMouseTracking(True)
        self._update_status()

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.fillRect(self.rect(), QColor("#fafafa"))

        for circle in self._storage.all():
            circle.draw(painter)

        painter.end()
        super().paintEvent(event)

    def resizeEvent(self, event) -> None:
        self._update_status()
        super().resizeEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton:
            super().mousePressEvent(event)
            return

        ctrl_pressed = bool(event.modifiers() & Qt.KeyboardModifier.ControlModifier)
        hit_circle = self._storage.hit_test_topmost(event.position().toPoint())

        if not hit_circle:
            self._storage.add(CCircle(event.position().toPoint()))
            if not ctrl_pressed:
                self._storage.clear_selection()
        else:
            if ctrl_pressed:
                for c in hit_circle:
                    c.set_selected(not c.is_selected())
            else:
                self._storage.clear_selection()
                for c in hit_circle:
                    c.set_selected(True)

        self._update_status()
        self.update()
        super().mousePressEvent(event)

    def delete_selected(self) -> int:
        removed = self._storage.remove_selected()
        self._update_status()
        self.update()
        return removed

    def _update_status(self) -> None:
        self._status_label.setText(
            f"Кругов: {len(self._storage.all())} | Выделено: {self._storage.selected_count()} | "
            f"Размер: {self.width()}x{self.height()}"
        )


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("ЛР3.1 - Круги на форме (PyQt6)")
        self.resize(900, 600)

        self._status_label = QLabel()
        self._storage = CircleStorage()
        self._canvas = CanvasWidget(self._storage, self._status_label)

        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        layout.addWidget(self._status_label)
        layout.addWidget(self._canvas, stretch=1)
        self.setCentralWidget(root)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Delete:
            self._canvas.delete_selected()
            event.accept()
            return 
        super().keyPressEvent(event)


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
