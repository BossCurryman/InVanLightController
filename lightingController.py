from RGBObject import RGB
from lightingTypes import LightingObject
from machine import Timer
import time

class RGBController:
    """
    Controls all the attached lighting objects
    """
    colour = RGB(0,0,0)
    # Arbitrary length of each end of the rainbow for rainbow effects
    span = 20

    def __init__(self):
        self.devices = []
        self.brightness = 1

    def SetBrightness(self, level:float):
        """
        DEPRECATED
        This was meant to be a better way of changing brightness but now does nothing
        """
        self.brightness = level

    def LightsOff(self):
        """
        Turns all lights off
        """
        self.PushStaticColour(RGB(0,0,0))

    def AddLightObj(self, obj:LightingObject):
        """
        Attaches a lighting object to the controller
        """
        self.devices.append(obj)

    def DisposeOfDynamics(self):
        """
        Disposes of the timer associated with a dynamic effect
        """
        try:
            self.timer.deinit()
        except:
            pass

#-------------------BASIC EFFECT DEFINITIONS AND FUNCTIONS-------------------#
    #-------STATIC COLOUR-------#
    def PushStaticColour(self, colour:RGB):
        self.colour = RGB(int(colour.R * self.brightness), int(colour.G * self.brightness), int(colour.B * self.brightness))
        for item in self.devices:
            item.PushColour(self.StaticColour)
    
    def StaticColour(self, x:int, y:int):
        return self.colour


    #-------STROBING-------#    
    strobingCounter=span

    def StrobingIncramentCounter(self,timer):
        """
        Timer callback that incraments a counter and pushes a dynamic colour.
        """
        if(self.strobingCounter == 1):
            self.strobingCounter == self.span + 1

        self.strobingCounter = self.strobingCounter - 1

        for item in self.devices:
            item.PushColourDynamic(self.Strobing,self.strobingCounter)

    def PushStrobing(self, colour:RGB, period:int):
        self.colour = RGB.GetWithBrightness(colour.R,colour.G,colour.B,self.brightness)
        self.span=period
        self.timer = Timer(-1)
        self.timer.init(freq=240,mode=Timer.PERIODIC, callback=self.StrobingIncramentCounter)
        for item in self.devices:
            item.PushColour(self.StaticColour)

    def Strobing(self,x:int,y:int,t):
        ratio = t / self.span
        return self.colour.CloneWithBrightness(ratio)    
    
    #-------BREATHING-------#

    breathingCounter=0
    breathingDir = 1

    def BreathingIncramentCounter(self,timer):
        if(self.breathingCounter == self.span):
            self.breathingDir = -1
        elif(self.breathingCounter == 0):
            self.breathingDir = 1
        self.breathingCounter = self.breathingCounter + self.breathingDir

        for item in self.devices:
            item.PushColourDynamic(self.Breathing,self.breathingCounter)

    def PushBreathing(self, colour:RGB, period:int):
        self.colour = RGB.GetWithBrightness(colour.R,colour.G,colour.B,self.brightness)
        self.span=period
        self.timer = Timer()
        self.timer.init(freq=60,mode=Timer.PERIODIC, callback=self.BreathingIncramentCounter)
        for item in self.devices:
            item.PushColour(self.StaticColour)

    def Breathing(self,x:int,y:int,t):
        ratio = t / self.span
        return self.colour.CloneWithBrightness(ratio)

    #-------STATIC RAINBOW-------#
    
    def PushStaticRainbow(self, span:int):
        self.span = span
        for item in self.devices:
            item.PushColour(self.StaticRainbow1D)

    def StaticRainbow1D(self, x:int, y:int):
        x = x%self.span
        fraction = self.span/6
        r = 0
        g = 0
        b = 0
        if(x < fraction):
            r = 255
            g = int(255*(x/fraction))
            b = 0
        elif(x < (2*fraction)):
            r = int(255*((-x+(2*fraction))/fraction))
            g = 255
            b = 0
        elif(x < (3 * fraction)):
            r = 0
            g = 255
            b = int(255*((x-(2 * fraction))/fraction))            
        elif(x < (4 * fraction)):
            r = 0
            g = int(255*((-x+(4 * fraction))/fraction))
            b = 255            
        elif(x < (5 * fraction)):
            r = int(255*((x-(4 * fraction))/fraction))
            g = 0
            b = 255            
        elif(x < (6 * fraction)):
            r = 255
            g = 0
            b = int(255*((-x+(6*fraction))/fraction))
        return RGB.GetWithBrightness(r,g,b,self.brightness)
    
    #-------DYNAMIC RAINBOW-------#
    rainbowCounter=0

    def RainbowIncramentCounter(self,timer):
        self.rainbowCounter = (self.rainbowCounter + 1)%self.span
        self.RainbowInternalPush()

    def RainbowInternalPush(self):
        for item in self.devices:
            item.PushColourDynamic(self.DynamicRainbow1D,self.rainbowCounter)
        time.sleep_ms(1)

    def PushDynamicRainbow(self, span:int, freq:int):
        self.timer = Timer(-1)
        self.timer.init(freq=freq,mode=Timer.PERIODIC,callback=self.RainbowIncramentCounter)
        self.span = span

    def DynamicRainbow1D(self, x:int, y:int, xOffset:int):
        x = (x+ xOffset)%self.span
        fraction = self.span/6
        r = 0
        g = 0
        b = 0
        if(x < fraction):
            r = 255
            g = int(255*(x/fraction))
            b = 0
        elif(x < (2*fraction)):
            r = int(255*((-x+(2 * fraction))/fraction))
            g = 255
            b = 0
        elif(x < (3 * fraction)):
            r = 0
            g = 255
            b = int(255*((x-(2 * fraction))/fraction))            
        elif(x < (4 * fraction)):
            r = 0
            g = int(255*((-x+(4 * fraction))/fraction))
            b = 255            
        elif(x < (5 * fraction)):
            r = int(255*((x-(4 * fraction))/fraction))
            g = 0
            b = 255            
        elif(x < (6 * fraction)):
            r = 255
            g = 0
            b = int(255*((-x+(6*fraction))/fraction))
        return RGB.GetWithBrightness(r,g,b,self.brightness)