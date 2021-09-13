from machine import Timer
from RGBObject import RGB
from ws2815Controller import ws2815
import _assembly, time

class LightingObject:
    """
    Base class for all types of lighting objects
    """
    def __init__(self):
        pass

    def PushColour(self, colourFunction:function):
        pass

class LightObj:
    """
    A singluar point lighting object. An LED if you will.
    """
    def __init__(self, r:int, g:int, b:int, x:int, y:int):
        self.Colour = RGB(r,g,b)
        self.PosX = x
        self.PosY = y
    
    def SetColour(self, r, g, b):
        self.Colour = RGB(r,g,b)

    def SetPosition(self, x, y):
        self.PosX = x
        self.PosY = y

#Using the zeroth state machine
StateMachineID = 0

class LightStrip(LightingObject):
    """
    A strip of lighting objects. Technically a collection of Lighting objeccts, a collection of LEDs
    """

    def __init__(self, pin, originX, originY, NoOfLEDs, lenBetweenLEDs):
        """
        Create a new light strip with the zeroth LED at originX and originY.
        It is NoOfLEDs long and the physical distance between each LED is lenBetweenLEDs
        """
        self.Lights = list()
        for i in range(NoOfLEDs):
            realX = originX + (lenBetweenLEDs * i)
            self.Lights.append(LightObj(255,255,255,realX,originY))
        self.SM = ws2815(pin,NoOfLEDs,0,_assembly.bitbang)

    def PushColour(self, colourFunction):
        """
        Sets each pixel of the strip to a certain colour according to the given colour function.    
        """
        rgbList = []
        for i,lightObject in enumerate(self.Lights):
            colour = colourFunction(lightObject.PosX,lightObject.PosY)
            lightObject.Colour = colour
            self.SM.SetIndividualPixel(colour,i)
        self.SM.PushPixelData()

    def PushColourDynamic(self, colourFunction,t):
        """
        Sets each pixel of the strip to a certain colour according to the given colour function over time.
        """
        rgbList = []
        for i,lightObject in enumerate(self.Lights):
            colour = colourFunction(lightObject.PosX,lightObject.PosY,t)
            lightObject.Colour = colour
            self.SM.SetIndividualPixel(colour,i)
        self.SM.PushPixelData()

    def DecodeUART(self, char:str) -> int:
        """
        UNUSED
        Decodes and returns a UART input.
        """
        x = ord(char)
        #print(x)
        return x

    def PushBuffer(self, buf:str):
        """
        DEPRECATED
        Pushes all data in the current buffer to the state machine
        """
        arr = []
        for char in buf:
            arr.append(self.DecodeUART(char))
        rgbList = []
        for i in range(len(arr)//3):
            rgbList.append(RGB(arr[i*3],arr[i*3+1],arr[i*3+2]))
        self.SM.SetPixelData(rgbList)
        self.SM.PushPixelData()

    bufferList = []

    def PreCalculateBuffers(self, colourFunction, tSpan):
        """
        DEPRECATED
        Pre calculated the next frame in hopes of gaining speed, just ran into memory issues instead.
        """
        for i in range(tSpan):
            rgbList = []
            for j,lightObject in enumerate(self.Lights):
                colour = colourFunction(lightObject.PosX,lightObject.PosY,i)
                rgbList.append(colour)
            self.bufferList.append(rgbList)

    def PushPreCalculatedBuffers(self, t):
        """
        DEPRECTAED
        Pushed the precalcuted buffers.
        """
        self.SM.SetPixelData(self.bufferList[t])
        self.SM.PushPixelData()
        time.sleep_us(250)