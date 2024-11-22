#    Copyright (C) 2008 Jeremy S. Sanders
#    Email: Jeremy Sanders <jeremy@jeremysanders.net>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
##############################################################################

"""A convenience module to import used Qt symbols from."""

from PyQt6.QtCore import (
    QT_VERSION_STR, PYQT_VERSION_STR, Qt, QCoreApplication, QRectF, QPoint,
    QPointF, QLineF, QTime, QTimer, QEvent, QSignalMapper, QBuffer, QByteArray,
    QIODevice, QLocale, QSettings, QDir, QUrl, QItemSelectionModel, QRect,
    pyqtSignal, pyqtSlot, QThread, QTranslator, QAbstractTableModel, QSizeF,
    QStringListModel, QObject, QSemaphore, QMutex, QSize, QAbstractListModel,
    QAbstractItemModel, QRegularExpression, QModelIndex, QRunnable, QMimeData,
    QSortFilterProxyModel, QThreadPool, QMarginsF, QStandardPaths, QSocketNotifier
)
from PyQt6.QtGui import (
    QDesktopServices, QBrush, QPen, QFont, QAction, QPalette, QFontMetrics,
    QFontMetricsF, QScreen, QFileSystemModel, QIntValidator, QDoubleValidator,
    QPainter, QPainterPath, QPaintEngine, QTextDocument, QPaintDevice, QImage,
    QFontDatabase, QPixmap, QColor, QIcon, QActionGroup, QCursor, QMouseEvent,
    QValidator, QRegularExpressionValidator, QTransform, QPolygonF, QIconEngine,
    QKeySequence, QPicture, QTextOption, QTextCursor, QPageSize, QPageLayout,
    QImageWriter, qRgba
)
from PyQt6.QtWidgets import (
    QWidget, QMainWindow, QApplication, QSplashScreen, QLabel, QVBoxLayout,
    QHBoxLayout, QGridLayout, QMessageBox, QGraphicsRectItem, QGraphicsLineItem,
    QGraphicsSimpleTextItem, QGraphicsItem, QSizePolicy, QCompleter, QButtonGroup,
    QDialogButtonBox, QFileDialog, QStatusBar, QAbstractItemView, QDialog,
    QTreeWidgetItem, QStyle, QStyledItemDelegate, QLineEdit, QMenu, QFrame, QSlider,
    QGraphicsPathItem, QGraphicsView, QGraphicsScene, QPushButton, QToolButton,
    QHeaderView, QToolBar, QScrollArea, QTextEdit, QSpinBox, QCheckBox, QComboBox,
    QFontComboBox, QGroupBox, QDockWidget, QTreeView, QTabWidget, QTableWidgetItem,
    QColorDialog, QListWidgetItem, QInputDialog, QRadioButton, QItemDelegate
)
from PyQt6.QtSvgWidgets import QGraphicsSvgItem
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog, QAbstractPrintDialog
from PyQt6.uic import loadUi

try:
    from PyQt6 import sip
except ImportError:
    import sip

