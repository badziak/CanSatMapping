import sys
import random
import folium
import serial
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox, QMessageBox
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from folium.plugins import MarkerCluster
from colour import Color


class RefreshOptionDialog(QMessageBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Refresh Option")
        self.setText("Choose Refresh Option:")
        self.addButton("Update Automatically", QMessageBox.AcceptRole)
        self.addButton("Update Manually", QMessageBox.RejectRole)

def LoRa(COM_PORT):
    # Define the COM port and baud rate

    BAUD_RATE = 9600

    # Open the serial port
    ser = serial.Serial(COM_PORT, BAUD_RATE)
    try:
        while True:
            # Read a line of data from the serial port
            data = ser.readline().decode().strip()

            # Process the data as needed
            print("Received:", data)

    except KeyboardInterrupt:
        # Close the serial port when Ctrl+C is pressed
        ser.close()


def real_time_map(x, y):
    class RealTimePlot(FigureCanvas):
        def __init__(self, parent=None, width=5, height=4, dpi=100):
            fig = Figure(figsize=(width, height), dpi=dpi)
            self.axes = fig.add_subplot(111)
            self.axes.grid(True)  # Enabling gridlines
            super(RealTimePlot, self).__init__(fig)
            self.setParent(parent)

        def plot(self, data):
            self.axes.clear()
            self.axes.plot(data, color='red')  # Setting plot color to red
            self.axes.grid(True)  # Enabling gridlines
            self.draw()

    class RealTimeMap(QWidget):
        def __init__(self):
            super().__init__()

            self.zoom_level = 5  # Adjust the zoom level here
            self.map_object = folium.Map(location=[0, 0], zoom_start=self.zoom_level)
            self.marker_cluster = MarkerCluster().add_to(self.map_object)
            self.coordinates_history = []
            self.is_auto_refresh = True
            self.temperature_data = []
            self.pressure_data = []
            self.height_data = []
            self.time_data = []

            self.init_ui()

            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_data)
            self.timer.start(1000)  # Update every 1 second

        def init_ui(self):
            self.webview = QWebEngineView()
            self.webview.setHtml(self.map_object._repr_html_())

            self.com_port_combobox = QComboBox()
            for i in range(1, 13):
                self.com_port_combobox.addItem(f"COM{i}")

            self.com_port_combobox.currentIndexChanged.connect(self.connect_to_com_port)
            self.com_port_combobox.setFixedSize(300, 20)

            self.refresh_button = QPushButton("Refresh options")
            self.refresh_button.clicked.connect(self.show_refresh_option_dialog)
            self.refresh_button.setFixedSize(300, 20)

            # Creating a QHBoxLayout for the buttons above the map
            buttons_layout = QHBoxLayout()
            buttons_layout.addWidget(self.com_port_combobox)
            buttons_layout.addWidget(self.refresh_button)

            self.temp_plot = RealTimePlot(self, width=5, height=4, dpi=100)
            self.pressure_plot = RealTimePlot(self, width=5, height=4, dpi=100)
            self.height_plot = RealTimePlot(self, width=5, height=4, dpi=100)

            self.rssi_label = QLabel("RSSI: N/A")
            self.temperature_label = QLabel("Temperature: N/A")
            self.pressure_label = QLabel("Pressure: N/A")
            self.height_label = QLabel("Height: N/A")

            controls_layout = QHBoxLayout()
            controls_layout.addWidget(self.rssi_label)

            labels_layout = QHBoxLayout()
            labels_layout.addWidget(self.temperature_label)
            labels_layout.addWidget(self.pressure_label)
            labels_layout.addWidget(self.height_label)

            plots_layout = QHBoxLayout()
            plots_layout.addWidget(self.temp_plot)
            plots_layout.addWidget(self.pressure_plot)
            plots_layout.addWidget(self.height_plot)

            layout = QVBoxLayout()
            layout.addLayout(buttons_layout)  # Add buttons layout above the map
            layout.addWidget(self.webview)
            layout.addLayout(controls_layout)
            layout.addLayout(labels_layout)
            layout.addLayout(plots_layout)

            self.setLayout(layout)

        def connect_to_com_port(self, index):
            selected_com_port = self.com_port_combobox.currentText()
            LoRa(selected_com_port)

        def update_data(self):
            if self.is_auto_refresh:
                self.update_map()
                self.update_plots()
                self.update_labels()

        def update_map(self):
            latitude = random.uniform(51, 51.3)
            longitude = random.uniform(21, 21.2)
            coordinates = (latitude, longitude)

            self.coordinates_history.append(coordinates)
            self.map_object.location = coordinates

            # Calculate the latest coordinates
            latest_coordinates = self.coordinates_history[-1]

            # Center the map on the latest coordinates using JavaScript
            js_code = f"""
                   var latlng = L.latLng({latest_coordinates[0]}, {latest_coordinates[1]});
                   window.map.setView(latlng);
               """
            self.webview.page().runJavaScript(js_code)

            if len(self.coordinates_history) > 1:
                # Calculate color gradient
                num_points = len(self.coordinates_history)
                color_gradient = list(Color("blue").range_to(Color("red"), num_points))
                for i in range(1, num_points):
                    start_color = color_gradient[i - 1].hex
                    end_color = color_gradient[i].hex
                    folium.PolyLine([self.coordinates_history[i - 1], self.coordinates_history[i]],
                                    color=start_color,
                                    fill=False,
                                    weight=2,
                                    opacity=0.7).add_to(self.map_object)

            self.map_object.options['zoom'] = 7
            # Add marker for the most recent point ale to robi mess więc po chuj
            #folium.Marker(location=coordinates, icon=folium.Icon(color='red')).add_to(self.map_object)

            self.webview.setHtml(self.map_object._repr_html_())

        def update_plots(self):
            time = len(self.temperature_data)
            self.time_data.append(time)
            self.temperature_data.append(random.randint(10, 25))
            self.pressure_data.append(random.randint(800, 1050))
            self.height_data.append(random.randint(0, 3000))

            self.temp_plot.plot(self.temperature_data)
            self.pressure_plot.plot(self.pressure_data)
            self.height_plot.plot(self.height_data)

        def update_labels(self):
            self.rssi_label.setText(f"RSSI: {random.randint(-100, -50)} dBm")
            self.temperature_label.setText(f"Temperature: {self.temperature_data[-1]}°C")
            self.pressure_label.setText(f"Pressure: {self.pressure_data[-1]} hPa")
            self.height_label.setText(f"Height: {self.height_data[-1]} m")

        def toggle_refresh_option(self):
            self.is_auto_refresh = not self.is_auto_refresh

        def show_refresh_option_dialog(self):
            dialog = RefreshOptionDialog()
            result = dialog.exec_()
            if result == QMessageBox.Accepted:
                self.is_auto_refresh = True
            else:
                self.is_auto_refresh = False

        def get_bounds(self, coordinates_history):
            min_lat = min(lat for lat, lon in coordinates_history)
            max_lat = max(lat for lat, lon in coordinates_history)
            min_lon = min(lon for lat, lon in coordinates_history)
            max_lon = max(lon for lat, lon in coordinates_history)
            return [(min_lat, min_lon), (max_lat, max_lon)]

    if __name__ == '__main__':
        app = QApplication(sys.argv)
        window = RealTimeMap()
        window.setWindowIcon(QIcon(r"C:\Users\sherl\Downloads\eye_logo.png"))  # wstawiam logo w prawy górny róg


        window.setWindowTitle('Eye-In-The-Sky control center')
        window.setGeometry(100, 100, 800, 600)  # Adjust the window size
        window.show()
        sys.exit(app.exec_())


real_time_map(800, 600)  # Adjust the size of the window here






