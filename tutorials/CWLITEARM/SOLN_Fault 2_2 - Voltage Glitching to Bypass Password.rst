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
    scope.adc.trig\_count                     changed from 31694448                  to 42809867                 
    scope.clock.adc\_src                      changed from clkgen\_x1                 to clkgen\_x4                
    scope.clock.adc\_freq                     changed from 59836864                  to 30484725                 
    scope.clock.adc\_rate                     changed from 59836864.0                to 30484725.0               
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
    arm-none-eabi-gcc (15:9-2019-q4-0ubuntu1) 9.2.1 20191025 (release) [ARM/arm-9-branch revision 277599]
    Copyright (C) 2019 Free Software Foundation, Inc.
    This is free software; see the source for copying conditions.  There is NO
    warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
    
    Welcome to another exciting ChipWhisperer target build!!
    +--------------------------------------------------------
    Size after:
    + Built for platform CW-Lite Arm \(STM32F3\) with:
    + CRYPTO\_TARGET = NONE
       text	   data	    bss	    dec	    hex	filename
       5524	      8	   1368	   6900	   1af4	simpleserial-glitch-CWLITEARM.elf
    + CRYPTO\_OPTIONS = 
    +--------------------------------------------------------




**In [4]:**

.. code:: ipython3

    fw_path = "../../../firmware/mcu/simpleserial-glitch/simpleserial-glitch-{}.hex".format(PLATFORM)
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
        <div id='77943178-e1ed-4485-821c-b6422d603a2f'>
      <div id="c9d68491-1f82-41b8-b345-eaea8d4b9d66" data-root-id="77943178-e1ed-4485-821c-b6422d603a2f" style="display: contents;"></div>
    </div>
    <script type="application/javascript">(function(root) {
      var docs_json = {"3f1a5da8-eb37-43da-a5e8-f04316ebce29":{"version":"3.6.1","title":"Bokeh Application","roots":[{"type":"object","name":"panel.models.browser.BrowserInfo","id":"77943178-e1ed-4485-821c-b6422d603a2f"},{"type":"object","name":"panel.models.comm_manager.CommManager","id":"c3c0b476-c85e-41b4-b76c-b579ea064cf4","attributes":{"plot_id":"77943178-e1ed-4485-821c-b6422d603a2f","comm_id":"f67cad0f946840bc87a85b572ef880f0","client_comm_id":"cff343fa8e5149a1920e803f75292ec6"}}],"defs":[{"type":"model","name":"ReactiveHTML1"},{"type":"model","name":"FlexBox1","properties":[{"name":"align_content","kind":"Any","default":"flex-start"},{"name":"align_items","kind":"Any","default":"flex-start"},{"name":"flex_direction","kind":"Any","default":"row"},{"name":"flex_wrap","kind":"Any","default":"wrap"},{"name":"gap","kind":"Any","default":""},{"name":"justify_content","kind":"Any","default":"flex-start"}]},{"type":"model","name":"FloatPanel1","properties":[{"name":"config","kind":"Any","default":{"type":"map"}},{"name":"contained","kind":"Any","default":true},{"name":"position","kind":"Any","default":"right-top"},{"name":"offsetx","kind":"Any","default":null},{"name":"offsety","kind":"Any","default":null},{"name":"theme","kind":"Any","default":"primary"},{"name":"status","kind":"Any","default":"normalized"}]},{"type":"model","name":"GridStack1","properties":[{"name":"mode","kind":"Any","default":"warn"},{"name":"ncols","kind":"Any","default":null},{"name":"nrows","kind":"Any","default":null},{"name":"allow_resize","kind":"Any","default":true},{"name":"allow_drag","kind":"Any","default":true},{"name":"state","kind":"Any","default":[]}]},{"type":"model","name":"drag1","properties":[{"name":"slider_width","kind":"Any","default":5},{"name":"slider_color","kind":"Any","default":"black"},{"name":"value","kind":"Any","default":50}]},{"type":"model","name":"click1","properties":[{"name":"terminal_output","kind":"Any","default":""},{"name":"debug_name","kind":"Any","default":""},{"name":"clears","kind":"Any","default":0}]},{"type":"model","name":"FastWrapper1","properties":[{"name":"object","kind":"Any","default":null},{"name":"style","kind":"Any","default":null}]},{"type":"model","name":"NotificationAreaBase1","properties":[{"name":"js_events","kind":"Any","default":{"type":"map"}},{"name":"position","kind":"Any","default":"bottom-right"},{"name":"_clear","kind":"Any","default":0}]},{"type":"model","name":"NotificationArea1","properties":[{"name":"js_events","kind":"Any","default":{"type":"map"}},{"name":"notifications","kind":"Any","default":[]},{"name":"position","kind":"Any","default":"bottom-right"},{"name":"_clear","kind":"Any","default":0},{"name":"types","kind":"Any","default":[{"type":"map","entries":[["type","warning"],["background","#ffc107"],["icon",{"type":"map","entries":[["className","fas fa-exclamation-triangle"],["tagName","i"],["color","white"]]}]]},{"type":"map","entries":[["type","info"],["background","#007bff"],["icon",{"type":"map","entries":[["className","fas fa-info-circle"],["tagName","i"],["color","white"]]}]]}]}]},{"type":"model","name":"Notification","properties":[{"name":"background","kind":"Any","default":null},{"name":"duration","kind":"Any","default":3000},{"name":"icon","kind":"Any","default":null},{"name":"message","kind":"Any","default":""},{"name":"notification_type","kind":"Any","default":null},{"name":"_destroyed","kind":"Any","default":false}]},{"type":"model","name":"TemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"BootstrapTemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"TemplateEditor1","properties":[{"name":"layout","kind":"Any","default":[]}]},{"type":"model","name":"MaterialTemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"ReactiveESM1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"JSComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"ReactComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"AnyWidgetComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"request_value1","properties":[{"name":"fill","kind":"Any","default":"none"},{"name":"_synced","kind":"Any","default":null},{"name":"_request_sync","kind":"Any","default":0}]}]}};
      var render_items = [{"docid":"3f1a5da8-eb37-43da-a5e8-f04316ebce29","roots":{"77943178-e1ed-4485-821c-b6422d603a2f":"c9d68491-1f82-41b8-b345-eaea8d4b9d66"},"root_ids":["77943178-e1ed-4485-821c-b6422d603a2f"]}];
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
        <div id='730affec-2306-4426-a01d-2d167dfae889'>
      <div id="cc5bde23-b58d-4278-93a5-c5754f5cc77d" data-root-id="730affec-2306-4426-a01d-2d167dfae889" style="display: contents;"></div>
    </div>
    <script type="application/javascript">(function(root) {
      var docs_json = {"f9674f2c-e519-4673-8888-7608a100600f":{"version":"3.6.1","title":"Bokeh Application","roots":[{"type":"object","name":"Row","id":"730affec-2306-4426-a01d-2d167dfae889","attributes":{"name":"Row00289","stylesheets":["\n:host(.pn-loading):before, .pn-loading:before {\n  background-color: #c3c3c3;\n  mask-size: auto calc(min(50%, 400px));\n  -webkit-mask-size: auto calc(min(50%, 400px));\n}",{"type":"object","name":"ImportedStyleSheet","id":"fb4126a1-27ca-4991-a00e-521b4f0cf85e","attributes":{"url":"https://cdn.holoviz.org/panel/1.5.4/dist/css/loading.css"}},{"type":"object","name":"ImportedStyleSheet","id":"55387fe0-1b47-4056-acb3-20780cbf475e","attributes":{"url":"https://cdn.holoviz.org/panel/1.5.4/dist/css/listpanel.css"}},{"type":"object","name":"ImportedStyleSheet","id":"67fd0565-e3b4-4fc6-964a-9907d6a33c54","attributes":{"url":"https://cdn.holoviz.org/panel/1.5.4/dist/bundled/theme/default.css"}},{"type":"object","name":"ImportedStyleSheet","id":"21e9191f-220a-46c8-9562-a7a6db3ea348","attributes":{"url":"https://cdn.holoviz.org/panel/1.5.4/dist/bundled/theme/native.css"}}],"min_width":800,"margin":0,"sizing_mode":"stretch_width","align":"start","children":[{"type":"object","name":"Spacer","id":"b7cbdeb9-5701-4da4-8ad9-9c064927ce51","attributes":{"name":"HSpacer00293","stylesheets":["\n:host(.pn-loading):before, .pn-loading:before {\n  background-color: #c3c3c3;\n  mask-size: auto calc(min(50%, 400px));\n  -webkit-mask-size: auto calc(min(50%, 400px));\n}",{"id":"fb4126a1-27ca-4991-a00e-521b4f0cf85e"},{"id":"67fd0565-e3b4-4fc6-964a-9907d6a33c54"},{"id":"21e9191f-220a-46c8-9562-a7a6db3ea348"}],"margin":0,"sizing_mode":"stretch_width","align":"start"}},{"type":"object","name":"Figure","id":"17fef56f-00d2-47fe-bb51-266de3a082e7","attributes":{"js_event_callbacks":{"type":"map","entries":[["reset",[{"type":"object","name":"CustomJS","id":"7ca90690-82e1-43f0-874a-8621b50dd930","attributes":{"code":"export default (_, cb_obj) => { cb_obj.origin.hold_render = false }"}}]]]},"subscribed_events":{"type":"set","entries":["rangesupdate","reset"]},"width":800,"margin":[5,10],"sizing_mode":"fixed","align":"start","x_range":{"type":"object","name":"Range1d","id":"b46d57c4-b564-477e-a5b4-b5de9bcdfc84","attributes":{"name":"width","tags":[[["width",null]],[]]}},"y_range":{"type":"object","name":"Range1d","id":"c6621bbd-67b2-48a5-8ecb-b8aaa865e245","attributes":{"name":"offset","tags":[[["offset",null]],{"type":"map","entries":[["invert_yaxis",false],["autorange",false]]}]}},"x_scale":{"type":"object","name":"LinearScale","id":"04f98fa7-1e18-456c-9937-916399587006"},"y_scale":{"type":"object","name":"LinearScale","id":"0aaffc64-1fa1-4b91-be29-d338641535c2"},"title":{"type":"object","name":"Title","id":"8343869c-369d-4321-ae8d-5203b6d43e21","attributes":{"text_color":"black","text_font_size":"12pt"}},"renderers":[{"type":"object","name":"GlyphRenderer","id":"f27c1b21-931b-499d-8da9-3df8506ae914","attributes":{"data_source":{"type":"object","name":"ColumnDataSource","id":"cbd2bb98-7af2-4b52-a2d2-a7960d30aa96","attributes":{"selected":{"type":"object","name":"Selection","id":"fb0ffdbe-e50f-42e8-b771-fdf5189077cb","attributes":{"indices":[],"line_indices":[]}},"selection_policy":{"type":"object","name":"UnionRenderers","id":"1b8c9e3f-4b3b-4aea-8e2d-8ed0802333f7"},"data":{"type":"map","entries":[["width",{"type":"ndarray","array":{"type":"bytes","data":""},"shape":[0],"dtype":"float64","order":"little"}],["offset",{"type":"ndarray","array":{"type":"bytes","data":""},"shape":[0],"dtype":"float64","order":"little"}]]}}},"view":{"type":"object","name":"CDSView","id":"fd46e2b7-84f8-449a-9eea-3df5b4e4c0e1","attributes":{"filter":{"type":"object","name":"AllIndices","id":"00d9ca0e-08cd-4d2f-96b8-9680eb05b3ce"}}},"glyph":{"type":"object","name":"Scatter","id":"a36c01db-c214-4d68-939d-44dbd40e6fd9","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"width"},"y":{"type":"field","field":"offset"},"size":{"type":"value","value":10},"line_color":{"type":"value","value":"#007f00"},"fill_color":{"type":"value","value":"#007f00"},"hatch_color":{"type":"value","value":"#007f00"},"marker":{"type":"value","value":"cross"}}},"selection_glyph":{"type":"object","name":"Scatter","id":"1f7678e2-4cfd-4277-80e6-dcbf40a152f7","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"width"},"y":{"type":"field","field":"offset"},"size":{"type":"value","value":10},"angle":{"type":"value","value":0.0},"line_color":{"type":"value","value":"#007f00"},"line_alpha":{"type":"value","value":1.0},"line_width":{"type":"value","value":1},"line_join":{"type":"value","value":"bevel"},"line_cap":{"type":"value","value":"butt"},"line_dash":{"type":"value","value":[]},"line_dash_offset":{"type":"value","value":0},"fill_color":{"type":"value","value":"#007f00"},"fill_alpha":{"type":"value","value":1.0},"hatch_color":{"type":"value","value":"#007f00"},"hatch_alpha":{"type":"value","value":1.0},"hatch_scale":{"type":"value","value":12.0},"hatch_pattern":{"type":"value","value":null},"hatch_weight":{"type":"value","value":1.0},"marker":{"type":"value","value":"cross"}}},"nonselection_glyph":{"type":"object","name":"Scatter","id":"972df199-f8e0-49ad-9ca4-be57d5b141b3","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"width"},"y":{"type":"field","field":"offset"},"size":{"type":"value","value":10},"line_color":{"type":"value","value":"#007f00"},"line_alpha":{"type":"value","value":0.1},"fill_color":{"type":"value","value":"#007f00"},"fill_alpha":{"type":"value","value":0.1},"hatch_color":{"type":"value","value":"#007f00"},"hatch_alpha":{"type":"value","value":0.1},"marker":{"type":"value","value":"cross"}}},"muted_glyph":{"type":"object","name":"Scatter","id":"7f235b3b-3574-42b7-89cf-2672e6b809be","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"width"},"y":{"type":"field","field":"offset"},"size":{"type":"value","value":10},"line_color":{"type":"value","value":"#007f00"},"line_alpha":{"type":"value","value":0.2},"fill_color":{"type":"value","value":"#007f00"},"fill_alpha":{"type":"value","value":0.2},"hatch_color":{"type":"value","value":"#007f00"},"hatch_alpha":{"type":"value","value":0.2},"marker":{"type":"value","value":"cross"}}}}},{"type":"object","name":"GlyphRenderer","id":"51a6936b-59c5-4ef4-b567-152fbb8c35bc","attributes":{"data_source":{"type":"object","name":"ColumnDataSource","id":"8da25240-7267-427e-b9cd-ffba55deee71","attributes":{"selected":{"type":"object","name":"Selection","id":"c500daab-2020-4c7e-8be1-234faa872272","attributes":{"indices":[],"line_indices":[]}},"selection_policy":{"type":"object","name":"UnionRenderers","id":"e68914bb-8885-41db-a722-e6ab81217d8a"},"data":{"type":"map","entries":[["width",{"type":"ndarray","array":{"type":"bytes","data":""},"shape":[0],"dtype":"float64","order":"little"}],["offset",{"type":"ndarray","array":{"type":"bytes","data":""},"shape":[0],"dtype":"float64","order":"little"}]]}}},"view":{"type":"object","name":"CDSView","id":"db9f4c17-8940-46c9-8156-3a0f13452689","attributes":{"filter":{"type":"object","name":"AllIndices","id":"eecc979e-2cb1-41ac-b9c0-289c54e0a857"}}},"glyph":{"type":"object","name":"Scatter","id":"fdf9b0e1-3697-4f2f-94b7-71f249360c99","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"width"},"y":{"type":"field","field":"offset"},"size":{"type":"value","value":10},"angle":{"type":"value","value":0.7853981633974483},"line_color":{"type":"value","value":"#ff0000"},"fill_color":{"type":"value","value":"#ff0000"},"hatch_color":{"type":"value","value":"#ff0000"},"marker":{"type":"value","value":"cross"}}},"selection_glyph":{"type":"object","name":"Scatter","id":"6ef44116-bc6e-4143-85c1-78a7e743f06f","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"width"},"y":{"type":"field","field":"offset"},"size":{"type":"value","value":10},"angle":{"type":"value","value":0.7853981633974483},"line_color":{"type":"value","value":"#ff0000"},"line_alpha":{"type":"value","value":1.0},"line_width":{"type":"value","value":1},"line_join":{"type":"value","value":"bevel"},"line_cap":{"type":"value","value":"butt"},"line_dash":{"type":"value","value":[]},"line_dash_offset":{"type":"value","value":0},"fill_color":{"type":"value","value":"#ff0000"},"fill_alpha":{"type":"value","value":1.0},"hatch_color":{"type":"value","value":"#ff0000"},"hatch_alpha":{"type":"value","value":1.0},"hatch_scale":{"type":"value","value":12.0},"hatch_pattern":{"type":"value","value":null},"hatch_weight":{"type":"value","value":1.0},"marker":{"type":"value","value":"cross"}}},"nonselection_glyph":{"type":"object","name":"Scatter","id":"e6ac3706-2bf6-48c1-afd4-5058546a1dcc","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"width"},"y":{"type":"field","field":"offset"},"size":{"type":"value","value":10},"angle":{"type":"value","value":0.7853981633974483},"line_color":{"type":"value","value":"#ff0000"},"line_alpha":{"type":"value","value":0.1},"fill_color":{"type":"value","value":"#ff0000"},"fill_alpha":{"type":"value","value":0.1},"hatch_color":{"type":"value","value":"#ff0000"},"hatch_alpha":{"type":"value","value":0.1},"marker":{"type":"value","value":"cross"}}},"muted_glyph":{"type":"object","name":"Scatter","id":"01bba5a7-67fb-4ec0-9434-59ef602b14e1","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"width"},"y":{"type":"field","field":"offset"},"size":{"type":"value","value":10},"angle":{"type":"value","value":0.7853981633974483},"line_color":{"type":"value","value":"#ff0000"},"line_alpha":{"type":"value","value":0.2},"fill_color":{"type":"value","value":"#ff0000"},"fill_alpha":{"type":"value","value":0.2},"hatch_color":{"type":"value","value":"#ff0000"},"hatch_alpha":{"type":"value","value":0.2},"marker":{"type":"value","value":"cross"}}}}}],"toolbar":{"type":"object","name":"Toolbar","id":"8a22d5b2-231d-4f4a-b407-83f2aef301c9","attributes":{"tools":[{"type":"object","name":"WheelZoomTool","id":"e4a689ec-5610-425d-8c8e-3831bf6106b5","attributes":{"tags":["hv_created"],"renderers":"auto","zoom_together":"none"}},{"type":"object","name":"HoverTool","id":"de920cdb-b721-4e3d-8ed5-1194cdab32d8","attributes":{"tags":["hv_created"],"renderers":[{"id":"f27c1b21-931b-499d-8da9-3df8506ae914"},{"id":"51a6936b-59c5-4ef4-b567-152fbb8c35bc"}],"tooltips":[["width","@{width}"],["offset","@{offset}"]]}},{"type":"object","name":"SaveTool","id":"454deaeb-0554-49ce-bb60-f00bc0f08a5c"},{"type":"object","name":"PanTool","id":"c0055304-a61a-47a7-9e26-ac6acbbd3a2f"},{"type":"object","name":"BoxZoomTool","id":"056a29af-1881-4131-b6f9-42d32c6388b2","attributes":{"overlay":{"type":"object","name":"BoxAnnotation","id":"ba9a9906-4f7f-4cc9-bf64-96c0e7e8c421","attributes":{"syncable":false,"line_color":"black","line_alpha":1.0,"line_width":2,"line_dash":[4,4],"fill_color":"lightgrey","fill_alpha":0.5,"level":"overlay","visible":false,"left":{"type":"number","value":"nan"},"right":{"type":"number","value":"nan"},"top":{"type":"number","value":"nan"},"bottom":{"type":"number","value":"nan"},"left_units":"canvas","right_units":"canvas","top_units":"canvas","bottom_units":"canvas","handles":{"type":"object","name":"BoxInteractionHandles","id":"cfffea90-4d6f-43e9-9e1a-a10c37412b52","attributes":{"all":{"type":"object","name":"AreaVisuals","id":"84481f04-c0f6-44dc-a214-f99c7a3dff02","attributes":{"fill_color":"white","hover_fill_color":"lightgray"}}}}}}}},{"type":"object","name":"ResetTool","id":"3133e20d-3cb7-4837-b738-03077c28c09d"}],"active_drag":{"id":"c0055304-a61a-47a7-9e26-ac6acbbd3a2f"},"active_scroll":{"id":"e4a689ec-5610-425d-8c8e-3831bf6106b5"}}},"left":[{"type":"object","name":"LinearAxis","id":"e5084fd5-1ff9-40e7-9189-9f95253fab5f","attributes":{"ticker":{"type":"object","name":"BasicTicker","id":"361a0ce2-de61-4117-b380-463345c69b68","attributes":{"mantissas":[1,2,5]}},"formatter":{"type":"object","name":"BasicTickFormatter","id":"abace8ff-f9d5-4761-8b3a-3ba43f66c6e4"},"axis_label":"offset","major_label_policy":{"type":"object","name":"AllLabels","id":"62b98b1b-bcc6-45b2-9cdb-731c64047859"}}}],"below":[{"type":"object","name":"LinearAxis","id":"17f29081-8a62-4b09-a63b-b2eca9d286cb","attributes":{"ticker":{"type":"object","name":"BasicTicker","id":"265951f7-9d25-4271-bcc3-bf9c2917095a","attributes":{"mantissas":[1,2,5]}},"formatter":{"type":"object","name":"BasicTickFormatter","id":"b2fb2006-4fe6-426f-9088-5fef2b012cf5"},"axis_label":"width","major_label_policy":{"type":"object","name":"AllLabels","id":"a1a7bcb1-5cfe-4c4f-a8d7-7f1ab768542c"}}}],"center":[{"type":"object","name":"Grid","id":"b75482dd-2b19-4d3e-b0c6-122bb93e1373","attributes":{"axis":{"id":"17f29081-8a62-4b09-a63b-b2eca9d286cb"},"grid_line_color":null}},{"type":"object","name":"Grid","id":"be65a1a4-e488-4790-9a19-89efbcccd61b","attributes":{"dimension":1,"axis":{"id":"e5084fd5-1ff9-40e7-9189-9f95253fab5f"},"grid_line_color":null}}],"min_border_top":10,"min_border_bottom":10,"min_border_left":10,"min_border_right":10,"output_backend":"webgl"}},{"type":"object","name":"Spacer","id":"8b5dd07b-f5ef-4f1e-af43-dea3c9428922","attributes":{"name":"HSpacer00294","stylesheets":["\n:host(.pn-loading):before, .pn-loading:before {\n  background-color: #c3c3c3;\n  mask-size: auto calc(min(50%, 400px));\n  -webkit-mask-size: auto calc(min(50%, 400px));\n}",{"id":"fb4126a1-27ca-4991-a00e-521b4f0cf85e"},{"id":"67fd0565-e3b4-4fc6-964a-9907d6a33c54"},{"id":"21e9191f-220a-46c8-9562-a7a6db3ea348"}],"margin":0,"sizing_mode":"stretch_width","align":"start"}}]}},{"type":"object","name":"panel.models.comm_manager.CommManager","id":"7ae2cb99-f428-4d06-b7ae-900704741451","attributes":{"plot_id":"730affec-2306-4426-a01d-2d167dfae889","comm_id":"d357b50f5c6b4d84abd810d7aff62cab","client_comm_id":"167110a0ab1d41579bb06321b091fdc4"}}],"defs":[{"type":"model","name":"ReactiveHTML1"},{"type":"model","name":"FlexBox1","properties":[{"name":"align_content","kind":"Any","default":"flex-start"},{"name":"align_items","kind":"Any","default":"flex-start"},{"name":"flex_direction","kind":"Any","default":"row"},{"name":"flex_wrap","kind":"Any","default":"wrap"},{"name":"gap","kind":"Any","default":""},{"name":"justify_content","kind":"Any","default":"flex-start"}]},{"type":"model","name":"FloatPanel1","properties":[{"name":"config","kind":"Any","default":{"type":"map"}},{"name":"contained","kind":"Any","default":true},{"name":"position","kind":"Any","default":"right-top"},{"name":"offsetx","kind":"Any","default":null},{"name":"offsety","kind":"Any","default":null},{"name":"theme","kind":"Any","default":"primary"},{"name":"status","kind":"Any","default":"normalized"}]},{"type":"model","name":"GridStack1","properties":[{"name":"mode","kind":"Any","default":"warn"},{"name":"ncols","kind":"Any","default":null},{"name":"nrows","kind":"Any","default":null},{"name":"allow_resize","kind":"Any","default":true},{"name":"allow_drag","kind":"Any","default":true},{"name":"state","kind":"Any","default":[]}]},{"type":"model","name":"drag1","properties":[{"name":"slider_width","kind":"Any","default":5},{"name":"slider_color","kind":"Any","default":"black"},{"name":"value","kind":"Any","default":50}]},{"type":"model","name":"click1","properties":[{"name":"terminal_output","kind":"Any","default":""},{"name":"debug_name","kind":"Any","default":""},{"name":"clears","kind":"Any","default":0}]},{"type":"model","name":"FastWrapper1","properties":[{"name":"object","kind":"Any","default":null},{"name":"style","kind":"Any","default":null}]},{"type":"model","name":"NotificationAreaBase1","properties":[{"name":"js_events","kind":"Any","default":{"type":"map"}},{"name":"position","kind":"Any","default":"bottom-right"},{"name":"_clear","kind":"Any","default":0}]},{"type":"model","name":"NotificationArea1","properties":[{"name":"js_events","kind":"Any","default":{"type":"map"}},{"name":"notifications","kind":"Any","default":[]},{"name":"position","kind":"Any","default":"bottom-right"},{"name":"_clear","kind":"Any","default":0},{"name":"types","kind":"Any","default":[{"type":"map","entries":[["type","warning"],["background","#ffc107"],["icon",{"type":"map","entries":[["className","fas fa-exclamation-triangle"],["tagName","i"],["color","white"]]}]]},{"type":"map","entries":[["type","info"],["background","#007bff"],["icon",{"type":"map","entries":[["className","fas fa-info-circle"],["tagName","i"],["color","white"]]}]]}]}]},{"type":"model","name":"Notification","properties":[{"name":"background","kind":"Any","default":null},{"name":"duration","kind":"Any","default":3000},{"name":"icon","kind":"Any","default":null},{"name":"message","kind":"Any","default":""},{"name":"notification_type","kind":"Any","default":null},{"name":"_destroyed","kind":"Any","default":false}]},{"type":"model","name":"TemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"BootstrapTemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"TemplateEditor1","properties":[{"name":"layout","kind":"Any","default":[]}]},{"type":"model","name":"MaterialTemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"ReactiveESM1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"JSComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"ReactComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"AnyWidgetComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"request_value1","properties":[{"name":"fill","kind":"Any","default":"none"},{"name":"_synced","kind":"Any","default":null},{"name":"_request_sync","kind":"Any","default":0}]}]}};
      var render_items = [{"docid":"f9674f2c-e519-4673-8888-7608a100600f","roots":{"730affec-2306-4426-a01d-2d167dfae889":"cc5bde23-b58d-4278-93a5-c5754f5cc77d"},"root_ids":["730affec-2306-4426-a01d-2d167dfae889"]}];
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


    File ~/chipwhisperer/software/chipwhisperer/common/results/glitch.py:193, in GlitchController.set_step(self, parameter, step)
        191     self.steps[parameter] = step
        192 else:
    --> 193     self.steps[parameter] = [step] * self._num_steps


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
    34.765625 -39.84375 39
    🐙{'valid': True, 'payload': CWbytearray(b'01'), 'full\_response': CWbytearray(b'00 72 01 01 d4 00'), 'rv': bytearray(b'\x00')}
    CWbytearray(b'01')
    34.765625 -37.890625 39
    🐙{'valid': True, 'payload': CWbytearray(b'01'), 'full\_response': CWbytearray(b'00 72 01 01 d4 00'), 'rv': bytearray(b'\x00')}
    CWbytearray(b'01')
    34.765625 -37.109375 39
    🐙{'valid': True, 'payload': CWbytearray(b'01'), 'full\_response': CWbytearray(b'00 72 01 01 d4 00'), 'rv': bytearray(b'\x00')}
    CWbytearray(b'01')
    34.765625 -35.15625 39
    🐙{'valid': True, 'payload': CWbytearray(b'01'), 'full\_response': CWbytearray(b'00 72 01 01 d4 00'), 'rv': bytearray(b'\x00')}
    CWbytearray(b'01')
    35.546875 -39.0625 39
    🐙{'valid': True, 'payload': CWbytearray(b'01'), 'full\_response': CWbytearray(b'00 72 01 01 d4 00'), 'rv': bytearray(b'\x00')}
    CWbytearray(b'01')
    35.546875 -37.109375 39
    🐙{'valid': True, 'payload': CWbytearray(b'01'), 'full\_response': CWbytearray(b'00 72 01 01 d4 00'), 'rv': bytearray(b'\x00')}
    CWbytearray(b'01')
    35.546875 -35.9375 39
    🐙{'valid': True, 'payload': CWbytearray(b'01'), 'full\_response': CWbytearray(b'00 72 01 01 d4 00'), 'rv': bytearray(b'\x00')}
    CWbytearray(b'01')
    35.546875 -35.15625 39
    🐙


Let’s see where we needed to target for our glitch to work:


**In [12]:**

.. code:: ipython3

    gc.calc(["width", "offset"], "success_rate")


**Out [12]:**



.. parsed-literal::

    [((39,),
      {'total': 36,
       'success': 8,
       'success_rate': 0.2222222222222222,
       'reset': 4,
       'reset_rate': 0.1111111111111111,
       'normal': 24,
       'normal_rate': 0.6666666666666666}),
     ((150,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((149,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((148,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 6,
       'reset_rate': 0.16666666666666666,
       'normal': 30,
       'normal_rate': 0.8333333333333334}),
     ((147,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 6,
       'reset_rate': 0.16666666666666666,
       'normal': 30,
       'normal_rate': 0.8333333333333334}),
     ((146,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 6,
       'reset_rate': 0.16666666666666666,
       'normal': 30,
       'normal_rate': 0.8333333333333334}),
     ((145,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 10,
       'reset_rate': 0.2777777777777778,
       'normal': 26,
       'normal_rate': 0.7222222222222222}),
     ((144,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((143,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((142,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((141,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((140,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 6,
       'reset_rate': 0.16666666666666666,
       'normal': 30,
       'normal_rate': 0.8333333333333334}),
     ((139,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 7,
       'reset_rate': 0.19444444444444445,
       'normal': 29,
       'normal_rate': 0.8055555555555556}),
     ((138,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 7,
       'reset_rate': 0.19444444444444445,
       'normal': 29,
       'normal_rate': 0.8055555555555556}),
     ((137,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 12,
       'reset_rate': 0.3333333333333333,
       'normal': 24,
       'normal_rate': 0.6666666666666666}),
     ((136,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((135,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((134,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((133,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((132,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 6,
       'reset_rate': 0.16666666666666666,
       'normal': 30,
       'normal_rate': 0.8333333333333334}),
     ((131,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 6,
       'reset_rate': 0.16666666666666666,
       'normal': 30,
       'normal_rate': 0.8333333333333334}),
     ((130,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 6,
       'reset_rate': 0.16666666666666666,
       'normal': 30,
       'normal_rate': 0.8333333333333334}),
     ((129,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 8,
       'reset_rate': 0.2222222222222222,
       'normal': 28,
       'normal_rate': 0.7777777777777778}),
     ((128,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((127,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((126,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((125,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((124,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 7,
       'reset_rate': 0.19444444444444445,
       'normal': 29,
       'normal_rate': 0.8055555555555556}),
     ((123,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 7,
       'reset_rate': 0.19444444444444445,
       'normal': 29,
       'normal_rate': 0.8055555555555556}),
     ((122,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 5,
       'reset_rate': 0.1388888888888889,
       'normal': 31,
       'normal_rate': 0.8611111111111112}),
     ((121,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 12,
       'reset_rate': 0.3333333333333333,
       'normal': 24,
       'normal_rate': 0.6666666666666666}),
     ((120,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((119,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((118,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((117,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((116,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 6,
       'reset_rate': 0.16666666666666666,
       'normal': 30,
       'normal_rate': 0.8333333333333334}),
     ((115,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 6,
       'reset_rate': 0.16666666666666666,
       'normal': 30,
       'normal_rate': 0.8333333333333334}),
     ((114,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 7,
       'reset_rate': 0.19444444444444445,
       'normal': 29,
       'normal_rate': 0.8055555555555556}),
     ((113,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 9,
       'reset_rate': 0.25,
       'normal': 27,
       'normal_rate': 0.75}),
     ((112,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((111,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((110,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((109,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((108,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 6,
       'reset_rate': 0.16666666666666666,
       'normal': 30,
       'normal_rate': 0.8333333333333334}),
     ((107,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 6,
       'reset_rate': 0.16666666666666666,
       'normal': 30,
       'normal_rate': 0.8333333333333334}),
     ((106,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 3,
       'reset_rate': 0.08333333333333333,
       'normal': 33,
       'normal_rate': 0.9166666666666666}),
     ((105,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 10,
       'reset_rate': 0.2777777777777778,
       'normal': 26,
       'normal_rate': 0.7222222222222222}),
     ((104,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((103,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((102,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((101,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 10,
       'reset_rate': 0.2777777777777778,
       'normal': 26,
       'normal_rate': 0.7222222222222222}),
     ((100,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 12,
       'reset_rate': 0.3333333333333333,
       'normal': 24,
       'normal_rate': 0.6666666666666666}),
     ((99,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((98,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((97,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((96,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((95,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 8,
       'reset_rate': 0.2222222222222222,
       'normal': 28,
       'normal_rate': 0.7777777777777778}),
     ((94,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((93,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((92,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 1,
       'reset_rate': 0.027777777777777776,
       'normal': 35,
       'normal_rate': 0.9722222222222222}),
     ((91,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 2,
       'reset_rate': 0.05555555555555555,
       'normal': 34,
       'normal_rate': 0.9444444444444444}),
     ((90,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 7,
       'reset_rate': 0.19444444444444445,
       'normal': 29,
       'normal_rate': 0.8055555555555556}),
     ((89,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 5,
       'reset_rate': 0.1388888888888889,
       'normal': 31,
       'normal_rate': 0.8611111111111112}),
     ((88,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 8,
       'reset_rate': 0.2222222222222222,
       'normal': 28,
       'normal_rate': 0.7777777777777778}),
     ((87,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 12,
       'reset_rate': 0.3333333333333333,
       'normal': 24,
       'normal_rate': 0.6666666666666666}),
     ((86,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((85,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 1,
       'reset_rate': 0.027777777777777776,
       'normal': 35,
       'normal_rate': 0.9722222222222222}),
     ((84,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 7,
       'reset_rate': 0.19444444444444445,
       'normal': 29,
       'normal_rate': 0.8055555555555556}),
     ((83,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 1,
       'reset_rate': 0.027777777777777776,
       'normal': 35,
       'normal_rate': 0.9722222222222222}),
     ((82,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((81,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 12,
       'reset_rate': 0.3333333333333333,
       'normal': 24,
       'normal_rate': 0.6666666666666666}),
     ((80,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 12,
       'reset_rate': 0.3333333333333333,
       'normal': 24,
       'normal_rate': 0.6666666666666666}),
     ((79,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((78,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((77,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 1,
       'reset_rate': 0.027777777777777776,
       'normal': 35,
       'normal_rate': 0.9722222222222222}),
     ((76,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 1,
       'reset_rate': 0.027777777777777776,
       'normal': 35,
       'normal_rate': 0.9722222222222222}),
     ((75,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((74,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((73,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((72,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 1,
       'reset_rate': 0.027777777777777776,
       'normal': 35,
       'normal_rate': 0.9722222222222222}),
     ((71,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 1,
       'reset_rate': 0.027777777777777776,
       'normal': 35,
       'normal_rate': 0.9722222222222222}),
     ((70,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 8,
       'reset_rate': 0.2222222222222222,
       'normal': 28,
       'normal_rate': 0.7777777777777778}),
     ((69,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 10,
       'reset_rate': 0.2777777777777778,
       'normal': 26,
       'normal_rate': 0.7222222222222222}),
     ((68,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((67,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((66,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((65,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((64,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((63,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 9,
       'reset_rate': 0.25,
       'normal': 27,
       'normal_rate': 0.75}),
     ((62,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 10,
       'reset_rate': 0.2777777777777778,
       'normal': 26,
       'normal_rate': 0.7222222222222222}),
     ((61,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 12,
       'reset_rate': 0.3333333333333333,
       'normal': 24,
       'normal_rate': 0.6666666666666666}),
     ((60,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 12,
       'reset_rate': 0.3333333333333333,
       'normal': 24,
       'normal_rate': 0.6666666666666666}),
     ((59,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((58,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 2,
       'reset_rate': 0.05555555555555555,
       'normal': 34,
       'normal_rate': 0.9444444444444444}),
     ((57,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 2,
       'reset_rate': 0.05555555555555555,
       'normal': 34,
       'normal_rate': 0.9444444444444444}),
     ((56,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 12,
       'reset_rate': 0.3333333333333333,
       'normal': 24,
       'normal_rate': 0.6666666666666666}),
     ((55,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 12,
       'reset_rate': 0.3333333333333333,
       'normal': 24,
       'normal_rate': 0.6666666666666666}),
     ((54,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((53,),
      {'total': 37,
       'success': 0,
       'success_rate': 0.0,
       'reset': 1,
       'reset_rate': 0.02702702702702703,
       'normal': 36,
       'normal_rate': 0.972972972972973}),
     ((52,),
      {'total': 37,
       'success': 0,
       'success_rate': 0.0,
       'reset': 2,
       'reset_rate': 0.05405405405405406,
       'normal': 35,
       'normal_rate': 0.9459459459459459}),
     ((51,),
      {'total': 39,
       'success': 0,
       'success_rate': 0.0,
       'reset': 4,
       'reset_rate': 0.10256410256410256,
       'normal': 35,
       'normal_rate': 0.8974358974358975}),
     ((50,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 15,
       'reset_rate': 0.3125,
       'normal': 33,
       'normal_rate': 0.6875}),
     ((49,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 7,
       'reset_rate': 0.19444444444444445,
       'normal': 29,
       'normal_rate': 0.8055555555555556}),
     ((48,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((47,),
      {'total': 40,
       'success': 0,
       'success_rate': 0.0,
       'reset': 4,
       'reset_rate': 0.1,
       'normal': 36,
       'normal_rate': 0.9}),
     ((46,),
      {'total': 42,
       'success': 0,
       'success_rate': 0.0,
       'reset': 10,
       'reset_rate': 0.23809523809523808,
       'normal': 32,
       'normal_rate': 0.7619047619047619}),
     ((45,),
      {'total': 49,
       'success': 0,
       'success_rate': 0.0,
       'reset': 19,
       'reset_rate': 0.3877551020408163,
       'normal': 30,
       'normal_rate': 0.6122448979591837}),
     ((44,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 5,
       'reset_rate': 0.1388888888888889,
       'normal': 31,
       'normal_rate': 0.8611111111111112}),
     ((43,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((42,),
      {'total': 37,
       'success': 0,
       'success_rate': 0.0,
       'reset': 1,
       'reset_rate': 0.02702702702702703,
       'normal': 36,
       'normal_rate': 0.972972972972973}),
     ((41,),
      {'total': 38,
       'success': 0,
       'success_rate': 0.0,
       'reset': 3,
       'reset_rate': 0.07894736842105263,
       'normal': 35,
       'normal_rate': 0.9210526315789473}),
     ((40,),
      {'total': 47,
       'success': 0,
       'success_rate': 0.0,
       'reset': 13,
       'reset_rate': 0.2765957446808511,
       'normal': 34,
       'normal_rate': 0.723404255319149}),
     ((38,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((37,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((36,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((35,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((34,),
      {'total': 39,
       'success': 0,
       'success_rate': 0.0,
       'reset': 3,
       'reset_rate': 0.07692307692307693,
       'normal': 36,
       'normal_rate': 0.9230769230769231}),
     ((33,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 3,
       'reset_rate': 0.08333333333333333,
       'normal': 33,
       'normal_rate': 0.9166666666666666}),
     ((32,),
      {'total': 46,
       'success': 0,
       'success_rate': 0.0,
       'reset': 10,
       'reset_rate': 0.21739130434782608,
       'normal': 36,
       'normal_rate': 0.782608695652174}),
     ((31,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 10,
       'reset_rate': 0.2777777777777778,
       'normal': 26,
       'normal_rate': 0.7222222222222222}),
     ((30,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((29,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((28,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((27,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((26,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((25,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((24,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((23,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((22,),
      {'total': 46,
       'success': 0,
       'success_rate': 0.0,
       'reset': 10,
       'reset_rate': 0.21739130434782608,
       'normal': 36,
       'normal_rate': 0.782608695652174}),
     ((21,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 10,
       'reset_rate': 0.2777777777777778,
       'normal': 26,
       'normal_rate': 0.7222222222222222}),
     ((20,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((19,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((18,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((17,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((16,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((15,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((14,),
      {'total': 37,
       'success': 0,
       'success_rate': 0.0,
       'reset': 2,
       'reset_rate': 0.05405405405405406,
       'normal': 35,
       'normal_rate': 0.9459459459459459}),
     ((13,),
      {'total': 37,
       'success': 0,
       'success_rate': 0.0,
       'reset': 3,
       'reset_rate': 0.08108108108108109,
       'normal': 34,
       'normal_rate': 0.918918918918919}),
     ((12,),
      {'total': 45,
       'success': 0,
       'success_rate': 0.0,
       'reset': 10,
       'reset_rate': 0.2222222222222222,
       'normal': 35,
       'normal_rate': 0.7777777777777778}),
     ((11,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 9,
       'reset_rate': 0.25,
       'normal': 27,
       'normal_rate': 0.75}),
     ((10,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((9,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((8,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((7,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((6,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((5,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0}),
     ((4,),
      {'total': 37,
       'success': 0,
       'success_rate': 0.0,
       'reset': 1,
       'reset_rate': 0.02702702702702703,
       'normal': 36,
       'normal_rate': 0.972972972972973}),
     ((3,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 1,
       'reset_rate': 0.027777777777777776,
       'normal': 35,
       'normal_rate': 0.9722222222222222}),
     ((2,),
      {'total': 47,
       'success': 0,
       'success_rate': 0.0,
       'reset': 11,
       'reset_rate': 0.23404255319148937,
       'normal': 36,
       'normal_rate': 0.7659574468085106}),
     ((1,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 11,
       'reset_rate': 0.3055555555555556,
       'normal': 25,
       'normal_rate': 0.6944444444444444}),
     ((0,),
      {'total': 36,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 36,
       'normal_rate': 1.0})]




**In [13]:**

.. code:: ipython3

    scope.dis()
    target.dis()


**In [14]:**

.. code:: ipython3

    assert successes >= 1
