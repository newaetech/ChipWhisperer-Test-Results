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
    scope.adc.trig\_count                     changed from 10880394                  to 21858679                 
    scope.clock.adc\_src                      changed from clkgen\_x1                 to clkgen\_x4                
    scope.clock.adc\_freq                     changed from 102257434                 to 96000000                 
    scope.clock.adc\_rate                     changed from 102257434.0               to 96000000.0               
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
    .
    avr-gcc (GCC) 5.4.0
    Copyright (C) 2015 Free Software Foundation, Inc.
    This is free software; see the source for copying conditions.  There is NO
    warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
    
    .
    Compiling:
    .
    Compiling:
    -en     simpleserial-glitch.c ...
    Compiling:
    -en     .././simpleserial/simpleserial.c ...
    -en     .././hal/xmega/XMEGA\_AES\_driver.c ...
    .
    .
    Compiling:
    Compiling:
    -e Done!
    -en     .././hal/xmega/uart.c ...
    -en     .././hal/xmega/usart\_driver.c ...
    .
    Compiling:
    -en     .././hal/xmega/xmega\_hal.c ...
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
    Creating load file for Flash: simpleserial-glitch-CWLITEXMEGA.hex
    Creating load file for Flash: simpleserial-glitch-CWLITEXMEGA.bin
    .
    avr-objcopy -O ihex -R .eeprom -R .fuse -R .lock -R .signature simpleserial-glitch-CWLITEXMEGA.elf simpleserial-glitch-CWLITEXMEGA.hex
    Creating load file for EEPROM: simpleserial-glitch-CWLITEXMEGA.eep
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
    + Default target does full rebuild each time.
       text	   data	    bss	    dec	    hex	filename
       2628	      6	     82	   2716	    a9c	simpleserial-glitch-CWLITEXMEGA.elf
    +--------------------------------------------------------
    + Specify buildtarget == allquick == to avoid full rebuild
    + Built for platform CW-Lite XMEGA with:
    +--------------------------------------------------------
    + CRYPTO\_TARGET = NONE
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

    XMEGA Programming flash...
    XMEGA Reading flash...
    Verified flash OK, 2633 bytes




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
      <div class="bk-root" id="d1708ebb-7023-42d3-b160-0395e14a533c" data-root-id="1002"></div>
    </div>
    <script type="application/javascript">(function(root) {
      function embed_document(root) {
        var docs_json = {"92be15ba-4244-4aa1-beaa-0277fdb14f8d":{"defs":[{"extends":null,"module":null,"name":"ReactiveHTML1","overrides":[],"properties":[]},{"extends":null,"module":null,"name":"FlexBox1","overrides":[],"properties":[{"default":"flex-start","kind":null,"name":"align_content"},{"default":"flex-start","kind":null,"name":"align_items"},{"default":"row","kind":null,"name":"flex_direction"},{"default":"wrap","kind":null,"name":"flex_wrap"},{"default":"flex-start","kind":null,"name":"justify_content"}]},{"extends":null,"module":null,"name":"GridStack1","overrides":[],"properties":[{"default":"warn","kind":null,"name":"mode"},{"default":null,"kind":null,"name":"ncols"},{"default":null,"kind":null,"name":"nrows"},{"default":true,"kind":null,"name":"allow_resize"},{"default":true,"kind":null,"name":"allow_drag"},{"default":[],"kind":null,"name":"state"}]},{"extends":null,"module":null,"name":"click1","overrides":[],"properties":[{"default":"","kind":null,"name":"terminal_output"},{"default":"","kind":null,"name":"debug_name"},{"default":0,"kind":null,"name":"clears"}]},{"extends":null,"module":null,"name":"NotificationAreaBase1","overrides":[],"properties":[{"default":"bottom-right","kind":null,"name":"position"},{"default":0,"kind":null,"name":"_clear"}]},{"extends":null,"module":null,"name":"NotificationArea1","overrides":[],"properties":[{"default":[],"kind":null,"name":"notifications"},{"default":"bottom-right","kind":null,"name":"position"},{"default":0,"kind":null,"name":"_clear"},{"default":[{"background":"#ffc107","icon":{"className":"fas fa-exclamation-triangle","color":"white","tagName":"i"},"type":"warning"},{"background":"#007bff","icon":{"className":"fas fa-info-circle","color":"white","tagName":"i"},"type":"info"}],"kind":null,"name":"types"}]},{"extends":null,"module":null,"name":"Notification","overrides":[],"properties":[{"default":null,"kind":null,"name":"background"},{"default":3000,"kind":null,"name":"duration"},{"default":null,"kind":null,"name":"icon"},{"default":"","kind":null,"name":"message"},{"default":null,"kind":null,"name":"notification_type"},{"default":false,"kind":null,"name":"_destroyed"}]},{"extends":null,"module":null,"name":"TemplateActions1","overrides":[],"properties":[{"default":0,"kind":null,"name":"open_modal"},{"default":0,"kind":null,"name":"close_modal"}]},{"extends":null,"module":null,"name":"MaterialTemplateActions1","overrides":[],"properties":[{"default":0,"kind":null,"name":"open_modal"},{"default":0,"kind":null,"name":"close_modal"}]}],"roots":{"references":[{"attributes":{"data":{"offset":{"__ndarray__":"","dtype":"float64","order":"little","shape":[0]},"width":{"__ndarray__":"","dtype":"float64","order":"little","shape":[0]}},"selected":{"id":"1046"},"selection_policy":{"id":"1074"}},"id":"1045","type":"ColumnDataSource"},{"attributes":{"coordinates":null,"data_source":{"id":"1054"},"glyph":{"id":"1057"},"group":null,"hover_glyph":null,"muted_glyph":{"id":"1059"},"nonselection_glyph":{"id":"1058"},"selection_glyph":{"id":"1062"},"view":{"id":"1061"}},"id":"1060","type":"GlyphRenderer"},{"attributes":{"axis_label":"width","coordinates":null,"formatter":{"id":"1040"},"group":null,"major_label_policy":{"id":"1041"},"ticker":{"id":"1019"}},"id":"1018","type":"LinearAxis"},{"attributes":{"coordinates":null,"group":null,"text_color":"black","text_font_size":"12pt"},"id":"1010","type":"Title"},{"attributes":{"below":[{"id":"1018"}],"center":[{"id":"1021"},{"id":"1025"}],"left":[{"id":"1022"}],"margin":[5,5,5,5],"min_border_bottom":10,"min_border_left":10,"min_border_right":10,"min_border_top":10,"output_backend":"webgl","renderers":[{"id":"1051"},{"id":"1060"}],"sizing_mode":"fixed","title":{"id":"1010"},"toolbar":{"id":"1032"},"width":800,"x_range":{"id":"1003"},"x_scale":{"id":"1016"},"y_range":{"id":"1004"},"y_scale":{"id":"1017"}},"id":"1009","subtype":"Figure","type":"Plot"},{"attributes":{"fill_color":{"value":"#007f00"},"hatch_color":{"value":"#007f00"},"line_color":{"value":"#007f00"},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"width"},"y":{"field":"offset"}},"id":"1048","type":"Scatter"},{"attributes":{},"id":"1016","type":"LinearScale"},{"attributes":{"coordinates":null,"data_source":{"id":"1045"},"glyph":{"id":"1048"},"group":null,"hover_glyph":null,"muted_glyph":{"id":"1050"},"nonselection_glyph":{"id":"1049"},"selection_glyph":{"id":"1053"},"view":{"id":"1052"}},"id":"1051","type":"GlyphRenderer"},{"attributes":{},"id":"1017","type":"LinearScale"},{"attributes":{"angle":{"value":0.0},"fill_alpha":{"value":1.0},"fill_color":{"value":"#007f00"},"hatch_alpha":{"value":1.0},"hatch_color":{"value":"#007f00"},"hatch_scale":{"value":12.0},"hatch_weight":{"value":1.0},"line_alpha":{"value":1.0},"line_cap":{"value":"butt"},"line_color":{"value":"#007f00"},"line_dash":{"value":[]},"line_dash_offset":{"value":0},"line_join":{"value":"bevel"},"line_width":{"value":1},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"width"},"y":{"field":"offset"}},"id":"1053","type":"Scatter"},{"attributes":{},"id":"1019","type":"BasicTicker"},{"attributes":{"client_comm_id":"3252c0bc29b9420aa46c1f534579de48","comm_id":"b7ce2f2ef9bb4f7cbc9859d442a2a084","plot_id":"1002"},"id":"1115","type":"panel.models.comm_manager.CommManager"},{"attributes":{"axis":{"id":"1018"},"coordinates":null,"grid_line_color":null,"group":null,"ticker":null},"id":"1021","type":"Grid"},{"attributes":{"axis_label":"offset","coordinates":null,"formatter":{"id":"1043"},"group":null,"major_label_policy":{"id":"1044"},"ticker":{"id":"1023"}},"id":"1022","type":"LinearAxis"},{"attributes":{"children":[{"id":"1009"}],"height":600,"margin":[0,0,0,0],"name":"Row00811","sizing_mode":"fixed","width":800},"id":"1002","type":"Row"},{"attributes":{"axis":{"id":"1022"},"coordinates":null,"dimension":1,"grid_line_color":null,"group":null,"ticker":null},"id":"1025","type":"Grid"},{"attributes":{},"id":"1074","type":"UnionRenderers"},{"attributes":{},"id":"1023","type":"BasicTicker"},{"attributes":{},"id":"1028","type":"WheelZoomTool"},{"attributes":{},"id":"1046","type":"Selection"},{"attributes":{"angle":{"value":0.7853981633974483},"fill_alpha":{"value":0.1},"fill_color":{"value":"#ff0000"},"hatch_alpha":{"value":0.1},"hatch_color":{"value":"#ff0000"},"line_alpha":{"value":0.1},"line_color":{"value":"#ff0000"},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"width"},"y":{"field":"offset"}},"id":"1058","type":"Scatter"},{"attributes":{},"id":"1027","type":"PanTool"},{"attributes":{},"id":"1026","type":"SaveTool"},{"attributes":{"source":{"id":"1045"}},"id":"1052","type":"CDSView"},{"attributes":{"overlay":{"id":"1031"}},"id":"1029","type":"BoxZoomTool"},{"attributes":{"tags":[[["width","width",null]],[]]},"id":"1003","type":"Range1d"},{"attributes":{},"id":"1030","type":"ResetTool"},{"attributes":{},"id":"1076","type":"UnionRenderers"},{"attributes":{"tags":[[["offset","offset",null]],{"autorange":false,"invert_yaxis":false}]},"id":"1004","type":"Range1d"},{"attributes":{"angle":{"value":0.7853981633974483},"fill_alpha":{"value":0.2},"fill_color":{"value":"#ff0000"},"hatch_alpha":{"value":0.2},"hatch_color":{"value":"#ff0000"},"line_alpha":{"value":0.2},"line_color":{"value":"#ff0000"},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"width"},"y":{"field":"offset"}},"id":"1059","type":"Scatter"},{"attributes":{"data":{"offset":{"__ndarray__":"","dtype":"float64","order":"little","shape":[0]},"width":{"__ndarray__":"","dtype":"float64","order":"little","shape":[0]}},"selected":{"id":"1055"},"selection_policy":{"id":"1076"}},"id":"1054","type":"ColumnDataSource"},{"attributes":{"bottom_units":"screen","coordinates":null,"fill_alpha":0.5,"fill_color":"lightgrey","group":null,"left_units":"screen","level":"overlay","line_alpha":1.0,"line_color":"black","line_dash":[4,4],"line_width":2,"right_units":"screen","syncable":false,"top_units":"screen"},"id":"1031","type":"BoxAnnotation"},{"attributes":{"fill_alpha":{"value":0.2},"fill_color":{"value":"#007f00"},"hatch_alpha":{"value":0.2},"hatch_color":{"value":"#007f00"},"line_alpha":{"value":0.2},"line_color":{"value":"#007f00"},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"width"},"y":{"field":"offset"}},"id":"1050","type":"Scatter"},{"attributes":{"source":{"id":"1054"}},"id":"1061","type":"CDSView"},{"attributes":{"active_drag":{"id":"1027"},"active_scroll":{"id":"1028"},"tools":[{"id":"1007"},{"id":"1026"},{"id":"1027"},{"id":"1028"},{"id":"1029"},{"id":"1030"}]},"id":"1032","type":"Toolbar"},{"attributes":{},"id":"1041","type":"AllLabels"},{"attributes":{"angle":{"value":0.7853981633974483},"fill_color":{"value":"#ff0000"},"hatch_color":{"value":"#ff0000"},"line_color":{"value":"#ff0000"},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"width"},"y":{"field":"offset"}},"id":"1057","type":"Scatter"},{"attributes":{},"id":"1044","type":"AllLabels"},{"attributes":{"callback":null,"renderers":[{"id":"1051"},{"id":"1060"}],"tags":["hv_created"],"tooltips":[["width","@{width}"],["offset","@{offset}"]]},"id":"1007","type":"HoverTool"},{"attributes":{},"id":"1040","type":"BasicTickFormatter"},{"attributes":{"angle":{"value":0.7853981633974483},"fill_alpha":{"value":1.0},"fill_color":{"value":"#ff0000"},"hatch_alpha":{"value":1.0},"hatch_color":{"value":"#ff0000"},"hatch_scale":{"value":12.0},"hatch_weight":{"value":1.0},"line_alpha":{"value":1.0},"line_cap":{"value":"butt"},"line_color":{"value":"#ff0000"},"line_dash":{"value":[]},"line_dash_offset":{"value":0},"line_join":{"value":"bevel"},"line_width":{"value":1},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"width"},"y":{"field":"offset"}},"id":"1062","type":"Scatter"},{"attributes":{"fill_alpha":{"value":0.1},"fill_color":{"value":"#007f00"},"hatch_alpha":{"value":0.1},"hatch_color":{"value":"#007f00"},"line_alpha":{"value":0.1},"line_color":{"value":"#007f00"},"marker":{"value":"cross"},"size":{"value":10},"tags":["apply_ranges"],"x":{"field":"width"},"y":{"field":"offset"}},"id":"1049","type":"Scatter"},{"attributes":{},"id":"1043","type":"BasicTickFormatter"},{"attributes":{},"id":"1055","type":"Selection"}],"root_ids":["1002","1115"]},"title":"Bokeh Application","version":"2.4.3"}};
        var render_items = [{"docid":"92be15ba-4244-4aa1-beaa-0277fdb14f8d","root_ids":["1002"],"roots":{"1002":"d1708ebb-7023-42d3-b160-0395e14a533c"}}];
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
    43.359375 -19.921875 44
    🐙




.. parsed-literal::

    WARNING:root:SAM3U Serial buffers OVERRUN - data loss has occurred.



Let’s see where we needed to target for our glitch to work:


**In [12]:**

.. code:: ipython3

    gc.calc(["width", "offset"], "success_rate")


**Out [12]:**



.. parsed-literal::

    [((44,),
      {'total': 213,
       'success': 1,
       'success_rate': 0.004694835680751174,
       'reset': 151,
       'reset_rate': 0.7089201877934272,
       'normal': 61,
       'normal_rate': 0.2863849765258216}),
     ((45,),
      {'total': 208,
       'success': 0,
       'success_rate': 0.0,
       'reset': 149,
       'reset_rate': 0.7163461538461539,
       'normal': 59,
       'normal_rate': 0.28365384615384615}),
     ((43,),
      {'total': 219,
       'success': 0,
       'success_rate': 0.0,
       'reset': 160,
       'reset_rate': 0.730593607305936,
       'normal': 59,
       'normal_rate': 0.2694063926940639}),
     ((42,),
      {'total': 219,
       'success': 0,
       'success_rate': 0.0,
       'reset': 156,
       'reset_rate': 0.7123287671232876,
       'normal': 63,
       'normal_rate': 0.2876712328767123}),
     ((41,),
      {'total': 223,
       'success': 0,
       'success_rate': 0.0,
       'reset': 165,
       'reset_rate': 0.7399103139013453,
       'normal': 58,
       'normal_rate': 0.2600896860986547}),
     ((40,),
      {'total': 205,
       'success': 0,
       'success_rate': 0.0,
       'reset': 147,
       'reset_rate': 0.7170731707317073,
       'normal': 58,
       'normal_rate': 0.28292682926829266}),
     ((39,),
      {'total': 208,
       'success': 0,
       'success_rate': 0.0,
       'reset': 157,
       'reset_rate': 0.7548076923076923,
       'normal': 51,
       'normal_rate': 0.24519230769230768}),
     ((38,),
      {'total': 195,
       'success': 0,
       'success_rate': 0.0,
       'reset': 137,
       'reset_rate': 0.7025641025641025,
       'normal': 58,
       'normal_rate': 0.29743589743589743}),
     ((37,),
      {'total': 195,
       'success': 0,
       'success_rate': 0.0,
       'reset': 142,
       'reset_rate': 0.7282051282051282,
       'normal': 53,
       'normal_rate': 0.2717948717948718}),
     ((36,),
      {'total': 195,
       'success': 0,
       'success_rate': 0.0,
       'reset': 131,
       'reset_rate': 0.6717948717948717,
       'normal': 64,
       'normal_rate': 0.3282051282051282}),
     ((35,),
      {'total': 195,
       'success': 0,
       'success_rate': 0.0,
       'reset': 130,
       'reset_rate': 0.6666666666666666,
       'normal': 65,
       'normal_rate': 0.3333333333333333}),
     ((34,),
      {'total': 195,
       'success': 0,
       'success_rate': 0.0,
       'reset': 131,
       'reset_rate': 0.6717948717948717,
       'normal': 64,
       'normal_rate': 0.3282051282051282}),
     ((33,),
      {'total': 195,
       'success': 0,
       'success_rate': 0.0,
       'reset': 129,
       'reset_rate': 0.6615384615384615,
       'normal': 66,
       'normal_rate': 0.3384615384615385}),
     ((32,),
      {'total': 195,
       'success': 0,
       'success_rate': 0.0,
       'reset': 136,
       'reset_rate': 0.6974358974358974,
       'normal': 59,
       'normal_rate': 0.30256410256410254}),
     ((31,),
      {'total': 207,
       'success': 0,
       'success_rate': 0.0,
       'reset': 151,
       'reset_rate': 0.7294685990338164,
       'normal': 56,
       'normal_rate': 0.27053140096618356}),
     ((30,),
      {'total': 199,
       'success': 0,
       'success_rate': 0.0,
       'reset': 139,
       'reset_rate': 0.6984924623115578,
       'normal': 60,
       'normal_rate': 0.3015075376884422})]




**In [13]:**

.. code:: ipython3

    scope.dis()
    target.dis()


**In [14]:**

.. code:: ipython3

    assert successes >= 1
