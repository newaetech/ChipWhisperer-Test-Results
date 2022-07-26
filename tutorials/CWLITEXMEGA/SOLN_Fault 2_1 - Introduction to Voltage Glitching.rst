Part 2, Topic 1: Introduction to Voltage Glitching (MAIN)
=========================================================



**SUMMARY:** *Similarly to clock glitching, inserting brief glitches
into the power line of an embedded device can result in skipped
instructions and corrupted results. Besides providing a more reliable
glitch on some targets when compared to clock glitching, voltage
glitching also has the advanatage that the Vcc pins on chips are always
accessable. This won't be covered in this course, but it can also be
used to glitch a device asynchronous to its clock.*

**LEARNING OUTCOMES:**

-  Understanding voltage glitch settings
-  Building a voltage glitch and crash map.
-  Modifying glitch circuit to increase glitch success

Voltage Glitch Hardware
-----------------------

The ChipWhisperer uses the same hardware block for both voltage and
clock glitching, with the only difference being where the glitch output
is routed to. Instead of routing to HS2, voltage glitching is performed
by routing the glitch to either the ``glitch_hp`` transistor or the
``glitch_lp`` transistor. This can be done via the following API calls:

.. code:: python

    scope.io.glitch_hp = True #enable HP glitch
    scope.io.glitch_hp = False #disable LP glitch
    scope.io.glitch_lp = True #enable LP glitch
    scope.io.glitch_lp = False #disable LP glitch

While the hardware block are the same, you'll need to change how it's
configued. You wouldn't want to try routing ``"clock_xor"`` to the
glitch transistor and oscillate Vcc like the device's clock! Instead,
the following two output settings are best suited to voltage glitching:

1. ``"glitch_only"`` - insert a glitch for a portion of a clock cycle
   based on ``scope.glitch.width`` and ``scope.glitch.offset``
2. ``"enable_only"`` - insert a glitch for an entire clock cycle

Typically, the ``"enable_only"`` setting will be too powerful for most
devices. One situation where it outshines ``"glitch_only"`` is in
glitching asychronous to the target's clock. An example of this is
glitching a target with an internal clock. In this case, the
ChipWhisperer's clock can be boosted far above the target's to insert a
precise glitch, with ``repeat`` functioning as ``width`` and
``ext_offset`` functioning as ``offset``.

Voltage Glitching vs. Clock Glitching
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Voltage glitching has some obvious benefits over clock glitching, such
as working for a wider varitey of targets, but its downsides are less
obvious. One of the biggest is how much it depends on the actual glitch
circuit itself. With clock glitching, it's relatively easy to insert a
glitch - there's nothing external trying to keep the clock at a certain
voltage level. This is very different for a target's power pins. When we
try to drop the power pin to ground, there's a lot of stuff fighting us
to keep the power pin at the correct voltage, such as decoupling
capacitors, bulk supply capacitors, and the voltage regulator supplying
the voltage. This means when we make small changes to the glitch
circuit, the glitch settings and even our ability to insert a glitch at
all completely change! Consider glitching a target on the CW308 UFO
board. If you switch your coaxial cable length from 20cm to 40 cm,
you'll need to find entirely new glitch settings to repeat the attack
(if it's still even possible). This is quite easy to see on an
oscilloscope or using the ChipWhisperer's ADC: longer cables and lower
valued shunt resistors will make the glitch less sharp and increase
ringing.

While your first thought might be to go for as sharp a glitch as
possible, this often won't result in a high glitch success rate. If
you're unable to find any working glitches with your current setup, it
might be worth changing you hardware setup a bit. For example, on the
ChipWhisperer Lite 1 part, you can desolder SJ5 and solder header pins
to JP6. Even just connecting these pins with a jumper will have
different glitch behaviour than with a soldered SJ5.

You can refer to the training slides for more information about finding
good glitch settings, as well as more on the theory side of voltage
glitching.

The Lab
~~~~~~~

To introduce you to volatge glitching and find some settings, we're
going to walk back through the clock glitching loop lab. You may want to
capture some power traces while you're first experimenting with glitches
to see what effects different glitch widths have on the power trace.
Another thing to keep in mind is that targets often won't tolerate the
Vcc pin dropping for an extended period of time without crashing - once
you see the target start to crash, you won't see much else with larger
widths.

One thing you might have to change is the glitch repeat value. Depending
on how wide your glitch is, the voltage at the power pin may not recover
by the time the next glitch is inserted. This can have to effect of
increasing subsequent glitches' strength, which may or may not be
desirable. Since glitches inserted with repeat > 1 have different
strength, it's a good idea to scan through ext\_offset as well.

Higher Frequency Glitching
~~~~~~~~~~~~~~~~~~~~~~~~~~

The XMEGA target, and to a lesser extent the STM32F3, is very difficult
to glitch with the default ChipWhisperer settings. Try bumping the clock
frequency to 24MHz for the STM32 or 32MHz for the XMEGA and use a repeat
5-10 with both the high power and low power glitches active. You'll need
to adjust the baud rate by the same proportion as the clock.

Another setup that seems to work with the XMEGA is SJ5 unsoldered, JP6
jumpered, high+low power glitch, 32MHz, and repeat=5.

Disabling Logging
~~~~~~~~~~~~~~~~~

When glitching (or just running normally in earlier labs), you may have
seen various warnings from loggers ChipWhisperer uses. This often has
useful information, especially if things don't work right, but for
voltage glitching especially, it mostly clutters up any print output you
have. As such, we'll disable logging for the voltage glitching labs:

.. code:: python

    cw.set_all_log_levels(cw.logging.CRITICAL)

You can reenable logging via

.. code:: python

    cw.set_all_log_levels(cw.logging.WARNING)


**In [1]:**

.. code:: ipython3

    SCOPETYPE = 'OPENADC'
    PLATFORM = 'CWLITEXMEGA'
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
        scope = cw.scope(hw_location=(1, 99))
    
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
        scope = cw.scope(hw_location=(1, 99))
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
    rm -f -- simpleserial-glitch-CWLITEXMEGA.hex
    rm -f -- simpleserial-glitch-CWLITEXMEGA.eep
    rm -f -- simpleserial-glitch-CWLITEXMEGA.cof
    rm -f -- simpleserial-glitch-CWLITEXMEGA.elf
    rm -f -- simpleserial-glitch-CWLITEXMEGA.map
    rm -f -- simpleserial-glitch-CWLITEXMEGA.sym
    rm -f -- simpleserial-glitch-CWLITEXMEGA.lss
    rm -f -- objdir-CWLITEXMEGA/\*.o
    rm -f -- objdir-CWLITEXMEGA/\*.lst
    rm -f -- simpleserial-glitch.s simpleserial.s XMEGA\_AES\_driver.s uart.s usart\_driver.s xmega\_hal.s
    rm -f -- simpleserial-glitch.d simpleserial.d XMEGA\_AES\_driver.d uart.d usart\_driver.d xmega\_hal.d
    rm -f -- simpleserial-glitch.i simpleserial.i XMEGA\_AES\_driver.i uart.i usart\_driver.i xmega\_hal.i
    make[1]: '.dep' is up to date.
    make[1]: Leaving directory '/home/cwtests/chipwhisperer/hardware/victims/firmware/simpleserial-glitch'
    make begin gccversion build sizeafter fastnote end
    make[1]: Entering directory '/home/cwtests/chipwhisperer/hardware/victims/firmware/simpleserial-glitch'
    SS\_VER set to SS\_VER\_2\_1
    .
    Welcome to another exciting ChipWhisperer target build!!
    avr-gcc (GCC) 5.4.0
    Copyright (C) 2015 Free Software Foundation, Inc.
    This is free software; see the source for copying conditions.  There is NO
    warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
    
    .
    Compiling C: simpleserial-glitch.c
    avr-gcc -c -mmcu=atxmega128d3 -I. -fpack-struct -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_xmega -DPLATFORM=CWLITEXMEGA -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CWLITEXMEGA/simpleserial-glitch.lst -I.././simpleserial/ -I.././hal -I.././hal/xmega -I.././crypto/ -std=gnu99  -MMD -MP -MF .dep/simpleserial-glitch.o.d simpleserial-glitch.c -o objdir-CWLITEXMEGA/simpleserial-glitch.o
    .
    Compiling C: .././simpleserial/simpleserial.c
    avr-gcc -c -mmcu=atxmega128d3 -I. -fpack-struct -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_xmega -DPLATFORM=CWLITEXMEGA -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CWLITEXMEGA/simpleserial.lst -I.././simpleserial/ -I.././hal -I.././hal/xmega -I.././crypto/ -std=gnu99  -MMD -MP -MF .dep/simpleserial.o.d .././simpleserial/simpleserial.c -o objdir-CWLITEXMEGA/simpleserial.o
    .
    Compiling C: .././hal/xmega/XMEGA\_AES\_driver.c
    avr-gcc -c -mmcu=atxmega128d3 -I. -fpack-struct -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_xmega -DPLATFORM=CWLITEXMEGA -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CWLITEXMEGA/XMEGA\_AES\_driver.lst -I.././simpleserial/ -I.././hal -I.././hal/xmega -I.././crypto/ -std=gnu99  -MMD -MP -MF .dep/XMEGA\_AES\_driver.o.d .././hal/xmega/XMEGA\_AES\_driver.c -o objdir-CWLITEXMEGA/XMEGA\_AES\_driver.o
    .
    Compiling C: .././hal/xmega/uart.c
    avr-gcc -c -mmcu=atxmega128d3 -I. -fpack-struct -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_xmega -DPLATFORM=CWLITEXMEGA -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CWLITEXMEGA/uart.lst -I.././simpleserial/ -I.././hal -I.././hal/xmega -I.././crypto/ -std=gnu99  -MMD -MP -MF .dep/uart.o.d .././hal/xmega/uart.c -o objdir-CWLITEXMEGA/uart.o
    .
    Compiling C: .././hal/xmega/usart\_driver.c
    avr-gcc -c -mmcu=atxmega128d3 -I. -fpack-struct -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_xmega -DPLATFORM=CWLITEXMEGA -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CWLITEXMEGA/usart\_driver.lst -I.././simpleserial/ -I.././hal -I.././hal/xmega -I.././crypto/ -std=gnu99  -MMD -MP -MF .dep/usart\_driver.o.d .././hal/xmega/usart\_driver.c -o objdir-CWLITEXMEGA/usart\_driver.o
    .
    Compiling C: .././hal/xmega/xmega\_hal.c
    avr-gcc -c -mmcu=atxmega128d3 -I. -fpack-struct -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_xmega -DPLATFORM=CWLITEXMEGA -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CWLITEXMEGA/xmega\_hal.lst -I.././simpleserial/ -I.././hal -I.././hal/xmega -I.././crypto/ -std=gnu99  -MMD -MP -MF .dep/xmega\_hal.o.d .././hal/xmega/xmega\_hal.c -o objdir-CWLITEXMEGA/xmega\_hal.o
    .
    Linking: simpleserial-glitch-CWLITEXMEGA.elf
    avr-gcc -mmcu=atxmega128d3 -I. -fpack-struct -gdwarf-2 -DSS\_VER=SS\_VER\_2\_1 -DHAL\_TYPE=HAL\_xmega -DPLATFORM=CWLITEXMEGA -DF\_CPU=7372800UL -DSS\_VER\_2\_0=2 -DSS\_VER\_2\_1=3 -DSS\_VER\_1\_1=1 -DSS\_VER\_1\_0=0 -Os -funsigned-char -funsigned-bitfields -fshort-enums -Wall -Wstrict-prototypes -Wa,-adhlns=objdir-CWLITEXMEGA/simpleserial-glitch.o -I.././simpleserial/ -I.././hal -I.././hal/xmega -I.././crypto/ -std=gnu99  -MMD -MP -MF .dep/simpleserial-glitch-CWLITEXMEGA.elf.d objdir-CWLITEXMEGA/simpleserial-glitch.o objdir-CWLITEXMEGA/simpleserial.o objdir-CWLITEXMEGA/XMEGA\_AES\_driver.o objdir-CWLITEXMEGA/uart.o objdir-CWLITEXMEGA/usart\_driver.o objdir-CWLITEXMEGA/xmega\_hal.o --output simpleserial-glitch-CWLITEXMEGA.elf -Wl,-Map=simpleserial-glitch-CWLITEXMEGA.map,--cref   -lm  
    .
    Creating load file for Flash: simpleserial-glitch-CWLITEXMEGA.hex
    avr-objcopy -O ihex -R .eeprom -R .fuse -R .lock -R .signature simpleserial-glitch-CWLITEXMEGA.elf simpleserial-glitch-CWLITEXMEGA.hex
    .
    Creating load file for Flash: simpleserial-glitch-CWLITEXMEGA.bin
    avr-objcopy -O binary -R .eeprom -R .fuse -R .lock -R .signature simpleserial-glitch-CWLITEXMEGA.elf simpleserial-glitch-CWLITEXMEGA.bin
    .
    Creating load file for EEPROM: simpleserial-glitch-CWLITEXMEGA.eep
    avr-objcopy -j .eeprom --set-section-flags=.eeprom="alloc,load" \
    --change-section-lma .eeprom=0 --no-change-warnings -O ihex simpleserial-glitch-CWLITEXMEGA.elf simpleserial-glitch-CWLITEXMEGA.eep \|\| exit 0
    .
    Creating Extended Listing: simpleserial-glitch-CWLITEXMEGA.lss
    avr-objdump -h -S -z simpleserial-glitch-CWLITEXMEGA.elf > simpleserial-glitch-CWLITEXMEGA.lss
    .
    Creating Symbol Table: simpleserial-glitch-CWLITEXMEGA.sym
    avr-nm -n simpleserial-glitch-CWLITEXMEGA.elf > simpleserial-glitch-CWLITEXMEGA.sym
    Size after:
       text	   data	    bss	    dec	    hex	filename
       2490	      6	     82	   2578	    a12	simpleserial-glitch-CWLITEXMEGA.elf
    +--------------------------------------------------------
    + Default target does full rebuild each time.
    + Specify buildtarget == allquick == to avoid full rebuild
    +--------------------------------------------------------
    +--------------------------------------------------------
    + Built for platform CW-Lite XMEGA with:
    + CRYPTO\_TARGET = NONE
    + CRYPTO\_OPTIONS = 
    +--------------------------------------------------------
    make[1]: Leaving directory '/home/cwtests/chipwhisperer/hardware/victims/firmware/simpleserial-glitch'




**In [4]:**

.. code:: ipython3

    fw_path = "../../../hardware/victims/firmware/simpleserial-glitch/simpleserial-glitch-{}.hex".format(PLATFORM)
    cw.program_target(scope, prog, fw_path)
    if SS_VER=="SS_VER_2_1":
        target.reset_comms()


**Out [4]:**



.. parsed-literal::

    XMEGA Programming flash...
    XMEGA Reading flash...
    Verified flash OK, 2495 bytes




**In [5]:**

.. code:: ipython3

    if PLATFORM == "CWLITEXMEGA":
        scope.clock.clkgen_freq = 32E6
        if SS_VER=='SS_VER_2_1':
            target.baud = 230400*32/7.37
        else:
            target.baud = 38400*32/7.37
        def reboot_flush():            
            scope.io.pdic = False
            time.sleep(0.1)
            scope.io.pdic = "high_z"
            time.sleep(0.1)
            #Flush garbage too
            target.flush()
    else:
        scope.clock.clkgen_freq = 24E6
        if SS_VER=='SS_VER_2_1':
            target.baud = 230400*24/7.37
        else:
            target.baud = 38400*24/7.37
        time.sleep(0.1)
        def reboot_flush():            
            scope.io.nrst = False
            time.sleep(0.05)
            scope.io.nrst = "high_z"
            time.sleep(0.05)
            #Flush garbage too
            target.flush()


**In [6]:**

.. code:: ipython3

    reboot_flush()
    scope.arm()
    target.simpleserial_write("g", bytearray([]))
    scope.capture()
    val = target.simpleserial_read_witherrors('r', 4, glitch_timeout=10)#For loop check
    valid = val['valid']
    if valid:
        response = val['payload']
        raw_serial = val['full_response']
        error_code = val['rv']
    
    print(val)


**Out [6]:**



.. parsed-literal::

    {'valid': True, 'payload': CWbytearray(b'c4 09 00 00'), 'full\_response': CWbytearray(b'00 72 04 c4 09 00 00 15 00'), 'rv': bytearray(b'\x00')}




**In [7]:**

.. code:: ipython3

    import chipwhisperer.common.results.glitch as glitch
    gc = glitch.GlitchController(groups=["success", "reset", "normal"], parameters=["width", "offset", "ext_offset"])
    gc.display_stats()


**Out [7]:**


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



**In [8]:**

.. code:: ipython3

    scope.glitch.clk_src = "clkgen" # set glitch input clock
    scope.glitch.output = "glitch_only" # glitch_out = clk ^ glitch
    scope.glitch.trigger_src = "ext_single" # glitch only after scope.arm() called
    if PLATFORM == "CWLITEXMEGA":
        scope.io.glitch_lp = True
        scope.io.glitch_hp = True
    elif PLATFORM == "CWLITEARM":
        scope.io.glitch_lp = True
        scope.io.glitch_hp = True
    elif PLATFORM == "CW308_STM32F3":
        scope.io.glitch_hp = True
        scope.io.glitch_lp = True

Some tips for finding good glitches:

1. There's a lot of stuff fighting our glitch this time - unlike the
   clock line, the Vcc rail isn't supposed to oscillate! As such shorter
   glitches will have no effect. A good strategy can often to be to
   increase the minimum glitch width until you start seeing consistant
   crashes, then backing off on the width.
2. The repeat parameter behaves very differently than with voltage
   glitching - at the boosted clock rate, the Vcc often won't recover
   before the next glitch. Try different repeat values as well.
3. We've built in a success/reset measurement into the glitch loop. Once
   you've found some glitch spots, this will help you evaluate which
   ones are best for your target.

It can take a very long time to do go through the full search space, so
you may want to stop after you get a certain number of succeses. By
default here, it will be 1, but you may want to change it to 10, 20, or
go even higher.


**In [9]:**

.. code:: ipython3

    TOTAL_SUCCESSES = 1


**In [10]:**

.. code:: ipython3

    from importlib import reload
    import chipwhisperer.common.results.glitch as glitch
    from tqdm.notebook import trange
    import struct
    
    #disable logging
    cw.set_all_log_levels(cw.logging.CRITICAL)
    
    g_step = 0.4
    if PLATFORM=="CWLITEXMEGA":
        gc.set_range("width", 45.7, 47.8)
        gc.set_range("offset", 2.8, 10)
        gc.set_range("ext_offset", 2, 4)
        scope.glitch.repeat = 10
    elif PLATFORM == "CWLITEARM":
        #should also work for the bootloader memory dump
        gc.set_range("width", 34, 36)
        gc.set_range("offset", -10, 10)
        gc.set_range("ext_offset", 6, 7)
        scope.glitch.repeat = 7
    elif PLATFORM == "CW308_STM32F3":
        #these specific settings seem to work well for some reason
        #also works for the bootloader memory dump
        gc.set_range("ext_offset", 9, 12)
        gc.set_range("width", 47.6, 49.6)
        gc.set_range("offset", -19, -21.5)
        scope.glitch.repeat = 5
    
    gc.set_global_step(g_step)
    
    scope.adc.timeout = 0.5
    
    reboot_flush()
    sample_size = 10
    loff = scope.glitch.offset
    lwid = scope.glitch.width
    total_successes = 0
    for glitch_setting in gc.glitch_values():
        scope.glitch.offset = glitch_setting[1]
        scope.glitch.width = glitch_setting[0]
        scope.glitch.ext_offset = glitch_setting[2]
        #print(scope.glitch.ext_offset)
        successes = 0
        resets = 0
        for i in range(10):
            target.flush()
            if scope.adc.state:
                # can detect crash here (fast) before timing out (slow)
                #print("Trigger still high!")
                gc.add("reset", (scope.glitch.width, scope.glitch.offset, scope.glitch.ext_offset))
    
                #Device is slow to boot?
                reboot_flush()
                resets += 1
                
            scope.arm()
            
            #Do glitch loop
            target.simpleserial_write("g", bytearray([]))
            
            ret = scope.capture()
            
            
            
            
            scope.io.glitch_hp = False
            scope.io.glitch_hp = True
            scope.io.glitch_lp = False
            scope.io.glitch_lp = True
            if ret:
                #print('Timeout - no trigger')
                gc.add("reset", (scope.glitch.width, scope.glitch.offset, scope.glitch.ext_offset))
                resets += 1
    
                #Device is slow to boot?
                reboot_flush()
    
            else:
                val = target.simpleserial_read_witherrors('r', 4, glitch_timeout=10, timeout=50)#For loop check
                if val['valid'] is False:
                    gc.add("reset", (scope.glitch.width, scope.glitch.offset, scope.glitch.ext_offset))
                    reboot_flush()
                    resets += 1
                    #print(val)
                else:
                    gcnt = struct.unpack("<I", val['payload'])[0]
                    
                    if gcnt != 2500: #for loop check
                        gc.add("success", (scope.glitch.width, scope.glitch.offset, scope.glitch.ext_offset))
                        successes += 1
                    else:
                        gc.add("normal", (scope.glitch.width, scope.glitch.offset, scope.glitch.ext_offset))
        if successes > 0:                
            print("successes = {}, resets = {}, offset = {}, width = {}, ext_offset = {}".format(successes, resets, scope.glitch.offset, scope.glitch.width, scope.glitch.ext_offset))
            total_successes += successes
        if total_successes > TOTAL_SUCCESSES: #increase if you want to check more locations
            break
    print("Done glitching")
    #enable logging
    cw.set_all_log_levels(cw.logging.WARNING)


**Out [10]:**



.. parsed-literal::

    successes = 1, resets = 9, offset = 4.6875, width = 47.265625, ext\_offset = 2
    successes = 1, resets = 9, offset = 5.859375, width = 47.265625, ext\_offset = 2
    Done glitching




**In [11]:**

.. code:: ipython3

    %matplotlib inline
    gc.results.plot_2d(plotdots={"success":"+g", "reset":"xr", "normal":None})


**Out [11]:**


.. image:: img/OPENADC-CWLITEXMEGA-SOLN_Fault2_1-IntroductiontoVoltageGlitching_15_0.png



**In [12]:**

.. code:: ipython3

    scope.dis()
    target.dis()


**In [13]:**

.. code:: ipython3

    assert total_successes >= 1
