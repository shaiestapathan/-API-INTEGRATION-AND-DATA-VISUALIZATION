from tkinter import *
from tkinter import messagebox
import requests
from PIL import Image, ImageTk
import io
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import threading
import time

def round_rectangle(canvas, x1, y1, x2, y2, radius=20, **kwargs):
    points = [
        x1+radius, y1, x2-radius, y1, x2, y1, x2, y1+radius,
        x2, y2-radius, x2, y2, x2-radius, y2, x1+radius, y2,
        x1, y2, x1, y2-radius, x1, y1+radius, x1, y1
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)

def show_typing_animation():
    search_button.config(text="⏳ Fetching...")
    root.update_idletasks()

def hide_typing_animation():
    search_button.config(text="🔍 Search Weather")

def get_weather_threaded():
    threading.Thread(target=get_weather).start()

def get_weather():
    city = city_entry.get()
    if not city.strip():
        messagebox.showinfo("Input Error", "Please enter a city name.")
        return

    greetings = ["hi", "hello", "hey", "hola"]
    if city.lower() in greetings:
        messagebox.showinfo("Greeting", "Hello there! Please enter a city name to check the weather 🌦️")
        return

    show_typing_animation()

    api_key = "4eae97037b9bd531fb6608dc80fed456"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

    try:
        response = requests.get(url)
        data = response.json()
    except Exception as e:
        hide_typing_animation()
        messagebox.showerror("Error", f"Something went wrong.\n{e}")
        return

    if data.get("main"):
        temp = data["main"]["temp"]
        #feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        wind_speed = data["wind"]["speed"]
        condition = data["weather"][0]["description"].title()
        icon_code = data["weather"][0]["icon"]
        sunrise = datetime.fromtimestamp(data["sys"]["sunrise"]).strftime('%I:%M %p')
        sunset = datetime.fromtimestamp(data["sys"]["sunset"]).strftime('%I:%M %p')
        fetched_time = datetime.now().strftime('%b %d, %Y %I:%M %p')

        temp_label.config(text=f"🌡 Temperature: {temp}°C")
        #feels_like_label.config(text=f"🌡 Feels Like: {feels_like}°C")
        humidity_label.config(text=f"💧 Humidity: {humidity}%")
        pressure_label.config(text=f"⚙ Pressure: {pressure} hPa")
        wind_label.config(text=f"🌬 Wind Speed: {wind_speed} m/s")
        condition_label.config(text=f"🌥 Condition: {condition}")
        sunrise_label.config(text=f"🌅 Sunrise: {sunrise}")
        sunset_label.config(text=f"🌇 Sunset: {sunset}")
        timestamp_label.config(text=f"📅 Last Updated: {fetched_time}")

        icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
        icon_img = Image.open(io.BytesIO(requests.get(icon_url).content))
        icon_tk = ImageTk.PhotoImage(icon_img)
        weather_icon_label.config(image=icon_tk)
        weather_icon_label.image = icon_tk

        update_chart(temp, humidity, pressure)
        city_entry.delete(0, END)
    else:
        messagebox.showerror("City Not Found", f"Could not find weather data for '{city}'.")

    hide_typing_animation()

def update_chart(temp, humidity, pressure):
    chart_fig.clear()
    ax = chart_fig.add_subplot(111)
    values = [temp, humidity, pressure]
    labels = ["Temperature °C", "Humidity %", "Pressure hPa"]
    colors = ['#ff6f61', '#6ec6ff', '#b388ff']

    bars = ax.bar(labels, values, color=colors)
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval + 2, round(yval, 1), ha='center', fontsize=10, color='white')

    ax.set_facecolor('#1a1c2e')
    ax.tick_params(colors='white')
    ax.set_title("Weather Metrics Overview", color='white', fontsize=12)
    for spine in ax.spines.values():
        spine.set_color('white')

    chart_canvas.draw()

root = Tk()
root.title("Modern Weather Dashboard")
root.geometry("980x720")
root.configure(bg="#0f111a")

font_header = ("Segoe UI Semibold", 16)
font_info = ("Segoe UI", 13)

# Search Frame
search_frame = Frame(root, bg="#0f111a")
search_frame.grid(row=0, column=0, sticky="ew", pady=20, padx=20)
search_frame.columnconfigure(0, weight=1)

city_entry = Entry(search_frame, font=("Segoe UI", 14), bg="#1c1e2f", fg="white",
                   insertbackground="white", bd=0)
city_entry.insert(0, "Enter city name...")
city_entry.grid(row=0, column=0, sticky="ew", ipady=6, padx=(0, 10))

search_button = Button(search_frame, text="🔍 Search Weather", command=get_weather_threaded,
                       font=("Segoe UI", 11, "bold"), bg="#214d79", fg="white",
                       activebackground="#2d5d9f", relief=FLAT, padx=10, pady=6)
search_button.grid(row=0, column=1)

# Info Canvas Background
info_canvas = Canvas(root, bg="#0f111a", highlightthickness=0)
info_canvas.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
info_canvas.bind("<Configure>", lambda e: (
    info_canvas.delete("round_rect"),
    round_rectangle(info_canvas, 5, 5, e.width-5, e.height-5, radius=20, fill="#141625", tags="round_rect")
))

info_frame = Frame(info_canvas, bg="#141625")
info_frame.place(relx=0.01, rely=0.02, relwidth=0.98, relheight=0.96)

Label(info_frame, text="📍 Weather Info", font=font_header, bg="#141625", fg="white")\
    .grid(row=0, column=0, columnspan=4, sticky="w", pady=5, padx=10)

temp_label = Label(info_frame, text="🌡 Temperature: --", font=font_info, bg="#141625", fg="white")
#feels_like_label = Label(info_frame, text="🌡 Feels Like: --", font=font_info, bg="#141625", fg="white")
humidity_label = Label(info_frame, text="💧 Humidity: --", font=font_info, bg="#141625", fg="white")
pressure_label = Label(info_frame, text="⚙ Pressure: --", font=font_info, bg="#141625", fg="white")
wind_label = Label(info_frame, text="🌬 Wind Speed: --", font=font_info, bg="#141625", fg="white")
condition_label = Label(info_frame, text="🌥 Condition: --", font=font_info, bg="#141625", fg="white")
weather_icon_label = Label(info_frame,text="Weather:--", font=font_info, bg="#141625", fg="white")
sunrise_label = Label(info_frame, text="🌅 Sunrise: --", font=font_info, bg="#141625", fg="white")
sunset_label = Label(info_frame, text="🌇 Sunset: --", font=font_info, bg="#141625", fg="white")
timestamp_label = Label(info_frame, text="📅 Last Updated: --", font=("Segoe UI", 11), bg="#141625", fg="white")

# Row-wise Grid
temp_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
#feels_like_label.grid(row=1, column=1, sticky="w", padx=10, pady=5)
humidity_label.grid(row=1, column=1, sticky="w", padx=10, pady=5)
pressure_label.grid(row=1, column=2, sticky="w", padx=10, pady=5)

wind_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)
condition_label.grid(row=2, column=1, sticky="w", padx=10, pady=5)
weather_icon_label.grid(row=2, column=2, sticky="w", padx=10, pady=5)

sunrise_label.grid(row=3, column=0, sticky="w", padx=10, pady=5)
sunset_label.grid(row=3, column=1, sticky="w", padx=10, pady=5)
timestamp_label.grid(row=3, column=2, sticky="w", padx=10, pady=5)

# Enable row/column weights so the grid expands
root.grid_rowconfigure(2, weight=1)
root.grid_columnconfigure(0, weight=1)

# Chart Canvas Background
chart_canvas_bg = Canvas(root, bg="#0f111a", highlightthickness=0)
chart_canvas_bg.grid(row=2, column=0, sticky="nsew", padx=20, pady=20)
chart_canvas_bg.bind("<Configure>", lambda e: (
    chart_canvas_bg.delete("round_rect"),
    round_rectangle(chart_canvas_bg, 5, 5, e.width - 5, e.height - 5, radius=20, fill="#141625", tags="round_rect")
))

# Make sure the chart frame fills the canvas
chart_frame = Frame(chart_canvas_bg, bg="#141625")
chart_frame.place(relx=0, rely=0, relwidth=1, relheight=1)  # Full fill

# Chart Figure
chart_fig = plt.Figure(figsize=(5, 3), dpi=100)
chart_ax = chart_fig.add_subplot(111)

# Remove axis ticks and borders
chart_ax.set_xticks([])
chart_ax.set_yticks([])
for spine in chart_ax.spines.values():
    spine.set_visible(False)


# Chart Canvas
chart_canvas = FigureCanvasTkAgg(chart_fig, master=chart_frame)
chart_canvas_widget = chart_canvas.get_tk_widget()
chart_canvas_widget.pack(fill="both", expand=True)  # Important: fill and expand

footer = Label(root, text="Powered by OpenWeatherMap", font=("Segoe UI", 9), fg="#888", bg="#0f111a")
footer.grid(row=3, column=0, pady=10)

# Responsive config
root.rowconfigure(1, weight=1)
root.rowconfigure(2, weight=1)
root.rowconfigure(3, weight=0)
root.columnconfigure(0, weight=1)

root.mainloop()