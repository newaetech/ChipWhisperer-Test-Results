Part 2, Topic 2: Voltage Glitching to Bypass Password
=====================================================



**SUMMARY:** *We’ve seen how voltage glitching can be used to corrupt
calculations, just like clock glitching. Let’s continue on and see if it
can also be used to break past a password check.*

**LEARNING OUTCOMES:**

-  Applying previous glitch settings to new firmware
-  Checking for success and failure when glitching

Firmware
--------

Again, we’ve already covered this lab, so it’ll be mostly up to you!


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
    scope.adc.trig\_count                     changed from 11070229                  to 22142574                 
    scope.clock.adc\_src                      changed from clkgen\_x1                 to clkgen\_x4                
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
    -en     .././hal/stm32f3/stm32f3\_hal.c ...
    .
    Compiling:
    .
    -en     .././hal/stm32f3/stm32f3\_hal\_lowlevel.c ...
    Compiling:
    -en     .././hal/stm32f3/stm32f3\_sysmem.c ...
    .
    Assembling: .././hal/stm32f3/stm32f3\_startup.S
    -e Done!
    arm-none-eabi-gcc -c -mcpu=cortex-m4 -I. -x assembler-with-cpp -mthumb -mfloat-abi=soft -fmessage-length=0 -ffunction-sections -DF\_CPU=7372800 -Wa,-gstabs,-adhlns=objdir-CWLITEARM/stm32f3\_startup.lst -I.././simpleserial/ -I.././hal -I.././hal/stm32f3 -I.././hal/stm32f3/CMSIS -I.././hal/stm32f3/CMSIS/core -I.././hal/stm32f3/CMSIS/device -I.././hal/stm32f4/Legacy -I.././simpleserial/ -I.././crypto/ .././hal/stm32f3/stm32f3\_startup.S -o objdir-CWLITEARM/stm32f3\_startup.o
    -e Done!
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
    .
    Creating load file for Flash: simpleserial-glitch-CWLITEARM.bin
    Creating load file for EEPROM: simpleserial-glitch-CWLITEARM.eep
    arm-none-eabi-objcopy -O ihex -R .eeprom -R .fuse -R .lock -R .signature simpleserial-glitch-CWLITEARM.elf simpleserial-glitch-CWLITEARM.hex
    arm-none-eabi-objcopy -O binary -R .eeprom -R .fuse -R .lock -R .signature simpleserial-glitch-CWLITEARM.elf simpleserial-glitch-CWLITEARM.bin
    arm-none-eabi-objcopy -j .eeprom --set-section-flags=.eeprom="alloc,load" \
    --change-section-lma .eeprom=0 --no-change-warnings -O ihex simpleserial-glitch-CWLITEARM.elf simpleserial-glitch-CWLITEARM.eep \|\| exit 0
    .
    .
    Creating Extended Listing: simpleserial-glitch-CWLITEARM.lss
    Creating Symbol Table: simpleserial-glitch-CWLITEARM.sym
    arm-none-eabi-nm -n simpleserial-glitch-CWLITEARM.elf > simpleserial-glitch-CWLITEARM.sym
    arm-none-eabi-objdump -h -S -z simpleserial-glitch-CWLITEARM.elf > simpleserial-glitch-CWLITEARM.lss
    SS\_VER set to SS\_VER\_2\_1
    SS\_VER set to SS\_VER\_2\_1
    Size after:
    +--------------------------------------------------------
       text	   data	    bss	    dec	    hex	filename
       5524	      8	   1368	   6900	   1af4	simpleserial-glitch-CWLITEARM.elf
    +--------------------------------------------------------
    + Default target does full rebuild each time.
    + Built for platform CW-Lite Arm \(STM32F3\) with:
    + Specify buildtarget == allquick == to avoid full rebuild
    + CRYPTO\_TARGET = NONE
    +--------------------------------------------------------
    + CRYPTO\_OPTIONS = 
    +--------------------------------------------------------




**In [4]:**

.. code:: ipython3

    fw_path = "../../../hardware/victims/firmware/simpleserial-glitch/simpleserial-glitch-{}.hex".format(PLATFORM)
    cw.program_target(scope, prog, fw_path)
    if SS_VER=="SS_VER_2_1":
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
        target.flush()
    if PLATFORM == "CWLITEXMEGA":
        scope.clock.clkgen_freq = 32E6
        if SS_VER=='SS_VER_2_1':
            target.baud = 230400*32/7.37
        else:
            target.baud = 38400*32/7.37
    elif (PLATFORM == "CWLITEARM") or ("F3" in PLATFORM):
        scope.clock.clkgen_freq = 24E6
        if SS_VER=='SS_VER_2_1':
            target.baud = 230400*24/7.37
        else:
            target.baud = 38400*24/7.37
        


**In [6]:**

.. code:: ipython3

    #Do glitch loop
    reboot_flush()
    pw = bytearray([0x74, 0x6F, 0x75, 0x63, 0x68])
    target.simpleserial_write('p', pw)
    
    val = target.simpleserial_read_witherrors('r', 1, glitch_timeout=10)#For loop check
    valid = val['valid']
    if valid:
        response = val['payload']
        raw_serial = val['full_response']
        error_code = val['rv']
    
    print(val)


**Out [6]:**



.. parsed-literal::

    {'valid': True, 'payload': CWbytearray(b'01'), 'full\_response': CWbytearray(b'00 72 01 01 d4 00'), 'rv': bytearray(b'\x00')}



Like with clock glitching, the scope object can set some typical glitch
settings for you, with the additional requirement of specifying the
transistor to use for glitching (``'both'``, ``'lp'``, and ``'hp'``):


**In [7]:**

.. code:: ipython3

    if scope._is_husky:
        scope.vglitch_setup('hp', default_setup=False)
    else:
        scope.vglitch_setup('both', default_setup=False) # use both transistors


**In [8]:**

.. code:: ipython3

    gc = cw.GlitchController(groups=["success", "reset", "normal"], parameters=["width", "offset", "ext_offset"])
    gc.display_stats()


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

    FloatSlider(value=0.0, continuous_update=False, description='ext_offset setting:', disabled=True, max=10.0, re…



**In [9]:**

.. code:: ipython3

    gc.glitch_plot(plotdots={"success":"+g", "reset":"xr", "normal":None})


**Out [9]:**






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
      <div class="bk-root" id="696b018c-ec9f-4fea-8490-27fc92fbfeb9" data-root-id="1002"></div>
    </div>
    <script type="application/javascript">(function(root) {
      function embed_document(root) {
        var docs_json = {"03af1406-2e78-44ac-901c-221ae650f242":{"defs":[{"extends":null,"module":null,"name":"ReactiveHTML1","overrides":[],"properties":[]},{"extends":null,"module":null,"name":"FlexBox1","overrides":[],"properties":[{"default":"flex-start","kind":null,"name":"align_content"},{"default":"flex-start","kind":null,"name":"align_items"},{"default":"row","kind":null,"name":"flex_direction"},{"default":"wrap","kind":null,"name":"flex_wrap"},{"default":"flex-start","kind":null,"name":"justify_content"}]},{"extends":null,"module":null,"name":"GridStack1","overrides":[],"properties":[{"default":"warn","kind":null,"name":"mode"},{"default":null,"kind":null,"name":"ncols"},{"default":null,"kind":null,"name":"nrows"},{"default":true,"kind":null,"name":"allow_resize"},{"default":true,"kind":null,"name":"allow_drag"},{"default":[],"kind":null,"name":"state"}]},{"extends":null,"module":null,"name":"click1","overrides":[],"properties":[{"default":"","kind":null,"name":"terminal_output"},{"default":"","kind":null,"name":"debug_name"},{"default":0,"kind":null,"name":"clears"}]},{"extends":null,"module":null,"name":"NotificationAreaBase1","overrides":[],"properties":[{"default":"bottom-right","kind":null,"name":"position"},{"default":0,"kind":null,"name":"_clear"}]},{"extends":null,"module":null,"name":"NotificationArea1","overrides":[],"properties":[{"default":[],"kind":null,"name":"notifications"},{"default":"bottom-right","kind":null,"name":"position"},{"default":0,"kind":null,"name":"_clear"},{"default":[{"background":"#ffc107","icon":{"className":"fas fa-exclamation-triangle","color":"white","tagName":"i"},"type":"warning"},{"background":"#007bff","icon":{"className":"fas fa-info-circle","color":"white","tagName":"i"},"type":"info"}],"kind":null,"name":"types"}]},{"extends":null,"module":null,"name":"Notification","overrides":[],"properties":[{"default":null,"kind":null,"name":"background"},{"default":3000,"kind":null,"name":"duration"},{"default":null,"kind":null,"name":"icon"},{"default":"","kind":null,"name":"message"},{"default":null,"kind":null,"name":"notification_type"},{"default":false,"kind":null,"name":"_destroyed"}]},{"extends":null,"module":null,"name":"TemplateActions1","overrides":[],"properties":[{"default":0,"kind":null,"name":"open_modal"},{"default":0,"kind":null,"name":"close_modal"}]},{"extends":null,"module":null,"name":"MaterialTemplateActions1","overrides":[],"properties":[{"default":0,"kind":null,"name":"open_modal"},{"default":0,"kind":null,"name":"close_modal"}]}],"roots":{"references":[{"attributes":{"angle":{"value":0.7853981633974483},"fill_color":{"value":"#ff0000"},"hatch_color":{"value":"#ff0000"},"line_color":{"value":"#ff0000"},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"width"},"y":{"field":"offset"}},"id":"1057","type":"Scatter"},{"attributes":{},"id":"1017","type":"LinearScale"},{"attributes":{},"id":"1044","type":"AllLabels"},{"attributes":{"callback":null,"renderers":[{"id":"1051"},{"id":"1060"}],"tags":["hv_created"],"tooltips":[["width","@{width}"],["offset","@{offset}"]]},"id":"1007","type":"HoverTool"},{"attributes":{},"id":"1040","type":"BasicTickFormatter"},{"attributes":{"angle":{"value":0.7853981633974483},"fill_alpha":{"value":1.0},"fill_color":{"value":"#ff0000"},"hatch_alpha":{"value":1.0},"hatch_color":{"value":"#ff0000"},"hatch_scale":{"value":12.0},"hatch_weight":{"value":1.0},"line_alpha":{"value":1.0},"line_cap":{"value":"butt"},"line_color":{"value":"#ff0000"},"line_dash":{"value":[]},"line_dash_offset":{"value":0},"line_join":{"value":"bevel"},"line_width":{"value":1},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"width"},"y":{"field":"offset"}},"id":"1062","type":"Scatter"},{"attributes":{"fill_alpha":{"value":0.1},"fill_color":{"value":"#007f00"},"hatch_alpha":{"value":0.1},"hatch_color":{"value":"#007f00"},"line_alpha":{"value":0.1},"line_color":{"value":"#007f00"},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"width"},"y":{"field":"offset"}},"id":"1049","type":"Scatter"},{"attributes":{"data":{"offset":{"__ndarray__":"","dtype":"float64","order":"little","shape":[0]},"width":{"__ndarray__":"","dtype":"float64","order":"little","shape":[0]}},"selected":{"id":"1055"},"selection_policy":{"id":"1076"}},"id":"1054","type":"ColumnDataSource"},{"attributes":{},"id":"1043","type":"BasicTickFormatter"},{"attributes":{},"id":"1055","type":"Selection"},{"attributes":{"angle":{"value":0.7853981633974483},"fill_alpha":{"value":0.2},"fill_color":{"value":"#ff0000"},"hatch_alpha":{"value":0.2},"hatch_color":{"value":"#ff0000"},"line_alpha":{"value":0.2},"line_color":{"value":"#ff0000"},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"width"},"y":{"field":"offset"}},"id":"1059","type":"Scatter"},{"attributes":{"data":{"offset":{"__ndarray__":"","dtype":"float64","order":"little","shape":[0]},"width":{"__ndarray__":"","dtype":"float64","order":"little","shape":[0]}},"selected":{"id":"1046"},"selection_policy":{"id":"1074"}},"id":"1045","type":"ColumnDataSource"},{"attributes":{"coordinates":null,"data_source":{"id":"1054"},"glyph":{"id":"1057"},"group":null,"hover_glyph":null,"muted_glyph":{"id":"1059"},"nonselection_glyph":{"id":"1058"},"selection_glyph":{"id":"1062"},"view":{"id":"1061"}},"id":"1060","type":"GlyphRenderer"},{"attributes":{"axis_label":"width","coordinates":null,"formatter":{"id":"1040"},"group":null,"major_label_policy":{"id":"1041"},"ticker":{"id":"1019"}},"id":"1018","type":"LinearAxis"},{"attributes":{"coordinates":null,"group":null,"text_color":"black","text_font_size":"12pt"},"id":"1010","type":"Title"},{"attributes":{"fill_color":{"value":"#007f00"},"hatch_color":{"value":"#007f00"},"line_color":{"value":"#007f00"},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"width"},"y":{"field":"offset"}},"id":"1048","type":"Scatter"},{"attributes":{"below":[{"id":"1018"}],"center":[{"id":"1021"},{"id":"1025"}],"left":[{"id":"1022"}],"margin":[5,5,5,5],"min_border_bottom":10,"min_border_left":10,"min_border_right":10,"min_border_top":10,"output_backend":"webgl","renderers":[{"id":"1051"},{"id":"1060"}],"sizing_mode":"fixed","title":{"id":"1010"},"toolbar":{"id":"1032"},"width":800,"x_range":{"id":"1003"},"x_scale":{"id":"1016"},"y_range":{"id":"1004"},"y_scale":{"id":"1017"}},"id":"1009","subtype":"Figure","type":"Plot"},{"attributes":{"coordinates":null,"data_source":{"id":"1045"},"glyph":{"id":"1048"},"group":null,"hover_glyph":null,"muted_glyph":{"id":"1050"},"nonselection_glyph":{"id":"1049"},"selection_glyph":{"id":"1053"},"view":{"id":"1052"}},"id":"1051","type":"GlyphRenderer"},{"attributes":{},"id":"1016","type":"LinearScale"},{"attributes":{"client_comm_id":"5567c91f14a44727a0607422a6a2b296","comm_id":"f26bbe83ed0f42f888ff35a1cb5a52e9","plot_id":"1002"},"id":"1115","type":"panel.models.comm_manager.CommManager"},{"attributes":{},"id":"1019","type":"BasicTicker"},{"attributes":{},"id":"1076","type":"UnionRenderers"},{"attributes":{"axis":{"id":"1018"},"coordinates":null,"grid_line_color":null,"group":null,"ticker":null},"id":"1021","type":"Grid"},{"attributes":{},"id":"1074","type":"UnionRenderers"},{"attributes":{"axis_label":"offset","coordinates":null,"formatter":{"id":"1043"},"group":null,"major_label_policy":{"id":"1044"},"ticker":{"id":"1023"}},"id":"1022","type":"LinearAxis"},{"attributes":{"axis":{"id":"1022"},"coordinates":null,"dimension":1,"grid_line_color":null,"group":null,"ticker":null},"id":"1025","type":"Grid"},{"attributes":{"fill_alpha":{"value":0.2},"fill_color":{"value":"#007f00"},"hatch_alpha":{"value":0.2},"hatch_color":{"value":"#007f00"},"line_alpha":{"value":0.2},"line_color":{"value":"#007f00"},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"width"},"y":{"field":"offset"}},"id":"1050","type":"Scatter"},{"attributes":{},"id":"1023","type":"BasicTicker"},{"attributes":{"children":[{"id":"1009"}],"height":600,"margin":[0,0,0,0],"name":"Row00811","sizing_mode":"fixed","width":800},"id":"1002","type":"Row"},{"attributes":{},"id":"1028","type":"WheelZoomTool"},{"attributes":{},"id":"1046","type":"Selection"},{"attributes":{},"id":"1027","type":"PanTool"},{"attributes":{},"id":"1026","type":"SaveTool"},{"attributes":{"source":{"id":"1045"}},"id":"1052","type":"CDSView"},{"attributes":{"angle":{"value":0.7853981633974483},"fill_alpha":{"value":0.1},"fill_color":{"value":"#ff0000"},"hatch_alpha":{"value":0.1},"hatch_color":{"value":"#ff0000"},"line_alpha":{"value":0.1},"line_color":{"value":"#ff0000"},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"width"},"y":{"field":"offset"}},"id":"1058","type":"Scatter"},{"attributes":{"overlay":{"id":"1031"}},"id":"1029","type":"BoxZoomTool"},{"attributes":{"tags":[[["width","width",null]],[]]},"id":"1003","type":"Range1d"},{"attributes":{},"id":"1030","type":"ResetTool"},{"attributes":{"tags":[[["offset","offset",null]],{"autorange":false,"invert_yaxis":false}]},"id":"1004","type":"Range1d"},{"attributes":{"bottom_units":"screen","coordinates":null,"fill_alpha":0.5,"fill_color":"lightgrey","group":null,"left_units":"screen","level":"overlay","line_alpha":1.0,"line_color":"black","line_dash":[4,4],"line_width":2,"right_units":"screen","syncable":false,"top_units":"screen"},"id":"1031","type":"BoxAnnotation"},{"attributes":{"angle":{"value":0.0},"fill_alpha":{"value":1.0},"fill_color":{"value":"#007f00"},"hatch_alpha":{"value":1.0},"hatch_color":{"value":"#007f00"},"hatch_scale":{"value":12.0},"hatch_weight":{"value":1.0},"line_alpha":{"value":1.0},"line_cap":{"value":"butt"},"line_color":{"value":"#007f00"},"line_dash":{"value":[]},"line_dash_offset":{"value":0},"line_join":{"value":"bevel"},"line_width":{"value":1},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"width"},"y":{"field":"offset"}},"id":"1053","type":"Scatter"},{"attributes":{"source":{"id":"1054"}},"id":"1061","type":"CDSView"},{"attributes":{"active_drag":{"id":"1027"},"active_scroll":{"id":"1028"},"tools":[{"id":"1007"},{"id":"1026"},{"id":"1027"},{"id":"1028"},{"id":"1029"},{"id":"1030"}]},"id":"1032","type":"Toolbar"},{"attributes":{},"id":"1041","type":"AllLabels"}],"root_ids":["1002","1115"]},"title":"Bokeh Application","version":"2.4.3"}};
        var render_items = [{"docid":"03af1406-2e78-44ac-901c-221ae650f242","root_ids":["1002"],"roots":{"1002":"696b018c-ec9f-4fea-8490-27fc92fbfeb9"}}];
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




**In [10]:**

.. code:: ipython3

    gc.set_range("ext_offset", 0, 150)
    if scope._is_husky:
        gc.set_range("width", 1900, 1901)
        gc.set_range("offset", 2000, 2500)
        gc.set_global_step([50])
        gc.set_step("ext_offset", 1)
    else:
        if PLATFORM=="CWLITEXMEGA":
            gc.set_range("width", 43.5, 47.8)
            gc.set_range("offset", -48, -10)
            #gc.set_range("ext_offset", 7, 10)
            gc.set_range("ext_offset", 30, 45)
            scope.glitch.repeat = 11
        elif PLATFORM == "CWLITEARM":
            #should also work for the bootloader memory dump
            gc.set_range("width", 30.7, 36)
            gc.set_range("offset", -40, -35)
            scope.glitch.repeat = 7
        elif PLATFORM == "CW308_STM32F3":
            #these specific settings seem to work well for some reason
            #also works for the bootloader memory dump
            gc.set_range("ext_offset", 11, 31)
            gc.set_range("width", 47.6, 49.6)
            gc.set_range("offset", -19, -21.5)
            scope.glitch.repeat = 5
            
    gc.set_step("ext_offset", 1)


**Out [10]:**

::


    ---------------------------------------------------------------------------

    AttributeError                            Traceback (most recent call last)

    Cell In[10], line 27
         24         gc.set_range("offset", -19, -21.5)
         25         scope.glitch.repeat = 5
    ---> 27 gc.set_step("ext_offset", 1)


    File ~/chipwhisperer/software/chipwhisperer/common/results/glitch.py:156, in GlitchController.set_step(self, parameter, step)
        154     self.steps[parameter] = step
        155 else:
    --> 156     self.steps[parameter] = [step] * self._num_steps


    AttributeError: 'GlitchController' object has no attribute '_num_steps'



**In [11]:**

.. code:: ipython3

    #disable logging
    cw.set_all_log_levels(cw.logging.CRITICAL)
    
    scope.adc.timeout = 0.1
    successes = 0
    
    reboot_flush()
    
    for glitch_settings in gc.glitch_values():
        scope.glitch.offset = glitch_settings[1]
        scope.glitch.width = glitch_settings[0]
        scope.glitch.ext_offset = glitch_settings[2]
        if scope.adc.state:
            # can detect crash here (fast) before timing out (slow)
            #print("Trigger still high!")
            gc.add("reset")
            reboot_flush()
    
        scope.arm()
        target.simpleserial_write('p', bytearray([0]*5))
        ret = scope.capture()
        scope.io.vglitch_reset()
        
        if ret:
            #print('Timeout - no trigger')
            gc.add("reset")
    
            #Device is slow to boot?
            reboot_flush()
        else:
            val = target.simpleserial_read_witherrors('r', 1, glitch_timeout=10, timeout=50)#For loop check
            if val['valid'] is False:
                gc.add("reset")
            else:
                if val['payload'] == bytearray([1]): #for loop check
                    successes +=1 
                    gc.add("success")
                    print(val)
                    print(val['payload'])
                    print(scope.glitch.width, scope.glitch.offset, scope.glitch.ext_offset)
                    print("🐙", end="")
                else:
                    gc.add("normal")
                        
    #reenable logging
    cw.set_all_log_levels(cw.logging.WARNING)


**Out [11]:**



.. parsed-literal::

    {'valid': True, 'payload': CWbytearray(b'01'), 'full\_response': CWbytearray(b'00 72 01 01 d4 00'), 'rv': bytearray(b'\x00')}
    CWbytearray(b'01')
    32.8125 -39.84375 39
    🐙{'valid': True, 'payload': CWbytearray(b'01'), 'full\_response': CWbytearray(b'00 72 01 01 d4 00'), 'rv': bytearray(b'\x00')}
    CWbytearray(b'01')
    32.8125 -39.0625 39
    🐙{'valid': True, 'payload': CWbytearray(b'01'), 'full\_response': CWbytearray(b'00 72 01 01 d4 00'), 'rv': bytearray(b'\x00')}
    CWbytearray(b'01')
    32.8125 -37.890625 39
    🐙{'valid': True, 'payload': CWbytearray(b'01'), 'full\_response': CWbytearray(b'00 72 01 01 d4 00'), 'rv': bytearray(b'\x00')}
    CWbytearray(b'01')
    33.59375 -39.0625 39
    🐙{'valid': True, 'payload': CWbytearray(b'01'), 'full\_response': CWbytearray(b'00 72 01 01 d4 00'), 'rv': bytearray(b'\x00')}
    CWbytearray(b'01')
    33.59375 -37.890625 39
    🐙{'valid': True, 'payload': CWbytearray(b'01'), 'full\_response': CWbytearray(b'00 72 01 01 d4 00'), 'rv': bytearray(b'\x00')}
    CWbytearray(b'01')
    33.59375 -37.109375 39
    🐙{'valid': True, 'payload': CWbytearray(b'01'), 'full\_response': CWbytearray(b'00 72 01 01 d4 00'), 'rv': bytearray(b'\x00')}
    CWbytearray(b'01')
    33.59375 -35.9375 39
    🐙{'valid': True, 'payload': CWbytearray(b'01'), 'full\_response': CWbytearray(b'00 72 01 01 d4 00'), 'rv': bytearray(b'\x00')}
    CWbytearray(b'01')
    33.59375 -35.15625 39
    🐙{'valid': True, 'payload': CWbytearray(b'01'), 'full\_response': CWbytearray(b'00 72 01 01 d4 00'), 'rv': bytearray(b'\x00')}
    CWbytearray(b'01')
    35.546875 -35.9375 9
    🐙


Let’s see where we needed to target for our glitch to work:


**In [12]:**

.. code:: ipython3

    gc.calc(["width", "offset"], "success_rate")


**Out [12]:**



.. parsed-literal::

    [((39,),
      {'total': 38,
       'success': 8,
       'success_rate': 0.21052631578947367,
       'reset': 15,
       'reset_rate': 0.39473684210526316,
       'normal': 15,
       'normal_rate': 0.39473684210526316}),
     ((9,),
      {'total': 37,
       'success': 1,
       'success_rate': 0.02702702702702703,
       'reset': 2,
       'reset_rate': 0.05405405405405406,
       'normal': 34,
       'normal_rate': 0.918918918918919}),
     ((150,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 11,
       'reset_rate': 0.3055555555555556,
       'normal': 25,
       'normal_rate': 0.6944444444444444}),
     ((149,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 9,
       'reset_rate': 0.25,
       'normal': 27,
       'normal_rate': 0.75}),
     ((148,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 15,
       'reset_rate': 0.4166666666666667,
       'normal': 21,
       'normal_rate': 0.5833333333333334}),
     ((147,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 18,
       'reset_rate': 0.5,
       'normal': 18,
       'normal_rate': 0.5}),
     ((146,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 16,
       'reset_rate': 0.4444444444444444,
       'normal': 20,
       'normal_rate': 0.5555555555555556}),
     ((145,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 19,
       'reset_rate': 0.5277777777777778,
       'normal': 17,
       'normal_rate': 0.4722222222222222}),
     ((144,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 2,
       'reset_rate': 0.05555555555555555,
       'normal': 34,
       'normal_rate': 0.9444444444444444}),
     ((143,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 2,
       'reset_rate': 0.05555555555555555,
       'normal': 34,
       'normal_rate': 0.9444444444444444}),
     ((142,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 11,
       'reset_rate': 0.3055555555555556,
       'normal': 25,
       'normal_rate': 0.6944444444444444}),
     ((141,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 12,
       'reset_rate': 0.3333333333333333,
       'normal': 24,
       'normal_rate': 0.6666666666666666}),
     ((140,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 17,
       'reset_rate': 0.4722222222222222,
       'normal': 19,
       'normal_rate': 0.5277777777777778}),
     ((139,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 18,
       'reset_rate': 0.5,
       'normal': 18,
       'normal_rate': 0.5}),
     ((138,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 15,
       'reset_rate': 0.4166666666666667,
       'normal': 21,
       'normal_rate': 0.5833333333333334}),
     ((137,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 22,
       'reset_rate': 0.6111111111111112,
       'normal': 14,
       'normal_rate': 0.3888888888888889}),
     ((136,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 4,
       'reset_rate': 0.1111111111111111,
       'normal': 32,
       'normal_rate': 0.8888888888888888}),
     ((135,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 6,
       'reset_rate': 0.16666666666666666,
       'normal': 30,
       'normal_rate': 0.8333333333333334}),
     ((134,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 9,
       'reset_rate': 0.25,
       'normal': 27,
       'normal_rate': 0.75}),
     ((133,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 9,
       'reset_rate': 0.25,
       'normal': 27,
       'normal_rate': 0.75}),
     ((132,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 17,
       'reset_rate': 0.4722222222222222,
       'normal': 19,
       'normal_rate': 0.5277777777777778}),
     ((131,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 16,
       'reset_rate': 0.4444444444444444,
       'normal': 20,
       'normal_rate': 0.5555555555555556}),
     ((130,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 16,
       'reset_rate': 0.4444444444444444,
       'normal': 20,
       'normal_rate': 0.5555555555555556}),
     ((129,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 23,
       'reset_rate': 0.6388888888888888,
       'normal': 13,
       'normal_rate': 0.3611111111111111}),
     ((128,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 6,
       'reset_rate': 0.16666666666666666,
       'normal': 30,
       'normal_rate': 0.8333333333333334}),
     ((127,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 7,
       'reset_rate': 0.19444444444444445,
       'normal': 29,
       'normal_rate': 0.8055555555555556}),
     ((126,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 11,
       'reset_rate': 0.3055555555555556,
       'normal': 25,
       'normal_rate': 0.6944444444444444}),
     ((125,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 12,
       'reset_rate': 0.3333333333333333,
       'normal': 24,
       'normal_rate': 0.6666666666666666}),
     ((124,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 15,
       'reset_rate': 0.4166666666666667,
       'normal': 21,
       'normal_rate': 0.5833333333333334}),
     ((123,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 18,
       'reset_rate': 0.5,
       'normal': 18,
       'normal_rate': 0.5}),
     ((122,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 18,
       'reset_rate': 0.5,
       'normal': 18,
       'normal_rate': 0.5}),
     ((121,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 20,
       'reset_rate': 0.5555555555555556,
       'normal': 16,
       'normal_rate': 0.4444444444444444}),
     ((120,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 3,
       'reset_rate': 0.08333333333333333,
       'normal': 33,
       'normal_rate': 0.9166666666666666}),
     ((119,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 6,
       'reset_rate': 0.16666666666666666,
       'normal': 30,
       'normal_rate': 0.8333333333333334}),
     ((118,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 10,
       'reset_rate': 0.2777777777777778,
       'normal': 26,
       'normal_rate': 0.7222222222222222}),
     ((117,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 10,
       'reset_rate': 0.2777777777777778,
       'normal': 26,
       'normal_rate': 0.7222222222222222}),
     ((116,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 17,
       'reset_rate': 0.4722222222222222,
       'normal': 19,
       'normal_rate': 0.5277777777777778}),
     ((115,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 18,
       'reset_rate': 0.5,
       'normal': 18,
       'normal_rate': 0.5}),
     ((114,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 16,
       'reset_rate': 0.4444444444444444,
       'normal': 20,
       'normal_rate': 0.5555555555555556}),
     ((113,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 17,
       'reset_rate': 0.4722222222222222,
       'normal': 19,
       'normal_rate': 0.5277777777777778}),
     ((112,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 3,
       'reset_rate': 0.08333333333333333,
       'normal': 33,
       'normal_rate': 0.9166666666666666}),
     ((111,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 6,
       'reset_rate': 0.16666666666666666,
       'normal': 30,
       'normal_rate': 0.8333333333333334}),
     ((110,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 10,
       'reset_rate': 0.2777777777777778,
       'normal': 26,
       'normal_rate': 0.7222222222222222}),
     ((109,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 10,
       'reset_rate': 0.2777777777777778,
       'normal': 26,
       'normal_rate': 0.7222222222222222}),
     ((108,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 16,
       'reset_rate': 0.4444444444444444,
       'normal': 20,
       'normal_rate': 0.5555555555555556}),
     ((107,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 18,
       'reset_rate': 0.5,
       'normal': 18,
       'normal_rate': 0.5}),
     ((106,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 16,
       'reset_rate': 0.4444444444444444,
       'normal': 20,
       'normal_rate': 0.5555555555555556}),
     ((105,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 19,
       'reset_rate': 0.5277777777777778,
       'normal': 17,
       'normal_rate': 0.4722222222222222}),
     ((104,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 7,
       'reset_rate': 0.19444444444444445,
       'normal': 29,
       'normal_rate': 0.8055555555555556}),
     ((103,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 12,
       'reset_rate': 0.3333333333333333,
       'normal': 24,
       'normal_rate': 0.6666666666666666}),
     ((102,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 11,
       'reset_rate': 0.3055555555555556,
       'normal': 25,
       'normal_rate': 0.6944444444444444}),
     ((101,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 17,
       'reset_rate': 0.4722222222222222,
       'normal': 19,
       'normal_rate': 0.5277777777777778}),
     ((100,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 20,
       'reset_rate': 0.5555555555555556,
       'normal': 16,
       'normal_rate': 0.4444444444444444}),
     ((99,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 8,
       'reset_rate': 0.2222222222222222,
       'normal': 28,
       'normal_rate': 0.7777777777777778}),
     ((98,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 12,
       'reset_rate': 0.3333333333333333,
       'normal': 24,
       'normal_rate': 0.6666666666666666}),
     ((97,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 10,
       'reset_rate': 0.2777777777777778,
       'normal': 26,
       'normal_rate': 0.7222222222222222}),
     ((96,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 14,
       'reset_rate': 0.3888888888888889,
       'normal': 22,
       'normal_rate': 0.6111111111111112}),
     ((95,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 17,
       'reset_rate': 0.4722222222222222,
       'normal': 19,
       'normal_rate': 0.5277777777777778}),
     ((94,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 7,
       'reset_rate': 0.19444444444444445,
       'normal': 29,
       'normal_rate': 0.8055555555555556}),
     ((93,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 11,
       'reset_rate': 0.3055555555555556,
       'normal': 25,
       'normal_rate': 0.6944444444444444}),
     ((92,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 13,
       'reset_rate': 0.3611111111111111,
       'normal': 23,
       'normal_rate': 0.6388888888888888}),
     ((91,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 13,
       'reset_rate': 0.3611111111111111,
       'normal': 23,
       'normal_rate': 0.6388888888888888}),
     ((90,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 17,
       'reset_rate': 0.4722222222222222,
       'normal': 19,
       'normal_rate': 0.5277777777777778}),
     ((89,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 16,
       'reset_rate': 0.4444444444444444,
       'normal': 20,
       'normal_rate': 0.5555555555555556}),
     ((88,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 18,
       'reset_rate': 0.5,
       'normal': 18,
       'normal_rate': 0.5}),
     ((87,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 24,
       'reset_rate': 0.6666666666666666,
       'normal': 12,
       'normal_rate': 0.3333333333333333}),
     ((86,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 7,
       'reset_rate': 0.19444444444444445,
       'normal': 29,
       'normal_rate': 0.8055555555555556}),
     ((85,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 13,
       'reset_rate': 0.3611111111111111,
       'normal': 23,
       'normal_rate': 0.6388888888888888}),
     ((84,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 19,
       'reset_rate': 0.5277777777777778,
       'normal': 17,
       'normal_rate': 0.4722222222222222}),
     ((83,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 14,
       'reset_rate': 0.3888888888888889,
       'normal': 22,
       'normal_rate': 0.6111111111111112}),
     ((82,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 14,
       'reset_rate': 0.3888888888888889,
       'normal': 22,
       'normal_rate': 0.6111111111111112}),
     ((81,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 20,
       'reset_rate': 0.5555555555555556,
       'normal': 16,
       'normal_rate': 0.4444444444444444}),
     ((80,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 22,
       'reset_rate': 0.6111111111111112,
       'normal': 14,
       'normal_rate': 0.3888888888888889}),
     ((79,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 6,
       'reset_rate': 0.16666666666666666,
       'normal': 30,
       'normal_rate': 0.8333333333333334}),
     ((78,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 11,
       'reset_rate': 0.3055555555555556,
       'normal': 25,
       'normal_rate': 0.6944444444444444}),
     ((77,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 12,
       'reset_rate': 0.3333333333333333,
       'normal': 24,
       'normal_rate': 0.6666666666666666}),
     ((76,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 12,
       'reset_rate': 0.3333333333333333,
       'normal': 24,
       'normal_rate': 0.6666666666666666}),
     ((75,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 10,
       'reset_rate': 0.2777777777777778,
       'normal': 26,
       'normal_rate': 0.7222222222222222}),
     ((74,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 5,
       'reset_rate': 0.1388888888888889,
       'normal': 31,
       'normal_rate': 0.8611111111111112}),
     ((73,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 8,
       'reset_rate': 0.2222222222222222,
       'normal': 28,
       'normal_rate': 0.7777777777777778}),
     ((72,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 12,
       'reset_rate': 0.3333333333333333,
       'normal': 24,
       'normal_rate': 0.6666666666666666}),
     ((71,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 11,
       'reset_rate': 0.3055555555555556,
       'normal': 25,
       'normal_rate': 0.6944444444444444}),
     ((70,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 19,
       'reset_rate': 0.5277777777777778,
       'normal': 17,
       'normal_rate': 0.4722222222222222}),
     ((69,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 19,
       'reset_rate': 0.5277777777777778,
       'normal': 17,
       'normal_rate': 0.4722222222222222}),
     ((68,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 2,
       'reset_rate': 0.05555555555555555,
       'normal': 34,
       'normal_rate': 0.9444444444444444}),
     ((67,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 5,
       'reset_rate': 0.1388888888888889,
       'normal': 31,
       'normal_rate': 0.8611111111111112}),
     ((66,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 10,
       'reset_rate': 0.2777777777777778,
       'normal': 26,
       'normal_rate': 0.7222222222222222}),
     ((65,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 11,
       'reset_rate': 0.3055555555555556,
       'normal': 25,
       'normal_rate': 0.6944444444444444}),
     ((64,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 10,
       'reset_rate': 0.2777777777777778,
       'normal': 26,
       'normal_rate': 0.7222222222222222}),
     ((63,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 20,
       'reset_rate': 0.5555555555555556,
       'normal': 16,
       'normal_rate': 0.4444444444444444}),
     ((62,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 22,
       'reset_rate': 0.6111111111111112,
       'normal': 14,
       'normal_rate': 0.3888888888888889}),
     ((61,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 23,
       'reset_rate': 0.6388888888888888,
       'normal': 13,
       'normal_rate': 0.3611111111111111}),
     ((60,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 24,
       'reset_rate': 0.6666666666666666,
       'normal': 12,
       'normal_rate': 0.3333333333333333}),
     ((59,),
      {'total': 37,
       'success': 0,
       'success_rate': 0.0,
       'reset': 11,
       'reset_rate': 0.2972972972972973,
       'normal': 26,
       'normal_rate': 0.7027027027027027}),
     ((58,),
      {'total': 38,
       'success': 0,
       'success_rate': 0.0,
       'reset': 17,
       'reset_rate': 0.4473684210526316,
       'normal': 21,
       'normal_rate': 0.5526315789473685}),
     ((57,),
      {'total': 39,
       'success': 0,
       'success_rate': 0.0,
       'reset': 16,
       'reset_rate': 0.41025641025641024,
       'normal': 23,
       'normal_rate': 0.5897435897435898}),
     ((56,),
      {'total': 38,
       'success': 0,
       'success_rate': 0.0,
       'reset': 24,
       'reset_rate': 0.631578947368421,
       'normal': 14,
       'normal_rate': 0.3684210526315789}),
     ((55,),
      {'total': 40,
       'success': 0,
       'success_rate': 0.0,
       'reset': 25,
       'reset_rate': 0.625,
       'normal': 15,
       'normal_rate': 0.375}),
     ((54,),
      {'total': 45,
       'success': 0,
       'success_rate': 0.0,
       'reset': 12,
       'reset_rate': 0.26666666666666666,
       'normal': 33,
       'normal_rate': 0.7333333333333333}),
     ((53,),
      {'total': 47,
       'success': 0,
       'success_rate': 0.0,
       'reset': 20,
       'reset_rate': 0.425531914893617,
       'normal': 27,
       'normal_rate': 0.574468085106383}),
     ((52,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 23,
       'reset_rate': 0.4791666666666667,
       'normal': 25,
       'normal_rate': 0.5208333333333334}),
     ((51,),
      {'total': 47,
       'success': 0,
       'success_rate': 0.0,
       'reset': 22,
       'reset_rate': 0.46808510638297873,
       'normal': 25,
       'normal_rate': 0.5319148936170213}),
     ((50,),
      {'total': 61,
       'success': 0,
       'success_rate': 0.0,
       'reset': 36,
       'reset_rate': 0.5901639344262295,
       'normal': 25,
       'normal_rate': 0.4098360655737705}),
     ((49,),
      {'total': 46,
       'success': 0,
       'success_rate': 0.0,
       'reset': 28,
       'reset_rate': 0.6086956521739131,
       'normal': 18,
       'normal_rate': 0.391304347826087}),
     ((48,),
      {'total': 49,
       'success': 0,
       'success_rate': 0.0,
       'reset': 23,
       'reset_rate': 0.46938775510204084,
       'normal': 26,
       'normal_rate': 0.5306122448979592}),
     ((47,),
      {'total': 50,
       'success': 0,
       'success_rate': 0.0,
       'reset': 27,
       'reset_rate': 0.54,
       'normal': 23,
       'normal_rate': 0.46}),
     ((46,),
      {'total': 52,
       'success': 0,
       'success_rate': 0.0,
       'reset': 30,
       'reset_rate': 0.5769230769230769,
       'normal': 22,
       'normal_rate': 0.4230769230769231}),
     ((45,),
      {'total': 58,
       'success': 0,
       'success_rate': 0.0,
       'reset': 39,
       'reset_rate': 0.6724137931034483,
       'normal': 19,
       'normal_rate': 0.3275862068965517}),
     ((44,),
      {'total': 43,
       'success': 0,
       'success_rate': 0.0,
       'reset': 23,
       'reset_rate': 0.5348837209302325,
       'normal': 20,
       'normal_rate': 0.46511627906976744}),
     ((43,),
      {'total': 43,
       'success': 0,
       'success_rate': 0.0,
       'reset': 14,
       'reset_rate': 0.32558139534883723,
       'normal': 29,
       'normal_rate': 0.6744186046511628}),
     ((42,),
      {'total': 46,
       'success': 0,
       'success_rate': 0.0,
       'reset': 18,
       'reset_rate': 0.391304347826087,
       'normal': 28,
       'normal_rate': 0.6086956521739131}),
     ((41,),
      {'total': 45,
       'success': 0,
       'success_rate': 0.0,
       'reset': 21,
       'reset_rate': 0.4666666666666667,
       'normal': 24,
       'normal_rate': 0.5333333333333333}),
     ((40,),
      {'total': 55,
       'success': 0,
       'success_rate': 0.0,
       'reset': 29,
       'reset_rate': 0.5272727272727272,
       'normal': 26,
       'normal_rate': 0.4727272727272727}),
     ((38,),
      {'total': 42,
       'success': 0,
       'success_rate': 0.0,
       'reset': 8,
       'reset_rate': 0.19047619047619047,
       'normal': 34,
       'normal_rate': 0.8095238095238095}),
     ((37,),
      {'total': 44,
       'success': 0,
       'success_rate': 0.0,
       'reset': 11,
       'reset_rate': 0.25,
       'normal': 33,
       'normal_rate': 0.75}),
     ((36,),
      {'total': 45,
       'success': 0,
       'success_rate': 0.0,
       'reset': 17,
       'reset_rate': 0.37777777777777777,
       'normal': 28,
       'normal_rate': 0.6222222222222222}),
     ((35,),
      {'total': 47,
       'success': 0,
       'success_rate': 0.0,
       'reset': 20,
       'reset_rate': 0.425531914893617,
       'normal': 27,
       'normal_rate': 0.574468085106383}),
     ((34,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 23,
       'reset_rate': 0.4791666666666667,
       'normal': 25,
       'normal_rate': 0.5208333333333334}),
     ((33,),
      {'total': 45,
       'success': 0,
       'success_rate': 0.0,
       'reset': 21,
       'reset_rate': 0.4666666666666667,
       'normal': 24,
       'normal_rate': 0.5333333333333333}),
     ((32,),
      {'total': 53,
       'success': 0,
       'success_rate': 0.0,
       'reset': 26,
       'reset_rate': 0.49056603773584906,
       'normal': 27,
       'normal_rate': 0.5094339622641509}),
     ((31,),
      {'total': 39,
       'success': 0,
       'success_rate': 0.0,
       'reset': 20,
       'reset_rate': 0.5128205128205128,
       'normal': 19,
       'normal_rate': 0.48717948717948717}),
     ((30,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 3,
       'reset_rate': 0.08333333333333333,
       'normal': 33,
       'normal_rate': 0.9166666666666666}),
     ((29,),
      {'total': 37,
       'success': 0,
       'success_rate': 0.0,
       'reset': 1,
       'reset_rate': 0.02702702702702703,
       'normal': 36,
       'normal_rate': 0.972972972972973}),
     ((28,),
      {'total': 38,
       'success': 0,
       'success_rate': 0.0,
       'reset': 3,
       'reset_rate': 0.07894736842105263,
       'normal': 35,
       'normal_rate': 0.9210526315789473}),
     ((27,),
      {'total': 43,
       'success': 0,
       'success_rate': 0.0,
       'reset': 9,
       'reset_rate': 0.20930232558139536,
       'normal': 34,
       'normal_rate': 0.7906976744186046}),
     ((26,),
      {'total': 46,
       'success': 0,
       'success_rate': 0.0,
       'reset': 17,
       'reset_rate': 0.3695652173913043,
       'normal': 29,
       'normal_rate': 0.6304347826086957}),
     ((25,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 22,
       'reset_rate': 0.4583333333333333,
       'normal': 26,
       'normal_rate': 0.5416666666666666}),
     ((24,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 25,
       'reset_rate': 0.5208333333333334,
       'normal': 23,
       'normal_rate': 0.4791666666666667}),
     ((23,),
      {'total': 46,
       'success': 0,
       'success_rate': 0.0,
       'reset': 23,
       'reset_rate': 0.5,
       'normal': 23,
       'normal_rate': 0.5}),
     ((22,),
      {'total': 53,
       'success': 0,
       'success_rate': 0.0,
       'reset': 27,
       'reset_rate': 0.5094339622641509,
       'normal': 26,
       'normal_rate': 0.49056603773584906}),
     ((21,),
      {'total': 37,
       'success': 0,
       'success_rate': 0.0,
       'reset': 19,
       'reset_rate': 0.5135135135135135,
       'normal': 18,
       'normal_rate': 0.4864864864864865}),
     ((20,),
      {'total': 37,
       'success': 0,
       'success_rate': 0.0,
       'reset': 3,
       'reset_rate': 0.08108108108108109,
       'normal': 34,
       'normal_rate': 0.918918918918919}),
     ((19,),
      {'total': 37,
       'success': 0,
       'success_rate': 0.0,
       'reset': 2,
       'reset_rate': 0.05405405405405406,
       'normal': 35,
       'normal_rate': 0.9459459459459459}),
     ((18,),
      {'total': 39,
       'success': 0,
       'success_rate': 0.0,
       'reset': 4,
       'reset_rate': 0.10256410256410256,
       'normal': 35,
       'normal_rate': 0.8974358974358975}),
     ((17,),
      {'total': 42,
       'success': 0,
       'success_rate': 0.0,
       'reset': 9,
       'reset_rate': 0.21428571428571427,
       'normal': 33,
       'normal_rate': 0.7857142857142857}),
     ((16,),
      {'total': 44,
       'success': 0,
       'success_rate': 0.0,
       'reset': 14,
       'reset_rate': 0.3181818181818182,
       'normal': 30,
       'normal_rate': 0.6818181818181818}),
     ((15,),
      {'total': 46,
       'success': 0,
       'success_rate': 0.0,
       'reset': 18,
       'reset_rate': 0.391304347826087,
       'normal': 28,
       'normal_rate': 0.6086956521739131}),
     ((14,),
      {'total': 46,
       'success': 0,
       'success_rate': 0.0,
       'reset': 21,
       'reset_rate': 0.45652173913043476,
       'normal': 25,
       'normal_rate': 0.5434782608695652}),
     ((13,),
      {'total': 45,
       'success': 0,
       'success_rate': 0.0,
       'reset': 20,
       'reset_rate': 0.4444444444444444,
       'normal': 25,
       'normal_rate': 0.5555555555555556}),
     ((12,),
      {'total': 52,
       'success': 0,
       'success_rate': 0.0,
       'reset': 25,
       'reset_rate': 0.4807692307692308,
       'normal': 27,
       'normal_rate': 0.5192307692307693}),
     ((11,),
      {'total': 37,
       'success': 0,
       'success_rate': 0.0,
       'reset': 18,
       'reset_rate': 0.4864864864864865,
       'normal': 19,
       'normal_rate': 0.5135135135135135}),
     ((10,),
      {'total': 37,
       'success': 0,
       'success_rate': 0.0,
       'reset': 3,
       'reset_rate': 0.08108108108108109,
       'normal': 34,
       'normal_rate': 0.918918918918919}),
     ((8,),
      {'total': 40,
       'success': 0,
       'success_rate': 0.0,
       'reset': 5,
       'reset_rate': 0.125,
       'normal': 35,
       'normal_rate': 0.875}),
     ((7,),
      {'total': 41,
       'success': 0,
       'success_rate': 0.0,
       'reset': 9,
       'reset_rate': 0.21951219512195122,
       'normal': 32,
       'normal_rate': 0.7804878048780488}),
     ((6,),
      {'total': 47,
       'success': 0,
       'success_rate': 0.0,
       'reset': 16,
       'reset_rate': 0.3404255319148936,
       'normal': 31,
       'normal_rate': 0.6595744680851063}),
     ((5,),
      {'total': 49,
       'success': 0,
       'success_rate': 0.0,
       'reset': 24,
       'reset_rate': 0.4897959183673469,
       'normal': 25,
       'normal_rate': 0.5102040816326531}),
     ((4,),
      {'total': 46,
       'success': 0,
       'success_rate': 0.0,
       'reset': 23,
       'reset_rate': 0.5,
       'normal': 23,
       'normal_rate': 0.5}),
     ((3,),
      {'total': 46,
       'success': 0,
       'success_rate': 0.0,
       'reset': 20,
       'reset_rate': 0.43478260869565216,
       'normal': 26,
       'normal_rate': 0.5652173913043478}),
     ((2,),
      {'total': 52,
       'success': 0,
       'success_rate': 0.0,
       'reset': 26,
       'reset_rate': 0.5,
       'normal': 26,
       'normal_rate': 0.5}),
     ((1,),
      {'total': 37,
       'success': 0,
       'success_rate': 0.0,
       'reset': 18,
       'reset_rate': 0.4864864864864865,
       'normal': 19,
       'normal_rate': 0.5135135135135135}),
     ((0,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 4,
       'reset_rate': 0.1111111111111111,
       'normal': 32,
       'normal_rate': 0.8888888888888888})]




**In [13]:**

.. code:: ipython3

    scope.dis()
    target.dis()


**In [14]:**

.. code:: ipython3

    assert successes >= 1
