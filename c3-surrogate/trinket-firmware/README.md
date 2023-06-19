# Installation Instructions

* Update circuit python to version 8.02 or later. Use
  `adafruit-circuitpython-trinket_m0-en_US-8.0.2.uf2` in this repo.
  Instructions are here: https://learn.adafruit.com/adafruit-pyportal/update-the-uf2-bootloader
* Copy `code.py` from the correct directory onto the trinket **after**
  the bootloader has been updated. `ampy put` does not work (you will
  get readonly error), use the file system to copy `code.py`.
* For the opd-shell firmware: Open the serial device in a terminal and you
  should see help command output
