**In [1]:**

.. code:: ipython3

    allowable_exceptions = None
    CRYPTO_TARGET = 'TINYAES128C'
    VERSION = 'HARDWARE'
    SS_VER = 'SS_VER_2_1'
    SCOPETYPE = 'OPENADC'
    PLATFORM = 'CW308_K82F'


**In [2]:**

.. code:: ipython3

    #OPENOCD_PATH=r"C:\Users\adewa\OpenOCD\bin\openocd.exe"
    OPENOCD_PATH="../../../xpack-openocd-0.11.0-3/bin/openocd"


**In [ ]:**



**In [3]:**

.. code:: ipython3

    import chipwhisperer as cw
    scope = cw.scope(hw_location=(1, 101))
    serialnumber = scope.sn
    target = cw.target(scope)
    scope.default_setup()
    scope.dis()
    #scope.enable_MPSSE()


**Out [3]:**



.. parsed-literal::

    True




**In [4]:**

.. code:: bash

    %%bash
    cd ../../hardware/victims/firmware/simpleserial-aes
    make PLATFORM=CW308_K82F CRYPTO_TARGET=TINYAES128C SS_VER=SS_VER_2_1 -j


**Out [4]:**



.. parsed-literal::

    Building for platform CW308\_K82F with CRYPTO\_TARGET=TINYAES128C
    SS\_VER set to SS\_VER\_2\_1
    SRC is simpleserial-aes.c simpleserial.c fsl\_trng.c fsl\_pit.c fsl\_pdb.c fsl\_ftfx\_flash.c fsl\_lpuart\_edma.c fsl\_sai\_edma.c fsl\_gpio.c fsl\_ftfx\_cache.c fsl\_llwu.c fsl\_ftfx\_flexnvm.c fsl\_sai.c k82f\_hal.c fsl\_ftfx\_controller.c fsl\_wdog.c fsl\_smartcard\_phy\_tda8035.c fsl\_common.c system\_MK82F25615.c fsl\_cmt.c fsl\_cache.c fsl\_flexio\_spi.c fsl\_qspi\_edma.c fsl\_qspi.c fsl\_flexio\_uart\_edma.c fsl\_tsi\_v4.c fsl\_smartcard\_phy\_emvsim.c fsl\_flexio\_uart.c fsl\_sdhc.c fsl\_ltc.c fsl\_flexio\_i2c\_master.c fsl\_flexio\_camera\_edma.c fsl\_dspi\_edma.c fsl\_dspi.c fsl\_pmc.c fsl\_flexio\_i2s\_edma.c fsl\_ewm.c fsl\_flexio\_spi\_edma.c fsl\_clock.c fsl\_lmem\_cache.c fsl\_cmp.c fsl\_tpm.c fsl\_smc.c fsl\_lpuart.c fsl\_smartcard\_emvsim.c fsl\_flexio\_i2s.c fsl\_flexio.c fsl\_i2c\_edma.c fsl\_ltc\_edma.c fsl\_i2c.c fsl\_ftm.c fsl\_sysmpu.c fsl\_rtc.c fsl\_dac.c fsl\_lptmr.c fsl\_dmamux.c fsl\_vref.c clock\_config.c fsl\_flexio\_camera.c fsl\_crc.c k82f\_trace.c fsl\_mmcau.c fsl\_rcm.c fsl\_edma.c fsl\_flexbus.c fsl\_sdramc.c fsl\_sim.c fsl\_adc16.c
    Blank crypto options, building for AES128
    make clean\_objs .dep 
    make[1]: Entering directory '/home/cwtests/chipwhisperer/hardware/victims/firmware/simpleserial-aes'
    Building for platform CW308\_K82F with CRYPTO\_TARGET=TINYAES128C
    SS\_VER set to SS\_VER\_2\_1
    SRC is simpleserial-aes.c simpleserial.c fsl\_trng.c fsl\_pit.c fsl\_pdb.c fsl\_ftfx\_flash.c fsl\_lpuart\_edma.c fsl\_sai\_edma.c fsl\_gpio.c fsl\_ftfx\_cache.c fsl\_llwu.c fsl\_ftfx\_flexnvm.c fsl\_sai.c k82f\_hal.c fsl\_ftfx\_controller.c fsl\_wdog.c fsl\_smartcard\_phy\_tda8035.c fsl\_common.c system\_MK82F25615.c fsl\_cmt.c fsl\_cache.c fsl\_flexio\_spi.c fsl\_qspi\_edma.c fsl\_qspi.c fsl\_flexio\_uart\_edma.c fsl\_tsi\_v4.c fsl\_smartcard\_phy\_emvsim.c fsl\_flexio\_uart.c fsl\_sdhc.c fsl\_ltc.c fsl\_flexio\_i2c\_master.c fsl\_flexio\_camera\_edma.c fsl\_dspi\_edma.c fsl\_dspi.c fsl\_pmc.c fsl\_flexio\_i2s\_edma.c fsl\_ewm.c fsl\_flexio\_spi\_edma.c fsl\_clock.c fsl\_lmem\_cache.c fsl\_cmp.c fsl\_tpm.c fsl\_smc.c fsl\_lpuart.c fsl\_smartcard\_emvsim.c fsl\_flexio\_i2s.c fsl\_flexio.c fsl\_i2c\_edma.c fsl\_ltc\_edma.c fsl\_i2c.c fsl\_ftm.c fsl\_sysmpu.c fsl\_rtc.c fsl\_dac.c fsl\_lptmr.c fsl\_dmamux.c fsl\_vref.c clock\_config.c fsl\_flexio\_camera.c fsl\_crc.c k82f\_trace.c fsl\_mmcau.c fsl\_rcm.c fsl\_edma.c fsl\_flexbus.c fsl\_sdramc.c fsl\_sim.c fsl\_adc16.c
    Blank crypto options, building for AES128
    rm -f -- simpleserial-aes-CW308\_K82F.hex
    mkdir -p .dep
    rm -f -- simpleserial-aes-CW308\_K82F.eep
    rm -f -- simpleserial-aes-CW308\_K82F.cof
    rm -f -- simpleserial-aes-CW308\_K82F.elf
    rm -f -- simpleserial-aes-CW308\_K82F.map
    rm -f -- simpleserial-aes-CW308\_K82F.sym
    rm -f -- simpleserial-aes-CW308\_K82F.lss
    rm -f -- objdir-CW308\_K82F/\*.o
    rm -f -- objdir-CW308\_K82F/\*.lst
    rm -f -- simpleserial-aes.s simpleserial.s fsl\_trng.s fsl\_pit.s fsl\_pdb.s fsl\_ftfx\_flash.s fsl\_lpuart\_edma.s fsl\_sai\_edma.s fsl\_gpio.s fsl\_ftfx\_cache.s fsl\_llwu.s fsl\_ftfx\_flexnvm.s fsl\_sai.s k82f\_hal.s fsl\_ftfx\_controller.s fsl\_wdog.s fsl\_smartcard\_phy\_tda8035.s fsl\_common.s system\_MK82F25615.s fsl\_cmt.s fsl\_cache.s fsl\_flexio\_spi.s fsl\_qspi\_edma.s fsl\_qspi.s fsl\_flexio\_uart\_edma.s fsl\_tsi\_v4.s fsl\_smartcard\_phy\_emvsim.s fsl\_flexio\_uart.s fsl\_sdhc.s fsl\_ltc.s fsl\_flexio\_i2c\_master.s fsl\_flexio\_camera\_edma.s fsl\_dspi\_edma.s fsl\_dspi.s fsl\_pmc.s fsl\_flexio\_i2s\_edma.s fsl\_ewm.s fsl\_flexio\_spi\_edma.s fsl\_clock.s fsl\_lmem\_cache.s fsl\_cmp.s fsl\_tpm.s fsl\_smc.s fsl\_lpuart.s fsl\_smartcard\_emvsim.s fsl\_flexio\_i2s.s fsl\_flexio.s fsl\_i2c\_edma.s fsl\_ltc\_edma.s fsl\_i2c.s fsl\_ftm.s fsl\_sysmpu.s fsl\_rtc.s fsl\_dac.s fsl\_lptmr.s fsl\_dmamux.s fsl\_vref.s clock\_config.s fsl\_flexio\_camera.s fsl\_crc.s k82f\_trace.s fsl\_mmcau.s fsl\_rcm.s fsl\_edma.s fsl\_flexbus.s fsl\_sdramc.s fsl\_sim.s fsl\_adc16.s aes.s aes-independant.s
    rm -f -- simpleserial-aes.d simpleserial.d fsl\_trng.d fsl\_pit.d fsl\_pdb.d fsl\_ftfx\_flash.d fsl\_lpuart\_edma.d fsl\_sai\_edma.d fsl\_gpio.d fsl\_ftfx\_cache.d fsl\_llwu.d fsl\_ftfx\_flexnvm.d fsl\_sai.d k82f\_hal.d fsl\_ftfx\_controller.d fsl\_wdog.d fsl\_smartcard\_phy\_tda8035.d fsl\_common.d system\_MK82F25615.d fsl\_cmt.d fsl\_cache.d fsl\_flexio\_spi.d fsl\_qspi\_edma.d fsl\_qspi.d fsl\_flexio\_uart\_edma.d fsl\_tsi\_v4.d fsl\_smartcard\_phy\_emvsim.d fsl\_flexio\_uart.d fsl\_sdhc.d fsl\_ltc.d fsl\_flexio\_i2c\_master.d fsl\_flexio\_camera\_edma.d fsl\_dspi\_edma.d fsl\_dspi.d fsl\_pmc.d fsl\_flexio\_i2s\_edma.d fsl\_ewm.d fsl\_flexio\_spi\_edma.d fsl\_clock.d fsl\_lmem\_cache.d fsl\_cmp.d fsl\_tpm.d fsl\_smc.d fsl\_lpuart.d fsl\_smartcard\_emvsim.d fsl\_flexio\_i2s.d fsl\_flexio.d fsl\_i2c\_edma.d fsl\_ltc\_edma.d fsl\_i2c.d fsl\_ftm.d fsl\_sysmpu.d fsl\_rtc.d fsl\_dac.d fsl\_lptmr.d fsl\_dmamux.d fsl\_vref.d clock\_config.d fsl\_flexio\_camera.d fsl\_crc.d k82f\_trace.d fsl\_mmcau.d fsl\_rcm.d fsl\_edma.d fsl\_flexbus.d fsl\_sdramc.d fsl\_sim.d fsl\_adc16.d aes.d aes-independant.d
    rm -f -- simpleserial-aes.i simpleserial.i fsl\_trng.i fsl\_pit.i fsl\_pdb.i fsl\_ftfx\_flash.i fsl\_lpuart\_edma.i fsl\_sai\_edma.i fsl\_gpio.i fsl\_ftfx\_cache.i fsl\_llwu.i fsl\_ftfx\_flexnvm.i fsl\_sai.i k82f\_hal.i fsl\_ftfx\_controller.i fsl\_wdog.i fsl\_smartcard\_phy\_tda8035.i fsl\_common.i system\_MK82F25615.i fsl\_cmt.i fsl\_cache.i fsl\_flexio\_spi.i fsl\_qspi\_edma.i fsl\_qspi.i fsl\_flexio\_uart\_edma.i fsl\_tsi\_v4.i fsl\_smartcard\_phy\_emvsim.i fsl\_flexio\_uart.i fsl\_sdhc.i fsl\_ltc.i fsl\_flexio\_i2c\_master.i fsl\_flexio\_camera\_edma.i fsl\_dspi\_edma.i fsl\_dspi.i fsl\_pmc.i fsl\_flexio\_i2s\_edma.i fsl\_ewm.i fsl\_flexio\_spi\_edma.i fsl\_clock.i fsl\_lmem\_cache.i fsl\_cmp.i fsl\_tpm.i fsl\_smc.i fsl\_lpuart.i fsl\_smartcard\_emvsim.i fsl\_flexio\_i2s.i fsl\_flexio.i fsl\_i2c\_edma.i fsl\_ltc\_edma.i fsl\_i2c.i fsl\_ftm.i fsl\_sysmpu.i fsl\_rtc.i fsl\_dac.i fsl\_lptmr.i fsl\_dmamux.i fsl\_vref.i clock\_config.i fsl\_flexio\_camera.i fsl\_crc.i k82f\_trace.i fsl\_mmcau.i fsl\_rcm.i fsl\_edma.i fsl\_flexbus.i fsl\_sdramc.i fsl\_sim.i fsl\_adc16.i aes.i aes-independant.i
    make[1]: Leaving directory '/home/cwtests/chipwhisperer/hardware/victims/firmware/simpleserial-aes'
    make begin gccversion build sizeafter fastnote end
    make[1]: Entering directory '/home/cwtests/chipwhisperer/hardware/victims/firmware/simpleserial-aes'
    Building for platform CW308\_K82F with CRYPTO\_TARGET=TINYAES128C
    SS\_VER set to SS\_VER\_2\_1
    SRC is simpleserial-aes.c simpleserial.c fsl\_trng.c fsl\_pit.c fsl\_pdb.c fsl\_ftfx\_flash.c fsl\_lpuart\_edma.c fsl\_sai\_edma.c fsl\_gpio.c fsl\_ftfx\_cache.c fsl\_llwu.c fsl\_ftfx\_flexnvm.c fsl\_sai.c k82f\_hal.c fsl\_ftfx\_controller.c fsl\_wdog.c fsl\_smartcard\_phy\_tda8035.c fsl\_common.c system\_MK82F25615.c fsl\_cmt.c fsl\_cache.c fsl\_flexio\_spi.c fsl\_qspi\_edma.c fsl\_qspi.c fsl\_flexio\_uart\_edma.c fsl\_tsi\_v4.c fsl\_smartcard\_phy\_emvsim.c fsl\_flexio\_uart.c fsl\_sdhc.c fsl\_ltc.c fsl\_flexio\_i2c\_master.c fsl\_flexio\_camera\_edma.c fsl\_dspi\_edma.c fsl\_dspi.c fsl\_pmc.c fsl\_flexio\_i2s\_edma.c fsl\_ewm.c fsl\_flexio\_spi\_edma.c fsl\_clock.c fsl\_lmem\_cache.c fsl\_cmp.c fsl\_tpm.c fsl\_smc.c fsl\_lpuart.c fsl\_smartcard\_emvsim.c fsl\_flexio\_i2s.c fsl\_flexio.c fsl\_i2c\_edma.c fsl\_ltc\_edma.c fsl\_i2c.c fsl\_ftm.c fsl\_sysmpu.c fsl\_rtc.c fsl\_dac.c fsl\_lptmr.c fsl\_dmamux.c fsl\_vref.c clock\_config.c fsl\_flexio\_camera.c fsl\_crc.c k82f\_trace.c fsl\_mmcau.c fsl\_rcm.c fsl\_edma.c fsl\_flexbus.c fsl\_sdramc.c fsl\_sim.c fsl\_adc16.c
    Blank crypto options, building for AES128
    mkdir -p objdir-CW308\_K82F 
    .
    Welcome to another exciting ChipWhisperer target build!!
    +--------------------------------------------------------
    +--------------------------------------------------------
    arm-none-eabi-gcc (15:6.3.1+svn253039-1build1) 6.3.1 20170620
    Copyright (C) 2016 Free Software Foundation, Inc.
    This is free software; see the source for copying conditions.  There is NO
    warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
    
    + Default target does full rebuild each time.
    + Specify buildtarget == allquick == to avoid full rebuild
    + Built for platform CW308T: Kinetis MK82F Target with:
    .
    .
    .
    .
    .
    .
    .
    .
    .
    .
    + CRYPTO\_TARGET = TINYAES128C
    Compiling C: .././hal/k82f/fsl\_wdog.c
    Compiling C: .././hal/k82f/fsl\_llwu.c
    .
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_wdog.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_wdog.o.d .././hal/k82f/fsl\_wdog.c -o objdir-CW308\_K82F/fsl\_wdog.o
    Compiling C: .././hal/k82f/fsl\_pdb.c
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_pdb.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_pdb.o.d .././hal/k82f/fsl\_pdb.c -o objdir-CW308\_K82F/fsl\_pdb.o
    .
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_llwu.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_llwu.o.d .././hal/k82f/fsl\_llwu.c -o objdir-CW308\_K82F/fsl\_llwu.o
    + CRYPTO\_OPTIONS = AES128C
    Compiling C: .././hal/k82f/fsl\_sai\_edma.c
    .
    Compiling C: .././hal/k82f/fsl\_gpio.c
    .
    .
    Compiling C: .././simpleserial/simpleserial.c
    .
    .
    Compiling C: .././hal/k82f/fsl\_trng.c
    Compiling C: .././hal/k82f/fsl\_ftfx\_cache.c
    .
    .
    .
    .
    .
    .
    .
    .
    .
    .
    Compiling C: .././hal/k82f/fsl\_common.c
    .
    +--------------------------------------------------------
    .
    .
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_gpio.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_gpio.o.d .././hal/k82f/fsl\_gpio.c -o objdir-CW308\_K82F/fsl\_gpio.o
    Compiling C: .././hal/k82f/fsl\_flexio\_spi.c
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/simpleserial.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/simpleserial.o.d .././simpleserial/simpleserial.c -o objdir-CW308\_K82F/simpleserial.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_trng.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_trng.o.d .././hal/k82f/fsl\_trng.c -o objdir-CW308\_K82F/fsl\_trng.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_ftfx\_cache.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_ftfx\_cache.o.d .././hal/k82f/fsl\_ftfx\_cache.c -o objdir-CW308\_K82F/fsl\_ftfx\_cache.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_sai\_edma.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_sai\_edma.o.d .././hal/k82f/fsl\_sai\_edma.c -o objdir-CW308\_K82F/fsl\_sai\_edma.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_common.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_common.o.d .././hal/k82f/fsl\_common.c -o objdir-CW308\_K82F/fsl\_common.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_flexio\_spi.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_flexio\_spi.o.d .././hal/k82f/fsl\_flexio\_spi.c -o objdir-CW308\_K82F/fsl\_flexio\_spi.o
    Compiling C: .././hal/k82f/k82f\_hal.c
    Compiling C: .././hal/k82f/fsl\_sai.c
    .
    Compiling C: .././hal/k82f/fsl\_ftfx\_controller.c
    .
    Compiling C: .././hal/k82f/fsl\_smartcard\_phy\_tda8035.c
    Compiling C: simpleserial-aes.c
    Compiling C: .././hal/k82f/fsl\_ftfx\_flexnvm.c
    Compiling C: .././hal/k82f/system\_MK82F25615.c
    Compiling C: .././hal/k82f/fsl\_pit.c
    +--------------------------------------------------------
    .
    Compiling C: .././hal/k82f/fsl\_lpuart\_edma.c
    Compiling C: .././hal/k82f/fsl\_qspi\_edma.c
    Compiling C: .././hal/k82f/fsl\_cmt.c
    Compiling C: .././hal/k82f/fsl\_cache.c
    Compiling C: .././hal/k82f/fsl\_sdhc.c
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_pit.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_pit.o.d .././hal/k82f/fsl\_pit.c -o objdir-CW308\_K82F/fsl\_pit.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/simpleserial-aes.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/simpleserial-aes.o.d simpleserial-aes.c -o objdir-CW308\_K82F/simpleserial-aes.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_lpuart\_edma.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_lpuart\_edma.o.d .././hal/k82f/fsl\_lpuart\_edma.c -o objdir-CW308\_K82F/fsl\_lpuart\_edma.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_ftfx\_flexnvm.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_ftfx\_flexnvm.o.d .././hal/k82f/fsl\_ftfx\_flexnvm.c -o objdir-CW308\_K82F/fsl\_ftfx\_flexnvm.o
    Compiling C: .././hal/k82f/fsl\_ltc.c
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_sai.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_sai.o.d .././hal/k82f/fsl\_sai.c -o objdir-CW308\_K82F/fsl\_sai.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/k82f\_hal.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/k82f\_hal.o.d .././hal/k82f/k82f\_hal.c -o objdir-CW308\_K82F/k82f\_hal.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_ftfx\_controller.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_ftfx\_controller.o.d .././hal/k82f/fsl\_ftfx\_controller.c -o objdir-CW308\_K82F/fsl\_ftfx\_controller.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_smartcard\_phy\_tda8035.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_smartcard\_phy\_tda8035.o.d .././hal/k82f/fsl\_smartcard\_phy\_tda8035.c -o objdir-CW308\_K82F/fsl\_smartcard\_phy\_tda8035.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/system\_MK82F25615.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/system\_MK82F25615.o.d .././hal/k82f/system\_MK82F25615.c -o objdir-CW308\_K82F/system\_MK82F25615.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_cmt.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_cmt.o.d .././hal/k82f/fsl\_cmt.c -o objdir-CW308\_K82F/fsl\_cmt.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_cache.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_cache.o.d .././hal/k82f/fsl\_cache.c -o objdir-CW308\_K82F/fsl\_cache.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_qspi\_edma.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_qspi\_edma.o.d .././hal/k82f/fsl\_qspi\_edma.c -o objdir-CW308\_K82F/fsl\_qspi\_edma.o
    Compiling C: .././hal/k82f/fsl\_tsi\_v4.c
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_sdhc.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_sdhc.o.d .././hal/k82f/fsl\_sdhc.c -o objdir-CW308\_K82F/fsl\_sdhc.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_tsi\_v4.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_tsi\_v4.o.d .././hal/k82f/fsl\_tsi\_v4.c -o objdir-CW308\_K82F/fsl\_tsi\_v4.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_ltc.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_ltc.o.d .././hal/k82f/fsl\_ltc.c -o objdir-CW308\_K82F/fsl\_ltc.o
    Compiling C: .././hal/k82f/fsl\_ftfx\_flash.c
    Compiling C: .././hal/k82f/fsl\_qspi.c
    Compiling C: .././hal/k82f/fsl\_smartcard\_phy\_emvsim.c
    Compiling C: .././hal/k82f/fsl\_flexio\_uart.c
    Compiling C: .././hal/k82f/fsl\_flexio\_camera\_edma.c
    Compiling C: .././hal/k82f/fsl\_flexio\_uart\_edma.c
    Compiling C: .././hal/k82f/fsl\_dspi\_edma.c
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_ftfx\_flash.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_ftfx\_flash.o.d .././hal/k82f/fsl\_ftfx\_flash.c -o objdir-CW308\_K82F/fsl\_ftfx\_flash.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_qspi.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_qspi.o.d .././hal/k82f/fsl\_qspi.c -o objdir-CW308\_K82F/fsl\_qspi.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_flexio\_uart\_edma.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_flexio\_uart\_edma.o.d .././hal/k82f/fsl\_flexio\_uart\_edma.c -o objdir-CW308\_K82F/fsl\_flexio\_uart\_edma.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_flexio\_camera\_edma.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_flexio\_camera\_edma.o.d .././hal/k82f/fsl\_flexio\_camera\_edma.c -o objdir-CW308\_K82F/fsl\_flexio\_camera\_edma.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_smartcard\_phy\_emvsim.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_smartcard\_phy\_emvsim.o.d .././hal/k82f/fsl\_smartcard\_phy\_emvsim.c -o objdir-CW308\_K82F/fsl\_smartcard\_phy\_emvsim.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_flexio\_uart.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_flexio\_uart.o.d .././hal/k82f/fsl\_flexio\_uart.c -o objdir-CW308\_K82F/fsl\_flexio\_uart.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_dspi\_edma.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_dspi\_edma.o.d .././hal/k82f/fsl\_dspi\_edma.c -o objdir-CW308\_K82F/fsl\_dspi\_edma.o
    Compiling C: .././hal/k82f/fsl\_flexio\_i2c\_master.c
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_flexio\_i2c\_master.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_flexio\_i2c\_master.o.d .././hal/k82f/fsl\_flexio\_i2c\_master.c -o objdir-CW308\_K82F/fsl\_flexio\_i2c\_master.o
    .
    .
    .
    .
    .
    .
    .
    .
    .
    .
    .
    .
    .
    .
    .
    .
    .
    .
    .
    .
    .
    .
    .
    .
    .
    Compiling C: .././hal/k82f/fsl\_flexio\_spi\_edma.c
    Compiling C: .././hal/k82f/fsl\_lmem\_cache.c
    Compiling C: .././hal/k82f/fsl\_smartcard\_emvsim.c
    Compiling C: .././hal/k82f/fsl\_cmp.c
    Compiling C: .././hal/k82f/fsl\_sysmpu.c
    Compiling C: .././hal/k82f/fsl\_ltc\_edma.c
    Compiling C: .././hal/k82f/fsl\_rtc.c
    Compiling C: .././hal/k82f/fsl\_i2c\_edma.c
    Compiling C: .././hal/k82f/fsl\_tpm.c
    Compiling C: .././hal/k82f/fsl\_smc.c
    Compiling C: .././hal/k82f/fsl\_ftm.c
    Compiling C: .././hal/k82f/fsl\_lpuart.c
    Compiling C: .././hal/k82f/fsl\_clock.c
    Compiling C: .././hal/k82f/fsl\_i2c.c
    Compiling C: .././hal/k82f/fsl\_flexio\_i2s.c
    Compiling C: .././hal/k82f/fsl\_lptmr.c
    Compiling C: .././hal/k82f/fsl\_dac.c
    Compiling C: .././hal/k82f/fsl\_dmamux.c
    Compiling C: .././hal/k82f/fsl\_dspi.c
    Compiling C: .././hal/k82f/fsl\_ewm.c
    Compiling C: .././hal/k82f/fsl\_vref.c
    Compiling C: .././hal/k82f/fsl\_pmc.c
    Compiling C: .././hal/k82f/fsl\_flexio.c
    Compiling C: .././hal/k82f/fsl\_flexio\_i2s\_edma.c
    .
    .
    .
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_dspi.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_dspi.o.d .././hal/k82f/fsl\_dspi.c -o objdir-CW308\_K82F/fsl\_dspi.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_pmc.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_pmc.o.d .././hal/k82f/fsl\_pmc.c -o objdir-CW308\_K82F/fsl\_pmc.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_flexio\_i2s\_edma.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_flexio\_i2s\_edma.o.d .././hal/k82f/fsl\_flexio\_i2s\_edma.c -o objdir-CW308\_K82F/fsl\_flexio\_i2s\_edma.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_ewm.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_ewm.o.d .././hal/k82f/fsl\_ewm.c -o objdir-CW308\_K82F/fsl\_ewm.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_flexio\_spi\_edma.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_flexio\_spi\_edma.o.d .././hal/k82f/fsl\_flexio\_spi\_edma.c -o objdir-CW308\_K82F/fsl\_flexio\_spi\_edma.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_clock.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_clock.o.d .././hal/k82f/fsl\_clock.c -o objdir-CW308\_K82F/fsl\_clock.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_lmem\_cache.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_lmem\_cache.o.d .././hal/k82f/fsl\_lmem\_cache.c -o objdir-CW308\_K82F/fsl\_lmem\_cache.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_cmp.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_cmp.o.d .././hal/k82f/fsl\_cmp.c -o objdir-CW308\_K82F/fsl\_cmp.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_tpm.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_tpm.o.d .././hal/k82f/fsl\_tpm.c -o objdir-CW308\_K82F/fsl\_tpm.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_smc.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_smc.o.d .././hal/k82f/fsl\_smc.c -o objdir-CW308\_K82F/fsl\_smc.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_lpuart.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_lpuart.o.d .././hal/k82f/fsl\_lpuart.c -o objdir-CW308\_K82F/fsl\_lpuart.o
    .
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_smartcard\_emvsim.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_smartcard\_emvsim.o.d .././hal/k82f/fsl\_smartcard\_emvsim.c -o objdir-CW308\_K82F/fsl\_smartcard\_emvsim.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_flexio\_i2s.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_flexio\_i2s.o.d .././hal/k82f/fsl\_flexio\_i2s.c -o objdir-CW308\_K82F/fsl\_flexio\_i2s.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_flexio.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_flexio.o.d .././hal/k82f/fsl\_flexio.c -o objdir-CW308\_K82F/fsl\_flexio.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_i2c\_edma.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_i2c\_edma.o.d .././hal/k82f/fsl\_i2c\_edma.c -o objdir-CW308\_K82F/fsl\_i2c\_edma.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_ltc\_edma.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_ltc\_edma.o.d .././hal/k82f/fsl\_ltc\_edma.c -o objdir-CW308\_K82F/fsl\_ltc\_edma.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_i2c.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_i2c.o.d .././hal/k82f/fsl\_i2c.c -o objdir-CW308\_K82F/fsl\_i2c.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_ftm.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_ftm.o.d .././hal/k82f/fsl\_ftm.c -o objdir-CW308\_K82F/fsl\_ftm.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_sysmpu.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_sysmpu.o.d .././hal/k82f/fsl\_sysmpu.c -o objdir-CW308\_K82F/fsl\_sysmpu.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_rtc.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_rtc.o.d .././hal/k82f/fsl\_rtc.c -o objdir-CW308\_K82F/fsl\_rtc.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_dac.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_dac.o.d .././hal/k82f/fsl\_dac.c -o objdir-CW308\_K82F/fsl\_dac.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_lptmr.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_lptmr.o.d .././hal/k82f/fsl\_lptmr.c -o objdir-CW308\_K82F/fsl\_lptmr.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_dmamux.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_dmamux.o.d .././hal/k82f/fsl\_dmamux.c -o objdir-CW308\_K82F/fsl\_dmamux.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_vref.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_vref.o.d .././hal/k82f/fsl\_vref.c -o objdir-CW308\_K82F/fsl\_vref.o
    Compiling C: .././hal/k82f/clock\_config.c
    Compiling C: .././hal/k82f/fsl\_flexio\_camera.c
    Compiling C: .././hal/k82f/fsl\_mmcau.c
    .
    .
    Compiling C: .././hal/k82f/fsl\_crc.c
    Compiling C: .././hal/k82f/k82f\_trace.c
    .
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/clock\_config.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/clock\_config.o.d .././hal/k82f/clock\_config.c -o objdir-CW308\_K82F/clock\_config.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_flexio\_camera.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_flexio\_camera.o.d .././hal/k82f/fsl\_flexio\_camera.c -o objdir-CW308\_K82F/fsl\_flexio\_camera.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_crc.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_crc.o.d .././hal/k82f/fsl\_crc.c -o objdir-CW308\_K82F/fsl\_crc.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/k82f\_trace.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/k82f\_trace.o.d .././hal/k82f/k82f\_trace.c -o objdir-CW308\_K82F/k82f\_trace.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_mmcau.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_mmcau.o.d .././hal/k82f/fsl\_mmcau.c -o objdir-CW308\_K82F/fsl\_mmcau.o
    Compiling C: .././hal/k82f/fsl\_edma.c
    Compiling C: .././hal/k82f/fsl\_flexbus.c
    .
    .
    Compiling C: .././hal/k82f/fsl\_rcm.c
    .
    .
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_rcm.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_rcm.o.d .././hal/k82f/fsl\_rcm.c -o objdir-CW308\_K82F/fsl\_rcm.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_edma.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_edma.o.d .././hal/k82f/fsl\_edma.c -o objdir-CW308\_K82F/fsl\_edma.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_flexbus.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_flexbus.o.d .././hal/k82f/fsl\_flexbus.c -o objdir-CW308\_K82F/fsl\_flexbus.o
    .
    Compiling C: .././hal/k82f/fsl\_sdramc.c
    Compiling C: .././hal/k82f/fsl\_adc16.c
    Assembling: .././hal/k82f/startup\_MK82F25615.S
    .
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_sdramc.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_sdramc.o.d .././hal/k82f/fsl\_sdramc.c -o objdir-CW308\_K82F/fsl\_sdramc.o
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_adc16.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_adc16.o.d .././hal/k82f/fsl\_adc16.c -o objdir-CW308\_K82F/fsl\_adc16.o
    arm-none-eabi-gcc -c  -I. -x assembler-with-cpp -g -DDEBUG -D\_\_STARTUP\_CLEAR\_BSS -g -Wall -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -mfloat-abi=soft -DF\_CPU=7372800 -Wa,-gstabs,-adhlns=objdir-CW308\_K82F/startup\_MK82F25615.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C .././hal/k82f/startup\_MK82F25615.S -o objdir-CW308\_K82F/startup\_MK82F25615.o
    Compiling C: .././hal/k82f/fsl\_sim.c
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/fsl\_sim.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/fsl\_sim.o.d .././hal/k82f/fsl\_sim.c -o objdir-CW308\_K82F/fsl\_sim.o
    Compiling C: .././crypto/tiny-AES128-C/aes.c
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/aes.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/aes.o.d .././crypto/tiny-AES128-C/aes.c -o objdir-CW308\_K82F/aes.o
    Compiling C: .././crypto/aes-independant.c
    arm-none-eabi-gcc -c  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/aes-independant.lst -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/aes-independant.o.d .././crypto/aes-independant.c -o objdir-CW308\_K82F/aes-independant.o
    .
    Linking: simpleserial-aes-CW308\_K82F.elf
    arm-none-eabi-gcc  -I. -DNO\_EXTRA\_OPTS -Os -g -DDEBUG -DCPU\_MK82FN256VLL15 -w -fno-common -ffunction-sections -fdata-sections -ffreestanding -fno-builtin  -mthumb -mapcs -std=gnu99 -mcpu=cortex-m4 -MMD -MP -static -mfloat-abi=soft -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_k82f -DPLATFORM=CW308\_K82F -DTINYAES128C -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CW308\_K82F/simpleserial-aes.o -I.././simpleserial/ -I.././hal -I.././hal/k82f -I.././hal/k82f/CMSIS -I.././hal/k82f/Drivers -I.././crypto/ -I.././crypto/tiny-AES128-C -std=gnu99  -MMD -MP -MF .dep/simpleserial-aes-CW308\_K82F.elf.d objdir-CW308\_K82F/simpleserial-aes.o objdir-CW308\_K82F/simpleserial.o objdir-CW308\_K82F/fsl\_trng.o objdir-CW308\_K82F/fsl\_pit.o objdir-CW308\_K82F/fsl\_pdb.o objdir-CW308\_K82F/fsl\_ftfx\_flash.o objdir-CW308\_K82F/fsl\_lpuart\_edma.o objdir-CW308\_K82F/fsl\_sai\_edma.o objdir-CW308\_K82F/fsl\_gpio.o objdir-CW308\_K82F/fsl\_ftfx\_cache.o objdir-CW308\_K82F/fsl\_llwu.o objdir-CW308\_K82F/fsl\_ftfx\_flexnvm.o objdir-CW308\_K82F/fsl\_sai.o objdir-CW308\_K82F/k82f\_hal.o objdir-CW308\_K82F/fsl\_ftfx\_controller.o objdir-CW308\_K82F/fsl\_wdog.o objdir-CW308\_K82F/fsl\_smartcard\_phy\_tda8035.o objdir-CW308\_K82F/fsl\_common.o objdir-CW308\_K82F/system\_MK82F25615.o objdir-CW308\_K82F/fsl\_cmt.o objdir-CW308\_K82F/fsl\_cache.o objdir-CW308\_K82F/fsl\_flexio\_spi.o objdir-CW308\_K82F/fsl\_qspi\_edma.o objdir-CW308\_K82F/fsl\_qspi.o objdir-CW308\_K82F/fsl\_flexio\_uart\_edma.o objdir-CW308\_K82F/fsl\_tsi\_v4.o objdir-CW308\_K82F/fsl\_smartcard\_phy\_emvsim.o objdir-CW308\_K82F/fsl\_flexio\_uart.o objdir-CW308\_K82F/fsl\_sdhc.o objdir-CW308\_K82F/fsl\_ltc.o objdir-CW308\_K82F/fsl\_flexio\_i2c\_master.o objdir-CW308\_K82F/fsl\_flexio\_camera\_edma.o objdir-CW308\_K82F/fsl\_dspi\_edma.o objdir-CW308\_K82F/fsl\_dspi.o objdir-CW308\_K82F/fsl\_pmc.o objdir-CW308\_K82F/fsl\_flexio\_i2s\_edma.o objdir-CW308\_K82F/fsl\_ewm.o objdir-CW308\_K82F/fsl\_flexio\_spi\_edma.o objdir-CW308\_K82F/fsl\_clock.o objdir-CW308\_K82F/fsl\_lmem\_cache.o objdir-CW308\_K82F/fsl\_cmp.o objdir-CW308\_K82F/fsl\_tpm.o objdir-CW308\_K82F/fsl\_smc.o objdir-CW308\_K82F/fsl\_lpuart.o objdir-CW308\_K82F/fsl\_smartcard\_emvsim.o objdir-CW308\_K82F/fsl\_flexio\_i2s.o objdir-CW308\_K82F/fsl\_flexio.o objdir-CW308\_K82F/fsl\_i2c\_edma.o objdir-CW308\_K82F/fsl\_ltc\_edma.o objdir-CW308\_K82F/fsl\_i2c.o objdir-CW308\_K82F/fsl\_ftm.o objdir-CW308\_K82F/fsl\_sysmpu.o objdir-CW308\_K82F/fsl\_rtc.o objdir-CW308\_K82F/fsl\_dac.o objdir-CW308\_K82F/fsl\_lptmr.o objdir-CW308\_K82F/fsl\_dmamux.o objdir-CW308\_K82F/fsl\_vref.o objdir-CW308\_K82F/clock\_config.o objdir-CW308\_K82F/fsl\_flexio\_camera.o objdir-CW308\_K82F/fsl\_crc.o objdir-CW308\_K82F/k82f\_trace.o objdir-CW308\_K82F/fsl\_mmcau.o objdir-CW308\_K82F/fsl\_rcm.o objdir-CW308\_K82F/fsl\_edma.o objdir-CW308\_K82F/fsl\_flexbus.o objdir-CW308\_K82F/fsl\_sdramc.o objdir-CW308\_K82F/fsl\_sim.o objdir-CW308\_K82F/fsl\_adc16.o objdir-CW308\_K82F/aes.o objdir-CW308\_K82F/aes-independant.o objdir-CW308\_K82F/startup\_MK82F25615.o --output simpleserial-aes-CW308\_K82F.elf -Xlinker --gc-sections -Xlinker -static -Xlinker -z -Xlinker muldefs -T .././hal/k82f/MK82FN256xxx15\_flash.ld  --specs=nano.specs --specs=nosys.specs -Wl,--start-group -L .././hal/k82f/ -l:lib\_mmcau.a -lm -lc -lgcc -lnosys -Wl,--end-group  -Wl,-Map=simpleserial-aes-CW308\_K82F.map,--cref   -lm  
    .
    .
    .
    .
    .
    Creating load file for Flash: simpleserial-aes-CW308\_K82F.hex
    arm-none-eabi-objcopy -O ihex -R .eeprom -R .fuse -R .lock -R .signature simpleserial-aes-CW308\_K82F.elf simpleserial-aes-CW308\_K82F.hex
    Creating load file for Flash: simpleserial-aes-CW308\_K82F.bin
    Creating load file for EEPROM: simpleserial-aes-CW308\_K82F.eep
    arm-none-eabi-objcopy -O binary -R .eeprom -R .fuse -R .lock -R .signature simpleserial-aes-CW308\_K82F.elf simpleserial-aes-CW308\_K82F.bin
    arm-none-eabi-objcopy -j .eeprom --set-section-flags=.eeprom="alloc,load" \
    --change-section-lma .eeprom=0 --no-change-warnings -O ihex simpleserial-aes-CW308\_K82F.elf simpleserial-aes-CW308\_K82F.eep \|\| exit 0
    Creating Symbol Table: simpleserial-aes-CW308\_K82F.sym
    Creating Extended Listing: simpleserial-aes-CW308\_K82F.lss
    arm-none-eabi-nm -n simpleserial-aes-CW308\_K82F.elf > simpleserial-aes-CW308\_K82F.sym
    arm-none-eabi-objdump -h -S -z simpleserial-aes-CW308\_K82F.elf > simpleserial-aes-CW308\_K82F.lss
    Size after:
       text	   data	    bss	    dec	    hex	filename
      16604	    384	   2880	  19868	   4d9c	simpleserial-aes-CW308\_K82F.elf
    make[1]: Leaving directory '/home/cwtests/chipwhisperer/hardware/victims/firmware/simpleserial-aes'




**In [5]:**

.. code:: ipython3

    import subprocess, sys
    commands = [OPENOCD_PATH, '-f', "../../cw_openocd.cfg", '-c', "transport select jtag", '-c', 
                "ftdi vid_pid 0x2b3e 0xace2", '-c', 'adapter serial {}'.format(serialnumber), '-f', "target/kx.cfg", '-c', "init", '-c', "reset halt", '-c', 
                "flash write_image erase ../../hardware/victims/firmware/simpleserial-aes/simpleserial-aes-CW308_K82F.elf",
                '-c', "shutdown"]
    try:
        x = subprocess.run(commands, check=True, capture_output=True)
    except Exception as x:
        print(x.stderr.decode())
        print(x.stdout.decode())
        raise x
    print(x.stderr.decode())
    print(x.stdout.decode())


**Out [5]:**



.. parsed-literal::

    xPack OpenOCD x86\_64 Open On-Chip Debugger 0.11.0+dev (2021-12-07-17:30)
    Licensed under GNU GPL v2
    For bug reports, read
    	http://openocd.org/doc/doxygen/bugs.html
    jtag
    Info : add flash\_bank kinetis kx.pflash
    Info : clock speed 1000 kHz
    Info : JTAG tap: kx.cpu tap/device found: 0x4ba00477 (mfg: 0x23b (ARM Ltd), part: 0xba00, ver: 0x4)
    Info : kx.cpu: Cortex-M4 r0p1 processor detected
    Info : kx.cpu: target has 6 breakpoints, 4 watchpoints
    Info : kx.cpu: external reset detected
    Info : MDM: Chip is unsecured. Continuing.
    Info : starting gdb server for kx.cpu on 3333
    Info : Listening on port 3333 for gdb connections
    Info : JTAG tap: kx.cpu tap/device found: 0x4ba00477 (mfg: 0x23b (ARM Ltd), part: 0xba00, ver: 0x4)
    Info : MDM: Chip is unsecured. Continuing.
    target halted due to debug-request, current mode: Thread 
    xPSR: 0x01000000 pc: 0x0000051c msp: 0x20030000
    Warn : SIM\_FCFG1 PFSIZE = 0xf: please check if pflash is 256 KB
    Info : Kinetis MK82FN256xxx15 detected: 1 flash blocks
    Info : 1 PFlash banks: 256k total
    Info : Padding image section 0 at 0x000003c0 with 64 bytes
    Info : This device supports Program Longword execution only.
    Info : Disabling Kinetis watchdog (initial WDOG\_STCTRLH = 0x01d3)
    Info : WDOG\_STCTRLH = 0x01d2
    Info : FOPT requested in the programmed file differs from current setting, set 'kinetis fopt 0x3d'.
    Info : Trying to re-program FCF.
    Info : This device supports Program Longword execution only.
    auto erase enabled
    wrote 20480 bytes from file ../../hardware/victims/firmware/simpleserial-aes/simpleserial-aes-CW308\_K82F.elf in 2.166669s (9.231 KiB/s)
    
    shutdown command invoked
    
    




**In [ ]:**

