#!/usr/bin/env python
import ads1256
import math
import time
import threading

class TestSensor(object):

	# configuration
	adcChannel = 2
	publishInterval = 1
	readFrequency = 30000 # ADC's SPS parameter. Possible values:   2d5,  5,  10,  15,  25,  30,  50,  60,  100,  500,  1000,  2000,  3750,  7500,  15000,  30000
	smoothingFactor = 0.01
	minimumDeltaMilliampsForPublish = 250

	def __init__(self):
		print("init")
		self.voltageAverage = 0
		self.voltagePositiveAverage = 0
		self.lastPublishedCurrent = -999999
		ads1256.start("1",str(self.readFrequency))
		threading.Thread(target=self.loop).start()

	def __del__(self):
		ads1256.stop()

	def loop(self):
		while True:
			self.processData(ads1256.read_channel(self.adcChannel))
			time.sleep(1 / self.readFrequency / 2)

	def processData(self, channelValue):
		voltage = ((channelValue * 100) / 167.0) / 1000000.0
		if(self.voltageAverage == 0):
			voltageAverage = voltage
			voltagePositiveAverage = voltage
		else:
			voltageAverage = voltage * self.smoothingFactor + voltageAverage * (1 - self.smoothingFactor)
			if(voltage > voltageAverage):
				voltagePositiveAverage = voltage * self.smoothingFactor + voltagePositiveAverage * (1 - self.smoothingFactor)
		rmsMillivolts = (voltagePositiveAverage - voltageAverage) * 1000 # voltage on the ends of coil
		rmsMilliamps = math.floor(rmsMillivolts * 30)
		if math.fabs(self.lastPublishedCurrent - rmsMilliamps) < self.minimumDeltaMilliampsForPublish:
			return
		self.lastPublishedCurrent = rmsMilliamps
		print(rmsMilliamps)

sensor = TestSensor()
while True:
	pass