import piface.pfio as pfio
from time import sleep
import sys
import unittest


class TestPiFace(unittest.TestCase):
	def setUp(self):
		'''Called at the start of each test'''
		pass

	def tearDown(self):
		'''Called at the end of each test'''
		pass

	def test_pin_translation(self):
		'''Tests the pin translation functions'''
		for pin in range(1, 9):
			bit_mask = pfio.get_pin_bit_mask(pin)
			self.assertEqual(bit_mask, 1 << (pin-1))
			number = pfio.get_pin_number(bit_mask)
			self.assertEqual(number, pin)

	def test_switches(self):
		print 'The left most switch is switch 1'
		for switch_num in range(1,5):
			sys.stdout.write('Press switch %d...' % switch_num)
			sys.stdout.flush()

			switch_values = self.get_switch_values()
			while switch_values == 0:
				switch_values = self.get_switch_values()

			pressed_switch = pfio.get_pin_number(switch_values)
			self.assertEqual(pressed_switch, switch_num,
					'Switch %d was pressed.' % pressed_switch)

			## bad test case, this re-queries the switch - need a way around this...
			# test the switch class
			#this_switch = pfio.Switch(switch_num)
			#self.assertEqual(this_switch.value, 1)

			print 'OK!'

			sleep(0.3)

			# before moving on, wait until no switches are pressed
			switch_values = self.get_switch_values()
			while switch_values != 0:
				switch_values = self.get_switch_values()

	def get_switch_values(self):
		'''Returns the on/off states of the switches. 1 is on 0 is off'''
		return pfio.read_input() & 0x0f

	def test_output_objects(self):
		OUTPUT_SLEEP_DELAY = 0.01
		# test there are no outputs
		self.assertEqual(0, pfio.read_output())

		for led_num in range(1, 5):
			this_led = pfio.LED(led_num)
			this_led.turn_on()
			sleep(OUTPUT_SLEEP_DELAY)
			expected_output_bpat = 1 << (led_num-1)
			self.assertEqual(expected_output_bpat, pfio.read_output())
			this_led.turn_off()
			sleep(OUTPUT_SLEEP_DELAY)
			self.assertEqual(0, pfio.read_output())

		for relay_num in range(1, 3):
			this_relay = pfio.Relay(relay_num)
			this_relay.turn_on()
			sleep(OUTPUT_SLEEP_DELAY)
			expected_output_bpat = 1 << (relay_num-1)
			self.assertEqual(expected_output_bpat, pfio.read_output())
			this_relay.turn_off()
			sleep(OUTPUT_SLEEP_DELAY)
			self.assertEqual(0, pfio.read_output())

if __name__ == '__main__':
	pfio.init()
	unittest.main()
	pfio.deinit()
