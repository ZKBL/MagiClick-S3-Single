'''
https://github.com/MakerM0/MagiClick-esp32s3
v0.4.0
    20240612
    ported to cpy 9.x

v0.3.0
    20230922
    add voice


v0.2.0
    20230723
    add bmp

'''


from magiclick import MagiClick
import adafruit_imageload
import asyncio
import random 
import terminalio,displayio,time,gc

import audiocore
import board
import audiobusio
 
mc = MagiClick()
voice = ["1", "2", "3", "4", "5", "6"]

def playwave(filename):
    mc.audio_enable()
    
    try :
        wave_file = open(filename, "rb")
        wave = audiocore.WaveFile(wave_file)
        mc.audio.play(wave)
        while mc.audio.playing:
            pass
        wave.deinit()
        wave_file.close()
        wave_file=None
        gc.collect()
         
    except Exception as e : 
        print (e)
 
    mc.audio_disable()
    pass


class Dice:
    def __init__(self):
        self.value=0
        self.f_start=False
        self.f_loop = False
        self.f_stop = False
        self.f_destroy =False
        
    def roll(self):
        self.value = random.randint(0,5)
        
    
    def start(self):
        pass
    
    def stop(self):
        pass
        
        
mc.display.root_group=None 
 


# Make the display context
splash = displayio.Group()


# image, palette = adafruit_imageload.load('/images/dice/dice_.png')
image, palette = adafruit_imageload.load('/images/dice/dice.bmp',bitmap = displayio.Bitmap,palette = displayio.Palette)
# Set the transparency index color to be hidden
# palette.make_transparent(0)

tile_grid = displayio.TileGrid(image,pixel_shader = palette,
                               tile_width = 100,
                               tile_height = 100,
                               width = 1,
                               height = 1)
tile_grid.x = mc.display.width//2-50 
tile_grid.y = mc.display.height//2-50


splash.append(tile_grid)
mc.display.root_group =splash

mc.display.brightness=1.0   
        

TICK_DICE = 0.5
# 
async def draw(dice):
    starttick=0.0
    while True:
        if dice.f_start==True:
            playwave("audio/dice/dice.wav") 
            starttick = time.monotonic()
            dice.f_start=False            
            dice.f_loop=True
        if dice.f_loop==True:
            dice.roll()
             
            tile_grid[0] = dice.value
            tile_grid.x = mc.display.width//2-50 +random.randint(-10,10)
            tile_grid.y = mc.display.height//2-50+random.randint(-10,10)
            if time.monotonic()-starttick >= TICK_DICE:
                playwave("audio/cn_girl/{}.wav".format(voice[dice.value])) 
                dice.f_loop=False
                dice.f_stop=True
        
        if dice.f_stop==True:
            dice.f_stop = False
          
        await asyncio.sleep(0.04)
        if dice.f_destroy:
            break
        
    



async def button_handle(dice):
    key=-1
    while True:
        await asyncio.sleep(0.2)
        key_event = mc.keys.events.get()
        if key_event:
            if key_event.pressed:
                key = key_event.key_number
        else:
             key=-1
        
        if key==0:
            key=-1
            dice.f_start=True
        
        if key==2:
            dice.f_destroy=True
            mc.exit()
             
        acceleration = mc.imu.acceleration
        if acceleration[2] > 8.0:
            mc.exit()
        


# 
async def main():
    dice =Dice()

    # playwave("{}.wav".format(voice[0])) 
    # playwave("{}.wav".format(voice[1])) 
    # playwave("{}.wav".format(voice[2])) 
    # playwave("{}.wav".format(voice[3])) 
    # playwave("{}.wav".format(voice[4])) 
    # playwave("{}.wav".format(voice[5])) 
    
    
    
    
    draw_task = asyncio.create_task(draw(dice))

    btn_task = asyncio.create_task(button_handle(dice))
    await asyncio.gather(draw_task ,btn_task)


#




asyncio.run(main())       
    
print('end')    
    



