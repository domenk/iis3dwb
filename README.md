Using STMicroelectronics IIS3DWB with Raspberry Pi

Example Python code for IIS3DWB accelerometer using I2C and SPI. SPI version also includes code for reading FIFO.

Resources:
* [Web site](https://www.st.com/en/mems-and-sensors/iis3dwb.html)
* [Data sheet](https://www.st.com/resource/en/datasheet/iis3dwb.pdf)
* [Application note](https://www.st.com/resource/en/application_note/an5444-iis3dwb-ultrawide-bandwidth-lownoise-3axis-digital-vibration-sensor-stmicroelectronics.pdf)
* Evaluation board [STEVAL-MKI208V1K](https://www.st.com/en/evaluation-tools/steval-mki208v1k.html) ([schematic](https://www.st.com/resource/en/data_brief/steval-mki208v1k.pdf))

If you have custom IIS3DWB breakout board and are following the schematic in the data sheet, these changes may help if you encounter problems with SPI:
* Each of the four SPI lines should have 33 Ω resistor connected in series.
* Make sure 0.1 μF capacitor between VDD_IO and GND is connected closer to GND than capacitor between VDD and GND (e.g. on a breadboard).
* Add 1 μF capacitor between VDD and GND.
