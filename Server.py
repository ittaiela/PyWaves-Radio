# server.py - Modern Radio Station GUI with enhanced aesthetics
import tkinter as tk
from pydoc import plain
from tkinter import ttk, messagebox, scrolledtext, font
import socket
import threading
import json
import os
from tkinter import filedialog
from datetime import datetime, timedelta
import pyaudio
import wave
import time
# from pydub import AudioSegment
# from pydub.utils import make_chunks
import queue
from dataclasses import dataclass
from loginserver import start_server, active_tokens
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import struct
import math


@dataclass
class UdpClient:
    addr: tuple  # IPv4: (host, port)
    active: bool
    lastping: datetime


def create_modern_styles():
    """Create a modern, professional radio station theme"""
    style = ttk.Style()

    # Professional dark theme with accent colors
    colors = {
        'bg_primary': '#0f0f0f',  # Deep black background
        'bg_secondary': '#1a1a1a',  # Slightly lighter black
        'surface': '#252525',  # Card/panel background
        'surface_light': '#303030',  # Hover states
        'accent': '#ff3366',  # Vibrant pink-red (radio station color)
        'accent_hover': '#ff4477',  # Lighter accent
        'accent_dim': '#cc2855',  # Darker accent
        'success': '#00d67a',  # Bright green
        'warning': '#ffaa00',  # Amber
        'error': '#ff4444',  # Red
        'text_primary': '#ffffff',  # White text
        'text_secondary': '#b0b0b0',  # Gray text
        'text_dim': '#808080',  # Dimmer gray
        'border': '#404040',  # Border color
        'gradient_start': '#ff3366',  # Gradient colors
        'gradient_end': '#ff6b96',
    }

    # Configure theme
    style.theme_use('clam')

    # Configure root window elements
    style.configure('TFrame',
                    background=colors['bg_primary'],
                    borderwidth=0)

    style.configure('Card.TFrame',
                    background=colors['surface'],
                    relief='flat',
                    borderwidth=1)

    style.configure('TLabelframe',
                    background=colors['surface'],
                    foreground=colors['text_primary'],
                    borderwidth=1,
                    relief='flat',
                    bordercolor=colors['border'])

    style.configure('TLabelframe.Label',
                    background=colors['surface'],
                    foreground=colors['accent'],
                    font=('SF Pro Display', 11, 'bold'))

    # Headers and labels
    style.configure('Title.TLabel',
                    font=('SF Pro Display', 28, 'bold'),
                    foreground=colors['text_primary'],
                    background=colors['bg_primary'])

    style.configure('Subtitle.TLabel',
                    font=('SF Pro Text', 12),
                    foreground=colors['text_secondary'],
                    background=colors['bg_primary'])

    style.configure('Header.TLabel',
                    font=('SF Pro Display', 16, 'bold'),
                    foreground=colors['accent'],
                    background=colors['surface'])

    style.configure('Status.TLabel',
                    font=('SF Pro Text', 11),
                    foreground=colors['text_secondary'],
                    background=colors['surface'])

    style.configure('StatusGood.TLabel',
                    font=('SF Pro Text', 11, 'bold'),
                    foreground=colors['success'],
                    background=colors['surface'])

    style.configure('StatusBad.TLabel',
                    font=('SF Pro Text', 11, 'bold'),
                    foreground=colors['error'],
                    background=colors['surface'])

    style.configure('IP.TLabel',
                    font=('SF Mono', 13, 'bold'),
                    foreground=colors['text_primary'],
                    background=colors['surface_light'],
                    padding=(15, 10))

    style.configure('NowPlaying.TLabel',
                    font=('SF Pro Display', 14, 'bold'),
                    foreground=colors['accent'],
                    background=colors['surface'])

    style.configure('TrackInfo.TLabel',
                    font=('SF Pro Text', 12),
                    foreground=colors['text_primary'],
                    background=colors['surface'])

    # Modern buttons with hover effects
    style.configure('Action.TButton',
                    font=('SF Pro Text', 10, 'bold'),
                    foreground=colors['text_primary'],
                    background=colors['accent'],
                    borderwidth=0,
                    focuscolor='none',
                    padding=(20, 10),
                    relief='flat')
    style.map('Action.TButton',
              background=[('active', colors['accent_hover']),
                          ('pressed', colors['accent_dim'])])

    style.configure('Control.TButton',
                    font=('SF Pro Text', 14, 'bold'),
                    foreground=colors['text_primary'],
                    background=colors['surface_light'],
                    borderwidth=0,
                    focuscolor='none',
                    padding=(15, 12),
                    relief='flat')
    style.map('Control.TButton',
              background=[('active', colors['border']),
                          ('pressed', colors['surface'])])

    style.configure('Success.TButton',
                    font=('SF Pro Text', 10, 'bold'),
                    foreground=colors['bg_primary'],
                    background=colors['success'],
                    borderwidth=0,
                    focuscolor='none',
                    padding=(20, 10),
                    relief='flat')
    style.map('Success.TButton',
              background=[('active', '#00e688'),
                          ('pressed', '#00c06a')])

    style.configure('Warning.TButton',
                    font=('SF Pro Text', 10, 'bold'),
                    foreground=colors['text_primary'],
                    background=colors['error'],
                    borderwidth=0,
                    focuscolor='none',
                    padding=(20, 10),
                    relief='flat')
    style.map('Warning.TButton',
              background=[('active', '#ff5555'),
                          ('pressed', '#ee3333')])

    style.configure('Small.TButton',
                    font=('SF Pro Text', 9),
                    foreground=colors['text_primary'],
                    background=colors['surface_light'],
                    borderwidth=0,
                    focuscolor='none',
                    padding=(10, 5),
                    relief='flat')
    style.map('Small.TButton',
              background=[('active', colors['border']),
                          ('pressed', colors['surface'])])

    # Modern Treeview styling
    style.configure('Treeview',
                    background=colors['surface'],
                    foreground=colors['text_primary'],
                    fieldbackground=colors['surface'],
                    borderwidth=0,
                    font=('SF Pro Text', 10))
    style.configure('Treeview.Heading',
                    background=colors['surface_light'],
                    foreground=colors['text_secondary'],
                    font=('SF Pro Text', 10, 'bold'),
                    borderwidth=0,
                    relief='flat')
    style.map('Treeview',
              background=[('selected', colors['accent'])],
              foreground=[('selected', colors['text_primary'])])
    style.map('Treeview.Heading',
              background=[('active', colors['border'])])

    # Progress bar styling
    style.configure('Audio.Horizontal.TProgressbar',
                    background=colors['accent'],
                    troughcolor=colors['surface_light'],
                    borderwidth=0,
                    lightcolor=colors['accent'],
                    darkcolor=colors['accent'])

    # Scrollbar styling
    style.configure('Vertical.TScrollbar',
                    background=colors['surface_light'],
                    troughcolor=colors['surface'],
                    borderwidth=0,
                    arrowcolor=colors['text_dim'],
                    darkcolor=colors['surface_light'],
                    lightcolor=colors['surface_light'],
                    width=12)

    # Scale (slider) styling for volume
    style.configure('Volume.Horizontal.TScale',
                    background=colors['surface'],
                    troughcolor=colors['surface_light'],
                    borderwidth=0)
    style.map('Volume.Horizontal.TScale',
              background=[('active', colors['surface'])])

    return colors


class ModernRadioServer:
    def __init__(self, root):
        self.client_count = None
        self.server_status = None
        self.server_ip_label = None
        self.root = root
        self.root.title("Radio Station Control Center")
        self.root.geometry("1500x800")

        # Get colors from style
        self.colors = create_modern_styles()
        self.root.configure(bg=self.colors['bg_primary'])

        # Set window icon and properties
        self.root.resizable(True, True)
        self.root.minsize(1000, 700)

        # Server settings
        self.host = '0.0.0.0'
        self.port = 12345
        self.server_socket = None
        self.clients = []
        self.udpclients = {}
        self.current_track = ""
        self.playlist = []
        self.index = 0
        self.audio = pyaudio.PyAudio()
        self.TOKEN_VALID_HOURS = 10

        # Audio settings
        self.chunk_size = 256
        self.buffer_chunks = 8
        self.audio_queue = queue.Queue(maxsize=50)
        self.playing = False
        self.audio_thread_active = False
        self.sampwidth = 2
        self.params = None
        self.default_params = {
            "nchannels": 2,
            "framerate": 44100,
            "sampwidth": 2,
            "nframes": 0
        }
        self.current_track_elapsed = 0
        self.resume_button = True

        # Audio conversion variables
        self.audio_segments = {}
        self.current_audio_data = None
        self.audio_position = 0

        # Threading controls
        self.frame_reader_thread = None
        self.broadcast_thread = None
        self.stop_event = threading.Event()

        # Playlist file path
        self.playlist_file = "server_playlist.json"

        # Volume control
        self.volume = 1.0

        # Animation variables
        self.animation_running = False
        self.waveform_canvas = None

        self.setup_modern_ui()
        self.load_playlist()
        self.start_animations()

    def get_local_ip(self):
        """Get the local IP address of the machine"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "127.0.0.1"

    def setup_modern_ui(self):
        """Create the modern UI layout"""
        # Main container with gradient-like background effect
        main_container = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_container.pack(fill="both", expand=True)

        # Top header section
        self.create_header_section(main_container)

        # Content area with three columns
        content_frame = tk.Frame(main_container, bg=self.colors['bg_primary'])
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Left column - Server control and now playing
        left_frame = tk.Frame(content_frame, bg=self.colors['bg_primary'])
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.create_server_control_panel(left_frame)
        self.create_now_playing_panel(left_frame)
        self.create_activity_log_panel(left_frame)

        # Right column - Playlist management
        right_frame = tk.Frame(content_frame, bg=self.colors['bg_primary'])
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

        self.create_playlist_panel(right_frame)

    def create_header_section(self, parent):
        """Create the modern header with title and status"""
        header_frame = tk.Frame(parent, bg=self.colors['bg_primary'], height=100)
        header_frame.pack(fill="x", padx=20, pady=(20, 30))
        header_frame.pack_propagate(False)

        # Left side - Title and subtitle
        title_frame = tk.Frame(header_frame, bg=self.colors['bg_primary'])
        title_frame.pack(side="left", fill="both", expand=True)

        # Radio icon and title
        title_container = tk.Frame(title_frame, bg=self.colors['bg_primary'])
        title_container.pack(anchor="w", pady=(10, 5))

        title_label = ttk.Label(title_container,
                                text="📻 RADIO STATION",
                                style='Title.TLabel')
        title_label.pack(side="left")

        subtitle_label = ttk.Label(title_frame,
                                   text="Professional Broadcasting Control Center",
                                   style='Subtitle.TLabel')
        subtitle_label.pack(anchor="w")

        # Right side - Live status indicator
        status_frame = tk.Frame(header_frame, bg=self.colors['bg_primary'])
        status_frame.pack(side="right", anchor="e", pady=20)

        self.live_indicator = tk.Canvas(status_frame, width=120, height=40,
                                        bg=self.colors['bg_primary'],
                                        highlightthickness=0)
        self.live_indicator.pack()

        # Create ON AIR indicator
        self.on_air_bg = self.live_indicator.create_rectangle(0, 0, 120, 40,
                                                              fill=self.colors['surface'],
                                                              outline="")
        self.on_air_text = self.live_indicator.create_text(60, 20,
                                                           text="OFF AIR",
                                                           font=('SF Pro Display', 14, 'bold'),
                                                           fill=self.colors['text_dim'])

    def create_server_control_panel(self, parent):
        """Create the server control panel with modern styling"""
        # Card-style frame
        control_card = tk.Frame(parent, bg=self.colors['surface'])
        control_card.pack(fill="x", pady=(0, 15))
        self.add_shadow_effect(control_card)

        inner_frame = tk.Frame(control_card, bg=self.colors['surface'])
        inner_frame.pack(fill="x", padx=20, pady=20)

        # Section header
        header_label = ttk.Label(inner_frame, text="Server Control", style='Header.TLabel')
        header_label.pack(anchor="w", pady=(0, 15))

        # Server IP display with modern card design
        ip_card = tk.Frame(inner_frame, bg=self.colors['surface_light'], height=60)
        ip_card.pack(fill="x", pady=(0, 15))
        ip_card.pack_propagate(False)

        ip_inner = tk.Frame(ip_card, bg=self.colors['surface_light'])
        ip_inner.place(relx=0.5, rely=0.5, anchor="center")

        self.server_ip_label = ttk.Label(ip_inner,
                                         text=f"Server Address: {self.get_local_ip()}:{self.port}",
                                         style='IP.TLabel')
        self.server_ip_label.pack()

        # Status indicators row
        status_row = tk.Frame(inner_frame, bg=self.colors['surface'])
        status_row.pack(fill="x", pady=(0, 20))

        # Server status with icon
        status_left = tk.Frame(status_row, bg=self.colors['surface'])
        status_left.pack(side="left", fill="x", expand=True)

        self.server_status_icon = tk.Label(status_left, text="⚫",
                                           font=('Arial', 12),
                                           bg=self.colors['surface'],
                                           fg=self.colors['error'])
        self.server_status_icon.pack(side="left", padx=(0, 5))

        self.server_status = ttk.Label(status_left, text="Server Offline",
                                       style='StatusBad.TLabel')
        self.server_status.pack(side="left")

        # Client count with icon
        status_right = tk.Frame(status_row, bg=self.colors['surface'])
        status_right.pack(side="right")

        self.client_icon = tk.Label(status_right, text="👥",
                                    font=('Arial', 14),
                                    bg=self.colors['surface'])
        self.client_icon.pack(side="left", padx=(0, 5))

        self.client_count = ttk.Label(status_right, text="0 Listeners",
                                      style='Status.TLabel')
        self.client_count.pack(side="left")

        # Control buttons with better spacing
        btn_frame = tk.Frame(inner_frame, bg=self.colors['surface'])
        btn_frame.pack(fill="x")

        self.start_button = ttk.Button(btn_frame, text="▶  START SERVER",
                                       command=self.start_server, style='Success.TButton')
        self.start_button.pack(side="left", padx=(0, 10))

        self.stop_button = ttk.Button(btn_frame, text="■  STOP SERVER",
                                      command=self.stop_server, state="disabled",
                                      style='Warning.TButton')
        self.stop_button.pack(side="left")

    def create_now_playing_panel(self, parent):
        """Create the Now Playing panel with visualizer"""
        # Card-style frame
        playing_card = tk.Frame(parent, bg=self.colors['surface'])
        playing_card.pack(fill="x", pady=(0, 15))
        self.add_shadow_effect(playing_card)

        inner_frame = tk.Frame(playing_card, bg=self.colors['surface'])
        inner_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Section header
        header_label = ttk.Label(inner_frame, text="Now Playing", style='Header.TLabel')
        header_label.pack(anchor="w", pady=(0, 15))

        # Track info section
        track_frame = tk.Frame(inner_frame, bg=self.colors['surface'])
        track_frame.pack(fill="x", pady=(0, 15))

        self.now_playing_label = ttk.Label(track_frame,
                                           text="No track playing",
                                           style='NowPlaying.TLabel')
        self.now_playing_label.pack(anchor="w")

        self.track_time_label = ttk.Label(track_frame,
                                          text="--:-- / --:--",
                                          style='TrackInfo.TLabel')
        self.track_time_label.pack(anchor="w", pady=(5, 0))

        # Audio visualizer canvas
        self.waveform_canvas = tk.Canvas(inner_frame,
                                         height=60,
                                         bg=self.colors['surface_light'],
                                         highlightthickness=0)
        self.waveform_canvas.pack(fill="x", pady=(0, 15))

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(inner_frame,
                                            variable=self.progress_var,
                                            style='Audio.Horizontal.TProgressbar',
                                            maximum=100)
        self.progress_bar.pack(fill="x", pady=(0, 20))

        # Playback controls
        controls_frame = tk.Frame(inner_frame, bg=self.colors['surface'])
        controls_frame.pack()

        # Create rounded button style
        self.prev_button = ttk.Button(controls_frame, text="⏮",
                                      command=self.previous_track,
                                      style='Control.TButton',
                                      width=5)
        self.prev_button.pack(side="left", padx=5)

        self.play_button = ttk.Button(controls_frame, text="▶",
                                      command=self.toggle_play,
                                      style='Control.TButton',
                                      width=5)
        self.play_button.pack(side="left", padx=5)

        self.next_button = ttk.Button(controls_frame, text="⏭",
                                      command=self.next_track,
                                      style='Control.TButton',
                                      width=5)
        self.next_button.pack(side="left", padx=5)

    def create_activity_log_panel(self, parent):
        """Create the activity log with modern styling"""
        # Card-style frame
        log_card = tk.Frame(parent, bg=self.colors['surface'])
        log_card.pack(fill="both", expand=True)
        self.add_shadow_effect(log_card)

        inner_frame = tk.Frame(log_card, bg=self.colors['surface'])
        inner_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Section header with clear button
        header_frame = tk.Frame(inner_frame, bg=self.colors['surface'])
        header_frame.pack(fill="x", pady=(0, 15))

        header_label = ttk.Label(header_frame, text="Activity Log", style='Header.TLabel')
        header_label.pack(side="left")

        clear_btn = ttk.Button(header_frame, text="Clear",
                               command=self.clear_log,
                               style='Small.TButton')
        clear_btn.pack(side="right")

        # Modern log display
        log_container = tk.Frame(inner_frame, bg=self.colors['surface_light'])
        log_container.pack(fill="both", expand=True)

        self.log_text = scrolledtext.ScrolledText(
            log_container,
            height=8,
            font=('SF Mono', 9),
            bg=self.colors['surface_light'],
            fg=self.colors['text_secondary'],
            insertbackground=self.colors['accent'],
            selectbackground=self.colors['accent'],
            selectforeground=self.colors['text_primary'],
            borderwidth=0,
            relief='flat',
            wrap=tk.WORD
        )
        self.log_text.pack(fill="both", expand=True, padx=1, pady=1)

        # Configure log tags for colored messages
        self.log_text.tag_config("error", foreground=self.colors['error'])
        self.log_text.tag_config("success", foreground=self.colors['success'])
        self.log_text.tag_config("warning", foreground=self.colors['warning'])
        self.log_text.tag_config("info", foreground=self.colors['accent'])

    def create_playlist_panel(self, parent):
        """Create the playlist management panel"""
        # Card-style frame
        playlist_card = tk.Frame(parent, bg=self.colors['surface'])
        playlist_card.pack(fill="both", expand=True)
        self.add_shadow_effect(playlist_card)

        inner_frame = tk.Frame(playlist_card, bg=self.colors['surface'])
        inner_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Section header
        header_label = ttk.Label(inner_frame, text="Playlist Manager", style='Header.TLabel')
        header_label.pack(anchor="w", pady=(0, 15))

        # Playlist controls
        controls_frame = tk.Frame(inner_frame, bg=self.colors['surface'])
        controls_frame.pack(fill="x", pady=(0, 15))

        # File operations row
        file_ops = tk.Frame(controls_frame, bg=self.colors['surface'])
        file_ops.pack(fill="x", pady=(0, 10))

        self.add_button = ttk.Button(file_ops, text="+ Add Tracks",
                                     command=self.add_songs,
                                     style='Action.TButton')
        self.add_button.pack(side="left", padx=(0, 10))

        self.remove_button = ttk.Button(file_ops, text="− Remove",
                                        command=self.remove_selected,
                                        style='Small.TButton')
        self.remove_button.pack(side="left", padx=(0, 10))

        self.clear_playlist_btn = ttk.Button(file_ops, text="Clear All",
                                             command=self.clear_playlist,
                                             style='Small.TButton')
        self.clear_playlist_btn.pack(side="left")

        # Reorder operations row
        reorder_ops = tk.Frame(controls_frame, bg=self.colors['surface'])
        reorder_ops.pack(fill="x")

        reorder_label = ttk.Label(reorder_ops, text="Reorder:", style='Status.TLabel')
        reorder_label.pack(side="left", padx=(0, 10))

        self.move_up_button = ttk.Button(reorder_ops, text="↑",
                                         command=self.move_selected_up,
                                         style='Small.TButton',
                                         width=3)
        self.move_up_button.pack(side="left", padx=(0, 5))

        self.move_down_button = ttk.Button(reorder_ops, text="↓",
                                           command=self.move_selected_down,
                                           style='Small.TButton',
                                           width=3)
        self.move_down_button.pack(side="left")

        # Playlist info
        info_label = ttk.Label(reorder_ops,
                               text="Drag to reorder • Double-click to play",
                               style='Status.TLabel')
        info_label.pack(side="right")

        # Modern playlist display
        playlist_container = tk.Frame(inner_frame, bg=self.colors['surface_light'])
        playlist_container.pack(fill="both", expand=True)

        # Create treeview with custom style
        self.playlist_box = ttk.Treeview(playlist_container,
                                         columns=('Duration', 'Status'),
                                         show='tree headings',
                                         height=20,
                                         selectmode='browse')

        # Configure columns
        self.playlist_box.heading('#0', text='Track')
        self.playlist_box.heading('Duration', text='Duration')
        self.playlist_box.heading('Status', text='Status')

        self.playlist_box.column('#0', width=350, minwidth=250)
        self.playlist_box.column('Duration', width=80, minwidth=80, anchor='center')
        self.playlist_box.column('Status', width=100, minwidth=100, anchor='center')

        self.playlist_box.pack(side="left", fill="both", expand=True)

        # Modern scrollbar
        playlist_scroll = ttk.Scrollbar(playlist_container, orient="vertical",
                                        command=self.playlist_box.yview)
        playlist_scroll.pack(side="right", fill="y")
        self.playlist_box.configure(yscrollcommand=playlist_scroll.set)

        # Setup drag and drop
        self.setup_drag_and_drop()

        # Playlist stats
        stats_frame = tk.Frame(inner_frame, bg=self.colors['surface'])
        stats_frame.pack(fill="x", pady=(15, 0))

        self.playlist_stats = ttk.Label(stats_frame,
                                        text="0 tracks • 0:00 total duration",
                                        style='Status.TLabel')
        self.playlist_stats.pack(side="left")

    def add_shadow_effect(self, widget):
        """Add a subtle shadow effect to cards"""
        widget.configure(relief='flat', borderwidth=0)

    def clear_log(self):
        """Clear the activity log"""
        self.log_text.delete(1.0, tk.END)

    def clear_playlist(self):
        """Clear all tracks from playlist"""
        if self.playlist and messagebox.askyesno("Clear Playlist",
                                                 "Remove all tracks from the playlist?"):
            self.playlist_box.delete(*self.playlist_box.get_children())
            self.playlist = []
            self.save_playlist()
            self.update_playlist_stats()
            self.log_message("Playlist cleared", "info")

    def update_playlist_stats(self):
        """Update playlist statistics display"""
        total_duration = 0
        track_count = len(self.playlist)

        for item in self.playlist_box.get_children():
            duration = self.playlist_box.item(item, 'values')[0]
            if duration != "Unknown":
                parts = duration.split(':')
                if len(parts) == 2:
                    total_duration += int(parts[0]) * 60 + int(parts[1])

        # Format total duration
        hours = total_duration // 3600
        minutes = (total_duration % 3600) // 60
        seconds = total_duration % 60

        if hours > 0:
            duration_text = f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            duration_text = f"{minutes}:{seconds:02d}"

        self.playlist_stats.config(text=f"{track_count} tracks • {duration_text} total duration")

    def start_animations(self):
        """Start UI animations"""
        self.animation_running = True
        self.animate_on_air_indicator()
        self.animate_waveform()
        self.update_time_display()

    def animate_on_air_indicator(self):
        """Animate the ON AIR indicator"""
        if not self.animation_running:
            return

        if hasattr(self, 'server_socket') and self.server_socket and self.playing:
            # Pulsing red effect when on air
            self.on_air_pulse = getattr(self, 'on_air_pulse', 0)
            self.on_air_pulse += 0.1

            # Calculate pulsing alpha
            alpha = (math.sin(self.on_air_pulse) + 1) / 2
            color = self.interpolate_color(self.colors['error'], self.colors['accent'], alpha)

            self.live_indicator.itemconfig(self.on_air_bg, fill=color)
            self.live_indicator.itemconfig(self.on_air_text, text="ON AIR",
                                           fill=self.colors['text_primary'])
        else:
            self.live_indicator.itemconfig(self.on_air_bg, fill=self.colors['surface'])
            self.live_indicator.itemconfig(self.on_air_text, text="OFF AIR",
                                           fill=self.colors['text_dim'])

        self.root.after(50, self.animate_on_air_indicator)

    def animate_waveform(self):
        """Animate the audio waveform visualizer"""
        if not self.animation_running or not self.waveform_canvas:
            return

        self.waveform_canvas.delete("all")
        width = self.waveform_canvas.winfo_width()
        height = self.waveform_canvas.winfo_height()

        if width > 1 and self.playing:
            # Create animated waveform bars
            bar_count = 40
            bar_width = width / bar_count

            for i in range(bar_count):
                if self.playing:
                    # Random height for animation effect
                    bar_height = height * (0.3 + 0.7 * abs(math.sin(time.time() * 2 + i * 0.3)))
                else:
                    bar_height = height * 0.1

                x1 = i * bar_width + 2
                x2 = (i + 1) * bar_width - 2
                y1 = (height - bar_height) / 2
                y2 = (height + bar_height) / 2

                # Gradient effect based on position
                color = self.interpolate_color(self.colors['accent'],
                                               self.colors['gradient_end'],
                                               i / bar_count)

                self.waveform_canvas.create_rectangle(x1, y1, x2, y2,
                                                      fill=color,
                                                      outline="")

        self.root.after(50, self.animate_waveform)

    def update_time_display(self):
        """Update the track time display"""
        if not self.animation_running:
            return

        if self.playing and self.params:
            # Calculate total time
            total_seconds = self.params.nframes // self.params.framerate
            current_seconds = self.current_track_elapsed

            # Format times
            current_time = f"{current_seconds // 60}:{current_seconds % 60:02d}"
            total_time = f"{total_seconds // 60}:{total_seconds % 60:02d}"

            self.track_time_label.config(text=f"{current_time} / {total_time}")

            # Update progress bar
            if total_seconds > 0:
                progress = (current_seconds / total_seconds) * 100
                self.progress_var.set(progress)
        else:
            self.track_time_label.config(text="--:-- / --:--")
            self.progress_var.set(0)

        self.root.after(100, self.update_time_display)

    def interpolate_color(self, color1, color2, factor):
        """Interpolate between two colors"""
        # Convert hex to RGB
        r1 = int(color1[1:3], 16)
        g1 = int(color1[3:5], 16)
        b1 = int(color1[5:7], 16)

        r2 = int(color2[1:3], 16)
        g2 = int(color2[3:5], 16)
        b2 = int(color2[5:7], 16)

        # Interpolate
        r = int(r1 + (r2 - r1) * factor)
        g = int(g1 + (g2 - g1) * factor)
        b = int(b1 + (b2 - b1) * factor)

        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"

    def log_message(self, message, level="info"):
        """Add a message to the server log with modern formatting"""
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Insert timestamp
        self.log_text.insert(tk.END, f"[{timestamp}] ", "timestamp")

        # Insert message with appropriate tag
        self.log_text.insert(tk.END, f"{message}\n", level)
        self.log_text.see(tk.END)

        # Limit log size
        lines = int(self.log_text.index('end-1c').split('.')[0])
        if lines > 500:
            self.log_text.delete('1.0', '250.0')

    def update_client_count(self):
        """Update the client count display with modern styling"""
        count = len(self.udpclients)

        if count == 0:
            self.client_count.config(text="0 Listeners")
        elif count == 1:
            self.client_count.config(text="1 Listener")
        else:
            self.client_count.config(text=f"{count} Listeners")

        # Update client icon color based on count
        if count > 0:
            self.client_icon.config(fg=self.colors['success'])
        else:
            self.client_icon.config(fg=self.colors['text_dim'])

    def toggle_play(self):
        """Toggle playback with modern UI updates"""
        if not self.playing:
            if not self.playlist:
                messagebox.showwarning("No Playlist",
                                       "Please add tracks to the playlist first")
                return

            selected_items = self.playlist_box.selection()
            if not selected_items:
                # Select first item if nothing selected
                if self.playlist_box.get_children():
                    first_item = self.playlist_box.get_children()[0]
                    self.playlist_box.selection_set(first_item)
                    selected_items = [first_item]
                else:
                    messagebox.showwarning("Empty Playlist", "No tracks in playlist")
                    return

            selected_item = selected_items[0]
            selected_index = self.playlist_box.index(selected_item)
            file_path = self.playlist[selected_index]

            # Update UI
            self.play_button.config(text="⏸")
            self.current_track = os.path.basename(file_path)

            # Update now playing display
            track_name = os.path.splitext(self.current_track)[0]
            self.now_playing_label.config(text=track_name)

            # Update playlist status
            for item in self.playlist_box.get_children():
                self.playlist_box.set(item, 'Status', '')
            self.playlist_box.set(selected_item, 'Status', '▶ Playing')

            # Clear the audio queue
            while not self.audio_queue.empty():
                try:
                    self.audio_queue.get_nowait()
                except queue.Empty:
                    break

            # Log playback start
            self.log_message(f"Now playing: {track_name}", "info")

            # Send track info
            jsonfile = json.dumps({
                "type": "track_info",
                "track": self.current_track
            })
            self.broadcast(b'JSON' + len(jsonfile).to_bytes(4, 'big') + jsonfile.encode('utf-8'))

            # Start frame reading thread
            self.frame_reader_thread = threading.Thread(
                target=self.read_frames_optimized,
                args=(file_path,),
                daemon=True
            )
            self.frame_reader_thread.start()
            self.playing = True
            self.stop_event.clear()

        else:
            # Stop playback
            jsonfile = json.dumps({"type": "stop", "track": ""})
            self.broadcast(b'JSON' + len(jsonfile).to_bytes(4, 'big') + jsonfile.encode('utf-8'))
            self.stop_audio()
            if not self.resume_button:
                self.play_button.config(text="▶")

    def stop_audio(self):
        """Stop audio playback and update UI"""
        self.playing = False
        self.resume_button = False
        self.stop_event.set()
        self.audio_thread_active = False

        # Update UI
        self.play_button.config(text="▶")
        self.now_playing_label.config(text="No track playing")

        # Clear playlist status
        for item in self.playlist_box.get_children():
            self.playlist_box.set(item, 'Status', '')

        # Clear the audio queue
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
        self.current_track_elapsed = 0

    def add_songs(self):
        """Add songs with modern file dialog"""
        files = filedialog.askopenfilenames(
            title="Select Audio Files",
            filetypes=[
                ("Audio Files", "*.wav *.mp3"),
                ("WAV Files", "*.wav"),
                ("MP3 Files", "*.mp3"),
                ("All Files", "*.*")
            ]
        )

        if files:
            added_count = 0
            for file in files:
                try:
                    filename = os.path.basename(file)
                    duration = self.get_audio_duration(file)
                    display_name = os.path.splitext(filename)[0]

                    # Add to treeview with icon
                    item = self.playlist_box.insert('', 'end',
                                                    text=f"🎵 {display_name}",
                                                    values=(duration, ''))
                    self.playlist.append(file)
                    added_count += 1

                except Exception as e:
                    self.log_message(f"Error adding {file}: {str(e)}", "error")

            if added_count > 0:
                self.save_playlist()
                self.update_playlist_stats()
                self.log_message(f"Added {added_count} tracks to playlist", "success")

    def remove_selected(self):
        """Remove selected tracks from playlist"""
        selected = self.playlist_box.selection()
        if selected:
            # Confirm if multiple items
            if len(selected) > 1:
                if not messagebox.askyesno("Remove Tracks",
                                           f"Remove {len(selected)} selected tracks?"):
                    return

            for item in reversed(selected):
                index = self.playlist_box.index(item)
                track_name = self.playlist_box.item(item, 'text').replace('🎵 ', '')
                self.playlist_box.delete(item)
                if index < len(self.playlist):
                    del self.playlist[index]
                self.log_message(f"Removed: {track_name}", "warning")

            self.save_playlist()
            self.update_playlist_stats()

    def start_server(self):
        """Start server with modern UI updates"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.settimeout(3)

            # Update UI
            self.server_status.config(text="Server Online", style='StatusGood.TLabel')
            self.server_status_icon.config(text="●", fg=self.colors['success'])
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")

            # Update IP display
            self.server_ip_label.config(text=f"Server Address: {self.get_local_ip()}:{self.port}")

            self.log_message(f"Server started on {self.get_local_ip()}:{self.port}", "success")
            self.log_message("Ready to accept connections...", "info")

            # Start listening thread
            self.accept_thread = threading.Thread(target=self.accept_clients, daemon=True)
            self.accept_thread.start()

        except Exception as e:
            messagebox.showerror("Server Error", f"Failed to start server: {str(e)}")
            self.log_message(f"Server start failed: {str(e)}", "error")

    def stop_server(self):
        """Stop server with modern UI updates"""
        if self.server_socket:
            # Stop any playing audio
            if self.playing:
                self.stop_audio()

            # Set stop event
            self.stop_event.set()

            # Close socket
            self.server_socket.close()
            self.server_socket = None

            # Update UI
            self.server_status.config(text="Server Offline", style='StatusBad.TLabel')
            self.server_status_icon.config(text="⚫", fg=self.colors['error'])
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")
            self.client_count.config(text="0 Listeners")

            self.udpclients = {}
            self.log_message("Server stopped", "warning")

    def setup_drag_and_drop(self):
        """Setup drag and drop functionality for the playlist"""
        self.playlist_box.bind('<Button-1>', self.on_drag_start)
        self.playlist_box.bind('<B1-Motion>', self.on_drag_motion)
        self.playlist_box.bind('<ButtonRelease-1>', self.on_drag_release)
        self.playlist_box.bind('<Double-1>', self.on_double_click)

        # Initialize drag data
        self.drag_data = {
            'item': None,
            'start_index': None,
            'drag_indicator': None,
            'original_selection': None,
            'start_x': None,
            'start_y': None,
            'start_time': None,
            'is_dragging': False
        }

    def on_double_click(self, event):
        """Handle double-click to play selected song"""
        item = self.playlist_box.identify('item', event.x, event.y)
        if item:
            self.playlist_box.selection_set(item)
            self.playlist_box.see(item)

            if self.playing:
                self.stop_audio()
                jsonfile = json.dumps({"type": "stop", "track": ""})
                self.broadcast(b'JSON' + len(jsonfile).to_bytes(4, 'big') + jsonfile.encode('utf-8'))

            self.resume_button = True
            time.sleep(0.1)
            self.toggle_play()

            track_name = self.playlist_box.item(item, 'text').replace('🎵 ', '')
            self.log_message(f"Playing selected: {track_name}", "info")

    def on_drag_start(self, event):
        """Handle start of drag operation"""
        item = self.playlist_box.identify('item', event.x, event.y)
        if item:
            self.drag_data['item'] = item
            self.drag_data['start_index'] = self.playlist_box.index(item)
            self.drag_data['original_selection'] = self.playlist_box.selection()
            self.playlist_box.selection_set(item)
            self.drag_data['start_x'] = event.x
            self.drag_data['start_y'] = event.y
            self.drag_data['start_time'] = time.time()
            self.drag_data['is_dragging'] = False
        else:
            self.drag_data['item'] = None

    def on_drag_motion(self, event):
        """Handle drag motion"""
        if not self.drag_data['item']:
            return

        dx = abs(event.x - self.drag_data.get('start_x', event.x))
        dy = abs(event.y - self.drag_data.get('start_y', event.y))

        if dx > 5 or dy > 5:
            self.drag_data['is_dragging'] = True

        if self.drag_data['is_dragging']:
            target_item = self.playlist_box.identify('item', event.x, event.y)
            if target_item and target_item != self.drag_data['item']:
                self.playlist_box.configure(cursor="hand2")
                self.playlist_box.selection_set(self.drag_data['item'])
            else:
                self.playlist_box.configure(cursor="")

    def on_drag_release(self, event):
        """Handle end of drag operation"""
        self.playlist_box.configure(cursor="")

        if not self.drag_data['item']:
            return

        if not self.drag_data.get('is_dragging', False):
            item = self.playlist_box.identify('item', event.x, event.y)
            if item:
                self.playlist_box.selection_set(item)
                self.playlist_box.see(item)

            self.drag_data = {
                'item': None,
                'start_index': None,
                'drag_indicator': None,
                'original_selection': None,
                'start_x': None,
                'start_y': None,
                'start_time': None,
                'is_dragging': False
            }
            return

        start_index = self.drag_data['start_index']
        target_item = self.playlist_box.identify('item', event.x, event.y)

        if target_item and target_item != self.drag_data['item']:
            target_index = self.playlist_box.index(target_item)
            bbox = self.playlist_box.bbox(target_item)
            if bbox:
                item_center = bbox[1] + bbox[3] // 2
                if event.y >= item_center:
                    target_index += 1

            if target_index != start_index:
                self.move_song_to_position(start_index, target_index)
        else:
            if 'original_selection' in self.drag_data and self.drag_data['original_selection']:
                self.playlist_box.selection_set(self.drag_data['original_selection'])

        self.drag_data = {
            'item': None,
            'start_index': None,
            'drag_indicator': None,
            'original_selection': None,
            'start_x': None,
            'start_y': None,
            'start_time': None,
            'is_dragging': False
        }

    def move_song_to_position(self, from_index, to_index):
        """Move a song from one position to another"""
        try:
            # Validate indices
            if from_index < 0 or from_index >= len(self.playlist):
                self.log_message(f"Invalid move index: {from_index}", "error")
                return

            # Don't move if it's the same position
            if from_index == to_index:
                return

            # Get the song data before removing
            items = self.playlist_box.get_children()
            moving_item = items[from_index]
            item_text = self.playlist_box.item(moving_item, 'text')
            song_values = self.playlist_box.item(moving_item, 'values')
            song_path = self.playlist[from_index]

            # Remove from playlist and treeview
            del self.playlist[from_index]
            self.playlist_box.delete(moving_item)

            # Adjust target index if we removed an item before it
            if to_index > from_index:
                to_index -= 1

            # Clamp to valid range after adjustment
            to_index = max(0, min(to_index, len(self.playlist)))

            # Insert at new position
            self.playlist.insert(to_index, song_path)
            new_item = self.playlist_box.insert('', to_index, text=item_text, values=song_values)

            # Select and show the moved item
            self.playlist_box.selection_set(new_item)
            self.playlist_box.see(new_item)

            # Save the updated playlist
            self.save_playlist()
            track_name = item_text.replace('🎵 ', '')
            self.log_message(f"Moved '{track_name}' to position {to_index + 1}", "info")

        except Exception as e:
            self.log_message(f"Error moving track: {str(e)}", "error")

    def move_selected_up(self):
        """Move selected track up in playlist"""
        selected = self.playlist_box.selection()
        if not selected:
            messagebox.showinfo("No Selection", "Please select a track to move")
            return

        selected_item = selected[0]
        current_index = self.playlist_box.index(selected_item)

        if current_index == 0:
            return

        self.move_song_to_position(current_index, current_index - 1)

    def move_selected_down(self):
        """Move selected track down in playlist"""
        selected = self.playlist_box.selection()
        if not selected:
            messagebox.showinfo("No Selection", "Please select a track to move")
            return

        selected_item = selected[0]
        current_index = self.playlist_box.index(selected_item)

        # Check if it's already at the bottom
        if current_index >= len(self.playlist) - 1:
            return

        # Move to next position
        self.move_song_to_position(current_index, current_index + 2)

    def save_playlist(self):
        """Save current playlist to file"""
        try:
            playlist_data = {
                "playlist": self.playlist,
                "timestamp": datetime.now().isoformat()
            }

            with open(self.playlist_file, 'w') as f:
                json.dump(playlist_data, f, indent=2)

            self.log_message("Playlist saved", "success")

        except Exception as e:
            self.log_message(f"Error saving playlist: {str(e)}", "error")

    def load_playlist(self):
        """Load playlist from file if it exists"""
        try:
            if os.path.exists(self.playlist_file):
                with open(self.playlist_file, 'r') as f:
                    playlist_data = json.load(f)

                loaded_count = 0
                for file_path in playlist_data.get("playlist", []):
                    if os.path.exists(file_path):
                        try:
                            filename = os.path.basename(file_path)
                            duration = self.get_audio_duration(file_path)
                            display_name = os.path.splitext(filename)[0]

                            self.playlist_box.insert('', 'end',
                                                     text=f"🎵 {display_name}",
                                                     values=(duration, ''))
                            self.playlist.append(file_path)
                            loaded_count += 1

                        except Exception as e:
                            self.log_message(f"Error loading track: {str(e)}", "error")
                    else:
                        self.log_message(f"File not found: {file_path}", "warning")

                if loaded_count > 0:
                    self.log_message(f"Loaded {loaded_count} tracks from saved playlist", "success")
                    self.update_playlist_stats()

        except Exception as e:
            self.log_message(f"Error loading playlist: {str(e)}", "error")

    def get_audio_duration(self, filename):
        """Get duration of audio file"""
        try:
            file_ext = os.path.splitext(filename)[1].lower()

            if file_ext == '.wav':
                with wave.open(filename, "rb") as wav_file:
                    frame_rate = wav_file.getframerate()
                    n_frames = wav_file.getnframes()
                    total_seconds = int(n_frames / frame_rate)
            elif file_ext == '.mp3':
                # If pydub is available
                # audio_segment = AudioSegment.from_mp3(filename)
                # total_seconds = int(len(audio_segment) / 1000)
                return "Unknown"  # Return unknown if pydub not available
            else:
                return "Unknown"

            minutes = total_seconds // 60
            seconds = total_seconds % 60
            return f"{minutes}:{seconds:02d}"

        except Exception as e:
            self.log_message(f"Error getting duration: {str(e)}", "error")
            return "Unknown"

    def next_track(self):
        """Play next track in playlist"""
        if not self.playlist:
            messagebox.showwarning("Empty Playlist", "Playlist is empty")
            return

        if self.playing:
            self.stop_audio()
            jsonfile = json.dumps({"type": "stop", "track": ""})
            self.broadcast(b'JSON' + len(jsonfile).to_bytes(4, 'big') + jsonfile.encode('utf-8'))

        current_selection = self.playlist_box.selection()
        if current_selection:
            current_index = self.playlist_box.index(current_selection[0])
            next_index = (current_index + 1) % len(self.playlist)
        else:
            next_index = 0

        next_item = self.playlist_box.get_children()[next_index]
        self.playlist_box.selection_set(next_item)
        self.playlist_box.see(next_item)

        self.resume_button = True
        time.sleep(0.1)
        self.toggle_play()

    def previous_track(self):
        """Play previous track in playlist"""
        if not self.playlist:
            messagebox.showwarning("Empty Playlist", "Playlist is empty")
            return

        if self.playing:
            self.stop_audio()
            jsonfile = json.dumps({"type": "stop", "track": ""})
            self.broadcast(b'JSON' + len(jsonfile).to_bytes(4, 'big') + jsonfile.encode('utf-8'))

        current_selection = self.playlist_box.selection()
        if current_selection:
            current_index = self.playlist_box.index(current_selection[0])
            prev_index = (current_index - 1) % len(self.playlist)
        else:
            prev_index = len(self.playlist) - 1

        prev_item = self.playlist_box.get_children()[prev_index]
        self.playlist_box.selection_set(prev_item)
        self.playlist_box.see(prev_item)

        self.resume_button = True
        time.sleep(0.1)
        self.toggle_play()

    def close_server(self):
        """Clean shutdown of server"""
        self.animation_running = False
        self.stop_server()
        if hasattr(self, 'audio'):
            self.audio.terminate()

    # All the original audio handling methods remain the same
    def read_frames_optimized(self, filename):
        """Optimized frame reading with better buffering"""
        self.log_message(f"Starting playback: {os.path.basename(filename)}", "info")

        try:
            audio_data, self.params = self.load_audio_file(filename)
            self.current_audio_data = audio_data
            self.audio_position = 0

            if self.params.sampwidth == 1:
                self.sampwidth = pyaudio.paInt8
            elif self.params.sampwidth == 2:
                self.sampwidth = pyaudio.paInt16
            elif self.params.sampwidth == 3:
                self.sampwidth = pyaudio.paInt24
            elif self.params.sampwidth == 4:
                self.sampwidth = pyaudio.paInt32
            else:
                self.sampwidth = pyaudio.paInt16

            jsonfile = json.dumps({
                "type": "format_info",
                "channels": self.params.nchannels,
                "rate": self.params.framerate,
                "format": self.sampwidth,
                "frames": self.params.nframes,
                "current_time": self.current_track_elapsed
            })
            self.broadcast(b'JSON' + len(jsonfile).to_bytes(4, 'big') + jsonfile.encode('utf-8'))

            bytes_per_frame = self.params.nchannels * self.params.sampwidth
            chunk_bytes = self.chunk_size * bytes_per_frame

            for _ in range(self.buffer_chunks):
                if self.audio_position < len(self.current_audio_data) and not self.stop_event.is_set():
                    end_pos = min(self.audio_position + chunk_bytes, len(self.current_audio_data))
                    data = self.current_audio_data[self.audio_position:end_pos]

                    if data:
                        try:
                            self.audio_queue.put(data, timeout=0.1)
                            self.audio_position = end_pos
                        except queue.Full:
                            break

            self.broadcast_thread = threading.Thread(target=self.broadcast_audio_loop, daemon=True)
            self.broadcast_thread.start()

            frame_count = 0
            self.current_track_elapsed = 0
            target_frame_time = time.time()
            frame_duration = self.chunk_size / self.params.framerate

            while self.playing and self.audio_position < len(self.current_audio_data) and not self.stop_event.is_set():
                try:
                    target_frame_time += frame_duration
                    current_time = time.time()
                    sleep_time = target_frame_time - current_time

                    if sleep_time > 0:
                        time.sleep(sleep_time)

                    end_pos = min(self.audio_position + chunk_bytes, len(self.current_audio_data))
                    data = self.current_audio_data[self.audio_position:end_pos]

                    if not data:
                        break

                    self.audio_queue.put(data, timeout=0.1)
                    self.audio_position = end_pos
                    frame_count += 1

                    if self.playing:
                        self.current_track_elapsed = int(frame_count * self.chunk_size / self.params.framerate)

                except queue.Full:
                    time.sleep(0.01)
                    continue
                except Exception as e:
                    self.log_message(f"Error in frame reading: {str(e)}", "error")
                    break

            if self.audio_position >= len(self.current_audio_data):
                self.log_message("Track completed", "info")
                if not self.resume_button:
                    self.play_button.config(text="▶")
                self.stop_audio()
                time.sleep(0.5)
                self.next_track()

        except Exception as e:
            self.log_message(f"Error in playback: {str(e)}", "error")
            self.playing = False
        finally:
            self.audio_thread_active = False

    def broadcast_audio_loop(self):
        """Separate thread for broadcasting audio to clients"""
        self.audio_thread_active = True
        client_error_counts = {}
        max_consecutive_errors = 5

        while self.playing and self.audio_thread_active and not self.stop_event.is_set():
            try:
                audio_data = self.audio_queue.get(timeout=0.1)

                if audio_data and self.udpclients:
                    packet = b'AUDIO' + len(audio_data).to_bytes(4, 'big') + audio_data

                    for key in list(self.udpclients.keys()):
                        oneudp = self.udpclients.get(key)
                        if self.server_socket and oneudp and oneudp.active and oneudp.addr:
                            try:
                                self.server_socket.sendto(packet, oneudp.addr)
                            except ConnectionResetError:
                                oneudp.active = False

                self.audio_queue.task_done()

            except queue.Empty:
                continue
            except Exception as e:
                self.log_message(f"Error in broadcast: {str(e)}", "error")
                break

    def load_audio_file(self, filename):
        """Load and convert audio file to standard format"""
        try:
            file_ext = os.path.splitext(filename)[1].lower()

            if file_ext == '.wav':
                with wave.open(filename, 'rb') as wf:
                    params = wf.getparams()
                    audio_data = wf.readframes(params.nframes)
                    return audio_data, params

            elif file_ext == '.mp3':
                self.log_message(f"Converting MP3: {os.path.basename(filename)}", "info")

                # If pydub is available
                # audio_segment = AudioSegment.from_mp3(filename)
                # audio_segment = audio_segment.set_frame_rate(44100)
                # audio_segment = audio_segment.set_channels(2)
                # audio_segment = audio_segment.set_sample_width(2)
                # audio_data = audio_segment.raw_data

                # For now, return error if MP3
                raise ValueError("MP3 support requires pydub library")

            else:
                raise ValueError(f"Unsupported format: {file_ext}")

        except Exception as e:
            self.log_message(f"Error loading audio: {str(e)}", "error")
            raise

    def broadcast(self, message):
        """Send a message to all connected clients"""
        for key in list(self.udpclients.keys()):
            oneudp = self.udpclients.get(key)
            if oneudp and oneudp.active and oneudp.addr:
                try:
                    self.server_socket.sendto(message, oneudp.addr)
                except ConnectionResetError:
                    oneudp.active = False

    def send_reject_token(self, addr):
        """Send login required message to client"""
        if addr:
            jsonfile = json.dumps({"type": "loginrequired"})
            packet = b'JSON' + len(jsonfile).to_bytes(4, 'big') + jsonfile.encode('utf-8')

            try:
                self.server_socket.sendto(packet, addr)
            except ConnectionResetError:
                pass

    def send_wav_parameters(self, oneudp):
        """Send audio parameters to client"""
        if oneudp and oneudp.addr and oneudp.active:
            try:
                jsonfile = json.dumps({
                    "type": "track_info",
                    "track": self.current_track if self.current_track else ""
                })
                packet = b'JSON' + len(jsonfile).to_bytes(4, 'big') + jsonfile.encode('utf-8')
                try:
                    self.server_socket.sendto(packet, oneudp.addr)
                except ConnectionResetError:
                    oneudp.active = False

                if self.playing and self.params:
                    jsonfile = json.dumps({
                        "type": "format_info",
                        "channels": self.params.nchannels,
                        "rate": self.params.framerate,
                        "format": self.sampwidth,
                        "frames": self.params.nframes,
                        "current_time": self.current_track_elapsed
                    })
                    packet = b'JSON' + len(jsonfile).to_bytes(4, 'big') + jsonfile.encode('utf-8')
                    try:
                        self.server_socket.sendto(packet, oneudp.addr)
                    except ConnectionResetError:
                        oneudp.active = False

            except Exception as e:
                self.log_message(f"Error sending parameters: {str(e)}", "error")

    def accept_clients(self):
        """Handle incoming client connections"""
        self.log_message("Waiting for client connections...", "info")

        last_check = datetime.now()

        while True:
            if self.server_socket:
                now = datetime.now()

                try:
                    data = None
                    try:
                        data, addr = self.server_socket.recvfrom(2048)
                    except ConnectionResetError:
                        pass
                    except socket.timeout:
                        pass
                    except OSError:
                        pass

                    client_list_changed = False

                    if data:
                        message = data[:4].decode('utf-8')
                        key = f"{addr[0]}:{addr[1]}"
                        udpone = self.udpclients.get(key)

                        if message.startswith("ping"):
                            index = data[4:14].decode('utf-8')
                            packed_ts = data[14:22]
                            nonce = data[14:26]
                            ciphertext = data[26:]

                            Entry = active_tokens.get(index)
                            if Entry is not None:
                                KEY = Entry.get("key")
                                if KEY is not None:
                                    aesgcm = AESGCM(KEY)

                                    try:
                                        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
                                        timestamp = struct.unpack('!d', plaintext[:8])[0]
                                        token = plaintext[8:].decode('utf-8')
                                        comparetonow = time.time()

                                        if token == Entry.get('token') and comparetonow - timestamp < 5:
                                            token_time = Entry.get('timestamp')
                                            if token_time is not None:
                                                if udpone:
                                                    udpone.active = True
                                                    udpone.lastping = datetime.now()
                                                else:
                                                    age = now - token_time
                                                    if age < timedelta(hours=self.TOKEN_VALID_HOURS):
                                                        udpone = UdpClient(active=True, addr=addr,
                                                                           lastping=datetime.now())
                                                        self.udpclients[key] = udpone
                                                        self.log_message(f"New client: {addr[0]}:{addr[1]}", "success")
                                                        self.send_wav_parameters(udpone)
                                            else:
                                                self.send_reject_token(addr)

                                            client_list_changed = True

                                    except Exception as e:
                                        pass

                        if udpone and message.startswith("quit"):
                            udpone.active = False
                            client_list_changed = True

                    if client_list_changed or now - last_check > timedelta(seconds=3):
                        last_check = now

                        for key in list(self.udpclients.keys()):
                            oneudp = self.udpclients.get(key)
                            if oneudp and (not oneudp.active or now - oneudp.lastping > timedelta(seconds=6)):
                                del self.udpclients[key]
                                self.log_message(f"Client disconnected: {oneudp.addr[0]}:{oneudp.addr[1]}", "warning")

                    self.update_client_count()

                except Exception as e:
                    if hasattr(self.server_socket, '_closed') and self.server_socket._closed:
                        break
                    self.log_message(f"Error in client handler: {str(e)}", "error")
                    break


def main():
    """Main entry point"""
    root = tk.Tk()

    # Set DPI awareness for Windows
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass

    app = ModernRadioServer(root)

    def on_closing():
        app.close_server()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Shutting down...")
        app.close_server()
        root.destroy()


if __name__ == "__main__":
    # Start login server in background
    login_server = threading.Thread(target=start_server, daemon=True)
    login_server.start()

    # Start main GUI
    main()