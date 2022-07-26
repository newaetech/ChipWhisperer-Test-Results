Part 1, Topic 1: Introduction to Clock Glitching (MAIN)
=======================================================



**SUMMARY:** *Microcontrollers and FPGAs have a number of operating
conditions that must be met in order for the device to work properly.
Outside of these conditions, devices will begin to malfunction, with
more extreme violations causing the device to stop entirely or even
become damaged. By going outside these operating conditions for very
small amounts of time, we can cause a varitey of temporary malfunctions*

*In this lab, we'll explore clock glitching, which inserts short
glitches into a device's clock. This will be used to get a target that's
summing numbers in a loop to arrive at the wrong result.*

**LEARNING OUTCOMES:**

-  Understand effects of clock glitching
-  Exploring ChipWhisperer's glitch module
-  Using clock glitching to disrupt a target's algorithm

Clock Glitching Theory
----------------------

Digital hardware devices almost always expect some form of reliable
clock. We can manipulate the clock being presented to the device to
cause unintended behaviour. We'll be concentrating on microcontrollers
here, however other digital devices (e.g. hardware encryption
accelerators) can also have faults injected using this technique.

Consider a microcontroller first. The following figure is an excerpt
from the Atmel AVR ATMega328P datasheet:

.. figure:: img/Mcu-unglitched.png
   :alt: A2\_1

   A2\_1

Rather than loading each instruction from FLASH and performing the
entire execution, the system has a pipeline to speed up the execution
process. This means that an instruction is being decoded while the next
one is being retrieved, as the following diagram shows:

.. figure:: img/Clock-normal.png
   :alt: A2\_2

   A2\_2

But if we modify the clock, we could have a situation where the system
doesn't have enough time to actually perform an instruction. Consider
the following, where Execute #1 is effectively skipped. Before the
system has time to actually execute it another clock edge comes, causing
the microcontroller to start execution of the next instruction:

.. figure:: img/Clock-glitched.png
   :alt: A2\_3

   A2\_3

This causes the microcontroller to skip an instruction. Such attacks can
be immensely powerful in practice. Consider for example the following
code from ``linux-util-2.24``:

.. code:: c

    /*
     *   auth.c -- PAM authorization code, common between chsh and chfn
     *   (c) 2012 by Cody Maloney <cmaloney@theoreticalchaos.com>
     *
     *   this program is free software.  you can redistribute it and
     *   modify it under the terms of the gnu general public license.
     *   there is no warranty.
     *
     */

    #include "auth.h"
    #include "pamfail.h"

    int auth_pam(const char *service_name, uid_t uid, const char *username)
    {
        if (uid != 0) {
            pam_handle_t *pamh = NULL;
            struct pam_conv conv = { misc_conv, NULL };
            int retcode;

            retcode = pam_start(service_name, username, &conv, &pamh);
            if (pam_fail_check(pamh, retcode))
                return FALSE;

            retcode = pam_authenticate(pamh, 0);
            if (pam_fail_check(pamh, retcode))
                return FALSE;

            retcode = pam_acct_mgmt(pamh, 0);
            if (retcode == PAM_NEW_AUTHTOK_REQD)
                retcode =
                    pam_chauthtok(pamh, PAM_CHANGE_EXPIRED_AUTHTOK);
            if (pam_fail_check(pamh, retcode))
                return FALSE;

            retcode = pam_setcred(pamh, 0);
            if (pam_fail_check(pamh, retcode))
                return FALSE;

            pam_end(pamh, 0);
            /* no need to establish a session; this isn't a
             * session-oriented activity...  */
        }
        return TRUE;
    }

This is the login code for the Linux OS. Note that if we could skip the
check of ``if (uid != 0)`` and simply branch to the end, we could avoid
having to enter a password. This is the power of glitch attacks - not
that we are breaking encryption, but simply bypassing the entire
authentication module!

Glitch Hardware
~~~~~~~~~~~~~~~

The ChipWhisperer Glitch system uses the same synchronous methodology as
its Side Channel Analysis (SCA) capture. A system clock (which can come
from either the ChipWhisperer or the Device Under Test (DUT)) is used to
generate the glitches. These glitches are then inserted back into the
clock, although it's possible to use the glitches alone for other
purposes (i.e. for voltage glitching, EM glitching).

The generation of glitches is done with two variable phase shift
modules, configured as follows:

.. figure:: img/Glitchgen-phaseshift.png
   :alt: A2\_4

   A2\_4

In CW-Husky there is one important difference: the phase shift 1 output
is not inverted before it is ANDed with the phase shift 2 output.

The enable line is used to determine when glitches are inserted.
Glitches can be inserted continuously (useful for development) or
triggered by some event. The following figure shows how the glitch can
be muxd to output to the Device Under Test (DUT).

.. figure:: img/Glitchgen-mux.png
   :alt: A2\_5

   A2\_5

Hardware Support: CW-Lite/Pro
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The phase shift blocks use the Digital Clock Manager (DCM) blocks within
the FPGA. These blocks have limited support for run-time configuration
of parameters such as phase delay and frequency generation, and for
maximum performance the configuration must be fixed at design time. The
Xilinx-provided run-time adjustment can shift the phase only by about
+/- 5nS in 30pS increments (exact values vary with operating
conditions).

For most operating conditions this is insufficient - if attacking a
target at 7.37MHz the clock cycle would have a period of 136nS. In order
to provide a larger adjustment range, an advanced FPGA feature called
Partial Reconfiguration (PR) is used. The PR system requires special
partial bitstreams which contain modifications to the FPGA bitstream.
These are stored as two files inside a "firmware" zip which contains
both the FPGA bitstream along with a file called ``glitchwidth.p`` and a
file called ``glitchoffset.p``. If a lone bitstream is being loaded into
the FPGA (i.e. not from the zip-file), the partial reconfiguration
system is disabled, as loading incorrect partial reconfiguration files
could damage the FPGA. This damage is mostly theoretical, more likely
the FPGA will fail to function correctly.

If in the course of following this tutorial you find the FPGA appears to
stop responding (i.e. certain features no longer work correctly), it
could be the partial reconfiguration data is incorrect.

We'll look at how to interface with these features later in the
tutorial.

Hardware Support: CW-Husky
~~~~~~~~~~~~~~~~~~~~~~~~~~

The clock-generation logic in Husky's 7-series FPGA is considerably
different than the 6-series FPGAs used in CW-Lite/Pro. The DCM is gone
and replaced by the much more powerful (and power hungry...) Mixed Mode
Clock Manager (MMCM). In particular for our glitching application, MMCMs
allow fine phase shift adjustments over an unlimited range, in steps as
small as 15ps. And all this without having to dynamically reconfigure
the FPGA bitfile! For this reason, the format for specifying the glitch
offset and width is different from what it was for CW-Lite/Pro. Instead
of specifiying a percentage of the source clock period, you now specify
the actual number of phase shift steps. The duration of one phase shift
step is 1/56 of the MMCM VCO clock period, which can itself be
configured to be anyhwere in the range from 600 MHz to 1200 MHz (via
``scope.clock.pll.update_fpga_vco()``).

While the MMCM is more powerful than the DCM with respect to its
features, it also requires a lot more power. For this reason, the glitch
generation circuitry is disabled by default and must be explicitly
turned on. Fear not, Husky also uses Xilinx's XADC module to
continuously monitor its temperature, and all MMCMs are automatically
turned off at when the temperature starts getting too high, well below
dangerous levels are reached (run ``scope.XADC`` to see all its
statistics and settings).


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
        scope = cw.scope(hw_location=(5, 3))
    
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
        scope = cw.scope(hw_location=(5, 3))
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
    
    mkdir -p objdir-CWLITEARM 
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
    if SS_VER=='SS_VER_2_0':
        target.reset_comms()


**Out [4]:**



.. parsed-literal::

    Detected known STMF32: STM32F302xB(C)/303xB(C)
    Extended erase (0x44), this can take ten seconds or more
    Attempting to program 5559 bytes at 0x8000000
    STM32F Programming flash...
    STM32F Reading flash...
    Verified flash OK, 5559 bytes



We'll probably crash the target a few times while we're trying some
glitching. Create a function to reset the target:


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

Communication
-------------

For this lab, we'll be introducing a new method:
``target.simpleserial_read_witherrors()``. We're expecting a
simpleserial response back; however, glitch will often cause the target
to crash and return an invalid string. This method will handle all that
for us. It'll also tell us whether the response was valid and what the
error return code was. Use as follows:


**In [6]:**

.. code:: ipython3

    #Do glitch loop
    target.simpleserial_write('g', bytearray([]))
    
    val = target.simpleserial_read_witherrors('r', 4, glitch_timeout=10)#For loop check
    valid = val['valid']
    if valid:
        response = val['payload']
        raw_serial = val['full_response']
        error_code = val['rv']
    
    #print(bytearray(val['full_response'].encode('latin-1')))
    print(val)


**Out [6]:**



.. parsed-literal::

    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:184) Infinite loop in unstuff data
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:185) CWbytearray(b'00 72 52 45 53 45 54 20 20')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 82, 4





.. parsed-literal::

    {'valid': False, 'payload': None, 'full\_response': '\x00rRESET   \n\x05r\x04Ä\t\x01\x02\x15\x00\x03e\x01\x02ë\x00', 'rv': None}



Target Firmware
---------------

For this lab, our goal is to get the following code to preduce an
incorrect result:

.. code:: c

    uint8_t glitch_loop(uint8_t* in)
    {
        volatile uint16_t i, j;
        volatile uint32_t cnt;
        cnt = 0;
        trigger_high();
        for(i=0; i<50; i++){
            for(j=0; j<50; j++){
                cnt++;
            }
        }
        trigger_low();
        simpleserial_put('r', 4, (uint8_t*)&cnt);
        return (cnt != 2500);
    }

As you can see, we've got a simple loop. This is a really good place to
start glitching for 2 reasons:

1. We've got a really long portion of time with a lot of instructions to
   glitch. In contrast, with the Linux example we're be trying to target
   a single instruction.

2. For some glitching scenarios, we're looking for a pretty specific
   glitch effect. In the Linux example, we might be banking on the
   glitch causing the target to skip an instruction instead of
   corrupting the comparison since that's a lot more likely to get us
   where we want in the code path. For this simple loop calculation,
   pretty much any malfunction will show up in the result.

Glitch Module
-------------

All the settings/methods for the glitch module can be accessed under
``scope.glitch``. As usual, documentation for the settings and methods
can be accessed on
`ReadtheDocs <https://chipwhisperer.readthedocs.io/en/latest/api.html>`__
or with the python ``help`` command:


**In [7]:**

.. code:: ipython3

    help(scope.glitch)


**Out [7]:**



.. parsed-literal::

    Help on GlitchSettings in module chipwhisperer.capture.scopes.cwhardware.ChipWhispererGlitch object:
    
    class GlitchSettings(chipwhisperer.common.utils.util.DisableNewAttr)
     \|  GlitchSettings(cwglitch)
     \|  
     \|  Method resolution order:
     \|      GlitchSettings
     \|      chipwhisperer.common.utils.util.DisableNewAttr
     \|      builtins.object
     \|  
     \|  Methods defined here:
     \|  
     \|  \_\_init\_\_(self, cwglitch)
     \|      Initialize self.  See help(type(self)) for accurate signature.
     \|  
     \|  \_\_repr\_\_(self)
     \|      Return repr(self).
     \|  
     \|  \_\_str\_\_(self)
     \|      Return str(self).
     \|  
     \|  manualTrigger(self)
     \|  
     \|  manual\_trigger(self)
     \|      Manually trigger the glitch output.
     \|      
     \|      This trigger is most useful in Manual trigger mode, where this is the
     \|      only way to cause a glitch.
     \|  
     \|  readStatus(self)
     \|      Read the status of the two glitch DCMs.
     \|      
     \|      Returns:
     \|          A tuple with 4 elements::
     \|      
     \|           \* phase1: Phase shift of DCM1 (N/A for Husky),
     \|           \* phase2: Phase shift of DCM2 (N/A for Husky),
     \|           \* lock1: Whether DCM1 is locked,
     \|           \* lock2: Whether DCM2 is locked
     \|  
     \|  resetDCMs(self, keepPhase=True)
     \|      Reset the two glitch DCMs.
     \|      
     \|      This is automatically run after changing the glitch width or offset,
     \|      so this function is typically not necessary.
     \|  
     \|  ----------------------------------------------------------------------
     \|  Readonly properties defined here:
     \|  
     \|  actual\_num\_glitches
     \|      The number of glitches that were generated during the previous
     \|      glitch event (should equal scope.glitch.num\_glitches; for debugging).
     \|      CW-Husky only.
     \|  
     \|  mmcm\_locked
     \|      Husky only. Whether the Xilinx MMCMs used to generate glitches are
     \|      locked or not.
     \|  
     \|  phase\_shift\_steps
     \|      The number of phase shift steps per target clock period.
     \|      Husky only.
     \|      To change, modify clock.pll.update\_fpga\_vco()
     \|      
     \|      :Getter: Returns the number of steps.
     \|  
     \|  ----------------------------------------------------------------------
     \|  Data descriptors defined here:
     \|  
     \|  arm\_timing
     \|      When to arm the glitch in single-shot mode.
     \|      
     \|      If the glitch module is in "ext\_single" trigger mode, it must be armed
     \|      when the scope is armed. There are two timings for this event:
     \|      
     \|       \* "no\_glitch": The glitch module is not armed. Gives a moderate speedup to capture.
     \|       \* "before\_scope": The glitch module is armed first.
     \|       \* "after\_scope": The scope is armed first. This is the default.
     \|      
     \|      This setting may be helpful if trigger events are happening very early.
     \|      
     \|      If the glitch module is not in external trigger single-shot mode, this
     \|      setting has no effect.
     \|      
     \|      :Getter: Return the current arm timing ("before\_scope" or "after\_scope")
     \|      
     \|      :Setter: Change the arm timing
     \|      
     \|      Raises:
     \|         ValueError: if value not listed above
     \|  
     \|  clk\_src
     \|      The clock signal that the glitch DCM is using as input.
     \|      
     \|      This DCM can be clocked from three different sources:
     \|       \* "target": The HS1 clock from the target device (can also be AUX clock for Husky)
     \|       \* "clkgen": The CLKGEN DCM output (N/A for Husky)
     \|       \* "pll": Husky's on-board PLL clock (Husky only)
     \|      
     \|      :Getter:
     \|         Return the clock signal currently in use
     \|      
     \|      :Setter:
     \|         Change the glitch clock source
     \|      
     \|      Raises:
     \|         ValueError: New value not one of "target", "clkgen" or "pll"
     \|  
     \|  enabled
     \|      Husky only. Whether the Xilinx MMCMs used to generate glitches are
     \|      powered on or not. 7-series MMCMs are power hungry and are estimated
     \|      to consume half of the FPGA's power. If you run into temperature
     \|      issues and don't require glitching, you can power down these MMCMs.
     \|  
     \|  ext\_offset
     \|      How long the glitch module waits between a trigger and a glitch.
     \|      
     \|      After the glitch module is triggered, it waits for a number of clock
     \|      cycles before generating glitch pulses. This delay allows the glitch to
     \|      be inserted at a precise moment during the target's execution to glitch
     \|      specific instructions.
     \|      
     \|      For CW-Husky when scope.glitch.num\_glitches > 1, this parameter is a
     \|      list with scope.glitch.num\_glitches elements, each element
     \|      representing the ext\_offset value for the corresponding glitch,
     \|      relative to the previous glitch. If ext\_offset[i] = j, glitch i will
     \|      be issued 2+j cycles after the start of glitch i-1.
     \|      
     \|      For CW-Lite/Pro, scope.glitch.num\_glitches is not supported so this is
     \|      a simply an integer.
     \|      
     \|      Has no effect when trigger\_src = 'manual' or 'continuous'.
     \|      
     \|      .. note::
     \|          It is possible to get more precise offsets by clocking the
     \|          glitch module faster than the target board.
     \|      
     \|      This offset must be in the range [0, 2\*\*32).
     \|      
     \|      :Getter: Return the current external trigger offset(s). For CW-lite/pro
     \|         or when num\_glitches=1, this is an integer (for backwards
     \|         compatibility).  Otherwise, it is a list of integers.
     \|      
     \|      :Setter: Set the external trigger offset(s). Integer for CW-lite/pro,
     \|         list of integers for Husky.
     \|      
     \|      Raises:
     \|         TypeError: if offset not an integer, or list of integers for Husky
     \|         ValueError: if any offset outside of range [0, 2\*\*32)
     \|  
     \|  num\_glitches
     \|      The number of glitch events to generate. CW-Husky only.
     \|      
     \|      Each glitch event uses the same offset and width settings. 
     \|      Glitch event x uses repeat[x] and ext\_offset[x].
     \|      
     \|      This parameter has no effect when scope.glitch.trigger\_src is set to
     \|      "manual" or "continuous".
     \|      
     \|      Raises:
     \|         ValueError: number outside of [1, 32].
     \|  
     \|  offset
     \|      The offset from a rising clock edge to a glitch pulse rising edge.
     \|      
     \|      For CW-Husky, offset is expressed as the number of phase shift steps.
     \|      Minimum offset is obtained at 0 (rising edge of glitch aligned with
     \|      rising edge of glitch source clock). At
     \|      scope.glitch.phase\_shift\_steps/2, the glitch rising edge is aligned
     \|      with the glitch source clock falling edge. Negative values are
     \|      allowed, but -x is equivalent to scope.glitch.phase\_shift\_steps-x. The
     \|      setting rolls over (+x is equivalent to
     \|      scope.glitch.phase\_shift\_steps+x). Run the notebook in
     \|      jupyter/demos/husky\_glitch.ipynb to visualize glitch settings.
     \|      
     \|      For other capture hardware (CW-lite, CW-pro), offset is expressed 
     \|      as a percentage of one period.
     \|      A pulse may begin anywhere from -49.8% to 49.8% away from a rising
     \|      edge, allowing glitches to be swept over the entire clock cycle.
     \|      
     \|      .. warning:: very large negative offset <-45 may result in double glitches
     \|          (CW-lite/pro only).
     \|      
     \|      :Getter: Return an int (Husky) or float (CW-lite/pro) with the current
     \|          glitch offset.
     \|      
     \|      :Setter: Set the glitch offset. For CW-lite/pro, the new value is
     \|          rounded to the nearest possible offset.
     \|      
     \|      Raises:
     \|         UserWarning: value outside range [-50, 50] (value is rounded)
     \|             (CW-lite/pro only)
     \|  
     \|  offset\_fine
     \|      The fine adjustment value on the glitch offset. N/A for Husky.
     \|      
     \|      This is a dimensionless number that makes small adjustments to the
     \|      glitch pulses' offset. Valid range is [-255, 255].
     \|      
     \|      .. warning:: This value is write-only. Reads will always return 0.
     \|      
     \|      :Getter: Returns 0
     \|      
     \|      :Setter: Update the glitch fine offset
     \|      
     \|      Raises:
     \|         TypeError: if offset not an integer
     \|         ValueError: if offset is outside of [-255, 255]
     \|  
     \|  output
     \|      The type of output produced by the glitch module.
     \|      
     \|      There are 5 ways that the glitch module can combine the clock with its
     \|      glitch pulses:
     \|      
     \|       \* "clock\_only": Output only the original input clock.
     \|       \* "glitch\_only": Output only the glitch pulses - do not use the clock.
     \|       \* "clock\_or": Output is high if either the clock or glitch are high.
     \|       \* "clock\_xor": Output is high if clock and glitch are different.
     \|       \* "enable\_only": Output is high for glitch.repeat cycles.
     \|      
     \|      Some of these settings are only useful in certain scenarios:
     \|       \* Clock glitching: "clock\_or" or "clock\_xor"
     \|       \* Voltage glitching: "glitch\_only" or "enable\_only"
     \|      
     \|      :Getter: Return the current glitch output mode (one of above strings)
     \|      
     \|      :Setter: Change the glitch output mode.
     \|      
     \|      Raises:
     \|         ValueError: if value not in above strings
     \|  
     \|  repeat
     \|      The number of glitch pulses to generate per trigger.
     \|      
     \|      When the glitch module is triggered, it produces a number of pulses
     \|      that can be combined with the clock signal. This setting allows for
     \|      the glitch module to produce stronger glitches (especially during
     \|      voltage glitching).
     \|      
     \|      For CW-Husky when scope.glitch.num\_glitches > 1, this parameter is a
     \|      list with scope.glitch.num\_glitches elements, each element
     \|      representing the repeat value for the corresponding glitch. The
     \|      maximum legal value for repeat[i] is ext\_offset[i+1]+1. If an
     \|      illegal value is specified, the glitch output may be held high for
     \|      up to 8192 cycles.
     \|      
     \|      For CW-Lite/Pro, scope.glitch.num\_glitches is not supported so this is
     \|      a simply an integer.
     \|      
     \|      Has no effect when trigger\_src = 'continuous'.
     \|      
     \|      Repeat counter must be in the range [1, 8192].
     \|      
     \|      :Getter: Return the current repeat value. For CW-lite/pro or when
     \|         num\_glitches=1, this is an integer (for backwards compatibility).
     \|         Otherwise, it is a list of integers.
     \|      
     \|      :Setter: Set the repeat counter. Integer for CW-lite/pro, list of
     \|         integers for Husky.
     \|      
     \|      Raises:
     \|         TypeError: if value not an integer, or list of integers for Husky
     \|         ValueError: if any value outside [1, 8192]
     \|  
     \|  state
     \|      Glitch FSM state. CW-Husky only. For debug.
     \|      Writing any value resets the FSM to its idle state.
     \|  
     \|  trigger\_src
     \|      The trigger signal for the glitch pulses.
     \|      
     \|      The glitch module can use four different types of triggers:
     \|       \* "continuous": Constantly trigger glitches. The following
     \|          scope.glitch parameters have no bearing in this mode: ext\_offset,
     \|          repeat, num\_glitches.
     \|       \* "manual": Only trigger glitches by calling :code:\`manual\_trigger()\`. The
     \|          following scope.glitch parameters have no bearing in this mode:
     \|          ext\_offset, num\_glitches. In this mode, calling :code:\`scope.arm()\` will
     \|          trigger a glitch as well.
     \|       \* "ext\_single": Use the trigger module. Once the scope is armed, one
     \|          set of glitch events is emitted when the trigger condition is
     \|          satisfied. Subsequent trigger conditions are ignored unless the
     \|          scope is re-armed.
     \|       \* "ext\_continuous": Use the trigger module. A set of glitch events is
     \|          emitted each time the trigger condition is satisfied, whether or
     \|          not the scope is armed.
     \|      
     \|       .. warning:: calling :code:\`scope.arm()\` in manual gitch mode will cause a glitch to trigger.
     \|      
     \|      :Getter: Return the current trigger source.
     \|      
     \|      :Setter: Change the trigger source.
     \|      
     \|      Raises:
     \|         ValueError: value not listed above.
     \|  
     \|  width
     \|      The width of a single glitch pulse.
     \|      
     \|      For CW-Husky, width is expressed as the number of phase shift steps.
     \|      Minimum width is obtained at 0. Maximum width is obtained at
     \|      scope.glitch.phase\_shift\_steps/2. Negative values are allowed, but -x
     \|      is equivalent to scope.glitch.phase\_shift\_steps-x. The setting rolls
     \|      over (+x is equivalent to scope.glitch.phase\_shift\_steps+x). Run the
     \|      notebook in jupyter/demos/husky\_glitch.ipynb to visualize glitch
     \|      settings.
     \|      
     \|      For other capture hardware (CW-lite, CW-pro), width is expressed as a
     \|      percentage of one period. One pulse can range from -49.8% to roughly
     \|      49.8% of a period. The system may not be reliable at 0%. Note that
     \|      negative widths are allowed; these act as if they are positive widths
     \|      on the other half of the clock cycle.
     \|      
     \|      :Getter: Return an int (Husky) or float (others) with the current
     \|          glitch width.
     \|      
     \|      :Setter: Update the glitch pulse width. For CW-lite/pro, the value is
     \|          adjusted to the closest possible glitch width.
     \|      
     \|      Raises:
     \|         UserWarning: Width outside of [-49.8, 49.8]. The value is rounded
     \|             to one of these. (CW-lite/pro only)
     \|  
     \|  width\_fine
     \|      The fine adjustment value on the glitch width. N/A for Husky.
     \|      
     \|      This is a dimensionless number that makes small adjustments to the
     \|      glitch pulses' width. Valid range is [-255, 255].
     \|      
     \|      .. warning:: This value is write-only. Reads will always return 0.
     \|      
     \|      :Getter: Returns 0
     \|      
     \|      :Setter: Update the glitch fine width
     \|      
     \|      Raises:
     \|         TypeError: offset not an integer
     \|         ValueError: offset is outside of [-255, 255]
     \|  
     \|  ----------------------------------------------------------------------
     \|  Methods inherited from chipwhisperer.common.utils.util.DisableNewAttr:
     \|  
     \|  \_\_setattr\_\_(self, name, value)
     \|      Implement setattr(self, name, value).
     \|  
     \|  add\_read\_only(self, name)
     \|  
     \|  disable\_newattr(self)
     \|  
     \|  disable\_strict\_newattr(self)
     \|  
     \|  enable\_newattr(self)
     \|  
     \|  remove\_read\_only(self, name)
     \|  
     \|  ----------------------------------------------------------------------
     \|  Data descriptors inherited from chipwhisperer.common.utils.util.DisableNewAttr:
     \|  
     \|  \_\_dict\_\_
     \|      dictionary for instance variables (if defined)
     \|  
     \|  \_\_weakref\_\_
     \|      list of weak references to the object (if defined)
     \|  
     \|  ----------------------------------------------------------------------
     \|  Data and other attributes inherited from chipwhisperer.common.utils.util.DisableNewAttr:
     \|  
     \|  \_\_annotations\_\_ = {'\_read\_only\_attrs': typing.List[str]}
    



Some of the important settings we'll want to look at here are:

-  clk\_src > The clock signal that the glitch DCM is using as input.
   Can be set to "target" or "clkgen" In this case, we'll be providing
   the clock to the target, so we'll want this set to "clkgen"
-  offset > Where in the output clock to place the glitch. Can be in the
   range ``[-50, 50]``. Often, we'll want to try many offsets when
   trying to glitch a target.
-  width > How wide to make the glitch. Can be in the range
   ``[-50, 50]``, though there is no reason to use widths < 0. Wider
   glitches more easily cause glitches, but are also more likely to
   crash the target, meaning we'll often want to try a range of widths
   when attacking a target.
-  output > The output produced by the glitch module. For clock
   glitching, clock\_xor is often the most useful option.
-  ext\_offset > The number of clock cycles after the trigger to put the
   glitch.
-  repeat > The number of clock cycles to repeat the glitch for. Higher
   values increase the number of instructions that can be glitched, but
   often increase the risk of crashing the target.
-  trigger\_src > How to trigger the glitch. For this tutorial, we want
   to automatically trigger the glitch from the trigger pin only after
   arming the ChipWhipserer, so we'll use ``ext_single``

In addition, we'll need to tell ChipWhipserer to use the glitch module's
output as a clock source for the target by setting
``scope.io.hs2 = "glitch"``. We'll also setup a large ``repeat`` to make
glitching easier. Finally, we'll also use a ``namedtuple`` to make
looping through parameters simpler.

CW Glitch Controller
--------------------

To make creating a glitch loop easier, ChipWhisperer includes a glitch
controller. We'll start of by initializing with with different potential
results of the attack. You define these to be whatever you want, but
typically "success", "reset", and "normal" will be sufficient. We also
need to tell it what glitch parameters we want to scan through, in this
case width and offset:


**In [8]:**

.. code:: ipython3

    import chipwhisperer.common.results.glitch as glitch
    gc = glitch.GlitchController(groups=["success", "reset", "normal"], parameters=["width", "offset"])

One of the niceties of the glitch controller is that it can display our
current settings. This will update in real time as we use the glitch
controller!


**In [9]:**

.. code:: ipython3

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


We can also make a settings map that can also update in realtime as
well:


**In [10]:**

.. code:: ipython3

    %matplotlib inline
    import matplotlib.pylab as plt
    fig = plt.figure()


**Out [10]:**


.. parsed-literal::

    <Figure size 432x288 with 0 Axes>



**In [11]:**

.. code:: ipython3

    ## to update the plot:
    plt.plot(-5, 5, '.')
    fig.canvas.draw()


**Out [11]:**


.. image:: img/_20_0.png


You can set ranges for each glitch setting:


**In [12]:**

.. code:: ipython3

    gc.set_range("width", -5, 5)
    gc.set_range("offset", -5, 5)

Each setting moves from min to max based on the global step:


**In [13]:**

.. code:: ipython3

    gc.set_global_step([5.0, 2.5])

We can print out all the glitch settings to see how this looks:


**In [14]:**

.. code:: ipython3

    for glitch_setting in gc.glitch_values():
        print("offset: {:4.1f}; width: {:4.1f}".format(glitch_setting[1], glitch_setting[0]))


**Out [14]:**



.. parsed-literal::

    offset: -5.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  5.0; width: -5.0
    offset: -5.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  5.0; width:  0.0
    offset: -5.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  5.0; width:  5.0
    offset: -5.0; width: -5.0
    offset: -2.5; width: -5.0
    offset:  0.0; width: -5.0
    offset:  2.5; width: -5.0
    offset:  5.0; width: -5.0
    offset: -5.0; width: -2.5
    offset: -2.5; width: -2.5
    offset:  0.0; width: -2.5
    offset:  2.5; width: -2.5
    offset:  5.0; width: -2.5
    offset: -5.0; width:  0.0
    offset: -2.5; width:  0.0
    offset:  0.0; width:  0.0
    offset:  2.5; width:  0.0
    offset:  5.0; width:  0.0
    offset: -5.0; width:  2.5
    offset: -2.5; width:  2.5
    offset:  0.0; width:  2.5
    offset:  2.5; width:  2.5
    offset:  5.0; width:  2.5
    offset: -5.0; width:  5.0
    offset: -2.5; width:  5.0
    offset:  0.0; width:  5.0
    offset:  2.5; width:  5.0
    offset:  5.0; width:  5.0



You can tell the glitch controller when you've reached a particular
result state like so:


**In [15]:**

.. code:: ipython3

    #gc.add("reset", (scope.glitch.width, scope.glitch.offset))
    #gc.add("success", (scope.glitch.width, scope.glitch.offset))

We'll start off with the following settings. It's usually best to use
"clock\_xor" with clock glitching, which will insert a glitch if the
clock is high or the clock is low.

For CW-Husky, we must first explicitly turn on the glitch circuitry (it
is off by default for power savings):


**In [16]:**

.. code:: ipython3

    if scope._is_husky:
        scope.glitch.enabled = True


**In [17]:**

.. code:: ipython3

    #Basic setup
    scope.glitch.clk_src = "clkgen" # set glitch input clock
    scope.glitch.output = "clock_xor" # glitch_out = clk ^ glitch
    scope.glitch.trigger_src = "ext_single" # glitch only after scope.arm() called
    
    scope.io.hs2 = "glitch"  # output glitch_out on the clock line
    print(scope.glitch)


**Out [17]:**



.. parsed-literal::

    clk\_src     = clkgen
    width       = 10.15625
    width\_fine  = 0
    offset      = 10.15625
    offset\_fine = 0
    trigger\_src = ext\_single
    arm\_timing  = after\_scope
    ext\_offset  = 0
    repeat      = 1
    output      = clock\_xor
    



Unless you don't mind your computer being occupied for a few days,
you'll want to break this into two glitch campaigns. The first will be
with wide ranges and large steps. Then, once you've found some
interesting locations, narrow down your ranges and step size to more
precisely map out what the best settings are.

We'll get you started, but it's up to you to finish the loop.


**In [18]:**

.. code:: ipython3

    import chipwhisperer.common.results.glitch as glitch
    from tqdm.notebook import trange
    import struct
    
    scope.glitch.ext_offset = 2
    
    # width and offset numbers have a very different meaning for Husky vs Lite/Pro;
    # see help(scope.glitch) for details
    if scope._is_husky:
        gc.set_range("width", 0, scope.glitch.phase_shift_steps)
        gc.set_range("offset", 0, scope.glitch.phase_shift_steps)
        gc.set_global_step([400, 200, 100])
        scope.adc.lo_gain_errors_disabled = True
        scope.adc.clip_errors_disabled = True
    else:
        gc.set_range("width", 0, 48)
        gc.set_range("offset", -48, 48)
        gc.set_global_step([8, 4, 2, 1, 0.4])
    scope.glitch.repeat = 10
    
    scope.adc.timeout = 0.1
    
    reboot_flush()
    broken = False
    for glitch_setting in gc.glitch_values():
        scope.glitch.offset = glitch_setting[1]
        scope.glitch.width = glitch_setting[0]
        # ###################
        # Add your code here
        # ###################
        #raise NotImplementedError("Add your code here, and delete this.")
    
        # ###################
        # START SOLUTION
        # ###################
        if scope.adc.state:
            # can detect crash here (fast) before timing out (slow)
            print("Trigger still high!")
            gc.add("reset", (scope.glitch.width, scope.glitch.offset))
            plt.plot(lwid, loff, 'xr', alpha=1)
            fig.canvas.draw()
    
            #Device is slow to boot?
            reboot_flush()
    
        scope.arm()
    
        #Do glitch loop
        target.simpleserial_write('g', bytearray([]))
    
        ret = scope.capture()
    
    
        
        loff = scope.glitch.offset
        lwid = scope.glitch.width
    
        if ret:
            print('Timeout - no trigger')
            gc.add("reset", (scope.glitch.width, scope.glitch.offset))
            plt.plot(scope.glitch.width, scope.glitch.offset, 'xr', alpha=1)
            fig.canvas.draw()
    
            #Device is slow to boot?
            reboot_flush()
    
        else:
            val = target.simpleserial_read_witherrors('r', 4, glitch_timeout=10, timeout=50)#For loop check
            if val['valid'] is False:
                gc.add("reset", (scope.glitch.width, scope.glitch.offset))
                plt.plot(scope.glitch.width, scope.glitch.offset, 'xr', alpha=1)
                fig.canvas.draw()
            else:
    
                #print(val['payload'])
                if val['payload'] is None:
                    print(val['payload'])
                    continue #what
                #gcnt = struct.unpack("<b", val['payload'])[0] #for code-flow check
                gcnt = struct.unpack("<I", val['payload'])[0]
    
                #print(gcnt)                
                # for table display purposes
                #if gnt != 0: #for code-flow check
                if gcnt != 2500: #for loop check
                    broken = True
                    gc.add("success", (scope.glitch.width, scope.glitch.offset))
                    plt.plot(scope.glitch.width, scope.glitch.offset, '+g')
                    fig.canvas.draw()
                    print(val['payload'])
                    print("🐙", end="")
                    break
                else:
                    gc.add("normal", (scope.glitch.width, scope.glitch.offset))
        # ###################
        # END SOLUTION
        # ###################
    
    print("Done glitching")


**Out [18]:**



.. parsed-literal::

    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:940) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:768) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:768) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:940) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:768) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:768) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:940) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:768) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:768) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:940) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:768) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:768) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:940) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:768) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:768) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:940) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:768) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:768) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:940) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:768) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:768) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:940) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:768) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:768) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:940) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work





.. parsed-literal::

    Trigger still high!
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:768) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:768) Partial reconfiguration for offset = 0 may not work





.. parsed-literal::

    Trigger still high!
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:940) Negative offsets <-45 may result in double glitches!





.. parsed-literal::

    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:768) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:768) Partial reconfiguration for offset = 0 may not work





.. parsed-literal::

    Trigger still high!
    Trigger still high!
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:940) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:768) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:768) Partial reconfiguration for offset = 0 may not work





.. parsed-literal::

    Trigger still high!
    Trigger still high!
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:940) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:768) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:768) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:940) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:768) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:768) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:940) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:768) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:768) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:940) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:768) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:768) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:940) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:768) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:768) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:940) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:768) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:768) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:940) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:768) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:768) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:940) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:768) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:768) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:940) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:768) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:768) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:940) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:940) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:768) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:768) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:940) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:765) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:940) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:288) Device reported error 0x10
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:290) CWbytearray(b'00 65 01 10 42 00')





.. parsed-literal::

    CWbytearray(b'c3 09 00 00')
    🐙Done glitching




.. image:: img/_33_12.png


Plotting Glitch Results
~~~~~~~~~~~~~~~~~~~~~~~

One thing you can do to speed up your glitch acquisition is avoid
plotting glitch results while you're trying to glitch the target. That
being said, it's still often helpful to plot this data at some point to
get a visual reference for good glitch spots. ChipWhisperer has built in
functionality for plotting the results of a glitch campagin. Simply call
the the following:


**In [19]:**

.. code:: ipython3

    %matplotlib inline
    gc.results.plot_2d(plotdots={"success":"+g", "reset":"xr", "normal":None})


**Out [19]:**


.. image:: img/_35_0.png


Make sure you write down those glitch settings, since we'll be using for
the rest of the glitching labs! In fact, we'll be using a lot of the
general code structure here for the rest of the labs, with the only big
changes being:

Repeat
~~~~~~

This lab used a pretty large repeat value. Like the name suggests, this
setting controls how many times the glitch is repeated (i.e. a repeat
value of 5 will place glitches in 5 consecutive clock cycles). Consider
that each glitch inserted has a chance to both cause a glitch or crash
the device. This was pretty advantageous for this lab since we had a lot
of different spots we wanted to place a glitch - using a high repeat
value increased our chance for a crash, but also increased our chance
for a successful glitch. For an attack where we're targeting a single
instruction, we don't really increase our glitch chance at all, but
still have the increased crash risk. Worse yet, a successful glitch in a
wrong spot may also cause a crash! It is for that reason that it's often
better to use a low repeat value when targeting a single instruction.

Ext Offset
~~~~~~~~~~

The ext offset setting controls a delay between the trigger firing and
the glitch being inserted. Like repeat, it's base on whole clock cycles,
meaning an ext offset of 10 will insert a glitch 10 cycles after the
trigger fires. We didn't have to worry about this setting for this lab
since the large repeat value was able to take us into the area we
wanted. This won't be true for many applications, where you'll have to
try glitches at a large variety of ext\_offsets.

Success, Reset, and Normal
~~~~~~~~~~~~~~~~~~~~~~~~~~

These three result states are usually enough to describe most glitch
results. What constitues a success, however, will change based on what
firmware you're attacking. For example, if we were attacking the Linux
authentication, we might base success on a check to see whether or not
we're root.


**In [20]:**

.. code:: ipython3

    scope.dis()
    target.dis()


**In [21]:**

.. code:: ipython3

    assert broken is True
