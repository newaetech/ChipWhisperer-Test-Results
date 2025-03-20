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
    scope.adc.trig\_count                     changed from 10986339                  to 22026832                 
    scope.clock.adc\_src                      changed from clkgen\_x1                 to clkgen\_x4                
    scope.clock.adc\_freq                     changed from 128000003                 to 29947734                 
    scope.clock.adc\_rate                     changed from 128000003.0               to 29947734.0               
    scope.clock.clkgen\_div                   changed from 1                         to 26                       
    scope.clock.clkgen\_freq                  changed from 192000000.0               to 7384615.384615385        
    scope.io.tio1                            changed from serial\_tx                 to serial\_rx                
    scope.io.tio2                            changed from serial\_rx                 to serial\_tx                
    scope.io.hs2                             changed from None                      to clkgen                   
    scope.io.tio\_states                      changed from (1, 0, 0, 0)              to (1, 1, 0, 0)             
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
    avr-gcc (GCC) 5.4.0
    Copyright (C) 2015 Free Software Foundation, Inc.
    This is free software; see the source for copying conditions.  There is NO
    warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
    
    Size after:
    +--------------------------------------------------------
    + Built for platform CW-Lite XMEGA with:
       text	   data	    bss	    dec	    hex	filename
       2792	      6	     82	   2880	    b40	simpleserial-glitch-CWLITEXMEGA.elf
    + CRYPTO\_TARGET = NONE
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

    XMEGA Programming flash...
    XMEGA Reading flash...
    Verified flash OK, 2797 bytes




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
        <div id='d4396a0a-6b6b-4e39-9f04-6979f673f0cb'>
      <div id="be56475b-0c57-4362-b247-f26415b2d8c9" data-root-id="d4396a0a-6b6b-4e39-9f04-6979f673f0cb" style="display: contents;"></div>
    </div>
    <script type="application/javascript">(function(root) {
      var docs_json = {"6f99793f-1375-40c1-a225-9debd6af8444":{"version":"3.6.1","title":"Bokeh Application","roots":[{"type":"object","name":"panel.models.browser.BrowserInfo","id":"d4396a0a-6b6b-4e39-9f04-6979f673f0cb"},{"type":"object","name":"panel.models.comm_manager.CommManager","id":"54ca5204-13cb-4a9e-b7de-ce3413f79386","attributes":{"plot_id":"d4396a0a-6b6b-4e39-9f04-6979f673f0cb","comm_id":"50108a43475540fe945030f0f000d22c","client_comm_id":"3fbe46081c804b40b80b79be19c7a364"}}],"defs":[{"type":"model","name":"ReactiveHTML1"},{"type":"model","name":"FlexBox1","properties":[{"name":"align_content","kind":"Any","default":"flex-start"},{"name":"align_items","kind":"Any","default":"flex-start"},{"name":"flex_direction","kind":"Any","default":"row"},{"name":"flex_wrap","kind":"Any","default":"wrap"},{"name":"gap","kind":"Any","default":""},{"name":"justify_content","kind":"Any","default":"flex-start"}]},{"type":"model","name":"FloatPanel1","properties":[{"name":"config","kind":"Any","default":{"type":"map"}},{"name":"contained","kind":"Any","default":true},{"name":"position","kind":"Any","default":"right-top"},{"name":"offsetx","kind":"Any","default":null},{"name":"offsety","kind":"Any","default":null},{"name":"theme","kind":"Any","default":"primary"},{"name":"status","kind":"Any","default":"normalized"}]},{"type":"model","name":"GridStack1","properties":[{"name":"mode","kind":"Any","default":"warn"},{"name":"ncols","kind":"Any","default":null},{"name":"nrows","kind":"Any","default":null},{"name":"allow_resize","kind":"Any","default":true},{"name":"allow_drag","kind":"Any","default":true},{"name":"state","kind":"Any","default":[]}]},{"type":"model","name":"drag1","properties":[{"name":"slider_width","kind":"Any","default":5},{"name":"slider_color","kind":"Any","default":"black"},{"name":"value","kind":"Any","default":50}]},{"type":"model","name":"click1","properties":[{"name":"terminal_output","kind":"Any","default":""},{"name":"debug_name","kind":"Any","default":""},{"name":"clears","kind":"Any","default":0}]},{"type":"model","name":"FastWrapper1","properties":[{"name":"object","kind":"Any","default":null},{"name":"style","kind":"Any","default":null}]},{"type":"model","name":"NotificationAreaBase1","properties":[{"name":"js_events","kind":"Any","default":{"type":"map"}},{"name":"position","kind":"Any","default":"bottom-right"},{"name":"_clear","kind":"Any","default":0}]},{"type":"model","name":"NotificationArea1","properties":[{"name":"js_events","kind":"Any","default":{"type":"map"}},{"name":"notifications","kind":"Any","default":[]},{"name":"position","kind":"Any","default":"bottom-right"},{"name":"_clear","kind":"Any","default":0},{"name":"types","kind":"Any","default":[{"type":"map","entries":[["type","warning"],["background","#ffc107"],["icon",{"type":"map","entries":[["className","fas fa-exclamation-triangle"],["tagName","i"],["color","white"]]}]]},{"type":"map","entries":[["type","info"],["background","#007bff"],["icon",{"type":"map","entries":[["className","fas fa-info-circle"],["tagName","i"],["color","white"]]}]]}]}]},{"type":"model","name":"Notification","properties":[{"name":"background","kind":"Any","default":null},{"name":"duration","kind":"Any","default":3000},{"name":"icon","kind":"Any","default":null},{"name":"message","kind":"Any","default":""},{"name":"notification_type","kind":"Any","default":null},{"name":"_destroyed","kind":"Any","default":false}]},{"type":"model","name":"TemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"BootstrapTemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"TemplateEditor1","properties":[{"name":"layout","kind":"Any","default":[]}]},{"type":"model","name":"MaterialTemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"ReactiveESM1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"JSComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"ReactComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"AnyWidgetComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"request_value1","properties":[{"name":"fill","kind":"Any","default":"none"},{"name":"_synced","kind":"Any","default":null},{"name":"_request_sync","kind":"Any","default":0}]}]}};
      var render_items = [{"docid":"6f99793f-1375-40c1-a225-9debd6af8444","roots":{"d4396a0a-6b6b-4e39-9f04-6979f673f0cb":"be56475b-0c57-4362-b247-f26415b2d8c9"},"root_ids":["d4396a0a-6b6b-4e39-9f04-6979f673f0cb"]}];
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
        <div id='50316ee1-33cd-4a95-9a9c-9785882f142b'>
      <div id="dbfac4c2-c145-4f10-80c0-4a1772a36382" data-root-id="50316ee1-33cd-4a95-9a9c-9785882f142b" style="display: contents;"></div>
    </div>
    <script type="application/javascript">(function(root) {
      var docs_json = {"5546b00a-ee8f-4445-ac9a-342c3d901e5d":{"version":"3.6.1","title":"Bokeh Application","roots":[{"type":"object","name":"Row","id":"50316ee1-33cd-4a95-9a9c-9785882f142b","attributes":{"name":"Row00289","stylesheets":["\n:host(.pn-loading):before, .pn-loading:before {\n  background-color: #c3c3c3;\n  mask-size: auto calc(min(50%, 400px));\n  -webkit-mask-size: auto calc(min(50%, 400px));\n}",{"type":"object","name":"ImportedStyleSheet","id":"9f3a593b-3ecf-4592-b9de-43a598f5de60","attributes":{"url":"https://cdn.holoviz.org/panel/1.5.4/dist/css/loading.css"}},{"type":"object","name":"ImportedStyleSheet","id":"3730fbba-2332-423e-8d68-b1cbd59788b9","attributes":{"url":"https://cdn.holoviz.org/panel/1.5.4/dist/css/listpanel.css"}},{"type":"object","name":"ImportedStyleSheet","id":"8092df71-171a-4441-810f-947b221f14cd","attributes":{"url":"https://cdn.holoviz.org/panel/1.5.4/dist/bundled/theme/default.css"}},{"type":"object","name":"ImportedStyleSheet","id":"a55a2185-9d89-415c-b5c8-fd5f0a96ee56","attributes":{"url":"https://cdn.holoviz.org/panel/1.5.4/dist/bundled/theme/native.css"}}],"min_width":800,"margin":0,"sizing_mode":"stretch_width","align":"start","children":[{"type":"object","name":"Spacer","id":"7c3dcfb5-8f02-49f2-b758-9d2fb97be065","attributes":{"name":"HSpacer00293","stylesheets":["\n:host(.pn-loading):before, .pn-loading:before {\n  background-color: #c3c3c3;\n  mask-size: auto calc(min(50%, 400px));\n  -webkit-mask-size: auto calc(min(50%, 400px));\n}",{"id":"9f3a593b-3ecf-4592-b9de-43a598f5de60"},{"id":"8092df71-171a-4441-810f-947b221f14cd"},{"id":"a55a2185-9d89-415c-b5c8-fd5f0a96ee56"}],"margin":0,"sizing_mode":"stretch_width","align":"start"}},{"type":"object","name":"Figure","id":"21eee464-99a9-4a70-8e46-112f4cce505e","attributes":{"js_event_callbacks":{"type":"map","entries":[["reset",[{"type":"object","name":"CustomJS","id":"cf214eae-1459-44f0-9a8f-f737d6b7181a","attributes":{"code":"export default (_, cb_obj) => { cb_obj.origin.hold_render = false }"}}]]]},"subscribed_events":{"type":"set","entries":["reset","rangesupdate"]},"width":800,"margin":[5,10],"sizing_mode":"fixed","align":"start","x_range":{"type":"object","name":"Range1d","id":"6cb7f658-bced-417f-926f-ca509db70f13","attributes":{"name":"width","tags":[[["width",null]],[]]}},"y_range":{"type":"object","name":"Range1d","id":"336120c8-212c-43fe-8d5a-8c4fd6362b96","attributes":{"name":"offset","tags":[[["offset",null]],{"type":"map","entries":[["invert_yaxis",false],["autorange",false]]}]}},"x_scale":{"type":"object","name":"LinearScale","id":"b30ce5be-5d52-42af-b319-1b88459555de"},"y_scale":{"type":"object","name":"LinearScale","id":"f6728921-718a-4725-817a-ba0b70e88b07"},"title":{"type":"object","name":"Title","id":"464f98ed-de47-4aeb-8b54-d097c8cdec2d","attributes":{"text_color":"black","text_font_size":"12pt"}},"renderers":[{"type":"object","name":"GlyphRenderer","id":"d483ab0d-5968-40fe-a610-c6764a3f6d0b","attributes":{"data_source":{"type":"object","name":"ColumnDataSource","id":"6fdf2757-82b0-4f2b-b874-ab7131534d78","attributes":{"selected":{"type":"object","name":"Selection","id":"6d49c2b6-6120-48b3-8f0b-550fbd9aeb6e","attributes":{"indices":[],"line_indices":[]}},"selection_policy":{"type":"object","name":"UnionRenderers","id":"fbf4dec2-12c4-41ce-b5ef-a83fff534bd6"},"data":{"type":"map","entries":[["width",{"type":"ndarray","array":{"type":"bytes","data":""},"shape":[0],"dtype":"float64","order":"little"}],["offset",{"type":"ndarray","array":{"type":"bytes","data":""},"shape":[0],"dtype":"float64","order":"little"}]]}}},"view":{"type":"object","name":"CDSView","id":"030280ac-1c17-4127-ae42-524d1bed318c","attributes":{"filter":{"type":"object","name":"AllIndices","id":"5f35cbb2-b1b6-477b-84c0-ba7de2fb8bf5"}}},"glyph":{"type":"object","name":"Scatter","id":"ff26ff9d-f02b-43eb-b02f-adb1200dfdcb","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"width"},"y":{"type":"field","field":"offset"},"size":{"type":"value","value":10},"line_color":{"type":"value","value":"#007f00"},"fill_color":{"type":"value","value":"#007f00"},"hatch_color":{"type":"value","value":"#007f00"},"marker":{"type":"value","value":"cross"}}},"selection_glyph":{"type":"object","name":"Scatter","id":"80ae5577-f25f-49f3-b9bb-ed39b0654a41","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"width"},"y":{"type":"field","field":"offset"},"size":{"type":"value","value":10},"angle":{"type":"value","value":0.0},"line_color":{"type":"value","value":"#007f00"},"line_alpha":{"type":"value","value":1.0},"line_width":{"type":"value","value":1},"line_join":{"type":"value","value":"bevel"},"line_cap":{"type":"value","value":"butt"},"line_dash":{"type":"value","value":[]},"line_dash_offset":{"type":"value","value":0},"fill_color":{"type":"value","value":"#007f00"},"fill_alpha":{"type":"value","value":1.0},"hatch_color":{"type":"value","value":"#007f00"},"hatch_alpha":{"type":"value","value":1.0},"hatch_scale":{"type":"value","value":12.0},"hatch_pattern":{"type":"value","value":null},"hatch_weight":{"type":"value","value":1.0},"marker":{"type":"value","value":"cross"}}},"nonselection_glyph":{"type":"object","name":"Scatter","id":"2b779ffa-10d9-439e-9063-2d354d7eb0e7","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"width"},"y":{"type":"field","field":"offset"},"size":{"type":"value","value":10},"line_color":{"type":"value","value":"#007f00"},"line_alpha":{"type":"value","value":0.1},"fill_color":{"type":"value","value":"#007f00"},"fill_alpha":{"type":"value","value":0.1},"hatch_color":{"type":"value","value":"#007f00"},"hatch_alpha":{"type":"value","value":0.1},"marker":{"type":"value","value":"cross"}}},"muted_glyph":{"type":"object","name":"Scatter","id":"11761d60-58af-48e7-a707-ed4cb1a920cd","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"width"},"y":{"type":"field","field":"offset"},"size":{"type":"value","value":10},"line_color":{"type":"value","value":"#007f00"},"line_alpha":{"type":"value","value":0.2},"fill_color":{"type":"value","value":"#007f00"},"fill_alpha":{"type":"value","value":0.2},"hatch_color":{"type":"value","value":"#007f00"},"hatch_alpha":{"type":"value","value":0.2},"marker":{"type":"value","value":"cross"}}}}},{"type":"object","name":"GlyphRenderer","id":"6e80d35e-9fb2-41d3-b486-f2d831458131","attributes":{"data_source":{"type":"object","name":"ColumnDataSource","id":"46cfe6f4-f5d6-4ad6-b0be-2dab7abc97ea","attributes":{"selected":{"type":"object","name":"Selection","id":"e431d7bf-0892-46cb-9bca-4b719ed5af36","attributes":{"indices":[],"line_indices":[]}},"selection_policy":{"type":"object","name":"UnionRenderers","id":"ed9126bf-0361-4917-ada0-a5eb7c4b495c"},"data":{"type":"map","entries":[["width",{"type":"ndarray","array":{"type":"bytes","data":""},"shape":[0],"dtype":"float64","order":"little"}],["offset",{"type":"ndarray","array":{"type":"bytes","data":""},"shape":[0],"dtype":"float64","order":"little"}]]}}},"view":{"type":"object","name":"CDSView","id":"2aa32b65-a60c-4bab-ace6-e94cc3cc63f7","attributes":{"filter":{"type":"object","name":"AllIndices","id":"3a5d0dfa-916b-41bb-9ab6-0f13cdf65e4c"}}},"glyph":{"type":"object","name":"Scatter","id":"fd33a541-0780-4d98-a971-a9a14edbaf20","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"width"},"y":{"type":"field","field":"offset"},"size":{"type":"value","value":10},"angle":{"type":"value","value":0.7853981633974483},"line_color":{"type":"value","value":"#ff0000"},"fill_color":{"type":"value","value":"#ff0000"},"hatch_color":{"type":"value","value":"#ff0000"},"marker":{"type":"value","value":"cross"}}},"selection_glyph":{"type":"object","name":"Scatter","id":"9835f6e1-b818-4ecd-8090-b04aaae1fc11","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"width"},"y":{"type":"field","field":"offset"},"size":{"type":"value","value":10},"angle":{"type":"value","value":0.7853981633974483},"line_color":{"type":"value","value":"#ff0000"},"line_alpha":{"type":"value","value":1.0},"line_width":{"type":"value","value":1},"line_join":{"type":"value","value":"bevel"},"line_cap":{"type":"value","value":"butt"},"line_dash":{"type":"value","value":[]},"line_dash_offset":{"type":"value","value":0},"fill_color":{"type":"value","value":"#ff0000"},"fill_alpha":{"type":"value","value":1.0},"hatch_color":{"type":"value","value":"#ff0000"},"hatch_alpha":{"type":"value","value":1.0},"hatch_scale":{"type":"value","value":12.0},"hatch_pattern":{"type":"value","value":null},"hatch_weight":{"type":"value","value":1.0},"marker":{"type":"value","value":"cross"}}},"nonselection_glyph":{"type":"object","name":"Scatter","id":"4f674fec-2be9-411c-bf9d-4c16d3b97891","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"width"},"y":{"type":"field","field":"offset"},"size":{"type":"value","value":10},"angle":{"type":"value","value":0.7853981633974483},"line_color":{"type":"value","value":"#ff0000"},"line_alpha":{"type":"value","value":0.1},"fill_color":{"type":"value","value":"#ff0000"},"fill_alpha":{"type":"value","value":0.1},"hatch_color":{"type":"value","value":"#ff0000"},"hatch_alpha":{"type":"value","value":0.1},"marker":{"type":"value","value":"cross"}}},"muted_glyph":{"type":"object","name":"Scatter","id":"8297e700-a463-4f05-b8ea-7e4c00c311d4","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"width"},"y":{"type":"field","field":"offset"},"size":{"type":"value","value":10},"angle":{"type":"value","value":0.7853981633974483},"line_color":{"type":"value","value":"#ff0000"},"line_alpha":{"type":"value","value":0.2},"fill_color":{"type":"value","value":"#ff0000"},"fill_alpha":{"type":"value","value":0.2},"hatch_color":{"type":"value","value":"#ff0000"},"hatch_alpha":{"type":"value","value":0.2},"marker":{"type":"value","value":"cross"}}}}}],"toolbar":{"type":"object","name":"Toolbar","id":"ddd396c3-2d79-492a-b03c-64efcdbbd28d","attributes":{"tools":[{"type":"object","name":"WheelZoomTool","id":"625db27d-d122-4f2b-bd86-22a7f3562376","attributes":{"tags":["hv_created"],"renderers":"auto","zoom_together":"none"}},{"type":"object","name":"HoverTool","id":"b49ddc3e-3b1b-4eab-9a6d-21cdfc610c14","attributes":{"tags":["hv_created"],"renderers":[{"id":"d483ab0d-5968-40fe-a610-c6764a3f6d0b"},{"id":"6e80d35e-9fb2-41d3-b486-f2d831458131"}],"tooltips":[["width","@{width}"],["offset","@{offset}"]]}},{"type":"object","name":"SaveTool","id":"cd7b58a1-66ec-4be9-b8fd-203e20afb35b"},{"type":"object","name":"PanTool","id":"b294bebd-455b-44e3-9bfe-4dde3c27a9fa"},{"type":"object","name":"BoxZoomTool","id":"0a9cf6c3-5026-4184-b82a-53d0de2f45e2","attributes":{"overlay":{"type":"object","name":"BoxAnnotation","id":"d03948dd-2d0c-44d6-8902-cb36a2defe4f","attributes":{"syncable":false,"line_color":"black","line_alpha":1.0,"line_width":2,"line_dash":[4,4],"fill_color":"lightgrey","fill_alpha":0.5,"level":"overlay","visible":false,"left":{"type":"number","value":"nan"},"right":{"type":"number","value":"nan"},"top":{"type":"number","value":"nan"},"bottom":{"type":"number","value":"nan"},"left_units":"canvas","right_units":"canvas","top_units":"canvas","bottom_units":"canvas","handles":{"type":"object","name":"BoxInteractionHandles","id":"287de339-0588-4015-aa8c-86cff939397e","attributes":{"all":{"type":"object","name":"AreaVisuals","id":"9bc7a407-1bcc-42eb-bb4b-03fa013527cb","attributes":{"fill_color":"white","hover_fill_color":"lightgray"}}}}}}}},{"type":"object","name":"ResetTool","id":"02b06950-52df-477a-b001-c320e13ef8a2"}],"active_drag":{"id":"b294bebd-455b-44e3-9bfe-4dde3c27a9fa"},"active_scroll":{"id":"625db27d-d122-4f2b-bd86-22a7f3562376"}}},"left":[{"type":"object","name":"LinearAxis","id":"05fab74f-a4af-4aa3-9839-05f0a42dfbec","attributes":{"ticker":{"type":"object","name":"BasicTicker","id":"2ffc2636-122e-4760-9c4a-66e00c8f8898","attributes":{"mantissas":[1,2,5]}},"formatter":{"type":"object","name":"BasicTickFormatter","id":"f76ce564-fe9c-4421-97f7-c434b2eb6193"},"axis_label":"offset","major_label_policy":{"type":"object","name":"AllLabels","id":"ad93e6bd-f456-41df-943e-f53f04ff1267"}}}],"below":[{"type":"object","name":"LinearAxis","id":"e8c2ad87-81b3-4d45-8e2d-89d563401960","attributes":{"ticker":{"type":"object","name":"BasicTicker","id":"10d341e1-8dbe-4bfc-a571-62e941f9b3f5","attributes":{"mantissas":[1,2,5]}},"formatter":{"type":"object","name":"BasicTickFormatter","id":"1b104f7a-629c-4a30-bf82-7773cbbd2fe8"},"axis_label":"width","major_label_policy":{"type":"object","name":"AllLabels","id":"37c1080d-5a88-42d5-9628-7f84899e36e7"}}}],"center":[{"type":"object","name":"Grid","id":"12d08aa9-57f3-4918-bd3d-0429a7e2268b","attributes":{"axis":{"id":"e8c2ad87-81b3-4d45-8e2d-89d563401960"},"grid_line_color":null}},{"type":"object","name":"Grid","id":"a7b90615-13ee-4632-8e68-1c6c4117ef28","attributes":{"dimension":1,"axis":{"id":"05fab74f-a4af-4aa3-9839-05f0a42dfbec"},"grid_line_color":null}}],"min_border_top":10,"min_border_bottom":10,"min_border_left":10,"min_border_right":10,"output_backend":"webgl"}},{"type":"object","name":"Spacer","id":"9fc830d4-6072-49bc-806d-818d91fbe39e","attributes":{"name":"HSpacer00294","stylesheets":["\n:host(.pn-loading):before, .pn-loading:before {\n  background-color: #c3c3c3;\n  mask-size: auto calc(min(50%, 400px));\n  -webkit-mask-size: auto calc(min(50%, 400px));\n}",{"id":"9f3a593b-3ecf-4592-b9de-43a598f5de60"},{"id":"8092df71-171a-4441-810f-947b221f14cd"},{"id":"a55a2185-9d89-415c-b5c8-fd5f0a96ee56"}],"margin":0,"sizing_mode":"stretch_width","align":"start"}}]}},{"type":"object","name":"panel.models.comm_manager.CommManager","id":"2e4f340d-447f-4058-952a-4723096b50bc","attributes":{"plot_id":"50316ee1-33cd-4a95-9a9c-9785882f142b","comm_id":"2dbc220698ba45c39b0ec604e9ad9282","client_comm_id":"5d475c338eb14e02a70a34975e315b7d"}}],"defs":[{"type":"model","name":"ReactiveHTML1"},{"type":"model","name":"FlexBox1","properties":[{"name":"align_content","kind":"Any","default":"flex-start"},{"name":"align_items","kind":"Any","default":"flex-start"},{"name":"flex_direction","kind":"Any","default":"row"},{"name":"flex_wrap","kind":"Any","default":"wrap"},{"name":"gap","kind":"Any","default":""},{"name":"justify_content","kind":"Any","default":"flex-start"}]},{"type":"model","name":"FloatPanel1","properties":[{"name":"config","kind":"Any","default":{"type":"map"}},{"name":"contained","kind":"Any","default":true},{"name":"position","kind":"Any","default":"right-top"},{"name":"offsetx","kind":"Any","default":null},{"name":"offsety","kind":"Any","default":null},{"name":"theme","kind":"Any","default":"primary"},{"name":"status","kind":"Any","default":"normalized"}]},{"type":"model","name":"GridStack1","properties":[{"name":"mode","kind":"Any","default":"warn"},{"name":"ncols","kind":"Any","default":null},{"name":"nrows","kind":"Any","default":null},{"name":"allow_resize","kind":"Any","default":true},{"name":"allow_drag","kind":"Any","default":true},{"name":"state","kind":"Any","default":[]}]},{"type":"model","name":"drag1","properties":[{"name":"slider_width","kind":"Any","default":5},{"name":"slider_color","kind":"Any","default":"black"},{"name":"value","kind":"Any","default":50}]},{"type":"model","name":"click1","properties":[{"name":"terminal_output","kind":"Any","default":""},{"name":"debug_name","kind":"Any","default":""},{"name":"clears","kind":"Any","default":0}]},{"type":"model","name":"FastWrapper1","properties":[{"name":"object","kind":"Any","default":null},{"name":"style","kind":"Any","default":null}]},{"type":"model","name":"NotificationAreaBase1","properties":[{"name":"js_events","kind":"Any","default":{"type":"map"}},{"name":"position","kind":"Any","default":"bottom-right"},{"name":"_clear","kind":"Any","default":0}]},{"type":"model","name":"NotificationArea1","properties":[{"name":"js_events","kind":"Any","default":{"type":"map"}},{"name":"notifications","kind":"Any","default":[]},{"name":"position","kind":"Any","default":"bottom-right"},{"name":"_clear","kind":"Any","default":0},{"name":"types","kind":"Any","default":[{"type":"map","entries":[["type","warning"],["background","#ffc107"],["icon",{"type":"map","entries":[["className","fas fa-exclamation-triangle"],["tagName","i"],["color","white"]]}]]},{"type":"map","entries":[["type","info"],["background","#007bff"],["icon",{"type":"map","entries":[["className","fas fa-info-circle"],["tagName","i"],["color","white"]]}]]}]}]},{"type":"model","name":"Notification","properties":[{"name":"background","kind":"Any","default":null},{"name":"duration","kind":"Any","default":3000},{"name":"icon","kind":"Any","default":null},{"name":"message","kind":"Any","default":""},{"name":"notification_type","kind":"Any","default":null},{"name":"_destroyed","kind":"Any","default":false}]},{"type":"model","name":"TemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"BootstrapTemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"TemplateEditor1","properties":[{"name":"layout","kind":"Any","default":[]}]},{"type":"model","name":"MaterialTemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"ReactiveESM1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"JSComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"ReactComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"AnyWidgetComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"request_value1","properties":[{"name":"fill","kind":"Any","default":"none"},{"name":"_synced","kind":"Any","default":null},{"name":"_request_sync","kind":"Any","default":0}]}]}};
      var render_items = [{"docid":"5546b00a-ee8f-4445-ac9a-342c3d901e5d","roots":{"50316ee1-33cd-4a95-9a9c-9785882f142b":"dbfac4c2-c145-4f10-80c0-4a1772a36382"},"root_ids":["50316ee1-33cd-4a95-9a9c-9785882f142b"]}];
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
    46.484375 -10.15625 43
    🐙{'valid': True, 'payload': CWbytearray(b'01'), 'full\_response': CWbytearray(b'00 72 01 01 d4 00'), 'rv': bytearray(b'\x00')}
    CWbytearray(b'01')
    47.65625 -42.1875 44
    🐙{'valid': True, 'payload': CWbytearray(b'01'), 'full\_response': CWbytearray(b'00 72 01 01 d4 00'), 'rv': bytearray(b'\x00')}
    CWbytearray(b'01')
    47.65625 -39.0625 44
    🐙


Let’s see where we needed to target for our glitch to work:


**In [12]:**

.. code:: ipython3

    gc.calc(["width", "offset"], "success_rate")


**Out [12]:**



.. parsed-literal::

    [((44,),
      {'total': 221,
       'success': 2,
       'success_rate': 0.00904977375565611,
       'reset': 62,
       'reset_rate': 0.28054298642533937,
       'normal': 157,
       'normal_rate': 0.7104072398190046}),
     ((43,),
      {'total': 222,
       'success': 1,
       'success_rate': 0.0045045045045045045,
       'reset': 62,
       'reset_rate': 0.27927927927927926,
       'normal': 159,
       'normal_rate': 0.7162162162162162}),
     ((45,),
      {'total': 204,
       'success': 0,
       'success_rate': 0.0,
       'reset': 50,
       'reset_rate': 0.24509803921568626,
       'normal': 154,
       'normal_rate': 0.7549019607843137}),
     ((42,),
      {'total': 225,
       'success': 0,
       'success_rate': 0.0,
       'reset': 67,
       'reset_rate': 0.29777777777777775,
       'normal': 158,
       'normal_rate': 0.7022222222222222}),
     ((41,),
      {'total': 234,
       'success': 0,
       'success_rate': 0.0,
       'reset': 78,
       'reset_rate': 0.3333333333333333,
       'normal': 156,
       'normal_rate': 0.6666666666666666}),
     ((40,),
      {'total': 208,
       'success': 0,
       'success_rate': 0.0,
       'reset': 53,
       'reset_rate': 0.2548076923076923,
       'normal': 155,
       'normal_rate': 0.7451923076923077}),
     ((39,),
      {'total': 209,
       'success': 0,
       'success_rate': 0.0,
       'reset': 62,
       'reset_rate': 0.2966507177033493,
       'normal': 147,
       'normal_rate': 0.7033492822966507}),
     ((38,),
      {'total': 195,
       'success': 0,
       'success_rate': 0.0,
       'reset': 45,
       'reset_rate': 0.23076923076923078,
       'normal': 150,
       'normal_rate': 0.7692307692307693}),
     ((37,),
      {'total': 199,
       'success': 0,
       'success_rate': 0.0,
       'reset': 48,
       'reset_rate': 0.24120603015075376,
       'normal': 151,
       'normal_rate': 0.7587939698492462}),
     ((36,),
      {'total': 196,
       'success': 0,
       'success_rate': 0.0,
       'reset': 51,
       'reset_rate': 0.2602040816326531,
       'normal': 145,
       'normal_rate': 0.7397959183673469}),
     ((35,),
      {'total': 195,
       'success': 0,
       'success_rate': 0.0,
       'reset': 41,
       'reset_rate': 0.21025641025641026,
       'normal': 154,
       'normal_rate': 0.7897435897435897}),
     ((34,),
      {'total': 197,
       'success': 0,
       'success_rate': 0.0,
       'reset': 39,
       'reset_rate': 0.19796954314720813,
       'normal': 158,
       'normal_rate': 0.8020304568527918}),
     ((33,),
      {'total': 195,
       'success': 0,
       'success_rate': 0.0,
       'reset': 38,
       'reset_rate': 0.19487179487179487,
       'normal': 157,
       'normal_rate': 0.8051282051282052}),
     ((32,),
      {'total': 195,
       'success': 0,
       'success_rate': 0.0,
       'reset': 38,
       'reset_rate': 0.19487179487179487,
       'normal': 157,
       'normal_rate': 0.8051282051282052}),
     ((31,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 43,
       'reset_rate': 0.215,
       'normal': 157,
       'normal_rate': 0.785}),
     ((30,),
      {'total': 196,
       'success': 0,
       'success_rate': 0.0,
       'reset': 38,
       'reset_rate': 0.19387755102040816,
       'normal': 158,
       'normal_rate': 0.8061224489795918})]




**In [13]:**

.. code:: ipython3

    scope.dis()
    target.dis()


**In [14]:**

.. code:: ipython3

    assert successes >= 1
