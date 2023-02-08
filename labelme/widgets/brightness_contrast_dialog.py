import PIL.Image
import PIL.ImageEnhance
from qtpy.QtCore import Qt
from qtpy import QtGui
from qtpy import QtWidgets
import numpy as np

from .. import utils


class BrightnessContrastDialog(QtWidgets.QDialog):
    def __init__(self, img, callback, parent=None):
        super(BrightnessContrastDialog, self).__init__(parent)
        self.setModal(True)
        self.setWindowTitle("Brightness/Contrast")
        self.value_scale = 100

        self.slider_brightness, self.box_brightness = self._create_elements((0,3), 1)
        self.slider_contrast, self.box_contrast = self._create_elements((0,3), 1)
        self.slider_exposure, self.box_exposure = self._create_elements((-4,4), 0)

        self.btn_reset = QtWidgets.QPushButton("Reset")
        self.btn_reset.clicked.connect(self.reset)

        def make_row(slider, box):
            row = QtWidgets.QHBoxLayout()
            row.addWidget(slider)
            row.addWidget(box)
            return row

        formLayout = QtWidgets.QFormLayout()
        formLayout.addRow(self.tr("Brightness"), make_row(self.slider_brightness, self.box_brightness))
        formLayout.addRow(self.tr("Contrast"), make_row(self.slider_contrast, self.box_contrast))
        formLayout.addRow(self.tr("Exposure"), make_row(self.slider_exposure, self.box_exposure))
        formLayout.addRow(self.btn_reset)
        self.setLayout(formLayout)

        assert isinstance(img, PIL.Image.Image)
        self.img = img
        self.callback = callback

    def reset(self):
        self.slider_brightness.setValue(1 * self.value_scale)
        self.slider_contrast.setValue(1 * self.value_scale)
        self.slider_exposure.setValue(0 * self.value_scale)

    def onNewValue(self, value):
        brightness = self.slider_brightness.value() / self.value_scale
        contrast = self.slider_contrast.value() / self.value_scale
        exposure = self.slider_exposure.value() / self.value_scale

        img = self.img
        img = PIL.ImageEnhance.Brightness(img).enhance(brightness)
        img = PIL.ImageEnhance.Contrast(img).enhance(contrast)
        img = PIL.Image.fromarray((np.array(img) * 2**exposure).clip(0,255).astype(np.uint8))

        img_data = utils.img_pil_to_data(img)
        qimage = QtGui.QImage.fromData(img_data)
        self.callback(qimage)

    def _create_elements(self, range, default):
        # Initialize.
        slider = QtWidgets.QSlider(Qt.Horizontal)
        slider.setRange(range[0] * self.value_scale, range[1] * self.value_scale)
        slider.setValue(default * self.value_scale)
        box = QtWidgets.QSpinBox()
        box.setRange(range[0] * self.value_scale, range[1] * self.value_scale)
        box.setValue(default * self.value_scale)
        # Connect listeners.
        slider.valueChanged.connect(self.onNewValue)
        slider.valueChanged.connect(box.setValue)
        box.valueChanged.connect(slider.setValue)
        return slider, box
