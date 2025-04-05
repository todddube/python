import streamlit as st
from huesdk import Hue
import time
import logging
import base64
import json
import urllib3
from typing import Optional, Dict, Any, Tuple, List
from pathlib import Path
from datetime import datetime

# Suppress InsecureRequestWarning
# TODO: Implement proper certificate verification
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HueCredentials:
    def __init__(self, filepath: str = 'creds/hue_credentials.json'):
        self.filepath = Path(filepath)
        self.filepath.parent.mkdir(exist_ok=True)
        
    def save(self, ip: str, username: str) -> None:
        """Save Hue bridge credentials with base64 encoding."""
        try:
            encoded_creds = {
                'bridge_ip': base64.b64encode(ip.encode()).decode('utf-8'),
                'bridge_username': base64.b64encode(username.encode()).decode('utf-8')
            }
            
            with open(self.filepath, 'w') as f:
                json.dump(encoded_creds, f, indent=4)
                
            logger.info(f"Credentials saved to {self.filepath}")
            
        except Exception as e:
            logger.error(f"Error saving credentials: {str(e)}")
            raise

    def load(self) -> Tuple[Optional[str], Optional[str]]:
        """Load and decode credentials from file."""
        try:
            if not self.filepath.exists():
                return None, None
                
            with open(self.filepath, 'r') as f:
                encoded_creds = json.load(f)
            
            bridge_ip = base64.b64decode(encoded_creds['bridge_ip']).decode('utf-8')
            bridge_username = base64.b64decode(encoded_creds['bridge_username']).decode('utf-8')
            
            return bridge_ip, bridge_username
            
        except Exception as e:
            logger.error(f"Error loading credentials: {str(e)}")
            return None, None

class HueController:
    def __init__(self, ip: str, username: str):
        self.hue = self._init_connection(ip, username)
        
    @staticmethod
    @st.cache_resource
    def _init_connection(ip: str, username: str) -> Optional[Hue]:
        """Initialize Hue bridge connection."""
        try:
            return Hue(bridge_ip=ip, username=username)
        except Exception as e:
            logger.error(f"Error initializing Hue: {str(e)}")
            raise

    def get_lights(self) -> List:
        return self.hue.get_lights()
    
    def get_groups(self) -> List:
        return self.hue.get_groups()
    
    @staticmethod
    def get_light_state(light) -> bool:
        """Get current light state safely."""
        try:
            return bool(light.state.get('on', False))
        except AttributeError:
            return False

    @staticmethod
    def control_light(light, new_state: bool) -> None:
        """Control individual light state with error handling."""
        try:
            if new_state:
                light.on()
            else:
                light.off()
            time.sleep(0.5)  # Brief delay for API
            logger.info(f"Set light {light.name} to state: {new_state}")
        except Exception as e:
            logger.error(f"Error controlling light {light.name}: {str(e)}")
            raise

    @staticmethod
    def get_group_state(group) -> bool:
        """Get current group state safely."""
        try:
            return bool(group.state.get('any_on', False))
        except AttributeError:
            return False

    @staticmethod
    def control_group(group, new_state: bool) -> None:
        """Control group state with error handling."""
        try:
            if new_state:
                group.on()
            else:
                group.off()
            time.sleep(0.5)  # Brief delay for API
            logger.info(f"Set group {group.name} to state: {new_state}")
        except Exception as e:
            logger.error(f"Error controlling group {group.name}: {str(e)}")
            raise

class HueApp:
    def __init__(self):
        self.credentials = HueCredentials()
        self.controller = None
        # Initialize session state variables
        if 'last_update' not in st.session_state:
            st.session_state.last_update = 0
        if 'poll_interval' not in st.session_state:
            st.session_state.poll_interval = 1  # 1 second default

    def should_update(self) -> bool:
        """Check if it's time to update based on polling interval"""
        current_time = time.time()
        if current_time - st.session_state.last_update >= st.session_state.poll_interval:
            st.session_state.last_update = current_time
            return True
        return False

    def render_status_bar(self):
        """Render the status bar with update information"""
        status_col1, status_col2 = st.columns([3, 1])
        with status_col1:
            st.caption("🔄 Auto-updating status")
        with status_col2:
            st.caption(f"Last update: {datetime.now().strftime('%H:%M:%S')}")

    def show_credentials_form(self) -> Tuple[Optional[str], Optional[str]]:
        """Display and handle the credentials input form."""
        st.warning("No credentials found. Please enter your Hue Bridge details:")
        
        with st.form("credentials_form"):
            input_ip = st.text_input("Bridge IP Address")
            input_username = st.text_input("Bridge Username/Token")
            submitted = st.form_submit_button("Save Credentials")
            
            if submitted and input_ip and input_username:
                self.credentials.save(input_ip, input_username)
                st.success("Credentials saved successfully!")
                st.rerun()
        
        return self.credentials.load()

    def main(self):
        st.title("Philips Hue Control Panel")
        
        # Load credentials
        bridge_ip, bridge_username = self.credentials.load()
        
        # If no credentials exist, show input form
        if not bridge_ip or not bridge_username:
            bridge_ip, bridge_username = self.show_credentials_form()
            if not bridge_ip or not bridge_username:
                return
        
        try:
            # Initialize controller if not already initialized
            if not self.controller:
                self.controller = HueController(bridge_ip, bridge_username)
            
            # Check if we should update based on polling interval
            if self.should_update():
                logger.debug(f"Polling update at {datetime.now().strftime('%H:%M:%S')}")
                st.rerun()
            
            # Render status bar and get devices
            self.render_status_bar()
            lights = self.controller.get_lights()
            groups = self.controller.get_groups()
            
            # Display groups section
            st.header("🏠 Groups/Rooms")
            for group in groups:
                # Create columns for group name and control button
                col1, col2, col3 = st.columns([2.5, 0.5, 1])
                
                with col1:
                    # Define emoji mappings
                    room_emojis = {
                        'living': '🛋️',
                        'bedroom': '🛏️',
                        'kitchen': '🍳',
                        'bathroom': '🚿',
                        'dining': '🍽️',
                        'office': '💼',
                        'garage': '🚗',
                        'garden': '🌺',
                        'outdoor': '🌳'
                    }
                    
                    # Find matching emoji or default to house
                    emoji = '🏠'
                    name_lower = group.name.lower()
                    for key, value in room_emojis.items():
                        if key in name_lower:
                            emoji = value
                            break
                            
                    st.write(f"{emoji} **{group.name}** (ID: {group.id_})")
                    
                with col2:
                    st.write("Status: 🟢" if self.controller.get_group_state(group) else "Status: ⚫")
                    
                with col3:
                    current_state = self.controller.get_group_state(group)
                    if st.button(
                        "Turn Off" if current_state else "Turn On",
                        key=f"group_{group.id_}"
                    ):
                        try:
                            self.controller.control_group(group, not current_state)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error controlling group: {str(e)}")

                # Update the lights expander section
                with st.expander("Show Lights in this Group"):
                    if hasattr(group, 'lights') and group.lights:
                        for light_id in group.lights:
                            light = next((l for l in lights if str(l.id_) == str(light_id)), None)
                            if light:
                                lcol1, lcol2, lcol3 = st.columns([2.5, 0.5, 1])
                                with lcol1:
                                    st.write(f"  • {light.name}")
                                with lcol2:
                                    st.write("🟢" if self.controller.get_light_state(light) else "⚫")
                                with lcol3:
                                    current_light_state = self.controller.get_light_state(light)
                                    if st.button(
                                        "Turn Off" if current_light_state else "Turn On",
                                        key=f"light_{light.id_}_in_group_{group.id_}"
                                    ):
                                        try:
                                            self.controller.control_light(light, not current_light_state)
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"Error controlling light: {str(e)}")
                    else:
                        st.info("No lights in this group")
                
                st.divider()
                            
        except Exception as e:
            st.error(f"Error connecting to Hue bridge: {str(e)}")

if __name__ == "__main__":
    app = HueApp()
    app.main()