import sys
import time
from datetime import datetime
import os
import glob
import serial
from PyQt5 import QtWidgets, QtSvg, QtCore, QtGui, Qt
import pyqtgraph as pg
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter, WindowOperations, DetrendOperations
import numpy as np
import pandas as pd

shape_colors = ["ffb480"] * 8

svg_str = """<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.0//EN" "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd">
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" id="body_1" width="510" height="510" vertical-align="bottom">

<g transform="matrix(0.44270834 0 0 0.44270834 0 0)">
    <path transform="matrix(1 0 0 1 124.7702 96.797455)"  d="M556.08 0L337.018 0L91.7438 192.849L0 509.272L22.4679 726.461L99.2331 842.545L230.296 971.736L446.784 1024.16L666.547 971.736L801.354 848.162L876.247 724.589L902.46 509.272L808.843 185.36L556.08 0z" stroke="#000000" stroke-width="8.2584" stroke-linecap="round" fill="#FFFFFF" fill-rule="nonzero" />

    <path transform="matrix(-1 -0 0 0.99999994 912.24457 120.67955)"  d="M327.934 0L327.934 320.53L0 179.563L232.331 0L327.934 0z" stroke="#FFFFFF" stroke-width="8.2584" stroke-linecap="round" id="shape0" fill="#""" + \
          shape_colors[0] + """" fill-rule="nonzero" stroke-opacity="0" />
    <path transform="matrix(-1 -0 0 0.99999994 1003.7819 306.3404)"  d="M419.471 143.887L419.471 295.06L0 297.806L84.8303 0L419.471 143.887z" stroke="#FFFFFF" stroke-width="8.2584" stroke-linecap="round" id="shape1" fill="#""" + \
          shape_colors[1] + """" fill-rule="nonzero" stroke-opacity="0" />
    <path transform="matrix(-1 -0 0 0.99999994 1003.7819 606.8925)"  d="M419.471 154.317L91.7926 314.449L19.849 203.053L0 6.40761L419.471 0L419.471 154.317z" stroke="#FFFFFF" stroke-width="8.2584" stroke-linecap="round" id="shape2" fill="#""" + \
          shape_colors[2] + """" fill-rule="nonzero" stroke-opacity="0" />
    <path transform="matrix(-1 -0 0 0.99999994 908.58307 769.829)"  d="M324.272 323.249L126.556 276.834L0 159.275L324.272 0L324.272 323.249z" stroke="#FFFFFF" stroke-width="8.2584" stroke-linecap="round" id="shape3" fill="#""" + \
          shape_colors[3] + """" fill-rule="nonzero" stroke-opacity="0" />
    <path transform="matrix(1 0 0 0.99999994 246.23544 120.67955)"  d="M327.934 0L327.934 320.53L0 179.563L232.331 0L327.934 0z" stroke="#FFFFFF" stroke-width="8.2584" stroke-linecap="round" id="shape4" fill="#""" + \
          shape_colors[4] + """" fill-rule="nonzero" stroke-opacity="0" />
    <path transform="matrix(1 0 0 0.99999994 154.6981 306.3404)"  d="M419.471 143.887L419.471 295.06L0 297.806L84.8303 0L419.471 143.887z" stroke="#FFFFFF" stroke-width="8.2584" stroke-linecap="round" id="shape5" fill="#""" + \
          shape_colors[5] + """" fill-rule="nonzero" stroke-opacity="0" />
    <path transform="matrix(1 0 0 0.99999994 154.6981 606.8925)"  d="M419.471 154.317L91.7926 314.449L19.849 203.053L0 6.40761L419.471 0L419.471 154.317z" stroke="#FFFFFF" stroke-width="8.2584" stroke-linecap="round" id="shape6" fill="#""" + \
          shape_colors[6] + """" fill-rule="nonzero" stroke-opacity="0" />
    <path transform="matrix(1 0 0 0.99999994 249.89694 769.829)"  d="M324.272 323.249L126.556 276.834L0 159.275L324.272 0L324.272 323.249z" stroke="#FFFFFF" stroke-width="8.2584" stroke-linecap="round" id="shape7" fill="#""" + \
          shape_colors[7] + """" fill-rule="nonzero" stroke-opacity="0" />

    <path transform="matrix(1.0000001 0 0 0.99999994 248.76448 120.67955)"  d="M327.934 0L327.934 320.53L0 179.563L232.331 0L327.934 0z" id="outline0" stroke="#FFFFFF" fill="#888888" stroke-width="21.6" stroke-linecap="round" fill-opacity="0.4" />
    <path transform="matrix(1.0000001 0 0 0.99999994 155.30183 306.3404)"  d="M419.471 143.887L419.471 295.06L0 297.806L84.8303 0L419.471 143.887z" id="outline1" stroke="#FFFFFF" fill="#888888" stroke-width="21.6" stroke-linecap="round" fill-opacity="0.4" />
    <path transform="matrix(1.0000001 0 0 0.99999994 155.30183 606.8925)"  d="M419.471 154.317L91.7926 314.449L19.849 203.053L0 6.40761L419.471 0L419.471 154.317z" id="outline2" stroke="#FFFFFF" fill="#888888" stroke-width="21.6" stroke-linecap="round" fill-opacity="0.4" />
    <path transform="matrix(1.0000001 0 0 0.99999994 250.103 769.8289)"  d="M324.272 323.249L126.556 276.834L0 159.275L324.272 0L324.272 323.249z" id="outline3" stroke="#FFFFFF" fill="#888888" stroke-width="21.6" stroke-linecap="round" fill-opacity="0.4" />
    <path transform="matrix(-1 -0 0 0.99999994 909.7155 120.67955)"  d="M327.934 0L327.934 320.53L0 179.563L232.331 0L327.934 0z" id="outline4" stroke="#FFFFFF" fill="#888888" stroke-width="21.6" stroke-linecap="round" fill-opacity="0.4" />
    <path transform="matrix(-1 -0 0 0.99999994 1003.17816 306.3404)"  d="M419.471 143.887L419.471 295.06L0 297.806L84.8303 0L419.471 143.887z" id="outline5" stroke="#FFFFFF" fill="#888888" stroke-width="21.6" stroke-linecap="round" fill-opacity="0.4" />
    <path transform="matrix(-1 -0 0 0.99999994 1003.17816 606.8925)"  d="M419.471 154.317L91.7926 314.449L19.849 203.053L0 6.40761L419.471 0L419.471 154.317z" id="outline6" stroke="#FFFFFF" fill="#888888" stroke-width="21.6" stroke-linecap="round" fill-opacity="0.4" />
    <path transform="matrix(-1 -0 0 0.99999994 908.377 769.8289)"  d="M324.272 323.249L126.556 276.834L0 159.275L324.272 0L324.272 323.249z" id="outline7" stroke="#FFFFFF" fill="#888888" stroke-width="21.6" stroke-linecap="round" fill-opacity="0.4" />

	<text transform="matrix(1 0 0 1 408.25653 288.45828)" x="0" y="0" style="fill:#FFFFFF;font-family:ABeeZee;" font-size="50">

	</text>
	<text transform="matrix(1 0 0 1 408.25653 288.45828)" x="0" y="0" style="fill:#FFFFFF;font-family:ABeeZee;" font-size="50">
Fp1
	</text>
	<text transform="matrix(0.99999994 0 0 1 298.26758 507.25952)" x="0" y="0" style="fill:#FFFFFF;font-family:ABeeZee;" font-size="50">

	</text>
	<text transform="matrix(0.99999994 0 0 1 298.26758 507.25952)" x="0" y="0" style="fill:#FFFFFF;font-family:ABeeZee;" font-size="50">
F3
	</text>
	<text transform="matrix(0.99999994 0 0 1 304.03036 751.21643)" x="0" y="0" style="fill:#FFFFFF;font-family:ABeeZee;" font-size="50">

	</text>
	<text transform="matrix(0.99999994 0 0 1 304.03036 751.21643)" x="0" y="0" style="fill:#FFFFFF;font-family:ABeeZee;" font-size="50">
P3
	</text>
	<text transform="matrix(0.99999994 0 0 1 401.99728 958.67584)" x="0" y="0" style="fill:#FFFFFF;font-family:ABeeZee;" font-size="50">

	</text>
	<text transform="matrix(0.99999994 0 0 1 401.99728 958.67584)" x="0" y="0" style="fill:#FFFFFF;font-family:ABeeZee;" font-size="50">
O1
	</text>
	<text transform="matrix(0.99999994 0 0 1 634.9171 288.06412)" x="0" y="0" style="fill:#FFFFFF;font-family:ABeeZee;" font-size="50">

	</text>
	<text transform="matrix(0.99999994 0 0 1 634.9171 288.06412)" x="0" y="0" style="fill:#FFFFFF;font-family:ABeeZee;" font-size="50">
Fp2
	</text>
	<text transform="matrix(0.99999994 0 0 0.99999994 769.92816 506.86536)" x="0" y="0" style="fill:#FFFFFF;font-family:ABeeZee;" font-size="50">

	</text>
	<text transform="matrix(0.99999994 0 0 0.99999994 769.92816 506.86536)" x="0" y="0" style="fill:#FFFFFF;font-family:ABeeZee;" font-size="50">
F4
	</text>
	<text transform="matrix(0.99999994 0 0 0.99999994 775.6909 750.82227)" x="0" y="0" style="fill:#FFFFFF;font-family:ABeeZee;" font-size="50">

	</text>
	<text transform="matrix(0.99999994 0 0 0.99999994 775.6909 750.82227)" x="0" y="0" style="fill:#FFFFFF;font-family:ABeeZee;" font-size="50">
P4
	</text>
	<text transform="matrix(0.99999994 0 0 0.99999994 640.1834 956.3608)" x="0" y="0" style="fill:#FFFFFF;font-family:ABeeZee;" font-size="50">

	</text>
	<text transform="matrix(0.99999994 0 0 0.99999994 640.1834 956.3608)" x="0" y="0" style="fill:#FFFFFF;font-family:ABeeZee;" font-size="50">
O2
	</text>
</g>
</svg>
"""

start_stream = False
stream_running = False
stop_stream = False
current_device = 0
freq_bands = {'delta': [0, 4], 'theta': [4, 7], 'alpha': [8, 12], 'beta': [12, 30], 'gamma': [30, 100]}
current_freq_band = 2
current_electrodes = []
electrode_locations = [1, 3, 5, 7, 0, 2, 4, 6]
electrode_names = ['Fp2', 'Fp1', 'F4', 'F3', 'P4', 'P3', 'O2', 'O1']
datapoints = 30
X = list(range(0, datapoints))
y = {0: [0] * datapoints, 1: [0] * datapoints, 2: [0] * datapoints, 3: [0] * datapoints, 4: [0] * datapoints,
     5: [0] * datapoints, 6: [0] * datapoints, 7: [0] * datapoints}
color_count = {'delta': 100, 'theta': 30, 'alpha': 30, 'beta': 30, 'gamma': 100}
freq_band_colors = [np.array(
    [np.rint(np.linspace(255, 255, color_count['delta'])), np.rint(np.linspace(136, 161, color_count['delta'])),
     np.rint(np.linspace(136, 0, color_count['delta']))]).T,
                    np.array(
                        [np.rint(np.linspace(255, 177, color_count['theta'])),
                         np.rint(np.linspace(246, 255, color_count['theta'])),
                         np.rint(np.linspace(136, 0, color_count['theta']))]).T,
                    np.array(
                        [np.rint(np.linspace(137, 0, color_count['alpha'])),
                         np.rint(np.linspace(255, 223, color_count['alpha'])),
                         np.rint(np.linspace(173, 255, color_count['alpha']))]).T,
                    np.array(
                        [np.rint(np.linspace(135, 57, color_count['beta'])),
                         np.rint(np.linspace(208, 0, color_count['beta'])),
                         np.rint(np.linspace(255, 255, color_count['beta']))]).T,
                    np.array(
                        [np.rint(np.linspace(232, 255, color_count['gamma'])),
                         np.rint(np.linspace(144, 0, color_count['gamma'])),
                         np.rint(np.linspace(255, 138, color_count['gamma']))]).T]
marker_offset = 0
threshold_value = 0
smoothing = 1
current_trigger = 0
trigger_widgets = []
trigger_layouts = []
band_power_log = {'delta': [[0] * datapoints] * 9,
                  'theta': [[0] * datapoints] * 9,
                  'alpha': [[0] * datapoints] * 9,
                  'beta': [[0] * datapoints] * 9,
                  'gamma': [[0] * datapoints] * 9}
log_updated = False
all_triggers = pd.read_csv("triggers.csv")
last_trigger_timestamp = {}
last_nontrigger_timestamp = {}
serial_port = ''

class triggerListener(QtCore.QThread):
    def run(self):
        global band_power_log
        global log_updated
        global all_triggers
        global electrode_names

        trigger_timestamp = {}

        while True:
            while not log_updated:  # Wait until band_power_log has been updated
                time.sleep(0.05)

            # Check for trigger matches
            for index in all_triggers.index:
                frequency_band = all_triggers["frequency_band"][index]

                # Average logs for each electrode listed into one signal
                signal = []
                electrodes = all_triggers["electrodes"][index].split(", ")
                for electrode in electrodes:
                    if len(signal) == 0:
                        signal = band_power_log[frequency_band][electrode_names.index(electrode) + 1]
                    else:
                        signal = np.mean(
                            np.vstack([signal, band_power_log[frequency_band][electrode_names.index(electrode) + 1]]),
                            axis=0).tolist()

                # apply smoothing
                for a in range(all_triggers["smoothing"][index], len(signal)):
                    signal[a - 1] = np.mean(signal[a - all_triggers["smoothing"][index]:a])

                # check for a threshold pass
                val = signal[len(signal) - 1:]
                if len(val) > 0 and \
                        ((all_triggers["threshold_direction"][index] == "below" and val[0] < all_triggers["threshold"][
                            index]) or
                         (all_triggers["threshold_direction"][index] == "above" and val[0] > all_triggers["threshold"][
                             index])):

                    trigger_timestamp[index] = time.time()

                    # check that activation delay and cool down are satisfied
                    activation_delay_passed = False
                    if float(all_triggers["activation_delay"][index]) > 0:
                        if trigger_timestamp[index] - last_nontrigger_timestamp[index] >= float(all_triggers["activation_delay"][index]):
                            activation_delay_passed = True

                    cool_down_passed = False
                    if float(all_triggers["cool_down"][index]) > 0:
                        if trigger_timestamp[index] - last_trigger_timestamp[index] >= float(all_triggers["cool_down"][index]):
                            cool_down_passed = True

                    if activation_delay_passed and cool_down_passed:
                        # run associated system command
                        if type(all_triggers["system_command"][index]) == str:
                            print(all_triggers["system_command"][index])
                            os.system(all_triggers["system_command"][index])

                    last_trigger_timestamp[index] = trigger_timestamp
                else:
                    last_nontrigger_timestamp[index] = time.time()

            log_updated = False

class signalListener(QtCore.QThread):
    band_power = QtCore.pyqtSignal(list)

    def run(self):
        global start_stream
        global stream_running
        global stop_stream
        global freq_bands
        global current_freq_band
        global svg_str
        global current_device
        global smoothing
        global band_power_log
        global log_updated
        global all_triggers
        global color_count
        global serial_port

        BoardShim.enable_dev_board_logger()
        params = BrainFlowInputParams()
        channels = {}

        while True:
            # try:
            if start_stream:
                print("STARTING STREAM")
                if current_device == 0:
                    board = BoardShim(BoardIds.SYNTHETIC_BOARD.value, params)
                elif current_device == 1 and serial_port != "":
                    params.serial_port = serial_port
                    board = BoardShim(BoardIds.CYTON_BOARD.value, params)

                if (current_device == 1 and serial_port != "") or current_device != 1:
                    board.prepare_session()
                    board.start_stream()
                    time.sleep(3)
                    stream_running = True
                start_stream = False

            if stop_stream:
                board.stop_stream()
                board.release_session()
                stop_stream = False

            if stream_running:
                # data = board.get_board_data()
                data = board.get_current_board_data(256)

                if current_device == 0:
                    board_descr = BoardShim.get_board_descr(BoardIds.SYNTHETIC_BOARD.value)
                elif current_device == 1:
                    board_descr = BoardShim.get_board_descr(BoardIds.CYTON_BOARD.value)
                sampling_rate = int(board_descr['sampling_rate'])
                nfft = DataFilter.get_nearest_power_of_two(sampling_rate)
                detrend_data = data
                channels_copy = {}
                if channels != {}:
                    channels_copy = channels
                channels = {}
                channel_bands = []
                for eeg_channel in board_descr['eeg_channels']:
                    DataFilter.detrend(detrend_data[eeg_channel], DetrendOperations.LINEAR.value)
                    psd = DataFilter.get_psd_welch(detrend_data[eeg_channel], nfft, nfft // 2, sampling_rate,
                                                   WindowOperations.BLACKMAN_HARRIS.value)
                    channels[eeg_channel] = []
                    current_index = 0
                    for name in freq_bands.keys():
                        freq_band = freq_bands[name]
                        power = round(DataFilter.get_band_power(psd, freq_band[0], freq_band[1]), 2)

                        if name == 'delta' or name == 'gamma':
                            power = power / 100
                        power = (color_count[name] - 1 if power >= color_count[name] else power)
                        channels[eeg_channel].append(power)
                        current_index += 1

                    if len(channels) == 8:
                        # while log_updated:  # Wait until previous update has been processed
                        #     pass

                        for key in channels:
                            band_power_log['delta'][key] = band_power_log['delta'][key][1:] + [channels[key][0]]
                            band_power_log['theta'][key] = band_power_log['theta'][key][1:] + [channels[key][1]]
                            band_power_log['alpha'][key] = band_power_log['alpha'][key][1:] + [channels[key][2]]
                            band_power_log['beta'][key] = band_power_log['beta'][key][1:] + [channels[key][3]]
                            band_power_log['gamma'][key] = band_power_log['gamma'][key][1:] + [channels[key][4]]
                        log_updated = True

                    channel_bands.append(channels[eeg_channel][current_freq_band])

                self.band_power.emit(channel_bands)

                time.sleep(0.1)
            else:
                if svg_str.count("42d6a4") < 8:
                    svg_str = svg_str.replace("ffb480", "42d6a4", 1)
                else:
                    svg_str = svg_str.replace("42d6a4", "ffb480")
                svg_bytes = bytearray(svg_str, encoding='utf-8')
                self.band_power.emit([svg_bytes])

                time.sleep(1)
            # except Exception as e:
            #     print("ERR:", e)

def clearLayout(layout):
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()

uiclass, baseclass = pg.Qt.loadUiType("interface.ui")

class MainWindow(uiclass, baseclass):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Window init
        self.setWindowTitle("NeuroShortcut")
        self.setFixedSize(self.width(), self.height())

        # Pin Configuration Init
        self.pinConfigImg.setHidden(True)

        # Band power plot init
        self.powerTimeSeries.setLimits(yMin=0, yMax=30)
        self.powerTimeSeries.setBackground("#ffffff")
        self.powerTimeSeries.hideAxis('left')
        self.powerTimeSeries.hideAxis('bottom')

        # Vector head plot init
        svg_bytes = bytearray(svg_str, encoding='utf-8')
        self.svgWidget = QtSvg.QSvgWidget(self)
        self.svgWidget.renderer().load(svg_bytes)
        self.svgWidget.move(self.svgWidget.x() + 10, self.svgWidget.y() + 50)
        self.svgWidget.setHidden(True)

        # Trigger list layout init
        self.triggerListLayout = QtWidgets.QVBoxLayout()
        self.triggerList.setLayout(self.triggerListLayout)

        # COM port init
        self.ports = self.serial_ports()
        if len(self.ports) > 0:
            self.portSelected(self.ports[0])
        self.portSelect.clear()
        self.portSelect.addItems(self.ports)

        # Event connections
        self.svgWidget.mousePressEvent = self.svgClicked
        self.tabs.currentChanged.connect(self.tabChange)
        self.deviceSelect.currentIndexChanged.connect(self.deviceSelected)
        self.startStreamButton.clicked.connect(self.startStreamButtonClicked)
        self.bandSelect.currentIndexChanged.connect(self.bandSelectChanged)
        self.thresholdSlider.valueChanged.connect(self.updateThreshold)
        self.invertTriggerArea.stateChanged.connect(self.invertTriggerAreaClicked)
        self.smoothingSelect.currentIndexChanged.connect(self.smoothingChanged)
        self.saveTriggerButton.clicked.connect(self.saveTriggerButtonClicked)
        self.activationTimepoints.valueChanged.connect(self.activationTimepointsChanged)
        self.cooldownDelay.valueChanged.connect(self.cooldownDelayChanged)
        self.systemCommand.textChanged.connect(self.systemCommandChanged)
        self.deleteTriggerButton.clicked.connect(self.deleteTriggerButtonClicked)
        self.activeCheckBox.stateChanged.connect(self.activeCheckBoxClicked)
        self.portSelect.currentIndexChanged.connect(self.portSelected)
        self.portRefreshButton.clicked.connect(self.portRefreshButtonClicked)

        # Background tasks
        self.signalHandler = signalListener()
        self.signalHandler.start()
        self.signalHandler.band_power.connect(self.updateTiles)

        self.triggerHandler = triggerListener()
        self.triggerHandler.start()

    def serial_ports(self):
        """ Lists serial port names

            :raises EnvironmentError:
                On unsupported or unknown platforms
            :returns:
                A list of the serial ports available on the system
        """
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result

    def tabChange(self, index):
        if index == 1:
            self.svgWidget.setHidden(False)
        else:
            self.svgWidget.setHidden(True)
            if index == 2:
                self.loadTriggers()

    def tileClick(self, outline_id):
        global svg_str
        global current_electrodes
        global electrode_names

        svg_str_list = svg_str.split('id="outline' + str(outline_id) + '" stroke="')
        if svg_str_list[1].split('"')[0] == "none":
            svg_str_list[0] = svg_str_list[0] + 'id="outline' + str(outline_id) + '" stroke="#FFFFFF" fill="#888888"'
            current_electrodes.remove(electrode_names[electrode_locations[outline_id]])
        else:
            svg_str_list[0] = svg_str_list[0] + 'id="outline' + str(outline_id) + '" stroke="none" fill="none"'
            current_electrodes.append(electrode_names[electrode_locations[outline_id]])
        svg_str_list[1] = "\"".join(svg_str_list[1].split('"')[3:])

        svg_str = "".join(svg_str_list)
        svg_bytes = bytearray(svg_str, encoding='utf-8')
        self.svgWidget.renderer().load(svg_bytes)

        electrodes_label_text = "Selected Electrode(s): "
        for electrode_name in current_electrodes:
            electrodes_label_text += electrode_name + ", "
        electrodes_label_text = electrodes_label_text[:-2]
        self.electrodesLabel.setText(electrodes_label_text)

    def svgClicked(self, event):
        global svg_str

        # print(event.x(), event.y())
        if event.x() >= 127 and event.x() <= 248 and event.y() >= 50 and event.y() <= 164:
            # print("Fp1")
            self.tileClick(0)
        elif event.x() >= 74 and event.x() <= 247 and event.y() >= 168 and event.y() <= 261:
            # print("F3")
            self.tileClick(1)
        elif event.x() >= 75 and event.x() <= 230 and event.y() >= 276 and event.y() <= 363:
            # print("P3")
            self.tileClick(2)
        elif event.x() >= 163 and event.x() <= 254 and event.y() >= 372 and event.y() <= 483:
            # print("O1")
            self.tileClick(3)
        elif event.x() >= 261 and event.x() <= 374 and event.y() >= 52 and event.y() <= 165:
            # print("Fp2")
            self.tileClick(4)
        elif event.x() >= 284 and event.x() <= 445 and event.y() >= 173 and event.y() <= 266:
            # print("F4")
            self.tileClick(5)
        elif event.x() >= 259 and event.x() <= 448 and event.y() >= 266 and event.y() <= 380:
            # print("P4")
            self.tileClick(6)
        elif event.x() >= 261 and event.x() <= 354 and event.y() >= 388 and event.y() <= 475:
            # print("O2")
            self.tileClick(7)

    def startStreamButtonClicked(self):
        self.startStream()
        self.tabs.setCurrentWidget(self.triggersTab)

    def bandSelectChanged(self, band_id):
        global current_freq_band
        current_freq_band = band_id
        self.thresholdSlider.setValue(0)

        if current_freq_band == 0:  # Delta
            self.descriptionLabel.setText(
                '<html><head/><body><p>Delta waves are usually associated with the deep stage 3 of NREM sleep, also known as slow-wave sleep (SWS), and aid in characterizing the depth of sleep. (<a href="https://en.wikipedia.org/wiki/Delta_wave"><span style=" text-decoration: underline; color:#0000ff;">Learn More</span></a>)</p></body></html>')
        elif current_freq_band == 1:  # Theta
            self.descriptionLabel.setText(
                '<html><head/><body><p>Humans exhibit predominantly cortical theta wave activity during REM sleep. Increased sleepiness is associated with decreased alpha wave power and increased theta wave power. Meditation has been shown to increase theta power. (<a href="https://en.wikipedia.org/wiki/Theta_wave"><span style=" text-decoration: underline; color:#0000ff;">Learn More</span></a>)</p></body></html>')
        elif current_freq_band == 2:  # Alpha
            self.descriptionLabel.setText(
                '<html><head/><body><p>Alpha waves are reduced with open eyes and sleep, while they are enhanced during drowsiness. Occipital alpha waves during periods of eyes closed are the strongest EEG brain signals. (<a href="https://en.wikipedia.org/wiki/Alpha_wave"><span style=" text-decoration: underline; color:#0000ff;">Learn More</span></a>)</p></body></html>')
        elif current_freq_band == 3:  # Beta
            self.descriptionLabel.setText(
                '<html><head/><body><p>Low-amplitude beta waves with multiple and varying frequencies are often associated with active, busy or anxious thinking and active concentration. Over the motor cortex, beta waves are associated with the muscle contractions that happen in isotonic movements and are suppressed prior to and during movement changes, with similar observations across fine and gross motor skills. (<a href="https://en.wikipedia.org/wiki/Beta_wave"><span style=" text-decoration: underline; color:#0000ff;">Learn More</span></a>)</p></body></html>')
        elif current_freq_band == 4:  # Gamma
            self.descriptionLabel.setText(
                '<html><head/><body><p>High-amplitude gamma wave synchrony can be self-induced via meditation. Long-term practitioners of meditation such as Tibetan Buddhist monks exhibit both increased gamma-band activity at baseline as well as significant increases in gamma synchrony during meditation, as determined by scalp EEG. (<a href="https://en.wikipedia.org/wiki/Gamma_wave"><span style=" text-decoration: underline; color:#0000ff;">Learn More</span></a>)</p></body></html>')

    def deviceSelected(self, device_id):
        global current_device
        current_device = device_id

        if current_device == 1:  # cyton
            self.pinConfigImg.setHidden(False)
            self.portSelect.setEnabled(True)
            self.portRefreshButton.setEnabled(True)
        else:
            self.pinConfigImg.setHidden(True)
            self.portSelect.setEnabled(False)
            self.portRefreshButton.setEnabled(False)

        self.ports = self.serial_ports()
        if len(self.ports) > 0:
            self.portSelected(self.ports[0])
    def portSelected(self, port):
        global serial_port

        serial_port = port

    def portRefreshButtonClicked(self):
        self.ports = self.serial_ports()
        if len(self.ports) > 0:
            self.portSelected(self.ports[0])
        self.portSelect.clear()
        self.portSelect.addItems(self.ports)

    def startStream(self):
        global start_stream
        global stream_running
        global stop_stream

        if stream_running:
            stop_stream = True
            # self.streamAction.setText("Start Stream")
        else:
            start_stream = True
            # self.streamAction.setText("Stop Stream")

    def updateTiles(self, band_power):
        global stream_running
        global freq_band_colors
        global current_freq_band
        global svg_str
        global electrode_locations
        global X
        global y
        global color_count
        global threshold_value

        if stream_running:
            # print(band_power)
            try:
                self.powerTimeSeries.clear()
                y_mean = []
                for a in range(0, 8):
                    # Band power plotting
                    if electrode_names[electrode_locations[a]] in current_electrodes:
                        y[a] = y[a][1:] + [band_power[electrode_locations[a]]]
                        if len(y_mean) == 0:
                            y_mean = y[a]
                        else:
                            y_mean = np.mean(np.vstack([y_mean, y[a]]), axis=0).tolist()

                        self.powerTimeSeries.plot(X, y[a], pen={'color': '#BBBBBB', 'width': 0.5})

                    # Vector tile colors
                    color = "rgb(" + ",".join([str(int(i)) for i in freq_band_colors[current_freq_band][
                        int(band_power[electrode_locations[a]])]]) + ")"
                    svg_str_split = svg_str.split('id="shape' + str(electrode_locations[a]) + '" fill="')
                    svg_start = svg_str_split[0] + 'id="shape' + str(electrode_locations[a]) + '" fill="' + color + '"'
                    svg_end = '"'.join(svg_str_split[1].split('"')[1:])
                    svg_str = svg_start + svg_end

                # apply smoothing
                if len(y_mean) > 0:
                    y_mean[len(y_mean) - 1] = np.mean(y_mean[len(y_mean) - smoothing:len(y_mean)])

                # Threshold triggered indicator
                val = y_mean[len(y_mean) - 1:]
                if len(val) > 0:
                    val = val[0]
                    if self.invertTriggerArea.isChecked():
                        if val < threshold_value:
                            self.indicator.setStyleSheet(
                                "border: 2px solid black; border-radius: 10px; background-color: red;")
                        else:
                            self.indicator.setStyleSheet(
                                "border: 2px solid black; border-radius: 10px; background-color: #222222;")
                    else:
                        if val > threshold_value:
                            self.indicator.setStyleSheet(
                                "border: 2px solid black; border-radius: 10px; background-color: red;")
                        else:
                            self.indicator.setStyleSheet(
                                "border: 2px solid black; border-radius: 10px; background-color: #222222;")

                # Plot layout
                self.powerTimeSeries.plot(X, y_mean, pen={'color': '#000000', 'width': 1.5})
                self.powerTimeSeries.setRange(yRange=[0, list(color_count.values())[current_freq_band]])

                svg_bytes = bytearray(svg_str, encoding='utf-8')
                self.svgWidget.renderer().load(svg_bytes)
            except Exception as e:
                print("ERR: ", end="")
                input(e)

        else:
            self.svgWidget.renderer().load(band_power[0])

    def updateThreshold(self):
        global marker_offset
        global threshold_value
        global color_count
        global current_freq_band

        marker_position = self.powerTimeSeries.height() - self.thresholdSlider.value()
        threshold_value = ((((marker_position - 0) * (30 - 0)) / (self.thresholdSlider.maximum() - 0)) - 30) * -1
        self.thresholdMarker.move(self.thresholdMarker.x(), marker_position - marker_offset)
        self.thresholdValueLabel.setText("Threshold: " + str(round(threshold_value, 2)))

    def invertTriggerAreaClicked(self):
        global marker_offset
        if self.invertTriggerArea.isChecked():
            self.thresholdMarker.setStyleSheet("background-color: rgba(255, 0, 0, 40); border-top: 1px solid red;")
            marker_offset = 0
        else:
            self.thresholdMarker.setStyleSheet("background-color: rgba(255, 0, 0, 40); border-bottom: 1px solid red;")
            marker_offset = self.powerTimeSeries.height()
        self.updateThreshold()

    def smoothingChanged(self, smoothing_level):
        global smoothing
        smoothing = smoothing_level + 1

    def saveTriggerButtonClicked(self):
        global freq_bands
        global smoothing
        global threshold_value
        global all_triggers

        triggers_file = open("triggers.csv", "r")
        triggers = triggers_file.read()
        triggers_file.close()

        last_edit = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        name = self.triggerName.text()
        if name in triggers:
            return
        frequency_band = list(freq_bands.keys())[current_freq_band]
        electrodes = self.electrodesLabel.text().split("Selected Electrode(s): ")
        if len(electrodes) == 1:
            return
        else:
            electrodes = electrodes[1]
        threshold = round(threshold_value, 2)
        threshold_direction = "above"
        if self.invertTriggerArea.isChecked():
            threshold_direction = "below"
        activation_delay = 0.0
        cool_down = 0.0
        system_command = ""
        active = True

        pd.DataFrame([[last_edit, name, frequency_band, electrodes, smoothing, threshold, threshold_direction,
                       activation_delay, cool_down, system_command, active]]).to_csv("triggers.csv", mode='a',
                                                                                     header=False, index=False)
        self.triggerName.setText("")
        all_triggers = pd.read_csv("triggers.csv")
        print("Saved")

    def loadTriggers(self):
        global trigger_widgets
        global trigger_layouts

        triggers = pd.read_csv("triggers.csv").to_numpy()

        clearLayout(self.triggerListLayout)

        trigger_widgets = []
        trigger_layouts = []
        trigger_id = 0
        for trigger in triggers:
            # Add selectable widgets to scroll area
            trigger_widgets.append(QtWidgets.QWidget())
            self.triggerListLayout.addWidget(trigger_widgets[trigger_id])
            trigger_widgets[trigger_id].setObjectName("trigger")
            trigger_widgets[trigger_id].setFixedHeight(101)
            trigger_widgets[trigger_id].setStyleSheet(
                "QWidget#trigger { border: 2px solid #BBBBBB; } QLabel { font-size: 10pt; }")
            trigger_widgets[trigger_id].mousePressEvent = self.triggerSelect

            trigger_layouts.append(QtWidgets.QGridLayout())
            trigger_widgets[trigger_id].setLayout(trigger_layouts[trigger_id])
            trigger_layouts[trigger_id].addWidget(QtWidgets.QLabel("<b>Last Edit</b><br>" + trigger[0]), 1, 1)
            trigger_layouts[trigger_id].addWidget(QtWidgets.QLabel("<b>Name</b><br>" + trigger[1]), 1, 2)
            trigger_layouts[trigger_id].addWidget(QtWidgets.QLabel("<b>Freq. Band</b><br>" + trigger[2]), 1, 3)
            trigger_layouts[trigger_id].addWidget(QtWidgets.QLabel("<b>Electrodes</b><br>" + trigger[3]), 1, 4)
            trigger_layouts[trigger_id].addWidget(QtWidgets.QLabel("<b>Smoothing</b><br>" + str(trigger[4])), 2, 1)
            trigger_layouts[trigger_id].addWidget(QtWidgets.QLabel("<b>Threshold</b><br>" + str(trigger[5])), 2, 2)
            trigger_layouts[trigger_id].addWidget(QtWidgets.QLabel("<b>Threshold Direction</b><br>" + trigger[6]), 2, 3)
            trigger_layouts[trigger_id].addWidget(QtWidgets.QLabel("<b>Active</b><br>" + str(trigger[10])), 2, 4)

            trigger_id += 1

        self.triggerListLayout.addStretch()

        self.activationTimepoints.setEnabled(False)
        self.cooldownDelay.setEnabled(False)
        self.systemCommand.setEnabled(False)
        self.deleteTriggerButton.setEnabled(False)
        self.activeCheckBox.setEnabled(False)

    def triggerSelect(self, event):
        global current_trigger
        global trigger_widgets

        scroll_height = self.triggerListArea.verticalScrollBar().value()
        for tridder_id in range(1, 10000):
            if event.windowPos().y() > ((tridder_id - 1) * 106 + 50 - scroll_height) and \
                    event.windowPos().y() < tridder_id * 106 + 50 - scroll_height:
                # Set current trigger id
                current_trigger = tridder_id - 1
                break
        # Update trigger widget, number selection boxes, and line edit
        for trigger_widget in trigger_widgets:
            trigger_widget.setStyleSheet(
                "QWidget#trigger { border: 2px solid #BBBBBB; background-color: none; } QLabel { font-size: 10pt; }")
        trigger_widgets[current_trigger].setStyleSheet(
            "QWidget#trigger { border: 2px solid #BBBBBB; background-color: #CCCCCC; } QLabel { font-size: 10pt; }")

        triggers = pd.read_csv("triggers.csv").to_numpy()
        self.activeCheckBox.setChecked(int(triggers[current_trigger][10]))
        self.activationTimepoints.setValue(triggers[current_trigger][7])
        self.cooldownDelay.setValue(triggers[current_trigger][8])
        if type(triggers[current_trigger][9]) != str:
            self.systemCommand.setText("")
        else:
            self.systemCommand.setText(triggers[current_trigger][9])

        self.activationTimepoints.setEnabled(True)
        self.cooldownDelay.setEnabled(True)
        self.systemCommand.setEnabled(True)
        self.deleteTriggerButton.setEnabled(True)
        self.activeCheckBox.setEnabled(True)

    def activeCheckBoxClicked(self):
        global current_trigger
        global all_triggers

        triggers = pd.read_csv("triggers.csv")
        if self.activeCheckBox.isChecked():
            triggers.loc[current_trigger, "active"] = "1"
        else:
            triggers.loc[current_trigger, "active"] = "0"
        triggers.to_csv("triggers.csv", index=False)

        all_triggers = triggers

    def activationTimepointsChanged(self):
        global current_trigger
        global all_triggers

        triggers = pd.read_csv("triggers.csv")
        if len(triggers.last_edit) > 0:
            triggers.loc[current_trigger, "activation_delay"] = str(self.activationTimepoints.value())
            triggers.to_csv("triggers.csv", index=False)

            all_triggers = triggers

    def cooldownDelayChanged(self):
        global current_trigger
        global all_triggers

        triggers = pd.read_csv("triggers.csv")
        triggers.loc[current_trigger, "cool_down"] = str(self.cooldownDelay.value())
        triggers.to_csv("triggers.csv", index=False)

        all_triggers = triggers

    def systemCommandChanged(self):
        global current_trigger
        global all_triggers

        triggers = pd.read_csv("triggers.csv")
        triggers.loc[current_trigger, "system_command"] = str(self.systemCommand.text())
        triggers.to_csv("triggers.csv", index=False)

        all_triggers = triggers

    def deleteTriggerButtonClicked(self):
        global current_trigger
        triggers = pd.read_csv("triggers.csv")
        triggers = triggers.drop(current_trigger)
        triggers.to_csv("triggers.csv", index=False)

        # refresh trigger list and reset inputs
        self.loadTriggers()
        self.activationTimepoints.setValue(0)
        self.activationTimepoints.setEnabled(False)
        self.cooldownDelay.setValue(0)
        self.cooldownDelay.setEnabled(False)
        self.systemCommand.setText("")
        self.systemCommand.setEnabled(False)
        self.deleteTriggerButton.setEnabled(False)

        print("Deleted")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')

    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(255, 255, 255))
    palette.setColor(QtGui.QPalette.Base, QtGui.QColor(25, 25, 25))
    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor(0, 0, 0))
    palette.setColor(QtGui.QPalette.ToolTipText, QtGui.QColor(255, 255, 255))
    palette.setColor(QtGui.QPalette.Text, QtGui.QColor(255, 255, 255))
    palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(255, 255, 255))
    palette.setColor(QtGui.QPalette.BrightText, QtGui.QColor(255, 0, 0))
    palette.setColor(QtGui.QPalette.Link, QtGui.QColor(218, 53, 42))
    palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(218, 53, 42))
    # palette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
    # palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
    palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(0, 0, 0))
    app.setPalette(palette)

    window = MainWindow()
    window.show()
    app.exec()