# client.py - Modern Radio Client with Enhanced UI
import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, font
import socket
import threading
import pyaudio
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import collections
import os
import queue
import ssl
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64
import struct
import math

CERT_FILE = 'PyWavesClientCert.pem'
SAVE_FILE = "user_data.txt"
LOGINPORT = 12346
BUFFER_SIZE = 1024


class ModernLoginDialog(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PyWaves Radio • Login")
        self.geometry("400x1000")
        self.resizable(False, False)

        # Variables
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.verify_password = tk.StringVar()
        self.server_ip = tk.StringVar()
        self.token = None
        self.index = None
        self.key = None
        self.is_registering = False

        # Colors
        self.colors = {
            'bg': '#0a0a0a',
            'surface': '#1a1a1a',
            'accent': '#ff3366',
            'text': '#ffffff',
            'text_dim': '#808080',
            'input_bg': '#252525',
            'button_hover': '#ff4477'
        }

        self.configure(bg=self.colors['bg'])
        self.load_saved_data()
        self.create_modern_ui()

        # SSL context
        self.context = ssl.create_default_context()
        self.context.check_hostname = False
        self.context.verify_mode = ssl.CERT_REQUIRED
        self.context.load_verify_locations(CERT_FILE)

    def create_modern_ui(self):
        # Main container
        main_frame = tk.Frame(self, bg=self.colors['bg'])
        main_frame.pack(fill="both", expand=True, padx=40, pady=40)

        # Logo/Title
        title_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        title_frame.pack(pady=(0, 30))

        logo_label = tk.Label(title_frame, text="📻", font=('Arial', 48),
                              bg=self.colors['bg'], fg=self.colors['accent'])
        logo_label.pack()

        title_label = tk.Label(title_frame, text="PyWaves Radio",
                               font=('SF Pro Display', 24, 'bold'),
                               bg=self.colors['bg'], fg=self.colors['text'])
        title_label.pack()

        subtitle_label = tk.Label(title_frame, text="Stream Your Favorite Tunes",
                                  font=('SF Pro Text', 12),
                                  bg=self.colors['bg'], fg=self.colors['text_dim'])
        subtitle_label.pack()

        # Form container
        form_frame = tk.Frame(main_frame, bg=self.colors['surface'])
        form_frame.pack(fill="both", expand=True)

        # Inner padding
        inner_frame = tk.Frame(form_frame, bg=self.colors['surface'])
        inner_frame.pack(fill="both", expand=True, padx=30, pady=30)

        # Username field
        self.create_input_field(inner_frame, "Username", self.username)

        # Password field
        self.create_input_field(inner_frame, "Password", self.password, show="•")

        # Verify password field (hidden by default)
        self.verify_frame = tk.Frame(inner_frame, bg=self.colors['surface'])
        self.verify_label = tk.Label(self.verify_frame, text="Verify Password",
                                     font=('SF Pro Text', 11),
                                     bg=self.colors['surface'], fg=self.colors['text_dim'])
        self.verify_entry = tk.Entry(self.verify_frame, textvariable=self.verify_password,
                                     font=('SF Pro Text', 12), show="•",
                                     bg=self.colors['input_bg'], fg=self.colors['text'],
                                     insertbackground=self.colors['accent'],
                                     relief='flat', bd=10)

        # Server IP field
        self.create_input_field(inner_frame, "Server IP", self.server_ip)

        # Action button
        self.action_button = tk.Button(inner_frame, text="LOGIN",
                                       font=('SF Pro Text', 12, 'bold'),
                                       bg=self.colors['accent'], fg=self.colors['text'],
                                       activebackground=self.colors['button_hover'],
                                       activeforeground=self.colors['text'],
                                       relief='flat', cursor='hand2',
                                       command=self.on_login)
        self.action_button.pack(fill="x", pady=(20, 10), ipady=12)

        # Toggle link
        self.toggle_frame = tk.Frame(inner_frame, bg=self.colors['surface'])
        self.toggle_frame.pack()

        toggle_text = tk.Label(self.toggle_frame, text="Don't have an account?",
                               font=('SF Pro Text', 11),
                               bg=self.colors['surface'], fg=self.colors['text_dim'])
        toggle_text.pack(side="left", padx=(0, 5))

        self.toggle_link = tk.Label(self.toggle_frame, text="Register",
                                    font=('SF Pro Text', 11, 'underline'),
                                    bg=self.colors['surface'], fg=self.colors['accent'],
                                    cursor="hand2")
        self.toggle_link.pack(side="left")
        self.toggle_link.bind("<Button-1>", lambda e: self.toggle_register())

        # Hover effects
        self.action_button.bind("<Enter>", lambda e: self.action_button.config(bg=self.colors['button_hover']))
        self.action_button.bind("<Leave>", lambda e: self.action_button.config(bg=self.colors['accent']))

    def create_input_field(self, parent, label_text, variable, show=None):
        # Container
        field_frame = tk.Frame(parent, bg=self.colors['surface'])
        field_frame.pack(fill="x", pady=(0, 15))

        # Label
        label = tk.Label(field_frame, text=label_text,
                         font=('SF Pro Text', 11),
                         bg=self.colors['surface'], fg=self.colors['text_dim'])
        label.pack(anchor="w", pady=(0, 5))

        # Entry
        entry = tk.Entry(field_frame, textvariable=variable,
                         font=('SF Pro Text', 12),
                         bg=self.colors['input_bg'], fg=self.colors['text'],
                         insertbackground=self.colors['accent'],
                         relief='flat', bd=10)
        if show:
            entry.config(show=show)
        entry.pack(fill="x", ipady=8)

        return entry

    def toggle_register(self):
        self.is_registering = not self.is_registering
        if self.is_registering:
            self.title("PyWaves Radio • Register")
            self.action_button.config(text="REGISTER")

            # Show verify password field
            self.verify_frame.pack(fill="x", pady=(0, 15), after=self.verify_frame.master.winfo_children()[1])
            self.verify_label.pack(anchor="w", pady=(0, 5))
            self.verify_entry.pack(fill="x", ipady=8)

            # Update toggle text
            for widget in self.toggle_frame.winfo_children():
                widget.destroy()

            toggle_text = tk.Label(self.toggle_frame, text="Already have an account?",
                                   font=('SF Pro Text', 11),
                                   bg=self.colors['surface'], fg=self.colors['text_dim'])
            toggle_text.pack(side="left", padx=(0, 5))

            self.toggle_link = tk.Label(self.toggle_frame, text="Login",
                                        font=('SF Pro Text', 11, 'underline'),
                                        bg=self.colors['surface'], fg=self.colors['accent'],
                                        cursor="hand2")
            self.toggle_link.pack(side="left")
            self.toggle_link.bind("<Button-1>", lambda e: self.toggle_register())
        else:
            self.title("PyWaves Radio • Login")
            self.action_button.config(text="LOGIN")

            # Hide verify password field
            self.verify_frame.pack_forget()

            # Update toggle text
            for widget in self.toggle_frame.winfo_children():
                widget.destroy()

            toggle_text = tk.Label(self.toggle_frame, text="Don't have an account?",
                                   font=('SF Pro Text', 11),
                                   bg=self.colors['surface'], fg=self.colors['text_dim'])
            toggle_text.pack(side="left", padx=(0, 5))

            self.toggle_link = tk.Label(self.toggle_frame, text="Register",
                                        font=('SF Pro Text', 11, 'underline'),
                                        bg=self.colors['surface'], fg=self.colors['accent'],
                                        cursor="hand2")
            self.toggle_link.pack(side="left")
            self.toggle_link.bind("<Button-1>", lambda e: self.toggle_register())

    def on_login(self):
        user = self.username.get().strip()
        pw = self.password.get().strip()
        ip = self.server_ip.get().strip()

        if not user or not pw or not ip:
            messagebox.showwarning("Missing Info", "Please fill in all fields.")
            return

        if self.is_registering:
            verify_pw = self.verify_password.get().strip()
            if pw != verify_pw:
                messagebox.showerror("Mismatch", "Passwords do not match.")
                return
            action = "register"
        else:
            action = "login"

        message = {
            "username": user,
            "password": pw,
            "type": action
        }

        try:
            response = self.send_tcp_message(ip, LOGINPORT, message)

            if isinstance(response, dict) and response.get("status") == "success":
                self.token = response.get("token")
                self.index = response.get("index")
                self.key = response.get("key")
                self.save_user_data(user, pw, ip, self.token)
                self.destroy()
                open_main_app(user, pw, ip, self.token, self.index, self.key)
            elif response == "already exists":
                messagebox.showerror("Register Failed", "User already exists.")
            else:
                messagebox.showerror("Authentication Failed", "Invalid username or password.")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Could not connect to server at {ip}:{LOGINPORT}")

    def send_tcp_message(self, ip, port, data_dict):
        with socket.create_connection((ip, port), timeout=5) as sock:
            with self.context.wrap_socket(sock, server_hostname=ip) as ssock:
                ssock.sendall(json.dumps(data_dict).encode('utf-8'))
                response = ssock.recv(BUFFER_SIZE).decode('utf-8').strip()

                try:
                    return json.loads(response)
                except json.JSONDecodeError:
                    return response

    def save_user_data(self, username, password, ip, token):
        with open(SAVE_FILE, "w") as f:
            f.write(f"{username}\n{password}\n{ip}\n{token or ''}")

    def load_saved_data(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r") as f:
                    lines = f.read().splitlines()
                    if len(lines) >= 3:
                        self.username.set(lines[0])
                        self.password.set(lines[1])
                        self.server_ip.set(lines[2])
                        if len(lines) >= 4:
                            self.token = lines[3]
            except Exception as e:
                print("Failed to load saved data:", e)


class ModernRadioClient:
    def __init__(self, root, server_ip, token, index, key, username, password):
        self.token = token
        self.index = index
        self.key = key
        self.username = username
        self.password = password
        self.server_ip = server_ip
        self.conn_status = None
        self.root = root
        self.root.title("PyWaves Radio")
        self.root.geometry("1000x1000")
        self.root.minsize(800, 600)

        # Modern color scheme
        self.colors = {
            'bg': '#0a0a0a',
            'surface': '#1a1a1a',
            'surface_light': '#252525',
            'accent': '#ff3366',
            'accent_glow': '#ff6b96',
            'success': '#00d67a',
            'text': '#ffffff',
            'text_secondary': '#b0b0b0',
            'text_dim': '#606060',
            'visualizer_primary': '#ff3366',
            'visualizer_secondary': '#8338ec',
            'visualizer_glow': '#ff006e'
        }

        self.root.configure(bg=self.colors['bg'])

        # Server settings
        self.host = server_ip
        self.port = 12345
        self.client_socket = None
        self.connected = False
        self.settings_file = "client_settings.json"

        # Audio settings
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.chunk_size = 256
        self.format = pyaudio.paInt16
        self.channels = 2
        self.rate = 44100
        self.frames = 0

        # Audio buffer management
        self.audio_queue = queue.Queue(maxsize=100)
        self.max_buffer_size = 100

        # Thread safety
        self.playback_thread = None
        self.playback_active = False
        self.cleanup_in_progress = False
        self.stream_lock = threading.Lock()
        self.shutdown_event = threading.Event()

        # Time tracking
        self.current_track_duration = 0
        self.current_track_elapsed = 0
        self.time_update_thread = None
        self.time_tracking_active = False
        self.track_start_time = None

        # Visualizer settings
        self.visualizer_data = collections.deque(maxlen=50)
        self.visualizer_lock = threading.Lock()
        self.visualizer_enabled = True
        self.spectrum_bars = 32

        self.setup_modern_ui()
        self.setup_advanced_visualizer()
        self.load_settings()

        # Auto-connect on startup
        self.root.after(100, self.connect)

    def setup_modern_ui(self):
        """Create the modern UI layout"""
        # Main container
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill="both", expand=True)

        # Header section
        self.create_header(main_container)

        # Content area
        content_frame = tk.Frame(main_container, bg=self.colors['bg'])
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Left panel - Now playing and controls
        left_panel = tk.Frame(content_frame, bg=self.colors['bg'])
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.create_now_playing_card(left_panel)
        self.create_connection_info(left_panel)

        # Right panel - Visualizer
        right_panel = tk.Frame(content_frame, bg=self.colors['bg'])
        right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))

        self.create_visualizer_card(right_panel)

    def create_header(self, parent):
        """Create the modern header"""
        header_frame = tk.Frame(parent, bg=self.colors['bg'], height=80)
        header_frame.pack(fill="x", padx=20, pady=(20, 20))
        header_frame.pack_propagate(False)

        # Logo and title
        title_container = tk.Frame(header_frame, bg=self.colors['bg'])
        title_container.pack(side="left", fill="both", expand=True)

        logo_frame = tk.Frame(title_container, bg=self.colors['bg'])
        logo_frame.pack(anchor="w", pady=(15, 5))

        logo_label = tk.Label(logo_frame, text="📻", font=('Arial', 24),
                              bg=self.colors['bg'], fg=self.colors['accent'])
        logo_label.pack(side="left", padx=(0, 10))

        title_label = tk.Label(logo_frame, text="PYWAVES RADIO",
                               font=('SF Pro Display', 24, 'bold'),
                               bg=self.colors['bg'], fg=self.colors['text'])
        title_label.pack(side="left")

        subtitle_label = tk.Label(title_container, text="High Quality Audio Streaming",
                                  font=('SF Pro Text', 12),
                                  bg=self.colors['bg'], fg=self.colors['text_dim'])
        subtitle_label.pack(anchor="w")

        # Connection status indicator
        status_container = tk.Frame(header_frame, bg=self.colors['bg'])
        status_container.pack(side="right", anchor="e", pady=25)

        self.status_indicator = tk.Canvas(status_container, width=150, height=40,
                                          bg=self.colors['bg'], highlightthickness=0)
        self.status_indicator.pack()

        self.status_bg = self.status_indicator.create_rectangle(0, 0, 150, 40,
                                                                fill=self.colors['surface'],
                                                                outline="")
        self.status_dot = self.status_indicator.create_oval(15, 15, 25, 25,
                                                            fill=self.colors['text_dim'],
                                                            outline="")
        self.status_text = self.status_indicator.create_text(75, 20,
                                                             text="OFFLINE",
                                                             font=('SF Pro Text', 12, 'bold'),
                                                             fill=self.colors['text_dim'])

    def create_now_playing_card(self, parent):
        """Create the now playing card"""
        card_frame = tk.Frame(parent, bg=self.colors['surface'])
        card_frame.pack(fill="both", expand=True, pady=(0, 15))

        inner_frame = tk.Frame(card_frame, bg=self.colors['surface'])
        inner_frame.pack(fill="both", expand=True, padx=25, pady=25)

        # Section header
        header_label = tk.Label(inner_frame, text="Now Playing",
                                font=('SF Pro Display', 18, 'bold'),
                                bg=self.colors['surface'], fg=self.colors['accent'])
        header_label.pack(anchor="w", pady=(0, 20))

        # Album art placeholder
        art_frame = tk.Frame(inner_frame, bg=self.colors['surface_light'],
                             width=250, height=250)
        art_frame.pack(pady=(0, 20))
        art_frame.pack_propagate(False)

        # Animated gradient background for album art
        self.album_canvas = tk.Canvas(art_frame, width=250, height=250,
                                      bg=self.colors['surface_light'],
                                      highlightthickness=0)
        self.album_canvas.pack()

        # Create gradient effect
        for i in range(250):
            color = self.interpolate_color(self.colors['accent'],
                                           self.colors['visualizer_secondary'],
                                           i / 250)
            self.album_canvas.create_line(0, i, 250, i, fill=color, width=2)

        # Radio icon overlay
        self.album_canvas.create_text(125, 125, text="🎵",
                                      font=('Arial', 64),
                                      fill=self.colors['text'])

        # Track info
        self.track_label = tk.Label(inner_frame, text="No track playing",
                                    font=('SF Pro Display', 16, 'bold'),
                                    bg=self.colors['surface'], fg=self.colors['text'])
        self.track_label.pack(pady=(0, 10))

        self.artist_label = tk.Label(inner_frame, text="Connect to start streaming",
                                     font=('SF Pro Text', 12),
                                     bg=self.colors['surface'],
                                     fg=self.colors['text_secondary'])
        self.artist_label.pack()

        # Progress section
        progress_frame = tk.Frame(inner_frame, bg=self.colors['surface'])
        progress_frame.pack(fill="x", pady=(20, 0))

        # Time labels
        time_container = tk.Frame(progress_frame, bg=self.colors['surface'])
        time_container.pack(fill="x", pady=(0, 10))

        self.time_elapsed = tk.Label(time_container, text="0:00",
                                     font=('SF Mono', 11),
                                     bg=self.colors['surface'],
                                     fg=self.colors['text_secondary'])
        self.time_elapsed.pack(side="left")

        self.time_total = tk.Label(time_container, text="0:00",
                                   font=('SF Mono', 11),
                                   bg=self.colors['surface'],
                                   fg=self.colors['text_secondary'])
        self.time_total.pack(side="right")

        # Custom progress bar
        self.progress_canvas = tk.Canvas(progress_frame, height=6,
                                         bg=self.colors['surface_light'],
                                         highlightthickness=0)
        self.progress_canvas.pack(fill="x")

        self.progress_bg = self.progress_canvas.create_rectangle(0, 0, 0, 0,
                                                                 fill=self.colors['surface_light'],
                                                                 outline="")
        self.progress_fill = self.progress_canvas.create_rectangle(0, 0, 0, 6,
                                                                   fill=self.colors['accent'],
                                                                   outline="")

        # Volume control
        volume_frame = tk.Frame(inner_frame, bg=self.colors['surface'])
        volume_frame.pack(fill="x", pady=(30, 0))

        volume_header = tk.Frame(volume_frame, bg=self.colors['surface'])
        volume_header.pack(fill="x", pady=(0, 10))

        vol_icon = tk.Label(volume_header, text="🔊",
                            font=('Arial', 16),
                            bg=self.colors['surface'])
        vol_icon.pack(side="left", padx=(0, 10))

        vol_label = tk.Label(volume_header, text="Volume",
                             font=('SF Pro Text', 12, 'bold'),
                             bg=self.colors['surface'],
                             fg=self.colors['text_secondary'])
        vol_label.pack(side="left")

        self.volume_percent = tk.Label(volume_header, text="70%",
                                       font=('SF Mono', 12),
                                       bg=self.colors['surface'],
                                       fg=self.colors['accent'])
        self.volume_percent.pack(side="right")

        # Custom volume slider
        self.volume_canvas = tk.Canvas(volume_frame, height=40,
                                       bg=self.colors['surface'],
                                       highlightthickness=0)
        self.volume_canvas.pack(fill="x")

        # Create custom slider
        self.create_volume_slider()

    def create_volume_slider(self):
        """Create a custom volume slider"""
        self.volume_value = 70

        # Track
        track_y = 20
        self.volume_track = self.volume_canvas.create_rectangle(10, track_y - 2, 10, track_y + 2,
                                                                fill=self.colors['surface_light'],
                                                                outline="")
        self.volume_fill = self.volume_canvas.create_rectangle(10, track_y - 2, 10, track_y + 2,
                                                               fill=self.colors['accent'],
                                                               outline="")

        # Slider handle
        self.volume_handle = self.volume_canvas.create_oval(0, track_y - 8, 16, track_y + 8,
                                                            fill=self.colors['accent'],
                                                            outline=self.colors['accent_glow'],
                                                            width=2)

        # Bind events
        self.volume_canvas.bind('<Button-1>', self.on_volume_click)
        self.volume_canvas.bind('<B1-Motion>', self.on_volume_drag)
        self.volume_canvas.bind('<Configure>', self.on_volume_resize)

    def on_volume_resize(self, event):
        """Handle volume slider resize"""
        width = event.width
        track_y = 20

        # Update track width
        self.volume_canvas.coords(self.volume_track, 10, track_y - 2, width - 10, track_y + 2)

        # Update fill and handle position
        self.update_volume_display()

    def on_volume_click(self, event):
        """Handle volume slider click"""
        self.update_volume_from_position(event.x)

    def on_volume_drag(self, event):
        """Handle volume slider drag"""
        self.update_volume_from_position(event.x)

    def update_volume_from_position(self, x):
        """Update volume based on mouse position"""
        width = self.volume_canvas.winfo_width()
        if width > 20:
            # Calculate volume (0-100)
            volume = max(0, min(100, (x - 10) / (width - 20) * 100))
            self.volume_value = volume
            self.update_volume_display()

    def update_volume_display(self):
        """Update volume slider display"""
        width = self.volume_canvas.winfo_width()
        if width > 20:
            track_y = 20

            # Update fill
            fill_width = 10 + (width - 20) * (self.volume_value / 100)
            self.volume_canvas.coords(self.volume_fill, 10, track_y - 2, fill_width, track_y + 2)

            # Update handle
            handle_x = fill_width
            self.volume_canvas.coords(self.volume_handle,
                                      handle_x - 8, track_y - 8,
                                      handle_x + 8, track_y + 8)

            # Update percentage
            self.volume_percent.config(text=f"{int(self.volume_value)}%")

    def create_connection_info(self, parent):
        """Create connection info card"""
        card_frame = tk.Frame(parent, bg=self.colors['surface'])
        card_frame.pack(fill="x")

        inner_frame = tk.Frame(card_frame, bg=self.colors['surface'])
        inner_frame.pack(fill="x", padx=25, pady=20)

        # Header
        header_label = tk.Label(inner_frame, text="Connection",
                                font=('SF Pro Display', 14, 'bold'),
                                bg=self.colors['surface'], fg=self.colors['text_secondary'])
        header_label.pack(anchor="w", pady=(0, 15))

        # Server info
        self.server_info_label = tk.Label(inner_frame,
                                          text=f"Server: {self.host}:{self.port}",
                                          font=('SF Mono', 11),
                                          bg=self.colors['surface'],
                                          fg=self.colors['text_dim'])
        self.server_info_label.pack(anchor="w", pady=(0, 5))

        # User info
        self.user_info_label = tk.Label(inner_frame,
                                        text=f"User: {self.username}",
                                        font=('SF Mono', 11),
                                        bg=self.colors['surface'],
                                        fg=self.colors['text_dim'])
        self.user_info_label.pack(anchor="w")

    def create_visualizer_card(self, parent):
        """Create the visualizer card"""
        card_frame = tk.Frame(parent, bg=self.colors['surface'])
        card_frame.pack(fill="both", expand=True)

        inner_frame = tk.Frame(card_frame, bg=self.colors['surface'])
        inner_frame.pack(fill="both", expand=True, padx=25, pady=25)

        # Header with toggle
        header_frame = tk.Frame(inner_frame, bg=self.colors['surface'])
        header_frame.pack(fill="x", pady=(0, 20))

        header_label = tk.Label(header_frame, text="Audio Visualizer",
                                font=('SF Pro Display', 18, 'bold'),
                                bg=self.colors['surface'], fg=self.colors['accent'])
        header_label.pack(side="left")

        # Custom toggle switch
        self.create_toggle_switch(header_frame)

        # Visualizer container
        self.viz_container = tk.Frame(inner_frame, bg=self.colors['surface_light'])
        self.viz_container.pack(fill="both", expand=True)

    def create_toggle_switch(self, parent):
        """Create a custom toggle switch"""
        # Add rounded rectangle method
        self.add_rounded_rectangle_method()

        self.visualizer_enabled = True

        switch_frame = tk.Frame(parent, bg=self.colors['surface'])
        switch_frame.pack(side="right")

        self.switch_canvas = tk.Canvas(switch_frame, width=50, height=26,
                                       bg=self.colors['surface'], highlightthickness=0)
        self.switch_canvas.pack()

        # Create switch background
        self.switch_bg = self.switch_canvas.create_rounded_rectangle(0, 0, 50, 26, 13,
                                                                     fill=self.colors['accent'],
                                                                     outline="")
        # Create switch handle
        self.switch_handle = self.switch_canvas.create_oval(24, 2, 48, 24,
                                                            fill=self.colors['text'],
                                                            outline="")

        # Bind click event
        self.switch_canvas.bind("<Button-1>", self.toggle_visualizer)



    def add_rounded_rectangle_method(self):
        """Add method to create rounded rectangles on canvas"""

        def create_rounded_rectangle(canvas, x1, y1, x2, y2, radius, **kwargs):
            points = []
            for x, y in [(x1, y1 + radius), (x1, y1), (x1 + radius, y1),
                         (x2 - radius, y1), (x2, y1), (x2, y1 + radius),
                         (x2, y2 - radius), (x2, y2), (x2 - radius, y2),
                         (x1 + radius, y2), (x1, y2), (x1, y2 - radius)]:
                points.extend([x, y])
            return canvas.create_polygon(points, smooth=True, **kwargs)

        tk.Canvas.create_rounded_rectangle = create_rounded_rectangle

    def toggle_visualizer(self, event=None):
        """Toggle visualizer on/off with animation"""
        self.visualizer_enabled = not self.visualizer_enabled

        # Animate switch
        if self.visualizer_enabled:
            # Move handle to right
            self.switch_canvas.coords(self.switch_handle, 24, 2, 48, 24)
            self.switch_canvas.itemconfig(self.switch_bg, fill=self.colors['accent'])
        else:
            # Move handle to left
            self.switch_canvas.coords(self.switch_handle, 2, 2, 24, 24)
            self.switch_canvas.itemconfig(self.switch_bg, fill=self.colors['surface_light'])

            # Clear visualizer
            if hasattr(self, 'spectrum_bars_list'):
                for bar in self.spectrum_bars_list:
                    self.viz_canvas.coords(bar, 0, 0, 0, 0)

    def setup_advanced_visualizer(self):
        """Setup advanced spectrum visualizer"""
        # Create custom canvas for visualizer
        self.viz_canvas = tk.Canvas(self.viz_container,
                                    bg=self.colors['surface_light'],
                                    highlightthickness=0)
        self.viz_canvas.pack(fill="both", expand=True)

        # Initialize spectrum bars
        self.spectrum_bars_list = []
        self.spectrum_heights = [0] * self.spectrum_bars
        self.spectrum_smoothing = 0.7  # Smoothing factor

        # Start animation
        self.animate_visualizer()

        # Bind resize event
        self.viz_canvas.bind('<Configure>', self.on_viz_resize)

    def on_viz_resize(self, event):
        """Handle visualizer resize"""
        self.setup_spectrum_bars()

    def setup_spectrum_bars(self):
        """Setup spectrum analyzer bars"""
        self.viz_canvas.delete("all")
        self.spectrum_bars_list = []

        width = self.viz_canvas.winfo_width()
        height = self.viz_canvas.winfo_height()

        if width > 1 and height > 1:
            bar_width = width / self.spectrum_bars
            padding = bar_width * 0.2
            actual_bar_width = bar_width - padding

            for i in range(self.spectrum_bars):
                x = i * bar_width + padding / 2

                # Create gradient color for each bar
                color = self.interpolate_color(
                    self.colors['visualizer_primary'],
                    self.colors['visualizer_secondary'],
                    i / self.spectrum_bars
                )

                # Create bar with glow effect
                glow = self.viz_canvas.create_rectangle(
                    x - 2, height, x + actual_bar_width + 2, height,
                    fill=color, outline="", stipple="gray50"
                )

                bar = self.viz_canvas.create_rectangle(
                    x, height, x + actual_bar_width, height,
                    fill=color, outline=""
                )

                self.spectrum_bars_list.append(bar)

    def animate_visualizer(self):
        """Animate the spectrum visualizer"""
        if not self.visualizer_enabled or not self.connected:
            self.root.after(50, self.animate_visualizer)
            return

        try:
            # Get latest audio data
            with self.visualizer_lock:
                if self.visualizer_data:
                    audio_data = self.visualizer_data[-1]
                    self.update_spectrum_visualizer(audio_data)
        except Exception as e:
            print(f"Visualizer error: {e}")

        self.root.after(50, self.animate_visualizer)

    def update_spectrum_visualizer(self, audio_data):
        """Update spectrum analyzer display"""
        if not hasattr(self, 'spectrum_bars_list') or not self.spectrum_bars_list:
            return

        height = self.viz_canvas.winfo_height()
        if height <= 1:
            return

        try:
            # Perform FFT on audio data
            fft_data = np.fft.fft(audio_data)
            fft_magnitude = np.abs(fft_data[:len(fft_data) // 2])

            # Group frequencies into bands
            bands = np.array_split(fft_magnitude[:self.spectrum_bars * 4], self.spectrum_bars)

            for i, band in enumerate(bands):
                if i < len(self.spectrum_bars_list):
                    # Calculate band magnitude
                    magnitude = np.mean(band)

                    # Normalize and apply logarithmic scaling
                    if magnitude > 0:
                        db_value = 20 * np.log10(magnitude + 1)
                        normalized_height = min(1.0, db_value / 80)
                    else:
                        normalized_height = 0

                    # Apply smoothing
                    self.spectrum_heights[i] = (
                            self.spectrum_heights[i] * self.spectrum_smoothing +
                            normalized_height * (1 - self.spectrum_smoothing)
                    )

                    # Update bar height
                    bar_height = self.spectrum_heights[i] * height * 0.9
                    bar = self.spectrum_bars_list[i]

                    coords = self.viz_canvas.coords(bar)
                    if len(coords) >= 4:
                        self.viz_canvas.coords(bar,
                                               coords[0], height - bar_height,
                                               coords[2], height)

                        # Add pulsing effect for active bars
                        if bar_height > height * 0.5:
                            color = self.interpolate_color(
                                self.colors['visualizer_primary'],
                                self.colors['visualizer_glow'],
                                min(1.0, bar_height / height)
                            )
                            self.viz_canvas.itemconfig(bar, fill=color)

        except Exception as e:
            print(f"Spectrum update error: {e}")

    def interpolate_color(self, color1, color2, factor):
        """Interpolate between two colors"""
        r1 = int(color1[1:3], 16)
        g1 = int(color1[3:5], 16)
        b1 = int(color1[5:7], 16)

        r2 = int(color2[1:3], 16)
        g2 = int(color2[3:5], 16)
        b2 = int(color2[5:7], 16)

        r = int(r1 + (r2 - r1) * factor)
        g = int(g1 + (g2 - g1) * factor)
        b = int(b1 + (b2 - b1) * factor)

        return f"#{r:02x}{g:02x}{b:02x}"

    def update_connection_status(self, connected):
        """Update connection status indicator"""
        if connected:
            self.status_indicator.itemconfig(self.status_dot, fill=self.colors['success'])
            self.status_indicator.itemconfig(self.status_text, text="ONLINE",
                                             fill=self.colors['success'])
            # Pulse animation
            self.pulse_status_indicator()
        else:
            self.status_indicator.itemconfig(self.status_dot, fill=self.colors['text_dim'])
            self.status_indicator.itemconfig(self.status_text, text="OFFLINE",
                                             fill=self.colors['text_dim'])

    def pulse_status_indicator(self):
        """Pulse animation for online status"""
        if not self.connected:
            return

        # Create pulsing effect
        def pulse():
            for i in range(10):
                if not self.connected:
                    break
                scale = 1 + (0.2 * math.sin(i * math.pi / 10))
                self.status_indicator.scale(self.status_dot, 20, 20, scale, scale)
                self.root.update()
                time.sleep(0.05)

            # Reset size
            self.status_indicator.coords(self.status_dot, 15, 15, 25, 25)

        threading.Thread(target=pulse, daemon=True).start()

    def update_progress_bar(self, progress):
        """Update custom progress bar"""
        width = self.progress_canvas.winfo_width()
        if width > 1:
            fill_width = width * (progress / 100)
            self.progress_canvas.coords(self.progress_fill, 0, 0, fill_width, 6)

    def update_track_display(self, track_name):
        """Update track display with animation"""
        if track_name:
            display_name = os.path.splitext(track_name)[0]
            self.track_label.config(text=display_name)
            self.artist_label.config(text="Radio Stream")

            # Add fade-in effect
            self.fade_in_track_info()
        else:
            self.track_label.config(text="No track playing")
            self.artist_label.config(text="Connect to start streaming")

    def fade_in_track_info(self):
        """Fade in track information"""
        # This would require more complex implementation
        # For now, just ensure it's visible
        pass

    def process_audio_for_visualizer(self, audio_data):
        """Process audio data for visualization"""
        if not self.visualizer_enabled or self.shutdown_event.is_set():
            return

        try:
            audio_array = np.frombuffer(audio_data, dtype=np.int16)

            if self.channels == 2 and len(audio_array) >= 2:
                audio_array = audio_array[::2]

            if len(audio_array) < self.chunk_size:
                padded = np.zeros(self.chunk_size, dtype=np.int16)
                if len(audio_array) > 0:
                    padded[:len(audio_array)] = audio_array
                audio_array = padded
            else:
                audio_array = audio_array[:self.chunk_size]

            with self.visualizer_lock:
                if not self.shutdown_event.is_set():
                    self.visualizer_data.append(audio_array.copy())

        except Exception as e:
            print(f"Error processing audio for visualizer: {e}")

    def apply_volume(self, audio_data):
        """Apply volume scaling to audio data"""
        try:
            if self.shutdown_event.is_set():
                return audio_data

            volume = self.volume_value / 100.0
            if volume == 1.0:
                return audio_data

            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            audio_array = (audio_array * volume).astype(np.int16)
            return audio_array.tobytes()
        except Exception as e:
            print(f"Error applying volume: {e}")
            return audio_data

    def load_settings(self):
        """Load saved settings"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)

                if 'volume' in settings:
                    self.volume_value = settings['volume']
                    self.update_volume_display()

        except Exception as e:
            print(f"Error loading settings: {e}")

    def save_settings(self):
        """Save current settings"""
        try:
            settings = {
                'server_ip': self.host,
                'server_port': self.port,
                'volume': self.volume_value,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }

            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)

        except Exception as e:
            print(f"Error saving settings: {e}")

    # Include all the original audio handling methods
    def play_audio_buffer_safe(self):
        """Thread function to play buffered audio frames"""
        print("Starting audio playback thread")
        self.playback_active = True

        while self.connected and self.playback_active and not self.shutdown_event.is_set():
            try:
                try:
                    frame = self.audio_queue.get(timeout=0.1)
                except queue.Empty:
                    continue

                if not frame or self.shutdown_event.is_set():
                    continue

                self.process_audio_for_visualizer(frame)

                with self.stream_lock:
                    if self.stream and frame and not self.shutdown_event.is_set():
                        try:
                            frame = self.apply_volume(frame)
                            if frame and not self.shutdown_event.is_set():
                                self.stream.write(frame)
                        except Exception as e:
                            print(f"Error playing audio frame: {e}")
                            break

            except Exception as e:
                print(f"Error in playback thread: {e}")
                break

        print("Audio playback thread ended")
        self.playback_active = False

    def start_time_tracking(self):
        """Start tracking elapsed time"""

        def update_time():
            self.track_start_time = time.time() - self.current_track_elapsed

            while self.time_tracking_active and self.connected and not self.shutdown_event.is_set():
                try:
                    current_time = time.time()
                    elapsed = int(current_time - self.track_start_time)

                    if elapsed > self.current_track_duration:
                        elapsed = self.current_track_duration

                    if not self.shutdown_event.is_set():
                        self.root.after(0, self.update_time_display, elapsed)

                    if elapsed >= self.current_track_duration:
                        break

                    time.sleep(0.5)

                except Exception as e:
                    print(f"Error in time tracking: {e}")
                    break

        self.time_tracking_active = True
        self.time_update_thread = threading.Thread(target=update_time, daemon=True)
        self.time_update_thread.start()

    def update_time_display(self, elapsed):
        """Update time display"""
        try:
            if self.shutdown_event.is_set():
                return

            minutes, seconds = divmod(elapsed, 60)
            time_str = f"{minutes}:{seconds:02d}"
            self.time_elapsed.config(text=time_str)

            if self.current_track_duration > 0:
                progress = min(100, (elapsed / self.current_track_duration) * 100)
                self.update_progress_bar(progress)
        except Exception as e:
            print(f"Error updating time display: {e}")

    def stop_time_tracking_safe(self):
        """Stop time tracking safely"""
        print("Stopping time tracking")
        self.time_tracking_active = False

        if self.time_update_thread and self.time_update_thread.is_alive():
            self.time_update_thread.join(timeout=2.0)

        try:
            if not self.shutdown_event.is_set():
                self.root.after(0, lambda: self.time_elapsed.config(text="0:00"))
                self.root.after(0, lambda: self.update_progress_bar(0))
        except:
            pass

        self.current_track_elapsed = 0

    def clear_audio_buffers_safe(self):
        """Clear audio buffers safely"""
        print("Clearing audio buffers")

        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break

        with self.visualizer_lock:
            self.visualizer_data.clear()

    def close_audio_stream_safe(self):
        """Close audio stream safely"""
        print("Closing audio stream")

        with self.stream_lock:
            if self.stream:
                try:
                    if hasattr(self.stream, 'is_active') and self.stream.is_active():
                        self.stream.stop_stream()
                    self.stream.close()
                    self.stream = None
                    print("Audio stream closed")
                except Exception as e:
                    print(f"Error closing audio stream: {e}")
                    self.stream = None

    def login_again(self):
        """Try to login again with saved credentials"""
        message = {
            "username": self.username,
            "password": self.password,
            "type": 'login'
        }

        self.context = ssl.create_default_context()
        self.context.check_hostname = False
        self.context.verify_mode = ssl.CERT_REQUIRED
        self.context.load_verify_locations(CERT_FILE)

        try:
            with socket.create_connection((self.server_ip, LOGINPORT), timeout=5) as sock:
                with self.context.wrap_socket(sock, server_hostname=self.server_ip) as ssock:
                    ssock.sendall(json.dumps(message).encode('utf-8'))
                    response = ssock.recv(BUFFER_SIZE).decode('utf-8').strip()
                    try:
                        response = json.loads(response)
                        if isinstance(response, dict) and response.get("status") == "success":
                            self.token = response.get("token")
                            self.index = response.get("index")
                            self.key = response.get("key")
                            return True
                    except json.JSONDecodeError:
                        pass
        except:
            pass

        return False

    def receive_messages(self):
        """Receive messages from server"""
        buffer = b''

        while self.connected and not self.shutdown_event.is_set():
            try:
                data = None
                self.client_socket.settimeout(5000)
                try:
                    data, addr = self.client_socket.recvfrom(2048 * 4)
                except ConnectionResetError:
                    break
                except socket.timeout:
                    break
                except Exception as e:
                    print("Error in receive udp", e)

                if not data:
                    print("No data received")
                    break

                buffer += data

                while buffer and not self.shutdown_event.is_set():
                    if buffer.startswith(b'AUDIO'):
                        if len(buffer) < 9:
                            break

                        data_len = int.from_bytes(buffer[5:9], 'big')
                        total_len = 9 + data_len

                        if len(buffer) < total_len:
                            break

                        audio_data = buffer[9:total_len]

                        if not self.shutdown_event.is_set():
                            try:
                                self.audio_queue.put(audio_data, timeout=0.01)
                            except queue.Full:
                                try:
                                    self.audio_queue.get_nowait()
                                    self.audio_queue.put(audio_data, timeout=0.01)
                                except:
                                    pass

                        buffer = buffer[total_len:]

                    elif buffer.startswith(b'JSON'):
                        if len(buffer) < 8:
                            break

                        msg_len = int.from_bytes(buffer[4:8], 'big')
                        total_len = 8 + msg_len

                        if len(buffer) < total_len:
                            break

                        json_data = buffer[8:total_len].decode('utf-8')

                        try:
                            msg = json.loads(json_data)
                            if not self.shutdown_event.is_set():
                                self.handle_json_message_safe(msg)
                        except json.JSONDecodeError as e:
                            print(f"Error decoding JSON: {e}")

                        buffer = buffer[total_len:]

                    else:
                        print("Unknown message format")
                        buffer = b''
                        break

            except Exception as e:
                if not self.shutdown_event.is_set():
                    print(f"Error receiving data: {e}")
                break

        print("Message receiver thread ending")
        if not hasattr(self, 'closing') or not self.closing:
            if not self.shutdown_event.is_set():
                self.disconnect_safe()

    def handle_json_message_safe(self, msg):
        """Handle JSON messages safely"""
        try:
            if self.shutdown_event.is_set():
                return

            if msg["type"] == "stop":
                print("Received stop command")
                self.stop_time_tracking_safe()
                self.clear_audio_buffers_safe()

                if not self.shutdown_event.is_set():
                    self.root.after(0, lambda: self.update_track_display(""))

            elif msg["type"] == "track_info":
                track_name = msg.get('track', '')
                if not self.shutdown_event.is_set():
                    self.root.after(0, lambda: self.update_track_display(track_name))

            elif msg["type"] == "format_info":
                print(f"Format info: rate={msg.get('rate')}, channels={msg.get('channels')}")

                if self.shutdown_event.is_set():
                    return

                self.rate = msg.get("rate", 44100)
                self.channels = msg.get("channels", 2)
                self.format = msg.get("format", pyaudio.paInt16)
                self.frames = msg.get("frames", 0)

                if self.frames > 0 and self.rate > 0:
                    self.current_track_duration = int(self.frames / self.rate)
                    minutes = self.current_track_duration // 60
                    seconds = self.current_track_duration % 60
                    duration_str = f"{minutes}:{seconds:02d}"
                    if not self.shutdown_event.is_set():
                        self.root.after(0, lambda: self.time_total.config(text=duration_str))

                self.current_track_elapsed = msg.get("current_time", 0)

                self.close_audio_stream_safe()

                if not self.shutdown_event.is_set():
                    try:
                        with self.stream_lock:
                            self.stream = self.audio.open(
                                format=self.format,
                                channels=self.channels,
                                rate=self.rate,
                                output=True,
                                frames_per_buffer=self.chunk_size
                            )
                        print(f"Audio stream created: {self.rate}Hz, {self.channels} channels")
                        self.start_time_tracking()

                    except Exception as e:
                        print(f"Error creating audio stream: {e}")

            elif msg["type"] == "loginrequired":
                self.token = None
                print("Login required")
                self.login_again()

        except Exception as e:
            print(f"Error handling JSON message: {e}")

    def ping_host(self):
        """Send ping to server"""
        while self.connected:
            if self.token is not None:
                timestamp = time.time()
                packed_ts = struct.pack('!d', timestamp)
                decoded_key = base64.b64decode(self.key.encode('utf-8'))
                aesgcm = AESGCM(decoded_key)
                nonce = os.urandom(12)
                ciphertext = aesgcm.encrypt(nonce, packed_ts + self.token.encode('utf-8'), None)

                pingmsg = b'ping' + self.index.encode('utf-8') + nonce + ciphertext

                try:
                    self.client_socket.sendto(pingmsg, self.server_addr)
                except ConnectionResetError:
                    pass

            time.sleep(4)

    def connect(self):
        """Connect to server"""
        if not self.connected:
            try:
                self.server_addr = (self.server_ip, self.port)
                self.shutdown_event.clear()

                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.connected = True

                ping_thread = threading.Thread(target=self.ping_host, daemon=True)
                ping_thread.start()

                self.update_connection_status(True)
                self.save_settings()

                receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
                receive_thread.start()

                self.playback_thread = threading.Thread(target=self.play_audio_buffer_safe, daemon=True)
                self.playback_thread.start()

                print("Connected successfully")

            except Exception as e:
                messagebox.showerror("Connection Error", f"Failed to connect: {str(e)}")
                self.connected = False
                self.update_connection_status(False)
        else:
            self.disconnect_safe()

    def disconnect_safe(self):
        """Disconnect safely"""
        print("Disconnecting...")

        try:
            self.client_socket.sendto("quit".encode('utf-8'), self.server_addr)
        except:
            pass

        self.shutdown_event.set()
        self.connected = False
        self.playback_active = False

        self.stop_time_tracking_safe()
        self.clear_audio_buffers_safe()
        self.close_audio_stream_safe()

        if self.client_socket:
            try:
                self.client_socket.close()
                self.client_socket = None
            except:
                pass

        self.update_connection_status(False)
        self.update_track_display("")

        print("Disconnected")

    def close_client_safe(self):
        """Close client safely"""
        print("Closing client...")

        self.shutdown_event.set()
        self.closing = True

        if self.connected:
            self.disconnect_safe()

        time.sleep(0.2)

        try:
            if hasattr(self, 'audio'):
                self.audio.terminate()
        except:
            pass

        try:
            self.save_settings()
        except:
            pass

        print("Client closed")


def open_main_app(username, password, server_ip, token, index, key):
    main(server_ip, token, index, key, username, password)


def main(server_ip, token, index, key, username, password):
    root = tk.Tk()

    # Set DPI awareness for Windows
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass

    app = ModernRadioClient(root, server_ip, token, index, key, username, password)

    def on_closing():
        print("Closing window...")
        if app.connected:
            result = messagebox.askyesno(
                "Confirm Exit",
                "You are still connected. Disconnect and exit?"
            )
            if not result:
                return

        try:
            app.close_client_safe()
        except:
            pass

        try:
            root.destroy()
        except:
            pass

    root.protocol("WM_DELETE_WINDOW", on_closing)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            app.close_client_safe()
        except:
            pass


if __name__ == "__main__":
    login = ModernLoginDialog()
    login.mainloop()