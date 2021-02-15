obj-m += csikernel.o

KID := /lib/modules/$(shell uname -r)/build
PWD := $(shell pwd)

all:
	make -C $(KID) M=$(PWD) modules

clean:
	rm -rf *.o *.mod.c .*.cmd *.ko modules.order Module.symvers *.mod *.tmp_versions
