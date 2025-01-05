import streamlit as st
import subprocess
import time

# Function to perform GET request
def perform_get(ip, resource):
    try:
        command = f"coap-client -m GET coap://{ip}/{resource}"
        result = subprocess.check_output(command, shell=True, text=True)
        return result.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"

# Function to perform PUT request
def perform_put(ip, resource, payload):
    try:
        command = f'coap-client -m PUT -e "{payload}" coap://{ip}/{resource}'
        result = subprocess.check_output(command, shell=True, text=True)
        return result.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"

# Initialize Streamlit session state
if "sensor_states" not in st.session_state:
    st.session_state.sensor_states = []
if "monitoring" not in st.session_state:
    st.session_state.monitoring = False

st.title("CoAP Control and Monitoring UI")

# Input for Arduino IP
arduino_ip = st.text_input("Enter Arduino IP Address", placeholder="e.g., 192.168.10.107")

# Actuator Control (LED)
st.subheader("Actuator Control")
actuator_resource = st.text_input("Enter Actuator Resource Name", value="led")
actuator_payload = st.text_input("Enter Payload for Actuator", placeholder="e.g., 1 or 0")
if st.button("Send PUT Request to Actuator"):
    if arduino_ip and actuator_resource and actuator_payload:
        put_result = perform_put(arduino_ip, actuator_resource, actuator_payload)
        st.text_area("PUT Response", put_result)
    else:
        st.warning("Please enter the Arduino IP, resource name, and payload.")

# Sensor Monitoring
st.subheader("Sensor Monitoring")
sensor_resource = st.text_input("Enter Sensor Resource Name", value="sensor")

# Start Monitoring
if st.button("Start Monitoring Sensor"):
    if arduino_ip and sensor_resource:
        st.session_state.monitoring = True
        st.success("Started monitoring sensor data.")
    else:
        st.warning("Please enter the Arduino IP and sensor resource name.")

# Stop Monitoring
if st.button("Stop Monitoring Sensor"):
    st.session_state.monitoring = False
    st.success("Stopped monitoring sensor data.")

# Display Latest Sensor Data
st.subheader("Latest Sensor Data (Last 5 States)")

placeholder = st.empty()  # Create a placeholder for dynamic updates

if st.session_state.monitoring:
    while st.session_state.monitoring:
        # Fetch new sensor data
        result = perform_get(arduino_ip, sensor_resource)

        # Append the new result to the list
        st.session_state.sensor_states.append(result)

        # Keep only the last 5 states
        if len(st.session_state.sensor_states) > 5:
            st.session_state.sensor_states.pop(0)

        # Display the last 5 states dynamically
        with placeholder.container():
            for i, state in enumerate(st.session_state.sensor_states, start=1):
                st.write(f"{i}: {state}")

        # Sleep for 1 second to fetch data again
        time.sleep(1)

# Show the last 5 states when not monitoring
with placeholder.container():
    for i, state in enumerate(st.session_state.sensor_states, start=1):
        st.write(f"{i}: {state}")

