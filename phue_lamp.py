from phue import Bridge

def rgb_to_xy(red, green, blue):
    """ conversion of RGB colors to CIE1931 XY colors
    Formulas implemented from: https://gist.github.com/popcorn245/30afa0f98eea1c2fd34d
    Args: 
        red (float): a number between 0.0 and 1.0 representing red in the RGB space
        green (float): a number between 0.0 and 1.0 representing green in the RGB space
        blue (float): a number between 0.0 and 1.0 representing blue in the RGB space
    Returns:
        xy (list): x and y
    """

    # gamma correction
    red = pow((red + 0.055) / (1.0 + 0.055), 2.4) if red > 0.04045 else (red / 12.92)
    green = pow((green + 0.055) / (1.0 + 0.055), 2.4) if green > 0.04045 else (green / 12.92)
    blue =  pow((blue + 0.055) / (1.0 + 0.055), 2.4) if blue > 0.04045 else (blue / 12.92)

    # convert rgb to xyz
    x = red * 0.649926 + green * 0.103455 + blue * 0.197109
    y = red * 0.234327 + green * 0.743075 + blue * 0.022598
    z = green * 0.053077 + blue * 1.035763

    # convert xyz to xy
    x = x / (x + y + z)
    y = y / (x + y + z)

    # TODO check color gamut if known
     
    return [x, y]

color_list = [ [1,0,0],  #red
               [0,1,0],  #green
               [0,0,1],  #blue
               [1,1,0],  #yellow
               [0,1,1],  #sky
               [1,0,1],  #purple
               [1,1,1] ] #white

reading_light = [ 1, 1, 0.94 ]

class Phue:
    def __init__(self, Hue_ip):
        # connect phue
        self.lamp = Bridge(Hue_ip)
        while True:
            try:
                self.lamp.connect()
                break
            except:
                print("retry - press the bridge link button")
                continue
        self.bool_lamp_state = self.get_light_state()
        self.color_num = 0
        self.bri_value = 254
        print("Hue lamp connected -- now state : ", self.bool_lamp_state)
    
    def get_light_state(self):
        return self.lamp.get_light(1, 'on')

    def power_switch(self, switch):
        if switch == True or switch == False: # except bool 
            self.lamp.set_light(1, 'on', switch)
            self.bool_lamp_state = self.get_light_state()
        else:
            print("variable 'switch' must be True or False")
    
    def change_color_rgb(self, rgb_list):
        xy_info = rgb_to_xy(rgb_list[0], rgb_list[1], rgb_list[2])
        self.lamp.set_light(1, 'xy', xy_info)

    def change_bri(self):
        self.lamp.set_light(1, 'bri', self.bri_value)

# Gesture list [ Swiping Up / Sliding Two Fingers Up / Swiping Left / Thumb Up / Sliding Two Fingers Right / Stop Sign
#                Sliding Two Fingers Left / Sliding Two Fingers Down / Rolling Hand Backward / Doing other things
#                Swiping Right / Swiping Down / Thumb Down ]
    def control_lamp(self, pre_gesture, now_gesture):
        if pre_gesture == now_gesture:
            pass

        else:
            if now_gesture == 'Sliding Two Fingers Up':
                #
                pass

            elif now_gesture == 'Thumb Up':
                # power on
                self.power_switch(True)

            elif now_gesture == 'Stop Sign':
                # power off
                self.power_switch(False)

            elif now_gesture == 'Swiping Right':
                # color change
                self.change_color_rgb(color_list[self.color_num])
                self.color_num += 1
                if self.color_num > 6:
                    self.color_num = 0

            elif now_gesture == 'Swiping Left':
                # color change
                self.change_color_rgb(color_list[self.color_num])
                self.color_num += -1
                if self.color_num <0:
                    self.color_num = 6

            elif now_gesture == 'Sliding Two Fingers Right':
                # bri up
                self.bri_value += 80
                if self.bri_value > 253:
                    self.bri_value = 254
                self.change_bri()
            
            elif now_gesture == 'Sliding Two Fingers Left':
                # bri down
                self.bri_value += -80
                if self.bri_value < 20:
                    self.bri_value = 10
                self.change_bri()

            elif now_gesture == 'Sliding Two Fingers Down':
                # 
                pass
            elif now_gesture == 'Swiping Up':
                #
                pass
            elif now_gesture == 'Swiping Down':
                #
                pass
            elif now_gesture == 'Rolling Hand Backward':
                # power on
                self.power_switch(True)
            else:
                #
                pass
    
# class end