Part 1, Topic 1: Introduction to Clock Glitching (MAIN)
=======================================================



**SUMMARY:** *Microcontrollers and FPGAs have a number of operating
conditions that must be met in order for the device to work properly.
Outside of these conditions, devices will begin to malfunction, with
more extreme violations causing the device to stop entirely or even
become damaged. By going outside these operating conditions for very
small amounts of time, we can cause a varitey of temporary malfunctions*

*In this lab, we’ll explore clock glitching, which inserts short
glitches into a device’s clock. This will be used to get a target that’s
summing numbers in a loop to arrive at the wrong result.*

**LEARNING OUTCOMES:**

-  Understand effects of clock glitching
-  Exploring ChipWhisperer’s glitch module
-  Using clock glitching to disrupt a target’s algorithm

Clock Glitching Theory
----------------------

Digital hardware devices almost always expect some form of reliable
clock. We can manipulate the clock being presented to the device to
cause unintended behaviour. We’ll be concentrating on microcontrollers
here, however other digital devices (e.g. hardware encryption
accelerators) can also have faults injected using this technique.

Consider a microcontroller first. The following figure is an excerpt
from the Atmel AVR ATMega328P datasheet:

.. figure:: img/Mcu-unglitched.png
   :alt: A2_1

   A2_1

Rather than loading each instruction from FLASH and performing the
entire execution, the system has a pipeline to speed up the execution
process. This means that an instruction is being decoded while the next
one is being retrieved, as the following diagram shows:

.. figure:: img/Clock-normal.png
   :alt: A2_2

   A2_2

But if we modify the clock, we could have a situation where the system
doesn’t have enough time to actually perform an instruction. Consider
the following, where Execute #1 is effectively skipped. Before the
system has time to actually execute it another clock edge comes, causing
the microcontroller to start execution of the next instruction:

.. figure:: img/Clock-glitched.png
   :alt: A2_3

   A2_3

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
clock, although it’s possible to use the glitches alone for other
purposes (i.e. for voltage glitching, EM glitching).

The generation of glitches is done with two variable phase shift
modules, configured as follows:

.. figure:: img/Glitchgen-phaseshift.png
   :alt: A2_4

   A2_4

In CW-Husky there is one important difference: the phase shift 1 output
is not inverted before it is ANDed with the phase shift 2 output.

The enable line is used to determine when glitches are inserted.
Glitches can be inserted continuously (useful for development) or
triggered by some event. The following figure shows how the glitch can
be muxd to output to the Device Under Test (DUT).

.. figure:: img/Glitchgen-mux.png
   :alt: A2_5

   A2_5

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
These are stored as two files inside a “firmware” zip which contains
both the FPGA bitstream along with a file called ``glitchwidth.p`` and a
file called ``glitchoffset.p``. If a lone bitstream is being loaded into
the FPGA (i.e. not from the zip-file), the partial reconfiguration
system is disabled, as loading incorrect partial reconfiguration files
could damage the FPGA. This damage is mostly theoretical, more likely
the FPGA will fail to function correctly.

If in the course of following this tutorial you find the FPGA appears to
stop responding (i.e. certain features no longer work correctly), it
could be the partial reconfiguration data is incorrect.

We’ll look at how to interface with these features later in the
tutorial.

Hardware Support: CW-Husky
~~~~~~~~~~~~~~~~~~~~~~~~~~

The clock-generation logic in Husky’s 7-series FPGA is considerably
different than the 6-series FPGAs used in CW-Lite/Pro. The DCM is gone
and replaced by the much more powerful (and power hungry…) Mixed Mode
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
turned on. Fear not, Husky also uses Xilinx’s XADC module to
continuously monitor its temperature, and all MMCMs are automatically
turned off at when the temperature starts getting too high, well below
dangerous levels are reached (run ``scope.XADC`` to see all its
statistics and settings).


**In [1]:**

.. code:: ipython3

    SCOPETYPE = 'OPENADC'
    PLATFORM = 'CW308_STM32F4'
    SS_VER = 'SS_VER_2_1'
    
    CRYPTO_TARGET = 'TINYAES128C'
    allowable_exceptions = None
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
        scope = cw.scope(hw_location=(5, 8))
    
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
        scope = cw.scope(hw_location=(5, 8))
        target = cw.target(scope, target_type)
    
    
    print("INFO: Found ChipWhisperer😍")
    
    
    # In[ ]:
    
    
    if "STM" in PLATFORM or PLATFORM == "CWLITEARM" or PLATFORM == "CWNANO":
        prog = cw.programmers.STM32FProgrammer
    elif PLATFORM == "CW303" or PLATFORM == "CWLITEXMEGA":
        prog = cw.programmers.XMEGAProgrammer
    elif "neorv32" in PLATFORM.lower():
        prog = cw.programmers.NEORV32Programmer
    elif PLATFORM == "CW308_SAM4S" or PLATFORM == "CWHUSKY":
        prog = cw.programmers.SAM4SProgrammer
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
        elif PLATFORM == "CW308_SAM4S" or PLATFORM == "CWHUSKY":
            scope.io.nrst = 'low'
            time.sleep(0.25)
            scope.io.nrst = 'high_z'
            time.sleep(0.25)
        else:  
            scope.io.nrst = 'low'
            time.sleep(0.05)
            scope.io.nrst = 'high_z'
            time.sleep(0.05)
    
    



**Out [2]:**



.. parsed-literal::

    INFO: Found ChipWhisperer😍
    scope.gain.mode                          changed from low                       to high                     
    scope.gain.gain                          changed from 0                         to 30                       
    scope.gain.db                            changed from 5.5                       to 24.8359375               
    scope.adc.basic\_mode                     changed from low                       to rising\_edge              
    scope.adc.samples                        changed from 98134                     to 5000                     
    scope.adc.trig\_count                     changed from 11062002                  to 22091709                 
    scope.clock.adc\_src                      changed from clkgen\_x1                 to clkgen\_x4                
    scope.clock.adc\_freq                     changed from 29538471                  to 96000000                 
    scope.clock.adc\_rate                     changed from 29538471.0                to 96000000.0               
    scope.clock.clkgen\_div                   changed from 1                         to 26                       
    scope.clock.clkgen\_freq                  changed from 192000000.0               to 7384615.384615385        
    scope.io.tio1                            changed from serial\_tx                 to serial\_rx                
    scope.io.tio2                            changed from serial\_rx                 to serial\_tx                
    scope.io.hs2                             changed from None                      to clkgen                   




**In [3]:**

.. code:: bash

    %%bash -s "$PLATFORM" "$SS_VER"
    cd ../../../hardware/victims/firmware/simpleserial-glitch
    make PLATFORM=$1 CRYPTO_TARGET=NONE SS_VER=$2 -j


**Out [3]:**



.. parsed-literal::

    SS\_VER set to SS\_VER\_2\_1
    SS\_VER set to SS\_VER\_2\_1
    SS\_VER set to SS\_VER\_2\_1
    SS\_VER set to SS\_VER\_2\_1
    make[1]: '.dep' is up to date.
    SS\_VER set to SS\_VER\_2\_1
    SS\_VER set to SS\_VER\_2\_1
    .
    arm-none-eabi-gcc (15:9-2019-q4-0ubuntu1) 9.2.1 20191025 (release) [ARM/arm-9-branch revision 277599]
    Copyright (C) 2019 Free Software Foundation, Inc.
    This is free software; see the source for copying conditions.  There is NO
    warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
    
    Welcome to another exciting ChipWhisperer target build!!
    .
    .
    Compiling:
    Compiling:
    -en     simpleserial-glitch.c ...
    -en     .././simpleserial/simpleserial.c ...
    .
    Compiling:
    .
    -en     .././hal/stm32f4/stm32f4\_hal.c ...
    Compiling:
    -en     .././hal/stm32f4/stm32f4\_hal\_lowlevel.c ...
    .
    Compiling:
    .
    -en     .././hal/stm32f4/stm32f4\_sysmem.c ...
    Compiling:
    -en     .././hal/stm32f4/stm32f4xx\_hal\_rng.c ...
    .
    Assembling: .././hal/stm32f4/stm32f4\_startup.S
    arm-none-eabi-gcc -c -mcpu=cortex-m4 -I. -x assembler-with-cpp -mthumb -mfloat-abi=soft -fmessage-length=0 -ffunction-sections -DF\_CPU=7372800 -Wa,-gstabs,-adhlns=objdir-CW308\_STM32F4/stm32f4\_startup.lst -I.././simpleserial/ -I.././hal -I.././hal/stm32f4 -I.././hal/stm32f4/CMSIS -I.././hal/stm32f4/CMSIS/core -I.././hal/stm32f4/CMSIS/device -I.././hal/stm32f4/Legacy -I.././simpleserial/ -I.././crypto/ .././hal/stm32f4/stm32f4\_startup.S -o objdir-CW308\_STM32F4/stm32f4\_startup.o
    -e Done!
    -e Done!
    -e Done!





.. parsed-literal::

    In file included from .././hal/stm32f4/stm32f4\_hal.c:3:
    .././hal/stm32f4/stm32f4\_hal\_lowlevel.h:108: warning: "STM32F415xx" redefined
      108 \| #define STM32F415xx
          \| 
    <command-line>: note: this is the location of the previous definition





.. parsed-literal::

    -e Done!
    -e Done!





.. parsed-literal::

    In file included from .././hal/stm32f4/stm32f4\_hal\_lowlevel.c:39:
    .././hal/stm32f4/stm32f4\_hal\_lowlevel.h:108: warning: "STM32F415xx" redefined
      108 \| #define STM32F415xx
          \| 
    <command-line>: note: this is the location of the previous definition





.. parsed-literal::

    -e Done!
    .
    LINKING:
    -en     simpleserial-glitch-CW308\_STM32F4.elf ...
    -e Done!
    .
    .
    Creating load file for Flash: simpleserial-glitch-CW308\_STM32F4.hex
    Creating load file for Flash: simpleserial-glitch-CW308\_STM32F4.bin
    arm-none-eabi-objcopy -O ihex -R .eeprom -R .fuse -R .lock -R .signature simpleserial-glitch-CW308\_STM32F4.elf simpleserial-glitch-CW308\_STM32F4.hex
    .
    .
    arm-none-eabi-objcopy -O binary -R .eeprom -R .fuse -R .lock -R .signature simpleserial-glitch-CW308\_STM32F4.elf simpleserial-glitch-CW308\_STM32F4.bin
    Creating load file for EEPROM: simpleserial-glitch-CW308\_STM32F4.eep
    Creating Extended Listing: simpleserial-glitch-CW308\_STM32F4.lss
    .
    arm-none-eabi-objcopy -j .eeprom --set-section-flags=.eeprom="alloc,load" \
    --change-section-lma .eeprom=0 --no-change-warnings -O ihex simpleserial-glitch-CW308\_STM32F4.elf simpleserial-glitch-CW308\_STM32F4.eep \|\| exit 0
    Creating Symbol Table: simpleserial-glitch-CW308\_STM32F4.sym
    arm-none-eabi-nm -n simpleserial-glitch-CW308\_STM32F4.elf > simpleserial-glitch-CW308\_STM32F4.sym
    arm-none-eabi-objdump -h -S -z simpleserial-glitch-CW308\_STM32F4.elf > simpleserial-glitch-CW308\_STM32F4.lss
    SS\_VER set to SS\_VER\_2\_1
    SS\_VER set to SS\_VER\_2\_1
    Size after:
    +--------------------------------------------------------
       text	   data	    bss	    dec	    hex	filename
       4588	   1084	   1344	   7016	   1b68	simpleserial-glitch-CW308\_STM32F4.elf
    + Default target does full rebuild each time.
    + Specify buildtarget == allquick == to avoid full rebuild
    +--------------------------------------------------------
    +--------------------------------------------------------
    + Built for platform CW308T: STM32F4 Target with:
    + CRYPTO\_TARGET = NONE
    + CRYPTO\_OPTIONS = 
    +--------------------------------------------------------




**In [4]:**

.. code:: ipython3

    fw_path = "../../../hardware/victims/firmware/simpleserial-glitch/simpleserial-glitch-{}.hex".format(PLATFORM)
    cw.program_target(scope, prog, fw_path)
    if SS_VER=='SS_VER_2_1':
        target.reset_comms()


**Out [4]:**



.. parsed-literal::

    Detected known STMF32: STM32F40xxx/41xxx
    Extended erase (0x44), this can take ten seconds or more
    Attempting to program 5671 bytes at 0x8000000
    STM32F Programming flash...
    STM32F Reading flash...
    Verified flash OK, 5671 bytes



We’ll probably crash the target a few times while we’re trying some
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

For this lab, we’ll be introducing a new method:
``target.simpleserial_read_witherrors()``. We’re expecting a
simpleserial response back; however, glitch will often cause the target
to crash and return an invalid string. This method will handle all that
for us. It’ll also tell us whether the response was valid and what the
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

    {'valid': True, 'payload': CWbytearray(b'c4 09 00 00'), 'full\_response': CWbytearray(b'00 72 04 c4 09 00 00 15 00'), 'rv': bytearray(b'\x00')}



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

As you can see, we’ve got a simple loop. This is a really good place to
start glitching for 2 reasons:

1. We’ve got a really long portion of time with a lot of instructions to
   glitch. In contrast, with the Linux example we’re be trying to target
   a single instruction.

2. For some glitching scenarios, we’re looking for a pretty specific
   glitch effect. In the Linux example, we might be banking on the
   glitch causing the target to skip an instruction instead of
   corrupting the comparison since that’s a lot more likely to get us
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
     \|      Note that for ChipWhisperer-Husky, this method will only cause a glitch
     \|      in manual mode, while on the Lite/Pro, this method will always insert a glitch.
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
     \|         compatibility).  Otherwise, it is a MultiGlitchList, which behaves as a list,
     \|         but allows ext\_offset[x] = y to set settings for glitch x.
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
     \|      .. note:: Subsequent glitches are offset from the previous glitch.
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
     \|  Data and other attributes defined here:
     \|  
     \|  \_\_annotations\_\_ = {}
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
    



We’ll first go over settings that differ between the CW Husky and the CW Lite/Pro:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

-  clk_src

..

   The clock signal that the glitch DCM is using as input. Can be set to
   “target” or “clkgen” In this case, we’ll be providing the clock to
   the target, so we’ll want this set to “clkgen”.

   On CW Husky, a separate PLL is used to clock the glitch module
   instead of the clkgen module. The equivalent setting here for
   “clkgen” is “pll” \* offset

..

   Where in the output clock to place the glitch. Can be in the range
   ``[-48.8, 48.8]``. Often, we’ll want to try many offsets when trying
   to glitch a target.

   On CW Husky, the range will depend on frequency of the PLL used to
   drive the glitch module (settable which can be configured to be
   anyhwere in the range from 600 MHz to 1200 MHz via
   ``scope.clock.pll.update_fpga_vco()``), but, when the glitch module
   is active, the range will be ``[0, scope.glitch.phase_shift_steps]``.
   \* width

..

   How wide to make the glitch. Can be in the range ``[-50, 50]``,
   though there is no reason to use widths < 0. Wider glitches more
   easily cause glitches, but are also more likely to crash the target,
   meaning we’ll often want to try a range of widths when attacking a
   target.

   Like offset, the range will be
   ``[0, scope.glitch.phase_shift_steps]``.

These settings, on the other hand, are the same between the Husky and the Lite/Pro:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

-  output

..

   The output produced by the glitch module. For clock glitching,
   clock_xor is often the most useful option, as this inverts the clock
   during the glitch. \* ext_offset

   The number of clock cycles after the trigger to put the glitch. \*
   repeat

..

   The number of clock cycles to repeat the glitch for. Higher values
   increase the number of instructions that can be glitched, but often
   increase the risk of crashing the target.

-  trigger_src

..

   How to trigger the glitch. For this tutorial, we want to
   automatically trigger the glitch from the trigger pin only after
   arming the ChipWhipserer, so we’ll use ``ext_single``

In addition, we’ll need to tell ChipWhipserer to use the glitch module’s
output as a clock source for the target by setting
``scope.io.hs2 = "glitch"``. We’ll also setup a large ``repeat`` to make
glitching easier.

CW Glitch Controller
--------------------

To make creating a glitch loop easier, ChipWhisperer includes a glitch
controller. We’ll start of by initializing it with different potential
results of the attack. You define these to be whatever you want, but
often three groups are sufficient:

1. ``"success"``, where our glitch had the desired effect
2. ``"reset"``, where our glitch had an undesirable effect. Often, this
   effect is crashing or resetting the target, which is why we’re
   calling it ``"reset"``
3. ``"normal"``, where you glitch didn’t have a noticable effect.

We also need to tell it what glitch parameters we want to scan through,
in this case width and offset. We’ll also add a “tries” parameter which,
as the name suggests, is just there to try each setting multiple times:


**In [8]:**

.. code:: ipython3

    gc = cw.GlitchController(groups=["success", "reset", "normal"], parameters=["width", "offset", "ext_offset", "tries"])

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



.. parsed-literal::

    FloatSlider(value=0.0, continuous_update=False, description='ext_offset setting:', disabled=True, max=10.0, re…



.. parsed-literal::

    FloatSlider(value=0.0, continuous_update=False, description='tries setting:', disabled=True, max=10.0, readout…


We can also make a settings map that can also update in realtime as
well:


**In [10]:**

.. code:: ipython3

    gc.glitch_plot(plotdots={"success":"+g", "reset":"xr", "normal":None})


**Out [10]:**






.. raw:: html

    <div class="data_html">
        <style>.bk-root, .bk-root .bk:before, .bk-root .bk:after {
      font-family: var(--jp-ui-font-size1);
      font-size: var(--jp-ui-font-size1);
      color: var(--jp-ui-font-color1);
    }
    </style>
    </div>




.. parsed-literal::

    /home/testserveradmin/.pyenv/versions/cwtests/lib/python3.10/site-packages/holoviews/core/data/pandas.py:39: FutureWarning: Series.\_\_getitem\_\_ treating keys as positions is deprecated. In a future version, integer keys will always be treated as labels (consistent with DataFrame behavior). To access a value by position, use \`ser.iloc[pos]\`
      return dataset.data.dtypes[idx].type
    /home/testserveradmin/.pyenv/versions/cwtests/lib/python3.10/site-packages/holoviews/core/data/pandas.py:39: FutureWarning: Series.\_\_getitem\_\_ treating keys as positions is deprecated. In a future version, integer keys will always be treated as labels (consistent with DataFrame behavior). To access a value by position, use \`ser.iloc[pos]\`
      return dataset.data.dtypes[idx].type







.. raw:: html

    <div class="data_html">
        <div id='1002'>
      <div class="bk-root" id="c76180e4-e1f0-43d4-864d-7920655ec706" data-root-id="1002"></div>
    </div>
    <script type="application/javascript">(function(root) {
      function embed_document(root) {
        var docs_json = {"dbda235d-657f-4b6e-ac5e-7b722739df7f":{"defs":[{"extends":null,"module":null,"name":"ReactiveHTML1","overrides":[],"properties":[]},{"extends":null,"module":null,"name":"FlexBox1","overrides":[],"properties":[{"default":"flex-start","kind":null,"name":"align_content"},{"default":"flex-start","kind":null,"name":"align_items"},{"default":"row","kind":null,"name":"flex_direction"},{"default":"wrap","kind":null,"name":"flex_wrap"},{"default":"flex-start","kind":null,"name":"justify_content"}]},{"extends":null,"module":null,"name":"GridStack1","overrides":[],"properties":[{"default":"warn","kind":null,"name":"mode"},{"default":null,"kind":null,"name":"ncols"},{"default":null,"kind":null,"name":"nrows"},{"default":true,"kind":null,"name":"allow_resize"},{"default":true,"kind":null,"name":"allow_drag"},{"default":[],"kind":null,"name":"state"}]},{"extends":null,"module":null,"name":"click1","overrides":[],"properties":[{"default":"","kind":null,"name":"terminal_output"},{"default":"","kind":null,"name":"debug_name"},{"default":0,"kind":null,"name":"clears"}]},{"extends":null,"module":null,"name":"NotificationAreaBase1","overrides":[],"properties":[{"default":"bottom-right","kind":null,"name":"position"},{"default":0,"kind":null,"name":"_clear"}]},{"extends":null,"module":null,"name":"NotificationArea1","overrides":[],"properties":[{"default":[],"kind":null,"name":"notifications"},{"default":"bottom-right","kind":null,"name":"position"},{"default":0,"kind":null,"name":"_clear"},{"default":[{"background":"#ffc107","icon":{"className":"fas fa-exclamation-triangle","color":"white","tagName":"i"},"type":"warning"},{"background":"#007bff","icon":{"className":"fas fa-info-circle","color":"white","tagName":"i"},"type":"info"}],"kind":null,"name":"types"}]},{"extends":null,"module":null,"name":"Notification","overrides":[],"properties":[{"default":null,"kind":null,"name":"background"},{"default":3000,"kind":null,"name":"duration"},{"default":null,"kind":null,"name":"icon"},{"default":"","kind":null,"name":"message"},{"default":null,"kind":null,"name":"notification_type"},{"default":false,"kind":null,"name":"_destroyed"}]},{"extends":null,"module":null,"name":"TemplateActions1","overrides":[],"properties":[{"default":0,"kind":null,"name":"open_modal"},{"default":0,"kind":null,"name":"close_modal"}]},{"extends":null,"module":null,"name":"MaterialTemplateActions1","overrides":[],"properties":[{"default":0,"kind":null,"name":"open_modal"},{"default":0,"kind":null,"name":"close_modal"}]}],"roots":{"references":[{"attributes":{"fill_alpha":{"value":0.2},"fill_color":{"value":"#007f00"},"hatch_alpha":{"value":0.2},"hatch_color":{"value":"#007f00"},"line_alpha":{"value":0.2},"line_color":{"value":"#007f00"},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"width"},"y":{"field":"offset"}},"id":"1050","type":"Scatter"},{"attributes":{"angle":{"value":0.7853981633974483},"fill_alpha":{"value":1.0},"fill_color":{"value":"#ff0000"},"hatch_alpha":{"value":1.0},"hatch_color":{"value":"#ff0000"},"hatch_scale":{"value":12.0},"hatch_weight":{"value":1.0},"line_alpha":{"value":1.0},"line_cap":{"value":"butt"},"line_color":{"value":"#ff0000"},"line_dash":{"value":[]},"line_dash_offset":{"value":0},"line_join":{"value":"bevel"},"line_width":{"value":1},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"width"},"y":{"field":"offset"}},"id":"1062","type":"Scatter"},{"attributes":{"active_drag":{"id":"1027"},"active_scroll":{"id":"1028"},"tools":[{"id":"1007"},{"id":"1026"},{"id":"1027"},{"id":"1028"},{"id":"1029"},{"id":"1030"}]},"id":"1032","type":"Toolbar"},{"attributes":{"angle":{"value":0.7853981633974483},"fill_alpha":{"value":0.1},"fill_color":{"value":"#ff0000"},"hatch_alpha":{"value":0.1},"hatch_color":{"value":"#ff0000"},"line_alpha":{"value":0.1},"line_color":{"value":"#ff0000"},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"width"},"y":{"field":"offset"}},"id":"1058","type":"Scatter"},{"attributes":{},"id":"1055","type":"Selection"},{"attributes":{},"id":"1041","type":"AllLabels"},{"attributes":{},"id":"1044","type":"AllLabels"},{"attributes":{"callback":null,"renderers":[{"id":"1051"},{"id":"1060"}],"tags":["hv_created"],"tooltips":[["width","@{width}"],["offset","@{offset}"]]},"id":"1007","type":"HoverTool"},{"attributes":{},"id":"1040","type":"BasicTickFormatter"},{"attributes":{"client_comm_id":"3d3cc9840f9840c0920c7ebe0402f81a","comm_id":"5825ba48702c4084be6c7929b9b62501","plot_id":"1002"},"id":"1115","type":"panel.models.comm_manager.CommManager"},{"attributes":{"angle":{"value":0.7853981633974483},"fill_alpha":{"value":0.2},"fill_color":{"value":"#ff0000"},"hatch_alpha":{"value":0.2},"hatch_color":{"value":"#ff0000"},"line_alpha":{"value":0.2},"line_color":{"value":"#ff0000"},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"width"},"y":{"field":"offset"}},"id":"1059","type":"Scatter"},{"attributes":{"fill_color":{"value":"#007f00"},"hatch_color":{"value":"#007f00"},"line_color":{"value":"#007f00"},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"width"},"y":{"field":"offset"}},"id":"1048","type":"Scatter"},{"attributes":{},"id":"1043","type":"BasicTickFormatter"},{"attributes":{"coordinates":null,"data_source":{"id":"1054"},"glyph":{"id":"1057"},"group":null,"hover_glyph":null,"muted_glyph":{"id":"1059"},"nonselection_glyph":{"id":"1058"},"selection_glyph":{"id":"1062"},"view":{"id":"1061"}},"id":"1060","type":"GlyphRenderer"},{"attributes":{},"id":"1046","type":"Selection"},{"attributes":{"data":{"offset":{"__ndarray__":"","dtype":"float64","order":"little","shape":[0]},"width":{"__ndarray__":"","dtype":"float64","order":"little","shape":[0]}},"selected":{"id":"1046"},"selection_policy":{"id":"1074"}},"id":"1045","type":"ColumnDataSource"},{"attributes":{"source":{"id":"1054"}},"id":"1061","type":"CDSView"},{"attributes":{"axis_label":"width","coordinates":null,"formatter":{"id":"1040"},"group":null,"major_label_policy":{"id":"1041"},"ticker":{"id":"1019"}},"id":"1018","type":"LinearAxis"},{"attributes":{"coordinates":null,"group":null,"text_color":"black","text_font_size":"12pt"},"id":"1010","type":"Title"},{"attributes":{"children":[{"id":"1009"}],"height":600,"margin":[0,0,0,0],"name":"Row00811","sizing_mode":"fixed","width":800},"id":"1002","type":"Row"},{"attributes":{"below":[{"id":"1018"}],"center":[{"id":"1021"},{"id":"1025"}],"left":[{"id":"1022"}],"margin":[5,5,5,5],"min_border_bottom":10,"min_border_left":10,"min_border_right":10,"min_border_top":10,"output_backend":"webgl","renderers":[{"id":"1051"},{"id":"1060"}],"sizing_mode":"fixed","title":{"id":"1010"},"toolbar":{"id":"1032"},"width":800,"x_range":{"id":"1003"},"x_scale":{"id":"1016"},"y_range":{"id":"1004"},"y_scale":{"id":"1017"}},"id":"1009","subtype":"Figure","type":"Plot"},{"attributes":{"coordinates":null,"data_source":{"id":"1045"},"glyph":{"id":"1048"},"group":null,"hover_glyph":null,"muted_glyph":{"id":"1050"},"nonselection_glyph":{"id":"1049"},"selection_glyph":{"id":"1053"},"view":{"id":"1052"}},"id":"1051","type":"GlyphRenderer"},{"attributes":{},"id":"1016","type":"LinearScale"},{"attributes":{},"id":"1017","type":"LinearScale"},{"attributes":{"fill_alpha":{"value":0.1},"fill_color":{"value":"#007f00"},"hatch_alpha":{"value":0.1},"hatch_color":{"value":"#007f00"},"line_alpha":{"value":0.1},"line_color":{"value":"#007f00"},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"width"},"y":{"field":"offset"}},"id":"1049","type":"Scatter"},{"attributes":{},"id":"1019","type":"BasicTicker"},{"attributes":{"axis":{"id":"1018"},"coordinates":null,"grid_line_color":null,"group":null,"ticker":null},"id":"1021","type":"Grid"},{"attributes":{"axis_label":"offset","coordinates":null,"formatter":{"id":"1043"},"group":null,"major_label_policy":{"id":"1044"},"ticker":{"id":"1023"}},"id":"1022","type":"LinearAxis"},{"attributes":{},"id":"1076","type":"UnionRenderers"},{"attributes":{"axis":{"id":"1022"},"coordinates":null,"dimension":1,"grid_line_color":null,"group":null,"ticker":null},"id":"1025","type":"Grid"},{"attributes":{},"id":"1074","type":"UnionRenderers"},{"attributes":{},"id":"1023","type":"BasicTicker"},{"attributes":{"angle":{"value":0.0},"fill_alpha":{"value":1.0},"fill_color":{"value":"#007f00"},"hatch_alpha":{"value":1.0},"hatch_color":{"value":"#007f00"},"hatch_scale":{"value":12.0},"hatch_weight":{"value":1.0},"line_alpha":{"value":1.0},"line_cap":{"value":"butt"},"line_color":{"value":"#007f00"},"line_dash":{"value":[]},"line_dash_offset":{"value":0},"line_join":{"value":"bevel"},"line_width":{"value":1},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"width"},"y":{"field":"offset"}},"id":"1053","type":"Scatter"},{"attributes":{},"id":"1028","type":"WheelZoomTool"},{"attributes":{"source":{"id":"1045"}},"id":"1052","type":"CDSView"},{"attributes":{},"id":"1027","type":"PanTool"},{"attributes":{},"id":"1026","type":"SaveTool"},{"attributes":{"overlay":{"id":"1031"}},"id":"1029","type":"BoxZoomTool"},{"attributes":{"tags":[[["width","width",null]],[]]},"id":"1003","type":"Range1d"},{"attributes":{},"id":"1030","type":"ResetTool"},{"attributes":{"tags":[[["offset","offset",null]],{"autorange":false,"invert_yaxis":false}]},"id":"1004","type":"Range1d"},{"attributes":{"angle":{"value":0.7853981633974483},"fill_color":{"value":"#ff0000"},"hatch_color":{"value":"#ff0000"},"line_color":{"value":"#ff0000"},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"width"},"y":{"field":"offset"}},"id":"1057","type":"Scatter"},{"attributes":{"data":{"offset":{"__ndarray__":"","dtype":"float64","order":"little","shape":[0]},"width":{"__ndarray__":"","dtype":"float64","order":"little","shape":[0]}},"selected":{"id":"1055"},"selection_policy":{"id":"1076"}},"id":"1054","type":"ColumnDataSource"},{"attributes":{"bottom_units":"screen","coordinates":null,"fill_alpha":0.5,"fill_color":"lightgrey","group":null,"left_units":"screen","level":"overlay","line_alpha":1.0,"line_color":"black","line_dash":[4,4],"line_width":2,"right_units":"screen","syncable":false,"top_units":"screen"},"id":"1031","type":"BoxAnnotation"}],"root_ids":["1002","1115"]},"title":"Bokeh Application","version":"2.4.3"}};
        var render_items = [{"docid":"dbda235d-657f-4b6e-ac5e-7b722739df7f","root_ids":["1002"],"roots":{"1002":"c76180e4-e1f0-43d4-864d-7920655ec706"}}];
        root.Bokeh.embed.embed_items_notebook(docs_json, render_items);
        for (const render_item of render_items) {
          for (const root_id of render_item.root_ids) {
    	const id_el = document.getElementById(root_id)
    	if (id_el.children.length && (id_el.children[0].className === 'bk-root')) {
    	  const root_el = id_el.children[0]
    	  root_el.id = root_el.id + '-rendered'
    	}
          }
        }
      }
      if (root.Bokeh !== undefined && root.Bokeh.Panel !== undefined) {
        embed_document(root);
      } else {
        var attempts = 0;
        var timer = setInterval(function(root) {
          if (root.Bokeh !== undefined && root.Bokeh.Panel !== undefined) {
            clearInterval(timer);
            embed_document(root);
          } else if (document.readyState == "complete") {
            attempts++;
            if (attempts > 200) {
              clearInterval(timer);
              console.log("Bokeh: ERROR: Unable to run BokehJS code because BokehJS library is missing");
            }
          }
        }, 25, root)
      }
    })(window);</script>
    </div>



Here ``plotdots`` is a dictionary that specifies how you want to plot
each group. In this case, we’re plotting ``"success"`` as a green ``+``
(``"+g"``), ``"reset"`` as a red ``x`` (``"xr"``), and we won’t be
plotting glitch attempts where nothing abnormal happens (``None``)

This plot will auto update its bounds as points are added. If you want
to specify the axis bounds, you can do so as follows:

.. code:: python

   gc.glitch_plot(plotdots={"success":"+g", "reset":"xr", "normal":None}, x_bound=(-48, 48), y_bound=(-48, 48))

You can also select which parameters you want to use for x and y, either
by index, or by its name:

.. code:: python

   # will flip width and offset axes
   gc.glitch_plot(plotdots={"success":"+g", "reset":"xr", "normal":None}, x_index=1, y_index=0)
   # or
   gc.glitch_plot(plotdots={"success":"+g", "reset":"xr", "normal":None}, x_index="offset", y_index="width")

You can set ranges for each glitch setting:


**In [11]:**

.. code:: ipython3

    gc.set_range("width", -5, 5)
    gc.set_range("offset", -5, 5)

Each setting moves from min to max based on the global step:


**In [12]:**

.. code:: ipython3

    gc.set_global_step([5.0, 2.5])

We can print out all the glitch settings to see how this looks:


**In [13]:**

.. code:: ipython3

    for glitch_setting in gc.glitch_values():
        print("offset: {:4.1f}; width: {:4.1f}".format(glitch_setting[1], glitch_setting[0]))


**Out [13]:**



.. parsed-literal::

    offset: -5.0; width: -5.0
    offset: -5.0; width: -5.0
    offset: -5.0; width: -5.0
    offset: -5.0; width: -5.0
    offset: -5.0; width: -5.0
    offset: -5.0; width: -5.0
    offset: -5.0; width: -5.0
    offset: -5.0; width: -5.0
    offset: -5.0; width: -5.0
    offset: -5.0; width: -5.0
    offset: -5.0; width: -5.0
    offset: -5.0; width: -5.0
    offset: -5.0; width: -5.0
    offset: -5.0; width: -5.0
    offset: -5.0; width: -5.0
    offset: -5.0; width: -5.0
    offset: -5.0; width: -5.0
    offset: -5.0; width: -5.0
    offset: -5.0; width: -5.0
    offset: -5.0; width: -5.0
    offset: -5.0; width: -5.0
    offset: -5.0; width: -5.0
    offset: -5.0; width: -5.0
    offset: -5.0; width: -5.0
    offset: -5.0; width: -5.0
    offset: -5.0; width: -5.0
    offset: -5.0; width: -5.0
    offset: -5.0; width: -5.0
    offset: -5.0; width: -5.0
    offset: -5.0; width: -5.0
    offset: -5.0; width: -5.0
    offset: -5.0; width: -5.0
    offset: -5.0; width: -5.0
    offset: -5.0; width: -5.0
    offset: -5.0; width: -5.0
    offset: -5.0; width: -5.0
    offset: -5.0; width: -5.0
    offset: -5.0; width: -5.0
    offset: -5.0; width: -5.0
    offset: -5.0; width: -5.0
    offset: -5.0; width: -5.0
    offset: -5.0; width: -5.0
    offset: -5.0; width: -5.0
    offset: -5.0; width: -5.0
    offset: -5.0; width: -5.0
    offset: -5.0; width: -5.0
    offset: -5.0; width: -5.0
    offset: -5.0; width: -5.0
    offset: -5.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset: -2.5; width: -5.0
    offset: -2.5; width: -5.0
    offset: -2.5; width: -5.0
    offset: -2.5; width: -5.0
    offset: -2.5; width: -5.0
    offset: -2.5; width: -5.0
    offset: -2.5; width: -5.0
    offset: -2.5; width: -5.0
    offset: -2.5; width: -5.0
    offset: -2.5; width: -5.0
    offset: -2.5; width: -5.0
    offset: -2.5; width: -5.0
    offset: -2.5; width: -5.0
    offset: -2.5; width: -5.0
    offset: -2.5; width: -5.0
    offset: -2.5; width: -5.0
    offset: -2.5; width: -5.0
    offset: -2.5; width: -5.0
    offset: -2.5; width: -5.0
    offset: -2.5; width: -5.0
    offset: -2.5; width: -5.0
    offset: -2.5; width: -5.0
    offset: -2.5; width: -5.0
    offset: -2.5; width: -5.0
    offset: -2.5; width: -5.0
    offset: -2.5; width: -5.0
    offset: -2.5; width: -5.0
    offset: -2.5; width: -5.0
    offset: -2.5; width: -5.0
    offset: -2.5; width: -5.0
    offset: -2.5; width: -5.0
    offset: -2.5; width: -5.0
    offset: -2.5; width: -5.0
    offset: -2.5; width: -5.0
    offset: -2.5; width: -5.0
    offset: -2.5; width: -5.0
    offset: -2.5; width: -5.0
    offset: -2.5; width: -5.0
    offset: -2.5; width: -5.0
    offset: -2.5; width: -5.0
    offset: -2.5; width: -5.0
    offset: -2.5; width: -5.0
    offset: -2.5; width: -5.0
    offset: -2.5; width: -5.0
    offset: -2.5; width: -5.0
    offset: -2.5; width: -5.0
    offset: -2.5; width: -5.0
    offset: -2.5; width: -5.0
    offset: -2.5; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  0.0; width: -5.0
    offset:  2.5; width: -5.0
    offset:  2.5; width: -5.0
    offset:  2.5; width: -5.0
    offset:  2.5; width: -5.0
    offset:  2.5; width: -5.0
    offset:  2.5; width: -5.0
    offset:  2.5; width: -5.0
    offset:  2.5; width: -5.0
    offset:  2.5; width: -5.0
    offset:  2.5; width: -5.0
    offset:  2.5; width: -5.0
    offset:  2.5; width: -5.0
    offset:  2.5; width: -5.0
    offset:  2.5; width: -5.0
    offset:  2.5; width: -5.0
    offset:  2.5; width: -5.0
    offset:  2.5; width: -5.0
    offset:  2.5; width: -5.0
    offset:  2.5; width: -5.0
    offset:  2.5; width: -5.0
    offset:  2.5; width: -5.0
    offset:  2.5; width: -5.0
    offset:  2.5; width: -5.0
    offset:  2.5; width: -5.0
    offset:  2.5; width: -5.0
    offset:  2.5; width: -5.0
    offset:  2.5; width: -5.0
    offset:  2.5; width: -5.0
    offset:  2.5; width: -5.0
    offset:  2.5; width: -5.0
    offset:  2.5; width: -5.0
    offset:  2.5; width: -5.0
    offset:  2.5; width: -5.0
    offset:  2.5; width: -5.0
    offset:  2.5; width: -5.0
    offset:  2.5; width: -5.0
    offset:  2.5; width: -5.0
    offset:  2.5; width: -5.0
    offset:  2.5; width: -5.0
    offset:  2.5; width: -5.0
    offset:  2.5; width: -5.0
    offset:  2.5; width: -5.0
    offset:  2.5; width: -5.0
    offset:  2.5; width: -5.0
    offset:  2.5; width: -5.0
    offset:  2.5; width: -5.0
    offset:  2.5; width: -5.0
    offset:  2.5; width: -5.0
    offset:  2.5; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset:  5.0; width: -5.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset: -5.0; width: -2.5
    offset: -5.0; width: -2.5
    offset: -5.0; width: -2.5
    offset: -5.0; width: -2.5
    offset: -5.0; width: -2.5
    offset: -5.0; width: -2.5
    offset: -5.0; width: -2.5
    offset: -5.0; width: -2.5
    offset: -5.0; width: -2.5
    offset: -5.0; width: -2.5
    offset: -5.0; width: -2.5
    offset: -5.0; width: -2.5
    offset: -5.0; width: -2.5
    offset: -5.0; width: -2.5
    offset: -5.0; width: -2.5
    offset: -5.0; width: -2.5
    offset: -5.0; width: -2.5
    offset: -5.0; width: -2.5
    offset: -5.0; width: -2.5
    offset: -5.0; width: -2.5
    offset: -5.0; width: -2.5
    offset: -5.0; width: -2.5
    offset: -5.0; width: -2.5
    offset: -5.0; width: -2.5
    offset: -5.0; width: -2.5
    offset: -5.0; width: -2.5
    offset: -5.0; width: -2.5
    offset: -5.0; width: -2.5
    offset: -5.0; width: -2.5
    offset: -5.0; width: -2.5
    offset: -5.0; width: -2.5
    offset: -5.0; width: -2.5
    offset: -5.0; width: -2.5
    offset: -5.0; width: -2.5
    offset: -5.0; width: -2.5
    offset: -5.0; width: -2.5
    offset: -5.0; width: -2.5
    offset: -5.0; width: -2.5
    offset: -5.0; width: -2.5
    offset: -5.0; width: -2.5
    offset: -5.0; width: -2.5
    offset: -5.0; width: -2.5
    offset: -5.0; width: -2.5
    offset: -5.0; width: -2.5
    offset: -5.0; width: -2.5
    offset: -5.0; width: -2.5
    offset: -5.0; width: -2.5
    offset: -5.0; width: -2.5
    offset: -5.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset: -2.5; width: -2.5
    offset: -2.5; width: -2.5
    offset: -2.5; width: -2.5
    offset: -2.5; width: -2.5
    offset: -2.5; width: -2.5
    offset: -2.5; width: -2.5
    offset: -2.5; width: -2.5
    offset: -2.5; width: -2.5
    offset: -2.5; width: -2.5
    offset: -2.5; width: -2.5
    offset: -2.5; width: -2.5
    offset: -2.5; width: -2.5
    offset: -2.5; width: -2.5
    offset: -2.5; width: -2.5
    offset: -2.5; width: -2.5
    offset: -2.5; width: -2.5
    offset: -2.5; width: -2.5
    offset: -2.5; width: -2.5
    offset: -2.5; width: -2.5
    offset: -2.5; width: -2.5
    offset: -2.5; width: -2.5
    offset: -2.5; width: -2.5
    offset: -2.5; width: -2.5
    offset: -2.5; width: -2.5
    offset: -2.5; width: -2.5
    offset: -2.5; width: -2.5
    offset: -2.5; width: -2.5
    offset: -2.5; width: -2.5
    offset: -2.5; width: -2.5
    offset: -2.5; width: -2.5
    offset: -2.5; width: -2.5
    offset: -2.5; width: -2.5
    offset: -2.5; width: -2.5
    offset: -2.5; width: -2.5
    offset: -2.5; width: -2.5
    offset: -2.5; width: -2.5
    offset: -2.5; width: -2.5
    offset: -2.5; width: -2.5
    offset: -2.5; width: -2.5
    offset: -2.5; width: -2.5
    offset: -2.5; width: -2.5
    offset: -2.5; width: -2.5
    offset: -2.5; width: -2.5
    offset: -2.5; width: -2.5
    offset: -2.5; width: -2.5
    offset: -2.5; width: -2.5
    offset: -2.5; width: -2.5
    offset: -2.5; width: -2.5
    offset: -2.5; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  0.0; width: -2.5
    offset:  2.5; width: -2.5
    offset:  2.5; width: -2.5
    offset:  2.5; width: -2.5
    offset:  2.5; width: -2.5
    offset:  2.5; width: -2.5
    offset:  2.5; width: -2.5
    offset:  2.5; width: -2.5
    offset:  2.5; width: -2.5
    offset:  2.5; width: -2.5
    offset:  2.5; width: -2.5
    offset:  2.5; width: -2.5
    offset:  2.5; width: -2.5
    offset:  2.5; width: -2.5
    offset:  2.5; width: -2.5
    offset:  2.5; width: -2.5
    offset:  2.5; width: -2.5
    offset:  2.5; width: -2.5
    offset:  2.5; width: -2.5
    offset:  2.5; width: -2.5
    offset:  2.5; width: -2.5
    offset:  2.5; width: -2.5
    offset:  2.5; width: -2.5
    offset:  2.5; width: -2.5
    offset:  2.5; width: -2.5
    offset:  2.5; width: -2.5
    offset:  2.5; width: -2.5
    offset:  2.5; width: -2.5
    offset:  2.5; width: -2.5
    offset:  2.5; width: -2.5
    offset:  2.5; width: -2.5
    offset:  2.5; width: -2.5
    offset:  2.5; width: -2.5
    offset:  2.5; width: -2.5
    offset:  2.5; width: -2.5
    offset:  2.5; width: -2.5
    offset:  2.5; width: -2.5
    offset:  2.5; width: -2.5
    offset:  2.5; width: -2.5
    offset:  2.5; width: -2.5
    offset:  2.5; width: -2.5
    offset:  2.5; width: -2.5
    offset:  2.5; width: -2.5
    offset:  2.5; width: -2.5
    offset:  2.5; width: -2.5
    offset:  2.5; width: -2.5
    offset:  2.5; width: -2.5
    offset:  2.5; width: -2.5
    offset:  2.5; width: -2.5
    offset:  2.5; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset:  5.0; width: -2.5
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset: -5.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset: -2.5; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  0.0; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  2.5; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset:  5.0; width:  0.0
    offset: -5.0; width:  2.5
    offset: -5.0; width:  2.5
    offset: -5.0; width:  2.5
    offset: -5.0; width:  2.5
    offset: -5.0; width:  2.5
    offset: -5.0; width:  2.5
    offset: -5.0; width:  2.5
    offset: -5.0; width:  2.5
    offset: -5.0; width:  2.5
    offset: -5.0; width:  2.5
    offset: -5.0; width:  2.5
    offset: -5.0; width:  2.5
    offset: -5.0; width:  2.5
    offset: -5.0; width:  2.5
    offset: -5.0; width:  2.5
    offset: -5.0; width:  2.5
    offset: -5.0; width:  2.5
    offset: -5.0; width:  2.5
    offset: -5.0; width:  2.5
    offset: -5.0; width:  2.5
    offset: -5.0; width:  2.5
    offset: -5.0; width:  2.5
    offset: -5.0; width:  2.5
    offset: -5.0; width:  2.5
    offset: -5.0; width:  2.5
    offset: -5.0; width:  2.5
    offset: -5.0; width:  2.5
    offset: -5.0; width:  2.5
    offset: -5.0; width:  2.5
    offset: -5.0; width:  2.5
    offset: -5.0; width:  2.5
    offset: -5.0; width:  2.5
    offset: -5.0; width:  2.5
    offset: -5.0; width:  2.5
    offset: -5.0; width:  2.5
    offset: -5.0; width:  2.5
    offset: -5.0; width:  2.5
    offset: -5.0; width:  2.5
    offset: -5.0; width:  2.5
    offset: -5.0; width:  2.5
    offset: -5.0; width:  2.5
    offset: -5.0; width:  2.5
    offset: -5.0; width:  2.5
    offset: -5.0; width:  2.5
    offset: -5.0; width:  2.5
    offset: -5.0; width:  2.5
    offset: -5.0; width:  2.5
    offset: -5.0; width:  2.5
    offset: -5.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset: -2.5; width:  2.5
    offset: -2.5; width:  2.5
    offset: -2.5; width:  2.5
    offset: -2.5; width:  2.5
    offset: -2.5; width:  2.5
    offset: -2.5; width:  2.5
    offset: -2.5; width:  2.5
    offset: -2.5; width:  2.5
    offset: -2.5; width:  2.5
    offset: -2.5; width:  2.5
    offset: -2.5; width:  2.5
    offset: -2.5; width:  2.5
    offset: -2.5; width:  2.5
    offset: -2.5; width:  2.5
    offset: -2.5; width:  2.5
    offset: -2.5; width:  2.5
    offset: -2.5; width:  2.5
    offset: -2.5; width:  2.5
    offset: -2.5; width:  2.5
    offset: -2.5; width:  2.5
    offset: -2.5; width:  2.5
    offset: -2.5; width:  2.5
    offset: -2.5; width:  2.5
    offset: -2.5; width:  2.5
    offset: -2.5; width:  2.5
    offset: -2.5; width:  2.5
    offset: -2.5; width:  2.5
    offset: -2.5; width:  2.5
    offset: -2.5; width:  2.5
    offset: -2.5; width:  2.5
    offset: -2.5; width:  2.5
    offset: -2.5; width:  2.5
    offset: -2.5; width:  2.5
    offset: -2.5; width:  2.5
    offset: -2.5; width:  2.5
    offset: -2.5; width:  2.5
    offset: -2.5; width:  2.5
    offset: -2.5; width:  2.5
    offset: -2.5; width:  2.5
    offset: -2.5; width:  2.5
    offset: -2.5; width:  2.5
    offset: -2.5; width:  2.5
    offset: -2.5; width:  2.5
    offset: -2.5; width:  2.5
    offset: -2.5; width:  2.5
    offset: -2.5; width:  2.5
    offset: -2.5; width:  2.5
    offset: -2.5; width:  2.5
    offset: -2.5; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  0.0; width:  2.5
    offset:  2.5; width:  2.5
    offset:  2.5; width:  2.5
    offset:  2.5; width:  2.5
    offset:  2.5; width:  2.5
    offset:  2.5; width:  2.5
    offset:  2.5; width:  2.5
    offset:  2.5; width:  2.5
    offset:  2.5; width:  2.5
    offset:  2.5; width:  2.5
    offset:  2.5; width:  2.5
    offset:  2.5; width:  2.5
    offset:  2.5; width:  2.5
    offset:  2.5; width:  2.5
    offset:  2.5; width:  2.5
    offset:  2.5; width:  2.5
    offset:  2.5; width:  2.5
    offset:  2.5; width:  2.5
    offset:  2.5; width:  2.5
    offset:  2.5; width:  2.5
    offset:  2.5; width:  2.5
    offset:  2.5; width:  2.5
    offset:  2.5; width:  2.5
    offset:  2.5; width:  2.5
    offset:  2.5; width:  2.5
    offset:  2.5; width:  2.5
    offset:  2.5; width:  2.5
    offset:  2.5; width:  2.5
    offset:  2.5; width:  2.5
    offset:  2.5; width:  2.5
    offset:  2.5; width:  2.5
    offset:  2.5; width:  2.5
    offset:  2.5; width:  2.5
    offset:  2.5; width:  2.5
    offset:  2.5; width:  2.5
    offset:  2.5; width:  2.5
    offset:  2.5; width:  2.5
    offset:  2.5; width:  2.5
    offset:  2.5; width:  2.5
    offset:  2.5; width:  2.5
    offset:  2.5; width:  2.5
    offset:  2.5; width:  2.5
    offset:  2.5; width:  2.5
    offset:  2.5; width:  2.5
    offset:  2.5; width:  2.5
    offset:  2.5; width:  2.5
    offset:  2.5; width:  2.5
    offset:  2.5; width:  2.5
    offset:  2.5; width:  2.5
    offset:  2.5; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset:  5.0; width:  2.5
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset: -5.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset: -2.5; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  0.0; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  2.5; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0
    offset:  5.0; width:  5.0



You can tell the glitch controller when you’ve reached a particular
result state like so:


**In [14]:**

.. code:: ipython3

    #gc.add("reset", (scope.glitch.width, scope.glitch.offset)) or simply gc.add("reset")
    #gc.add("success", (scope.glitch.width, scope.glitch.offset)) or simply gc.add("success")

As of ChipWhisperer 5.7, you can skip the glitch width and glitch offset
parameters. In this case, the glitch controller will use its internal
values for the coordinates. Note that due to rounding, this will usually
be a bit different from the actual hardware value on the Lite/Pro;
however, the values will still correspond to the correct settings on
your ChipWhisperer.

We’ll start off with the following settings. It’s usually best to use
“clock_xor” with clock glitching, which will insert a glitch if the
clock is high or the clock is low.

For CW-Husky, we must first explicitly turn on the glitch circuitry (it
is off by default for power savings):


**In [15]:**

.. code:: ipython3

    if scope._is_husky:
        scope.glitch.enabled = True

We’ll start off with the following settings. It’s usually best to use
“clock_xor” with clock glitching, which will insert a glitch if the
clock is high or the clock is low.


**In [16]:**

.. code:: ipython3

    #Basic setup
    # set glitch clock
    if scope._is_husky:
        scope.glitch.clk_src = "pll"
    else:
        scope.glitch.clk_src = "clkgen" 
    
    scope.glitch.output = "clock_xor" # glitch_out = clk ^ glitch
    scope.glitch.trigger_src = "ext_single" # glitch only after scope.arm() called
    
    scope.io.hs2 = "glitch"  # output glitch_out on the clock line
    print(scope.glitch)


**Out [16]:**



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
    



These settings are often a good starting point for all clock glitching,
so, new with ChipWhisperer 5.7, we’ve got a method that sets all of this
up for you:


**In [17]:**

.. code:: ipython3

    scope.cglitch_setup()


**Out [17]:**



.. parsed-literal::

    scope.clock.adc\_freq                     changed from 96000000                  to 29538459                 
    scope.clock.adc\_rate                     changed from 96000000.0                to 29538459.0               
    scope.io.hs2                             changed from glitch                    to clkgen                   



You should have all you need to construct your glitch loop. We’ll get
you started, but the rest is up to you! Also, some stuff to keep in
mind:

-  You’ll need to detect crashes, successful glitches, and normal
   returns from the target. Don’t be afraid to experiment with the loop:
   you can always restart it and rerun the code.
-  You can cover a larger set of glitch settings by starting with large
   glitch controller steps to get idea where some interesting locations
   are, then repeating the glitch loop with small steps in interesting
   areas. Where there’s one successful glitch, there’s probably more!
-  You can speed up your glitch campaign substantially by only plotting
   crashes and successes, since they’re typically much rarer than normal
   behaviour in the target
-  On CW-Husky, glitch offset and width are specified in number of phase
   shift steps, whereas on CW-Lite/Pro, they are specified in percentage
   of clock period. The code provided below sets appropriate starting
   ranges for each case. Run ``help(scope.glitch)`` to understand this
   better.


**In [18]:**

.. code:: ipython3

    from tqdm.notebook import trange
    import struct
    
    # width and offset numbers have a very different meaning for Husky vs Lite/Pro;
    # see help(scope.glitch) for details
    num_tries = 1
    gc.set_range("tries", 1, num_tries)
    if scope._is_husky:
        gc.set_range("width", 0, scope.glitch.phase_shift_steps//2)
        gc.set_range("offset", 0, scope.glitch.phase_shift_steps)
        gc.set_global_step([100]) # reduce if you don't get any glitches
        scope.adc.lo_gain_errors_disabled = True
        scope.adc.clip_errors_disabled = True
    else:
        gc.set_range("width", 0, 48)
        gc.set_range("offset", -48, 48)
        gc.set_global_step([8, 4, 2, 1])
        
    scope.glitch.repeat = 1
    gc.set_step("tries", 1)
    scope.adc.timeout = 0.1
    gc.set_range("ext_offset", 0, 40)
    gc.set_step("ext_offset", 1)
    
    reboot_flush()
    broken = False
    for glitch_setting in gc.glitch_values():
        scope.glitch.offset = glitch_setting[1]
        scope.glitch.width = glitch_setting[0]
        scope.glitch.ext_offset = glitch_setting[2]
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
            gc.add("reset")
    
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
            gc.add("reset")
    
            #Device is slow to boot?
            reboot_flush()
    
        else:
            val = target.simpleserial_read_witherrors('r', 4, glitch_timeout=10, timeout=50)#For loop check
            if val['valid'] is False:
                gc.add("reset")
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
                    gc.add("success")
                    print(val['payload'])
                    print("🐙", end="")
                    break # <-- remove this to try for multiple glitches
                else:
                    gc.add("normal")
        # ###################
        # END SOLUTION
        # ###################
    
    print("Done glitching")


**Out [18]:**



.. parsed-literal::

    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:799) Partial reconfiguration for offset = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work





.. parsed-literal::

    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work





.. parsed-literal::

    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work





.. parsed-literal::

    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:796) Partial reconfiguration for width = 0 may not work
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:288) Device reported error 0x10
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:290) CWbytearray(b'00 65 01 10 42 00')





.. parsed-literal::

    CWbytearray(b'00 02 20 69')
    🐙Done glitching



Results
~~~~~~~

In addition to plotting, the glitch controller also has the capability
to return results as a list that groups paramters and results. These
results give both the number of each result, as well as the rate of each
result:


**In [19]:**

.. code:: ipython3

    gc.calc()


**Out [19]:**



.. parsed-literal::

    [((0, -48, 0, 1),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, -48, 1, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 2, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 3, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 4, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 5, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 6, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 7, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 8, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 9, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 10, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 11, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 12, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 13, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 14, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 15, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 16, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 17, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 18, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 19, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 20, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 21, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 22, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 23, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 24, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 25, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 26, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 27, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 28, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 29, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 30, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 31, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 32, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 33, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 34, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 35, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 36, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 37, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 38, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 39, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 40, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 0, 1),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, -40, 1, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 2, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 3, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 4, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 5, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 6, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 7, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 8, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 9, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 10, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 11, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 12, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 13, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 14, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 15, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 16, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 17, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 18, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 19, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 20, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 21, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 22, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 23, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 24, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 25, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 26, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 27, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 28, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 29, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 30, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 31, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 32, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 33, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 34, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 35, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 36, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 37, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 38, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 39, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 40, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 0, 1),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, -32, 1, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 2, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 3, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 4, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 5, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 6, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 7, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 8, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 9, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 10, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 11, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 12, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 13, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 14, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 15, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 16, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 17, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 18, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 19, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 20, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 21, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 22, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 23, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 24, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 25, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 26, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 27, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 28, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 29, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 30, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 31, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 32, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 33, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 34, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 35, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 36, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 37, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 38, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 39, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 40, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 0, 1),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, -24, 1, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 2, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 3, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 4, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 5, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 6, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 7, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 8, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 9, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 10, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 11, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 12, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 13, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 14, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 15, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 16, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 17, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 18, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 19, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 20, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 21, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 22, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 23, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 24, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 25, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 26, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 27, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 28, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 29, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 30, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 31, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 32, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 33, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 34, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 35, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 36, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 37, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 38, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 39, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 40, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 0, 1),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, -16, 1, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 2, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 3, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 4, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 5, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 6, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 7, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 8, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 9, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 10, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 11, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 12, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 13, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 14, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 15, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 16, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 17, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 18, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 19, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 20, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 21, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 22, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 23, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 24, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 25, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 26, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 27, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 28, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 29, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 30, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 31, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 32, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 33, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 34, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 35, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 36, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 37, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 38, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 39, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 40, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 0, 1),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, -8, 1, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 2, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 3, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 4, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 5, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 6, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 7, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 8, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 9, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 10, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 11, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 12, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 13, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 14, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 15, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 16, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 17, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 18, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 19, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 20, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 21, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 22, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 23, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 24, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 25, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 26, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 27, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 28, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 29, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 30, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 31, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 32, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 33, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 34, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 35, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 36, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 37, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 38, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 39, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 40, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 0, 1),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 0, 1, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 2, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 3, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 4, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 5, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 6, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 7, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 8, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 9, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 10, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 11, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 12, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 13, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 14, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 15, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 16, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 17, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 18, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 19, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 20, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 21, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 22, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 23, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 24, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 25, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 26, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 27, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 28, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 29, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 30, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 31, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 32, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 33, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 34, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 35, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 36, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 37, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 38, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 39, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 40, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 0, 1),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 8, 1, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 2, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 3, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 4, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 5, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 6, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 7, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 8, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 9, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 10, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 11, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 12, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 13, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 14, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 15, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 16, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 17, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 18, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 19, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 20, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 21, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 22, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 23, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 24, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 25, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 26, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 27, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 28, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 29, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 30, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 31, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 32, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 33, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 34, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 35, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 36, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 37, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 38, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 39, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 40, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 0, 1),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 16, 1, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 2, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 3, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 4, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 5, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 6, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 7, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 8, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 9, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 10, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 11, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 12, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 13, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 14, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 15, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 16, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 17, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 18, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 19, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 20, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 21, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 22, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 23, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 24, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 25, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 26, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 27, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 28, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 29, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 30, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 31, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 32, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 33, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 34, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 35, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 36, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 37, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 38, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 39, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 40, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 0, 1),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 24, 1, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 2, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 3, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 4, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 5, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 6, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 7, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 8, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 9, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 10, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 11, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 12, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 13, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 14, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 15, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 16, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 17, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 18, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 19, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 20, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 21, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 22, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 23, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 24, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 25, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 26, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 27, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 28, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 29, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 30, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 31, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 32, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 33, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 34, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 35, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 36, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 37, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 38, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 39, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 40, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 32, 0, 1),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 1, 1),
      {'total': 2,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 2,
       'normal_rate': 1.0}),
     ((0, 32, 2, 1),
      {'total': 2,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 2,
       'normal_rate': 1.0}),
     ((0, 32, 3, 1),
      {'total': 2,
       'success': 0,
       'success_rate': 0.0,
       'reset': 1,
       'reset_rate': 0.5,
       'normal': 1,
       'normal_rate': 0.5}),
     ((0, 32, 4, 1),
      {'total': 3,
       'success': 0,
       'success_rate': 0.0,
       'reset': 1,
       'reset_rate': 0.3333333333333333,
       'normal': 2,
       'normal_rate': 0.6666666666666666}),
     ((0, 32, 5, 1),
      {'total': 2,
       'success': 0,
       'success_rate': 0.0,
       'reset': 1,
       'reset_rate': 0.5,
       'normal': 1,
       'normal_rate': 0.5}),
     ((0, 32, 6, 1),
      {'total': 3,
       'success': 0,
       'success_rate': 0.0,
       'reset': 1,
       'reset_rate': 0.3333333333333333,
       'normal': 2,
       'normal_rate': 0.6666666666666666}),
     ((0, 32, 7, 1),
      {'total': 2,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 2,
       'normal_rate': 1.0}),
     ((0, 32, 8, 1),
      {'total': 2,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 2,
       'normal_rate': 1.0}),
     ((0, 32, 9, 1),
      {'total': 2,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 2,
       'normal_rate': 1.0}),
     ((0, 32, 10, 1),
      {'total': 2,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 2,
       'normal_rate': 1.0}),
     ((0, 32, 11, 1),
      {'total': 2,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 2,
       'normal_rate': 1.0}),
     ((0, 32, 12, 1),
      {'total': 2,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 2,
       'normal_rate': 1.0}),
     ((0, 32, 13, 1),
      {'total': 2,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 2,
       'normal_rate': 1.0}),
     ((0, 32, 14, 1),
      {'total': 2,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 2,
       'normal_rate': 1.0}),
     ((0, 32, 15, 1),
      {'total': 2,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 2,
       'normal_rate': 1.0}),
     ((0, 32, 16, 1),
      {'total': 2,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 2,
       'normal_rate': 1.0}),
     ((0, 32, 17, 1),
      {'total': 2,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 2,
       'normal_rate': 1.0}),
     ((0, 32, 18, 1),
      {'total': 2,
       'success': 1,
       'success_rate': 0.5,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 0.5}),
     ((0, 32, 19, 1),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 20, 1),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 21, 1),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 22, 1),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 23, 1),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 24, 1),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 25, 1),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 26, 1),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 1,
       'reset_rate': 1.0,
       'normal': 0,
       'normal_rate': 0.0}),
     ((0, 32, 27, 1),
      {'total': 2,
       'success': 0,
       'success_rate': 0.0,
       'reset': 1,
       'reset_rate': 0.5,
       'normal': 1,
       'normal_rate': 0.5}),
     ((0, 32, 28, 1),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 29, 1),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 30, 1),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 31, 1),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 32, 1),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 33, 1),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 34, 1),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 35, 1),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 36, 1),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 37, 1),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 38, 1),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 39, 1),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 40, 1),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0})]



You can also get results back with some parameters ignored. Results from
parameters that now match will be grouped. This is particularly useful
with something like the ``"tries"`` parameter, as you don’t typically
care whether a glitch was successful on your first, second, or third
attempt:


**In [20]:**

.. code:: ipython3

    results = gc.calc(ignore_params="tries")
    results


**Out [20]:**



.. parsed-literal::

    [((0, -48, 0),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, -48, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 2),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 3),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 4),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 5),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 6),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 7),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 8),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 9),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 10),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 11),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 12),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 13),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 14),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 15),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 16),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 17),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 18),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 19),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 20),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 21),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 22),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 23),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 24),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 25),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 26),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 27),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 28),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 29),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 30),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 31),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 32),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 33),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 34),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 35),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 36),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 37),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 38),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 39),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 40),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 0),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, -40, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 2),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 3),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 4),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 5),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 6),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 7),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 8),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 9),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 10),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 11),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 12),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 13),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 14),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 15),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 16),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 17),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 18),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 19),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 20),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 21),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 22),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 23),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 24),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 25),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 26),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 27),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 28),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 29),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 30),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 31),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 32),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 33),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 34),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 35),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 36),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 37),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 38),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 39),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 40),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 0),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, -32, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 2),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 3),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 4),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 5),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 6),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 7),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 8),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 9),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 10),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 11),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 12),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 13),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 14),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 15),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 16),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 17),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 18),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 19),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 20),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 21),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 22),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 23),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 24),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 25),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 26),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 27),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 28),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 29),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 30),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 31),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 32),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 33),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 34),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 35),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 36),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 37),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 38),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 39),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 40),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 0),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, -24, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 2),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 3),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 4),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 5),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 6),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 7),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 8),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 9),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 10),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 11),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 12),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 13),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 14),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 15),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 16),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 17),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 18),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 19),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 20),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 21),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 22),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 23),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 24),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 25),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 26),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 27),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 28),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 29),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 30),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 31),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 32),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 33),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 34),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 35),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 36),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 37),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 38),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 39),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 40),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 0),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, -16, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 2),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 3),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 4),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 5),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 6),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 7),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 8),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 9),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 10),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 11),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 12),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 13),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 14),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 15),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 16),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 17),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 18),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 19),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 20),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 21),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 22),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 23),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 24),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 25),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 26),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 27),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 28),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 29),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 30),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 31),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 32),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 33),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 34),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 35),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 36),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 37),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 38),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 39),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 40),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 0),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, -8, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 2),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 3),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 4),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 5),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 6),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 7),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 8),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 9),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 10),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 11),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 12),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 13),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 14),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 15),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 16),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 17),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 18),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 19),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 20),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 21),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 22),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 23),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 24),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 25),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 26),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 27),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 28),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 29),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 30),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 31),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 32),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 33),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 34),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 35),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 36),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 37),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 38),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 39),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 40),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 0),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 0, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 2),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 3),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 4),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 5),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 6),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 7),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 8),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 9),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 10),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 11),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 12),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 13),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 14),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 15),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 16),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 17),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 18),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 19),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 20),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 21),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 22),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 23),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 24),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 25),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 26),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 27),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 28),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 29),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 30),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 31),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 32),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 33),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 34),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 35),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 36),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 37),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 38),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 39),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 40),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 0),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 8, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 2),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 3),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 4),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 5),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 6),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 7),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 8),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 9),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 10),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 11),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 12),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 13),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 14),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 15),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 16),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 17),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 18),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 19),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 20),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 21),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 22),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 23),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 24),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 25),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 26),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 27),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 28),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 29),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 30),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 31),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 32),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 33),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 34),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 35),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 36),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 37),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 38),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 39),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 40),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 0),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 16, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 2),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 3),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 4),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 5),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 6),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 7),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 8),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 9),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 10),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 11),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 12),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 13),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 14),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 15),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 16),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 17),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 18),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 19),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 20),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 21),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 22),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 23),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 24),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 25),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 26),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 27),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 28),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 29),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 30),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 31),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 32),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 33),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 34),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 35),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 36),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 37),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 38),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 39),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 40),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 0),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 24, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 2),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 3),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 4),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 5),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 6),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 7),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 8),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 9),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 10),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 11),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 12),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 13),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 14),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 15),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 16),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 17),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 18),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 19),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 20),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 21),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 22),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 23),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 24),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 25),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 26),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 27),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 28),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 29),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 30),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 31),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 32),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 33),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 34),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 35),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 36),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 37),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 38),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 39),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 40),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 32, 0),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 1),
      {'total': 2,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 2,
       'normal_rate': 1.0}),
     ((0, 32, 2),
      {'total': 2,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 2,
       'normal_rate': 1.0}),
     ((0, 32, 3),
      {'total': 2,
       'success': 0,
       'success_rate': 0.0,
       'reset': 1,
       'reset_rate': 0.5,
       'normal': 1,
       'normal_rate': 0.5}),
     ((0, 32, 4),
      {'total': 3,
       'success': 0,
       'success_rate': 0.0,
       'reset': 1,
       'reset_rate': 0.3333333333333333,
       'normal': 2,
       'normal_rate': 0.6666666666666666}),
     ((0, 32, 5),
      {'total': 2,
       'success': 0,
       'success_rate': 0.0,
       'reset': 1,
       'reset_rate': 0.5,
       'normal': 1,
       'normal_rate': 0.5}),
     ((0, 32, 6),
      {'total': 3,
       'success': 0,
       'success_rate': 0.0,
       'reset': 1,
       'reset_rate': 0.3333333333333333,
       'normal': 2,
       'normal_rate': 0.6666666666666666}),
     ((0, 32, 7),
      {'total': 2,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 2,
       'normal_rate': 1.0}),
     ((0, 32, 8),
      {'total': 2,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 2,
       'normal_rate': 1.0}),
     ((0, 32, 9),
      {'total': 2,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 2,
       'normal_rate': 1.0}),
     ((0, 32, 10),
      {'total': 2,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 2,
       'normal_rate': 1.0}),
     ((0, 32, 11),
      {'total': 2,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 2,
       'normal_rate': 1.0}),
     ((0, 32, 12),
      {'total': 2,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 2,
       'normal_rate': 1.0}),
     ((0, 32, 13),
      {'total': 2,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 2,
       'normal_rate': 1.0}),
     ((0, 32, 14),
      {'total': 2,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 2,
       'normal_rate': 1.0}),
     ((0, 32, 15),
      {'total': 2,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 2,
       'normal_rate': 1.0}),
     ((0, 32, 16),
      {'total': 2,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 2,
       'normal_rate': 1.0}),
     ((0, 32, 17),
      {'total': 2,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 2,
       'normal_rate': 1.0}),
     ((0, 32, 18),
      {'total': 2,
       'success': 1,
       'success_rate': 0.5,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 0.5}),
     ((0, 32, 19),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 20),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 21),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 22),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 23),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 24),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 25),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 26),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 1,
       'reset_rate': 1.0,
       'normal': 0,
       'normal_rate': 0.0}),
     ((0, 32, 27),
      {'total': 2,
       'success': 0,
       'success_rate': 0.0,
       'reset': 1,
       'reset_rate': 0.5,
       'normal': 1,
       'normal_rate': 0.5}),
     ((0, 32, 28),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 29),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 30),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 31),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 32),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 33),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 34),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 35),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 36),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 37),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 38),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 39),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 40),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0})]



Finally, ``calc()`` can also sort by different results. A common use for
this is to sort by success rate:


**In [21]:**

.. code:: ipython3

    results = gc.calc(ignore_params="tries", sort="success_rate")
    results


**Out [21]:**



.. parsed-literal::

    [((0, 32, 18),
      {'total': 2,
       'success': 1,
       'success_rate': 0.5,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 0.5}),
     ((0, 32, 40),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 39),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 38),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 37),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 36),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 35),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 34),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 33),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 32),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 31),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 30),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 29),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 28),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 27),
      {'total': 2,
       'success': 0,
       'success_rate': 0.0,
       'reset': 1,
       'reset_rate': 0.5,
       'normal': 1,
       'normal_rate': 0.5}),
     ((0, 32, 26),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 1,
       'reset_rate': 1.0,
       'normal': 0,
       'normal_rate': 0.0}),
     ((0, 32, 25),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 24),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 23),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 22),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 21),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 20),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 19),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 32, 17),
      {'total': 2,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 2,
       'normal_rate': 1.0}),
     ((0, 32, 16),
      {'total': 2,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 2,
       'normal_rate': 1.0}),
     ((0, 32, 15),
      {'total': 2,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 2,
       'normal_rate': 1.0}),
     ((0, 32, 14),
      {'total': 2,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 2,
       'normal_rate': 1.0}),
     ((0, 32, 13),
      {'total': 2,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 2,
       'normal_rate': 1.0}),
     ((0, 32, 12),
      {'total': 2,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 2,
       'normal_rate': 1.0}),
     ((0, 32, 11),
      {'total': 2,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 2,
       'normal_rate': 1.0}),
     ((0, 32, 10),
      {'total': 2,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 2,
       'normal_rate': 1.0}),
     ((0, 32, 9),
      {'total': 2,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 2,
       'normal_rate': 1.0}),
     ((0, 32, 8),
      {'total': 2,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 2,
       'normal_rate': 1.0}),
     ((0, 32, 7),
      {'total': 2,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 2,
       'normal_rate': 1.0}),
     ((0, 32, 6),
      {'total': 3,
       'success': 0,
       'success_rate': 0.0,
       'reset': 1,
       'reset_rate': 0.3333333333333333,
       'normal': 2,
       'normal_rate': 0.6666666666666666}),
     ((0, 32, 5),
      {'total': 2,
       'success': 0,
       'success_rate': 0.0,
       'reset': 1,
       'reset_rate': 0.5,
       'normal': 1,
       'normal_rate': 0.5}),
     ((0, 32, 4),
      {'total': 3,
       'success': 0,
       'success_rate': 0.0,
       'reset': 1,
       'reset_rate': 0.3333333333333333,
       'normal': 2,
       'normal_rate': 0.6666666666666666}),
     ((0, 32, 3),
      {'total': 2,
       'success': 0,
       'success_rate': 0.0,
       'reset': 1,
       'reset_rate': 0.5,
       'normal': 1,
       'normal_rate': 0.5}),
     ((0, 32, 2),
      {'total': 2,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 2,
       'normal_rate': 1.0}),
     ((0, 32, 1),
      {'total': 2,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 2,
       'normal_rate': 1.0}),
     ((0, 32, 0),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 24, 40),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 39),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 38),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 37),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 36),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 35),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 34),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 33),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 32),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 31),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 30),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 29),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 28),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 27),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 26),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 25),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 24),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 23),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 22),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 21),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 20),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 19),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 18),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 17),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 16),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 15),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 14),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 13),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 12),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 11),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 10),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 9),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 8),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 7),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 6),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 5),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 4),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 3),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 2),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 24, 0),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 16, 40),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 39),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 38),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 37),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 36),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 35),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 34),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 33),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 32),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 31),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 30),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 29),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 28),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 27),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 26),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 25),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 24),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 23),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 22),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 21),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 20),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 19),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 18),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 17),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 16),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 15),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 14),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 13),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 12),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 11),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 10),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 9),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 8),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 7),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 6),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 5),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 4),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 3),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 2),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 16, 0),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 8, 40),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 39),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 38),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 37),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 36),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 35),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 34),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 33),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 32),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 31),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 30),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 29),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 28),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 27),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 26),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 25),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 24),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 23),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 22),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 21),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 20),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 19),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 18),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 17),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 16),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 15),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 14),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 13),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 12),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 11),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 10),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 9),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 8),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 7),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 6),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 5),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 4),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 3),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 2),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 8, 0),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, 0, 40),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 39),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 38),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 37),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 36),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 35),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 34),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 33),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 32),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 31),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 30),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 29),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 28),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 27),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 26),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 25),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 24),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 23),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 22),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 21),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 20),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 19),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 18),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 17),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 16),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 15),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 14),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 13),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 12),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 11),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 10),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 9),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 8),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 7),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 6),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 5),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 4),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 3),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 2),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, 0, 0),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, -8, 40),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 39),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 38),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 37),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 36),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 35),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 34),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 33),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 32),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 31),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 30),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 29),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 28),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 27),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 26),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 25),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 24),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 23),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 22),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 21),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 20),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 19),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 18),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 17),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 16),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 15),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 14),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 13),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 12),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 11),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 10),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 9),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 8),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 7),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 6),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 5),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 4),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 3),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 2),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -8, 0),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, -16, 40),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 39),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 38),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 37),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 36),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 35),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 34),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 33),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 32),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 31),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 30),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 29),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 28),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 27),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 26),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 25),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 24),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 23),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 22),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 21),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 20),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 19),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 18),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 17),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 16),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 15),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 14),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 13),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 12),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 11),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 10),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 9),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 8),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 7),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 6),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 5),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 4),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 3),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 2),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -16, 0),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, -24, 40),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 39),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 38),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 37),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 36),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 35),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 34),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 33),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 32),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 31),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 30),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 29),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 28),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 27),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 26),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 25),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 24),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 23),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 22),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 21),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 20),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 19),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 18),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 17),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 16),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 15),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 14),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 13),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 12),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 11),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 10),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 9),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 8),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 7),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 6),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 5),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 4),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 3),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 2),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -24, 0),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, -32, 40),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 39),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 38),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 37),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 36),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 35),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 34),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 33),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 32),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 31),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 30),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 29),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 28),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 27),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 26),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 25),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 24),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 23),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 22),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 21),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 20),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 19),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 18),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 17),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 16),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 15),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 14),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 13),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 12),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 11),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 10),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 9),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 8),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 7),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 6),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 5),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 4),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 3),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 2),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -32, 0),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, -40, 40),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 39),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 38),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 37),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 36),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 35),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 34),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 33),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 32),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 31),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 30),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 29),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 28),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 27),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 26),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 25),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 24),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 23),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 22),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 21),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 20),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 19),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 18),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 17),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 16),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 15),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 14),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 13),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 12),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 11),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 10),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 9),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 8),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 7),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 6),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 5),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 4),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 3),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 2),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -40, 0),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0}),
     ((0, -48, 40),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 39),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 38),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 37),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 36),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 35),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 34),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 33),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 32),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 31),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 30),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 29),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 28),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 27),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 26),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 25),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 24),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 23),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 22),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 21),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 20),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 19),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 18),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 17),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 16),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 15),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 14),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 13),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 12),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 11),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 10),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 9),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 8),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 7),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 6),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 5),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 4),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 3),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 2),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 1),
      {'total': 4,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 4,
       'normal_rate': 1.0}),
     ((0, -48, 0),
      {'total': 1,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 1,
       'normal_rate': 1.0})]



Plotting Glitch Results
~~~~~~~~~~~~~~~~~~~~~~~

We can replot our glitch map using the ``plot_2d()`` method. Settings
are similar to ``glitch_plot()``. If ``plotdots`` are not specified, the
same ones as the ``glitch_plot()`` will be used.

``plot_2d()`` also has the advantage of displaying an alpha channel. The
hover tool, which allows you to see the coordinates by mousing over a
plot point, has a separate button for each group on the right toolbar.
This allows you to see, for example, only the hover information for
successes by turning the reset hover off. The hover tool will also show
the rate of occurrence for the group.


**In [22]:**

.. code:: ipython3

    gc.plot_2d()


**Out [22]:**






.. raw:: html

    <div class="data_html">
        <style>.bk-root, .bk-root .bk:before, .bk-root .bk:after {
      font-family: var(--jp-ui-font-size1);
      font-size: var(--jp-ui-font-size1);
      color: var(--jp-ui-font-color1);
    }
    </style>
    </div>




.. parsed-literal::

    /home/testserveradmin/.pyenv/versions/cwtests/lib/python3.10/site-packages/holoviews/core/data/pandas.py:39: FutureWarning: Series.\_\_getitem\_\_ treating keys as positions is deprecated. In a future version, integer keys will always be treated as labels (consistent with DataFrame behavior). To access a value by position, use \`ser.iloc[pos]\`
      return dataset.data.dtypes[idx].type
    /home/testserveradmin/.pyenv/versions/cwtests/lib/python3.10/site-packages/holoviews/core/data/pandas.py:39: FutureWarning: Series.\_\_getitem\_\_ treating keys as positions is deprecated. In a future version, integer keys will always be treated as labels (consistent with DataFrame behavior). To access a value by position, use \`ser.iloc[pos]\`
      return dataset.data.dtypes[idx].type







.. raw:: html

    <div class="data_html">
        <div id='1267'>
      <div class="bk-root" id="84814c61-88fc-449b-b632-ef2b1def3c59" data-root-id="1267"></div>
    </div>
    <script type="application/javascript">(function(root) {
      function embed_document(root) {
        var docs_json = {"6042f5b5-4b92-4e7d-b0ae-32ebb0da8d5e":{"defs":[{"extends":null,"module":null,"name":"ReactiveHTML1","overrides":[],"properties":[]},{"extends":null,"module":null,"name":"FlexBox1","overrides":[],"properties":[{"default":"flex-start","kind":null,"name":"align_content"},{"default":"flex-start","kind":null,"name":"align_items"},{"default":"row","kind":null,"name":"flex_direction"},{"default":"wrap","kind":null,"name":"flex_wrap"},{"default":"flex-start","kind":null,"name":"justify_content"}]},{"extends":null,"module":null,"name":"GridStack1","overrides":[],"properties":[{"default":"warn","kind":null,"name":"mode"},{"default":null,"kind":null,"name":"ncols"},{"default":null,"kind":null,"name":"nrows"},{"default":true,"kind":null,"name":"allow_resize"},{"default":true,"kind":null,"name":"allow_drag"},{"default":[],"kind":null,"name":"state"}]},{"extends":null,"module":null,"name":"click1","overrides":[],"properties":[{"default":"","kind":null,"name":"terminal_output"},{"default":"","kind":null,"name":"debug_name"},{"default":0,"kind":null,"name":"clears"}]},{"extends":null,"module":null,"name":"NotificationAreaBase1","overrides":[],"properties":[{"default":"bottom-right","kind":null,"name":"position"},{"default":0,"kind":null,"name":"_clear"}]},{"extends":null,"module":null,"name":"NotificationArea1","overrides":[],"properties":[{"default":[],"kind":null,"name":"notifications"},{"default":"bottom-right","kind":null,"name":"position"},{"default":0,"kind":null,"name":"_clear"},{"default":[{"background":"#ffc107","icon":{"className":"fas fa-exclamation-triangle","color":"white","tagName":"i"},"type":"warning"},{"background":"#007bff","icon":{"className":"fas fa-info-circle","color":"white","tagName":"i"},"type":"info"}],"kind":null,"name":"types"}]},{"extends":null,"module":null,"name":"Notification","overrides":[],"properties":[{"default":null,"kind":null,"name":"background"},{"default":3000,"kind":null,"name":"duration"},{"default":null,"kind":null,"name":"icon"},{"default":"","kind":null,"name":"message"},{"default":null,"kind":null,"name":"notification_type"},{"default":false,"kind":null,"name":"_destroyed"}]},{"extends":null,"module":null,"name":"TemplateActions1","overrides":[],"properties":[{"default":0,"kind":null,"name":"open_modal"},{"default":0,"kind":null,"name":"close_modal"}]},{"extends":null,"module":null,"name":"MaterialTemplateActions1","overrides":[],"properties":[{"default":0,"kind":null,"name":"open_modal"},{"default":0,"kind":null,"name":"close_modal"}]}],"roots":{"references":[{"attributes":{"coordinates":null,"group":null,"text_color":"black","text_font_size":"12pt"},"id":"1275","type":"Title"},{"attributes":{"callback":null,"renderers":[{"id":"1326"}],"tags":["hv_created"],"tooltips":[["width","@{width}"],["offset","@{offset}"],["success_rate","@{success_rate}"]]},"id":"1272","type":"HoverTool"},{"attributes":{"fill_alpha":{"value":0.016129032258064516},"fill_color":{"value":"#007f00"},"hatch_alpha":{"value":0.1},"hatch_color":{"value":"#007f00"},"line_alpha":{"value":0.016129032258064516},"line_color":{"value":"#007f00"},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"width"},"y":{"field":"offset"}},"id":"1324","type":"Scatter"},{"attributes":{"angle":{"value":0.0},"fill_alpha":{"value":1.0},"fill_color":{"value":"#30a2da"},"hatch_alpha":{"value":1.0},"hatch_color":{"value":"#30a2da"},"hatch_scale":{"value":12.0},"hatch_weight":{"value":1.0},"line_alpha":{"value":1.0},"line_cap":{"value":"butt"},"line_color":{"value":"#30a2da"},"line_dash":{"value":[]},"line_dash_offset":{"value":0},"line_join":{"value":"bevel"},"line_width":{"value":1},"marker":{"value":"circle"},"size":{"value":2.449489742783178},"tags":["apply_ranges"],"x":{"field":"x"},"y":{"field":"y"}},"id":"1319","type":"Scatter"},{"attributes":{},"id":"1282","type":"LinearScale"},{"attributes":{},"id":"1284","type":"BasicTicker"},{"attributes":{"label":{"value":"Success"},"renderers":[{"id":"1326"}]},"id":"1341","type":"LegendItem"},{"attributes":{},"id":"1344","type":"Selection"},{"attributes":{"end":33.2,"reset_end":33.2,"reset_start":30.8,"start":30.8,"tags":[[["y","y",null]],{"autorange":false,"invert_yaxis":false}]},"id":"1269","type":"Range1d"},{"attributes":{"coordinates":null,"data_source":{"id":"1320"},"glyph":{"id":"1323"},"group":null,"hover_glyph":null,"muted_glyph":{"id":"1325"},"name":"Success","nonselection_glyph":{"id":"1324"},"selection_glyph":{"id":"1342"},"view":{"id":"1327"}},"id":"1326","type":"GlyphRenderer"},{"attributes":{"source":{"id":"1343"}},"id":"1350","type":"CDSView"},{"attributes":{"below":[{"id":"1283"}],"center":[{"id":"1286"},{"id":"1290"},{"id":"1340"}],"left":[{"id":"1287"}],"margin":[5,5,5,5],"min_border_bottom":10,"min_border_left":10,"min_border_right":10,"min_border_top":10,"output_backend":"webgl","renderers":[{"id":"1317"},{"id":"1326"},{"id":"1349"}],"sizing_mode":"fixed","title":{"id":"1275"},"toolbar":{"id":"1297"},"width":800,"x_range":{"id":"1268"},"x_scale":{"id":"1281"},"y_range":{"id":"1269"},"y_scale":{"id":"1282"}},"id":"1274","subtype":"Figure","type":"Plot"},{"attributes":{"data":{"offset":[32],"success_rate":{"__ndarray__":"hBBCCCGEkD8=","dtype":"float64","order":"little","shape":[1]},"width":[0]},"selected":{"id":"1321"},"selection_policy":{"id":"1337"}},"id":"1320","type":"ColumnDataSource"},{"attributes":{"source":{"id":"1311"}},"id":"1318","type":"CDSView"},{"attributes":{"angle":{"value":0.7853981633974483},"fill_alpha":{"value":0.2},"fill_color":{"value":"#ff0000"},"hatch_alpha":{"value":0.2},"hatch_color":{"value":"#ff0000"},"line_alpha":{"value":0.2},"line_color":{"value":"#ff0000"},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"width"},"y":{"field":"offset"}},"id":"1348","type":"Scatter"},{"attributes":{},"id":"1295","type":"ResetTool"},{"attributes":{"axis":{"id":"1287"},"coordinates":null,"dimension":1,"grid_line_color":null,"group":null,"ticker":null},"id":"1290","type":"Grid"},{"attributes":{"axis_label":"x","coordinates":null,"formatter":{"id":"1306"},"group":null,"major_label_policy":{"id":"1307"},"ticker":{"id":"1284"}},"id":"1283","type":"LinearAxis"},{"attributes":{"angle":{"value":0.7853981633974483},"fill_alpha":{"value":0.0967741935483871},"fill_color":{"value":"#ff0000"},"hatch_alpha":{"value":0.0967741935483871},"hatch_color":{"value":"#ff0000"},"hatch_scale":{"value":12.0},"hatch_weight":{"value":1.0},"line_alpha":{"value":0.0967741935483871},"line_cap":{"value":"butt"},"line_color":{"value":"#ff0000"},"line_dash":{"value":[]},"line_dash_offset":{"value":0},"line_join":{"value":"bevel"},"line_width":{"value":1},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"width"},"y":{"field":"offset"}},"id":"1366","type":"Scatter"},{"attributes":{},"id":"1321","type":"Selection"},{"attributes":{},"id":"1307","type":"AllLabels"},{"attributes":{"children":[{"id":"1274"}],"height":600,"margin":[0,0,0,0],"name":"Row01432","sizing_mode":"fixed","tags":["embedded"],"width":800},"id":"1267","type":"Row"},{"attributes":{"bottom_units":"screen","coordinates":null,"fill_alpha":0.5,"fill_color":"lightgrey","group":null,"left_units":"screen","level":"overlay","line_alpha":1.0,"line_color":"black","line_dash":[4,4],"line_width":2,"right_units":"screen","syncable":false,"top_units":"screen"},"id":"1296","type":"BoxAnnotation"},{"attributes":{"fill_alpha":{"value":0.2},"fill_color":{"value":"#007f00"},"hatch_alpha":{"value":0.2},"hatch_color":{"value":"#007f00"},"line_alpha":{"value":0.2},"line_color":{"value":"#007f00"},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"width"},"y":{"field":"offset"}},"id":"1325","type":"Scatter"},{"attributes":{"axis":{"id":"1283"},"coordinates":null,"grid_line_color":null,"group":null,"ticker":null},"id":"1286","type":"Grid"},{"attributes":{"fill_alpha":{"value":0.1},"fill_color":{"value":"#30a2da"},"hatch_alpha":{"value":0.1},"hatch_color":{"value":"#30a2da"},"line_alpha":{"value":0.1},"line_color":{"value":"#30a2da"},"size":{"value":2.449489742783178},"tags":["apply_ranges"],"x":{"field":"x"},"y":{"field":"y"}},"id":"1315","type":"Scatter"},{"attributes":{},"id":"1291","type":"SaveTool"},{"attributes":{"overlay":{"id":"1296"}},"id":"1294","type":"BoxZoomTool"},{"attributes":{},"id":"1335","type":"UnionRenderers"},{"attributes":{"active_drag":{"id":"1292"},"active_scroll":{"id":"1293"},"tools":[{"id":"1272"},{"id":"1273"},{"id":"1291"},{"id":"1292"},{"id":"1293"},{"id":"1294"},{"id":"1295"}]},"id":"1297","type":"Toolbar"},{"attributes":{},"id":"1312","type":"Selection"},{"attributes":{},"id":"1309","type":"BasicTickFormatter"},{"attributes":{},"id":"1362","type":"UnionRenderers"},{"attributes":{"angle":{"value":0.7853981633974483},"fill_alpha":{"value":0.0967741935483871},"fill_color":{"value":"#ff0000"},"hatch_alpha":{"value":0.0967741935483871},"hatch_color":{"value":"#ff0000"},"line_alpha":{"value":0.0967741935483871},"line_color":{"value":"#ff0000"},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"width"},"y":{"field":"offset"}},"id":"1346","type":"Scatter"},{"attributes":{"data":{"x":{"__ndarray__":"","dtype":"float64","order":"little","shape":[0]},"y":{"__ndarray__":"","dtype":"float64","order":"little","shape":[0]}},"selected":{"id":"1312"},"selection_policy":{"id":"1335"}},"id":"1311","type":"ColumnDataSource"},{"attributes":{"callback":null,"renderers":[{"id":"1349"}],"tags":["hv_created"],"tooltips":[["width","@{width}"],["offset","@{offset}"],["reset_rate","@{reset_rate}"]]},"id":"1273","type":"HoverTool"},{"attributes":{"data":{"offset":[32],"reset_rate":{"__ndarray__":"xhhjjDHGuD8=","dtype":"float64","order":"little","shape":[1]},"width":[0]},"selected":{"id":"1344"},"selection_policy":{"id":"1362"}},"id":"1343","type":"ColumnDataSource"},{"attributes":{"click_policy":"mute","coordinates":null,"group":null,"items":[{"id":"1341"},{"id":"1365"}]},"id":"1340","type":"Legend"},{"attributes":{"source":{"id":"1320"}},"id":"1327","type":"CDSView"},{"attributes":{"axis_label":"y","coordinates":null,"formatter":{"id":"1309"},"group":null,"major_label_policy":{"id":"1310"},"ticker":{"id":"1288"}},"id":"1287","type":"LinearAxis"},{"attributes":{},"id":"1310","type":"AllLabels"},{"attributes":{},"id":"1306","type":"BasicTickFormatter"},{"attributes":{},"id":"1337","type":"UnionRenderers"},{"attributes":{"coordinates":null,"data_source":{"id":"1311"},"glyph":{"id":"1314"},"group":null,"hover_glyph":null,"muted_glyph":{"id":"1316"},"nonselection_glyph":{"id":"1315"},"selection_glyph":{"id":"1319"},"view":{"id":"1318"}},"id":"1317","type":"GlyphRenderer"},{"attributes":{"angle":{"value":0.7853981633974483},"fill_alpha":{"value":0.0967741935483871},"fill_color":{"value":"#ff0000"},"hatch_alpha":{"value":0.1},"hatch_color":{"value":"#ff0000"},"line_alpha":{"value":0.0967741935483871},"line_color":{"value":"#ff0000"},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"width"},"y":{"field":"offset"}},"id":"1347","type":"Scatter"},{"attributes":{},"id":"1288","type":"BasicTicker"},{"attributes":{"fill_color":{"value":"#30a2da"},"hatch_color":{"value":"#30a2da"},"line_color":{"value":"#30a2da"},"size":{"value":2.449489742783178},"tags":["apply_ranges"],"x":{"field":"x"},"y":{"field":"y"}},"id":"1314","type":"Scatter"},{"attributes":{"angle":{"value":0.0},"fill_alpha":{"value":0.016129032258064516},"fill_color":{"value":"#007f00"},"hatch_alpha":{"value":0.016129032258064516},"hatch_color":{"value":"#007f00"},"hatch_scale":{"value":12.0},"hatch_weight":{"value":1.0},"line_alpha":{"value":0.016129032258064516},"line_cap":{"value":"butt"},"line_color":{"value":"#007f00"},"line_dash":{"value":[]},"line_dash_offset":{"value":0},"line_join":{"value":"bevel"},"line_width":{"value":1},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"width"},"y":{"field":"offset"}},"id":"1342","type":"Scatter"},{"attributes":{"fill_alpha":{"value":0.016129032258064516},"fill_color":{"value":"#007f00"},"hatch_alpha":{"value":0.016129032258064516},"hatch_color":{"value":"#007f00"},"line_alpha":{"value":0.016129032258064516},"line_color":{"value":"#007f00"},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"width"},"y":{"field":"offset"}},"id":"1323","type":"Scatter"},{"attributes":{"end":1.15,"reset_end":1.15,"reset_start":-1.15,"start":-1.15,"tags":[[["x","x",null]],[]]},"id":"1268","type":"Range1d"},{"attributes":{},"id":"1292","type":"PanTool"},{"attributes":{},"id":"1293","type":"WheelZoomTool"},{"attributes":{},"id":"1281","type":"LinearScale"},{"attributes":{"coordinates":null,"data_source":{"id":"1343"},"glyph":{"id":"1346"},"group":null,"hover_glyph":null,"muted_glyph":{"id":"1348"},"name":"Reset","nonselection_glyph":{"id":"1347"},"selection_glyph":{"id":"1366"},"view":{"id":"1350"}},"id":"1349","type":"GlyphRenderer"},{"attributes":{"label":{"value":"Reset"},"renderers":[{"id":"1349"}]},"id":"1365","type":"LegendItem"},{"attributes":{"fill_alpha":{"value":0.2},"fill_color":{"value":"#30a2da"},"hatch_alpha":{"value":0.2},"hatch_color":{"value":"#30a2da"},"line_alpha":{"value":0.2},"line_color":{"value":"#30a2da"},"size":{"value":2.449489742783178},"tags":["apply_ranges"],"x":{"field":"x"},"y":{"field":"y"}},"id":"1316","type":"Scatter"}],"root_ids":["1267"]},"title":"Bokeh Application","version":"2.4.3"}};
        var render_items = [{"docid":"6042f5b5-4b92-4e7d-b0ae-32ebb0da8d5e","root_ids":["1267"],"roots":{"1267":"84814c61-88fc-449b-b632-ef2b1def3c59"}}];
        root.Bokeh.embed.embed_items_notebook(docs_json, render_items);
        for (const render_item of render_items) {
          for (const root_id of render_item.root_ids) {
    	const id_el = document.getElementById(root_id)
    	if (id_el.children.length && (id_el.children[0].className === 'bk-root')) {
    	  const root_el = id_el.children[0]
    	  root_el.id = root_el.id + '-rendered'
    	}
          }
        }
      }
      if (root.Bokeh !== undefined && root.Bokeh.Panel !== undefined) {
        embed_document(root);
      } else {
        var attempts = 0;
        var timer = setInterval(function(root) {
          if (root.Bokeh !== undefined && root.Bokeh.Panel !== undefined) {
            clearInterval(timer);
            embed_document(root);
          } else if (document.readyState == "complete") {
            attempts++;
            if (attempts > 200) {
              clearInterval(timer);
              console.log("Bokeh: ERROR: Unable to run BokehJS code because BokehJS library is missing");
            }
          }
        }, 25, root)
      }
    })(window);</script>
    </div>



Make sure you write down those glitch settings, since we’ll be using for
the rest of the glitching labs! In fact, we’ll be using a lot of the
general code structure here for the rest of the labs, with the only big
changes being:

Repeat
~~~~~~

This lab used a pretty large repeat value. Like the name suggests, this
setting controls how many times the glitch is repeated (i.e. a repeat
value of 5 will place glitches in 5 consecutive clock cycles). Consider
that each glitch inserted has a chance to both cause a glitch or crash
the device. This was pretty advantageous for this lab since we had a lot
of different spots we wanted to place a glitch - using a high repeat
value increased our chance for a crash, but also increased our chance
for a successful glitch. For an attack where we’re targeting a single
instruction, we don’t really increase our glitch chance at all, but
still have the increased crash risk. Worse yet, a successful glitch in a
wrong spot may also cause a crash! It is for that reason that it’s often
better to use a low repeat value when targeting a single instruction.

Ext Offset
~~~~~~~~~~

The ext offset setting controls a delay between the trigger firing and
the glitch being inserted. Like repeat, it’s base on whole clock cycles,
meaning an ext offset of 10 will insert a glitch 10 cycles after the
trigger fires. We didn’t have to worry about this setting for this lab
since the large repeat value was able to take us into the area we
wanted. This won’t be true for many applications, where you’ll have to
try glitches at a large variety of ext_offsets.

Success, Reset, and Normal
~~~~~~~~~~~~~~~~~~~~~~~~~~

These three result states are usually enough to describe most glitch
results. What constitues a success, however, will change based on what
firmware you’re attacking. For example, if we were attacking the Linux
authentication, we might base success on a check to see whether or not
we’re root.


**In [23]:**

.. code:: ipython3

    #scope.dis()
    #target.dis()


**In [24]:**

.. code:: ipython3

    assert broken is True
