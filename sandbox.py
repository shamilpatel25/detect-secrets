# your_custom_main.py
import detect_secrets.main

print('starting')
# provide cli args as an array here
detect_secrets.main.main(['scan', '--update', '.secrets.baseline'])