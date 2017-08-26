import math
import os
import time

from lifxlan import LifxLAN

K = 2500
FULL = 65535
LOW = 15000
MAXSCORE = 25

RED = (0, FULL, LOW, K)
GREEN = (25000, FULL, LOW, K)
OFF = (0, 0, 0, K)

class SetLights():
    def __init__(self):
        lan = LifxLAN()
        self.light = lan.get_multizone_lights()[0]
        self.zone_count = len(self.light.get_color_zones())

    @staticmethod
    def make_gradient(start, end, steps):
        startH = start[0]
        startS = start[1]
        startV = start[2]
        startK = start[3]
        
        endH = end[0]
        endS = end[1]
        endV = end[2]
        endK = end[3]

        deltaH = endH - startH
        deltaS = endS - startS
        deltaV = endV - startV
        deltaK = endK - startK

        stepH = deltaH / steps
        stepS = deltaS / steps
        stepV = deltaV / steps
        stepK = deltaK / steps
        
        outlist = []
        curH = startH
        curS = startS
        curV = startV
        curK = startK
        for i in range(steps):
            color = (curH, curS, curV, curK)
            outlist.append(color)
            curH += stepH
            curS += stepS
            curV += stepV
            curK += stepK
        return outlist

    @staticmethod
    def set_height(original, height, total):
        for zone in range(height, total):
            original[zone] = OFF
        return original

    @staticmethod
    def check_score():
        basepath = os.path.expanduser('~/Downloads/')
        dircontents = os.scandir(basepath)
        most_recent = sorted(dircontents, key=lambda x: x.stat().st_mtime, reverse=True)
        most_recent = most_recent[0].path
        with open(most_recent) as scorefile:
            score = scorefile.read().strip()
        return int(score)

    @staticmethod
    def adjust_score(score, raw_max, scaled_max):
        return math.floor((score / raw_max) * scaled_max)

    def main(self):
        original_gradient = self.make_gradient(RED, GREEN, self.zone_count)
        score = self.adjust_score(self.check_score(), MAXSCORE, self.zone_count)
        gradient = self.set_height(original_gradient, score, self.zone_count)
        self.light.set_zone_colors(gradient)

if __name__ == '__main__':
    control = SetLights()
    while True:
        control.main()
        time.sleep(1)
