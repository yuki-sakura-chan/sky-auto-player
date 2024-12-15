import time
import requests
import humanize
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QProgressBar, 
                              QHBoxLayout, QWidget)
from qfluentwidgets import FluentStyleSheet, PushButton, FluentIcon

from sakura.config.sakura_logging import logger


class DownloadManager:
    """Manages download process with retry logic and progress tracking"""

    def __init__(self, session=None, timeout=3):
        self.session = session or self._create_session()
        self.timeout = timeout
        self._is_cancelled = False

    def _create_session(self):
        """
        Creates and configures requests session with retry logic.
        Sets up retry policy for failed requests.
        
        Returns:
            Configured requests.Session object
        """
        session = requests.Session()
        retries = Retry(
            total=5,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504, 404],
            allowed_methods=["GET", "HEAD", "OPTIONS"],  # Allow redirects for GET
        )
        session.mount('https://', HTTPAdapter(max_retries=retries))
        return session

    def cancel(self):
        """Cancel ongoing download"""
        self._is_cancelled = True
    
    def download_file(self, url: str, callback=None):
        """
        Downloads file with progress tracking and cancellation support.
        
        Args:
            url: URL to download from
            callback: Optional progress callback function
            
        Yields:
            Downloaded data chunks
            
        Raises:
            InterruptedError: If download is cancelled
            RequestException: If download fails
        """
        try:
            with self.session.get(url, stream=True, timeout=self.timeout, allow_redirects=True) as response:
                response.raise_for_status()
                total_size = int(response.headers.get('content-length', 0))
                if total_size == 0:
                    logger.warning("Content-Length header is missing")
                
                downloaded = 0
                update_interval = 0.25
                last_time = time.time()
                last_bytes = 0

                for data in response.iter_content(chunk_size=8192):
                    if self._is_cancelled:
                        logger.info("Download cancelled by user")
                        raise InterruptedError("Download cancelled by user")
                    if not data:
                        continue
                    downloaded += len(data)
                    if callback:
                        current_time = time.time()
                        if current_time - last_time >= update_interval:
                            speed = (downloaded - last_bytes) / (current_time - last_time)
                            last_time = current_time
                            last_bytes = downloaded
                            progress = (downloaded / total_size * 100) if total_size > 0 else -1
                            callback(progress, downloaded, speed)
                    yield data
        except requests.RequestException as e:
            logger.error(f"Download error: {e}")
            raise


class DownloadThread(QThread):
    """
    Background thread for handling downloads without blocking UI.
    Emits progress and completion signals.
    """
    
    progress_updated = Signal(float, int, float)
    finished = Signal(bool, str)
    
    def __init__(self, instruments_manager):
        super().__init__()
        self.instruments_manager = instruments_manager
        self.download_manager = DownloadManager()
        self._is_cancelled = False
        
    def cancel(self):
        """Cancel download thread"""
        self._is_cancelled = True
        logger.info("Download thread cancellation flag set")
        self.download_manager.cancel()
        self.terminate()
        self.wait()
        
    def run(self):
        """Executes download process with retry logic"""
        try:
            def progress_callback(progress, current_bytes, speed):
                if self._is_cancelled:
                    raise InterruptedError("Download cancelled by user")
                self.progress_updated.emit(progress, current_bytes, speed)
                logger.debug(f"Download progress: {progress:.2f}%, Speed: {speed:.2f} B/s")
            
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    logger.info(f"Download attempt {attempt + 1}/{max_retries}")
                    self.instruments_manager.download_instruments(
                        callback=progress_callback,
                        session=self.download_manager.session,
                        timeout=3
                    )
                    logger.info("Download completed successfully")
                    self.finished.emit(True, "")
                    break
                except InterruptedError as e:
                    logger.info(f"Download interrupted: {e}")
                    self.finished.emit(False, str(e))
                    break
                except Exception as e:
                    logger.error(f"Error on attempt {attempt + 1}: {e}")
                    if attempt == max_retries - 1:
                        self.finished.emit(False, str(e))
                    time.sleep(2)
        except Exception as e:
            logger.error(f"Download failed with error: {e}", exc_info=True)
            self.finished.emit(False, str(e))


class DownloadDialog(QDialog):
    """
    Dialog window showing download progress with cancel option.
    Displays progress bar, speed, size and time remaining.
    """

    def __init__(self, instruments_manager, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Downloading Instruments')
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        self.setFixedSize(500, 130)
        
        self._setup_ui()
        self._setup_download_thread(instruments_manager)
        self._apply_styling(parent)

    def _setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 15)
        layout.setSpacing(5)
        
        self._setup_status_section(layout)
        self._setup_progress_section(layout)

    def _setup_status_section(self, layout):
        """Setup status section with icon"""
        status_layout = QHBoxLayout()
        status_layout.setSpacing(5)
        self.status_icon = QLabel()
        self.status_icon.setPixmap(FluentIcon.DOWNLOAD.icon().pixmap(16, 16))
        self.status_label = QLabel("Preparing download...")
        status_layout.addWidget(self.status_icon)
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        layout.addLayout(status_layout)

    def _setup_progress_section(self, layout):
        """Setup progress bar and details section"""
        progress_layout = QHBoxLayout()
        progress_layout.setSpacing(5)
        
        # Progress bar and details
        progress_container = QVBoxLayout()
        progress_container.setSpacing(3)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(15)
        progress_container.addWidget(self.progress_bar)
        
        # Details widget
        details_widget = QWidget()
        details_layout = QHBoxLayout(details_widget)
        details_layout.setContentsMargins(0, 0, 0, 0)
        details_layout.setSpacing(10)
        
        self.size_label = QLabel("Size: --")
        self.speed_label = QLabel("Speed: --")
        self.time_label = QLabel("Time left: --")
        
        details_layout.addWidget(self.size_label)
        details_layout.addWidget(self.speed_label)
        details_layout.addWidget(self.time_label)
        details_layout.addStretch()
        
        self.cancel_button = PushButton('Cancel')
        self.cancel_button.setFixedHeight(24)
        details_layout.addWidget(self.cancel_button)
        
        progress_container.addWidget(details_widget)
        progress_layout.addLayout(progress_container)
        layout.addLayout(progress_layout)

    def _setup_download_thread(self, instruments_manager):
        """Setup download thread and connections"""
        self.download_thread = DownloadThread(instruments_manager)
        self.download_thread.progress_updated.connect(self.update_progress)
        self.download_thread.finished.connect(self.on_download_finished)
        self.cancel_button.clicked.connect(self.cancel_download)

    def _apply_styling(self, parent):
        """Apply styling and position dialog"""
        FluentStyleSheet.DIALOG.apply(self)
        if parent:
            center = parent.window().frameGeometry().center()
            self.move(center.x() - self.width() * 0.5,
                     center.y() - self.height() * 0.5)

    def update_status_icon(self, status):
        """Update status icon based on current state"""
        icons = {
            "downloading": FluentIcon.DOWNLOAD,
            "success": FluentIcon.ACCEPT,
            "error": FluentIcon.CLOSE,
            "cancelled": FluentIcon.CANCEL
        }
        icon = icons.get(status, FluentIcon.DOWNLOAD)
        self.status_icon.setPixmap(icon.icon().pixmap(16, 16))

    def update_progress(self, progress: float, bytes_downloaded: int, speed: float):
        """
        Updates progress display with current status.
        
        Args:
            progress: Download progress percentage
            bytes_downloaded: Total bytes downloaded
            speed: Current download speed in bytes/sec
        """
        if progress < 0:
            self.progress_bar.setRange(0, 0)
            self.status_label.setText("Downloading instruments... (size unknown)")
            log_message = f"Progress: Unknown | Downloaded: {humanize.naturalsize(bytes_downloaded, binary=True)} | Speed: {humanize.naturalsize(speed, binary=True)}/s | Time left: unknown"
        else:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(int(progress))
            self.status_label.setText("Downloading instruments...")
            
            remaining_bytes = (bytes_downloaded / progress * 100) - bytes_downloaded
            eta_seconds = remaining_bytes / speed if speed > 0 else 0
            if eta_seconds >= 60:
                eta_text = f"{int(eta_seconds/60)}m {int(eta_seconds%60)}s"
            else:
                eta_text = f"{int(eta_seconds)}s"
            
            log_message = f"Progress: {progress:.2f}% | Downloaded: {humanize.naturalsize(bytes_downloaded, binary=True)} | Speed: {humanize.naturalsize(speed, binary=True)}/s | Time left: {eta_text}"
            
        logger.info(f"update_progress called with {log_message}")
        
        self.update_status_icon("downloading")
        
        size_text = humanize.naturalsize(bytes_downloaded, binary=True)
        self.size_label.setText(f"Size: {size_text}")
        
        speed_text = humanize.naturalsize(speed, binary=True) + "/s"
        self.speed_label.setText(f"Speed: {speed_text}")
        
        if progress > 0 and speed > 0:
            remaining_bytes = (bytes_downloaded / progress * 100) - bytes_downloaded
            eta_seconds = remaining_bytes / speed
            eta_text = f"{int(eta_seconds/60)}m {int(eta_seconds%60)}s" if eta_seconds >= 60 else f"{int(eta_seconds)}s"
            self.time_label.setText(f"Time left: {eta_text}")
        else:
            self.time_label.setText("Time left: unknown")

    def start_download(self):
        """Start download process"""
        self.download_thread.start()

    def cancel_download(self):
        """Cancel download process"""
        logger.info("Download cancellation requested by user")
        self.cancel_button.setEnabled(False)
        self.status_label.setText("Cancelling download...")
        self.update_status_icon("cancelled")
        self.download_thread.cancel()
        self.reject()

    def on_download_finished(self, success: bool, error_message: str):
        """Handles download completion or failure"""
        if success:
            self.update_status_icon("success")
            self.accept()
        else:
            if "cancelled" in error_message.lower():
                self.status_label.setText("Download cancelled")
                self.update_status_icon("cancelled")
            else:
                self.status_label.setText("Download failed")
                self.update_status_icon("error")
            self.reject()
