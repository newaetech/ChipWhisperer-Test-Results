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
    
    allowable_exceptions = None
    VERSION = 'HARDWARE'
    CRYPTO_TARGET = 'TINYAES128C'



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
        scope = cw.scope(hw_location=(5, 7))
    
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
        scope = cw.scope(hw_location=(5, 7))
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
    scope.adc.trig\_count                     changed from 11243949                  to 22691022                 
    scope.clock.adc\_src                      changed from clkgen\_x1                 to clkgen\_x4                
    scope.clock.adc\_freq                     changed from 29538459                  to 27848922                 
    scope.clock.adc\_rate                     changed from 29538459.0                to 27848922.0               
    scope.clock.clkgen\_div                   changed from 1                         to 26                       
    scope.clock.clkgen\_freq                  changed from 192000000.0               to 7384615.384615385        
    scope.io.tio1                            changed from serial\_tx                 to serial\_rx                
    scope.io.tio2                            changed from serial\_rx                 to serial\_tx                
    scope.io.hs2                             changed from None                      to clkgen                   
    scope.glitch.mmcm\_locked                 changed from True                      to False                    




**In [3]:**

.. code:: bash

    %%bash -s "$PLATFORM" "$SS_VER"
    cd ../../../firmware/mcu/simpleserial-glitch
    make PLATFORM=$1 CRYPTO_TARGET=NONE SS_VER=$2 -j


**Out [3]:**



.. parsed-literal::

    SS\_VER set to SS\_VER\_2\_1
    SS\_VER set to SS\_VER\_2\_1
    .
    Welcome to another exciting ChipWhisperer target build!!
    +--------------------------------------------------------
    Size after:
    arm-none-eabi-gcc (15:9-2019-q4-0ubuntu1) 9.2.1 20191025 (release) [ARM/arm-9-branch revision 277599]
    Copyright (C) 2019 Free Software Foundation, Inc.
    This is free software; see the source for copying conditions.  There is NO
    warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
    
    + Built for platform CW308T: STM32F4 Target with:
       text	   data	    bss	    dec	    hex	filename
       4708	   1084	   1344	   7136	   1be0	simpleserial-glitch-CW308\_STM32F4.elf
    + CRYPTO\_TARGET = NONE
    + CRYPTO\_OPTIONS = 
    +--------------------------------------------------------




**In [4]:**

.. code:: ipython3

    fw_path = "../../../firmware/mcu/simpleserial-glitch/simpleserial-glitch-{}.hex".format(PLATFORM)
    cw.program_target(scope, prog, fw_path)
    if SS_VER == 'SS_VER_2_1':
        target.reset_comms()


**Out [4]:**



.. parsed-literal::

    Detected known STMF32: STM32F40xxx/41xxx
    Extended erase (0x44), this can take ten seconds or more
    Attempting to program 5791 bytes at 0x8000000
    STM32F Programming flash...
    STM32F Reading flash...
    Verified flash OK, 5791 bytes




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

    scope.clock.adc\_freq                     changed from 27848922                  to 29538459                 
    scope.clock.adc\_rate                     changed from 27848922.0                to 29538459.0               



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
        <script type="esms-options">{"shimMode": true}</script><style>*[data-root-id],
    *[data-root-id] > * {
      box-sizing: border-box;
      font-family: var(--jp-ui-font-family);
      font-size: var(--jp-ui-font-size1);
      color: var(--vscode-editor-foreground, var(--jp-ui-font-color1));
    }
    
    /* Override VSCode background color */
    .cell-output-ipywidget-background:has(
        > .cell-output-ipywidget-background > .lm-Widget > *[data-root-id]
      ),
    .cell-output-ipywidget-background:has(> .lm-Widget > *[data-root-id]) {
      background-color: transparent !important;
    }
    </style>
    </div>







.. raw:: html

    <div class="data_html">
        <div id='dea595c5-fa08-45bb-ab3c-c8153dd416a6'>
      <div id="fc201104-f92f-4e58-97ba-fc386829622e" data-root-id="dea595c5-fa08-45bb-ab3c-c8153dd416a6" style="display: contents;"></div>
    </div>
    <script type="application/javascript">(function(root) {
      var docs_json = {"f0b65cc6-cd7c-4969-991a-b67f9e5a27df":{"version":"3.6.1","title":"Bokeh Application","roots":[{"type":"object","name":"panel.models.browser.BrowserInfo","id":"dea595c5-fa08-45bb-ab3c-c8153dd416a6"},{"type":"object","name":"panel.models.comm_manager.CommManager","id":"e9c2c71e-1e40-43a4-9fd0-1afe5618d97e","attributes":{"plot_id":"dea595c5-fa08-45bb-ab3c-c8153dd416a6","comm_id":"8fcae88f71374c69ab557e1ffa912965","client_comm_id":"be0af565526543059b11541a714ee388"}}],"defs":[{"type":"model","name":"ReactiveHTML1"},{"type":"model","name":"FlexBox1","properties":[{"name":"align_content","kind":"Any","default":"flex-start"},{"name":"align_items","kind":"Any","default":"flex-start"},{"name":"flex_direction","kind":"Any","default":"row"},{"name":"flex_wrap","kind":"Any","default":"wrap"},{"name":"gap","kind":"Any","default":""},{"name":"justify_content","kind":"Any","default":"flex-start"}]},{"type":"model","name":"FloatPanel1","properties":[{"name":"config","kind":"Any","default":{"type":"map"}},{"name":"contained","kind":"Any","default":true},{"name":"position","kind":"Any","default":"right-top"},{"name":"offsetx","kind":"Any","default":null},{"name":"offsety","kind":"Any","default":null},{"name":"theme","kind":"Any","default":"primary"},{"name":"status","kind":"Any","default":"normalized"}]},{"type":"model","name":"GridStack1","properties":[{"name":"mode","kind":"Any","default":"warn"},{"name":"ncols","kind":"Any","default":null},{"name":"nrows","kind":"Any","default":null},{"name":"allow_resize","kind":"Any","default":true},{"name":"allow_drag","kind":"Any","default":true},{"name":"state","kind":"Any","default":[]}]},{"type":"model","name":"drag1","properties":[{"name":"slider_width","kind":"Any","default":5},{"name":"slider_color","kind":"Any","default":"black"},{"name":"value","kind":"Any","default":50}]},{"type":"model","name":"click1","properties":[{"name":"terminal_output","kind":"Any","default":""},{"name":"debug_name","kind":"Any","default":""},{"name":"clears","kind":"Any","default":0}]},{"type":"model","name":"FastWrapper1","properties":[{"name":"object","kind":"Any","default":null},{"name":"style","kind":"Any","default":null}]},{"type":"model","name":"NotificationAreaBase1","properties":[{"name":"js_events","kind":"Any","default":{"type":"map"}},{"name":"position","kind":"Any","default":"bottom-right"},{"name":"_clear","kind":"Any","default":0}]},{"type":"model","name":"NotificationArea1","properties":[{"name":"js_events","kind":"Any","default":{"type":"map"}},{"name":"notifications","kind":"Any","default":[]},{"name":"position","kind":"Any","default":"bottom-right"},{"name":"_clear","kind":"Any","default":0},{"name":"types","kind":"Any","default":[{"type":"map","entries":[["type","warning"],["background","#ffc107"],["icon",{"type":"map","entries":[["className","fas fa-exclamation-triangle"],["tagName","i"],["color","white"]]}]]},{"type":"map","entries":[["type","info"],["background","#007bff"],["icon",{"type":"map","entries":[["className","fas fa-info-circle"],["tagName","i"],["color","white"]]}]]}]}]},{"type":"model","name":"Notification","properties":[{"name":"background","kind":"Any","default":null},{"name":"duration","kind":"Any","default":3000},{"name":"icon","kind":"Any","default":null},{"name":"message","kind":"Any","default":""},{"name":"notification_type","kind":"Any","default":null},{"name":"_destroyed","kind":"Any","default":false}]},{"type":"model","name":"TemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"BootstrapTemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"TemplateEditor1","properties":[{"name":"layout","kind":"Any","default":[]}]},{"type":"model","name":"MaterialTemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"ReactiveESM1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"JSComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"ReactComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"AnyWidgetComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"request_value1","properties":[{"name":"fill","kind":"Any","default":"none"},{"name":"_synced","kind":"Any","default":null},{"name":"_request_sync","kind":"Any","default":0}]}]}};
      var render_items = [{"docid":"f0b65cc6-cd7c-4969-991a-b67f9e5a27df","roots":{"dea595c5-fa08-45bb-ab3c-c8153dd416a6":"fc201104-f92f-4e58-97ba-fc386829622e"},"root_ids":["dea595c5-fa08-45bb-ab3c-c8153dd416a6"]}];
      var docs = Object.values(docs_json)
      if (!docs) {
        return
      }
      const py_version = docs[0].version.replace('rc', '-rc.').replace('.dev', '-dev.')
      async function embed_document(root) {
        var Bokeh = get_bokeh(root)
        await Bokeh.embed.embed_items_notebook(docs_json, render_items);
        for (const render_item of render_items) {
          for (const root_id of render_item.root_ids) {
    	const id_el = document.getElementById(root_id)
    	if (id_el.children.length && id_el.children[0].hasAttribute('data-root-id')) {
    	  const root_el = id_el.children[0]
    	  root_el.id = root_el.id + '-rendered'
    	  for (const child of root_el.children) {
                // Ensure JupyterLab does not capture keyboard shortcuts
                // see: https://jupyterlab.readthedocs.io/en/4.1.x/extension/notebook.html#keyboard-interaction-model
    	    child.setAttribute('data-lm-suppress-shortcuts', 'true')
    	  }
    	}
          }
        }
      }
      function get_bokeh(root) {
        if (root.Bokeh === undefined) {
          return null
        } else if (root.Bokeh.version !== py_version) {
          if (root.Bokeh.versions === undefined || !root.Bokeh.versions.has(py_version)) {
    	return null
          }
          return root.Bokeh.versions.get(py_version);
        } else if (root.Bokeh.version === py_version) {
          return root.Bokeh
        }
        return null
      }
      function is_loaded(root) {
        var Bokeh = get_bokeh(root)
        return (Bokeh != null && Bokeh.Panel !== undefined)
      }
      if (is_loaded(root)) {
        embed_document(root);
      } else {
        var attempts = 0;
        var timer = setInterval(function(root) {
          if (is_loaded(root)) {
            clearInterval(timer);
            embed_document(root);
          } else if (document.readyState == "complete") {
            attempts++;
            if (attempts > 200) {
              clearInterval(timer);
    	  var Bokeh = get_bokeh(root)
    	  if (Bokeh == null || Bokeh.Panel == null) {
                console.warn("Panel: ERROR: Unable to run Panel code because Bokeh or Panel library is missing");
    	  } else {
    	    console.warn("Panel: WARNING: Attempting to render but not all required libraries could be resolved.")
    	    embed_document(root)
    	  }
            }
          }
        }, 25, root)
      }
    })(window);</script>
    </div>






.. raw:: html

    <div class="data_html">
        <div id='ee3c55df-4579-4dc5-a19e-76b912f5bd6b'>
      <div id="a5f9b397-b315-41ce-98f8-c0e48cba85b6" data-root-id="ee3c55df-4579-4dc5-a19e-76b912f5bd6b" style="display: contents;"></div>
    </div>
    <script type="application/javascript">(function(root) {
      var docs_json = {"8dafdbb1-78dd-4417-989e-e181df20de42":{"version":"3.6.1","title":"Bokeh Application","roots":[{"type":"object","name":"Row","id":"ee3c55df-4579-4dc5-a19e-76b912f5bd6b","attributes":{"name":"Row00289","stylesheets":["\n:host(.pn-loading):before, .pn-loading:before {\n  background-color: #c3c3c3;\n  mask-size: auto calc(min(50%, 400px));\n  -webkit-mask-size: auto calc(min(50%, 400px));\n}",{"type":"object","name":"ImportedStyleSheet","id":"62d63671-1ce5-42f5-9379-a7440d2c09de","attributes":{"url":"https://cdn.holoviz.org/panel/1.5.4/dist/css/loading.css"}},{"type":"object","name":"ImportedStyleSheet","id":"ea6587f1-781c-4a85-95f5-be9f0c25f051","attributes":{"url":"https://cdn.holoviz.org/panel/1.5.4/dist/css/listpanel.css"}},{"type":"object","name":"ImportedStyleSheet","id":"2b84b27e-60da-4a5e-8a21-294876f16dd3","attributes":{"url":"https://cdn.holoviz.org/panel/1.5.4/dist/bundled/theme/default.css"}},{"type":"object","name":"ImportedStyleSheet","id":"41a9636a-5160-4c88-91a0-579621af680c","attributes":{"url":"https://cdn.holoviz.org/panel/1.5.4/dist/bundled/theme/native.css"}}],"min_width":800,"margin":0,"sizing_mode":"stretch_width","align":"start","children":[{"type":"object","name":"Spacer","id":"23c13fba-4dff-4d44-a533-fdc10e41f9d8","attributes":{"name":"HSpacer00293","stylesheets":["\n:host(.pn-loading):before, .pn-loading:before {\n  background-color: #c3c3c3;\n  mask-size: auto calc(min(50%, 400px));\n  -webkit-mask-size: auto calc(min(50%, 400px));\n}",{"id":"62d63671-1ce5-42f5-9379-a7440d2c09de"},{"id":"2b84b27e-60da-4a5e-8a21-294876f16dd3"},{"id":"41a9636a-5160-4c88-91a0-579621af680c"}],"margin":0,"sizing_mode":"stretch_width","align":"start"}},{"type":"object","name":"Figure","id":"c54d2620-192d-4bf5-bb7a-65d3fba522c4","attributes":{"js_event_callbacks":{"type":"map","entries":[["reset",[{"type":"object","name":"CustomJS","id":"aa194bdc-0e1c-4551-b78d-982ea7ff01df","attributes":{"code":"export default (_, cb_obj) => { cb_obj.origin.hold_render = false }"}}]]]},"subscribed_events":{"type":"set","entries":["reset","rangesupdate"]},"width":800,"margin":[5,10],"sizing_mode":"fixed","align":"start","x_range":{"type":"object","name":"Range1d","id":"449419b2-c37c-486e-96ed-4ce607408c9b","attributes":{"name":"ext_offset","tags":[[["ext_offset",null]],[]]}},"y_range":{"type":"object","name":"Range1d","id":"b9dc0abe-6182-41a3-a826-77dc50936984","attributes":{"name":"offset","tags":[[["offset",null]],{"type":"map","entries":[["invert_yaxis",false],["autorange",false]]}]}},"x_scale":{"type":"object","name":"LinearScale","id":"393b7ee7-38b0-4e3d-87b1-32f42de4bcf5"},"y_scale":{"type":"object","name":"LinearScale","id":"bf6ece33-eef9-40f3-8054-c064bcc2fd04"},"title":{"type":"object","name":"Title","id":"7f0b4317-3adb-428b-bae1-2b26b1632c73","attributes":{"text_color":"black","text_font_size":"12pt"}},"renderers":[{"type":"object","name":"GlyphRenderer","id":"f2e77214-aa6e-42b3-a39e-cc86998bb106","attributes":{"data_source":{"type":"object","name":"ColumnDataSource","id":"c5db7817-8494-4782-b2bd-0c398839dda4","attributes":{"selected":{"type":"object","name":"Selection","id":"426125cc-2ce4-4210-ba8e-4e573128c818","attributes":{"indices":[],"line_indices":[]}},"selection_policy":{"type":"object","name":"UnionRenderers","id":"c81e4e48-6ded-4eae-a5df-cab2f9479391"},"data":{"type":"map","entries":[["ext_offset",{"type":"ndarray","array":{"type":"bytes","data":""},"shape":[0],"dtype":"float64","order":"little"}],["offset",{"type":"ndarray","array":{"type":"bytes","data":""},"shape":[0],"dtype":"float64","order":"little"}]]}}},"view":{"type":"object","name":"CDSView","id":"f2629fe7-e9b1-4d01-9a2d-325282660e11","attributes":{"filter":{"type":"object","name":"AllIndices","id":"01d50abd-2ff4-42ec-9179-64dddd68337e"}}},"glyph":{"type":"object","name":"Scatter","id":"5af85ff6-ae46-4f03-a9de-3758edd2829f","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"ext_offset"},"y":{"type":"field","field":"offset"},"size":{"type":"value","value":10},"line_color":{"type":"value","value":"#007f00"},"fill_color":{"type":"value","value":"#007f00"},"hatch_color":{"type":"value","value":"#007f00"},"marker":{"type":"value","value":"cross"}}},"selection_glyph":{"type":"object","name":"Scatter","id":"582d07ba-6a2e-498c-90e7-417c62359fa5","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"ext_offset"},"y":{"type":"field","field":"offset"},"size":{"type":"value","value":10},"angle":{"type":"value","value":0.0},"line_color":{"type":"value","value":"#007f00"},"line_alpha":{"type":"value","value":1.0},"line_width":{"type":"value","value":1},"line_join":{"type":"value","value":"bevel"},"line_cap":{"type":"value","value":"butt"},"line_dash":{"type":"value","value":[]},"line_dash_offset":{"type":"value","value":0},"fill_color":{"type":"value","value":"#007f00"},"fill_alpha":{"type":"value","value":1.0},"hatch_color":{"type":"value","value":"#007f00"},"hatch_alpha":{"type":"value","value":1.0},"hatch_scale":{"type":"value","value":12.0},"hatch_pattern":{"type":"value","value":null},"hatch_weight":{"type":"value","value":1.0},"marker":{"type":"value","value":"cross"}}},"nonselection_glyph":{"type":"object","name":"Scatter","id":"f34305e0-b96b-47e0-9a67-785a0c4696d3","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"ext_offset"},"y":{"type":"field","field":"offset"},"size":{"type":"value","value":10},"line_color":{"type":"value","value":"#007f00"},"line_alpha":{"type":"value","value":0.1},"fill_color":{"type":"value","value":"#007f00"},"fill_alpha":{"type":"value","value":0.1},"hatch_color":{"type":"value","value":"#007f00"},"hatch_alpha":{"type":"value","value":0.1},"marker":{"type":"value","value":"cross"}}},"muted_glyph":{"type":"object","name":"Scatter","id":"0bfc9bc2-047f-473b-b632-b08c03635edb","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"ext_offset"},"y":{"type":"field","field":"offset"},"size":{"type":"value","value":10},"line_color":{"type":"value","value":"#007f00"},"line_alpha":{"type":"value","value":0.2},"fill_color":{"type":"value","value":"#007f00"},"fill_alpha":{"type":"value","value":0.2},"hatch_color":{"type":"value","value":"#007f00"},"hatch_alpha":{"type":"value","value":0.2},"marker":{"type":"value","value":"cross"}}}}},{"type":"object","name":"GlyphRenderer","id":"f0e8301e-1a3d-4ae4-8047-d96deac39f15","attributes":{"data_source":{"type":"object","name":"ColumnDataSource","id":"777a4405-f697-4bfb-9353-ccbfce173970","attributes":{"selected":{"type":"object","name":"Selection","id":"7fc558e3-b124-469a-a274-fd09431e438f","attributes":{"indices":[],"line_indices":[]}},"selection_policy":{"type":"object","name":"UnionRenderers","id":"68585a89-c509-42dc-ab38-510c2ed5f895"},"data":{"type":"map","entries":[["ext_offset",{"type":"ndarray","array":{"type":"bytes","data":""},"shape":[0],"dtype":"float64","order":"little"}],["offset",{"type":"ndarray","array":{"type":"bytes","data":""},"shape":[0],"dtype":"float64","order":"little"}]]}}},"view":{"type":"object","name":"CDSView","id":"a39dc267-adb5-43c4-80bd-2cf20e634437","attributes":{"filter":{"type":"object","name":"AllIndices","id":"ca90b09b-186e-4758-9fa4-2b92585788c2"}}},"glyph":{"type":"object","name":"Scatter","id":"dd2b1a91-e8a4-49a2-93f4-65b7061cbdbb","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"ext_offset"},"y":{"type":"field","field":"offset"},"size":{"type":"value","value":10},"angle":{"type":"value","value":0.7853981633974483},"line_color":{"type":"value","value":"#ff0000"},"fill_color":{"type":"value","value":"#ff0000"},"hatch_color":{"type":"value","value":"#ff0000"},"marker":{"type":"value","value":"cross"}}},"selection_glyph":{"type":"object","name":"Scatter","id":"6ea02d8a-aea7-4efc-bf70-7980438b028c","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"ext_offset"},"y":{"type":"field","field":"offset"},"size":{"type":"value","value":10},"angle":{"type":"value","value":0.7853981633974483},"line_color":{"type":"value","value":"#ff0000"},"line_alpha":{"type":"value","value":1.0},"line_width":{"type":"value","value":1},"line_join":{"type":"value","value":"bevel"},"line_cap":{"type":"value","value":"butt"},"line_dash":{"type":"value","value":[]},"line_dash_offset":{"type":"value","value":0},"fill_color":{"type":"value","value":"#ff0000"},"fill_alpha":{"type":"value","value":1.0},"hatch_color":{"type":"value","value":"#ff0000"},"hatch_alpha":{"type":"value","value":1.0},"hatch_scale":{"type":"value","value":12.0},"hatch_pattern":{"type":"value","value":null},"hatch_weight":{"type":"value","value":1.0},"marker":{"type":"value","value":"cross"}}},"nonselection_glyph":{"type":"object","name":"Scatter","id":"6327489f-a2d8-47f3-a43b-d48a7ef8dcb0","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"ext_offset"},"y":{"type":"field","field":"offset"},"size":{"type":"value","value":10},"angle":{"type":"value","value":0.7853981633974483},"line_color":{"type":"value","value":"#ff0000"},"line_alpha":{"type":"value","value":0.1},"fill_color":{"type":"value","value":"#ff0000"},"fill_alpha":{"type":"value","value":0.1},"hatch_color":{"type":"value","value":"#ff0000"},"hatch_alpha":{"type":"value","value":0.1},"marker":{"type":"value","value":"cross"}}},"muted_glyph":{"type":"object","name":"Scatter","id":"21788c26-71c9-42bb-b438-df94a1966a31","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"ext_offset"},"y":{"type":"field","field":"offset"},"size":{"type":"value","value":10},"angle":{"type":"value","value":0.7853981633974483},"line_color":{"type":"value","value":"#ff0000"},"line_alpha":{"type":"value","value":0.2},"fill_color":{"type":"value","value":"#ff0000"},"fill_alpha":{"type":"value","value":0.2},"hatch_color":{"type":"value","value":"#ff0000"},"hatch_alpha":{"type":"value","value":0.2},"marker":{"type":"value","value":"cross"}}}}}],"toolbar":{"type":"object","name":"Toolbar","id":"138b9f14-0e48-4d60-aefe-2098695ff461","attributes":{"tools":[{"type":"object","name":"WheelZoomTool","id":"3dbd2cfe-9ce7-46b9-a274-38f5f401473e","attributes":{"tags":["hv_created"],"renderers":"auto","zoom_together":"none"}},{"type":"object","name":"HoverTool","id":"d56e7b06-9b32-4e59-902e-aef5c810f05e","attributes":{"tags":["hv_created"],"renderers":[{"id":"f2e77214-aa6e-42b3-a39e-cc86998bb106"},{"id":"f0e8301e-1a3d-4ae4-8047-d96deac39f15"}],"tooltips":[["ext_offset","@{ext_offset}"],["offset","@{offset}"]]}},{"type":"object","name":"SaveTool","id":"1f7954ee-315b-458b-9f69-cf5bd7ecc20c"},{"type":"object","name":"PanTool","id":"7184cecf-4508-4baf-b508-79b70fb272ec"},{"type":"object","name":"BoxZoomTool","id":"1162ad76-0077-4d53-a29f-70f92af53c2b","attributes":{"overlay":{"type":"object","name":"BoxAnnotation","id":"87781f3c-7f75-4380-bf8a-86e77d55c20b","attributes":{"syncable":false,"line_color":"black","line_alpha":1.0,"line_width":2,"line_dash":[4,4],"fill_color":"lightgrey","fill_alpha":0.5,"level":"overlay","visible":false,"left":{"type":"number","value":"nan"},"right":{"type":"number","value":"nan"},"top":{"type":"number","value":"nan"},"bottom":{"type":"number","value":"nan"},"left_units":"canvas","right_units":"canvas","top_units":"canvas","bottom_units":"canvas","handles":{"type":"object","name":"BoxInteractionHandles","id":"c21a648c-ed9d-4521-8d35-edd75ac03a28","attributes":{"all":{"type":"object","name":"AreaVisuals","id":"ea1dd4b2-e1c5-4283-8b4e-30cdbc785a4c","attributes":{"fill_color":"white","hover_fill_color":"lightgray"}}}}}}}},{"type":"object","name":"ResetTool","id":"11f6c165-77dc-42fb-8395-9f873b7e05d4"}],"active_drag":{"id":"7184cecf-4508-4baf-b508-79b70fb272ec"},"active_scroll":{"id":"3dbd2cfe-9ce7-46b9-a274-38f5f401473e"}}},"left":[{"type":"object","name":"LinearAxis","id":"9793b60c-c108-4853-9cd9-580e1e30eb6c","attributes":{"ticker":{"type":"object","name":"BasicTicker","id":"88256d78-78c4-4cc3-bf50-bbccd867e837","attributes":{"mantissas":[1,2,5]}},"formatter":{"type":"object","name":"BasicTickFormatter","id":"96e3fd29-67b7-4f17-8a96-6d225a7f3544"},"axis_label":"offset","major_label_policy":{"type":"object","name":"AllLabels","id":"89ac44a3-13f1-46a5-9e4a-c4f3f5e18bf6"}}}],"below":[{"type":"object","name":"LinearAxis","id":"c4d9f2b6-b135-4761-825f-1629854e8d91","attributes":{"ticker":{"type":"object","name":"BasicTicker","id":"19d10aba-f120-460b-a062-925ba9556983","attributes":{"mantissas":[1,2,5]}},"formatter":{"type":"object","name":"BasicTickFormatter","id":"264f54cc-6f70-4d79-8eca-457010a4f83a"},"axis_label":"ext_offset","major_label_policy":{"type":"object","name":"AllLabels","id":"751d1896-7338-4c34-b735-0a4dd74ebd47"}}}],"center":[{"type":"object","name":"Grid","id":"41b2de0d-633d-4165-8f28-52d5a7253c5c","attributes":{"axis":{"id":"c4d9f2b6-b135-4761-825f-1629854e8d91"},"grid_line_color":null}},{"type":"object","name":"Grid","id":"e757d025-c541-4652-902b-9d92e9fb4264","attributes":{"dimension":1,"axis":{"id":"9793b60c-c108-4853-9cd9-580e1e30eb6c"},"grid_line_color":null}}],"min_border_top":10,"min_border_bottom":10,"min_border_left":10,"min_border_right":10,"output_backend":"webgl"}},{"type":"object","name":"Spacer","id":"2c9291f0-4385-4fda-88da-a0914531d9b9","attributes":{"name":"HSpacer00294","stylesheets":["\n:host(.pn-loading):before, .pn-loading:before {\n  background-color: #c3c3c3;\n  mask-size: auto calc(min(50%, 400px));\n  -webkit-mask-size: auto calc(min(50%, 400px));\n}",{"id":"62d63671-1ce5-42f5-9379-a7440d2c09de"},{"id":"2b84b27e-60da-4a5e-8a21-294876f16dd3"},{"id":"41a9636a-5160-4c88-91a0-579621af680c"}],"margin":0,"sizing_mode":"stretch_width","align":"start"}}]}},{"type":"object","name":"panel.models.comm_manager.CommManager","id":"7b81428c-a167-4441-852a-f156669635f4","attributes":{"plot_id":"ee3c55df-4579-4dc5-a19e-76b912f5bd6b","comm_id":"84f8b1dd092047d7aa265e1be95d3569","client_comm_id":"e74270fd9d874b8e91e79580b8e1e99b"}}],"defs":[{"type":"model","name":"ReactiveHTML1"},{"type":"model","name":"FlexBox1","properties":[{"name":"align_content","kind":"Any","default":"flex-start"},{"name":"align_items","kind":"Any","default":"flex-start"},{"name":"flex_direction","kind":"Any","default":"row"},{"name":"flex_wrap","kind":"Any","default":"wrap"},{"name":"gap","kind":"Any","default":""},{"name":"justify_content","kind":"Any","default":"flex-start"}]},{"type":"model","name":"FloatPanel1","properties":[{"name":"config","kind":"Any","default":{"type":"map"}},{"name":"contained","kind":"Any","default":true},{"name":"position","kind":"Any","default":"right-top"},{"name":"offsetx","kind":"Any","default":null},{"name":"offsety","kind":"Any","default":null},{"name":"theme","kind":"Any","default":"primary"},{"name":"status","kind":"Any","default":"normalized"}]},{"type":"model","name":"GridStack1","properties":[{"name":"mode","kind":"Any","default":"warn"},{"name":"ncols","kind":"Any","default":null},{"name":"nrows","kind":"Any","default":null},{"name":"allow_resize","kind":"Any","default":true},{"name":"allow_drag","kind":"Any","default":true},{"name":"state","kind":"Any","default":[]}]},{"type":"model","name":"drag1","properties":[{"name":"slider_width","kind":"Any","default":5},{"name":"slider_color","kind":"Any","default":"black"},{"name":"value","kind":"Any","default":50}]},{"type":"model","name":"click1","properties":[{"name":"terminal_output","kind":"Any","default":""},{"name":"debug_name","kind":"Any","default":""},{"name":"clears","kind":"Any","default":0}]},{"type":"model","name":"FastWrapper1","properties":[{"name":"object","kind":"Any","default":null},{"name":"style","kind":"Any","default":null}]},{"type":"model","name":"NotificationAreaBase1","properties":[{"name":"js_events","kind":"Any","default":{"type":"map"}},{"name":"position","kind":"Any","default":"bottom-right"},{"name":"_clear","kind":"Any","default":0}]},{"type":"model","name":"NotificationArea1","properties":[{"name":"js_events","kind":"Any","default":{"type":"map"}},{"name":"notifications","kind":"Any","default":[]},{"name":"position","kind":"Any","default":"bottom-right"},{"name":"_clear","kind":"Any","default":0},{"name":"types","kind":"Any","default":[{"type":"map","entries":[["type","warning"],["background","#ffc107"],["icon",{"type":"map","entries":[["className","fas fa-exclamation-triangle"],["tagName","i"],["color","white"]]}]]},{"type":"map","entries":[["type","info"],["background","#007bff"],["icon",{"type":"map","entries":[["className","fas fa-info-circle"],["tagName","i"],["color","white"]]}]]}]}]},{"type":"model","name":"Notification","properties":[{"name":"background","kind":"Any","default":null},{"name":"duration","kind":"Any","default":3000},{"name":"icon","kind":"Any","default":null},{"name":"message","kind":"Any","default":""},{"name":"notification_type","kind":"Any","default":null},{"name":"_destroyed","kind":"Any","default":false}]},{"type":"model","name":"TemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"BootstrapTemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"TemplateEditor1","properties":[{"name":"layout","kind":"Any","default":[]}]},{"type":"model","name":"MaterialTemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"ReactiveESM1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"JSComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"ReactComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"AnyWidgetComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"request_value1","properties":[{"name":"fill","kind":"Any","default":"none"},{"name":"_synced","kind":"Any","default":null},{"name":"_request_sync","kind":"Any","default":0}]}]}};
      var render_items = [{"docid":"8dafdbb1-78dd-4417-989e-e181df20de42","roots":{"ee3c55df-4579-4dc5-a19e-76b912f5bd6b":"a5f9b397-b315-41ce-98f8-c0e48cba85b6"},"root_ids":["ee3c55df-4579-4dc5-a19e-76b912f5bd6b"]}];
      var docs = Object.values(docs_json)
      if (!docs) {
        return
      }
      const py_version = docs[0].version.replace('rc', '-rc.').replace('.dev', '-dev.')
      async function embed_document(root) {
        var Bokeh = get_bokeh(root)
        await Bokeh.embed.embed_items_notebook(docs_json, render_items);
        for (const render_item of render_items) {
          for (const root_id of render_item.root_ids) {
    	const id_el = document.getElementById(root_id)
    	if (id_el.children.length && id_el.children[0].hasAttribute('data-root-id')) {
    	  const root_el = id_el.children[0]
    	  root_el.id = root_el.id + '-rendered'
    	  for (const child of root_el.children) {
                // Ensure JupyterLab does not capture keyboard shortcuts
                // see: https://jupyterlab.readthedocs.io/en/4.1.x/extension/notebook.html#keyboard-interaction-model
    	    child.setAttribute('data-lm-suppress-shortcuts', 'true')
    	  }
    	}
          }
        }
      }
      function get_bokeh(root) {
        if (root.Bokeh === undefined) {
          return null
        } else if (root.Bokeh.version !== py_version) {
          if (root.Bokeh.versions === undefined || !root.Bokeh.versions.has(py_version)) {
    	return null
          }
          return root.Bokeh.versions.get(py_version);
        } else if (root.Bokeh.version === py_version) {
          return root.Bokeh
        }
        return null
      }
      function is_loaded(root) {
        var Bokeh = get_bokeh(root)
        return (Bokeh != null && Bokeh.Panel !== undefined)
      }
      if (is_loaded(root)) {
        embed_document(root);
      } else {
        var attempts = 0;
        var timer = setInterval(function(root) {
          if (is_loaded(root)) {
            clearInterval(timer);
            embed_document(root);
          } else if (document.readyState == "complete") {
            attempts++;
            if (attempts > 200) {
              clearInterval(timer);
    	  var Bokeh = get_bokeh(root)
    	  if (Bokeh == null || Bokeh.Panel == null) {
                console.warn("Panel: ERROR: Unable to run Panel code because Bokeh or Panel library is missing");
    	  } else {
    	    console.warn("Panel: WARNING: Attempting to render but not all required libraries could be resolved.")
    	    embed_document(root)
    	  }
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

