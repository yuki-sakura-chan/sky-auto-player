import os
import time
import shutil
import tempfile
import requests
import humanize
from zipfile import ZipFile
from typing import Dict, List
from dataclasses import dataclass

from PySide6.QtWidgets import QComboBox

from sakura.config import conf, save_conf
from sakura.config.sakura_logging import logger


@dataclass
class InstrumentSource:
    name: str
    instruments: List[str]
    url: str

class InstrumentsManager:
    """
    Manages instrument sources and handles downloading/updating of instrument files.
    Provides functionality for scanning local instruments and managing instrument selection.
    """

    GITHUB_REPO = "Ai-Vonie/Sky-Musical-Instruments-Directory"
    BASE_PATH = "resources/Instruments"
    
    def __init__(self):
        self.sources: Dict[str, InstrumentSource] = {}
        self.temp_dir = None
        self.scan_local_instruments()
        
    def scan_local_instruments(self):
        """
        Scans local instruments directories and catalogs available instruments.
        Creates instrument sources directory if it doesn't exist.
        """
        try:
            os.makedirs(self.BASE_PATH, exist_ok=True)
            logger.info(f"Using instruments base directory at {self.BASE_PATH}")
            
            for source_name in os.listdir(self.BASE_PATH):
                source_path = os.path.join(self.BASE_PATH, source_name)
                if os.path.isdir(source_path):
                    instruments = self._get_instruments_in_source(source_path)
                    
                    if instruments:
                        self.sources[source_name] = InstrumentSource(
                            name=source_name,
                            instruments=sorted(instruments),
                            url=""  
                        )
                        logger.info(f"Found local source [{source_name}] with instruments: {instruments}")
                        
        except OSError as e:
            logger.error(f"OS error during scanning local instruments: {e}")
        except Exception as e:
            logger.error(f"Unexpected error scanning local instruments: {e}")
    
    def _get_instruments_in_source(self, source_path: str) -> List[str]:
        """
        Retrieves list of valid instruments from a source directory.
        
        Args:
            source_path: Path to source directory to scan
            
        Returns:
            List of instrument names that have valid audio files
        """
        instruments = []
        for instrument in os.listdir(source_path):
            instrument_dir = os.path.join(source_path, instrument)
            if os.path.isdir(instrument_dir):
                if any(f.endswith(('.wav', '.mp3', '.ogg', '.flac')) for f in os.listdir(instrument_dir)):
                    instruments.append(instrument)
        return instruments
    
    def get_sources(self) -> Dict[str, InstrumentSource]:
        """Get available local instrument sources"""
        return self.sources

    def download_instruments(self, callback=None, session=None, timeout=3):
        """
        Downloads instruments from GitHub repository.
        
        Args:
            callback: Optional progress callback function
            session: Optional requests session to use
            timeout: Connection timeout in seconds
        """
        url = f"https://github.com/{self.GITHUB_REPO}/archive/refs/heads/main.zip"
        logger.info(f"Starting download from {url}")
        
        os.makedirs(self.BASE_PATH, exist_ok=True)
        zip_path = os.path.join(self.BASE_PATH, "instruments.zip")
        self.temp_dir = tempfile.mkdtemp()
        
        request_session = session or requests.Session()
        
        try:
            with request_session.get(url, stream=True, timeout=timeout, allow_redirects=True) as response:
                response.raise_for_status()
                
                total_size = int(response.headers.get('content-length', 0))
                if total_size == 0:
                    logger.warning("Content-Length header is missing")
                else:
                    logger.info(f"Total file size: {humanize.naturalsize(total_size, binary=True)}")
                
                with open(zip_path, 'wb') as f:
                    self._download_file(response, f, total_size, callback)
            
            logger.info("Download completed, extracting files")
            self._extract_zip(zip_path)
            logger.info("Files extracted, updating sources")
            self.scan_local_instruments()
            logger.info("Download and update completed successfully")
        
        except requests.RequestException as e:
            logger.error(f"HTTP error during download: {e}", exc_info=True)
            self._cleanup(zip_path)
            raise
        except Exception as e:
            logger.error(f"Error downloading instruments: {e}", exc_info=True)
            self._cleanup(zip_path)
            raise
        finally:
            self._cleanup(zip_path)

    def _download_file(self, response, file_obj, total_size, callback):
        """
        Handles downloading file chunks and progress tracking.
        
        Args:
            response: Request response object
            file_obj: File object to write to
            total_size: Total expected file size
            callback: Progress callback function
        """
        downloaded = 0
        last_time = time.time()
        last_bytes = 0
        update_interval = 0.25
        
        for data in response.iter_content(chunk_size=8192):
            if not data:
                continue
            file_obj.write(data)
            downloaded += len(data)
            
            if callback:
                current_time = time.time()
                if current_time - last_time >= update_interval:
                    speed = (downloaded - last_bytes) / (current_time - last_time)
                    last_time = current_time
                    last_bytes = downloaded
                    progress = (downloaded / total_size * 100) if total_size > 0 else -1
                    callback(progress, downloaded, speed)
                    
    def _extract_zip(self, zip_path: str):
        """Extract the downloaded zip file"""
        with ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.temp_dir)
        extracted_dir = os.path.join(self.temp_dir, f"{self.GITHUB_REPO.split('/')[-1]}-main")
        for source_name in os.listdir(extracted_dir):
            source_path = os.path.join(extracted_dir, source_name)
            if os.path.isdir(source_path):
                target_path = os.path.join(self.BASE_PATH, source_name)
                shutil.rmtree(target_path, ignore_errors=True)
                shutil.copytree(source_path, target_path)
                logger.info(f"Installed instrument source: {source_name} to {target_path}")

    def _cleanup(self, zip_path):
        """
        Clean up temporary files after download
        
        Args:
            zip_path: Path to downloaded zip file
        """
        # Remove temp directory
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                self.temp_dir = None
                logger.info(f"Removed temporary directory: {self.temp_dir}")
            except OSError as e:
                logger.error(f"Error removing temporary directory: {e}")
        
        # Remove downloaded zip file
        if os.path.exists(zip_path):
            try:
                os.remove(zip_path)
                logger.info(f"Removed downloaded zip file: {zip_path}")
            except OSError as e:
                logger.error(f"Error removing zip file: {e}")

    def update_instruments_combo(self, combo: QComboBox) -> None:
        """
        Updates instruments list in combo box UI element.
        Preserves current selection if possible.
        
        Args:
            combo: QComboBox to update with instruments list
        """
        combo.blockSignals(True)
        combo.clear()
        
        sources = self.get_sources()
        
        for source_name, source in sources.items():
            header_item = f"📁 {source_name}:"
            combo.addItem(header_item)
            
            for instrument in source.instruments:
                combo.addItem(f"🎵 {instrument} [{source_name}]")
        
        current_text = f"🎵 {conf.player.instruments} [{conf.player.source}]"
        index = combo.findText(current_text)
        if index >= 0:
            combo.setCurrentIndex(index)
            
        combo.blockSignals(False)

    def handle_instrument_selection(self, instrument_text: str, source_name: str) -> None:
        """
        Handles instrument selection change from UI.
        Updates config with new selection.
        
        Args:
            instrument_text: Name of selected instrument
            source_name: Name of instrument source
        """
        sources = self.get_sources()
        if source_name in sources and instrument_text in sources[source_name].instruments:
            conf.player.source = source_name
            conf.player.instruments = instrument_text
            save_conf(conf)
            logger.info(f"Selected instrument: [{instrument_text}] from source: [{source_name}]")

    def handle_combo_index_change(self, combo: QComboBox, index: int) -> None:
        """Handle combo box index change"""
        current_text = combo.itemText(index)
        if current_text.startswith("📁"):
            next_index = index + 1
            while next_index < combo.count():
                if not combo.itemText(next_index).startswith("📁"):
                    combo.setCurrentIndex(next_index)
                    break
                next_index += 1
        else:
            text = current_text.replace("🎵 ", "").strip()
            instrument_name = text[:text.rfind("[")].strip()
            source_name = text[text.rfind("[")+1:text.rfind("]")]
            self.handle_instrument_selection(instrument_name, source_name)
