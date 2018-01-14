import argparse
import math
import os
import signal
import sys
import time

from neopixel import *

class SetLights():
    def __init__(self, led_count=30, led_pin=18, led_freq_hz=800000, led_dma=10, led_brightness=255, led_invert=False, led_channel=0, led_strip=ws.WS2811_STRIP_GRB):
        signal.signal(signal.SIGINT, self.signal_handler)
        self.strip = Adafruit_NeoPixel(led_count, led_pin, led_freq_hz, led_dma, led_invert, led_brightness, led_channel, led_strip)
        self.strip.begin()
        self.most_recent_score_file = None
        self.max_score = 25

    def parse_args(self):
        parser = argparse.ArgumentParser('run score lights based on scorefile')
        parser.add_argument('--maxscore', type=int, default=25, help='score to scale as "max"')
        parser.add_argument('scorepath', help='path where the scorefiles appear')
        args = parser.parse_args()
        self.max_score = args.maxscore
        self.scorepath = args.scorepath

    def signal_handler(self, signal, frame):
        self.colorWipe(self.strip, Color(0,0,0), reverse=True)
        sys.exit(0)

    def colorWipe(self, strip, color, fake_len=-1, wait_ms=50, reverse=False):
        """Wipe color across display a pixel at a time."""
        if fake_len == -1:
            fake_len = self.strip.numPixels()
        for i in range(fake_len):
            if not reverse:
                self.strip.setPixelColor(i, color)
            else:
                self.strip.setPixelColor(self.strip.numPixels() - (i + 1), color)
            self.strip.show()
            time.sleep(wait_ms/1000.0)

    @staticmethod
    def wheel(pos):
        """Generate rainbow colors across 0-255 positions."""
        if pos < 85:
            return Color(pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return Color(255 - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return Color(0, pos * 3, 255 - pos * 3)

    def rainbow(self, strip, wait_ms=10, fake_len=-1, iterations=1):
        """Draw rainbow that fades across all pixels at once."""
        if fake_len == -1:
            fake_len = self.strip.numPixels()
        for j in range(256*iterations):
            for i in range(fake_len):
                self.strip.setPixelColor(i, self.wheel((i+j) & 255))
            self.strip.show()
            time.sleep(wait_ms/1000.0)

    def rainbowCycle(self, strip, wait_ms=10, fake_len=-1, iterations=5):
        """Draw rainbow that uniformly distributes itself across all pixels."""
        if fake_len == -1:
            fake_len = self.strip.numPixels()
        for j in range(256*iterations):
            for i in range(fake_len):
                self.strip.setPixelColor(i, self.wheel((int(i * 256 / self.strip.numPixels()) + j) & 255))
            self.strip.show()
            time.sleep(wait_ms/1000.0)

    def check_score(self):
        basepath = os.path.expanduser(self.scorepath)
        dircontents = os.scandir(basepath)
        most_recent = sorted(dircontents, key=lambda x: x.stat().st_mtime, reverse=True)
        most_recent = most_recent[0].path
        if most_recent != self.most_recent_score_file:
            with open(most_recent) as scorefile:
                score = scorefile.read().strip()
            self.most_recent_score_file = most_recent
            return int(score)
        else:
            return 0

    @staticmethod
    def adjust_score(score, raw_max, scaled_max):
        return math.floor((score / raw_max) * scaled_max)

    def animate_score(self, score):
        if score != 0:
            print('Animating a score of {}'.format(score))
            self.colorWipe(self.strip, Color(0, 255, 0), fake_len=score)
            self.rainbowCycle(self.strip, fake_len=score)
            self.colorWipe(self.strip, Color(0, 0, 0), reverse=True)

    def main(self):
        self.parse_args()
        while True:
            score = self.adjust_score(self.check_score(), self.max_score, self.strip.numPixels())
            self.animate_score(score)
            time.sleep(1)


if __name__ == '__main__':
    lights=SetLights()
    lights.main()
