
class RGB:
    """
    Object for representing red, green and blue on the WS2815s
    """

    def __init__(self, r:int, g:int, b:int) -> None:
        self.R = r
        self.G = g
        self.B = b
        
    def __repr__(self) -> str:
        x = "R:{0} G:{1} B:{2}".format(self.R, self.G,self.B)
        return x

    def CloneWithBrightness(self,brightness:float):
        """
        Returns a new RGB object with the same red, green and blue proportions at a new brightness
        """
        return RGB.GetWithBrightness(self.R,self.G,self.B,brightness)

    @classmethod
    def GetWithBrightness(cls, r:int,g:int,b:int,a:float):
        R = int(r * a)
        G = int(g * a)
        B = int(b * a)
        return RGB(R,G,B)

