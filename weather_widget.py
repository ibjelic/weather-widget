import sys
import requests
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QGridLayout, QFrame
from PyQt5.QtCore import QTimer, Qt, QTime
from PyQt5.QtGui import QPixmap, QImage, QPainter, QColor, QPalette
from datetime import datetime

API_KEY = '###'  # Replace with your OpenWeatherMap API key

class BlurryWindow(QWidget):
    def __init__(self, screen):
        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background:transparent;")
        self.layout = QVBoxLayout()
        # self.layout.setAlignment(Qt.AlignCenter)        
        self.layout.setAlignment(Qt.AlignCenter)
        font_color = "#FFFFFF"  # White color
        self.clock_label = QLabel(self)
        self.clock_label.setStyleSheet(f"font-size: 42pt; font-family: Segoe UI; font-weight: bold; color: {font_color};")
        self.clock_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.clock_label)

        self.weather_grid = QGridLayout()
        self.weather_grid.setSpacing(10)
        self.layout.addLayout(self.weather_grid)

        self.forecast_grid = QGridLayout()
        self.forecast_grid.setSpacing(10)
        self.layout.addLayout(self.forecast_grid)

        self.setLayout(self.layout)

        self.update_clock()
        self.update_weather()

        # Update clock every second
        clock_timer = QTimer(self)
        clock_timer.timeout.connect(self.update_clock)
        clock_timer.start(1000)

        # Update weather every 10 minutes
        weather_timer = QTimer(self)
        weather_timer.timeout.connect(self.update_weather)
        weather_timer.start(600000)

        # Move the window to the specified screen
        self.move(screen.geometry().topLeft())

    # def update_clock(self):
    #     current_time = QTime.currentTime().toString("hh:mm:ss")
    #     self.clock_label.setText(current_time)
    def update_clock(self):
        current_time = QTime.currentTime().toString("hh:mm:ss")
        current_date = datetime.now().strftime("%A, %d %B %Y")
        self.clock_label.setText(f"{current_time}\n{current_date}")

    def update_weather(self):
        # Fetch weather data from the API using the API key and city name
        url = f'http://api.openweathermap.org/data/2.5/forecast'
        params = {
            "q": "Belgrade,RS",  # Replace with the desired city and country code
            "appid": API_KEY,
            "units": 'metric'
        }
        response = requests.get(url, params=params)
        data = response.json()

        # Clear the weather grid
        for i in reversed(range(self.weather_grid.count())):
            self.weather_grid.itemAt(i).widget().setParent(None)

        # Clear the forecast grid
        for i in reversed(range(self.forecast_grid.count())):
            self.forecast_grid.itemAt(i).widget().setParent(None)
        font_color = "#FFFFFF"  # White color

        # Check if the 'list' key exists in the response data
        if 'list' in data:
            forecast_list = data['list']

            # Populate the weather grid with hourly forecast data
            hourly_forecast = forecast_list[:8]

            for i, forecast in enumerate(hourly_forecast):
                cell_widget = QWidget(self)
                cell_layout = QVBoxLayout(cell_widget)

                # Add reference to time
                time_label = QLabel(f"{forecast['dt_txt'].split()[1]}")
                time_label.setStyleSheet(f"color: {font_color}; font-size: 14pt; font-weight: bold;")
                time_label.setAlignment(Qt.AlignCenter)
                cell_layout.addWidget(time_label)

                # Add weather icon
                weather_icon = forecast['weather'][0]['icon']
                icon_url = f"http://openweathermap.org/img/wn/{weather_icon}.png"
                icon_label = QLabel(self)
                icon_image = QImage()
                icon_image.loadFromData(requests.get(icon_url).content)
                icon_label.setPixmap(QPixmap.fromImage(icon_image))
                cell_layout.addWidget(icon_label)

                # Add weather information
                temperature_label = QLabel(f"T: {forecast['main']['temp']}°C")
                humidity_label = QLabel(f"H: {forecast['main']['humidity']}%")
                pressure_label = QLabel(f"P: {forecast['main']['pressure']} hPa")
                wind_speed_label = QLabel(f"WS: {forecast['wind']['speed']} km/h")
                rain_chance_label = QLabel(f"RC: {int(forecast['pop']*100)}%")

                temperature_label.setStyleSheet(f"color: {font_color}; font-size: 12pt;")
                humidity_label.setStyleSheet(f"color: {font_color}; font-size: 12pt;")
                pressure_label.setStyleSheet(f"color: {font_color}; font-size: 12pt;")
                wind_speed_label.setStyleSheet(f"color: {font_color}; font-size: 12pt;")
                rain_chance_label.setStyleSheet(f"color: {font_color}; font-size: 12pt;")

                cell_layout.addWidget(temperature_label)
                cell_layout.addWidget(humidity_label)
                cell_layout.addWidget(pressure_label)
                cell_layout.addWidget(wind_speed_label)
                cell_layout.addWidget(rain_chance_label)

                cell_widget.setLayout(cell_layout)

                # Add separators between cells
                line = QFrame()
                line.setFrameShape(QFrame.VLine)
                line.setFrameShadow(QFrame.Sunken)
                line.setStyleSheet("background-color: white;")
                self.weather_grid.addWidget(line, 1, i, 4, 1)

                self.weather_grid.addWidget(cell_widget, 1, i)

            # Populate the forecast grid with daily forecast data
            daily_forecast = {}
            for forecast in forecast_list:
                date = forecast['dt_txt'].split()[0]
                if date not in daily_forecast:
                    daily_forecast[date] = {
                        'temperatures': [],
                        'humidity': [],
                        'pressure': [],
                        'wind_speed': [],
                        'rain_chance': []
                    }
                daily_forecast[date]['temperatures'].append(forecast['main']['temp'])
                daily_forecast[date]['humidity'].append(forecast['main']['humidity'])
                daily_forecast[date]['pressure'].append(forecast['main']['pressure'])
                daily_forecast[date]['wind_speed'].append(forecast['wind']['speed'])
                daily_forecast[date]['rain_chance'].append(forecast['pop']*100)


            daily_forecast_dates = list(daily_forecast.keys())
            daily_forecast_dates.sort()
            daily_forecast_dates = daily_forecast_dates[:5]  # Limit to 5 days

            for i, date in enumerate(daily_forecast_dates):
                cell_widget = QWidget(self)
                cell_layout = QVBoxLayout(cell_widget)

                # Add reference to date
                date_label = QLabel(date)
                date_label.setStyleSheet(f"color: {font_color}; font-size: 14pt; font-weight: bold;")
                date_label.setAlignment(Qt.AlignCenter)
                cell_layout.addWidget(date_label)

                # Add weather information
                average_temperature = sum(daily_forecast[date]['temperatures']) / len(daily_forecast[date]['temperatures'])
                average_humidity = sum(daily_forecast[date]['humidity']) / len(daily_forecast[date]['humidity'])
                average_pressure = sum(daily_forecast[date]['pressure']) / len(daily_forecast[date]['pressure'])
                average_wind_speed = sum(daily_forecast[date]['wind_speed']) / len(daily_forecast[date]['wind_speed'])
                average_rain_chance = sum(daily_forecast[date]['rain_chance']) / len(daily_forecast[date]['rain_chance'])

                temperature_label = QLabel(f"T: {average_temperature:.1f}°C")
                humidity_label = QLabel(f"H: {average_humidity:.1f}%")
                pressure_label = QLabel(f"P: {average_pressure:.1f} hPa")
                wind_speed_label = QLabel(f"WS: {average_wind_speed:.1f} km/h")
                rain_chance_label = QLabel(f"RC: {average_rain_chance:.1f}%")

                temperature_label.setStyleSheet(f"color: {font_color}; font-size: 12pt;")
                humidity_label.setStyleSheet(f"color: {font_color}; font-size: 12pt;")
                pressure_label.setStyleSheet(f"color: {font_color}; font-size: 12pt;")
                wind_speed_label.setStyleSheet(f"color: {font_color}; font-size: 12pt;")
                rain_chance_label.setStyleSheet(f"color: {font_color}; font-size: 12pt;")

                cell_layout.addWidget(temperature_label)
                cell_layout.addWidget(humidity_label)
                cell_layout.addWidget(pressure_label)
                cell_layout.addWidget(wind_speed_label)
                cell_layout.addWidget(rain_chance_label)

                cell_widget.setLayout(cell_layout)

                # Add separators between cells
                line = QFrame()
                line.setFrameShape(QFrame.VLine)
                line.setFrameShadow(QFrame.Sunken)
                line.setStyleSheet("background-color: white;")
                self.forecast_grid.addWidget(line, 1, i, 4, 1)

                self.forecast_grid.addWidget(cell_widget, 1, i)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(0, 0, 0, 180))
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Specify the index of the monitor where you want the window to run
    monitor_index = 1 # Change this to the desired monitor index (e.g., 0 for the first monitor)

    # Get the list of available screens
    available_screens = app.screens()

    if monitor_index < len(available_screens):
        # Create the window and pass the desired screen as an argument
        window = BlurryWindow(screen=available_screens[monitor_index])

        # Set the window background color to black
        palette = QPalette()
        palette.setColor(QPalette.Background, Qt.black)
        window.setPalette(palette)

        window.showFullScreen()
    else:
        print(f"Monitor index {monitor_index} is not available.")

    sys.exit(app.exec_())
