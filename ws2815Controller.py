import time, rp2, array
from machine import Pin
from RGBObject import RGB


class ws2815:
    """
    Interface class of the state machine for the WS2815s.
    """
    def __init__(self, pin:int, noOfLeds:int, SMID:int, bitbang):
        self.sm =rp2.StateMachine(SMID, bitbang, freq=8_000_000, sideset_base=Pin(pin))
        self.sm.active(1)
        self.LEDCount = noOfLeds
        self.rgbList = list([RGB(0,0,0) for _ in range(noOfLeds)])

    def PushPixelData(self):
        """
        Writes a given array of colours to the state machine.
        """
        arr = array.array("I", [0 for _ in range(self.LEDCount)])
        for i,v in enumerate(self.rgbList):
            r = v.R
            g = v.G
            b = v.B
            # Creates a single value with the necessary bits in the order of GRB
            arr[i] = g << 16 | r << 8 | b
        self.sm.put(arr, 8)
        # Sleep time required to latch the LEDs
        time.sleep_us(250)

    def SetPixelData(self, rgbList:list):
        self.rgbList = rgbList

    def SetIndividualPixel(self, value:RGB, index:int):
        self.rgbList[index] = value
