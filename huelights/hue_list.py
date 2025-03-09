from huesdk import Hue

bridgeIP = '192.168.7.213'
bridgeUsername = 'DEjNs62IugavQFib6aA4-s7RFVJPxfpxtAgGV1wm'

if bridgeUsername == "":
    username = Hue.connect(bridge_ip=bridgeIP, username=bridgeUsername)
    print(username)
  
hue = Hue(bridge_ip=bridgeIP, username=bridgeUsername)

# Get all the lights connected to the bridge
lights = hue.get_lights()
for light in lights:    
    print(light.name, light.id_, light.is_on)
    #print(hue.get_light(x))
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
# get light with name
#light = hue.get_light(name="Room 1")

groups = hue.get_groups()
for group in groups:
    print(group.name, group.id_)
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
