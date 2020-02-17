# To get ubuntu permissions: 

https://forum.arduino.cc/index.php?topic=49623.0

sudo chown cn /dev/ttyACM0

userGroup: dialout

sudo usermod -a -G dialout $USER

# To get PyMakr to upload files

Hit: ctrl + shift + G -> "safe_boot_on_upload" = true

