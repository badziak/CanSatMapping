import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, QTimer
import folium
import random

class RealTimeMap(QWidget):
    def __init__(self):
        super().__init__()

        self.map_object = folium.Map(location=[0, 0], zoom_start=2)
        self.coordinates_history = []
        self.is_paused = False

        self.webview = QWebEngineView()
        self.webview.setHtml(self.map_object._repr_html_())

        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.toggle_pause)

        layout = QVBoxLayout()
        layout.addWidget(self.webview)

       # layout.addWidget(self.update_button)
        layout.addWidget(self.pause_button)
        self.setLayout(layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_map)
        self.timer.start(1000)  # Uppdate every 1 second

    def update_map(self):
        if not self.is_paused:
            latitude = float(random.uniform())
            longitude = float(random.uniform())
            coordinates = (latitude, longitude)

            self.coordinates_history.append(coordinates)
            #if len(self.coordinates_history) > 5:
            #    self.coordinates_history = self.coordinates_history[-5:]

            self.map_object = folium.Map(location=coordinates, zoom_start=2)

            for coord in self.coordinates_history:
                map_center = [coord[0], coord[1]]
                folium.Marker(location=map_center, popup="Your Location").add_to(self.map_object)
            for i, coord in enumerate(self.coordinates_history):
                map_center = [coord[0], coord[1]]
                marker_color = 'red' if i == len(self.coordinates_history) - 1 else 'green'
                folium.Marker(location=map_center, popup="Your Location", icon=folium.Icon(color=marker_color)).add_to(
                    self.map_object)
            if len(self.coordinates_history) > 1:
                line = folium.PolyLine(self.coordinates_history, color='blue')
                line.add_to(self.map_object)

            self.webview.setHtml(self.map_object._repr_html_())

            self.webview.setHtml(self.map_object._repr_html_())

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_button.setText("Resume")
        else:
            self.pause_button.setText("Pause")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RealTimeMap()
    window.setGeometry(100, 100, 800, 600)
    window.setWindowTitle('Real-time Map Application')
    window.show()
    sys.exit(app.exec_())


