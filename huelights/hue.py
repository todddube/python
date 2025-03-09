from huesdk import Hue
import urllib3, random, time
import colorsys

# disbale https warnings
urllib3.disable_warnings()

bridgeIP = '192.168.7.213'
bridgeUsername = 'DEjNs62IugavQFib6aA4-s7RFVJPxfpxtAgGV1wm'

if bridgeUsername == "":
    username = Hue.connect(bridge_ip=bridgeIP, username=bridgeUsername)
    print(username)
  
hue = Hue(bridge_ip=bridgeIP, username=bridgeUsername)
# Get lights in the room "Front Room"
lights = hue.get_lights_by_room("Front Room")

# Function to change light color
def change_light_color(light):
    hue_value = random.randint(0, 65535)
    sat_value = random.randint(200, 254)
    bri_value = random.randint(150, 254)
    light.set_state(hue=hue_value, sat=sat_value, bri=bri_value)

# Change lights color randomly for 60 seconds
end_time = time.time() + 60
while time.time() < end_time:
    for light in lights:
        change_light_color(light)
    time.sleep(5)