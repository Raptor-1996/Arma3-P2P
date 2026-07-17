"""
A2M P2P Convertor
Developer : A2M (EbiRom96)
Email : EbiRom1996@gmail.com
Github : EbiRom96
Version : 6.0.0
Description : Professional PAA ↔ PNG converter for Arma 3
"""

import sys
import os
import json
import shutil
import subprocess
import tempfile
import struct
from pathlib import Path
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PIL import Image, ImageOps

# ==================== Constants ====================
APP_NAME = "A2M P2P Convertor"
APP_VERSION = "6.0.0"
DEVELOPER = "A2M (EbiRom96)"
EMAIL = "EbiRom1996@gmail.com"
GITHUB = "EbiRom96"
DESCRIPTION = "Professional PAA ↔ PNG converter for Arma 3 modding"
DOCS_PATH = Path(os.path.expanduser("~/Documents/A2M_P2P"))
LOGS_PATH = DOCS_PATH / "Logs"
CONFIG_PATH = DOCS_PATH / "config.hpp"

# ==================== Logger ====================
class Logger:
    def __init__(self):
        self.log_file = None
        self.setup_logging()
    
    def setup_logging(self):
        try:
            LOGS_PATH.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.log_file = LOGS_PATH / f"log_{timestamp}.log"
            
            with open(self.log_file, 'w') as f:
                f.write(f"=== A2M P2P Convertor Log ===\n")
                f.write(f"Version: {APP_VERSION}\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 50 + "\n\n")
        except Exception as e:
            print(f"Failed to setup logging: {e}")
    
    def log(self, message, level="INFO"):
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] [{level}] {message}\n"
            
            if self.log_file:
                with open(self.log_file, 'a') as f:
                    f.write(log_entry)
            
            print(log_entry.strip())
        except Exception as e:
            print(f"Logging error: {e}")
    
    def info(self, message):
        self.log(message, "INFO")
    
    def error(self, message):
        self.log(message, "ERROR")
    
    def warning(self, message):
        self.log(message, "WARNING")
    
    def success(self, message):
        self.log(message, "SUCCESS")

# ==================== Splash Screen ====================
class SplashScreen(QSplashScreen):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.counter = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_splash)
        self.timer.start(30)
    
    def setup_ui(self):
        splash_pixmap = QPixmap(700, 500)
        splash_pixmap.fill(QColor(10, 10, 15))
        
        painter = QPainter(splash_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        
        # Dark gradient background
        gradient = QLinearGradient(0, 0, 700, 500)
        gradient.setColorAt(0, QColor(15, 15, 25))
        gradient.setColorAt(0.5, QColor(20, 20, 30))
        gradient.setColorAt(1, QColor(10, 10, 20))
        painter.fillRect(splash_pixmap.rect(), gradient)
        
        # Animated border glow
        painter.setPen(QPen(QColor(255, 0, 0, 150), 3))
        painter.drawRoundedRect(10, 10, 680, 480, 15, 15)
        
        # Logo
        try:
            logo_path = Path("p2p_logo.png")
            if logo_path.exists():
                logo = QPixmap(str(logo_path))
                if not logo.isNull():
                    logo = logo.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    painter.drawPixmap(275, 50, logo)
        except:
            pass
        
        # Title with glow effect
        title_font = QFont("Segoe UI", 32, QFont.Bold)
        painter.setFont(title_font)
        
        # Title shadow
        painter.setPen(QPen(QColor(255, 0, 0, 50)))
        painter.drawText(QRect(2, 222, 700, 50), Qt.AlignCenter, APP_NAME)
        
        # Title main
        painter.setPen(QPen(QColor(0, 150, 255)))
        painter.drawText(QRect(0, 220, 700, 50), Qt.AlignCenter, APP_NAME)
        
        # Description
        desc_font = QFont("Segoe UI", 12)
        painter.setFont(desc_font)
        painter.setPen(QPen(QColor(150, 150, 180)))
        painter.drawText(QRect(0, 280, 700, 30), Qt.AlignCenter, DESCRIPTION)
        
        # Version
        version_font = QFont("Segoe UI", 10)
        painter.setFont(version_font)
        painter.setPen(QPen(QColor(100, 100, 130)))
        painter.drawText(QRect(0, 320, 700, 25), Qt.AlignCenter, f"Version {APP_VERSION}")
        
        # Developer info
        dev_font = QFont("Segoe UI", 9)
        painter.setFont(dev_font)
        painter.setPen(QPen(QColor(80, 80, 110)))
        painter.drawText(QRect(0, 360, 700, 20), Qt.AlignCenter, f"Developer: {DEVELOPER}")
        painter.drawText(QRect(0, 380, 700, 20), Qt.AlignCenter, f"GitHub: {GITHUB}")
        painter.drawText(QRect(0, 400, 700, 20), Qt.AlignCenter, f"Email: {EMAIL}")
        
        # Loading bar
        self.progress_rect = QRect(150, 440, 400, 8)
        painter.setPen(QPen(QColor(255, 0, 0, 80), 2))
        painter.drawRoundedRect(self.progress_rect, 4, 4)
        
        # Initial progress
        self.progress_value = 0
        
        painter.end()
        
        self.setPixmap(splash_pixmap)
        self.show()
        QApplication.processEvents()
    
    def update_splash(self):
        self.counter += 1
        self.progress_value = min(100, self.progress_value + 2)
        
        pixmap = self.pixmap()
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Animated border
        color_value = int(abs(127 * (self.counter % 60 - 30) / 30))
        red = 255 - color_value
        blue = 150 + color_value
        
        border_color = QColor(red, 0, blue, 180)
        painter.setPen(QPen(border_color, 3))
        painter.drawRoundedRect(10, 10, 680, 480, 15, 15)
        
        # Update progress bar
        painter.setPen(QPen(QColor(255, 0, 0, 80), 2))
        painter.drawRoundedRect(self.progress_rect, 4, 4)
        
        progress_width = int(self.progress_rect.width() * self.progress_value / 100)
        progress_rect = QRect(self.progress_rect.x(), self.progress_rect.y(),
                             progress_width, self.progress_rect.height())
        
        gradient = QLinearGradient(progress_rect.topLeft(), progress_rect.topRight())
        gradient.setColorAt(0, QColor(255, 0, 0))
        gradient.setColorAt(0.5, QColor(0, 150, 255))
        gradient.setColorAt(1, QColor(255, 0, 0))
        painter.fillRect(progress_rect, gradient)
        
        painter.end()
        self.setPixmap(pixmap)
        self.repaint()
        
        if self.progress_value >= 100:
            self.timer.stop()
            QTimer.singleShot(500, self.finish_splash)
    
    def finish_splash(self):
        self.close()
        
        # Try to find tools automatically
        tools = self.find_tools()
        
        if tools:
            try:
                DOCS_PATH.mkdir(parents=True, exist_ok=True)
                with open(CONFIG_PATH, 'w') as f:
                    f.write("// A2M P2P Convertor Configuration\n")
                    f.write(f"// Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    for key, value in tools.items():
                        f.write(f'{key} = "{value}"\n')
            except:
                pass
        
        if not CONFIG_PATH.exists():
            self.config_dialog = ConfigDialog()
            self.config_dialog.show()
        else:
            self.main_window = MainWindow()
            self.main_window.show()
    
    def find_tools(self):
        """Find Arma 3 tools automatically"""
        tools = {}
        
        possible_paths = [
            r"D:\SteamLibrary\steamapps\common\Arma 3 Tools",
            r"C:\Program Files (x86)\Steam\steamapps\common\Arma 3 Tools",
            r"E:\SteamLibrary\steamapps\common\Arma 3 Tools",
            r"D:\Steam\steamapps\common\Arma 3 Tools",
            r"C:\Steam\steamapps\common\Arma 3 Tools",
        ]
        
        for base_path in possible_paths:
            if not os.path.exists(base_path):
                continue
            
            # TexView2
            tex_paths = [
                os.path.join(base_path, "TexView2", "TexView2.exe"),
                os.path.join(base_path, "TexView2.exe"),
                os.path.join(base_path, "Bin", "TexView2.exe"),
            ]
            for path in tex_paths:
                if os.path.exists(path):
                    tools["TexView2"] = path
                    break
            
            # ImageToPAA
            img_paths = [
                os.path.join(base_path, "ImageToPAA", "ImageToPAA.exe"),
                os.path.join(base_path, "ImageToPAA.exe"),
                os.path.join(base_path, "Bin", "ImageToPAA.exe"),
            ]
            for path in img_paths:
                if os.path.exists(path):
                    tools["ImageToPAA"] = path
                    break
        
        return tools

# ==================== Configuration Dialog ====================
class ConfigDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.logger = Logger()
        self.setup_ui()
        self.load_existing_config()
    
    def setup_ui(self):
        self.setWindowTitle("A2M P2P - First Time Setup")
        self.setFixedSize(750, 600)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #121216;
                border: 3px solid #ff0000;
                border-radius: 15px;
            }
            QLabel {
                color: #c0c0d0;
                font-family: Segoe UI;
            }
            QLineEdit {
                background-color: #1a1a24;
                border: 2px solid #ff0000;
                border-radius: 8px;
                color: #ffffff;
                padding: 10px 12px;
                font-family: Segoe UI;
                font-size: 12px;
                min-height: 20px;
            }
            QLineEdit:focus {
                border: 2px solid #00aaff;
                box-shadow: 0 0 20px rgba(0, 170, 255, 0.3);
            }
            QPushButton {
                background-color: #2a2a34;
                border: 2px solid #ff0000;
                border-radius: 8px;
                color: #ffffff;
                padding: 10px 25px;
                font-weight: bold;
                font-size: 12px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #3a3a44;
                border: 2px solid #00aaff;
                box-shadow: 0 0 25px rgba(0, 170, 255, 0.3);
            }
            QPushButton#close_btn {
                background-color: transparent;
                border: none;
                color: #666688;
                font-size: 18px;
                padding: 5px 10px;
                min-height: 20px;
            }
            QPushButton#close_btn:hover {
                color: #ff3333;
                background-color: transparent;
            }
        """)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(25, 25, 25, 25)
        
        # Title bar
        title_bar = QWidget()
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel("⚙️ First Time Setup")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #00aaff;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        close_btn = QPushButton("✕")
        close_btn.setObjectName("close_btn")
        close_btn.clicked.connect(self.reject)
        title_layout.addWidget(close_btn)
        
        title_bar.setLayout(title_layout)
        main_layout.addWidget(title_bar)
        
        desc_label = QLabel("Please select the paths to Arma 3 Tools")
        desc_label.setStyleSheet("font-size: 12px; color: #8888aa; margin-bottom: 10px;")
        main_layout.addWidget(desc_label)
        
        # ImageToPAA path
        container1 = QWidget()
        container1_layout = QVBoxLayout()
        container1_layout.setSpacing(5)
        
        label1 = QLabel("📁 ImageToPAA:")
        label1.setStyleSheet("color: #00aaff; font-weight: bold; font-size: 12px;")
        container1_layout.addWidget(label1)
        
        input_container1 = QWidget()
        input_layout1 = QHBoxLayout()
        input_layout1.setContentsMargins(0, 0, 0, 0)
        input_layout1.setSpacing(8)
        
        self.imagetopaa_path = QLineEdit()
        self.imagetopaa_path.setPlaceholderText("Browse to ImageToPAA.exe")
        input_layout1.addWidget(self.imagetopaa_path)
        
        browse_btn1 = QPushButton("📂 Browse")
        browse_btn1.setFixedWidth(100)
        browse_btn1.clicked.connect(lambda: self.browse_path("ImageToPAA"))
        input_layout1.addWidget(browse_btn1)
        
        input_container1.setLayout(input_layout1)
        container1_layout.addWidget(input_container1)
        container1.setLayout(container1_layout)
        main_layout.addWidget(container1)
        
        # TexView2 path
        container2 = QWidget()
        container2_layout = QVBoxLayout()
        container2_layout.setSpacing(5)
        
        label2 = QLabel("📁 TexView2:")
        label2.setStyleSheet("color: #00aaff; font-weight: bold; font-size: 12px;")
        container2_layout.addWidget(label2)
        
        input_container2 = QWidget()
        input_layout2 = QHBoxLayout()
        input_layout2.setContentsMargins(0, 0, 0, 0)
        input_layout2.setSpacing(8)
        
        self.texview_path = QLineEdit()
        self.texview_path.setPlaceholderText("Browse to TexView2.exe")
        input_layout2.addWidget(self.texview_path)
        
        browse_btn2 = QPushButton("📂 Browse")
        browse_btn2.setFixedWidth(100)
        browse_btn2.clicked.connect(lambda: self.browse_path("TexView2"))
        input_layout2.addWidget(browse_btn2)
        
        input_container2.setLayout(input_layout2)
        container2_layout.addWidget(input_container2)
        container2.setLayout(container2_layout)
        main_layout.addWidget(container2)
        
        # Validation
        validation_layout = QHBoxLayout()
        validation_layout.setSpacing(15)
        
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #8888aa; font-size: 11px;")
        validation_layout.addWidget(self.status_label)
        validation_layout.addStretch()
        
        main_layout.addLayout(validation_layout)
        
        # Action buttons
        action_layout = QHBoxLayout()
        action_layout.addStretch()
        
        save_btn = QPushButton("💾 Save & Continue")
        save_btn.clicked.connect(self.save_config)
        action_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(self.reject)
        action_layout.addWidget(cancel_btn)
        
        main_layout.addLayout(action_layout)
        self.setLayout(main_layout)
    
    def load_existing_config(self):
        if CONFIG_PATH.exists():
            try:
                with open(CONFIG_PATH, 'r') as f:
                    config_data = f.read()
                
                for line in config_data.split('\n'):
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        if key.strip() == "ImageToPAA":
                            self.imagetopaa_path.setText(value.strip().strip('"'))
                        elif key.strip() == "TexView2":
                            self.texview_path.setText(value.strip().strip('"'))
            except:
                pass
    
    def browse_path(self, tool_name):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Select {tool_name}.exe",
            "C:/",
            "Executable Files (*.exe);;All Files (*)"
        )
        if file_path:
            if tool_name == "ImageToPAA":
                self.imagetopaa_path.setText(file_path)
            else:
                self.texview_path.setText(file_path)
    
    def save_config(self):
        img_path = Path(self.imagetopaa_path.text().strip())
        tex_path = Path(self.texview_path.text().strip())
        
        if not img_path.exists() and not tex_path.exists():
            QMessageBox.warning(self, "No Tools Found", 
                               "Please select at least one tool (ImageToPAA or TexView2)")
            return
        
        try:
            DOCS_PATH.mkdir(parents=True, exist_ok=True)
            
            with open(CONFIG_PATH, 'w') as f:
                f.write("// A2M P2P Convertor Configuration\n")
                f.write(f"// Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                if img_path.exists():
                    f.write(f'ImageToPAA = "{self.imagetopaa_path.text().strip()}"\n')
                if tex_path.exists():
                    f.write(f'TexView2 = "{self.texview_path.text().strip()}"\n')
            
            self.logger.success("Configuration saved successfully")
            self.accept()
            
            self.main_window = MainWindow()
            self.main_window.show()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save configuration: {str(e)}")

# ==================== Converter Worker ====================
class ConverterWorker(QThread):
    progress_updated = pyqtSignal(int)
    log_updated = pyqtSignal(str, str)
    finished = pyqtSignal(int, int)
    
    def __init__(self, files, config, output_path, prefix, suffix, mode):
        super().__init__()
        self.files = files
        self.config = config
        self.output_path = output_path
        self.prefix = prefix
        self.suffix = suffix
        self.mode = mode  # "paa_to_png" or "png_to_paa"
        self.is_running = True
    
    def run(self):
        total = len(self.files)
        success_count = 0
        error_count = 0
        
        for i, file_path in enumerate(self.files):
            if not self.is_running:
                break
            
            try:
                self.log_updated.emit(f"Processing: {os.path.basename(file_path)}", "INFO")
                
                if self.mode == "paa_to_png":
                    img = self.convert_paa_to_png(file_path)
                    if img is None:
                        raise Exception("Could not convert PAA to image")
                    
                    # Save as PNG
                    output_dir = Path(self.output_path) if self.output_path else Path(file_path).parent
                    base_name = Path(file_path).stem
                    new_name = f"{self.prefix}{base_name}{self.suffix}.png" if (self.prefix or self.suffix) else f"{base_name}.png"
                    output_file = output_dir / new_name
                    img.save(str(output_file), "PNG")
                    success_count += 1
                    self.log_updated.emit(f"✅ Converted: {os.path.basename(file_path)} → {new_name}", "SUCCESS")
                    
                else:  # png_to_paa
                    paa_data = self.convert_png_to_paa(file_path)
                    if paa_data is None:
                        raise Exception("Could not convert PNG to PAA")
                    
                    # Save as PAA
                    output_dir = Path(self.output_path) if self.output_path else Path(file_path).parent
                    base_name = Path(file_path).stem
                    new_name = f"{self.prefix}{base_name}{self.suffix}.paa" if (self.prefix or self.suffix) else f"{base_name}.paa"
                    output_file = output_dir / new_name
                    with open(output_file, 'wb') as f:
                        f.write(paa_data)
                    success_count += 1
                    self.log_updated.emit(f"✅ Converted: {os.path.basename(file_path)} → {new_name}", "SUCCESS")
                
            except Exception as e:
                error_count += 1
                self.log_updated.emit(f"❌ Failed: {os.path.basename(file_path)} - {str(e)}", "ERROR")
            
            self.progress_updated.emit(int((i + 1) / total * 100))
        
        self.finished.emit(success_count, error_count)
    
    def convert_paa_to_png(self, paa_path):
        """Convert PAA to PNG using multiple methods"""
        
        # Method 1: TexView2
        if "TexView2" in self.config:
            try:
                img = self.convert_with_texview(paa_path)
                if img is not None:
                    self.log_updated.emit("✅ Converted with TexView2", "SUCCESS")
                    return img
            except Exception as e:
                self.log_updated.emit(f"⚠️ TexView2 failed: {str(e)}", "WARNING")
        
        # Method 2: ImageToPAA
        if "ImageToPAA" in self.config:
            try:
                img = self.convert_with_imagetopaa(paa_path)
                if img is not None:
                    self.log_updated.emit("✅ Converted with ImageToPAA", "SUCCESS")
                    return img
            except Exception as e:
                self.log_updated.emit(f"⚠️ ImageToPAA failed: {str(e)}", "WARNING")
        
        # Method 3: PIL fallback
        try:
            img = self.convert_with_pil(paa_path)
            if img is not None:
                self.log_updated.emit("✅ Converted with PIL fallback", "SUCCESS")
                return img
        except Exception as e:
            self.log_updated.emit(f"⚠️ PIL fallback failed: {str(e)}", "WARNING")
        
        raise Exception("All conversion methods failed")
    
    def convert_png_to_paa(self, png_path):
        """Convert PNG to PAA using ImageToPAA"""
        
        # Method 1: ImageToPAA
        if "ImageToPAA" in self.config:
            try:
                paa_data = self.convert_with_imagetopaa_png_to_paa(png_path)
                if paa_data is not None:
                    self.log_updated.emit("✅ Converted with ImageToPAA", "SUCCESS")
                    return paa_data
            except Exception as e:
                self.log_updated.emit(f"⚠️ ImageToPAA failed: {str(e)}", "WARNING")
        
        raise Exception("PNG to PAA conversion failed - ImageToPAA required")
    
    def convert_with_texview(self, paa_path):
        """Convert using TexView2 - HIDDEN WINDOW"""
        try:
            texview_path = self.config["TexView2"]
            temp_dir = tempfile.mkdtemp()
            temp_png = os.path.join(temp_dir, "temp.png")
            
            cmd = [texview_path, "-export", "png", paa_path, temp_png]
            
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if os.path.exists(temp_png) and os.path.getsize(temp_png) > 0:
                img = Image.open(temp_png)
                try:
                    os.remove(temp_png)
                    os.rmdir(temp_dir)
                except:
                    pass
                return img
            
            # Try alternative format
            cmd2 = [texview_path, "-export=PNG", paa_path, temp_png]
            result2 = subprocess.run(
                cmd2,
                capture_output=True,
                text=True,
                timeout=30,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if os.path.exists(temp_png) and os.path.getsize(temp_png) > 0:
                img = Image.open(temp_png)
                try:
                    os.remove(temp_png)
                    os.rmdir(temp_dir)
                except:
                    pass
                return img
            
            raise Exception("TexView2 did not create output file")
            
        except Exception as e:
            raise Exception(f"TexView2 error: {str(e)}")
    
    def convert_with_imagetopaa(self, paa_path):
        """Convert using ImageToPAA - HIDDEN WINDOW"""
        try:
            imagetopaa_path = self.config["ImageToPAA"]
            temp_dir = tempfile.mkdtemp()
            temp_png = os.path.join(temp_dir, "temp.png")
            
            commands = [
                [imagetopaa_path, "-t", "png", "-i", paa_path, "-o", temp_png],
                [imagetopaa_path, "-t", "png", "--input", paa_path, "--output", temp_png],
                [imagetopaa_path, "-convert", paa_path, temp_png],
                [imagetopaa_path, paa_path, temp_png],
            ]
            
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            for cmd in commands:
                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=30,
                        startupinfo=startupinfo,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    
                    if os.path.exists(temp_png) and os.path.getsize(temp_png) > 0:
                        img = Image.open(temp_png)
                        try:
                            os.remove(temp_png)
                            os.rmdir(temp_dir)
                        except:
                            pass
                        return img
                except:
                    continue
            
            raise Exception("All ImageToPAA commands failed")
            
        except Exception as e:
            raise Exception(f"ImageToPAA error: {str(e)}")
    
    def convert_with_imagetopaa_png_to_paa(self, png_path):
        """Convert PNG to PAA using ImageToPAA"""
        try:
            imagetopaa_path = self.config["ImageToPAA"]
            temp_dir = tempfile.mkdtemp()
            temp_paa = os.path.join(temp_dir, "temp.paa")
            
            commands = [
                [imagetopaa_path, "-t", "paa", "-i", png_path, "-o", temp_paa],
                [imagetopaa_path, "-t", "paa", "--input", png_path, "--output", temp_paa],
                [imagetopaa_path, "-convert", png_path, temp_paa],
                [imagetopaa_path, png_path, temp_paa],
            ]
            
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            for cmd in commands:
                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=30,
                        startupinfo=startupinfo,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    
                    if os.path.exists(temp_paa) and os.path.getsize(temp_paa) > 0:
                        with open(temp_paa, 'rb') as f:
                            data = f.read()
                        try:
                            os.remove(temp_paa)
                            os.rmdir(temp_dir)
                        except:
                            pass
                        return data
                except:
                    continue
            
            raise Exception("All ImageToPAA commands failed")
            
        except Exception as e:
            raise Exception(f"ImageToPAA error: {str(e)}")
    
    def convert_with_pil(self, paa_path):
        """Convert using PIL fallback"""
        try:
            img = Image.open(paa_path)
            if img.mode == 'P':
                img = img.convert('RGB')
            elif img.mode == 'RGBA':
                pass
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            return img
        except Exception as e:
            raise Exception(f"PIL parsing failed: {str(e)}")

# ==================== Main Window ====================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logger = Logger()
        self.files_to_convert = []
        self.output_path = None
        self.config = {}
        self.worker = None
        self.border_animation = None
        self.setup_ui()
        self.load_config()
        self.start_border_animation()
        self.set_window_icon()
        self.logger.info("Main window initialized")
    
    def set_window_icon(self):
        """Set window icon for both window and taskbar"""
        icon_path = Path("p2p_icon.ico")
        if icon_path.exists():
            icon = QIcon(str(icon_path))
            self.setWindowIcon(icon)
            
            # Force taskbar icon update on Windows
            if sys.platform == 'win32':
                try:
                    import ctypes
                    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("A2M.P2P.Convertor.6.0")
                    
                    # Force window icon update
                    hwnd = int(self.winId())
                    ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 0, icon.pixmap(32, 32).toWinHBITMAP())
                    ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 1, icon.pixmap(256, 256).toWinHBITMAP())
                    ctypes.windll.user32.SetWindowPos(hwnd, None, 0, 0, 0, 0, 0x0001)
                except:
                    pass
    
    def setup_ui(self):
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(950, 800)
        
        # Central widget
        central_widget = QWidget()
        central_widget.setStyleSheet("""
            QWidget {
                background-color: #0a0a0e;
                color: #c0c0d0;
                font-family: Segoe UI;
                border: 2px solid #1a1a2a;
                border-radius: 15px;
            }
            QMainWindow {
                background-color: #0a0a0e;
            }
        """)
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(25, 25, 25, 25)
        
        # ===== HEADER =====
        header_widget = QWidget()
        header_widget.setStyleSheet("background-color: transparent; padding: 5px 0px;")
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(15)
        
        # Logo
        try:
            logo_path = Path("p2p_logo.png")
            if logo_path.exists():
                logo_pixmap = QPixmap(str(logo_path))
                if not logo_pixmap.isNull():
                    logo_label = QLabel()
                    logo_pixmap = logo_pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    logo_label.setPixmap(logo_pixmap)
                    logo_label.setStyleSheet("background-color: transparent;")
                    header_layout.addWidget(logo_label)
        except:
            pass
        
        title_label = QLabel(f"{APP_NAME}")
        title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #00aaff;
            background-color: transparent;
        """)
        header_layout.addWidget(title_label)
        
        version_label = QLabel(f"v{APP_VERSION}")
        version_label.setStyleSheet("""
            color: #666688;
            font-size: 14px;
            background-color: transparent;
            margin-top: 8px;
        """)
        header_layout.addWidget(version_label)
        
        header_layout.addStretch()
        
        dev_label = QLabel(f"Dev: {DEVELOPER}")
        dev_label.setStyleSheet("""
            color: #444466;
            font-size: 11px;
            background-color: transparent;
        """)
        header_layout.addWidget(dev_label)
        
        header_widget.setLayout(header_layout)
        main_layout.addWidget(header_widget)
        
        # ===== CONVERSION MODE =====
        mode_widget = QWidget()
        mode_widget.setStyleSheet("""
            QWidget {
                background-color: #12121a;
                border: 2px solid #1a1a2a;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(15)
        
        mode_label = QLabel("🔄 Conversion Mode:")
        mode_label.setStyleSheet("color: #00aaff; font-weight: bold; font-size: 13px;")
        mode_layout.addWidget(mode_label)
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["PAA → PNG", "PNG → PAA"])
        self.mode_combo.setStyleSheet("""
            QComboBox {
                background-color: #1a1a26;
                border: 2px solid #00aaff;
                border-radius: 8px;
                color: #ffffff;
                padding: 8px 15px;
                font-size: 13px;
                font-weight: bold;
                min-width: 150px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
            }
            QComboBox QAbstractItemView {
                background-color: #1a1a26;
                border: 2px solid #00aaff;
                color: #ffffff;
                selection-background-color: #003366;
            }
        """)
        self.mode_combo.currentTextChanged.connect(self.update_mode)
        mode_layout.addWidget(self.mode_combo)
        
        self.mode_info_label = QLabel("📌 Convert PAA files to PNG format")
        self.mode_info_label.setStyleSheet("color: #8888aa; font-size: 12px;")
        mode_layout.addWidget(self.mode_info_label)
        
        mode_layout.addStretch()
        mode_widget.setLayout(mode_layout)
        main_layout.addWidget(mode_widget)
        
        # ===== BUTTON PANEL =====
        button_panel = QWidget()
        button_panel.setStyleSheet("""
            QWidget {
                background-color: #12121a;
                border: 2px solid #1a1a2a;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        add_files_btn = QPushButton("📄 Add Files")
        add_files_btn.clicked.connect(self.add_files)
        add_files_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a1a26;
                border: 2px solid #00aaff;
                border-radius: 8px;
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 25px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #2a2a3a;
                border: 2px solid #ff0000;
                box-shadow: 0 0 20px rgba(0, 170, 255, 0.2);
            }
        """)
        button_layout.addWidget(add_files_btn)
        
        add_dir_btn = QPushButton("📁 Add Directory")
        add_dir_btn.clicked.connect(self.add_directory)
        add_dir_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a1a26;
                border: 2px solid #00aaff;
                border-radius: 8px;
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 25px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #2a2a3a;
                border: 2px solid #ff0000;
                box-shadow: 0 0 20px rgba(0, 170, 255, 0.2);
            }
        """)
        button_layout.addWidget(add_dir_btn)
        
        clear_btn = QPushButton("🗑️ Clear")
        clear_btn.clicked.connect(self.clear_files)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a1a26;
                border: 2px solid #ff3333;
                border-radius: 8px;
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 25px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #2a1a1a;
                border: 2px solid #ff0000;
                box-shadow: 0 0 20px rgba(255, 0, 0, 0.2);
            }
        """)
        button_layout.addWidget(clear_btn)
        
        button_layout.addStretch()
        
        self.file_count_label = QLabel("Files: 0")
        self.file_count_label.setStyleSheet("color: #666688; font-size: 12px;")
        button_layout.addWidget(self.file_count_label)
        
        button_panel.setLayout(button_layout)
        main_layout.addWidget(button_panel)
        
        # ===== FILE LIST =====
        self.file_list = QListWidget()
        self.file_list.setStyleSheet("""
            QListWidget {
                background-color: #12121a;
                border: 2px solid #1a1a2a;
                border-radius: 10px;
                color: #c0c0d0;
                padding: 8px;
                min-height: 150px;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #1a1a2a;
                border-radius: 5px;
            }
            QListWidget::item:hover {
                background-color: #1a1a2a;
            }
            QListWidget::item:selected {
                background-color: #1a2a3a;
                border: 1px solid #00aaff;
            }
        """)
        main_layout.addWidget(self.file_list)
        
        # ===== OPTIONS =====
        options_widget = QWidget()
        options_widget.setStyleSheet("""
            QWidget {
                background-color: #12121a;
                border: 2px solid #1a1a2a;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        options_layout = QHBoxLayout()
        options_layout.setSpacing(15)
        
        # Same as source checkbox
        self.same_as_source = QCheckBox("Same as source")
        self.same_as_source.setChecked(True)
        self.same_as_source.setStyleSheet("""
            QCheckBox {
                color: #c0c0d0;
                font-size: 13px;
                font-weight: bold;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #ff0000;
                border-radius: 5px;
                background-color: #12121a;
            }
            QCheckBox::indicator:checked {
                background-color: #00aaff;
                border: 2px solid #00aaff;
            }
            QCheckBox::indicator:hover {
                border: 2px solid #00aaff;
                box-shadow: 0 0 15px rgba(0, 170, 255, 0.2);
            }
        """)
        self.same_as_source.toggled.connect(self.toggle_output_path)
        options_layout.addWidget(self.same_as_source)
        
        # Output path
        self.output_path_widget = QWidget()
        self.output_path_widget.setVisible(False)
        output_layout = QHBoxLayout()
        output_layout.setContentsMargins(0, 0, 0, 0)
        output_layout.setSpacing(8)
        
        self.output_path_input = QLineEdit()
        self.output_path_input.setPlaceholderText("Select output directory...")
        self.output_path_input.setStyleSheet("""
            QLineEdit {
                background-color: #0a0a12;
                border: 2px solid #00aaff;
                border-radius: 8px;
                color: #ffffff;
                padding: 10px 12px;
                font-size: 12px;
                min-height: 20px;
                min-width: 300px;
            }
            QLineEdit:focus {
                border: 2px solid #ff0000;
                box-shadow: 0 0 20px rgba(255, 0, 0, 0.2);
            }
        """)
        output_layout.addWidget(self.output_path_input)
        
        browse_output_btn = QPushButton("Browse")
        browse_output_btn.clicked.connect(self.browse_output)
        browse_output_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a1a26;
                border: 2px solid #00aaff;
                border-radius: 8px;
                color: #ffffff;
                padding: 10px 20px;
                font-weight: bold;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #2a2a3a;
                border: 2px solid #ff0000;
                box-shadow: 0 0 20px rgba(0, 170, 255, 0.2);
            }
        """)
        output_layout.addWidget(browse_output_btn)
        
        self.output_path_widget.setLayout(output_layout)
        options_layout.addWidget(self.output_path_widget)
        
        options_layout.addStretch()
        
        # Prefix and suffix
        prefix_label = QLabel("Prefix:")
        prefix_label.setStyleSheet("color: #8888aa; font-weight: bold;")
        options_layout.addWidget(prefix_label)
        
        self.prefix_input = QLineEdit()
        self.prefix_input.setPlaceholderText("prefix")
        self.prefix_input.setFixedWidth(120)
        self.prefix_input.setStyleSheet("""
            QLineEdit {
                background-color: #0a0a12;
                border: 2px solid #1a1a2a;
                border-radius: 8px;
                color: #ffffff;
                padding: 8px 12px;
                font-size: 12px;
                min-height: 20px;
            }
            QLineEdit:focus {
                border: 2px solid #00aaff;
                box-shadow: 0 0 15px rgba(0, 170, 255, 0.2);
            }
        """)
        options_layout.addWidget(self.prefix_input)
        
        suffix_label = QLabel("Suffix:")
        suffix_label.setStyleSheet("color: #8888aa; font-weight: bold;")
        options_layout.addWidget(suffix_label)
        
        self.suffix_input = QLineEdit()
        self.suffix_input.setPlaceholderText("suffix")
        self.suffix_input.setFixedWidth(120)
        self.suffix_input.setStyleSheet("""
            QLineEdit {
                background-color: #0a0a12;
                border: 2px solid #1a1a2a;
                border-radius: 8px;
                color: #ffffff;
                padding: 8px 12px;
                font-size: 12px;
                min-height: 20px;
            }
            QLineEdit:focus {
                border: 2px solid #00aaff;
                box-shadow: 0 0 15px rgba(0, 170, 255, 0.2);
            }
        """)
        options_layout.addWidget(self.suffix_input)
        
        options_widget.setLayout(options_layout)
        main_layout.addWidget(options_widget)
        
        # ===== CONVERT BUTTON =====
        self.convert_btn = QPushButton("🚀 Start Conversion")
        self.convert_btn.clicked.connect(self.convert_files)
        self.convert_btn.setStyleSheet("""
            QPushButton {
                background-color: #003366;
                border: 3px solid #00aaff;
                border-radius: 12px;
                color: #ffffff;
                font-size: 18px;
                font-weight: bold;
                padding: 15px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #004488;
                border: 3px solid #ff0000;
                box-shadow: 0 0 40px rgba(0, 170, 255, 0.3);
            }
            QPushButton:pressed {
                background-color: #002244;
            }
            QPushButton:disabled {
                background-color: #1a1a2a;
                border: 3px solid #444466;
                color: #666688;
            }
        """)
        main_layout.addWidget(self.convert_btn)
        
        # ===== PROGRESS BAR =====
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #12121a;
                border: 2px solid #ff0000;
                border-radius: 12px;
                height: 30px;
                text-align: center;
                color: #ffffff;
                font-weight: bold;
                font-size: 13px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff0000, stop:0.3 #ff4400, stop:0.6 #00aaff, stop:0.8 #0044ff, stop:1 #ff0000);
                border-radius: 10px;
            }
        """)
        main_layout.addWidget(self.progress_bar)
        
        # ===== LOG AREA =====
        log_label = QLabel("📋 Log:")
        log_label.setStyleSheet("color: #8888aa; font-weight: bold; margin-top: 5px; font-size: 13px;")
        main_layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #0a0a10;
                border: 2px solid #1a1a2a;
                border-radius: 10px;
                color: #00ff88;
                font-family: Consolas, monospace;
                font-size: 11px;
                padding: 12px;
                min-height: 150px;
            }
        """)
        main_layout.addWidget(self.log_text)
        
        # Status bar
        self.statusBar().setStyleSheet("""
            QStatusBar {
                background-color: #12121a;
                color: #666688;
                border-top: 1px solid #1a1a2a;
                padding: 5px;
                font-size: 12px;
            }
        """)
        self.statusBar().showMessage("Ready")
        
        central_widget.setLayout(main_layout)
        
        # Log initial message
        self.add_log("A2M P2P Convertor v6.0 started successfully", "INFO")
        self.add_log(f"Developer: {DEVELOPER}", "INFO")
        self.add_log(f"GitHub: {GITHUB}", "INFO")
    
    def update_mode(self, mode_text):
        """Update mode info label"""
        if "PAA → PNG" in mode_text:
            self.mode_info_label.setText("📌 Convert PAA files to PNG format")
            self.add_log("Switched to PAA → PNG mode", "INFO")
        else:
            self.mode_info_label.setText("📌 Convert PNG files to PAA format")
            self.add_log("Switched to PNG → PAA mode", "INFO")
        
        # Update file list extensions
        self.update_file_list_display()
    
    def update_file_list_display(self):
        """Update file list display based on mode"""
        # Just refresh the list display
        current_files = []
        for i in range(self.file_list.count()):
            current_files.append(self.file_list.item(i).text())
        
        # Update extension display
        mode = self.mode_combo.currentText()
        if "PAA → PNG" in mode:
            self.file_count_label.setText(f"Files: {len(self.files_to_convert)}")
        else:
            self.file_count_label.setText(f"Files: {len(self.files_to_convert)}")
    
    def start_border_animation(self):
        """Start animated border for main window"""
        self.border_animation = QVariantAnimation()
        self.border_animation.setDuration(3000)
        self.border_animation.setStartValue(0.0)
        self.border_animation.setEndValue(1.0)
        self.border_animation.valueChanged.connect(self.update_border)
        self.border_animation.setLoopCount(-1)
        self.border_animation.start()
    
    def update_border(self, value):
        """Update main window border color"""
        import math
        angle = value * 2 * math.pi
        
        red = int(255 * (0.5 + 0.5 * math.cos(angle)))
        blue = int(255 * (0.5 + 0.5 * math.sin(angle)))
        
        self.centralWidget().setStyleSheet(f"""
            QWidget {{
                background-color: #0a0a0e;
                color: #c0c0d0;
                font-family: Segoe UI;
                border: 2px solid rgb({red}, 0, {blue});
                border-radius: 15px;
            }}
            QMainWindow {{
                background-color: #0a0a0e;
            }}
        """)
    
    def load_config(self):
        """Load configuration"""
        try:
            if CONFIG_PATH.exists():
                with open(CONFIG_PATH, 'r') as f:
                    config_data = f.read()
                
                for line in config_data.split('\n'):
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        path = Path(value.strip().strip('"'))
                        if path.exists():
                            self.config[key.strip()] = str(path)
                
                if self.config:
                    self.add_log(f"Configuration loaded: {', '.join(self.config.keys())}", "SUCCESS")
                else:
                    self.add_log("No valid tools found in configuration", "WARNING")
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            self.add_log(f"Failed to load configuration: {e}", "ERROR")
    
    def toggle_output_path(self, checked):
        """Toggle output path visibility"""
        self.output_path_widget.setVisible(not checked)
        if checked:
            self.output_path = None
    
    def add_files(self):
        """Add files via dialog"""
        mode = self.mode_combo.currentText()
        if "PAA → PNG" in mode:
            file_filter = "PAA Files (*.paa);;All Files (*)"
            title = "Select PAA files to convert"
        else:
            file_filter = "PNG Files (*.png);;All Files (*)"
            title = "Select PNG files to convert"
        
        files, _ = QFileDialog.getOpenFileNames(
            self,
            title,
            "",
            file_filter
        )
        if files:
            for file in files:
                if file not in self.files_to_convert:
                    self.files_to_convert.append(file)
                    self.file_list.addItem(os.path.basename(file))
            self.update_file_count()
            self.add_log(f"Added {len(files)} file(s)", "INFO")
            self.statusBar().showMessage(f"Added {len(files)} files")
    
    def add_directory(self):
        """Add files from directory"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select directory containing files",
            ""
        )
        if directory:
            mode = self.mode_combo.currentText()
            if "PAA → PNG" in mode:
                ext = '.paa'
                ext_name = "PAA"
            else:
                ext = '.png'
                ext_name = "PNG"
            
            added_files = []
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.lower().endswith(ext):
                        full_path = os.path.join(root, file)
                        if full_path not in self.files_to_convert:
                            added_files.append(full_path)
                            self.files_to_convert.append(full_path)
                            self.file_list.addItem(os.path.basename(full_path))
            
            self.update_file_count()
            self.add_log(f"Added {len(added_files)} {ext_name} file(s) from directory", "INFO")
            self.statusBar().showMessage(f"Added {len(added_files)} files from directory")
    
    def clear_files(self):
        """Clear all files from list"""
        self.files_to_convert.clear()
        self.file_list.clear()
        self.update_file_count()
        self.add_log("Cleared all files", "INFO")
        self.statusBar().showMessage("Cleared all files")
    
    def update_file_count(self):
        """Update file count label"""
        self.file_count_label.setText(f"Files: {len(self.files_to_convert)}")
    
    def browse_output(self):
        """Browse for output directory"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select output directory",
            ""
        )
        if directory:
            self.output_path_input.setText(directory)
            self.output_path = directory
            self.add_log(f"Output directory set to: {directory}", "INFO")
    
    def add_log(self, message, level="INFO"):
        """Add message to log area"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        color_map = {
            "INFO": "#00aaff",
            "SUCCESS": "#00ff88",
            "WARNING": "#ffaa00",
            "ERROR": "#ff3333"
        }
        color = color_map.get(level, "#00aaff")
        self.log_text.append(
            f'<span style="color: #444466;">[{timestamp}]</span> '
            f'<span style="color: {color};">[{level}]</span> '
            f'<span style="color: #c0c0d0;">{message}</span>'
        )
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
        self.logger.log(message, level)
    
    def convert_files(self):
        """Convert files"""
        if not self.files_to_convert:
            QMessageBox.warning(self, "No Files", "Please add files to convert first!")
            return
        
        if not self.same_as_source.isChecked() and not self.output_path:
            QMessageBox.warning(self, "No Output Path", 
                               "Please select an output directory!")
            return
        
        if not self.config:
            reply = QMessageBox.question(
                self,
                "No Tools Found",
                "No conversion tools found!\nDo you want to run the setup?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.config_dialog = ConfigDialog()
                self.config_dialog.show()
            return
        
        # Get mode
        mode = "paa_to_png" if "PAA → PNG" in self.mode_combo.currentText() else "png_to_paa"
        
        # Disable convert button
        self.convert_btn.setEnabled(False)
        self.convert_btn.setText("⏳ Converting...")
        self.progress_bar.setValue(0)
        
        # Create worker thread
        self.worker = ConverterWorker(
            self.files_to_convert.copy(),
            self.config,
            self.output_path,
            self.prefix_input.text(),
            self.suffix_input.text(),
            mode
        )
        
        # Connect signals
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.log_updated.connect(self.add_log)
        self.worker.finished.connect(self.conversion_finished)
        
        # Start worker
        self.worker.start()
        
        self.statusBar().showMessage("Converting files...")
    
    def update_progress(self, value):
        """Update progress bar"""
        self.progress_bar.setValue(value)
    
    def conversion_finished(self, success_count, error_count):
        """Handle conversion completion"""
        self.convert_btn.setEnabled(True)
        self.convert_btn.setText("🚀 Start Conversion")
        
        self.statusBar().showMessage(f"Conversion completed! Success: {success_count}, Failed: {error_count}")
        self.add_log(f"✅ Conversion completed - Success: {success_count}, Failed: {error_count}", "SUCCESS")
        
        if success_count > 0 and error_count == 0:
            QMessageBox.information(
                self,
                "Conversion Complete",
                f"🎉 All {success_count} files converted successfully!"
            )
        else:
            QMessageBox.information(
                self,
                "Conversion Complete",
                f"Conversion completed!\n\n✅ Success: {success_count}\n❌ Failed: {error_count}\n\nCheck log for details."
            )

# ==================== Main Application ====================
def main():
    # Set DPI awareness for Windows
    if sys.platform == 'win32':
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass
    
    # Set AppUserModelID BEFORE creating QApplication
    if sys.platform == 'win32':
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("A2M.P2P.Convertor.6.0")
        except:
            pass
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set application info
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    
    # Set application icon
    icon_path = Path("p2p_icon.ico")
    if icon_path.exists():
        app_icon = QIcon(str(icon_path))
        app.setWindowIcon(app_icon)
    
    # Show splash screen
    splash = SplashScreen()
    splash.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()