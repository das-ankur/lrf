sshfs vsc33647@login.hpc.kuleuven.be:/data/leuven/336/vsc33647 /Users/pooya/Desktop/vsc/vsc_data -o defer_permissions -o volname=vsc_data
sshfs vsc33647@login.hpc.kuleuven.be:/scratch/leuven/336/vsc33647 /Users/pooya/Desktop/vsc/vsc_scratch -o defer_permissions -o volname=vsc_scratch

umount -f /Users/pooya/Desktop/vsc/vsc_data
umount -f /Users/pooya/Desktop/vsc/vsc_scratch

