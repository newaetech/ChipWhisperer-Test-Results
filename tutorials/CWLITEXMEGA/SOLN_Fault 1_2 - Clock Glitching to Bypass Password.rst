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
    PLATFORM = 'CWLITEXMEGA'
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
        scope = cw.scope(hw_location=(5, 4))
    
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
        scope = cw.scope(hw_location=(5, 4))
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
    scope.adc.trig\_count                     changed from 10854567                  to 21897954                 
    scope.clock.adc\_src                      changed from clkgen\_x1                 to clkgen\_x4                
    scope.clock.adc\_freq                     changed from 29538459                  to 96000000                 
    scope.clock.adc\_rate                     changed from 29538459.0                to 96000000.0               
    scope.clock.clkgen\_div                   changed from 1                         to 26                       
    scope.clock.clkgen\_freq                  changed from 192000000.0               to 7384615.384615385        
    scope.io.tio1                            changed from serial\_tx                 to serial\_rx                
    scope.io.tio2                            changed from serial\_rx                 to serial\_tx                
    scope.io.hs2                             changed from None                      to clkgen                   
    scope.io.tio\_states                      changed from (1, 0, 0, 0)              to (1, 1, 0, 0)             




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
    Welcome to another exciting ChipWhisperer target build!!
    avr-gcc (GCC) 5.4.0
    Copyright (C) 2015 Free Software Foundation, Inc.
    This is free software; see the source for copying conditions.  There is NO
    warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
    
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
    -en     .././hal/xmega/XMEGA\_AES\_driver.c ...
    -en     .././hal/xmega/uart.c ...
    .
    .
    Compiling:
    Compiling:
    -en     .././hal/xmega/usart\_driver.c ...
    -en     .././hal/xmega/xmega\_hal.c ...
    -e Done!
    -e Done!
    -e Done!
    -e Done!
    -e Done!
    -e Done!
    .
    LINKING:
    -en     simpleserial-glitch-CWLITEXMEGA.elf ...
    -e Done!
    .
    .
    .
    Creating load file for Flash: simpleserial-glitch-CWLITEXMEGA.hex
    Creating load file for Flash: simpleserial-glitch-CWLITEXMEGA.bin
    Creating load file for EEPROM: simpleserial-glitch-CWLITEXMEGA.eep
    avr-objcopy -O ihex -R .eeprom -R .fuse -R .lock -R .signature simpleserial-glitch-CWLITEXMEGA.elf simpleserial-glitch-CWLITEXMEGA.hex
    avr-objcopy -O binary -R .eeprom -R .fuse -R .lock -R .signature simpleserial-glitch-CWLITEXMEGA.elf simpleserial-glitch-CWLITEXMEGA.bin
    .
    .
    avr-objcopy -j .eeprom --set-section-flags=.eeprom="alloc,load" \
    --change-section-lma .eeprom=0 --no-change-warnings -O ihex simpleserial-glitch-CWLITEXMEGA.elf simpleserial-glitch-CWLITEXMEGA.eep \|\| exit 0
    Creating Extended Listing: simpleserial-glitch-CWLITEXMEGA.lss
    Creating Symbol Table: simpleserial-glitch-CWLITEXMEGA.sym
    avr-nm -n simpleserial-glitch-CWLITEXMEGA.elf > simpleserial-glitch-CWLITEXMEGA.sym
    avr-objdump -h -S -z simpleserial-glitch-CWLITEXMEGA.elf > simpleserial-glitch-CWLITEXMEGA.lss
    SS\_VER set to SS\_VER\_2\_1
    SS\_VER set to SS\_VER\_2\_1
    Size after:
    +--------------------------------------------------------
       text	   data	    bss	    dec	    hex	filename
       2628	      6	     82	   2716	    a9c	simpleserial-glitch-CWLITEXMEGA.elf
    +--------------------------------------------------------
    + Built for platform CW-Lite XMEGA with:
    + Default target does full rebuild each time.
    + CRYPTO\_TARGET = NONE
    + Specify buildtarget == allquick == to avoid full rebuild
    + CRYPTO\_OPTIONS = 
    +--------------------------------------------------------
    +--------------------------------------------------------




**In [4]:**

.. code:: ipython3

    fw_path = "../../../hardware/victims/firmware/simpleserial-glitch/simpleserial-glitch-{}.hex".format(PLATFORM)
    cw.program_target(scope, prog, fw_path)
    if SS_VER == 'SS_VER_2_1':
        target.reset_comms()


**Out [4]:**



.. parsed-literal::

    XMEGA Programming flash...
    XMEGA Reading flash...
    Verified flash OK, 2633 bytes




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

    scope.clock.adc\_freq                     changed from 96000000                  to 29538459                 
    scope.clock.adc\_rate                     changed from 96000000.0                to 29538459.0               



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
      <div class="bk-root" id="795c1ea1-1323-4acb-b1c7-1067cc35f341" data-root-id="1002"></div>
    </div>
    <script type="application/javascript">(function(root) {
      function embed_document(root) {
        var docs_json = {"0aa609aa-3d12-4300-8229-9e19598e8e8c":{"defs":[{"extends":null,"module":null,"name":"ReactiveHTML1","overrides":[],"properties":[]},{"extends":null,"module":null,"name":"FlexBox1","overrides":[],"properties":[{"default":"flex-start","kind":null,"name":"align_content"},{"default":"flex-start","kind":null,"name":"align_items"},{"default":"row","kind":null,"name":"flex_direction"},{"default":"wrap","kind":null,"name":"flex_wrap"},{"default":"flex-start","kind":null,"name":"justify_content"}]},{"extends":null,"module":null,"name":"GridStack1","overrides":[],"properties":[{"default":"warn","kind":null,"name":"mode"},{"default":null,"kind":null,"name":"ncols"},{"default":null,"kind":null,"name":"nrows"},{"default":true,"kind":null,"name":"allow_resize"},{"default":true,"kind":null,"name":"allow_drag"},{"default":[],"kind":null,"name":"state"}]},{"extends":null,"module":null,"name":"click1","overrides":[],"properties":[{"default":"","kind":null,"name":"terminal_output"},{"default":"","kind":null,"name":"debug_name"},{"default":0,"kind":null,"name":"clears"}]},{"extends":null,"module":null,"name":"NotificationAreaBase1","overrides":[],"properties":[{"default":"bottom-right","kind":null,"name":"position"},{"default":0,"kind":null,"name":"_clear"}]},{"extends":null,"module":null,"name":"NotificationArea1","overrides":[],"properties":[{"default":[],"kind":null,"name":"notifications"},{"default":"bottom-right","kind":null,"name":"position"},{"default":0,"kind":null,"name":"_clear"},{"default":[{"background":"#ffc107","icon":{"className":"fas fa-exclamation-triangle","color":"white","tagName":"i"},"type":"warning"},{"background":"#007bff","icon":{"className":"fas fa-info-circle","color":"white","tagName":"i"},"type":"info"}],"kind":null,"name":"types"}]},{"extends":null,"module":null,"name":"Notification","overrides":[],"properties":[{"default":null,"kind":null,"name":"background"},{"default":3000,"kind":null,"name":"duration"},{"default":null,"kind":null,"name":"icon"},{"default":"","kind":null,"name":"message"},{"default":null,"kind":null,"name":"notification_type"},{"default":false,"kind":null,"name":"_destroyed"}]},{"extends":null,"module":null,"name":"TemplateActions1","overrides":[],"properties":[{"default":0,"kind":null,"name":"open_modal"},{"default":0,"kind":null,"name":"close_modal"}]},{"extends":null,"module":null,"name":"MaterialTemplateActions1","overrides":[],"properties":[{"default":0,"kind":null,"name":"open_modal"},{"default":0,"kind":null,"name":"close_modal"}]}],"roots":{"references":[{"attributes":{"fill_color":{"value":"#007f00"},"hatch_color":{"value":"#007f00"},"line_color":{"value":"#007f00"},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"ext_offset"},"y":{"field":"offset"}},"id":"1048","type":"Scatter"},{"attributes":{},"id":"1016","type":"LinearScale"},{"attributes":{"coordinates":null,"data_source":{"id":"1045"},"glyph":{"id":"1048"},"group":null,"hover_glyph":null,"muted_glyph":{"id":"1050"},"nonselection_glyph":{"id":"1049"},"selection_glyph":{"id":"1053"},"view":{"id":"1052"}},"id":"1051","type":"GlyphRenderer"},{"attributes":{},"id":"1017","type":"LinearScale"},{"attributes":{},"id":"1019","type":"BasicTicker"},{"attributes":{"axis":{"id":"1018"},"coordinates":null,"grid_line_color":null,"group":null,"ticker":null},"id":"1021","type":"Grid"},{"attributes":{"axis_label":"offset","coordinates":null,"formatter":{"id":"1043"},"group":null,"major_label_policy":{"id":"1044"},"ticker":{"id":"1023"}},"id":"1022","type":"LinearAxis"},{"attributes":{"axis":{"id":"1022"},"coordinates":null,"dimension":1,"grid_line_color":null,"group":null,"ticker":null},"id":"1025","type":"Grid"},{"attributes":{"fill_alpha":{"value":0.2},"fill_color":{"value":"#007f00"},"hatch_alpha":{"value":0.2},"hatch_color":{"value":"#007f00"},"line_alpha":{"value":0.2},"line_color":{"value":"#007f00"},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"ext_offset"},"y":{"field":"offset"}},"id":"1050","type":"Scatter"},{"attributes":{},"id":"1074","type":"UnionRenderers"},{"attributes":{},"id":"1023","type":"BasicTicker"},{"attributes":{"children":[{"id":"1009"}],"height":600,"margin":[0,0,0,0],"name":"Row00811","sizing_mode":"fixed","width":800},"id":"1002","type":"Row"},{"attributes":{},"id":"1028","type":"WheelZoomTool"},{"attributes":{},"id":"1046","type":"Selection"},{"attributes":{"angle":{"value":0.7853981633974483},"fill_alpha":{"value":0.1},"fill_color":{"value":"#ff0000"},"hatch_alpha":{"value":0.1},"hatch_color":{"value":"#ff0000"},"line_alpha":{"value":0.1},"line_color":{"value":"#ff0000"},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"ext_offset"},"y":{"field":"offset"}},"id":"1058","type":"Scatter"},{"attributes":{},"id":"1027","type":"PanTool"},{"attributes":{},"id":"1026","type":"SaveTool"},{"attributes":{"source":{"id":"1045"}},"id":"1052","type":"CDSView"},{"attributes":{"overlay":{"id":"1031"}},"id":"1029","type":"BoxZoomTool"},{"attributes":{"tags":[[["ext_offset","ext_offset",null]],[]]},"id":"1003","type":"Range1d"},{"attributes":{},"id":"1030","type":"ResetTool"},{"attributes":{},"id":"1076","type":"UnionRenderers"},{"attributes":{"tags":[[["offset","offset",null]],{"autorange":false,"invert_yaxis":false}]},"id":"1004","type":"Range1d"},{"attributes":{"client_comm_id":"a0c959a2fae8482a9ed8b7c0cbdaf4bc","comm_id":"bc9e5eeaddd7462abac23d06ba19c532","plot_id":"1002"},"id":"1115","type":"panel.models.comm_manager.CommManager"},{"attributes":{"data":{"ext_offset":{"__ndarray__":"","dtype":"float64","order":"little","shape":[0]},"offset":{"__ndarray__":"","dtype":"float64","order":"little","shape":[0]}},"selected":{"id":"1055"},"selection_policy":{"id":"1076"}},"id":"1054","type":"ColumnDataSource"},{"attributes":{"bottom_units":"screen","coordinates":null,"fill_alpha":0.5,"fill_color":"lightgrey","group":null,"left_units":"screen","level":"overlay","line_alpha":1.0,"line_color":"black","line_dash":[4,4],"line_width":2,"right_units":"screen","syncable":false,"top_units":"screen"},"id":"1031","type":"BoxAnnotation"},{"attributes":{"angle":{"value":0.0},"fill_alpha":{"value":1.0},"fill_color":{"value":"#007f00"},"hatch_alpha":{"value":1.0},"hatch_color":{"value":"#007f00"},"hatch_scale":{"value":12.0},"hatch_weight":{"value":1.0},"line_alpha":{"value":1.0},"line_cap":{"value":"butt"},"line_color":{"value":"#007f00"},"line_dash":{"value":[]},"line_dash_offset":{"value":0},"line_join":{"value":"bevel"},"line_width":{"value":1},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"ext_offset"},"y":{"field":"offset"}},"id":"1053","type":"Scatter"},{"attributes":{"source":{"id":"1054"}},"id":"1061","type":"CDSView"},{"attributes":{"active_drag":{"id":"1027"},"active_scroll":{"id":"1028"},"tools":[{"id":"1007"},{"id":"1026"},{"id":"1027"},{"id":"1028"},{"id":"1029"},{"id":"1030"}]},"id":"1032","type":"Toolbar"},{"attributes":{},"id":"1041","type":"AllLabels"},{"attributes":{"angle":{"value":0.7853981633974483},"fill_color":{"value":"#ff0000"},"hatch_color":{"value":"#ff0000"},"line_color":{"value":"#ff0000"},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"ext_offset"},"y":{"field":"offset"}},"id":"1057","type":"Scatter"},{"attributes":{},"id":"1044","type":"AllLabels"},{"attributes":{"callback":null,"renderers":[{"id":"1051"},{"id":"1060"}],"tags":["hv_created"],"tooltips":[["ext_offset","@{ext_offset}"],["offset","@{offset}"]]},"id":"1007","type":"HoverTool"},{"attributes":{},"id":"1040","type":"BasicTickFormatter"},{"attributes":{"angle":{"value":0.7853981633974483},"fill_alpha":{"value":1.0},"fill_color":{"value":"#ff0000"},"hatch_alpha":{"value":1.0},"hatch_color":{"value":"#ff0000"},"hatch_scale":{"value":12.0},"hatch_weight":{"value":1.0},"line_alpha":{"value":1.0},"line_cap":{"value":"butt"},"line_color":{"value":"#ff0000"},"line_dash":{"value":[]},"line_dash_offset":{"value":0},"line_join":{"value":"bevel"},"line_width":{"value":1},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"ext_offset"},"y":{"field":"offset"}},"id":"1062","type":"Scatter"},{"attributes":{"fill_alpha":{"value":0.1},"fill_color":{"value":"#007f00"},"hatch_alpha":{"value":0.1},"hatch_color":{"value":"#007f00"},"line_alpha":{"value":0.1},"line_color":{"value":"#007f00"},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"ext_offset"},"y":{"field":"offset"}},"id":"1049","type":"Scatter"},{"attributes":{},"id":"1043","type":"BasicTickFormatter"},{"attributes":{},"id":"1055","type":"Selection"},{"attributes":{"axis_label":"ext_offset","coordinates":null,"formatter":{"id":"1040"},"group":null,"major_label_policy":{"id":"1041"},"ticker":{"id":"1019"}},"id":"1018","type":"LinearAxis"},{"attributes":{"angle":{"value":0.7853981633974483},"fill_alpha":{"value":0.2},"fill_color":{"value":"#ff0000"},"hatch_alpha":{"value":0.2},"hatch_color":{"value":"#ff0000"},"line_alpha":{"value":0.2},"line_color":{"value":"#ff0000"},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"ext_offset"},"y":{"field":"offset"}},"id":"1059","type":"Scatter"},{"attributes":{"data":{"ext_offset":{"__ndarray__":"","dtype":"float64","order":"little","shape":[0]},"offset":{"__ndarray__":"","dtype":"float64","order":"little","shape":[0]}},"selected":{"id":"1046"},"selection_policy":{"id":"1074"}},"id":"1045","type":"ColumnDataSource"},{"attributes":{"coordinates":null,"data_source":{"id":"1054"},"glyph":{"id":"1057"},"group":null,"hover_glyph":null,"muted_glyph":{"id":"1059"},"nonselection_glyph":{"id":"1058"},"selection_glyph":{"id":"1062"},"view":{"id":"1061"}},"id":"1060","type":"GlyphRenderer"},{"attributes":{"coordinates":null,"group":null,"text_color":"black","text_font_size":"12pt"},"id":"1010","type":"Title"},{"attributes":{"below":[{"id":"1018"}],"center":[{"id":"1021"},{"id":"1025"}],"left":[{"id":"1022"}],"margin":[5,5,5,5],"min_border_bottom":10,"min_border_left":10,"min_border_right":10,"min_border_top":10,"output_backend":"webgl","renderers":[{"id":"1051"},{"id":"1060"}],"sizing_mode":"fixed","title":{"id":"1010"},"toolbar":{"id":"1032"},"width":800,"x_range":{"id":"1003"},"x_scale":{"id":"1016"},"y_range":{"id":"1004"},"y_scale":{"id":"1017"}},"id":"1009","subtype":"Figure","type":"Plot"}],"root_ids":["1002","1115"]},"title":"Bokeh Application","version":"2.4.3"}};
        var render_items = [{"docid":"0aa609aa-3d12-4300-8229-9e19598e8e8c","root_ids":["1002"],"roots":{"1002":"795c1ea1-1323-4acb-b1c7-1067cc35f341"}}];
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

    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!





.. parsed-literal::

    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!





.. parsed-literal::

    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!





.. parsed-literal::

    CWbytearray(b'01')
    44.921875 -47.65625 53
    🐙CWbytearray(b'01')
    44.921875 -47.65625 53
    🐙CWbytearray(b'01')
    44.921875 -47.65625 53
    🐙CWbytearray(b'01')
    44.921875 -47.65625 53
    🐙




.. parsed-literal::

    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1





.. parsed-literal::

    CWbytearray(b'01')
    44.921875 -47.65625 53
    🐙




.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    WARNING:root:SAM3U Serial buffers OVERRUN - data loss has occurred.
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    WARNING:root:SAM3U Serial buffers OVERRUN - data loss has occurred.
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 69, 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 69, 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 69, 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 69, 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 69, 1
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!





.. parsed-literal::

    Trigger still high!
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!





.. parsed-literal::

    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!





.. parsed-literal::

    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!





.. parsed-literal::

    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!





.. parsed-literal::

    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!





.. parsed-literal::

    CWbytearray(b'01')
    44.921875 -46.875 54
    🐙CWbytearray(b'01')
    44.921875 -46.875 54
    🐙




.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    WARNING:root:SAM3U Serial buffers OVERRUN - data loss has occurred.
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    WARNING:root:SAM3U Serial buffers OVERRUN - data loss has occurred.
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

    WARNING:root:SAM3U Serial buffers OVERRUN - data loss has occurred.
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:288) Device reported error 0x6
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:290) CWbytearray(b'00 65 01 06 08 00')
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:288) Device reported error 0x6
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:290) CWbytearray(b'00 65 01 06 08 00')
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 6
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:288) Device reported error 0x3
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:290) CWbytearray(b'00 06 06 03 72 01 00 06 06 86 00')
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!





.. parsed-literal::

    Trigger still high!
    Trigger still high!
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!





.. parsed-literal::

    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!





.. parsed-literal::

    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!





.. parsed-literal::

    CWbytearray(b'01')
    46.09375 -48.828125 54
    🐙CWbytearray(b'01')
    46.09375 -48.828125 54
    🐙




.. parsed-literal::

    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1





.. parsed-literal::

    CWbytearray(b'01')
    46.09375 -48.828125 54
    🐙




.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
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

    WARNING:root:SAM3U Serial buffers OVERRUN - data loss has occurred.
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    WARNING:root:SAM3U Serial buffers OVERRUN - data loss has occurred.
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 69, 1
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!





.. parsed-literal::

    Trigger still high!
    Trigger still high!
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!





.. parsed-literal::

    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!





.. parsed-literal::

    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!





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





.. parsed-literal::

    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!





.. parsed-literal::

    Trigger still high!
    Trigger still high!
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!





.. parsed-literal::

    CWbytearray(b'01')
    46.875 -49.609375 53
    🐙CWbytearray(b'01')
    46.875 -49.609375 53
    🐙CWbytearray(b'01')
    46.875 -49.609375 53
    🐙CWbytearray(b'01')
    46.875 -49.609375 53
    🐙CWbytearray(b'01')
    46.875 -49.609375 53
    🐙CWbytearray(b'01')
    46.875 -49.609375 53
    🐙




.. parsed-literal::

    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!





.. parsed-literal::

    CWbytearray(b'01')
    46.875 -49.609375 53
    🐙CWbytearray(b'01')
    46.875 -49.609375 54
    🐙




.. parsed-literal::

    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
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

    WARNING:root:SAM3U Serial buffers OVERRUN - data loss has occurred.
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

    WARNING:root:SAM3U Serial buffers OVERRUN - data loss has occurred.
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    WARNING:root:SAM3U Serial buffers OVERRUN - data loss has occurred.
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
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

    WARNING:root:SAM3U Serial buffers OVERRUN - data loss has occurred.
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 69, 1
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    WARNING:root:SAM3U Serial buffers OVERRUN - data loss has occurred.
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 69, 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 69, 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 69, 1
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!





.. parsed-literal::

    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!





.. parsed-literal::

    Trigger still high!
    Trigger still high!
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!





.. parsed-literal::

    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!





.. parsed-literal::

    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!





.. parsed-literal::

    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!





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

    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!





.. parsed-literal::

    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1





.. parsed-literal::

    CWbytearray(b'01')
    46.875 -48.828125 54
    🐙




.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
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

    WARNING:root:SAM3U Serial buffers OVERRUN - data loss has occurred.
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

    WARNING:root:SAM3U Serial buffers OVERRUN - data loss has occurred.
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    WARNING:root:SAM3U Serial buffers OVERRUN - data loss has occurred.
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 69, 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 69, 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 69, 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 69, 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 69, 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 69, 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 69, 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 69, 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 69, 1
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:288) Device reported error 0x6
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:290) CWbytearray(b'00 65 01 06 08 00')
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 6
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:288) Device reported error 0x3
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:290) CWbytearray(b'00 06 06 03 72 01 00 06 06 86 00')
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!





.. parsed-literal::

    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!





.. parsed-literal::

    Trigger still high!
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!





.. parsed-literal::

    CWbytearray(b'01')
    48.828125 -46.875 54
    🐙CWbytearray(b'01')
    48.828125 -46.875 54
    🐙




.. parsed-literal::

    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:723) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    WARNING:root:SAM3U Serial buffers OVERRUN - data loss has occurred.
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 69, 1
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:288) Device reported error 0x6
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:290) CWbytearray(b'00 65 01 06 08 00')
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 69, 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!
    (ChipWhisperer Glitch WARNING\|File ChipWhispererGlitch.py:971) Negative offsets <-45 may result in double glitches!



For this lab, you may want two copies of your results; one for finding
effective ext_offsets:


**In [12]:**

.. code:: ipython3

    results = gc.calc(ignore_params=["width", "offset"], sort="success_rate")
    results


**Out [12]:**



.. parsed-literal::

    [((53,),
      {'total': 200,
       'success': 12,
       'success_rate': 0.06,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 188,
       'normal_rate': 0.94}),
     ((54,),
      {'total': 200,
       'success': 9,
       'success_rate': 0.045,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 191,
       'normal_rate': 0.955}),
     ((70,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 7,
       'reset_rate': 0.035,
       'normal': 193,
       'normal_rate': 0.965}),
     ((69,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 15,
       'reset_rate': 0.075,
       'normal': 185,
       'normal_rate': 0.925}),
     ((68,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 25,
       'reset_rate': 0.125,
       'normal': 175,
       'normal_rate': 0.875}),
     ((67,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 26,
       'reset_rate': 0.13,
       'normal': 174,
       'normal_rate': 0.87}),
     ((66,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 15,
       'reset_rate': 0.075,
       'normal': 185,
       'normal_rate': 0.925}),
     ((65,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 4,
       'reset_rate': 0.02,
       'normal': 196,
       'normal_rate': 0.98}),
     ((64,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 8,
       'reset_rate': 0.04,
       'normal': 192,
       'normal_rate': 0.96}),
     ((63,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 9,
       'reset_rate': 0.045,
       'normal': 191,
       'normal_rate': 0.955}),
     ((62,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 5,
       'reset_rate': 0.025,
       'normal': 195,
       'normal_rate': 0.975}),
     ((61,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 1,
       'reset_rate': 0.005,
       'normal': 199,
       'normal_rate': 0.995}),
     ((60,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 2,
       'reset_rate': 0.01,
       'normal': 198,
       'normal_rate': 0.99}),
     ((59,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 200,
       'normal_rate': 1.0}),
     ((58,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 10,
       'reset_rate': 0.05,
       'normal': 190,
       'normal_rate': 0.95}),
     ((57,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 40,
       'reset_rate': 0.2,
       'normal': 160,
       'normal_rate': 0.8}),
     ((56,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 16,
       'reset_rate': 0.08,
       'normal': 184,
       'normal_rate': 0.92}),
     ((55,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 200,
       'normal_rate': 1.0}),
     ((52,),
      {'total': 201,
       'success': 0,
       'success_rate': 0.0,
       'reset': 1,
       'reset_rate': 0.004975124378109453,
       'normal': 200,
       'normal_rate': 0.9950248756218906}),
     ((51,),
      {'total': 218,
       'success': 0,
       'success_rate': 0.0,
       'reset': 18,
       'reset_rate': 0.08256880733944955,
       'normal': 200,
       'normal_rate': 0.9174311926605505}),
     ((50,),
      {'total': 227,
       'success': 0,
       'success_rate': 0.0,
       'reset': 27,
       'reset_rate': 0.11894273127753303,
       'normal': 200,
       'normal_rate': 0.8810572687224669}),
     ((49,),
      {'total': 210,
       'success': 0,
       'success_rate': 0.0,
       'reset': 10,
       'reset_rate': 0.047619047619047616,
       'normal': 200,
       'normal_rate': 0.9523809523809523}),
     ((48,),
      {'total': 201,
       'success': 0,
       'success_rate': 0.0,
       'reset': 1,
       'reset_rate': 0.004975124378109453,
       'normal': 200,
       'normal_rate': 0.9950248756218906}),
     ((47,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 200,
       'normal_rate': 1.0}),
     ((46,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 200,
       'normal_rate': 1.0}),
     ((45,),
      {'total': 201,
       'success': 0,
       'success_rate': 0.0,
       'reset': 1,
       'reset_rate': 0.004975124378109453,
       'normal': 200,
       'normal_rate': 0.9950248756218906}),
     ((44,),
      {'total': 209,
       'success': 0,
       'success_rate': 0.0,
       'reset': 18,
       'reset_rate': 0.0861244019138756,
       'normal': 191,
       'normal_rate': 0.9138755980861244}),
     ((43,),
      {'total': 205,
       'success': 0,
       'success_rate': 0.0,
       'reset': 11,
       'reset_rate': 0.05365853658536585,
       'normal': 194,
       'normal_rate': 0.9463414634146341}),
     ((42,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 200,
       'normal_rate': 1.0}),
     ((41,),
      {'total': 201,
       'success': 0,
       'success_rate': 0.0,
       'reset': 2,
       'reset_rate': 0.009950248756218905,
       'normal': 199,
       'normal_rate': 0.9900497512437811}),
     ((40,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 1,
       'reset_rate': 0.005,
       'normal': 199,
       'normal_rate': 0.995}),
     ((39,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 200,
       'normal_rate': 1.0}),
     ((38,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 200,
       'normal_rate': 1.0}),
     ((37,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 200,
       'normal_rate': 1.0}),
     ((36,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 200,
       'normal_rate': 1.0}),
     ((35,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 200,
       'normal_rate': 1.0}),
     ((34,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 200,
       'normal_rate': 1.0}),
     ((33,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 200,
       'normal_rate': 1.0}),
     ((32,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 200,
       'normal_rate': 1.0}),
     ((31,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 200,
       'normal_rate': 1.0}),
     ((30,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 200,
       'normal_rate': 1.0}),
     ((29,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 200,
       'normal_rate': 1.0}),
     ((28,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 200,
       'normal_rate': 1.0}),
     ((27,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 200,
       'normal_rate': 1.0}),
     ((26,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 200,
       'normal_rate': 1.0}),
     ((25,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 200,
       'normal_rate': 1.0}),
     ((24,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 200,
       'normal_rate': 1.0}),
     ((23,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 200,
       'normal_rate': 1.0}),
     ((22,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 200,
       'normal_rate': 1.0}),
     ((21,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 200,
       'normal_rate': 1.0}),
     ((20,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 200,
       'normal_rate': 1.0}),
     ((19,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 200,
       'normal_rate': 1.0}),
     ((18,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 200,
       'normal_rate': 1.0}),
     ((17,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 200,
       'normal_rate': 1.0}),
     ((16,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 200,
       'normal_rate': 1.0}),
     ((15,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 200,
       'normal_rate': 1.0}),
     ((14,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 200,
       'normal_rate': 1.0}),
     ((13,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 200,
       'normal_rate': 1.0}),
     ((12,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 200,
       'normal_rate': 1.0}),
     ((11,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 200,
       'normal_rate': 1.0}),
     ((10,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 200,
       'normal_rate': 1.0}),
     ((9,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 200,
       'normal_rate': 1.0}),
     ((8,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 200,
       'normal_rate': 1.0}),
     ((7,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 200,
       'normal_rate': 1.0}),
     ((6,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 200,
       'normal_rate': 1.0}),
     ((5,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 200,
       'normal_rate': 1.0}),
     ((4,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 200,
       'normal_rate': 1.0})]



And one for your width/offset settings:


**In [13]:**

.. code:: ipython3

    results = gc.calc(ignore_params=["ext_offset"], sort="success_rate")
    results


**Out [13]:**



.. parsed-literal::

    [((47, -49.8),
      {'total': 693,
       'success': 8,
       'success_rate': 0.011544011544011544,
       'reset': 85,
       'reset_rate': 0.12265512265512266,
       'normal': 600,
       'normal_rate': 0.8658008658008658}),
     ((45, -47.8),
      {'total': 676,
       'success': 5,
       'success_rate': 0.0073964497041420114,
       'reset': 24,
       'reset_rate': 0.03550295857988166,
       'normal': 647,
       'normal_rate': 0.9571005917159763}),
     ((46, -48.8),
      {'total': 682,
       'success': 3,
       'success_rate': 0.004398826979472141,
       'reset': 29,
       'reset_rate': 0.04252199413489736,
       'normal': 650,
       'normal_rate': 0.9530791788856305}),
     ((49, -46.8),
      {'total': 673,
       'success': 2,
       'success_rate': 0.0029717682020802376,
       'reset': 20,
       'reset_rate': 0.029717682020802376,
       'normal': 651,
       'normal_rate': 0.9673105497771174}),
     ((45, -46.8),
      {'total': 676,
       'success': 2,
       'success_rate': 0.0029585798816568047,
       'reset': 32,
       'reset_rate': 0.047337278106508875,
       'normal': 642,
       'normal_rate': 0.9497041420118343}),
     ((47, -48.8),
      {'total': 693,
       'success': 1,
       'success_rate': 0.001443001443001443,
       'reset': 83,
       'reset_rate': 0.11976911976911978,
       'normal': 609,
       'normal_rate': 0.8787878787878788}),
     ((49, -47.8),
      {'total': 670,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 670,
       'normal_rate': 1.0}),
     ((49, -48.8),
      {'total': 670,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 670,
       'normal_rate': 1.0}),
     ((49, -49.8),
      {'total': 670,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 670,
       'normal_rate': 1.0}),
     ((48, -46.8),
      {'total': 670,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 670,
       'normal_rate': 1.0}),
     ((48, -47.8),
      {'total': 670,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 670,
       'normal_rate': 1.0}),
     ((48, -48.8),
      {'total': 670,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 670,
       'normal_rate': 1.0}),
     ((48, -49.8),
      {'total': 670,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 670,
       'normal_rate': 1.0}),
     ((47, -46.8),
      {'total': 670,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 670,
       'normal_rate': 1.0}),
     ((47, -47.8),
      {'total': 670,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 670,
       'normal_rate': 1.0}),
     ((46, -46.8),
      {'total': 670,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 670,
       'normal_rate': 1.0}),
     ((46, -47.8),
      {'total': 670,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 670,
       'normal_rate': 1.0}),
     ((46, -49.8),
      {'total': 670,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 670,
       'normal_rate': 1.0}),
     ((45, -48.8),
      {'total': 670,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 670,
       'normal_rate': 1.0}),
     ((45, -49.8),
      {'total': 670,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 670,
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

