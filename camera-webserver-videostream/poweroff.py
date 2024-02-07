import time
import subprocess

debug = False

while True:

	#obj = subprocess.call(["upower", "-i", "/org/freedesktop/UPower/devices/battery_BAT1"])
	obj = subprocess.run(["upower", "-i", "/org/freedesktop/UPower/devices/battery_BAT1"], capture_output=True, universal_newlines=True)
	#cmd = subprocess.Popen("upower -i /org/freedesktop/UPower/devices/battery_BAT1")
	
	#print(dir(obj))	
	#print("".join(obj.stdout))
	output = "".join(obj.stdout)
	output = output.split("\n")
	for line in output:
		#print(line)
		if "state:" in line:
			print(line)
			
			
			value = line.split("state: ")[1].strip()
			print(value)
			if value == "discharging":
				if debug:
					print("I need to shutdown now, but debug is active")
				else:
					subprocess.call(["sudo","systemctl", "poweroff"])	
				
	time.sleep(15)

