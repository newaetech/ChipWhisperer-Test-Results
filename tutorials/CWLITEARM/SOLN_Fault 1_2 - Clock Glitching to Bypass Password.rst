Part 1, Topic 2: Clock Glitching to Bypass Password
===================================================



**SUMMARY:** *In the previous lab, we learned how clock glitching can be
used to cause a target to behave unexpectedly. In this lab, we'll look
at a slightly more realistic example - glitching past a password check*

**LEARNING OUTCOMES:**

-  Applying previous glitch settings to new firmware
-  Checking for success and failure when glitching

Firmware
--------

We've already seen how we can insert clock gliches to mess up a
calculation that a target is trying to make. While this has many
applications, some which will be covered in Fault\_201, let's take a
look at something a little closer to our original example of glitch
vulnerable code: a password check. No need to change out firmware here,
we're still using the simpleserial-glitch project (though we'll go
through all the build stuff again).

The code is as follows for the password check:

.. code:: c

    uint8_t password(uint8_t* pw)
    {
        char passwd[] = "touch";
        char passok = 1;
        int cnt;

        trigger_high();

        //Simple test - doesn't check for too-long password!
        for(cnt = 0; cnt < 5; cnt++){
            if (pw[cnt] != passwd[cnt]){
                passok = 0;
            }
        }
        
        trigger_low();
        
        simpleserial_put('r', 1, (uint8_t*)&passok);
        return passok;
    }

There's really nothing out of the ordinary here - it's just a simple
password check. We can communicate with it using the ``'p'`` command.


**In [1]:**

.. code:: ipython3

    SCOPETYPE = 'OPENADC'
    PLATFORM = 'CWLITEARM'
    SS_VER = 'SS_VER_2_1'
    allowable_exceptions = None
    CRYPTO_TARGET = 'TINYAES128C'
    VERSION = 'HARDWARE'


**In [2]:**

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
    
    



**Out [2]:**



.. parsed-literal::

    INFO: Found ChipWhisperer😍




**In [3]:**

.. code:: bash

    %%bash -s "$PLATFORM" "$SS_VER"
    cd ../../../hardware/victims/firmware/simpleserial-glitch
    make PLATFORM=$1 CRYPTO_TARGET=NONE SS_VER=$2


**Out [3]:**



.. parsed-literal::

    SS\_VER set to SS\_VER\_2\_1
    make clean\_objs .dep 
    make[1]: Entering directory '/home/cwtests/chipwhisperer/hardware/victims/firmware/simpleserial-glitch'
    SS\_VER set to SS\_VER\_2\_1
    rm -f -- simpleserial-glitch-CWLITEARM.hex
    rm -f -- simpleserial-glitch-CWLITEARM.eep
    rm -f -- simpleserial-glitch-CWLITEARM.cof
    rm -f -- simpleserial-glitch-CWLITEARM.elf
    rm -f -- simpleserial-glitch-CWLITEARM.map
    rm -f -- simpleserial-glitch-CWLITEARM.sym
    rm -f -- simpleserial-glitch-CWLITEARM.lss
    rm -f -- objdir-CWLITEARM/\*.o
    rm -f -- objdir-CWLITEARM/\*.lst
    rm -f -- simpleserial-glitch.s simpleserial.s stm32f3\_hal.s stm32f3\_hal\_lowlevel.s stm32f3\_sysmem.s
    rm -f -- simpleserial-glitch.d simpleserial.d stm32f3\_hal.d stm32f3\_hal\_lowlevel.d stm32f3\_sysmem.d
    rm -f -- simpleserial-glitch.i simpleserial.i stm32f3\_hal.i stm32f3\_hal\_lowlevel.i stm32f3\_sysmem.i
    make[1]: '.dep' is up to date.
    make[1]: Leaving directory '/home/cwtests/chipwhisperer/hardware/victims/firmware/simpleserial-glitch'
    make begin gccversion build sizeafter fastnote end
    make[1]: Entering directory '/home/cwtests/chipwhisperer/hardware/victims/firmware/simpleserial-glitch'
    SS\_VER set to SS\_VER\_2\_1
    .
    Welcome to another exciting ChipWhisperer target build!!
    arm-none-eabi-gcc (15:6.3.1+svn253039-1build1) 6.3.1 20170620
    Copyright (C) 2016 Free Software Foundation, Inc.
    This is free software; see the source for copying conditions.  There is NO
    warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
    
    .
    Compiling C: simpleserial-glitch.c
    arm-none-eabi-gcc -c -mcpu=cortex-m4 -I. -mthumb -mfloat-abi=soft -fmessage-length=0 -ffunction-sections -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DSTM32F303xC -DSTM32F3 -DSTM32 -DDEBUG -DHAL\_TYPE=HAL\_stm32f3 -DPLATFORM=CWLITEARM -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CWLITEARM/simpleserial-glitch.lst -I.././simpleserial/ -I.././hal -I.././hal/stm32f3 -I.././hal/stm32f3/CMSIS -I.././hal/stm32f3/CMSIS/core -I.././hal/stm32f3/CMSIS/device -I.././hal/stm32f4/Legacy -I.././crypto/ -std=gnu99  -MMD -MP -MF .dep/simpleserial-glitch.o.d simpleserial-glitch.c -o objdir-CWLITEARM/simpleserial-glitch.o
    .
    Compiling C: .././simpleserial/simpleserial.c
    arm-none-eabi-gcc -c -mcpu=cortex-m4 -I. -mthumb -mfloat-abi=soft -fmessage-length=0 -ffunction-sections -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DSTM32F303xC -DSTM32F3 -DSTM32 -DDEBUG -DHAL\_TYPE=HAL\_stm32f3 -DPLATFORM=CWLITEARM -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CWLITEARM/simpleserial.lst -I.././simpleserial/ -I.././hal -I.././hal/stm32f3 -I.././hal/stm32f3/CMSIS -I.././hal/stm32f3/CMSIS/core -I.././hal/stm32f3/CMSIS/device -I.././hal/stm32f4/Legacy -I.././crypto/ -std=gnu99  -MMD -MP -MF .dep/simpleserial.o.d .././simpleserial/simpleserial.c -o objdir-CWLITEARM/simpleserial.o
    .
    Compiling C: .././hal/stm32f3/stm32f3\_hal.c
    arm-none-eabi-gcc -c -mcpu=cortex-m4 -I. -mthumb -mfloat-abi=soft -fmessage-length=0 -ffunction-sections -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DSTM32F303xC -DSTM32F3 -DSTM32 -DDEBUG -DHAL\_TYPE=HAL\_stm32f3 -DPLATFORM=CWLITEARM -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CWLITEARM/stm32f3\_hal.lst -I.././simpleserial/ -I.././hal -I.././hal/stm32f3 -I.././hal/stm32f3/CMSIS -I.././hal/stm32f3/CMSIS/core -I.././hal/stm32f3/CMSIS/device -I.././hal/stm32f4/Legacy -I.././crypto/ -std=gnu99  -MMD -MP -MF .dep/stm32f3\_hal.o.d .././hal/stm32f3/stm32f3\_hal.c -o objdir-CWLITEARM/stm32f3\_hal.o
    .
    Compiling C: .././hal/stm32f3/stm32f3\_hal\_lowlevel.c
    arm-none-eabi-gcc -c -mcpu=cortex-m4 -I. -mthumb -mfloat-abi=soft -fmessage-length=0 -ffunction-sections -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DSTM32F303xC -DSTM32F3 -DSTM32 -DDEBUG -DHAL\_TYPE=HAL\_stm32f3 -DPLATFORM=CWLITEARM -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CWLITEARM/stm32f3\_hal\_lowlevel.lst -I.././simpleserial/ -I.././hal -I.././hal/stm32f3 -I.././hal/stm32f3/CMSIS -I.././hal/stm32f3/CMSIS/core -I.././hal/stm32f3/CMSIS/device -I.././hal/stm32f4/Legacy -I.././crypto/ -std=gnu99  -MMD -MP -MF .dep/stm32f3\_hal\_lowlevel.o.d .././hal/stm32f3/stm32f3\_hal\_lowlevel.c -o objdir-CWLITEARM/stm32f3\_hal\_lowlevel.o
    .
    Compiling C: .././hal/stm32f3/stm32f3\_sysmem.c
    arm-none-eabi-gcc -c -mcpu=cortex-m4 -I. -mthumb -mfloat-abi=soft -fmessage-length=0 -ffunction-sections -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DSTM32F303xC -DSTM32F3 -DSTM32 -DDEBUG -DHAL\_TYPE=HAL\_stm32f3 -DPLATFORM=CWLITEARM -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CWLITEARM/stm32f3\_sysmem.lst -I.././simpleserial/ -I.././hal -I.././hal/stm32f3 -I.././hal/stm32f3/CMSIS -I.././hal/stm32f3/CMSIS/core -I.././hal/stm32f3/CMSIS/device -I.././hal/stm32f4/Legacy -I.././crypto/ -std=gnu99  -MMD -MP -MF .dep/stm32f3\_sysmem.o.d .././hal/stm32f3/stm32f3\_sysmem.c -o objdir-CWLITEARM/stm32f3\_sysmem.o
    .
    Assembling: .././hal/stm32f3/stm32f3\_startup.S
    arm-none-eabi-gcc -c -mcpu=cortex-m4 -I. -x assembler-with-cpp -mthumb -mfloat-abi=soft -fmessage-length=0 -ffunction-sections -DF\_CPU=7372800 -Wa,-gstabs,-adhlns=objdir-CWLITEARM/stm32f3\_startup.lst -I.././simpleserial/ -I.././hal -I.././hal/stm32f3 -I.././hal/stm32f3/CMSIS -I.././hal/stm32f3/CMSIS/core -I.././hal/stm32f3/CMSIS/device -I.././hal/stm32f4/Legacy -I.././crypto/ .././hal/stm32f3/stm32f3\_startup.S -o objdir-CWLITEARM/stm32f3\_startup.o
    .
    Linking: simpleserial-glitch-CWLITEARM.elf
    arm-none-eabi-gcc -mcpu=cortex-m4 -I. -mthumb -mfloat-abi=soft -fmessage-length=0 -ffunction-sections -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DSTM32F303xC -DSTM32F3 -DSTM32 -DDEBUG -DHAL\_TYPE=HAL\_stm32f3 -DPLATFORM=CWLITEARM -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CWLITEARM/simpleserial-glitch.o -I.././simpleserial/ -I.././hal -I.././hal/stm32f3 -I.././hal/stm32f3/CMSIS -I.././hal/stm32f3/CMSIS/core -I.././hal/stm32f3/CMSIS/device -I.././hal/stm32f4/Legacy -I.././crypto/ -std=gnu99  -MMD -MP -MF .dep/simpleserial-glitch-CWLITEARM.elf.d objdir-CWLITEARM/simpleserial-glitch.o objdir-CWLITEARM/simpleserial.o objdir-CWLITEARM/stm32f3\_hal.o objdir-CWLITEARM/stm32f3\_hal\_lowlevel.o objdir-CWLITEARM/stm32f3\_sysmem.o objdir-CWLITEARM/stm32f3\_startup.o --output simpleserial-glitch-CWLITEARM.elf --specs=nano.specs --specs=nosys.specs -T .././hal/stm32f3/LinkerScript.ld -Wl,--gc-sections -lm -Wl,-Map=simpleserial-glitch-CWLITEARM.map,--cref   -lm  
    .
    Creating load file for Flash: simpleserial-glitch-CWLITEARM.hex
    arm-none-eabi-objcopy -O ihex -R .eeprom -R .fuse -R .lock -R .signature simpleserial-glitch-CWLITEARM.elf simpleserial-glitch-CWLITEARM.hex
    .
    Creating load file for Flash: simpleserial-glitch-CWLITEARM.bin
    arm-none-eabi-objcopy -O binary -R .eeprom -R .fuse -R .lock -R .signature simpleserial-glitch-CWLITEARM.elf simpleserial-glitch-CWLITEARM.bin
    .
    Creating load file for EEPROM: simpleserial-glitch-CWLITEARM.eep
    arm-none-eabi-objcopy -j .eeprom --set-section-flags=.eeprom="alloc,load" \
    --change-section-lma .eeprom=0 --no-change-warnings -O ihex simpleserial-glitch-CWLITEARM.elf simpleserial-glitch-CWLITEARM.eep \|\| exit 0
    .
    Creating Extended Listing: simpleserial-glitch-CWLITEARM.lss
    arm-none-eabi-objdump -h -S -z simpleserial-glitch-CWLITEARM.elf > simpleserial-glitch-CWLITEARM.lss
    .
    Creating Symbol Table: simpleserial-glitch-CWLITEARM.sym
    arm-none-eabi-nm -n simpleserial-glitch-CWLITEARM.elf > simpleserial-glitch-CWLITEARM.sym
    Size after:
       text	   data	    bss	    dec	    hex	filename
       5552	      8	   1368	   6928	   1b10	simpleserial-glitch-CWLITEARM.elf
    +--------------------------------------------------------
    + Default target does full rebuild each time.
    + Specify buildtarget == allquick == to avoid full rebuild
    +--------------------------------------------------------
    +--------------------------------------------------------
    + Built for platform CW-Lite Arm \(STM32F3\) with:
    + CRYPTO\_TARGET = NONE
    + CRYPTO\_OPTIONS = 
    +--------------------------------------------------------
    make[1]: Leaving directory '/home/cwtests/chipwhisperer/hardware/victims/firmware/simpleserial-glitch'




**In [4]:**

.. code:: ipython3

    fw_path = "../../../hardware/victims/firmware/simpleserial-glitch/simpleserial-glitch-{}.hex".format(PLATFORM)
    cw.program_target(scope, prog, fw_path)
    if SS_VER == 'SS_VER_2_1':
        target.reset_comms()


**Out [4]:**



.. parsed-literal::

    Detected known STMF32: STM32F302xB(C)/303xB(C)
    Extended erase (0x44), this can take ten seconds or more
    Attempting to program 5559 bytes at 0x8000000
    STM32F Programming flash...
    STM32F Reading flash...
    Verified flash OK, 5559 bytes




**In [5]:**

.. code:: ipython3

    if PLATFORM == "CWLITEXMEGA":
        def reboot_flush():            
            scope.io.pdic = False
            time.sleep(0.1)
            scope.io.pdic = "high_z"
            time.sleep(0.1)
            #Flush garbage too
            target.flush()
    else:
        def reboot_flush():            
            scope.io.nrst = False
            time.sleep(0.05)
            scope.io.nrst = "high_z"
            time.sleep(0.05)
            #Flush garbage too
            target.flush()

If we send a wrong password:


**In [6]:**

.. code:: ipython3

    #Do glitch loop
    pw = bytearray([0x00]*5)
    target.simpleserial_write('p', pw)
    
    val = target.simpleserial_read_witherrors('r', 1, glitch_timeout=10)#For loop check
    valid = val['valid']
    if valid:
        response = val['payload']
        raw_serial = val['full_response']
        error_code = val['rv']
    
    print(val)
    #print(bytearray(val['full_response'].encode('latin-1')))


**Out [6]:**



.. parsed-literal::

    {'valid': True, 'payload': CWbytearray(b'00'), 'full\_response': CWbytearray(b'00 72 01 00 99 00'), 'rv': bytearray(b'\x00')}



We get a resposne of zero. But if we send the correct password:


**In [7]:**

.. code:: ipython3

    #Do glitch loop
    pw = bytearray([0x74, 0x6F, 0x75, 0x63, 0x68]) # correct password ASCII representation
    target.simpleserial_write('p', pw)
    
    val = target.simpleserial_read_witherrors('r', 1, glitch_timeout=10)#For loop check
    valid = val['valid']
    if valid:
        response = val['payload']
        raw_serial = val['full_response']
        error_code = val['rv']
    
    print(val)


**Out [7]:**



.. parsed-literal::

    {'valid': True, 'payload': CWbytearray(b'01'), 'full\_response': CWbytearray(b'00 72 01 01 d4 00'), 'rv': bytearray(b'\x00')}



We get a 1 back. Set the glitch up as in the previous part:


**In [8]:**

.. code:: ipython3

    scope.glitch.clk_src = 'clkgen'
    scope.glitch.trigger_src = 'ext_single'
    scope.glitch.repeat = 1
    scope.glitch.output = "clock_xor"
    scope.io.hs2 = "glitch"

Update the code below to also add an ext offset parameter:


**In [9]:**

.. code:: ipython3

    import matplotlib.pylab as plt
    import chipwhisperer.common.results.glitch as glitch
    gc = glitch.GlitchController(groups=["success", "reset", "normal"], parameters=["width", "offset", "ext_offset"])
    gc.display_stats()


**Out [9]:**


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

    FloatSlider(value=0.0, continuous_update=False, description='ext_offset setting:', disabled=True, max=10.0, re…


And make a glitch loop. Make sure you use some successful settings that
you found in the previous lab, since it will make this one much shorter!

One change you probably want to make is to add a scan for ext\_offset.
The number of places we can insert a successful glitch has gone way
down. Doing this will also be very important for future labs.


**In [10]:**

.. code:: ipython3

    from importlib import reload
    import chipwhisperer.common.results.glitch as glitch
    from tqdm.notebook import tqdm
    import re
    import struct
    sample_size = 1
    gc.set_range("width", 2, 14)
    gc.set_range("offset", 0.4, 14)
    gc.set_range("ext_offset", 0, 41)
    if PLATFORM == "CWLITEXMEGA":
        gc.set_range("width", 45, 49.8)
        gc.set_range("offset", -46, -49.8)
        gc.set_range("ext_offset", 4, 20)
        sample_size = 10
    if PLATFORM == "CW308_STM32F4":
        gc.set_range("width", 0.4, 10)
        gc.set_range("offset", 40, 49.8)
    step = 0.4
    gc.set_global_step(step)
    scope.glitch.repeat = 1
    reboot_flush()
    broken = False
    
    
    
    for glitch_settings in gc.glitch_values():
        scope.glitch.offset = glitch_settings[1]
        scope.glitch.width = glitch_settings[0]
        scope.glitch.ext_offset = glitch_settings[2]
        for i in range(sample_size):
            if scope.adc.state:
                # can detect crash here (fast) before timing out (slow)
                print("Trigger still high!")
                gc.add("reset", (scope.glitch.width, scope.glitch.offset, scope.glitch.ext_offset))
                #plt.plot(lwid, loff, 'xr', alpha=1)
                #fig.canvas.draw()
    
                #Device is slow to boot?
                reboot_flush()
    
            scope.arm()
            target.simpleserial_write('p', bytearray([0]*5))
    
            ret = scope.capture()
    
    
            if ret:
                print('Timeout - no trigger')
                gc.add("reset", (scope.glitch.width, scope.glitch.offset, scope.glitch.ext_offset))
    
                #Device is slow to boot?
                reboot_flush()
    
            else:
                val = target.simpleserial_read_witherrors('r', 1, glitch_timeout=10, timeout=50)#For loop check
                if val['valid'] is False:
                    gc.add("reset", (scope.glitch.width, scope.glitch.offset, scope.glitch.ext_offset))
                    #plt.plot(scope.glitch.width, scope.glitch.offset, 'xr', alpha=1)
                    #fig.canvas.draw()
                else:
    
                    if val['payload'] == bytearray([1]): #for loop check
                        broken = True
                        gc.add("success", (scope.glitch.width, scope.glitch.offset, scope.glitch.ext_offset))
                        print(val['payload'])
                        print(scope.glitch.width, scope.glitch.offset, scope.glitch.ext_offset)
                        print("🐙", end="")
                        break
                    else:
                        gc.add("normal", (scope.glitch.width, scope.glitch.offset, scope.glitch.ext_offset))
        if broken:
            break


**Out [10]:**



.. parsed-literal::

    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    CWbytearray(b'01')
    1.953125 7.421875 11
    🐙



**In [11]:**

.. code:: ipython3

    scope.dis()
    target.dis()


**In [12]:**

.. code:: ipython3

    assert broken is True
