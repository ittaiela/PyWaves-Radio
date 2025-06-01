# 📻 PyWaves Radio - Secure Internet Radio Broadcasting System
A modern, secure internet radio broadcasting system built with Python, featuring real-time audio streaming, advanced visualization, and comprehensive security measures.
Show Image Show Image Show Image
## 🎵 Overview
PyWaves Radio is a professional-grade internet radio system that allows users to broadcast and stream high-quality audio over local networks or the internet. The system features a modern UI, real-time audio visualization, and enterprise-level security.
## Key Features
- **Real-time Audio Streaming** - Low-latency UDP broadcasting with intelligent buffering
- **Multi-client Support** - Broadcast to multiple listeners simultaneously
- **Modern UI** - Sleek, animated interface with waveform visualization
- **Drag & Drop Playlist** - Intuitive playlist management
- **Secure Authentication** - TLS/SSL encrypted login with token-based sessions
- **Cross-platform** - Works on Windows, macOS, and Linux

## 🚀 Quick Start
### Prerequisites
Python 3.12 or higher required


#### Required packages:
- **pyaudio** - Audio processing
- **numpy** - Numerical computations
- **matplotlib** - Visualization
- **cryptography** - Security features
- **bcrypt** - Password hashing

#### Installation


##### Clone the repository
`git clone https://github.com/yourusername/pywaves-radio.git
cd pywaves-radio
##### Install dependencies`
`pip install -r requirements.txt`

or 
`pip install pyaudio numpy matplotlib cryptography bcrypt`



##### Generate SSL certificates (for secure authentication)

 - PyWavesServerCert.pem
 - PyWavesServerPrivateKey.pem

## 📡 Usage
### Starting the Server
Launch the streaming server:

`python server.py`
#### The server UI will show:
- Server IP address
- Connection status
- Connected listeners count
#### Add music files:
- Click "Add Songs" button
- Select .wav files 
- Arrange playlist with drag & drop
#### Start broadcasting:
- Click "START SERVER" button
- Click "▶" (Play) to begin streaming
### Connecting as a Client
#### Launch the client:

`python client.py`
#### Login or Register:
- New users: Click "Register" and create account
- Existing users: Enter credentials
- Enter server IP address
#### Enjoy the stream:
- Adjust volume with slider
- Watch real-time audio visualization
- View current track information
## 🔒 Security Features
### Authentication & Encryption
#### 1. TLS/SSL Encrypted Login
- All authentication traffic encrypted with TLS 1.2+
- Certificate-based server verification
- Protection against man-in-the-middle attacks
#### 2. Secure Password Storage
- Passwords hashed with bcrypt (12 rounds)
- Automatic salt generation
- No plaintext passwords stored
####  3. Token-Based Sessions
- 20-character random tokens for session management
T- okens expire after 10 hours
- Unique index + AES key for each session
#### 4. AES-GCM Encrypted Heartbeat
- Ping messages encrypted with AES-128-GCM
- Prevents session hijacking
- Includes timestamp to prevent replay attacks

#### 5. DDoS Protection
- Connection rate limiting
- Automatic removal of inactive clients
- Buffer size limits to prevent memory exhaustion
#### 6. Thread Safety
- Thread-safe queues for audio data
- Proper locking mechanisms
- Graceful shutdown procedures
## 🏗️ Architecture
Network Architecture
┌─────────────┐         TLS/TCP          ┌──────────────┐
│   Client    │ ◄─────────────────────► │ Login Server │
│  (Login)    │      Authentication      │  Port 12346  │
└─────────────┘                          └──────────────┘
                                                 │
┌─────────────┐          UDP             ┌──────────────┐
│   Client    │ ◄─────────────────────► │ Radio Server │
│ (Streaming) │     Audio Streaming      │  Port 12345  │
└─────────────┘      + Encrypted Ping    └──────────────┘
Security Layers
Transport Layer - TLS for authentication, UDP for streaming
Session Layer - Token-based authentication with expiration
Application Layer - Input validation and sanitization
Data Layer - Bcrypt password hashing, AES encryption
📊 Performance
Latency: < 80ms typical
Concurrent Users: Tested up to 20 simultaneous listeners
Audio Quality: 44.1kHz, 16-bit stereo
Buffer Size: Configurable (default 8 chunks)
🛠️ Development
Project Structure
PyWavesRadio/
├── server.py          # Main radio server
├── client.py          # Client application
├── loginserver.py     # Authentication server
├── requirements.txt   # Python dependencies
├── audio/            # Audio files directory
└── certificates/     # SSL certificates
Key Technologies
Networking: Python sockets, UDP/TCP protocols
Audio: PyAudio, WAV file processing
UI: Tkinter with custom styling
Security: SSL/TLS, AES-GCM, bcrypt
Visualization: Matplotlib, NumPy FFT
📝 License
This project is licensed under the MIT License - see the LICENSE file for details.
👨‍💻 Author
Created as a final project demonstrating advanced networking, security, and audio processing concepts in Python.
🙏 Acknowledgments
Python community for excellent libraries
Stack Overflow for troubleshooting help
Contributors to PyAudio and cryptography libraries

Note: This is an educational project. For production use, consider additional security hardening and scalability improvements.

