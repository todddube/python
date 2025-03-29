import streamlit as st
import pyhocon
import os
from pyhocon import HOCONConverter

def load_config():
    """Load the configuration file."""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, 'agents_config.hocon')
        
        # Debug info
        st.sidebar.title("Configuration")   
        st.sidebar.text(f"Loading config from: {config_path}")
        if not os.path.exists(config_path):
            st.sidebar.error("Config file not found!")
            return pyhocon.ConfigTree()
            
        with open(config_path, 'r') as f:
            content = f.read()
            # Debug info
            st.sidebar.text("Config content:")
            st.sidebar.code(content)
            
        return pyhocon.ConfigFactory.parse_string(content)
    except Exception as e:
        st.sidebar.error(f"Config load error: {str(e)}")
        return pyhocon.ConfigTree()

def flatten_dict(d, parent_key='', sep='.'):
    """Flatten a nested dictionary."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def main():
    try:
        config = load_config()
        if not config:
            st.warning("Using empty configuration. Please create a valid HOCON file.")
            return
        # Flatten the config for easier handling
        st.title("Agent Configuration Setup")
        st.text("Modify the configuration settings below:")
        flat_config = flatten_dict(config)
    except Exception as e:
        st.error(f"Error loading configuration: {str(e)}")
    
    # Create form for input fields
    with st.form("config_form"):
        updated_values = {}
        for key, value in flat_config.items():
            if isinstance(value, bool):
                updated_values[key] = st.checkbox(key, value=value)
            elif isinstance(value, (int, float)):
                updated_values[key] = st.number_input(key, value=value, key=f"num_{key}")
            else:  # text or other types
                updated_values[key] = st.text_area(key, value=str(value), key=f"text_{key}", label_visibility="visible")
        
        # Add submit button
        if st.form_submit_button("Save Configuration"):
            try:
                # Convert flat dict back to HOCON
                config_str = HOCONConverter.to_hocon(updated_values)
                current_dir = os.path.dirname(os.path.abspath(__file__))
                config_path = os.path.join(current_dir, 'agents_config.hocon')
                
                with open(config_path, 'w') as f:
                    f.write(config_str)
                st.success("Configuration saved successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error saving configuration: {str(e)}")

if __name__ == "__main__":
    main()