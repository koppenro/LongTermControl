# mount the One-Wire filesystem to the specified path,
# create device aliases according to owfsalias.txt
#
#!/bin/bash
/opt/owfs/bin/owfs -u -c /home/readout/LongTermControl/owfs/owfsconfig.cfg --allow_other --mountpoint=/mnt/1-wire/ --alias=/home/readout/LongTermControl/owfs/owfsalias.txt
#/opt/owfs/bin/owfs -u --allow_other --mountpoint=/mnt/1-wire/
