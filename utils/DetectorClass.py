import base64
import json
import math
import threading
import time
import tkinter as tk

import numpy as np
from cv2 import cv2
import paho.mqtt.client as mqtt
from PIL import Image, ImageTk


from utils.fingerDetector import FingerDetector
from utils.poseDetector import PoseDetector
from utils.faceDetector import FaceDetector
from utils.speechDetector import SpeechDetector
from utils.MapFrameClass import MapFrameClass
from PIL import ImageTk
from tkinter import messagebox, YES, BOTH, NW
from apscheduler.schedulers.background import BackgroundScheduler
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


class DetectorClass:
    def __init__(self):
        self.father_frame = None
        self.mode = None
        self.client = None
        self.client2 = None
        self.client3 = None
        self.cap = None
        self.detector = None
        self.master = None
        self.top_frame = None
        self.state = None
        self.level = None
        self.easy_button = None
        self.difficult_button = None
        self.practice_button = None
        self.close_button = None
        self.button_frame = None
        self.select_scenario_button = None
        self.connect_button = None
        self.arm_button = None
        self.take_off_button = None
        self.return_home_button = None
        self.close_button2 = None
        self.bottom_frame = None
        self.map = None
        self.select_level_window = None
        self.image = None
        self.image1 = None
        self.image2 = None
        self.image3 = None
        self.bg = None
        self.bg1 = None
        self.bg2 = None
        self.bg3 = None
        self.level1_button = None
        self.level2_button = None
        self.level3_button = None
        self.direction = None
        self.selected_level = None
        self.show_video_window = None
        self.sched = None
        # self.canvas4 = None
        self.vidLabel = None
        # self.contador2 = None
        self.returning = None

    def build_frame(self, father_frame, mode):
        # self.contador2 = 0

        # mode can be: fingers, face or pose
        self.father_frame = father_frame
        self.mode = mode
        # treure
        if self.mode == "fingers":
            self.detector = FingerDetector()
        elif self.mode == "pose":
            self.detector = PoseDetector()
        elif self.mode == "voice":
            self.detector = SpeechDetector()
        else:
            self.detector = FaceDetector()

        if self.mode != "voice":
            self.cap = cv2.VideoCapture(0) # obrir camera
        #
        self.master = tk.Frame(self.father_frame)
        self.master.rowconfigure(0, weight=1)
        self.master.rowconfigure(1, weight=1)

        self.top_frame = tk.LabelFrame(self.master, text="Control")
        self.top_frame.columnconfigure(0, weight=1)
        self.top_frame.columnconfigure(1, weight=1)
        self.top_frame.rowconfigure(0, weight=1)
        self.top_frame.rowconfigure(1, weight=1)
        self.top_frame.rowconfigure(2, weight=1)
        self.top_frame.rowconfigure(3, weight=1)

        # level can be easy or difficult
        self.level = "easy"

        self.easy_button = tk.Button(
            self.top_frame, text="Fácil", bg="#367E18", fg="white", command=self.easy
        )
        self.easy_button.grid(
            row=0, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W
        )
        self.difficult_button = tk.Button(
            self.top_frame,
            text="Difícil",
            bg="#CC3636",
            fg="white",
            command=self.difficult,
        )
        self.difficult_button.grid(
            row=0, column=1, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W
        )
        # next button to be shown when level (easy or difficult) selected
        self.select_scenario_button = tk.Button(
            self.top_frame,
            text="Selecciona el escenario",
            bg="#F57328",
            fg="white",
            command=self.set_level,
        )

        # next button to be shown when scenario has been selected
        self.practice_button = tk.Button(
            self.top_frame,
            text="Practica los movimientos",
            bg="#F57328",
            fg="white",
            command=self.practice,
        )
        self.close_button = tk.Button(
            self.top_frame, text="Salir", bg="#FFE9A0", fg="black", command=self.close
        )

        # frame to be shown when practise is finish and user wants to fly
        self.button_frame = tk.Frame(self.top_frame)
        self.button_frame.rowconfigure(0, weight=1)
        self.button_frame.rowconfigure(1, weight=1)
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)
        self.button_frame.columnconfigure(2, weight=1)

        self.connect_button = tk.Button(
            self.button_frame,
            text="Connect",
            bg="#CC3636",
            fg="white",
            command=self.select_connection_mode,
        )
        self.connect_button.grid(
            row=0, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W
        )

        self.arm_button = tk.Button(
            self.button_frame, text="Arm", bg="#CC3636", fg="white", command=self.arm
        )
        self.arm_button.grid(
            row=0, column=1, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W
        )
        self.take_off_button = tk.Button(
            self.button_frame,
            text="Take Off",
            bg="#CC3636",
            fg="white",
            command=self.take_off,
        )
        self.take_off_button.grid(
            row=0, column=2, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W
        )

        # button to be shown when flying
        self.return_home_button = tk.Button(
            self.button_frame,
            text="Retorna",
            bg="#CC3636",
            fg="white",
            command=self.return_home,
        )

        # button to be shown when the dron is back home
        self.close_button2 = tk.Button(
            self.button_frame,
            text="Salir",
            bg="#FFE9A0",
            fg="black",
            command=self.close,
        )

        self.top_frame.grid(
            row=0, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W
        )

        # by defaulf, easy mode is selected
        self.bottom_frame = tk.LabelFrame(self.master, text="EASY")

        if self.mode == "fingers":
            self.image = Image.open("../assets_needed/dedos_faciles.png")
        elif self.mode == "pose":
            self.image = Image.open("../assets_needed/poses_faciles.png")
        elif self.mode == "voice":
            self.image = Image.open("../assets_needed/voces_faciles.png")
        else:
            self.image = Image.open("../assets_needed/caras_faciles.png")

        self.image = self.image.resize((350, 500), Image.ANTIALIAS)
        self.bg = ImageTk.PhotoImage(self.image)
        canvas1 = tk.Canvas(self.bottom_frame, width=350, height=500)
        canvas1.pack(fill="both", expand=True)
        canvas1.create_image(0, 0, image=self.bg, anchor="nw")

        self.bottom_frame.grid(
            row=1, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W
        )
        self.connected = False
        self.state = "disconnected"

        # ens conncectem al imageService
        broker_address = "broker.hivemq.com"
        # broker_address = "localhost"
        broker_port = 8000
        self.client2 = mqtt.Client(transport="websockets")
        self.client2.on_message = self.on_message2  # Callback function executed when a message is received
        self.client2.connect(broker_address, broker_port)
        self.client2.publish('droneCircus/imageService/Connect')
        self.client2.loop_start()

        return self.master

    def show_map(self, position):
        new_window = tk.Toplevel(self.master)
        new_window.title("Map")
        new_window.geometry("800x600")
        self.map = MapFrameClass()
        frame = self.map.build_frame(new_window, position, self.selected_level)
        frame.pack(fill="both", expand="yes", padx=10, pady=10)
        # new_window.mainloop()

    def on_message2(self, cli, userdata, message):
        splited = message.topic.split("/")
        origin = splited[0]
        destination = splited[1]
        command = splited[2]
        print(message.topic)
        if command == "code":
            if self.mode != "voice":
                code = int(message.payload.decode("utf-8"))
                self.direction = self.__set_direction(code)

                if self.state == "flying":
                    if not self.returning:
                        go_topic = "droneCircus/autopilotService/go"
                        if code == 1:
                            self.client.publish(go_topic, "North")
                        elif code == 2:
                            self.client.publish(go_topic, "South")
                        elif code == 3:  # east
                            self.client.publish(go_topic, "East")
                        elif code == 4:
                            self.client.publish(go_topic, "West")
                        elif code == 5:
                            self.client.publish("droneCircus/autopilotService/drop")
                            self.client.publish("droneCircus/autopilotService/reset")
                        elif code == 6:
                            self.returning = True
                            self.direction = "Volviendo a casa"
                            self.return_home()
                        elif code == 0:
                            self.client.publish(go_topic, "Stop")



        if command == "videoFrame":
            # self.contador2 = self.contador2 + 1
            # print("contador 2: ", self.contador2)
            # Decoding the message
            img = base64.b64decode(message.payload)
            # converting into numpy array from buffer
            npimg = np.frombuffer(img, dtype=np.uint8)
            # Decode to Original Frame
            frame2 = cv2.imdecode(npimg, 1)
            res = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)
            # cv2.putText(
            #     frame2,
            #     self.direction,
            #     (50, 450),
            #     cv2.FONT_HERSHEY_SIMPLEX,
            #     3,
            #     (0, 0, 255),
            #     10,
            # )
            # photo = ImageTk.PhotoImage(image=Image.fromarray(res))
            # self.canvas4.create_image(0, 0, image=photo, anchor=tk.NW)
            # cv2.imshow("video", frame2)
            # cv2.waitKey(1)
            res = Image.fromarray(res)
            res = ImageTk.PhotoImage(res)
            self.vidLabel.configure(image=res)
            self.vidLabel.image = res


    def on_message(self, cli, userdata, message):
        splited = message.topic.split("/")
        origin = splited[0]
        destination = splited[1]
        command = splited[2]

        if command == "telemetryInfo":
            telemetry_info = json.loads(message.payload)
            lat = telemetry_info["lat"]
            lon = telemetry_info["lon"]
            state = telemetry_info["state"]
            if state == "connected" and self.state != "connected":
                self.connect_button["text"] = "disconnect"
                self.connect_button["bg"] = "#367E18"
                self.show_map((lat, lon))
                self.state = "connected"
            elif state == "armed":
                self.arm_button["text"] = "armed"
                self.arm_button["bg"] = "#367E18"
                self.state = "armed"
            elif state == "flying" and self.state != "flying":
                self.take_off_button["text"] = "flying"
                self.take_off_button["bg"] = "#367E18"
                self.client.publish(
                    destination + "/" + origin + "/" + "guideManually", "Stop"
                )
                self.state = "flying"
                # this thread will start taking images and detecting patterns to guide the drone
                x = threading.Thread(target=self.flying)
                x.start()
                self.return_home_button.grid(
                    row=2,
                    column=0,
                    padx=5,
                    columnspan=3,
                    pady=5,
                    sticky=tk.N + tk.S + tk.E + tk.W,
                )
            elif state == "flying" and self.state == "flying":
                self.map.move_drone((lat, lon), "red")
            elif state == "returningHome":
                self.map.move_drone((lat, lon), "brown")
                self.state = "returningHome"
            elif (
                state == "onHearth"
                and self.state != "onHearth"
                and self.state != "disconnected"
            ):
                # the dron completed the RTL
                self.map.mark_at_home()
                messagebox.showwarning(
                    "Success", "Ya estamos en casa", parent=self.master
                )
                self.return_home_button.grid_forget()

                self.arm_button["bg"] = "#CC3636"
                self.arm_button["text"] = "Arm"
                self.take_off_button["bg"] = "#CC3636"
                self.take_off_button["text"] = "TakeOff"
                self.return_home_button["text"] = "Retorna"
                self.return_home_button["bg"] = "#CC3636"
                self.state = "onHearth"
                self.client.publish("droneCircus/monitor/stop")

    def connect(self):
        # does not allow to connect if the level of difficulty is not fixed
        if self.select_scenario_button["bg"] == "#367E18":
            if self.connection_mode == "global":
                # in global mode, the external broker must be running in internet
                # and must operate with websockets
                # there are several options:
                # a public broker

                external_broker_address = "broker.hivemq.com"

                # our broker (that requires credentials)
                # external_broker_address = "classpip.upc.edu"
                # a mosquitto broker running at localhost (only in simulation mode)
                #external_broker_address = "localhost"

            else:
                # in local mode, the external broker will run always in localhost
                # (either in production or simulation mode)
                # use this when connecting with the RPi
                external_broker_address = "10.10.10.1"
                #external_broker_address = "localhost"

            # the external broker must run always in port 8000
            external_broker_port = 8000

            self.client = mqtt.Client("Detector", transport="websockets")
            self.client.on_message = self.on_message
            print("voy a conectarme al broker en modo ", self.connection_mode)
            self.client.connect(external_broker_address, external_broker_port)
            self.client.loop_start()
            self.connected = True
            self.close_button2.grid_forget()
            self.client.subscribe("autopilotService/droneCircus/#")
            self.client.publish("droneCircus/autopilotService/connect")
            self.client.publish("droneCircus/monitor/start")
            self.connect_button["text"] = "connecting ..."
            self.connect_button["bg"] = "orange"

        else:
            messagebox.showwarning(
                "Error",
                "Antes de conectar debes fijar el nivel de dificultad",
                parent=self.master,
            )

    def global_mode(self):
        self.connection_mode = "global"
        self.select_connection_mode_window.destroy()
        self.connect()

    def local_mode(self):
        self.connection_mode = "local"
        self.select_connection_mode_window.destroy()
        self.connect()

    def select_connection_mode(self):
        if not self.connected:
            self.select_connection_mode_window = tk.Toplevel(self.master)
            self.select_connection_mode_window.title("Select connection mode")
            self.select_connection_mode_window.geometry("1200x500")
            select_connection_mode_frame = tk.Frame(self.select_connection_mode_window)
            select_connection_mode_frame.pack()
            select_connection_mode_frame.rowconfigure(0, weight=1)
            select_connection_mode_frame.rowconfigure(1, weight=1)
            select_connection_mode_frame.columnconfigure(0, weight=1)
            select_connection_mode_frame.columnconfigure(1, weight=1)

            self.image1 = Image.open("../assets_needed/connection_mode.png")
            self.image1 = self.image1.resize((1100, 450), Image.ANTIALIAS)
            self.bg1 = ImageTk.PhotoImage(self.image1)
            canvas1 = tk.Canvas(select_connection_mode_frame, width=1100, height=450)
            canvas1.create_image(0, 0, image=self.bg1, anchor="nw")
            canvas1.grid(
                row=0,
                column=0,
                padx=5,
                pady=5,
                columnspan=2,
                sticky=tk.N + tk.S + tk.E + tk.W,
            )

            self.global_button = tk.Button(
                select_connection_mode_frame,
                text="Global",
                bg="#CC3636",
                fg="white",
                command=self.global_mode,
            )
            self.global_button.grid(
                row=1, column=0, padx=20, pady=5, sticky=tk.N + tk.S + tk.E + tk.W
            )
            self.local_button = tk.Button(
                select_connection_mode_frame,
                text="Local",
                bg="#CC3636",
                fg="white",
                command=self.local_mode,
            )
            self.local_button.grid(
                row=1, column=1, padx=20, pady=5, sticky=tk.N + tk.S + tk.E + tk.W
            )
        elif self.state != "flying":
            self.connect_button["text"] = "connect"
            self.connect_button["bg"] = ("#CC3636",)
            self.client.publish("droneCircus/autopilotService/disconnect")
            # self.cap.release()
            self.client.loop_stop()
            self.client.disconnect()
            self.client2.disconnect()
            self.client2.loop_stop()
            self.connected = False
            self.state = "disconnected"
        else:
            messagebox.showwarning(
                "Error",
                "No puedes desconectar. Estas volando",
                parent=self.master,
            )

    def set_level(self):
        self.select_level_window = tk.Toplevel(self.master)
        self.select_level_window.title("Select level")
        self.select_level_window.geometry("1000x300")
        select_level_frame = tk.Frame(self.select_level_window)
        select_level_frame.pack()
        select_level_frame.rowconfigure(0, weight=1)
        select_level_frame.rowconfigure(1, weight=1)
        select_level_frame.columnconfigure(0, weight=1)
        select_level_frame.columnconfigure(1, weight=1)
        select_level_frame.columnconfigure(2, weight=1)

        self.image1 = Image.open("../assets_needed/no_fence.png")
        self.image1 = self.image1.resize((320, 240), Image.ANTIALIAS)
        self.bg1 = ImageTk.PhotoImage(self.image1)
        canvas1 = tk.Canvas(select_level_frame, width=320, height=240)
        canvas1.create_image(0, 0, image=self.bg1, anchor="nw")
        canvas1.grid(row=0, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

        self.image2 = Image.open("../assets_needed/fence_case1.png")
        self.image2 = self.image2.resize((320, 240), Image.ANTIALIAS)
        self.bg2 = ImageTk.PhotoImage(self.image2)
        canvas2 = tk.Canvas(select_level_frame, width=320, height=240)
        canvas2.create_image(0, 0, image=self.bg2, anchor="nw")
        canvas2.grid(row=0, column=1, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

        self.image3 = Image.open("../assets_needed/fence_case2.png")
        self.image3 = self.image3.resize((320, 240), Image.ANTIALIAS)
        self.bg3 = ImageTk.PhotoImage(self.image3)
        canvas3 = tk.Canvas(select_level_frame, width=320, height=240)
        canvas3.create_image(0, 0, image=self.bg3, anchor="nw")
        canvas3.grid(row=0, column=2, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W)

        self.level1_button = tk.Button(
            select_level_frame,
            text="Básico",
            bg="#CC3636",
            fg="white",
            command=self.level1,
        )
        self.level1_button.grid(
            row=1, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W
        )
        self.level2_button = tk.Button(
            select_level_frame,
            text="Medio",
            bg="#CC3636",
            fg="white",
            command=self.level2,
        )
        self.level2_button.grid(
            row=1, column=1, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W
        )
        self.level3_button = tk.Button(
            select_level_frame,
            text="Avanzado",
            bg="#CC3636",
            fg="white",
            command=self.level3,
        )
        self.level3_button.grid(
            row=1, column=2, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W
        )

    def level1(self):
        self.selected_level = "Basico"
        self.select_level_window.destroy()
        self.select_scenario_button["text"] = "Básico"
        self.select_scenario_button["bg"] = "#367E18"
        # show button to start practising
        self.practice_button.grid(
            row=2, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W
        )
        self.close_button.grid(
            row=2, column=1, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W
        )

    def level2(self):
        self.selected_level = "Medio"
        self.select_level_window.destroy()
        self.select_scenario_button["text"] = "Medio"
        self.select_scenario_button["bg"] = "#367E18"
        # show button to start practising
        self.practice_button.grid(
            row=2, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W
        )
        self.close_button.grid(
            row=2, column=1, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W
        )

    def level3(self):
        self.selected_level = "Avanzado"
        self.select_level_window.destroy()
        self.select_scenario_button["text"] = "Avanzado"
        self.select_scenario_button["bg"] = "#367E18"
        # show button to start practising
        self.practice_button.grid(
            row=2, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W
        )
        self.close_button.grid(
            row=2, column=1, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W
        )

    def arm(self):
        print("voy a armar ", self.state)
        # do not allow arming if destination is not fixed
        if self.state == "connected":
            self.client.publish("droneCircus/autopilotService/armDrone")
            self.arm_button["bg"] == "orange"
            self.arm_button["text"] == "arming ..."
        elif self.state == "disconnected":
            messagebox.showwarning(
                "Error", "Antes de armar, debes conectar", parent=self.master
            )
        elif self.state == "flying":
            messagebox.showwarning("Error", "Ya estas volando", parent=self.master)

    def take_off(self):
        print("voy a despegar ", self.state)
        # do not allow taking off if not armed
        if self.state == "armed":
            self.client.publish("droneCircus/autopilotService/takeOff")
            self.take_off_button["text"] = "taking off ..."
            self.take_off_button["bg"] = "orange"

        elif self.state == "flying":
            messagebox.showwarning("Error", "Ya estas volando", parent=self.master)
        elif self.state == "connected" or self.state == "disconnected":
            messagebox.showwarning(
                "Error", "Antes de despegar, debes armar", parent=self.master
            )

    def close(self):

        if self.state == 'disconnected' or self.state== 'practising':

            self.client2.publish('droneCircus/imageService/stopVideoStream')

            # this will stop the video stream thread
            self.state = "closed"

            """
            #self.client.loop_stop()
            #self.client.disconnect()

            #cv2.destroyAllWindows()
            #cv2.waitKey(1)

            self.client.publish("droneCircus/autopilotService/disconnect")
            # self.cap.release()
            #self.client.loop_stop()

            #self.client.disconnect()
            time.sleep(5)
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False
            self.state = 'disconnected'
            """

            self.cap.release()
            print("cap release done")
            self.father_frame.destroy()
        else:
            messagebox.showwarning(
                "Error", "Antes de salir debes desconectar", parent=self.master
            )

    def practice(self):
        print("practice")
        if self.state == "disconnected":
            # start practising
            self.practice_button["bg"] = "#367E18"
            self.practice_button["text"] = "Estoy preparado. Quiero volar"
            self.state = "practising"

            parameters = {
                'mode': self.mode,
                'level': self.level,
                'selected_level': self.selected_level
            }
            self.client2.publish('droneCircus/imageService/parameters', json.dumps(parameters))

            self.show_video_window = tk.Toplevel(self.master)
            self.show_video_window.title("Show video")
            self.show_video_window.geometry("800x600")
            self.vidLabel = tk.Label(self.show_video_window, anchor=NW)
            self.vidLabel.pack(expand=YES, fill=BOTH)
            # show_video_frame = tk.Frame(self.show_video_window)
            # show_video_frame.pack()
            #
            # self.canvas4 = tk.Canvas(show_video_frame, width=800, height=600)
            # self.canvas4.grid(row=1, column=0, columnspan=3, sticky="nesw")

            # startvideo stream to practice


            x = threading.Thread(target=self.practising)
            x.start()

        elif self.state == "practising":
            print("final practice")
            # stop the video stream thread for practice
            self.state = "disconnected"
            self.client2.publish('droneCircus/imageService/stopVideoStream')
            self.practice_button.grid_forget()
            # show buttons for connect, arm and takeOff
            self.button_frame.grid(
                row=1,
                column=0,
                columnspan=2,
                padx=5,
                pady=5,
                sticky=tk.N + tk.S + tk.E + tk.W,
            )
            self.client2.disconnect()  # disconnect gracefully
            self.client2.loop_stop()  # stops network loop

    def easy(self):
        # show button to select scenario
        self.select_scenario_button.grid(
            row=1,
            column=0,
            columnspan=2,
            padx=5,
            pady=5,
            sticky=tk.N + tk.S + tk.E + tk.W,
        )

        # highlight codes for easy pattern
        self.difficult_button["bg"] = "#CC3636"
        self.easy_button["bg"] = "#367E18"
        self.bottom_frame.destroy()
        self.bottom_frame = tk.LabelFrame(self.master, text="EASY")
        self.level = "easy"
        if self.mode == "fingers":
            self.image = Image.open("../assets_needed/dedos_faciles.png")
        elif self.mode == "pose":
            self.image = Image.open("../assets_needed/poses_faciles.png")
        elif self.mode == "voice":
            self.image = Image.open("../assets_needed/voces_faciles.png")
        else:
            self.image = Image.open("../assets_needed/caras_faciles.png")

        self.image = self.image.resize((350, 500), Image.ANTIALIAS)
        self.bg = ImageTk.PhotoImage(self.image)
        canvas1 = tk.Canvas(self.bottom_frame, width=350, height=500)
        canvas1.pack(fill="both", expand=True)
        canvas1.create_image(0, 0, image=self.bg, anchor="nw")

        self.bottom_frame.grid(
            row=1, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W
        )

    def difficult(self):

        # show button to select scenario
        self.select_scenario_button.grid(
            row=1,
            column=0,
            columnspan=2,
            padx=5,
            pady=5,
            sticky=tk.N + tk.S + tk.E + tk.W,
        )

        # highlight codes for difficult pattern
        self.difficult_button["bg"] = "#367E18"
        self.easy_button["bg"] = "#CC3636"
        self.bottom_frame.destroy()
        self.bottom_frame = tk.LabelFrame(self.master, text="DIFFICULT")

        # we still do not have difficult patters. So we use again easy patters

        if self.mode == "fingers":
            self.image = Image.open("../assets_needed/dedos_faciles.png")
        elif self.mode == "pose":
            self.image = Image.open("../assets_needed/poses_dificiles.png")
        elif self.mode == "voice":
            self.image = Image.open("../assets_needed/voces_dificiles.png")
        else:
            self.image = Image.open("../assets_needed/caras_faciles.png")

        self.image = self.image.resize((350, 500), Image.ANTIALIAS)
        self.bg = ImageTk.PhotoImage(self.image)

        canvas1 = tk.Canvas(self.bottom_frame, width=350, height=500)
        canvas1.pack(fill="both", expand=True)

        canvas1.create_image(0, 0, image=self.bg, anchor="nw")

        self.bottom_frame.grid(
            row=1, column=0, padx=5, pady=5, sticky=tk.N + tk.S + tk.E + tk.W
        )
        self.level = "difficult"

    def __set_direction(self, code):
        if code == 1:
            return "Norte"
        elif code == 2:
            return "Sur"
        elif code == 3:
            return "Este"
        elif code == 4:
            return "Oeste"
        elif code == 5:
            return "Drop"
        elif code == 6:
            return "Retorna"
        elif code == 0:
            return "Stop"
        else:
            return ""

    def movePoint(self):
        print("muevo a ", self.direction)
        bearing = None
        if self.direction == "Norte":
            bearing = math.radians(0)
        elif self.direction == "Sur":
            bearing = math.radians(180)
        elif self.direction == "Este":
            bearing = math.radians(90)
        elif self.direction == "Oeste":
            bearing = math.radians(270)
        if bearing != None:
            R = 6378.1
            d = 0.001

            lat = math.radians(self.practicePoint[0])
            lon = math.radians(self.practicePoint[1])

            lat2 = math.degrees(math.asin(
                math.sin(lat) * math.cos(d / R)
                + math.cos(lat) * math.sin(d / R) * math.cos(bearing)
            ))

            lon2 = math.degrees(lon + math.atan2(
                math.sin(bearing) * math.sin(d / R) * math.cos(lat),
                math.cos(d / R) - math.sin(lat) * math.sin(lat2),
            ))
            if self.selected_level == 'Basico' \
                    and self.dronLabLimits.contains(Point(lat2,lon2)):
                self.practicePoint = [lat2,lon2]
                self.map.move_drone([lat2,lon2], 'red')

            if self.selected_level == "Basico" and self.dronLabLimits.contains(
                Point(lat2, lon2)
            ):
                self.practicePoint = [lat2, lon2]
                self.map.move_drone([lat2, lon2], 'red')

            elif self.selected_level == 'Medio' \
                    and self.dronLabLimits.contains(Point(lat2, lon2)) \
                    and not self.obstacle_1.contains(Point(lat2, lon2)) :
                self.practicePoint = [lat2, lon2]
                self.map.move_drone([lat2, lon2], 'red')

            elif self.dronLabLimits.contains(Point(lat2, lon2)) \
                    and not self.obstacle_2_1.contains(Point(lat2, lon2)) \
                    and not self.obstacle_2_2.contains(Point(lat2, lon2)) \
                    and not self.obstacle_2_3.contains(Point(lat2, lon2)):
                self.practicePoint = [lat2, lon2]
                self.map.move_drone([lat2, lon2], 'red')


    def practising(self):

        self.direction = None

        self.dronLabLimits = Polygon(
            [
                (41.2764151, 1.9882914),
                (41.2762170, 1.9883551),
                (41.2763733, 1.9890491),
                (41.2765582, 1.9889881),
            ]
        )

        self.obstacle_1 = Polygon(
            [
                (41.2764408, 1.9885938),
                (41.2764368, 1.9886494),
                (41.2763385, 1.9886407),
                (41.2763450, 1.9885878),
            ]
        )

        self.obstacle_2_1 = Polygon(
            [
                (41.2765219, 1.9888506),
                (41.2764065, 1.9888902),
                (41.2763924, 1.9888600),
                (41.2765669, 1.9887990),
            ]
        )
        self.obstacle_2_2 = Polygon(
            [
                (41.2764287, 1.9887453),
                (41.2763123, 1.9888077),
                (41.2763032, 1.9887460),
                (41.2764267, 1.9887111),
            ]
        )
        self.obstacle_2_3 = Polygon(
            [
                (41.2764569, 1.9885515),
                (41.2763461, 1.9886903),
                (41.2763274, 1.9886535),
                (41.2764473, 1.9885274),
            ]
        )

        self.practicePoint = [41.2765003, 1.9889760]
        self.show_map(self.practicePoint)

        self.sched = BackgroundScheduler()
        self.sched.add_job(self.movePoint, "interval", seconds=1)
        self.sched.start()
        #
        # # when the user changes the pattern (new face, new pose or new fingers) the system
        # # waits some time (ignore 8 video frames) for the user to stabilize the new pattern
        # # we need the following variables to control this
        # prevCode = -1
        # cont = 0
        # if self.mode == "voice":
        #     self.map.putText("Di algo ...")
        #
        # while self.state == "practising":
        #
        #     # use the selected detector to get the code of the pattern and the image with landmarks
        #
        #     if self.mode != "voice":
        #         success, image = self.cap.read()
        #         if not success:
        #             print("Ignoring empty camera frame.")
        #             # If loading a video, use 'break' instead of 'continue'.
        #             continue
        #         img = cv2.resize(image, (800, 600))
        #         img = cv2.flip(img, 1)
        #         code, img = self.detector.detect(img, self.level)
        #         #print ('estoy enviando imagenes ', code)
        #         # if user changed the pattern we will ignore the next 8 video frames
        #         if code != prevCode:
        #             cont = 4
        #             prevCode = code
        #         else:
        #             cont = cont - 1
        #             if cont < 0:
        #                 # the first 8 video frames of the new pattern (to be ignored) are done
        #                 # we can start showing new results
        #                 self.direction = self.__set_direction(code)
        #                 cv2.putText(
        #                     img,
        #                     self.direction,
        #                     (50, 450),
        #                     cv2.FONT_HERSHEY_SIMPLEX,
        #                     3,
        #                     (0, 0, 255),
        #                     10,
        #                 )
        #
        #         cv2.imshow("video", img)
        #         cv2.waitKey(1)
        #     else:
        #         code, voice = self.detector.detect(self.level)
        #         if code != -1:
        #             self.direction = self.__set_direction(code)
        #         self.map.putText(voice)
        #
        # sched.shutdown()

        # Vull enviar el video
        # contador1 = 0
        self.client2.subscribe('imageService/droneCircus/code')
        self.client2.subscribe('imageService/droneCircus/videoFrame')

        while self.state == "practising":
            success, frame = self.cap.read()
            _, buffer = cv2.imencode('.jpg', frame)
            # Converting into encoded bytes
            if not success:
                print("Ignoring empty camera frame.")
                # If loading a video, use 'break' instead of 'continue'.
                continue
            jpg_as_text = base64.b64encode(buffer)
            self.client2.publish('droneCircus/imageService/videoFrame', jpg_as_text)
            # contador1 = contador1 + 1
            # print("contador1: ",contador1)
            # cv2.imshow("video", frame)
            # cv2.waitKey(1)
            time.sleep(0.25)  # baixar-ho si volem que s'envii més rapid

        self.show_video_window.destroy()

        self.sched.shutdown()
        cv2.waitKey(1)
        cv2.destroyAllWindows()
        cv2.waitKey(1)

    def flying(self):
        # see comments for practising function
        # prev_code = -1
        # cont = 0
        # we need to know if the dron is returning to lunch to show an apropriate message
        self.returning = False
        self.direction = ""

        # ens conncectem al imageService
        broker_address = "broker.hivemq.com"
        broker_port = 8000
        self.client3 = mqtt.Client(transport="websockets")
        self.client3.on_message = self.on_message2  # Callback function executed when a message is received
        self.client3.connect(broker_address, broker_port)
        self.client3.publish('droneCircus/imageService/Connect')
        self.client3.loop_start()

        parameters = {
            'mode': self.mode,
            'level': self.level,
            'selected_level': self.selected_level
        }
        self.client3.publish('droneCircus/imageService/parameters', json.dumps(parameters))

        self.client3.subscribe('imageService/droneCircus/code')
        self.client3.subscribe('imageService/droneCircus/videoFrame')

        self.show_video_window = tk.Toplevel(self.master)
        self.show_video_window.title("Show video")
        self.show_video_window.geometry("800x600")
        self.vidLabel = tk.Label(self.show_video_window, anchor=NW)
        self.vidLabel.pack(expand=YES, fill=BOTH)

        while self.state == "flying":

            # self.client2.subscribe('imageService/droneCircus/direction')
            success, frame = self.cap.read()
            _, buffer = cv2.imencode('.jpg', frame)
            # Converting into encoded bytes
            if not success:
                print("Ignoring empty camera frame.")
                # If loading a video, use 'break' instead of 'continue'.
                continue
            jpg_as_text = base64.b64encode(buffer)
            self.client3.publish('droneCircus/imageService/videoFrame', jpg_as_text)
            # cv2.imshow("video", frame)
            # cv2.waitKey(1)
            time.sleep(0.25)  # baixar-ho si volem que s'envii més rapid

        self.show_video_window.destroy()
        cv2.waitKey(1)
        cv2.destroyAllWindows()
        cv2.waitKey(1)


        # while self.state == "flying":
        #     success, image = self.cap.read()
        #
        #     if not success:
        #         print("Ignoring empty camera frame.")
        #         # If loading a video, use 'break' instead of 'continue'.
        #         continue
        #     code, img = self.detector.detect(image, self.level)
        #     img = cv2.resize(img, (800, 600))
        #     img = cv2.flip(img, 1)
        #     if not self.returning:
        #         if code != prev_code:
        #             cont = 8
        #             prev_code = code
        #         else:
        #             cont = cont - 1
        #             if cont < 0:
        #                 self.direction = self.__set_direction(code)
        #                 go_topic = "droneCircus/autopilotService/go"
        #                 if code == 1:
        #                     # north
        #                     self.client.publish(go_topic, "North")
        #                 elif code == 2:  # south
        #                     self.client.publish(go_topic, "South")
        #                 elif code == 5:
        #                     self.client.publish("droneCircus/autopilotService/drop")
        #                     time.sleep(2)
        #                     self.client.publish("droneCircus/autopilotService/reset")
        #                 elif code == 3:  # east
        #                     self.client.publish(go_topic, "East")
        #                 elif code == 4:  # west
        #                     self.client.publish(go_topic, "West")
        #                 elif code == 6:
        #                     self.return_home()
        #                 elif code == 0:
        #                     self.client.publish(go_topic, "Stop")
        #
        #     cv2.putText(
        #         img,
        #         self.direction,
        #         (50, 450),
        #         cv2.FONT_HERSHEY_SIMPLEX,
        #         3,
        #         (0, 0, 255),
        #         10,
        #     )
        #     cv2.imshow("video", img)
        #     cv2.waitKey(1)
        #
        # cv2.destroyWindow("video")
        # cv2.waitKey(1)


    def return_home(self):
        if self.state == "flying":
            self.returning = True
            self.direction = "Volviendo a casa"
            self.return_home_button["text"] = "Volviendo a casa"
            self.return_home_button["bg"] = "orange"
            self.client.publish("droneCircus/autopilotService/returnToLaunch")

        else:
            messagebox.showwarning("Error", "No estas volando", parent=self.master)

