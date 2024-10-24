Part 1, Topic 2: Clock Glitching to Bypass Password
===================================================



**SUMMARY:** *In the previous lab, we learned how clock glitching can be
used to cause a target to behave unexpectedly. In this lab, we’ll look
at a slightly more realistic example - glitching past a password check*

**LEARNING OUTCOMES:**

-  Applying previous glitch settings to new firmware
-  Checking for success and failure when glitching

Firmware
--------

We’ve already seen how we can insert clock gliches to mess up a
calculation that a target is trying to make. While this has many
applications, some which will be covered in Fault_201, let’s take a look
at something a little closer to our original example of glitch
vulnerable code: a password check. No need to change out firmware here,
we’re still using the simpleserial-glitch project (though we’ll go
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

There’s really nothing out of the ordinary here - it’s just a simple
password check. We can communicate with it using the ``'p'`` command.


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
    scope.adc.trig\_count                     changed from 347581646                 to 351046770                
    scope.clock.adc\_src                      changed from clkgen\_x1                 to clkgen\_x4                
    scope.clock.adc\_freq                     changed from 29538459                  to 96000000                 
    scope.clock.adc\_rate                     changed from 29538459.0                to 96000000.0               
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
    .
    -en     simpleserial-glitch.c ...
    -en     .././simpleserial/simpleserial.c ...
    Compiling:
    -en     .././hal/stm32f4/stm32f4\_hal.c ...
    .
    Compiling:
    .
    -en     .././hal/stm32f4/stm32f4\_hal\_lowlevel.c ...
    Compiling:
    -en     .././hal/stm32f4/stm32f4\_sysmem.c ...
    .
    Compiling:
    .
    -en     .././hal/stm32f4/stm32f4xx\_hal\_rng.c ...
    Assembling: .././hal/stm32f4/stm32f4\_startup.S
    -e Done!
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
    .
    Creating load file for Flash: simpleserial-glitch-CW308\_STM32F4.bin
    arm-none-eabi-objcopy -O ihex -R .eeprom -R .fuse -R .lock -R .signature simpleserial-glitch-CW308\_STM32F4.elf simpleserial-glitch-CW308\_STM32F4.hex
    Creating load file for EEPROM: simpleserial-glitch-CW308\_STM32F4.eep
    arm-none-eabi-objcopy -j .eeprom --set-section-flags=.eeprom="alloc,load" \
    --change-section-lma .eeprom=0 --no-change-warnings -O ihex simpleserial-glitch-CW308\_STM32F4.elf simpleserial-glitch-CW308\_STM32F4.eep \|\| exit 0
    .
    .
    Creating Symbol Table: simpleserial-glitch-CW308\_STM32F4.sym
    arm-none-eabi-objcopy -O binary -R .eeprom -R .fuse -R .lock -R .signature simpleserial-glitch-CW308\_STM32F4.elf simpleserial-glitch-CW308\_STM32F4.bin
    Creating Extended Listing: simpleserial-glitch-CW308\_STM32F4.lss
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
    if SS_VER == 'SS_VER_2_1':
        target.reset_comms()


**Out [4]:**



.. parsed-literal::

    Detected known STMF32: STM32F40xxx/41xxx
    Extended erase (0x44), this can take ten seconds or more
    Attempting to program 5671 bytes at 0x8000000
    STM32F Programming flash...
    STM32F Reading flash...
    Verified flash OK, 5671 bytes




**In [5]:**

.. code:: ipython3

    def reboot_flush():
        reset_target(scope)
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



We get a response of zero. But if we send the correct password:


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

    scope.cglitch_setup()


**Out [8]:**



.. parsed-literal::

    scope.clock.adc\_freq                     changed from 96000000                  to 30013984                 
    scope.clock.adc\_rate                     changed from 96000000.0                to 30013984.0               



Update the code below to also add an ext offset parameter:


**In [9]:**

.. code:: ipython3

    gc = cw.GlitchController(groups=["success", "reset", "normal"], parameters=["width", "offset", "ext_offset"])
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


Like before, we’ll plot our settings. The plot is 2D, so you’ll need to
make a decision about what to plot. In this case, we’ll plot offset and
ext_offset, but pick whichever you like:


**In [10]:**

.. code:: ipython3

    gc.glitch_plot(plotdots={"success":"+g", "reset":"xr", "normal":None}, x_index="ext_offset", y_index="offset")


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
      <div class="bk-root" id="f147e243-a43e-48e2-8943-6c8584128965" data-root-id="1002"></div>
    </div>
    <script type="application/javascript">(function(root) {
      function embed_document(root) {
        var docs_json = {"744f2171-f5a5-450c-ac75-9756cfec8735":{"defs":[{"extends":null,"module":null,"name":"ReactiveHTML1","overrides":[],"properties":[]},{"extends":null,"module":null,"name":"FlexBox1","overrides":[],"properties":[{"default":"flex-start","kind":null,"name":"align_content"},{"default":"flex-start","kind":null,"name":"align_items"},{"default":"row","kind":null,"name":"flex_direction"},{"default":"wrap","kind":null,"name":"flex_wrap"},{"default":"flex-start","kind":null,"name":"justify_content"}]},{"extends":null,"module":null,"name":"GridStack1","overrides":[],"properties":[{"default":"warn","kind":null,"name":"mode"},{"default":null,"kind":null,"name":"ncols"},{"default":null,"kind":null,"name":"nrows"},{"default":true,"kind":null,"name":"allow_resize"},{"default":true,"kind":null,"name":"allow_drag"},{"default":[],"kind":null,"name":"state"}]},{"extends":null,"module":null,"name":"click1","overrides":[],"properties":[{"default":"","kind":null,"name":"terminal_output"},{"default":"","kind":null,"name":"debug_name"},{"default":0,"kind":null,"name":"clears"}]},{"extends":null,"module":null,"name":"NotificationAreaBase1","overrides":[],"properties":[{"default":"bottom-right","kind":null,"name":"position"},{"default":0,"kind":null,"name":"_clear"}]},{"extends":null,"module":null,"name":"NotificationArea1","overrides":[],"properties":[{"default":[],"kind":null,"name":"notifications"},{"default":"bottom-right","kind":null,"name":"position"},{"default":0,"kind":null,"name":"_clear"},{"default":[{"background":"#ffc107","icon":{"className":"fas fa-exclamation-triangle","color":"white","tagName":"i"},"type":"warning"},{"background":"#007bff","icon":{"className":"fas fa-info-circle","color":"white","tagName":"i"},"type":"info"}],"kind":null,"name":"types"}]},{"extends":null,"module":null,"name":"Notification","overrides":[],"properties":[{"default":null,"kind":null,"name":"background"},{"default":3000,"kind":null,"name":"duration"},{"default":null,"kind":null,"name":"icon"},{"default":"","kind":null,"name":"message"},{"default":null,"kind":null,"name":"notification_type"},{"default":false,"kind":null,"name":"_destroyed"}]},{"extends":null,"module":null,"name":"TemplateActions1","overrides":[],"properties":[{"default":0,"kind":null,"name":"open_modal"},{"default":0,"kind":null,"name":"close_modal"}]},{"extends":null,"module":null,"name":"MaterialTemplateActions1","overrides":[],"properties":[{"default":0,"kind":null,"name":"open_modal"},{"default":0,"kind":null,"name":"close_modal"}]}],"roots":{"references":[{"attributes":{},"id":"1023","type":"BasicTicker"},{"attributes":{},"id":"1028","type":"WheelZoomTool"},{"attributes":{},"id":"1046","type":"Selection"},{"attributes":{},"id":"1027","type":"PanTool"},{"attributes":{},"id":"1026","type":"SaveTool"},{"attributes":{"source":{"id":"1045"}},"id":"1052","type":"CDSView"},{"attributes":{},"id":"1076","type":"UnionRenderers"},{"attributes":{"angle":{"value":0.7853981633974483},"fill_alpha":{"value":0.1},"fill_color":{"value":"#ff0000"},"hatch_alpha":{"value":0.1},"hatch_color":{"value":"#ff0000"},"line_alpha":{"value":0.1},"line_color":{"value":"#ff0000"},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"ext_offset"},"y":{"field":"offset"}},"id":"1058","type":"Scatter"},{"attributes":{"overlay":{"id":"1031"}},"id":"1029","type":"BoxZoomTool"},{"attributes":{"tags":[[["ext_offset","ext_offset",null]],[]]},"id":"1003","type":"Range1d"},{"attributes":{},"id":"1030","type":"ResetTool"},{"attributes":{"tags":[[["offset","offset",null]],{"autorange":false,"invert_yaxis":false}]},"id":"1004","type":"Range1d"},{"attributes":{"angle":{"value":0.7853981633974483},"fill_alpha":{"value":0.2},"fill_color":{"value":"#ff0000"},"hatch_alpha":{"value":0.2},"hatch_color":{"value":"#ff0000"},"line_alpha":{"value":0.2},"line_color":{"value":"#ff0000"},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"ext_offset"},"y":{"field":"offset"}},"id":"1059","type":"Scatter"},{"attributes":{"bottom_units":"screen","coordinates":null,"fill_alpha":0.5,"fill_color":"lightgrey","group":null,"left_units":"screen","level":"overlay","line_alpha":1.0,"line_color":"black","line_dash":[4,4],"line_width":2,"right_units":"screen","syncable":false,"top_units":"screen"},"id":"1031","type":"BoxAnnotation"},{"attributes":{"fill_alpha":{"value":0.2},"fill_color":{"value":"#007f00"},"hatch_alpha":{"value":0.2},"hatch_color":{"value":"#007f00"},"line_alpha":{"value":0.2},"line_color":{"value":"#007f00"},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"ext_offset"},"y":{"field":"offset"}},"id":"1050","type":"Scatter"},{"attributes":{"source":{"id":"1054"}},"id":"1061","type":"CDSView"},{"attributes":{"active_drag":{"id":"1027"},"active_scroll":{"id":"1028"},"tools":[{"id":"1007"},{"id":"1026"},{"id":"1027"},{"id":"1028"},{"id":"1029"},{"id":"1030"}]},"id":"1032","type":"Toolbar"},{"attributes":{"data":{"ext_offset":{"__ndarray__":"","dtype":"float64","order":"little","shape":[0]},"offset":{"__ndarray__":"","dtype":"float64","order":"little","shape":[0]}},"selected":{"id":"1055"},"selection_policy":{"id":"1076"}},"id":"1054","type":"ColumnDataSource"},{"attributes":{"angle":{"value":0.7853981633974483},"fill_alpha":{"value":1.0},"fill_color":{"value":"#ff0000"},"hatch_alpha":{"value":1.0},"hatch_color":{"value":"#ff0000"},"hatch_scale":{"value":12.0},"hatch_weight":{"value":1.0},"line_alpha":{"value":1.0},"line_cap":{"value":"butt"},"line_color":{"value":"#ff0000"},"line_dash":{"value":[]},"line_dash_offset":{"value":0},"line_join":{"value":"bevel"},"line_width":{"value":1},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"ext_offset"},"y":{"field":"offset"}},"id":"1062","type":"Scatter"},{"attributes":{},"id":"1041","type":"AllLabels"},{"attributes":{"angle":{"value":0.7853981633974483},"fill_color":{"value":"#ff0000"},"hatch_color":{"value":"#ff0000"},"line_color":{"value":"#ff0000"},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"ext_offset"},"y":{"field":"offset"}},"id":"1057","type":"Scatter"},{"attributes":{"coordinates":null,"group":null,"text_color":"black","text_font_size":"12pt"},"id":"1010","type":"Title"},{"attributes":{},"id":"1044","type":"AllLabels"},{"attributes":{"callback":null,"renderers":[{"id":"1051"},{"id":"1060"}],"tags":["hv_created"],"tooltips":[["ext_offset","@{ext_offset}"],["offset","@{offset}"]]},"id":"1007","type":"HoverTool"},{"attributes":{},"id":"1040","type":"BasicTickFormatter"},{"attributes":{},"id":"1043","type":"BasicTickFormatter"},{"attributes":{},"id":"1055","type":"Selection"},{"attributes":{"data":{"ext_offset":{"__ndarray__":"","dtype":"float64","order":"little","shape":[0]},"offset":{"__ndarray__":"","dtype":"float64","order":"little","shape":[0]}},"selected":{"id":"1046"},"selection_policy":{"id":"1074"}},"id":"1045","type":"ColumnDataSource"},{"attributes":{"coordinates":null,"data_source":{"id":"1054"},"glyph":{"id":"1057"},"group":null,"hover_glyph":null,"muted_glyph":{"id":"1059"},"nonselection_glyph":{"id":"1058"},"selection_glyph":{"id":"1062"},"view":{"id":"1061"}},"id":"1060","type":"GlyphRenderer"},{"attributes":{"axis_label":"ext_offset","coordinates":null,"formatter":{"id":"1040"},"group":null,"major_label_policy":{"id":"1041"},"ticker":{"id":"1019"}},"id":"1018","type":"LinearAxis"},{"attributes":{},"id":"1019","type":"BasicTicker"},{"attributes":{"fill_color":{"value":"#007f00"},"hatch_color":{"value":"#007f00"},"line_color":{"value":"#007f00"},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"ext_offset"},"y":{"field":"offset"}},"id":"1048","type":"Scatter"},{"attributes":{"below":[{"id":"1018"}],"center":[{"id":"1021"},{"id":"1025"}],"left":[{"id":"1022"}],"margin":[5,5,5,5],"min_border_bottom":10,"min_border_left":10,"min_border_right":10,"min_border_top":10,"output_backend":"webgl","renderers":[{"id":"1051"},{"id":"1060"}],"sizing_mode":"fixed","title":{"id":"1010"},"toolbar":{"id":"1032"},"width":800,"x_range":{"id":"1003"},"x_scale":{"id":"1016"},"y_range":{"id":"1004"},"y_scale":{"id":"1017"}},"id":"1009","subtype":"Figure","type":"Plot"},{"attributes":{"coordinates":null,"data_source":{"id":"1045"},"glyph":{"id":"1048"},"group":null,"hover_glyph":null,"muted_glyph":{"id":"1050"},"nonselection_glyph":{"id":"1049"},"selection_glyph":{"id":"1053"},"view":{"id":"1052"}},"id":"1051","type":"GlyphRenderer"},{"attributes":{},"id":"1016","type":"LinearScale"},{"attributes":{"angle":{"value":0.0},"fill_alpha":{"value":1.0},"fill_color":{"value":"#007f00"},"hatch_alpha":{"value":1.0},"hatch_color":{"value":"#007f00"},"hatch_scale":{"value":12.0},"hatch_weight":{"value":1.0},"line_alpha":{"value":1.0},"line_cap":{"value":"butt"},"line_color":{"value":"#007f00"},"line_dash":{"value":[]},"line_dash_offset":{"value":0},"line_join":{"value":"bevel"},"line_width":{"value":1},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"ext_offset"},"y":{"field":"offset"}},"id":"1053","type":"Scatter"},{"attributes":{"client_comm_id":"9e160a5f69074b9eb32e2ea088c784a4","comm_id":"9e9ec9b326f248b8803a4bbf18d054b2","plot_id":"1002"},"id":"1115","type":"panel.models.comm_manager.CommManager"},{"attributes":{},"id":"1017","type":"LinearScale"},{"attributes":{"children":[{"id":"1009"}],"height":600,"margin":[0,0,0,0],"name":"Row00811","sizing_mode":"fixed","width":800},"id":"1002","type":"Row"},{"attributes":{"axis":{"id":"1018"},"coordinates":null,"grid_line_color":null,"group":null,"ticker":null},"id":"1021","type":"Grid"},{"attributes":{},"id":"1074","type":"UnionRenderers"},{"attributes":{"axis_label":"offset","coordinates":null,"formatter":{"id":"1043"},"group":null,"major_label_policy":{"id":"1044"},"ticker":{"id":"1023"}},"id":"1022","type":"LinearAxis"},{"attributes":{"fill_alpha":{"value":0.1},"fill_color":{"value":"#007f00"},"hatch_alpha":{"value":0.1},"hatch_color":{"value":"#007f00"},"line_alpha":{"value":0.1},"line_color":{"value":"#007f00"},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"ext_offset"},"y":{"field":"offset"}},"id":"1049","type":"Scatter"},{"attributes":{"axis":{"id":"1022"},"coordinates":null,"dimension":1,"grid_line_color":null,"group":null,"ticker":null},"id":"1025","type":"Grid"}],"root_ids":["1002","1115"]},"title":"Bokeh Application","version":"2.4.3"}};
        var render_items = [{"docid":"744f2171-f5a5-450c-ac75-9756cfec8735","root_ids":["1002"],"roots":{"1002":"f147e243-a43e-48e2-8943-6c8584128965"}}];
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



And make a glitch loop. Make sure you use some successful settings that
you found in the previous lab, since it will make this one much shorter!

One change you probably want to make is to add a scan for ext_offset.
The number of places we can insert a successful glitch has gone way
down. Doing this will also be very important for future labs.


**In [11]:**

.. code:: ipython3

    from tqdm.notebook import tqdm
    import re
    import struct
    sample_size = 1
    
    if scope._is_husky:
        gc.set_range("width", 3500, 4500)
        gc.set_range("offset", 1300, 3200)
        gc.set_global_step([400, 200, 100])
        gc.set_range("ext_offset", 60, 100)
        gc.set_step("ext_offset", 1)
    else:
        gc.set_global_step(1)
        if PLATFORM == "CWLITEXMEGA":
            gc.set_range("width", 45, 49.8)
            gc.set_range("offset", -46, -49.8)
            gc.set_range("ext_offset", 4, 70)
            sample_size = 10
        elif PLATFORM == "CW308_STM32F4":
            gc.set_range("width", 0.4, 10)
            gc.set_range("offset", 40, 49.8)
        elif PLATFORM == "CWLITEARM":
            gc.set_range("width", 0.8, 3.6)
            gc.set_range("offset", -4, -2)
            gc.set_range("ext_offset", 0, 100)
            gc.set_global_step(0.4)
    
    gc.set_step("ext_offset", 1)
    scope.glitch.repeat = 1
    reboot_flush()
    broken = False
    scope.adc.timeout = 0.5
    
    for glitch_settings in gc.glitch_values():
        scope.glitch.offset = glitch_settings[1]
        scope.glitch.width = glitch_settings[0]
        scope.glitch.ext_offset = glitch_settings[2]
        for i in range(sample_size):
            if scope.adc.state:
                # can detect crash here (fast) before timing out (slow)
                print("Trigger still high!")
                gc.add("reset")
                
                #Device is slow to boot?
                reboot_flush()
    
            scope.arm()
            target.simpleserial_write('p', bytearray([0]*5))
    
            ret = scope.capture()
    
            if ret:
                print('Timeout - no trigger')
                gc.add("reset")
    
                #Device is slow to boot?
                reboot_flush()
    
            else:
                val = target.simpleserial_read_witherrors('r', 1, glitch_timeout=10, timeout=50)#For loop check
                if val['valid'] is False:
                    gc.add("reset")
                else:
    
                    if val['payload'] == bytearray([1]): #for loop check
                        #broken = True
                        gc.add("success")
                        print(val['payload'])
                        print(scope.glitch.width, scope.glitch.offset, scope.glitch.ext_offset)
                        print("🐙", end="")
                        #break
                    else:
                        gc.add("normal")
        if broken:
            break

For this lab, you may want two copies of your results; one for finding
effective ext_offsets:


**In [12]:**

.. code:: ipython3

    results = gc.calc(ignore_params=["width", "offset"], sort="success_rate")
    results


**Out [12]:**



.. parsed-literal::

    [((10.0,),
      {'total': 100,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 100,
       'normal_rate': 1.0}),
     ((9.0,),
      {'total': 100,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 100,
       'normal_rate': 1.0}),
     ((8.0,),
      {'total': 100,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 100,
       'normal_rate': 1.0}),
     ((7.0,),
      {'total': 100,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 100,
       'normal_rate': 1.0}),
     ((6.0,),
      {'total': 100,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 100,
       'normal_rate': 1.0}),
     ((5.0,),
      {'total': 100,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 100,
       'normal_rate': 1.0}),
     ((4.0,),
      {'total': 100,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 100,
       'normal_rate': 1.0}),
     ((3.0,),
      {'total': 100,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 100,
       'normal_rate': 1.0}),
     ((2.0,),
      {'total': 100,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 100,
       'normal_rate': 1.0}),
     ((1.0,),
      {'total': 100,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 100,
       'normal_rate': 1.0}),
     ((0.0,),
      {'total': 100,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 100,
       'normal_rate': 1.0})]



And one for your width/offset settings:


**In [13]:**

.. code:: ipython3

    results = gc.calc(ignore_params=["ext_offset"], sort="success_rate")
    results


**Out [13]:**



.. parsed-literal::

    [((9.4, 49),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((9.4, 48),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((9.4, 47),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((9.4, 46),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((9.4, 45),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((9.4, 44),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((9.4, 43),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((9.4, 42),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((9.4, 41),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((9.4, 40),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((8.4, 49),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((8.4, 48),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((8.4, 47),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((8.4, 46),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((8.4, 45),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((8.4, 44),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((8.4, 43),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((8.4, 42),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((8.4, 41),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((8.4, 40),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((7.4, 49),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((7.4, 48),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((7.4, 47),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((7.4, 46),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((7.4, 45),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((7.4, 44),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((7.4, 43),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((7.4, 42),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((7.4, 41),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((7.4, 40),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((6.4, 49),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((6.4, 48),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((6.4, 47),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((6.4, 46),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((6.4, 45),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((6.4, 44),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((6.4, 43),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((6.4, 42),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((6.4, 41),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((6.4, 40),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((5.4, 49),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((5.4, 48),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((5.4, 47),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((5.4, 46),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((5.4, 45),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((5.4, 44),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((5.4, 43),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((5.4, 42),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((5.4, 41),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((5.4, 40),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((4.4, 49),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((4.4, 48),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((4.4, 47),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((4.4, 46),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((4.4, 45),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((4.4, 44),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((4.4, 43),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((4.4, 42),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((4.4, 41),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((4.4, 40),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((3.4, 49),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((3.4, 48),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((3.4, 47),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((3.4, 46),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((3.4, 45),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((3.4, 44),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((3.4, 43),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((3.4, 42),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((3.4, 41),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((3.4, 40),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((2.4, 49),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((2.4, 48),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((2.4, 47),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((2.4, 46),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((2.4, 45),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((2.4, 44),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((2.4, 43),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((2.4, 42),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((2.4, 41),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((2.4, 40),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((1.4, 49),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((1.4, 48),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((1.4, 47),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((1.4, 46),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((1.4, 45),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((1.4, 44),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((1.4, 43),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((1.4, 42),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((1.4, 41),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((1.4, 40),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((0.4, 49),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((0.4, 48),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((0.4, 47),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((0.4, 46),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((0.4, 45),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((0.4, 44),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((0.4, 43),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((0.4, 42),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((0.4, 41),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0}),
     ((0.4, 40),
      {'total': 11,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 11,
       'normal_rate': 1.0})]




**In [14]:**

.. code:: ipython3

    scope.dis()
    target.dis()


**In [15]:**

.. code:: ipython3

    assert broken is True


**Out [15]:**

::


    ---------------------------------------------------------------------------

    AssertionError                            Traceback (most recent call last)

    Cell In[15], line 1
    ----> 1 assert broken is True


    AssertionError: 

