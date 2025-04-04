import streamlit as st
from huesdk import Hue
import time
import logging
import base64
import json
from typing import Optional, Dict, Any, Tuple
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def save_credentials(ip: str, username: str, filepath: str = 'hue_credentials.json') -> None:
    """Save Hue bridge credentials to file with base64 encoding."""
    try:
        encoded_creds = {
            'bridge_ip': base64.b64encode(ip.encode()).decode('utf-8'),
            'bridge_username': base64.b64encode(username.encode()).decode('utf-8')
        }
        
        with open(filepath, 'w') as f:
            json.dump(encoded_creds, f, indent=4)
            
        logger.info(f"Credentials saved to {filepath}")
        
    except Exception as e:
        logger.error(f"Error saving credentials: {str(e)}")
        raise

def load_credentials(filepath: str = 'hue_credentials.json') -> Tuple[Optional[str], Optional[str]]:
    """Load and decode credentials from file."""
    try:
        if not Path(filepath).exists():
            return None, None
            
        with open(filepath, 'r') as f:
            encoded_creds = json.load(f)
        
        bridge_ip = base64.b64decode(encoded_creds['bridge_ip']).decode('utf-8')
        bridge_username = base64.b64decode(encoded_creds['bridge_username']).decode('utf-8')
        
        return bridge_ip, bridge_username
        
    except Exception as e:
        logger.error(f"Error loading credentials: {str(e)}")
        return None, None

@st.cache_resource
def init_hue(ip: str, username: str) -> Optional[Hue]:
    """Initialize Hue bridge connection."""
    try:
        return Hue(bridge_ip=ip, username=username)
    except Exception as e:
        logger.error(f"Error initializing Hue: {str(e)}")
        raise

def get_light_state(light) -> bool:
    """Get current light state safely."""
    try:
        return bool(light.state.get('on', False))
    except AttributeError:
        return False

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

def get_group_state(group) -> bool:
    """Get current group state safely."""
    try:
        return bool(group.state.get('any_on', False))
    except AttributeError:
        return False

def control_group(group, new_state: bool) -> None:
    """Control group state with error handling."""
    try:
        group.set_state({"on": new_state})
        time.sleep(0.5)  # Brief delay for API
        logger.info(f"Set group {group.name} to state: {new_state}")
    except Exception as e:
        logger.error(f"Error controlling group {group.name}: {str(e)}")
        raise

def main():
    st.title("Philips Hue Control Panel")
    
    # Check for existing credentials
    bridge_ip, bridge_username = load_credentials()
    
    # If no credentials exist, show input form
    if not bridge_ip or not bridge_username:
        st.warning("No credentials found. Please enter your Hue Bridge details:")
        
        with st.form("credentials_form"):
            input_ip = st.text_input("Bridge IP Address")
            input_username = st.text_input("Bridge Username/Token")
            submitted = st.form_submit_button("Save Credentials")
            
            if submitted and input_ip and input_username:
                save_credentials(input_ip, input_username)
                bridge_ip, bridge_username = input_ip, input_username
                st.success("Credentials saved successfully!")
                st.rerun()
        
        if not bridge_ip or not bridge_username:
            return
    
    # Initialize Hue connection
    try:
        hue = init_hue(bridge_ip, bridge_username)
        
        # Get all lights
        lights = hue.get_lights()
        
        # Display lights section
        st.header("💡 Lights")
        for light in lights:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**{light.name}** (ID: {light.id_})")
                
            with col2:
                current_state = get_light_state(light)
                if st.button(
                    "Turn Off" if current_state else "Turn On",
                    key=f"light_{light.id_}"
                ):
                    try:
                        control_light(light, not current_state)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error controlling light: {str(e)}")
        
        # Get all groups
        groups = hue.get_groups()
        
        # Display groups section
        st.header("🏠 Groups/Rooms")
        for group in groups:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**{group.name}** (ID: {group.id_})")
                
            with col2:
                current_state = get_group_state(group)
                if st.button(
                    "Turn Off" if current_state else "Turn On",
                    key=f"group_{group.id_}"
                ):
                    try:
                        control_group(group, not current_state)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error controlling group: {str(e)}")
                        
    except Exception as e:
        st.error(f"Error connecting to Hue bridge: {str(e)}")

if __name__ == "__main__":
    main()