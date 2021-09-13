from utime import sleep_ms
from RGBObject import RGB
from lightingTypes import LightStrip
from lightingController import RGBController
from machine import Pin, ADC
import time
import _thread

strip1 = LightStrip(16,0,0,300,1)
controller = RGBController()
controller.AddLightObj(strip1)


def ClearBuffer():
    """
    Clears the state machine buffer and disposes of now uneeded objects 
    """
    controller.DisposeOfDynamics()
    time.sleep_us(250)
    controller.PushStaticColour(RGB(0,0,0))

def ClearBufferSeemles():
    """
    Clears the state machine buffer and disposes of now uneeded objects wihtout chaging the colour
    """
    controller.DisposeOfDynamics()
    time.sleep_us(250)
    controller.PushStaticColour(testCol)

testCol = RGB(255,128,0)

inputPressed = False
def InputButton(_):
    """
    Calback for button interrrupt. This is done like this to be compatible with multiprocessing.
    """
    global inputPressed
    inputPressed = True

inputPin = Pin(0, Pin.IN, Pin.PULL_UP)
inputPin.irq(trigger=Pin.IRQ_FALLING, handler=InputButton,hard=True)
RInput = ADC(28)
GInput = ADC(27)
BInput = ADC(26)
RGBChanged = False


def ControlThread():
    """
    Main thread function
    """
    # Pin for escaping the main thread, terminating the program
    threadNukePin = Pin(1, Pin.IN, Pin.PULL_UP)
    # status LED output pin
    outPin = Pin(25,Pin.OUT)
    curEffect = 0
    effectLen = 6
    global RGBChanged
    global inputPressed
    global testCol
    while True:
        if not threadNukePin.value() :
            break
        if inputPressed:
            outPin.toggle()
            curEffect = (curEffect + 1)%effectLen
            SetEffect(curEffect)
            inputPressed = False
        # Sets the current RGB value to what is read off of the ADC pins
        curRGB = RGB(int((RInput.read_u16())/256),int((GInput.read_u16())/256),int((BInput.read_u16())/256))

        # If the difference is outside of a small range, the change is ignored. To avoid flashing coming from noise.
        if CheckNoise(curRGB,testCol) and curEffect == 2:
            testCol = curRGB
            SetEffect(curEffect)      
        
        # Allow some time for other threads to use memory
        time.sleep_ms(5)

baton = _thread.allocate_lock()

noiseThreshold = 3
def CheckNoise(now:RGB, prev:RGB):
    """
    Checks two RGB values against eachother to see if any of the R,G or B values fall outside of a threshold. Essentially denoising.
    """
    isGreater = now.R > prev.R+noiseThreshold or now.G > prev.G+noiseThreshold or now.B > prev.B+noiseThreshold
    isLess = now.R < prev.R-noiseThreshold or now.G < prev.G-noiseThreshold or now.B < prev.B-noiseThreshold
    return isGreater or isLess

def SetEffect(effectIn):    
    locEffect = effectIn    
    if(locEffect == 0):
        baton.acquire()
        ClearBuffer()
        baton.release()
        ## strobing doesnt work well for some reason
        #_thread.start_new_thread(controller.PushStrobing,(testCol,60,))
        #controller.PushStaticColour(RGB(0,0,0))
    elif(locEffect == 1):
        baton.acquire()
        ClearBuffer()
        sleep_ms(2)
        baton.release()
        _thread.start_new_thread(controller.PushStaticRainbow, (100,))
    elif(locEffect == 2):
        baton.acquire()
        ClearBufferSeemles()
        sleep_ms(1)
        baton.release()
        _thread.start_new_thread(controller.PushStaticColour,(testCol,))
    elif(locEffect == 3):
        baton.acquire()
        ClearBufferSeemles()
        baton.release()
        _thread.start_new_thread(controller.PushBreathing,(testCol,60,))
    elif(locEffect == 4):
        baton.acquire()
        ClearBuffer()
        baton.release()
        _thread.start_new_thread(controller.PushDynamicRainbow,(30,60,))
    elif(locEffect == 5):
        baton.acquire()
        ClearBuffer()
        baton.release()
        controller.PushStaticColour(RGB(0,0,0))

ControlThread()
print("forced Exit")
