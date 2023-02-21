import math
import time
import tkinter as tk
import tkintermapview
from geographiclib.geodesic import Geodesic
from PIL import Image, ImageTk


class ComputeCoords:
    def __init__(self):
        self.geod = Geodesic.WGS84
        self.ppm = 1 / 0.1122
        # one point (x,y) in the canvas and the corresponding position (lat,lon)
        self.refCoord = [651, 279]
        self.refPosition = [41.2763748, 1.9889669]

    def convert(self, position):
        g = self.geod.Inverse(
            float(position[0]),
            float(position[1]),
            self.refPosition[0],
            self.refPosition[1],
        )
        azimuth = 180 - float(g["azi2"])
        dist = float(g["s12"])

        # ATENCION: NO SE POR QUE AQUI TENGO QUE RESTAR EN VEZ DE SUMAR
        x = self.refCoord[0] - math.trunc(
            dist * self.ppm * math.sin(math.radians(azimuth))
        )
        y = self.refCoord[1] - math.trunc(
            dist * self.ppm * math.cos(math.radians(azimuth))
        )
        return x, y


class MapFrameClass:
    def __init__(self):
        self.message = None
        self.point = None
        self.canvas = None
        self.bg = None
        self.converter = None
        self.image = None
        self.father_frame = None
        self.map_frame = None
        self.drone_lat = None
        self.drone_lon = None
        self.map_widget = None
        self.geod = None
        self.ppm = None
        self.drone_x = None
        self.drone_y = None
        self.to_east = None
        self.to_west = None
        self.to_north = None
        self.to_south = None
        self.dest = None
        self.N = None
        self.S = None
        self.E = None
        self.W = None

    def build_frame(self, father_frame, position, selected_level):
        self.father_frame = father_frame
        self.map_frame = tk.Frame(father_frame)
        self.converter = ComputeCoords()
        self.drone_lat = float(position[0])
        self.drone_lon = float(position[1])

        self.map_frame.rowconfigure(0, weight=1)
        self.map_frame.columnconfigure(0, weight=1)

        if selected_level == "Basico":
            self.image = Image.open("../assets_needed/caso1.png")
        elif selected_level == "Medio":
            self.image = Image.open("../assets_needed/caso2.png")
        else:
            self.image = Image.open("../assets_needed/caso3.png")

        self.image = self.image.resize((800, 600), Image.ANTIALIAS)
        self.bg = ImageTk.PhotoImage(self.image)
        self.canvas = tk.Canvas(self.map_frame, width=800, height=600)
        self.canvas.grid(row=0, column=0, sticky="nesw")
        self.canvas.create_image(0, 0, image=self.bg, anchor="nw")

        self.ppm = 1 / 0.1122

        self.drone_x, self.drone_y = self.converter.convert(position)

        self.point = self.canvas.create_oval(
            self.drone_x - 8,
            self.drone_y - 8,
            self.drone_x + 8,
            self.drone_y + 8,
            fill="blue",
        )

        # lines pointing to North, South, East and West
        point_north_x = self.drone_x + math.trunc(
            5 * self.ppm * math.sin(math.radians(180))
        )
        point_north_y = self.drone_y + math.trunc(
            5 * self.ppm * math.cos(math.radians(180))
        )
        self.to_north = self.canvas.create_line(
            self.drone_x, self.drone_y, point_north_x, point_north_y, fill="blue"
        )
        self.N = self.canvas.create_text(
            point_north_x,
            point_north_y,
            fill="yellow",
            text="N",
            font=("Helvetica 18 bold"),
        )

        point_east_x = self.drone_x + math.trunc(
            5 * self.ppm * math.sin(math.radians(90))
        )
        point_east_y = self.drone_y + math.trunc(
            5 * self.ppm * math.cos(math.radians(90))
        )
        self.to_east = self.canvas.create_line(
            self.drone_x, self.drone_y, point_east_x, point_east_y, fill="yellow"
        )

        self.E = self.canvas.create_text(
            point_east_x,
            point_east_y,
            fill="yellow",
            text="E",
            font=("Helvetica 18 bold"),
        )

        point_south_x = self.drone_x + math.trunc(
            5 * self.ppm * math.sin(math.radians(0))
        )
        point_south_y = self.drone_y + math.trunc(
            5 * self.ppm * math.cos(math.radians(0))
        )
        self.to_south = self.canvas.create_line(
            self.drone_x, self.drone_y, point_south_x, point_south_y, fill="pink"
        )
        self.S = self.canvas.create_text(
            point_south_x,
            point_south_y,
            fill="yellow",
            text="S",
            font=("Helvetica 18 bold"),
        )

        point_west_x = self.drone_x + math.trunc(
            5 * self.ppm * math.sin(math.radians(270))
        )
        point_west_y = self.drone_y + math.trunc(
            5 * self.ppm * math.cos(math.radians(270))
        )
        self.to_west = self.canvas.create_line(
            self.drone_x, self.drone_y, point_west_x, point_west_y, fill="green"
        )

        self.W = self.canvas.create_text(
            point_west_x,
            point_west_y,
            fill="yellow",
            text="W",
            font=("Helvetica 18 bold"),
        )
        self.message = None
        return self.map_frame

    def putText(self, message):
        if self.message in self.canvas.find_all():
            self.canvas.delete(self.message)
        self.message = self.canvas.create_text(
            400, 500, fill="yellow", text=message, font=("Helvetica 30 bold")
        )

    """
    def set_destination(self, position):
        position[0] = 41.2763108
        position[1] = 1.9883282

        g = self.geod.Inverse(
            self.drone_lat, self.drone_lon, float(position[0]), float(position[1])
        )

        azimuth = 180 - float(g["azi2"])
        dist = float(g["s12"])
        print("*****", dist, azimuth)

        dest_x = self.drone_x + math.trunc(
            dist * self.ppm * math.sin(math.radians(azimuth))
        )
        dest_y = self.drone_y + math.trunc(
            dist * self.ppm * math.cos(math.radians(azimuth))
        )

        self.dest = self.map_widget.canvas.create_oval(
            dest_x - 8, dest_y - 8, dest_x + 8, dest_y + 8, fill="green"
        )
    """

    def move_drone(self, position, color):
        self.drone_x, self.drone_y = self.converter.convert(position)

        self.canvas.itemconfig(self.point, fill=color)

        self.canvas.coords(
            self.point,
            self.drone_x - 8,
            self.drone_y - 8,
            self.drone_x + 8,
            self.drone_y + 8,
        )
        self.drone_lat = float(position[0])
        self.drone_lon = float(position[1])

        self.canvas.delete(self.to_south)
        self.canvas.delete(self.to_east)
        self.canvas.delete(self.to_north)
        self.canvas.delete(self.to_west)

        self.canvas.delete(self.N)
        self.canvas.delete(self.E)
        self.canvas.delete(self.S)
        self.canvas.delete(self.W)

        # lines pointing to North, South, East and West
        point_north_x = self.drone_x + math.trunc(
            5 * self.ppm * math.sin(math.radians(180))
        )
        point_north_y = self.drone_y + math.trunc(
            5 * self.ppm * math.cos(math.radians(180))
        )
        self.to_north = self.canvas.create_line(
            self.drone_x, self.drone_y, point_north_x, point_north_y, fill="blue"
        )
        self.N = self.canvas.create_text(
            point_north_x,
            point_north_y,
            fill="yellow",
            text="N",
            font=("Helvetica 18 bold"),
        )

        point_east_x = self.drone_x + math.trunc(
            5 * self.ppm * math.sin(math.radians(90))
        )
        point_east_y = self.drone_y + math.trunc(
            5 * self.ppm * math.cos(math.radians(90))
        )
        self.to_east = self.canvas.create_line(
            self.drone_x, self.drone_y, point_east_x, point_east_y, fill="yellow"
        )

        self.E = self.canvas.create_text(
            point_east_x,
            point_east_y,
            fill="yellow",
            text="E",
            font=("Helvetica 18 bold"),
        )

        point_south_x = self.drone_x + math.trunc(
            5 * self.ppm * math.sin(math.radians(0))
        )
        point_south_y = self.drone_y + math.trunc(
            5 * self.ppm * math.cos(math.radians(0))
        )
        self.to_south = self.canvas.create_line(
            self.drone_x, self.drone_y, point_south_x, point_south_y, fill="pink"
        )
        self.S = self.canvas.create_text(
            point_south_x,
            point_south_y,
            fill="yellow",
            text="S",
            font=("Helvetica 18 bold"),
        )

        point_west_x = self.drone_x + math.trunc(
            5 * self.ppm * math.sin(math.radians(270))
        )
        point_west_y = self.drone_y + math.trunc(
            5 * self.ppm * math.cos(math.radians(270))
        )
        self.to_west = self.canvas.create_line(
            self.drone_x, self.drone_y, point_west_x, point_west_y, fill="green"
        )
        self.W = self.canvas.create_text(
            point_west_x,
            point_west_y,
            fill="yellow",
            text="W",
            font=("Helvetica 18 bold"),
        )

    def mark_at_home(self):
        self.canvas.itemconfig(self.point, fill="blue")
