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
    PLATFORM = 'CWLITEARM'
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
    scope.adc.samples                        changed from 24400                     to 5000                     
    scope.adc.trig\_count                     changed from 11059381                  to 21937451                 
    scope.clock.adc\_src                      changed from clkgen\_x1                 to clkgen\_x4                
    scope.clock.adc\_freq                     changed from 23382854                  to 96000000                 
    scope.clock.adc\_rate                     changed from 23382854.0                to 96000000.0               
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
    .
    Compiling:
    Compiling:
    -en     .././hal/stm32f3/stm32f3\_hal.c ...
    -en     .././hal/stm32f3/stm32f3\_hal\_lowlevel.c ...
    .
    .
    Compiling:
    Assembling: .././hal/stm32f3/stm32f3\_startup.S
    -en     .././hal/stm32f3/stm32f3\_sysmem.c ...
    -e Done!
    -e Done!
    arm-none-eabi-gcc -c -mcpu=cortex-m4 -I. -x assembler-with-cpp -mthumb -mfloat-abi=soft -fmessage-length=0 -ffunction-sections -DF\_CPU=7372800 -Wa,-gstabs,-adhlns=objdir-CWLITEARM/stm32f3\_startup.lst -I.././simpleserial/ -I.././hal -I.././hal/stm32f3 -I.././hal/stm32f3/CMSIS -I.././hal/stm32f3/CMSIS/core -I.././hal/stm32f3/CMSIS/device -I.././hal/stm32f4/Legacy -I.././simpleserial/ -I.././crypto/ .././hal/stm32f3/stm32f3\_startup.S -o objdir-CWLITEARM/stm32f3\_startup.o
    -e Done!
    -e Done!
    -e Done!
    .
    LINKING:
    -en     simpleserial-glitch-CWLITEARM.elf ...
    -e Done!
    .
    .
    Creating load file for Flash: simpleserial-glitch-CWLITEARM.hex
    Creating load file for Flash: simpleserial-glitch-CWLITEARM.bin
    .
    arm-none-eabi-objcopy -O ihex -R .eeprom -R .fuse -R .lock -R .signature simpleserial-glitch-CWLITEARM.elf simpleserial-glitch-CWLITEARM.hex
    arm-none-eabi-objcopy -O binary -R .eeprom -R .fuse -R .lock -R .signature simpleserial-glitch-CWLITEARM.elf simpleserial-glitch-CWLITEARM.bin
    Creating load file for EEPROM: simpleserial-glitch-CWLITEARM.eep
    .
    arm-none-eabi-objcopy -j .eeprom --set-section-flags=.eeprom="alloc,load" \
    --change-section-lma .eeprom=0 --no-change-warnings -O ihex simpleserial-glitch-CWLITEARM.elf simpleserial-glitch-CWLITEARM.eep \|\| exit 0
    Creating Extended Listing: simpleserial-glitch-CWLITEARM.lss
    .
    Creating Symbol Table: simpleserial-glitch-CWLITEARM.sym
    arm-none-eabi-nm -n simpleserial-glitch-CWLITEARM.elf > simpleserial-glitch-CWLITEARM.sym
    arm-none-eabi-objdump -h -S -z simpleserial-glitch-CWLITEARM.elf > simpleserial-glitch-CWLITEARM.lss
    SS\_VER set to SS\_VER\_2\_1
    SS\_VER set to SS\_VER\_2\_1
    Size after:
    +--------------------------------------------------------
    +--------------------------------------------------------
       text	   data	    bss	    dec	    hex	filename
       5524	      8	   1368	   6900	   1af4	simpleserial-glitch-CWLITEARM.elf
    + Built for platform CW-Lite Arm \(STM32F3\) with:
    + CRYPTO\_TARGET = NONE
    + CRYPTO\_OPTIONS = 
    +--------------------------------------------------------
    + Default target does full rebuild each time.
    + Specify buildtarget == allquick == to avoid full rebuild
    +--------------------------------------------------------




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
    Attempting to program 5531 bytes at 0x8000000
    STM32F Programming flash...
    STM32F Reading flash...
    Verified flash OK, 5531 bytes




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

    scope.clock.adc\_freq                     changed from 96000000                  to 31023262                 
    scope.clock.adc\_rate                     changed from 96000000.0                to 31023262.0               



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
      <div class="bk-root" id="89034396-5844-4c23-954d-70ba93432cfa" data-root-id="1002"></div>
    </div>
    <script type="application/javascript">(function(root) {
      function embed_document(root) {
        var docs_json = {"b99e72ee-7590-4a69-9fb2-6abf0b18bdf6":{"defs":[{"extends":null,"module":null,"name":"ReactiveHTML1","overrides":[],"properties":[]},{"extends":null,"module":null,"name":"FlexBox1","overrides":[],"properties":[{"default":"flex-start","kind":null,"name":"align_content"},{"default":"flex-start","kind":null,"name":"align_items"},{"default":"row","kind":null,"name":"flex_direction"},{"default":"wrap","kind":null,"name":"flex_wrap"},{"default":"flex-start","kind":null,"name":"justify_content"}]},{"extends":null,"module":null,"name":"GridStack1","overrides":[],"properties":[{"default":"warn","kind":null,"name":"mode"},{"default":null,"kind":null,"name":"ncols"},{"default":null,"kind":null,"name":"nrows"},{"default":true,"kind":null,"name":"allow_resize"},{"default":true,"kind":null,"name":"allow_drag"},{"default":[],"kind":null,"name":"state"}]},{"extends":null,"module":null,"name":"click1","overrides":[],"properties":[{"default":"","kind":null,"name":"terminal_output"},{"default":"","kind":null,"name":"debug_name"},{"default":0,"kind":null,"name":"clears"}]},{"extends":null,"module":null,"name":"NotificationAreaBase1","overrides":[],"properties":[{"default":"bottom-right","kind":null,"name":"position"},{"default":0,"kind":null,"name":"_clear"}]},{"extends":null,"module":null,"name":"NotificationArea1","overrides":[],"properties":[{"default":[],"kind":null,"name":"notifications"},{"default":"bottom-right","kind":null,"name":"position"},{"default":0,"kind":null,"name":"_clear"},{"default":[{"background":"#ffc107","icon":{"className":"fas fa-exclamation-triangle","color":"white","tagName":"i"},"type":"warning"},{"background":"#007bff","icon":{"className":"fas fa-info-circle","color":"white","tagName":"i"},"type":"info"}],"kind":null,"name":"types"}]},{"extends":null,"module":null,"name":"Notification","overrides":[],"properties":[{"default":null,"kind":null,"name":"background"},{"default":3000,"kind":null,"name":"duration"},{"default":null,"kind":null,"name":"icon"},{"default":"","kind":null,"name":"message"},{"default":null,"kind":null,"name":"notification_type"},{"default":false,"kind":null,"name":"_destroyed"}]},{"extends":null,"module":null,"name":"TemplateActions1","overrides":[],"properties":[{"default":0,"kind":null,"name":"open_modal"},{"default":0,"kind":null,"name":"close_modal"}]},{"extends":null,"module":null,"name":"MaterialTemplateActions1","overrides":[],"properties":[{"default":0,"kind":null,"name":"open_modal"},{"default":0,"kind":null,"name":"close_modal"}]}],"roots":{"references":[{"attributes":{},"id":"1023","type":"BasicTicker"},{"attributes":{},"id":"1028","type":"WheelZoomTool"},{"attributes":{},"id":"1046","type":"Selection"},{"attributes":{},"id":"1027","type":"PanTool"},{"attributes":{},"id":"1026","type":"SaveTool"},{"attributes":{"source":{"id":"1045"}},"id":"1052","type":"CDSView"},{"attributes":{},"id":"1076","type":"UnionRenderers"},{"attributes":{"angle":{"value":0.7853981633974483},"fill_alpha":{"value":0.1},"fill_color":{"value":"#ff0000"},"hatch_alpha":{"value":0.1},"hatch_color":{"value":"#ff0000"},"line_alpha":{"value":0.1},"line_color":{"value":"#ff0000"},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"ext_offset"},"y":{"field":"offset"}},"id":"1058","type":"Scatter"},{"attributes":{"overlay":{"id":"1031"}},"id":"1029","type":"BoxZoomTool"},{"attributes":{"tags":[[["ext_offset","ext_offset",null]],[]]},"id":"1003","type":"Range1d"},{"attributes":{},"id":"1030","type":"ResetTool"},{"attributes":{"tags":[[["offset","offset",null]],{"autorange":false,"invert_yaxis":false}]},"id":"1004","type":"Range1d"},{"attributes":{"bottom_units":"screen","coordinates":null,"fill_alpha":0.5,"fill_color":"lightgrey","group":null,"left_units":"screen","level":"overlay","line_alpha":1.0,"line_color":"black","line_dash":[4,4],"line_width":2,"right_units":"screen","syncable":false,"top_units":"screen"},"id":"1031","type":"BoxAnnotation"},{"attributes":{"source":{"id":"1054"}},"id":"1061","type":"CDSView"},{"attributes":{"active_drag":{"id":"1027"},"active_scroll":{"id":"1028"},"tools":[{"id":"1007"},{"id":"1026"},{"id":"1027"},{"id":"1028"},{"id":"1029"},{"id":"1030"}]},"id":"1032","type":"Toolbar"},{"attributes":{"data":{"ext_offset":{"__ndarray__":"","dtype":"float64","order":"little","shape":[0]},"offset":{"__ndarray__":"","dtype":"float64","order":"little","shape":[0]}},"selected":{"id":"1055"},"selection_policy":{"id":"1076"}},"id":"1054","type":"ColumnDataSource"},{"attributes":{"angle":{"value":0.7853981633974483},"fill_alpha":{"value":1.0},"fill_color":{"value":"#ff0000"},"hatch_alpha":{"value":1.0},"hatch_color":{"value":"#ff0000"},"hatch_scale":{"value":12.0},"hatch_weight":{"value":1.0},"line_alpha":{"value":1.0},"line_cap":{"value":"butt"},"line_color":{"value":"#ff0000"},"line_dash":{"value":[]},"line_dash_offset":{"value":0},"line_join":{"value":"bevel"},"line_width":{"value":1},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"ext_offset"},"y":{"field":"offset"}},"id":"1062","type":"Scatter"},{"attributes":{},"id":"1041","type":"AllLabels"},{"attributes":{"angle":{"value":0.7853981633974483},"fill_color":{"value":"#ff0000"},"hatch_color":{"value":"#ff0000"},"line_color":{"value":"#ff0000"},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"ext_offset"},"y":{"field":"offset"}},"id":"1057","type":"Scatter"},{"attributes":{"coordinates":null,"group":null,"text_color":"black","text_font_size":"12pt"},"id":"1010","type":"Title"},{"attributes":{},"id":"1044","type":"AllLabels"},{"attributes":{"callback":null,"renderers":[{"id":"1051"},{"id":"1060"}],"tags":["hv_created"],"tooltips":[["ext_offset","@{ext_offset}"],["offset","@{offset}"]]},"id":"1007","type":"HoverTool"},{"attributes":{},"id":"1040","type":"BasicTickFormatter"},{"attributes":{"fill_alpha":{"value":0.1},"fill_color":{"value":"#007f00"},"hatch_alpha":{"value":0.1},"hatch_color":{"value":"#007f00"},"line_alpha":{"value":0.1},"line_color":{"value":"#007f00"},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"ext_offset"},"y":{"field":"offset"}},"id":"1049","type":"Scatter"},{"attributes":{},"id":"1043","type":"BasicTickFormatter"},{"attributes":{},"id":"1055","type":"Selection"},{"attributes":{"angle":{"value":0.7853981633974483},"fill_alpha":{"value":0.2},"fill_color":{"value":"#ff0000"},"hatch_alpha":{"value":0.2},"hatch_color":{"value":"#ff0000"},"line_alpha":{"value":0.2},"line_color":{"value":"#ff0000"},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"ext_offset"},"y":{"field":"offset"}},"id":"1059","type":"Scatter"},{"attributes":{"data":{"ext_offset":{"__ndarray__":"","dtype":"float64","order":"little","shape":[0]},"offset":{"__ndarray__":"","dtype":"float64","order":"little","shape":[0]}},"selected":{"id":"1046"},"selection_policy":{"id":"1074"}},"id":"1045","type":"ColumnDataSource"},{"attributes":{"coordinates":null,"data_source":{"id":"1054"},"glyph":{"id":"1057"},"group":null,"hover_glyph":null,"muted_glyph":{"id":"1059"},"nonselection_glyph":{"id":"1058"},"selection_glyph":{"id":"1062"},"view":{"id":"1061"}},"id":"1060","type":"GlyphRenderer"},{"attributes":{"client_comm_id":"50a7fc87e5e64a13833ad9dcb4309152","comm_id":"763f476a5861471caec7d1c25a1f2ef9","plot_id":"1002"},"id":"1115","type":"panel.models.comm_manager.CommManager"},{"attributes":{"axis_label":"ext_offset","coordinates":null,"formatter":{"id":"1040"},"group":null,"major_label_policy":{"id":"1041"},"ticker":{"id":"1019"}},"id":"1018","type":"LinearAxis"},{"attributes":{"children":[{"id":"1009"}],"height":600,"margin":[0,0,0,0],"name":"Row00811","sizing_mode":"fixed","width":800},"id":"1002","type":"Row"},{"attributes":{},"id":"1019","type":"BasicTicker"},{"attributes":{"fill_color":{"value":"#007f00"},"hatch_color":{"value":"#007f00"},"line_color":{"value":"#007f00"},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"ext_offset"},"y":{"field":"offset"}},"id":"1048","type":"Scatter"},{"attributes":{"below":[{"id":"1018"}],"center":[{"id":"1021"},{"id":"1025"}],"left":[{"id":"1022"}],"margin":[5,5,5,5],"min_border_bottom":10,"min_border_left":10,"min_border_right":10,"min_border_top":10,"output_backend":"webgl","renderers":[{"id":"1051"},{"id":"1060"}],"sizing_mode":"fixed","title":{"id":"1010"},"toolbar":{"id":"1032"},"width":800,"x_range":{"id":"1003"},"x_scale":{"id":"1016"},"y_range":{"id":"1004"},"y_scale":{"id":"1017"}},"id":"1009","subtype":"Figure","type":"Plot"},{"attributes":{"coordinates":null,"data_source":{"id":"1045"},"glyph":{"id":"1048"},"group":null,"hover_glyph":null,"muted_glyph":{"id":"1050"},"nonselection_glyph":{"id":"1049"},"selection_glyph":{"id":"1053"},"view":{"id":"1052"}},"id":"1051","type":"GlyphRenderer"},{"attributes":{},"id":"1016","type":"LinearScale"},{"attributes":{},"id":"1017","type":"LinearScale"},{"attributes":{"axis":{"id":"1018"},"coordinates":null,"grid_line_color":null,"group":null,"ticker":null},"id":"1021","type":"Grid"},{"attributes":{},"id":"1074","type":"UnionRenderers"},{"attributes":{"axis_label":"offset","coordinates":null,"formatter":{"id":"1043"},"group":null,"major_label_policy":{"id":"1044"},"ticker":{"id":"1023"}},"id":"1022","type":"LinearAxis"},{"attributes":{"angle":{"value":0.0},"fill_alpha":{"value":1.0},"fill_color":{"value":"#007f00"},"hatch_alpha":{"value":1.0},"hatch_color":{"value":"#007f00"},"hatch_scale":{"value":12.0},"hatch_weight":{"value":1.0},"line_alpha":{"value":1.0},"line_cap":{"value":"butt"},"line_color":{"value":"#007f00"},"line_dash":{"value":[]},"line_dash_offset":{"value":0},"line_join":{"value":"bevel"},"line_width":{"value":1},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"ext_offset"},"y":{"field":"offset"}},"id":"1053","type":"Scatter"},{"attributes":{"axis":{"id":"1022"},"coordinates":null,"dimension":1,"grid_line_color":null,"group":null,"ticker":null},"id":"1025","type":"Grid"},{"attributes":{"fill_alpha":{"value":0.2},"fill_color":{"value":"#007f00"},"hatch_alpha":{"value":0.2},"hatch_color":{"value":"#007f00"},"line_alpha":{"value":0.2},"line_color":{"value":"#007f00"},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"ext_offset"},"y":{"field":"offset"}},"id":"1050","type":"Scatter"}],"root_ids":["1002","1115"]},"title":"Bokeh Application","version":"2.4.3"}};
        var render_items = [{"docid":"b99e72ee-7590-4a69-9fb2-6abf0b18bdf6","root_ids":["1002"],"roots":{"1002":"89034396-5844-4c23-954d-70ba93432cfa"}}];
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


**Out [11]:**



.. parsed-literal::

    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 4, 1
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 101





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:502) Read timed out: 
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:502) Read timed out: 
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 4, 1





.. parsed-literal::

    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 255





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 255, 1
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08
    WARNING:root:SAM3U Serial buffers OVERRUN - data loss has occurred.





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:502) Read timed out: 
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 0, 1





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:184) Infinite loop in unstuff data
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:185) CWbytearray(b'00 a0 00 20 25 15')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 160
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 0, 1





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a
    WARNING:root:SAM3U Serial buffers OVERRUN - data loss has occurred.





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:417) Invalid CRC. Expected 153 got 8





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:417) Invalid CRC. Expected 153 got 0





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:502) Read timed out: 
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack





.. parsed-literal::

    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 0, 1
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 114





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 0
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 0
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:417) Invalid CRC. Expected 248 got 114
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    CWbytearray(b'01')
    1.5625 -2.734375 7
    🐙Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    CWbytearray(b'01')
    1.5625 -2.734375 17
    🐙Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    CWbytearray(b'01')
    1.5625 -2.734375 37
    🐙Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    CWbytearray(b'01')
    1.5625 -2.734375 48
    🐙Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:502) Read timed out: 
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:502) Read timed out: 
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 146
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 0, 1
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:184) Infinite loop in unstuff data
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:185) CWbytearray(b'00 a0 00 20 25 15')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 160
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 0, 1
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    WARNING:root:SAM3U Serial buffers OVERRUN - data loss has occurred.
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
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
    1.5625 -2.34375 44
    🐙Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    CWbytearray(b'01')
    1.5625 -2.34375 48
    🐙Trigger still high!





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:502) Read timed out: 
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:502) Read timed out: 
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 0
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 0, 1
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger
    Trigger still high!
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 101
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:502) Read timed out: 
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack





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





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 101
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:502) Read timed out: 
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:417) Invalid CRC. Expected 153 got 248





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





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 4, 1
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 255
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 255, 1
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    WARNING:root:SAM3U Serial buffers OVERRUN - data loss has occurred.
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 183
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 0, 1
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:417) Invalid CRC. Expected 153 got 51
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:417) Invalid CRC. Expected 153 got 0
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 114
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 183
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 0, 1
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:417) Invalid CRC. Expected 153 got 205
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
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
    1.953125 -2.734375 37
    🐙Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    CWbytearray(b'01')
    1.953125 -2.734375 48
    🐙Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 0, 1
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:502) Read timed out: 
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:502) Read timed out: 
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 0
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 0, 1
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:184) Infinite loop in unstuff data
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:185) CWbytearray(b'00 a0 00 20 25 15')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 160
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 0, 1
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    WARNING:root:SAM3U Serial buffers OVERRUN - data loss has occurred.
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:417) Invalid CRC. Expected 153 got 0
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:417) Invalid CRC. Expected 153 got 0
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
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
    2.34375 -3.90625 46
    🐙Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 101
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:502) Read timed out: 
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:417) Invalid CRC. Expected 153 got 158
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:502) Read timed out: 
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 4, 1
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 183
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:417) Invalid CRC. Expected 153 got 51
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:417) Invalid CRC. Expected 153 got 0
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
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
    2.34375 -3.125 48
    🐙Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 114
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 183
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 0, 1
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:417) Invalid CRC. Expected 153 got 205
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:417) Invalid CRC. Expected 153 got 0
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 101
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:502) Read timed out: 
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:417) Invalid CRC. Expected 153 got 248





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





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 183





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:184) Infinite loop in unstuff data
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:185) CWbytearray(b'00 a0 00 20 25 15')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 160
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 0, 1
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    WARNING:root:SAM3U Serial buffers OVERRUN - data loss has occurred.
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:417) Invalid CRC. Expected 153 got 0
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:417) Invalid CRC. Expected 153 got 95
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 101
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:502) Read timed out: 
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:417) Invalid CRC. Expected 153 got 158
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger
    Trigger still high!
    Trigger still high!
    CWbytearray(b'01')
    3.125 -1.953125 7
    🐙Trigger still high!
    Trigger still high!
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
    3.125 -1.953125 44
    🐙Trigger still high!
    CWbytearray(b'01')
    3.125 -1.953125 48
    🐙Trigger still high!
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 101
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:502) Read timed out: 
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack





.. parsed-literal::

    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:502) Read timed out: 
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:184) Infinite loop in unstuff data
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:185) CWbytearray(b'00 a0 00 20 25 15')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 160
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 0, 1
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    WARNING:root:SAM3U Serial buffers OVERRUN - data loss has occurred.
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger
    CWbytearray(b'01')
    3.515625 -2.34375 4
    🐙Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 0
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:288) Device reported error 0xd
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:290) CWbytearray(b'00 00 40 0d 00 00 00 00 00 00 00 00 00 00 00 20 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 d0 00 62 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 c7 00')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:417) Invalid CRC. Expected 153 got 116
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 0, 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 183
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 0, 1
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:417) Invalid CRC. Expected 153 got 8
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:417) Invalid CRC. Expected 153 got 0
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:417) Invalid CRC. Expected 153 got 0





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





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:502) Read timed out: 
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack





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





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:502) Read timed out: 
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 183
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 0, 1
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:417) Invalid CRC. Expected 153 got 8
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:417) Invalid CRC. Expected 153 got 0
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:417) Invalid CRC. Expected 153 got 0



For this lab, you may want two copies of your results; one for finding
effective ext_offsets:


**In [12]:**

.. code:: ipython3

    results = gc.calc(ignore_params=["width", "offset"], sort="success_rate")
    results


**Out [12]:**



.. parsed-literal::

    [((48,),
      {'total': 56,
       'success': 5,
       'success_rate': 0.08928571428571429,
       'reset': 20,
       'reset_rate': 0.35714285714285715,
       'normal': 31,
       'normal_rate': 0.5535714285714286}),
     ((44,),
      {'total': 49,
       'success': 2,
       'success_rate': 0.04081632653061224,
       'reset': 8,
       'reset_rate': 0.16326530612244897,
       'normal': 39,
       'normal_rate': 0.7959183673469388}),
     ((7,),
      {'total': 60,
       'success': 2,
       'success_rate': 0.03333333333333333,
       'reset': 27,
       'reset_rate': 0.45,
       'normal': 31,
       'normal_rate': 0.5166666666666667}),
     ((37,),
      {'total': 61,
       'success': 2,
       'success_rate': 0.03278688524590164,
       'reset': 29,
       'reset_rate': 0.47540983606557374,
       'normal': 30,
       'normal_rate': 0.4918032786885246}),
     ((4,),
      {'total': 49,
       'success': 1,
       'success_rate': 0.02040816326530612,
       'reset': 8,
       'reset_rate': 0.16326530612244897,
       'normal': 40,
       'normal_rate': 0.8163265306122449}),
     ((17,),
      {'total': 61,
       'success': 1,
       'success_rate': 0.01639344262295082,
       'reset': 29,
       'reset_rate': 0.47540983606557374,
       'normal': 31,
       'normal_rate': 0.5081967213114754}),
     ((46,),
      {'total': 63,
       'success': 1,
       'success_rate': 0.015873015873015872,
       'reset': 27,
       'reset_rate': 0.42857142857142855,
       'normal': 35,
       'normal_rate': 0.5555555555555556}),
     ((100,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 16,
       'reset_rate': 0.3333333333333333,
       'normal': 32,
       'normal_rate': 0.6666666666666666}),
     ((99,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 11,
       'reset_rate': 0.22916666666666666,
       'normal': 37,
       'normal_rate': 0.7708333333333334}),
     ((98,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 16,
       'reset_rate': 0.3333333333333333,
       'normal': 32,
       'normal_rate': 0.6666666666666666}),
     ((97,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 8,
       'reset_rate': 0.16666666666666666,
       'normal': 40,
       'normal_rate': 0.8333333333333334}),
     ((96,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 17,
       'reset_rate': 0.3541666666666667,
       'normal': 31,
       'normal_rate': 0.6458333333333334}),
     ((95,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 17,
       'reset_rate': 0.3541666666666667,
       'normal': 31,
       'normal_rate': 0.6458333333333334}),
     ((94,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 17,
       'reset_rate': 0.3541666666666667,
       'normal': 31,
       'normal_rate': 0.6458333333333334}),
     ((93,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 17,
       'reset_rate': 0.3541666666666667,
       'normal': 31,
       'normal_rate': 0.6458333333333334}),
     ((92,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 8,
       'reset_rate': 0.16666666666666666,
       'normal': 40,
       'normal_rate': 0.8333333333333334}),
     ((91,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 18,
       'reset_rate': 0.375,
       'normal': 30,
       'normal_rate': 0.625}),
     ((90,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 17,
       'reset_rate': 0.3541666666666667,
       'normal': 31,
       'normal_rate': 0.6458333333333334}),
     ((89,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 14,
       'reset_rate': 0.2916666666666667,
       'normal': 34,
       'normal_rate': 0.7083333333333334}),
     ((88,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 18,
       'reset_rate': 0.375,
       'normal': 30,
       'normal_rate': 0.625}),
     ((87,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 18,
       'reset_rate': 0.375,
       'normal': 30,
       'normal_rate': 0.625}),
     ((86,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 18,
       'reset_rate': 0.375,
       'normal': 30,
       'normal_rate': 0.625}),
     ((85,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 15,
       'reset_rate': 0.3125,
       'normal': 33,
       'normal_rate': 0.6875}),
     ((84,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 4,
       'reset_rate': 0.08333333333333333,
       'normal': 44,
       'normal_rate': 0.9166666666666666}),
     ((83,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 13,
       'reset_rate': 0.2708333333333333,
       'normal': 35,
       'normal_rate': 0.7291666666666666}),
     ((82,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 18,
       'reset_rate': 0.375,
       'normal': 30,
       'normal_rate': 0.625}),
     ((81,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 18,
       'reset_rate': 0.375,
       'normal': 30,
       'normal_rate': 0.625}),
     ((80,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 18,
       'reset_rate': 0.375,
       'normal': 30,
       'normal_rate': 0.625}),
     ((79,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 8,
       'reset_rate': 0.16666666666666666,
       'normal': 40,
       'normal_rate': 0.8333333333333334}),
     ((78,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 3,
       'reset_rate': 0.0625,
       'normal': 45,
       'normal_rate': 0.9375}),
     ((77,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 10,
       'reset_rate': 0.20833333333333334,
       'normal': 38,
       'normal_rate': 0.7916666666666666}),
     ((76,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 16,
       'reset_rate': 0.3333333333333333,
       'normal': 32,
       'normal_rate': 0.6666666666666666}),
     ((75,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 16,
       'reset_rate': 0.3333333333333333,
       'normal': 32,
       'normal_rate': 0.6666666666666666}),
     ((74,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 11,
       'reset_rate': 0.22916666666666666,
       'normal': 37,
       'normal_rate': 0.7708333333333334}),
     ((73,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 11,
       'reset_rate': 0.22916666666666666,
       'normal': 37,
       'normal_rate': 0.7708333333333334}),
     ((72,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 12,
       'reset_rate': 0.25,
       'normal': 36,
       'normal_rate': 0.75}),
     ((71,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 5,
       'reset_rate': 0.10416666666666667,
       'normal': 43,
       'normal_rate': 0.8958333333333334}),
     ((70,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 2,
       'reset_rate': 0.041666666666666664,
       'normal': 46,
       'normal_rate': 0.9583333333333334}),
     ((69,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 8,
       'reset_rate': 0.16666666666666666,
       'normal': 40,
       'normal_rate': 0.8333333333333334}),
     ((68,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 18,
       'reset_rate': 0.375,
       'normal': 30,
       'normal_rate': 0.625}),
     ((67,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 17,
       'reset_rate': 0.3541666666666667,
       'normal': 31,
       'normal_rate': 0.6458333333333334}),
     ((66,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 16,
       'reset_rate': 0.3333333333333333,
       'normal': 32,
       'normal_rate': 0.6666666666666666}),
     ((65,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 17,
       'reset_rate': 0.3541666666666667,
       'normal': 31,
       'normal_rate': 0.6458333333333334}),
     ((64,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 1,
       'reset_rate': 0.020833333333333332,
       'normal': 47,
       'normal_rate': 0.9791666666666666}),
     ((63,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 5,
       'reset_rate': 0.10416666666666667,
       'normal': 43,
       'normal_rate': 0.8958333333333334}),
     ((62,),
      {'total': 51,
       'success': 0,
       'success_rate': 0.0,
       'reset': 17,
       'reset_rate': 0.3333333333333333,
       'normal': 34,
       'normal_rate': 0.6666666666666666}),
     ((61,),
      {'total': 56,
       'success': 0,
       'success_rate': 0.0,
       'reset': 24,
       'reset_rate': 0.42857142857142855,
       'normal': 32,
       'normal_rate': 0.5714285714285714}),
     ((60,),
      {'total': 52,
       'success': 0,
       'success_rate': 0.0,
       'reset': 17,
       'reset_rate': 0.3269230769230769,
       'normal': 35,
       'normal_rate': 0.6730769230769231}),
     ((59,),
      {'total': 58,
       'success': 0,
       'success_rate': 0.0,
       'reset': 15,
       'reset_rate': 0.25862068965517243,
       'normal': 43,
       'normal_rate': 0.7413793103448276}),
     ((58,),
      {'total': 49,
       'success': 0,
       'success_rate': 0.0,
       'reset': 12,
       'reset_rate': 0.24489795918367346,
       'normal': 37,
       'normal_rate': 0.7551020408163265}),
     ((57,),
      {'total': 65,
       'success': 0,
       'success_rate': 0.0,
       'reset': 17,
       'reset_rate': 0.26153846153846155,
       'normal': 48,
       'normal_rate': 0.7384615384615385}),
     ((56,),
      {'total': 66,
       'success': 0,
       'success_rate': 0.0,
       'reset': 35,
       'reset_rate': 0.5303030303030303,
       'normal': 31,
       'normal_rate': 0.4696969696969697}),
     ((55,),
      {'total': 53,
       'success': 0,
       'success_rate': 0.0,
       'reset': 20,
       'reset_rate': 0.37735849056603776,
       'normal': 33,
       'normal_rate': 0.6226415094339622}),
     ((54,),
      {'total': 63,
       'success': 0,
       'success_rate': 0.0,
       'reset': 20,
       'reset_rate': 0.31746031746031744,
       'normal': 43,
       'normal_rate': 0.6825396825396826}),
     ((53,),
      {'total': 55,
       'success': 0,
       'success_rate': 0.0,
       'reset': 22,
       'reset_rate': 0.4,
       'normal': 33,
       'normal_rate': 0.6}),
     ((52,),
      {'total': 65,
       'success': 0,
       'success_rate': 0.0,
       'reset': 23,
       'reset_rate': 0.35384615384615387,
       'normal': 42,
       'normal_rate': 0.6461538461538462}),
     ((51,),
      {'total': 64,
       'success': 0,
       'success_rate': 0.0,
       'reset': 33,
       'reset_rate': 0.515625,
       'normal': 31,
       'normal_rate': 0.484375}),
     ((50,),
      {'total': 60,
       'success': 0,
       'success_rate': 0.0,
       'reset': 29,
       'reset_rate': 0.48333333333333334,
       'normal': 31,
       'normal_rate': 0.5166666666666667}),
     ((49,),
      {'total': 58,
       'success': 0,
       'success_rate': 0.0,
       'reset': 22,
       'reset_rate': 0.3793103448275862,
       'normal': 36,
       'normal_rate': 0.6206896551724138}),
     ((47,),
      {'total': 60,
       'success': 0,
       'success_rate': 0.0,
       'reset': 22,
       'reset_rate': 0.36666666666666664,
       'normal': 38,
       'normal_rate': 0.6333333333333333}),
     ((45,),
      {'total': 56,
       'success': 0,
       'success_rate': 0.0,
       'reset': 23,
       'reset_rate': 0.4107142857142857,
       'normal': 33,
       'normal_rate': 0.5892857142857143}),
     ((43,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 1,
       'reset_rate': 0.020833333333333332,
       'normal': 47,
       'normal_rate': 0.9791666666666666}),
     ((42,),
      {'total': 50,
       'success': 0,
       'success_rate': 0.0,
       'reset': 2,
       'reset_rate': 0.04,
       'normal': 48,
       'normal_rate': 0.96}),
     ((41,),
      {'total': 49,
       'success': 0,
       'success_rate': 0.0,
       'reset': 2,
       'reset_rate': 0.04081632653061224,
       'normal': 47,
       'normal_rate': 0.9591836734693877}),
     ((40,),
      {'total': 58,
       'success': 0,
       'success_rate': 0.0,
       'reset': 11,
       'reset_rate': 0.1896551724137931,
       'normal': 47,
       'normal_rate': 0.8103448275862069}),
     ((39,),
      {'total': 62,
       'success': 0,
       'success_rate': 0.0,
       'reset': 24,
       'reset_rate': 0.3870967741935484,
       'normal': 38,
       'normal_rate': 0.6129032258064516}),
     ((38,),
      {'total': 64,
       'success': 0,
       'success_rate': 0.0,
       'reset': 30,
       'reset_rate': 0.46875,
       'normal': 34,
       'normal_rate': 0.53125}),
     ((36,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 13,
       'reset_rate': 0.2708333333333333,
       'normal': 35,
       'normal_rate': 0.7291666666666666}),
     ((35,),
      {'total': 55,
       'success': 0,
       'success_rate': 0.0,
       'reset': 7,
       'reset_rate': 0.12727272727272726,
       'normal': 48,
       'normal_rate': 0.8727272727272727}),
     ((34,),
      {'total': 49,
       'success': 0,
       'success_rate': 0.0,
       'reset': 8,
       'reset_rate': 0.16326530612244897,
       'normal': 41,
       'normal_rate': 0.8367346938775511}),
     ((33,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 1,
       'reset_rate': 0.020833333333333332,
       'normal': 47,
       'normal_rate': 0.9791666666666666}),
     ((32,),
      {'total': 52,
       'success': 0,
       'success_rate': 0.0,
       'reset': 4,
       'reset_rate': 0.07692307692307693,
       'normal': 48,
       'normal_rate': 0.9230769230769231}),
     ((31,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 4,
       'reset_rate': 0.08333333333333333,
       'normal': 44,
       'normal_rate': 0.9166666666666666}),
     ((30,),
      {'total': 57,
       'success': 0,
       'success_rate': 0.0,
       'reset': 9,
       'reset_rate': 0.15789473684210525,
       'normal': 48,
       'normal_rate': 0.8421052631578947}),
     ((29,),
      {'total': 61,
       'success': 0,
       'success_rate': 0.0,
       'reset': 22,
       'reset_rate': 0.36065573770491804,
       'normal': 39,
       'normal_rate': 0.639344262295082}),
     ((28,),
      {'total': 64,
       'success': 0,
       'success_rate': 0.0,
       'reset': 29,
       'reset_rate': 0.453125,
       'normal': 35,
       'normal_rate': 0.546875}),
     ((27,),
      {'total': 60,
       'success': 0,
       'success_rate': 0.0,
       'reset': 28,
       'reset_rate': 0.4666666666666667,
       'normal': 32,
       'normal_rate': 0.5333333333333333}),
     ((26,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 12,
       'reset_rate': 0.25,
       'normal': 36,
       'normal_rate': 0.75}),
     ((25,),
      {'total': 54,
       'success': 0,
       'success_rate': 0.0,
       'reset': 6,
       'reset_rate': 0.1111111111111111,
       'normal': 48,
       'normal_rate': 0.8888888888888888}),
     ((24,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 6,
       'reset_rate': 0.125,
       'normal': 42,
       'normal_rate': 0.875}),
     ((23,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 48,
       'normal_rate': 1.0}),
     ((22,),
      {'total': 51,
       'success': 0,
       'success_rate': 0.0,
       'reset': 3,
       'reset_rate': 0.058823529411764705,
       'normal': 48,
       'normal_rate': 0.9411764705882353}),
     ((21,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 3,
       'reset_rate': 0.0625,
       'normal': 45,
       'normal_rate': 0.9375}),
     ((20,),
      {'total': 57,
       'success': 0,
       'success_rate': 0.0,
       'reset': 9,
       'reset_rate': 0.15789473684210525,
       'normal': 48,
       'normal_rate': 0.8421052631578947}),
     ((19,),
      {'total': 64,
       'success': 0,
       'success_rate': 0.0,
       'reset': 25,
       'reset_rate': 0.390625,
       'normal': 39,
       'normal_rate': 0.609375}),
     ((18,),
      {'total': 64,
       'success': 0,
       'success_rate': 0.0,
       'reset': 32,
       'reset_rate': 0.5,
       'normal': 32,
       'normal_rate': 0.5}),
     ((16,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 13,
       'reset_rate': 0.2708333333333333,
       'normal': 35,
       'normal_rate': 0.7291666666666666}),
     ((15,),
      {'total': 55,
       'success': 0,
       'success_rate': 0.0,
       'reset': 7,
       'reset_rate': 0.12727272727272726,
       'normal': 48,
       'normal_rate': 0.8727272727272727}),
     ((14,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 7,
       'reset_rate': 0.14583333333333334,
       'normal': 41,
       'normal_rate': 0.8541666666666666}),
     ((13,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 48,
       'normal_rate': 1.0}),
     ((12,),
      {'total': 52,
       'success': 0,
       'success_rate': 0.0,
       'reset': 4,
       'reset_rate': 0.07692307692307693,
       'normal': 48,
       'normal_rate': 0.9230769230769231}),
     ((11,),
      {'total': 49,
       'success': 0,
       'success_rate': 0.0,
       'reset': 5,
       'reset_rate': 0.10204081632653061,
       'normal': 44,
       'normal_rate': 0.8979591836734694}),
     ((10,),
      {'total': 57,
       'success': 0,
       'success_rate': 0.0,
       'reset': 10,
       'reset_rate': 0.17543859649122806,
       'normal': 47,
       'normal_rate': 0.8245614035087719}),
     ((9,),
      {'total': 61,
       'success': 0,
       'success_rate': 0.0,
       'reset': 22,
       'reset_rate': 0.36065573770491804,
       'normal': 39,
       'normal_rate': 0.639344262295082}),
     ((8,),
      {'total': 62,
       'success': 0,
       'success_rate': 0.0,
       'reset': 27,
       'reset_rate': 0.43548387096774194,
       'normal': 35,
       'normal_rate': 0.5645161290322581}),
     ((6,),
      {'total': 49,
       'success': 0,
       'success_rate': 0.0,
       'reset': 14,
       'reset_rate': 0.2857142857142857,
       'normal': 35,
       'normal_rate': 0.7142857142857143}),
     ((5,),
      {'total': 55,
       'success': 0,
       'success_rate': 0.0,
       'reset': 8,
       'reset_rate': 0.14545454545454545,
       'normal': 47,
       'normal_rate': 0.8545454545454545}),
     ((3,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 1,
       'reset_rate': 0.020833333333333332,
       'normal': 47,
       'normal_rate': 0.9791666666666666}),
     ((2,),
      {'total': 53,
       'success': 0,
       'success_rate': 0.0,
       'reset': 5,
       'reset_rate': 0.09433962264150944,
       'normal': 48,
       'normal_rate': 0.9056603773584906}),
     ((1,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 5,
       'reset_rate': 0.10416666666666667,
       'normal': 43,
       'normal_rate': 0.8958333333333334}),
     ((0,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 13,
       'reset_rate': 0.2708333333333333,
       'normal': 35,
       'normal_rate': 0.7291666666666666})]



And one for your width/offset settings:


**In [13]:**

.. code:: ipython3

    results = gc.calc(ignore_params=["ext_offset"], sort="success_rate")
    results


**Out [13]:**



.. parsed-literal::

    [((1.6, -2.8000000000000003),
      {'total': 131,
       'success': 4,
       'success_rate': 0.030534351145038167,
       'reset': 95,
       'reset_rate': 0.7251908396946565,
       'normal': 32,
       'normal_rate': 0.24427480916030533}),
     ((3.1999999999999997, -2.0000000000000004),
      {'total': 123,
       'success': 3,
       'success_rate': 0.024390243902439025,
       'reset': 65,
       'reset_rate': 0.5284552845528455,
       'normal': 55,
       'normal_rate': 0.44715447154471544}),
     ((2.0, -2.8000000000000003),
      {'total': 132,
       'success': 2,
       'success_rate': 0.015151515151515152,
       'reset': 95,
       'reset_rate': 0.7196969696969697,
       'normal': 35,
       'normal_rate': 0.26515151515151514}),
     ((1.6, -2.4000000000000004),
      {'total': 133,
       'success': 2,
       'success_rate': 0.015037593984962405,
       'reset': 103,
       'reset_rate': 0.7744360902255639,
       'normal': 28,
       'normal_rate': 0.21052631578947367}),
     ((3.5999999999999996, -2.4000000000000004),
      {'total': 116,
       'success': 1,
       'success_rate': 0.008620689655172414,
       'reset': 53,
       'reset_rate': 0.45689655172413796,
       'normal': 62,
       'normal_rate': 0.5344827586206896}),
     ((2.4, -4),
      {'total': 122,
       'success': 1,
       'success_rate': 0.00819672131147541,
       'reset': 67,
       'reset_rate': 0.5491803278688525,
       'normal': 54,
       'normal_rate': 0.4426229508196721}),
     ((2.4, -3.2),
      {'total': 129,
       'success': 1,
       'success_rate': 0.007751937984496124,
       'reset': 87,
       'reset_rate': 0.6744186046511628,
       'normal': 41,
       'normal_rate': 0.3178294573643411}),
     ((3.5999999999999996, -2.0000000000000004),
      {'total': 131,
       'success': 0,
       'success_rate': 0.0,
       'reset': 92,
       'reset_rate': 0.7022900763358778,
       'normal': 39,
       'normal_rate': 0.29770992366412213}),
     ((3.5999999999999996, -2.8000000000000003),
      {'total': 101,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 101,
       'normal_rate': 1.0}),
     ((3.5999999999999996, -3.2),
      {'total': 101,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 101,
       'normal_rate': 1.0}),
     ((3.5999999999999996, -3.6),
      {'total': 101,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 101,
       'normal_rate': 1.0}),
     ((3.5999999999999996, -4),
      {'total': 101,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 101,
       'normal_rate': 1.0}),
     ((3.1999999999999997, -2.4000000000000004),
      {'total': 101,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 101,
       'normal_rate': 1.0}),
     ((3.1999999999999997, -2.8000000000000003),
      {'total': 101,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 101,
       'normal_rate': 1.0}),
     ((3.1999999999999997, -3.2),
      {'total': 101,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 101,
       'normal_rate': 1.0}),
     ((3.1999999999999997, -3.6),
      {'total': 101,
       'success': 0,
       'success_rate': 0.0,
       'reset': 1,
       'reset_rate': 0.009900990099009901,
       'normal': 100,
       'normal_rate': 0.9900990099009901}),
     ((3.1999999999999997, -4),
      {'total': 119,
       'success': 0,
       'success_rate': 0.0,
       'reset': 61,
       'reset_rate': 0.5126050420168067,
       'normal': 58,
       'normal_rate': 0.48739495798319327}),
     ((2.8, -2.0000000000000004),
      {'total': 101,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 101,
       'normal_rate': 1.0}),
     ((2.8, -2.4000000000000004),
      {'total': 101,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 101,
       'normal_rate': 1.0}),
     ((2.8, -2.8000000000000003),
      {'total': 101,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 101,
       'normal_rate': 1.0}),
     ((2.8, -3.2),
      {'total': 101,
       'success': 0,
       'success_rate': 0.0,
       'reset': 1,
       'reset_rate': 0.009900990099009901,
       'normal': 100,
       'normal_rate': 0.9900990099009901}),
     ((2.8, -3.6),
      {'total': 119,
       'success': 0,
       'success_rate': 0.0,
       'reset': 61,
       'reset_rate': 0.5126050420168067,
       'normal': 58,
       'normal_rate': 0.48739495798319327}),
     ((2.8, -4),
      {'total': 122,
       'success': 0,
       'success_rate': 0.0,
       'reset': 68,
       'reset_rate': 0.5573770491803278,
       'normal': 54,
       'normal_rate': 0.4426229508196721}),
     ((2.4, -2.0000000000000004),
      {'total': 101,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 101,
       'normal_rate': 1.0}),
     ((2.4, -2.4000000000000004),
      {'total': 101,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 101,
       'normal_rate': 1.0}),
     ((2.4, -2.8000000000000003),
      {'total': 101,
       'success': 0,
       'success_rate': 0.0,
       'reset': 1,
       'reset_rate': 0.009900990099009901,
       'normal': 100,
       'normal_rate': 0.9900990099009901}),
     ((2.4, -3.6),
      {'total': 123,
       'success': 0,
       'success_rate': 0.0,
       'reset': 73,
       'reset_rate': 0.5934959349593496,
       'normal': 50,
       'normal_rate': 0.4065040650406504}),
     ((2.0, -2.0000000000000004),
      {'total': 101,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 101,
       'normal_rate': 1.0}),
     ((2.0, -2.4000000000000004),
      {'total': 102,
       'success': 0,
       'success_rate': 0.0,
       'reset': 3,
       'reset_rate': 0.029411764705882353,
       'normal': 99,
       'normal_rate': 0.9705882352941176}),
     ((2.0, -3.2),
      {'total': 129,
       'success': 0,
       'success_rate': 0.0,
       'reset': 88,
       'reset_rate': 0.6821705426356589,
       'normal': 41,
       'normal_rate': 0.3178294573643411}),
     ((2.0, -3.6),
      {'total': 125,
       'success': 0,
       'success_rate': 0.0,
       'reset': 75,
       'reset_rate': 0.6,
       'normal': 50,
       'normal_rate': 0.4}),
     ((2.0, -4),
      {'total': 123,
       'success': 0,
       'success_rate': 0.0,
       'reset': 70,
       'reset_rate': 0.5691056910569106,
       'normal': 53,
       'normal_rate': 0.43089430894308944}),
     ((1.6, -2.0000000000000004),
      {'total': 103,
       'success': 0,
       'success_rate': 0.0,
       'reset': 6,
       'reset_rate': 0.05825242718446602,
       'normal': 97,
       'normal_rate': 0.941747572815534}),
     ((1.6, -3.2),
      {'total': 132,
       'success': 0,
       'success_rate': 0.0,
       'reset': 98,
       'reset_rate': 0.7424242424242424,
       'normal': 34,
       'normal_rate': 0.25757575757575757}),
     ((1.6, -3.6),
      {'total': 125,
       'success': 0,
       'success_rate': 0.0,
       'reset': 82,
       'reset_rate': 0.656,
       'normal': 43,
       'normal_rate': 0.344}),
     ((1.6, -4),
      {'total': 122,
       'success': 0,
       'success_rate': 0.0,
       'reset': 70,
       'reset_rate': 0.5737704918032787,
       'normal': 52,
       'normal_rate': 0.4262295081967213}),
     ((1.2000000000000002, -2.0000000000000004),
      {'total': 101,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 101,
       'normal_rate': 1.0}),
     ((1.2000000000000002, -2.4000000000000004),
      {'total': 101,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 101,
       'normal_rate': 1.0}),
     ((1.2000000000000002, -2.8000000000000003),
      {'total': 101,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 101,
       'normal_rate': 1.0}),
     ((1.2000000000000002, -3.2),
      {'total': 101,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 101,
       'normal_rate': 1.0}),
     ((1.2000000000000002, -3.6),
      {'total': 101,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 101,
       'normal_rate': 1.0}),
     ((1.2000000000000002, -4),
      {'total': 101,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 101,
       'normal_rate': 1.0}),
     ((0.8, -2.0000000000000004),
      {'total': 101,
       'success': 0,
       'success_rate': 0.0,
       'reset': 4,
       'reset_rate': 0.039603960396039604,
       'normal': 97,
       'normal_rate': 0.9603960396039604}),
     ((0.8, -2.4000000000000004),
      {'total': 101,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 101,
       'normal_rate': 1.0}),
     ((0.8, -2.8000000000000003),
      {'total': 101,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 101,
       'normal_rate': 1.0}),
     ((0.8, -3.2),
      {'total': 101,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 101,
       'normal_rate': 1.0}),
     ((0.8, -3.6),
      {'total': 102,
       'success': 0,
       'success_rate': 0.0,
       'reset': 4,
       'reset_rate': 0.0392156862745098,
       'normal': 98,
       'normal_rate': 0.9607843137254902}),
     ((0.8, -4),
      {'total': 101,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 101,
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

