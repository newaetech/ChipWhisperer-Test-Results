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
    scope.adc.trig\_count                     changed from 11001536                  to 21919491                 
    scope.clock.adc\_src                      changed from clkgen\_x1                 to clkgen\_x4                
    scope.clock.adc\_freq                     changed from 29538459                  to 29611724                 
    scope.clock.adc\_rate                     changed from 29538459.0                to 29611724.0               
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
    Size after:
    +--------------------------------------------------------
    + Built for platform CW-Lite Arm \(STM32F3\) with:
    + CRYPTO\_TARGET = NONE
    + CRYPTO\_OPTIONS = 
    +--------------------------------------------------------
       text	   data	    bss	    dec	    hex	filename
       5524	      8	   1368	   6900	   1af4	simpleserial-glitch-CWLITEARM.elf




**In [4]:**

.. code:: ipython3

    fw_path = "../../../firmware/mcu/simpleserial-glitch/simpleserial-glitch-{}.hex".format(PLATFORM)
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

    scope.clock.adc\_freq                     changed from 29611724                  to 28752113                 
    scope.clock.adc\_rate                     changed from 29611724.0                to 28752113.0               



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
        <div id='97281d3a-143b-41b8-a645-bec79c7b4110'>
      <div id="d079c37f-98f5-4f49-b6f6-8e139b13e567" data-root-id="97281d3a-143b-41b8-a645-bec79c7b4110" style="display: contents;"></div>
    </div>
    <script type="application/javascript">(function(root) {
      var docs_json = {"77725d8a-7607-4ec3-ba7e-9d8f67c0820a":{"version":"3.6.1","title":"Bokeh Application","roots":[{"type":"object","name":"panel.models.browser.BrowserInfo","id":"97281d3a-143b-41b8-a645-bec79c7b4110"},{"type":"object","name":"panel.models.comm_manager.CommManager","id":"02338408-b844-4e65-ac9f-bd8a3f85ceff","attributes":{"plot_id":"97281d3a-143b-41b8-a645-bec79c7b4110","comm_id":"a9266e2ea1ae4039a74701f71f3ca255","client_comm_id":"d54dc93f92cc4cffb3c06ff0c83cf879"}}],"defs":[{"type":"model","name":"ReactiveHTML1"},{"type":"model","name":"FlexBox1","properties":[{"name":"align_content","kind":"Any","default":"flex-start"},{"name":"align_items","kind":"Any","default":"flex-start"},{"name":"flex_direction","kind":"Any","default":"row"},{"name":"flex_wrap","kind":"Any","default":"wrap"},{"name":"gap","kind":"Any","default":""},{"name":"justify_content","kind":"Any","default":"flex-start"}]},{"type":"model","name":"FloatPanel1","properties":[{"name":"config","kind":"Any","default":{"type":"map"}},{"name":"contained","kind":"Any","default":true},{"name":"position","kind":"Any","default":"right-top"},{"name":"offsetx","kind":"Any","default":null},{"name":"offsety","kind":"Any","default":null},{"name":"theme","kind":"Any","default":"primary"},{"name":"status","kind":"Any","default":"normalized"}]},{"type":"model","name":"GridStack1","properties":[{"name":"mode","kind":"Any","default":"warn"},{"name":"ncols","kind":"Any","default":null},{"name":"nrows","kind":"Any","default":null},{"name":"allow_resize","kind":"Any","default":true},{"name":"allow_drag","kind":"Any","default":true},{"name":"state","kind":"Any","default":[]}]},{"type":"model","name":"drag1","properties":[{"name":"slider_width","kind":"Any","default":5},{"name":"slider_color","kind":"Any","default":"black"},{"name":"value","kind":"Any","default":50}]},{"type":"model","name":"click1","properties":[{"name":"terminal_output","kind":"Any","default":""},{"name":"debug_name","kind":"Any","default":""},{"name":"clears","kind":"Any","default":0}]},{"type":"model","name":"FastWrapper1","properties":[{"name":"object","kind":"Any","default":null},{"name":"style","kind":"Any","default":null}]},{"type":"model","name":"NotificationAreaBase1","properties":[{"name":"js_events","kind":"Any","default":{"type":"map"}},{"name":"position","kind":"Any","default":"bottom-right"},{"name":"_clear","kind":"Any","default":0}]},{"type":"model","name":"NotificationArea1","properties":[{"name":"js_events","kind":"Any","default":{"type":"map"}},{"name":"notifications","kind":"Any","default":[]},{"name":"position","kind":"Any","default":"bottom-right"},{"name":"_clear","kind":"Any","default":0},{"name":"types","kind":"Any","default":[{"type":"map","entries":[["type","warning"],["background","#ffc107"],["icon",{"type":"map","entries":[["className","fas fa-exclamation-triangle"],["tagName","i"],["color","white"]]}]]},{"type":"map","entries":[["type","info"],["background","#007bff"],["icon",{"type":"map","entries":[["className","fas fa-info-circle"],["tagName","i"],["color","white"]]}]]}]}]},{"type":"model","name":"Notification","properties":[{"name":"background","kind":"Any","default":null},{"name":"duration","kind":"Any","default":3000},{"name":"icon","kind":"Any","default":null},{"name":"message","kind":"Any","default":""},{"name":"notification_type","kind":"Any","default":null},{"name":"_destroyed","kind":"Any","default":false}]},{"type":"model","name":"TemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"BootstrapTemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"TemplateEditor1","properties":[{"name":"layout","kind":"Any","default":[]}]},{"type":"model","name":"MaterialTemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"ReactiveESM1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"JSComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"ReactComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"AnyWidgetComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"request_value1","properties":[{"name":"fill","kind":"Any","default":"none"},{"name":"_synced","kind":"Any","default":null},{"name":"_request_sync","kind":"Any","default":0}]}]}};
      var render_items = [{"docid":"77725d8a-7607-4ec3-ba7e-9d8f67c0820a","roots":{"97281d3a-143b-41b8-a645-bec79c7b4110":"d079c37f-98f5-4f49-b6f6-8e139b13e567"},"root_ids":["97281d3a-143b-41b8-a645-bec79c7b4110"]}];
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
        <div id='d394226c-8653-46b7-991b-4effd01d39b1'>
      <div id="e6d09ac7-84d6-440d-8e92-69e2794d55dd" data-root-id="d394226c-8653-46b7-991b-4effd01d39b1" style="display: contents;"></div>
    </div>
    <script type="application/javascript">(function(root) {
      var docs_json = {"a075bd38-6bd8-44df-a29d-e15eebe4b329":{"version":"3.6.1","title":"Bokeh Application","roots":[{"type":"object","name":"Row","id":"d394226c-8653-46b7-991b-4effd01d39b1","attributes":{"name":"Row00289","stylesheets":["\n:host(.pn-loading):before, .pn-loading:before {\n  background-color: #c3c3c3;\n  mask-size: auto calc(min(50%, 400px));\n  -webkit-mask-size: auto calc(min(50%, 400px));\n}",{"type":"object","name":"ImportedStyleSheet","id":"14fdf63a-355c-415f-96e4-4d7e05405a19","attributes":{"url":"https://cdn.holoviz.org/panel/1.5.4/dist/css/loading.css"}},{"type":"object","name":"ImportedStyleSheet","id":"bbf9e68c-3c32-41ad-98c0-75839f7e0287","attributes":{"url":"https://cdn.holoviz.org/panel/1.5.4/dist/css/listpanel.css"}},{"type":"object","name":"ImportedStyleSheet","id":"614c02ee-3835-400a-b9dd-f2bfa8721486","attributes":{"url":"https://cdn.holoviz.org/panel/1.5.4/dist/bundled/theme/default.css"}},{"type":"object","name":"ImportedStyleSheet","id":"3110802c-24e9-4d50-9208-f3acb7cbe88f","attributes":{"url":"https://cdn.holoviz.org/panel/1.5.4/dist/bundled/theme/native.css"}}],"min_width":800,"margin":0,"sizing_mode":"stretch_width","align":"start","children":[{"type":"object","name":"Spacer","id":"37f32cd4-19d1-44b6-aa48-cebd9a03fc10","attributes":{"name":"HSpacer00293","stylesheets":["\n:host(.pn-loading):before, .pn-loading:before {\n  background-color: #c3c3c3;\n  mask-size: auto calc(min(50%, 400px));\n  -webkit-mask-size: auto calc(min(50%, 400px));\n}",{"id":"14fdf63a-355c-415f-96e4-4d7e05405a19"},{"id":"614c02ee-3835-400a-b9dd-f2bfa8721486"},{"id":"3110802c-24e9-4d50-9208-f3acb7cbe88f"}],"margin":0,"sizing_mode":"stretch_width","align":"start"}},{"type":"object","name":"Figure","id":"a756ae60-0902-4d0f-981b-d8d99476942c","attributes":{"js_event_callbacks":{"type":"map","entries":[["reset",[{"type":"object","name":"CustomJS","id":"c95206c7-f04e-4080-a14b-21a52089f9d6","attributes":{"code":"export default (_, cb_obj) => { cb_obj.origin.hold_render = false }"}}]]]},"subscribed_events":{"type":"set","entries":["reset","rangesupdate"]},"width":800,"margin":[5,10],"sizing_mode":"fixed","align":"start","x_range":{"type":"object","name":"Range1d","id":"296ad6e0-dc83-4c53-b6ca-eb86c19b1c8a","attributes":{"name":"ext_offset","tags":[[["ext_offset",null]],[]]}},"y_range":{"type":"object","name":"Range1d","id":"4af11d4e-6a6a-4e8c-b261-5a48a7652f7c","attributes":{"name":"offset","tags":[[["offset",null]],{"type":"map","entries":[["invert_yaxis",false],["autorange",false]]}]}},"x_scale":{"type":"object","name":"LinearScale","id":"fa7f976d-a2b9-4b12-819c-7fc6af25d6a4"},"y_scale":{"type":"object","name":"LinearScale","id":"6d1ccb25-cca7-4ee8-920f-a9fb1027e447"},"title":{"type":"object","name":"Title","id":"85a35669-9d85-4858-88a5-35d164cce761","attributes":{"text_color":"black","text_font_size":"12pt"}},"renderers":[{"type":"object","name":"GlyphRenderer","id":"2f7256b3-71b1-40f3-a74c-f5d2e8a7b50d","attributes":{"data_source":{"type":"object","name":"ColumnDataSource","id":"5695243f-d691-4333-92c7-39f8ee511cd5","attributes":{"selected":{"type":"object","name":"Selection","id":"4fdcbeb4-d9d8-46a0-9c13-a5a82a5d6ba2","attributes":{"indices":[],"line_indices":[]}},"selection_policy":{"type":"object","name":"UnionRenderers","id":"9f100c9e-b3bb-4250-81c7-08707b60a148"},"data":{"type":"map","entries":[["ext_offset",{"type":"ndarray","array":{"type":"bytes","data":""},"shape":[0],"dtype":"float64","order":"little"}],["offset",{"type":"ndarray","array":{"type":"bytes","data":""},"shape":[0],"dtype":"float64","order":"little"}]]}}},"view":{"type":"object","name":"CDSView","id":"ac572cef-452d-498e-a6ce-f9075741c061","attributes":{"filter":{"type":"object","name":"AllIndices","id":"490e9950-252c-4568-bc10-c02d2de5f9a0"}}},"glyph":{"type":"object","name":"Scatter","id":"9dc24505-5a16-4b82-9bb5-d8ce8a278861","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"ext_offset"},"y":{"type":"field","field":"offset"},"size":{"type":"value","value":10},"line_color":{"type":"value","value":"#007f00"},"fill_color":{"type":"value","value":"#007f00"},"hatch_color":{"type":"value","value":"#007f00"},"marker":{"type":"value","value":"cross"}}},"selection_glyph":{"type":"object","name":"Scatter","id":"d60f2c66-eb9f-4579-bfd1-505ae0cc8fe7","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"ext_offset"},"y":{"type":"field","field":"offset"},"size":{"type":"value","value":10},"angle":{"type":"value","value":0.0},"line_color":{"type":"value","value":"#007f00"},"line_alpha":{"type":"value","value":1.0},"line_width":{"type":"value","value":1},"line_join":{"type":"value","value":"bevel"},"line_cap":{"type":"value","value":"butt"},"line_dash":{"type":"value","value":[]},"line_dash_offset":{"type":"value","value":0},"fill_color":{"type":"value","value":"#007f00"},"fill_alpha":{"type":"value","value":1.0},"hatch_color":{"type":"value","value":"#007f00"},"hatch_alpha":{"type":"value","value":1.0},"hatch_scale":{"type":"value","value":12.0},"hatch_pattern":{"type":"value","value":null},"hatch_weight":{"type":"value","value":1.0},"marker":{"type":"value","value":"cross"}}},"nonselection_glyph":{"type":"object","name":"Scatter","id":"a5dfd3f3-3d6f-4f68-aa0e-6dd21ef57d39","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"ext_offset"},"y":{"type":"field","field":"offset"},"size":{"type":"value","value":10},"line_color":{"type":"value","value":"#007f00"},"line_alpha":{"type":"value","value":0.1},"fill_color":{"type":"value","value":"#007f00"},"fill_alpha":{"type":"value","value":0.1},"hatch_color":{"type":"value","value":"#007f00"},"hatch_alpha":{"type":"value","value":0.1},"marker":{"type":"value","value":"cross"}}},"muted_glyph":{"type":"object","name":"Scatter","id":"be7127f1-0773-4eee-bef5-0b42f9011ef3","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"ext_offset"},"y":{"type":"field","field":"offset"},"size":{"type":"value","value":10},"line_color":{"type":"value","value":"#007f00"},"line_alpha":{"type":"value","value":0.2},"fill_color":{"type":"value","value":"#007f00"},"fill_alpha":{"type":"value","value":0.2},"hatch_color":{"type":"value","value":"#007f00"},"hatch_alpha":{"type":"value","value":0.2},"marker":{"type":"value","value":"cross"}}}}},{"type":"object","name":"GlyphRenderer","id":"86618442-e4b3-4a51-b915-6fc9ac98c9e6","attributes":{"data_source":{"type":"object","name":"ColumnDataSource","id":"940249c2-8f1b-4590-b2f6-020fc485b573","attributes":{"selected":{"type":"object","name":"Selection","id":"32257553-ec45-4f79-b9ff-6f87d0b041f6","attributes":{"indices":[],"line_indices":[]}},"selection_policy":{"type":"object","name":"UnionRenderers","id":"0589a03e-e44b-42fb-81da-deb646dd309c"},"data":{"type":"map","entries":[["ext_offset",{"type":"ndarray","array":{"type":"bytes","data":""},"shape":[0],"dtype":"float64","order":"little"}],["offset",{"type":"ndarray","array":{"type":"bytes","data":""},"shape":[0],"dtype":"float64","order":"little"}]]}}},"view":{"type":"object","name":"CDSView","id":"72318c2d-74e5-4728-b01c-7b19e0239280","attributes":{"filter":{"type":"object","name":"AllIndices","id":"0882f818-62d1-4d4e-949f-5e2fe4f3a64d"}}},"glyph":{"type":"object","name":"Scatter","id":"7e4d66c2-a706-4b41-84e4-4c574769240e","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"ext_offset"},"y":{"type":"field","field":"offset"},"size":{"type":"value","value":10},"angle":{"type":"value","value":0.7853981633974483},"line_color":{"type":"value","value":"#ff0000"},"fill_color":{"type":"value","value":"#ff0000"},"hatch_color":{"type":"value","value":"#ff0000"},"marker":{"type":"value","value":"cross"}}},"selection_glyph":{"type":"object","name":"Scatter","id":"6edd804c-fb10-4714-b46e-064092095e4c","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"ext_offset"},"y":{"type":"field","field":"offset"},"size":{"type":"value","value":10},"angle":{"type":"value","value":0.7853981633974483},"line_color":{"type":"value","value":"#ff0000"},"line_alpha":{"type":"value","value":1.0},"line_width":{"type":"value","value":1},"line_join":{"type":"value","value":"bevel"},"line_cap":{"type":"value","value":"butt"},"line_dash":{"type":"value","value":[]},"line_dash_offset":{"type":"value","value":0},"fill_color":{"type":"value","value":"#ff0000"},"fill_alpha":{"type":"value","value":1.0},"hatch_color":{"type":"value","value":"#ff0000"},"hatch_alpha":{"type":"value","value":1.0},"hatch_scale":{"type":"value","value":12.0},"hatch_pattern":{"type":"value","value":null},"hatch_weight":{"type":"value","value":1.0},"marker":{"type":"value","value":"cross"}}},"nonselection_glyph":{"type":"object","name":"Scatter","id":"edfe76bf-b79f-488e-ba13-f3d55121a951","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"ext_offset"},"y":{"type":"field","field":"offset"},"size":{"type":"value","value":10},"angle":{"type":"value","value":0.7853981633974483},"line_color":{"type":"value","value":"#ff0000"},"line_alpha":{"type":"value","value":0.1},"fill_color":{"type":"value","value":"#ff0000"},"fill_alpha":{"type":"value","value":0.1},"hatch_color":{"type":"value","value":"#ff0000"},"hatch_alpha":{"type":"value","value":0.1},"marker":{"type":"value","value":"cross"}}},"muted_glyph":{"type":"object","name":"Scatter","id":"278d03b7-1c69-4862-9c4e-a17abae44190","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"ext_offset"},"y":{"type":"field","field":"offset"},"size":{"type":"value","value":10},"angle":{"type":"value","value":0.7853981633974483},"line_color":{"type":"value","value":"#ff0000"},"line_alpha":{"type":"value","value":0.2},"fill_color":{"type":"value","value":"#ff0000"},"fill_alpha":{"type":"value","value":0.2},"hatch_color":{"type":"value","value":"#ff0000"},"hatch_alpha":{"type":"value","value":0.2},"marker":{"type":"value","value":"cross"}}}}}],"toolbar":{"type":"object","name":"Toolbar","id":"61ff028e-7eda-4120-9c9b-f7fa05f73b0d","attributes":{"tools":[{"type":"object","name":"WheelZoomTool","id":"6b3c5020-2810-415f-8d5a-49764f7dfd45","attributes":{"tags":["hv_created"],"renderers":"auto","zoom_together":"none"}},{"type":"object","name":"HoverTool","id":"569f72e4-0e8d-4889-a8a8-334f366cdac0","attributes":{"tags":["hv_created"],"renderers":[{"id":"2f7256b3-71b1-40f3-a74c-f5d2e8a7b50d"},{"id":"86618442-e4b3-4a51-b915-6fc9ac98c9e6"}],"tooltips":[["ext_offset","@{ext_offset}"],["offset","@{offset}"]]}},{"type":"object","name":"SaveTool","id":"27784bd4-7e16-4bab-a9b5-0ae10bb36942"},{"type":"object","name":"PanTool","id":"978d163d-fc2d-4b02-a504-9a3ab0872ccf"},{"type":"object","name":"BoxZoomTool","id":"91cfc9ce-161f-4454-a078-d2dc5e6b867a","attributes":{"overlay":{"type":"object","name":"BoxAnnotation","id":"7db38602-7de1-4c17-8201-f9805fa2cd3d","attributes":{"syncable":false,"line_color":"black","line_alpha":1.0,"line_width":2,"line_dash":[4,4],"fill_color":"lightgrey","fill_alpha":0.5,"level":"overlay","visible":false,"left":{"type":"number","value":"nan"},"right":{"type":"number","value":"nan"},"top":{"type":"number","value":"nan"},"bottom":{"type":"number","value":"nan"},"left_units":"canvas","right_units":"canvas","top_units":"canvas","bottom_units":"canvas","handles":{"type":"object","name":"BoxInteractionHandles","id":"25d9aaaf-d6ec-4c26-b53c-201b5af43b5f","attributes":{"all":{"type":"object","name":"AreaVisuals","id":"5cbf1596-193c-434d-becf-d9afeee0d2cf","attributes":{"fill_color":"white","hover_fill_color":"lightgray"}}}}}}}},{"type":"object","name":"ResetTool","id":"78ad2c2b-101c-4125-a75a-b8a1561c3993"}],"active_drag":{"id":"978d163d-fc2d-4b02-a504-9a3ab0872ccf"},"active_scroll":{"id":"6b3c5020-2810-415f-8d5a-49764f7dfd45"}}},"left":[{"type":"object","name":"LinearAxis","id":"c6de600b-d3e2-4371-929b-93cd417eb48c","attributes":{"ticker":{"type":"object","name":"BasicTicker","id":"e3b5ebb9-980a-4fde-b24d-e8a4982dde3f","attributes":{"mantissas":[1,2,5]}},"formatter":{"type":"object","name":"BasicTickFormatter","id":"95a62201-2fc1-4e79-8173-4b6d8dfd5d2d"},"axis_label":"offset","major_label_policy":{"type":"object","name":"AllLabels","id":"d14f0309-11ca-43db-b047-e716dcdb1a96"}}}],"below":[{"type":"object","name":"LinearAxis","id":"5e6ab05a-242d-4980-8fd6-3d661b88f1b1","attributes":{"ticker":{"type":"object","name":"BasicTicker","id":"a22a07ee-9605-4b6f-b2cc-de899852e30a","attributes":{"mantissas":[1,2,5]}},"formatter":{"type":"object","name":"BasicTickFormatter","id":"f98fb234-1044-4831-bc3b-16f45fd33316"},"axis_label":"ext_offset","major_label_policy":{"type":"object","name":"AllLabels","id":"78829b91-bb45-44ca-a582-32cc6eada96e"}}}],"center":[{"type":"object","name":"Grid","id":"44e2d1b8-36b4-4ad5-8095-4e8efd28333f","attributes":{"axis":{"id":"5e6ab05a-242d-4980-8fd6-3d661b88f1b1"},"grid_line_color":null}},{"type":"object","name":"Grid","id":"f633c0ee-913a-45f3-b40a-55bb19cc0cdf","attributes":{"dimension":1,"axis":{"id":"c6de600b-d3e2-4371-929b-93cd417eb48c"},"grid_line_color":null}}],"min_border_top":10,"min_border_bottom":10,"min_border_left":10,"min_border_right":10,"output_backend":"webgl"}},{"type":"object","name":"Spacer","id":"5fa63882-0a57-4a2f-b8aa-1fc912670f8c","attributes":{"name":"HSpacer00294","stylesheets":["\n:host(.pn-loading):before, .pn-loading:before {\n  background-color: #c3c3c3;\n  mask-size: auto calc(min(50%, 400px));\n  -webkit-mask-size: auto calc(min(50%, 400px));\n}",{"id":"14fdf63a-355c-415f-96e4-4d7e05405a19"},{"id":"614c02ee-3835-400a-b9dd-f2bfa8721486"},{"id":"3110802c-24e9-4d50-9208-f3acb7cbe88f"}],"margin":0,"sizing_mode":"stretch_width","align":"start"}}]}},{"type":"object","name":"panel.models.comm_manager.CommManager","id":"9b51ce78-e23b-4af7-a00b-f5c91a1942cc","attributes":{"plot_id":"d394226c-8653-46b7-991b-4effd01d39b1","comm_id":"c3fa7916434c4075acdb2ca739d63ece","client_comm_id":"014b8b043e2349908b5ec1b9427ef89e"}}],"defs":[{"type":"model","name":"ReactiveHTML1"},{"type":"model","name":"FlexBox1","properties":[{"name":"align_content","kind":"Any","default":"flex-start"},{"name":"align_items","kind":"Any","default":"flex-start"},{"name":"flex_direction","kind":"Any","default":"row"},{"name":"flex_wrap","kind":"Any","default":"wrap"},{"name":"gap","kind":"Any","default":""},{"name":"justify_content","kind":"Any","default":"flex-start"}]},{"type":"model","name":"FloatPanel1","properties":[{"name":"config","kind":"Any","default":{"type":"map"}},{"name":"contained","kind":"Any","default":true},{"name":"position","kind":"Any","default":"right-top"},{"name":"offsetx","kind":"Any","default":null},{"name":"offsety","kind":"Any","default":null},{"name":"theme","kind":"Any","default":"primary"},{"name":"status","kind":"Any","default":"normalized"}]},{"type":"model","name":"GridStack1","properties":[{"name":"mode","kind":"Any","default":"warn"},{"name":"ncols","kind":"Any","default":null},{"name":"nrows","kind":"Any","default":null},{"name":"allow_resize","kind":"Any","default":true},{"name":"allow_drag","kind":"Any","default":true},{"name":"state","kind":"Any","default":[]}]},{"type":"model","name":"drag1","properties":[{"name":"slider_width","kind":"Any","default":5},{"name":"slider_color","kind":"Any","default":"black"},{"name":"value","kind":"Any","default":50}]},{"type":"model","name":"click1","properties":[{"name":"terminal_output","kind":"Any","default":""},{"name":"debug_name","kind":"Any","default":""},{"name":"clears","kind":"Any","default":0}]},{"type":"model","name":"FastWrapper1","properties":[{"name":"object","kind":"Any","default":null},{"name":"style","kind":"Any","default":null}]},{"type":"model","name":"NotificationAreaBase1","properties":[{"name":"js_events","kind":"Any","default":{"type":"map"}},{"name":"position","kind":"Any","default":"bottom-right"},{"name":"_clear","kind":"Any","default":0}]},{"type":"model","name":"NotificationArea1","properties":[{"name":"js_events","kind":"Any","default":{"type":"map"}},{"name":"notifications","kind":"Any","default":[]},{"name":"position","kind":"Any","default":"bottom-right"},{"name":"_clear","kind":"Any","default":0},{"name":"types","kind":"Any","default":[{"type":"map","entries":[["type","warning"],["background","#ffc107"],["icon",{"type":"map","entries":[["className","fas fa-exclamation-triangle"],["tagName","i"],["color","white"]]}]]},{"type":"map","entries":[["type","info"],["background","#007bff"],["icon",{"type":"map","entries":[["className","fas fa-info-circle"],["tagName","i"],["color","white"]]}]]}]}]},{"type":"model","name":"Notification","properties":[{"name":"background","kind":"Any","default":null},{"name":"duration","kind":"Any","default":3000},{"name":"icon","kind":"Any","default":null},{"name":"message","kind":"Any","default":""},{"name":"notification_type","kind":"Any","default":null},{"name":"_destroyed","kind":"Any","default":false}]},{"type":"model","name":"TemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"BootstrapTemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"TemplateEditor1","properties":[{"name":"layout","kind":"Any","default":[]}]},{"type":"model","name":"MaterialTemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"ReactiveESM1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"JSComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"ReactComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"AnyWidgetComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"request_value1","properties":[{"name":"fill","kind":"Any","default":"none"},{"name":"_synced","kind":"Any","default":null},{"name":"_request_sync","kind":"Any","default":0}]}]}};
      var render_items = [{"docid":"a075bd38-6bd8-44df-a29d-e15eebe4b329","roots":{"d394226c-8653-46b7-991b-4effd01d39b1":"e6d09ac7-84d6-440d-8e92-69e2794d55dd"},"root_ids":["d394226c-8653-46b7-991b-4effd01d39b1"]}];
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


**Out [11]:**



.. parsed-literal::

    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger
    Trigger still high!
    Trigger still high!
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 114, 1
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger
    Trigger still high!
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





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





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





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





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:417) Invalid CRC. Expected 153 got 96





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
    Trigger still high!
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





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

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:502) Read timed out: 
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger
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





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 4, 1





.. parsed-literal::

    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:502) Read timed out: 
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 101





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:502) Read timed out: 
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 183
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 0, 1





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:417) Invalid CRC. Expected 153 got 8





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:417) Invalid CRC. Expected 153 got 0





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





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
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 114
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 183
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 0, 1





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 3
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 101, 1





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:417) Invalid CRC. Expected 153 got 205





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





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
    CWbytearray(b'01')
    1.5625 -1.953125 27
    🐙Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    CWbytearray(b'01')
    1.5625 -1.953125 37
    🐙Trigger still high!
    CWbytearray(b'01')
    1.5625 -1.953125 44
    🐙Trigger still high!
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





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger
    Trigger still high!
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 101





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:502) Read timed out: 
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:502) Read timed out: 
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:417) Invalid CRC. Expected 104 got 111





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 2
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 0, 1





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:184) Infinite loop in unstuff data
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:185) CWbytearray(b'00 a0 00 20 25 15')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 160
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 0, 1





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a
    WARNING:root:SAM3U Serial buffers OVERRUN - data loss has occurred.





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:417) Invalid CRC. Expected 153 got 0





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:417) Invalid CRC. Expected 153 got 0
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





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

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





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

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





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

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 101
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:502) Read timed out: 
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





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





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 255
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 255, 1
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    WARNING:root:SAM3U Serial buffers OVERRUN - data loss has occurred.
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 183
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 0, 1
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:417) Invalid CRC. Expected 153 got 185
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:417) Invalid CRC. Expected 153 got 0
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:417) Invalid CRC. Expected 153 got 0
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





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

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 114
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 183
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 0, 1
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 0
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:184) Infinite loop in unstuff data
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:185) CWbytearray(b'00 a0 00 20 25 15')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 160
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 0, 1
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    WARNING:root:SAM3U Serial buffers OVERRUN - data loss has occurred.
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:417) Invalid CRC. Expected 153 got 205
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:417) Invalid CRC. Expected 153 got 54





.. parsed-literal::

    Trigger still high!
    Trigger still high!
    CWbytearray(b'01')
    1.953125 -1.953125 7
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
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger
    Trigger still high!
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:502) Read timed out: 
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:502) Read timed out: 
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





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

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





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
    CWbytearray(b'01')
    2.34375 -3.515625 48
    🐙Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:417) Invalid CRC. Expected 153 got 98





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
    CWbytearray(b'01')
    2.34375 -3.125 46
    🐙Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 101
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:502) Read timed out: 
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





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

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:502) Read timed out: 
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





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





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 255
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 255, 1
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    WARNING:root:SAM3U Serial buffers OVERRUN - data loss has occurred.
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:502) Read timed out: 
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:417) Invalid CRC. Expected 153 got 51
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:417) Invalid CRC. Expected 153 got 0
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





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
    CWbytearray(b'01')
    2.34375 -2.34375 27
    🐙Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    CWbytearray(b'01')
    2.34375 -2.34375 44
    🐙Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 114
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:184) Infinite loop in unstuff data
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:185) CWbytearray(b'00 a0 00 20 25 15')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 160
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 0, 1
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    WARNING:root:SAM3U Serial buffers OVERRUN - data loss has occurred.
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:417) Invalid CRC. Expected 153 got 140
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

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





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





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

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





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
    CWbytearray(b'01')
    2.734375 -3.125 46
    🐙Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 101





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:502) Read timed out: 
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:417) Invalid CRC. Expected 153 got 0
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





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

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 114
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 183
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 0, 1
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





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

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





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





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:417) Invalid CRC. Expected 153 got 96





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





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 101
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:502) Read timed out: 
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 183
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:417) Invalid CRC. Expected 153 got 0
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





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

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





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





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 08





.. parsed-literal::

    Timeout - no trigger



For this lab, you may want two copies of your results; one for finding
effective ext_offsets:


**In [12]:**

.. code:: ipython3

    results = gc.calc(ignore_params=["width", "offset"], sort="success_rate")
    results


**Out [12]:**



.. parsed-literal::

    [((44,),
      {'total': 49,
       'success': 2,
       'success_rate': 0.04081632653061224,
       'reset': 6,
       'reset_rate': 0.12244897959183673,
       'normal': 41,
       'normal_rate': 0.8367346938775511}),
     ((27,),
      {'total': 60,
       'success': 2,
       'success_rate': 0.03333333333333333,
       'reset': 35,
       'reset_rate': 0.5833333333333334,
       'normal': 23,
       'normal_rate': 0.38333333333333336}),
     ((46,),
      {'total': 73,
       'success': 2,
       'success_rate': 0.0273972602739726,
       'reset': 32,
       'reset_rate': 0.4383561643835616,
       'normal': 39,
       'normal_rate': 0.5342465753424658}),
     ((48,),
      {'total': 53,
       'success': 1,
       'success_rate': 0.018867924528301886,
       'reset': 20,
       'reset_rate': 0.37735849056603776,
       'normal': 32,
       'normal_rate': 0.6037735849056604}),
     ((37,),
      {'total': 59,
       'success': 1,
       'success_rate': 0.01694915254237288,
       'reset': 35,
       'reset_rate': 0.5932203389830508,
       'normal': 23,
       'normal_rate': 0.3898305084745763}),
     ((7,),
      {'total': 60,
       'success': 1,
       'success_rate': 0.016666666666666666,
       'reset': 37,
       'reset_rate': 0.6166666666666667,
       'normal': 22,
       'normal_rate': 0.36666666666666664}),
     ((100,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 18,
       'reset_rate': 0.375,
       'normal': 30,
       'normal_rate': 0.625}),
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
       'reset': 15,
       'reset_rate': 0.3125,
       'normal': 33,
       'normal_rate': 0.6875}),
     ((97,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 9,
       'reset_rate': 0.1875,
       'normal': 39,
       'normal_rate': 0.8125}),
     ((96,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 24,
       'reset_rate': 0.5,
       'normal': 24,
       'normal_rate': 0.5}),
     ((95,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 25,
       'reset_rate': 0.5208333333333334,
       'normal': 23,
       'normal_rate': 0.4791666666666667}),
     ((94,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 27,
       'reset_rate': 0.5625,
       'normal': 21,
       'normal_rate': 0.4375}),
     ((93,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 26,
       'reset_rate': 0.5416666666666666,
       'normal': 22,
       'normal_rate': 0.4583333333333333}),
     ((92,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 7,
       'reset_rate': 0.14583333333333334,
       'normal': 41,
       'normal_rate': 0.8541666666666666}),
     ((91,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 23,
       'reset_rate': 0.4791666666666667,
       'normal': 25,
       'normal_rate': 0.5208333333333334}),
     ((90,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 24,
       'reset_rate': 0.5,
       'normal': 24,
       'normal_rate': 0.5}),
     ((89,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 21,
       'reset_rate': 0.4375,
       'normal': 27,
       'normal_rate': 0.5625}),
     ((88,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 24,
       'reset_rate': 0.5,
       'normal': 24,
       'normal_rate': 0.5}),
     ((87,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 25,
       'reset_rate': 0.5208333333333334,
       'normal': 23,
       'normal_rate': 0.4791666666666667}),
     ((86,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 25,
       'reset_rate': 0.5208333333333334,
       'normal': 23,
       'normal_rate': 0.4791666666666667}),
     ((85,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 12,
       'reset_rate': 0.25,
       'normal': 36,
       'normal_rate': 0.75}),
     ((84,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 5,
       'reset_rate': 0.10416666666666667,
       'normal': 43,
       'normal_rate': 0.8958333333333334}),
     ((83,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 18,
       'reset_rate': 0.375,
       'normal': 30,
       'normal_rate': 0.625}),
     ((82,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 25,
       'reset_rate': 0.5208333333333334,
       'normal': 23,
       'normal_rate': 0.4791666666666667}),
     ((81,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 25,
       'reset_rate': 0.5208333333333334,
       'normal': 23,
       'normal_rate': 0.4791666666666667}),
     ((80,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 20,
       'reset_rate': 0.4166666666666667,
       'normal': 28,
       'normal_rate': 0.5833333333333334}),
     ((79,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 7,
       'reset_rate': 0.14583333333333334,
       'normal': 41,
       'normal_rate': 0.8541666666666666}),
     ((78,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 1,
       'reset_rate': 0.020833333333333332,
       'normal': 47,
       'normal_rate': 0.9791666666666666}),
     ((77,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 7,
       'reset_rate': 0.14583333333333334,
       'normal': 41,
       'normal_rate': 0.8541666666666666}),
     ((76,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 27,
       'reset_rate': 0.5625,
       'normal': 21,
       'normal_rate': 0.4375}),
     ((75,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 27,
       'reset_rate': 0.5625,
       'normal': 21,
       'normal_rate': 0.4375}),
     ((74,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 10,
       'reset_rate': 0.20833333333333334,
       'normal': 38,
       'normal_rate': 0.7916666666666666}),
     ((73,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 15,
       'reset_rate': 0.3125,
       'normal': 33,
       'normal_rate': 0.6875}),
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
       'reset': 1,
       'reset_rate': 0.020833333333333332,
       'normal': 47,
       'normal_rate': 0.9791666666666666}),
     ((70,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 48,
       'normal_rate': 1.0}),
     ((69,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 17,
       'reset_rate': 0.3541666666666667,
       'normal': 31,
       'normal_rate': 0.6458333333333334}),
     ((68,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 24,
       'reset_rate': 0.5,
       'normal': 24,
       'normal_rate': 0.5}),
     ((67,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 26,
       'reset_rate': 0.5416666666666666,
       'normal': 22,
       'normal_rate': 0.4583333333333333}),
     ((66,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 27,
       'reset_rate': 0.5625,
       'normal': 21,
       'normal_rate': 0.4375}),
     ((65,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 14,
       'reset_rate': 0.2916666666666667,
       'normal': 34,
       'normal_rate': 0.7083333333333334}),
     ((64,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 2,
       'reset_rate': 0.041666666666666664,
       'normal': 46,
       'normal_rate': 0.9583333333333334}),
     ((63,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 7,
       'reset_rate': 0.14583333333333334,
       'normal': 41,
       'normal_rate': 0.8541666666666666}),
     ((62,),
      {'total': 50,
       'success': 0,
       'success_rate': 0.0,
       'reset': 26,
       'reset_rate': 0.52,
       'normal': 24,
       'normal_rate': 0.48}),
     ((61,),
      {'total': 54,
       'success': 0,
       'success_rate': 0.0,
       'reset': 28,
       'reset_rate': 0.5185185185185185,
       'normal': 26,
       'normal_rate': 0.48148148148148145}),
     ((60,),
      {'total': 53,
       'success': 0,
       'success_rate': 0.0,
       'reset': 15,
       'reset_rate': 0.2830188679245283,
       'normal': 38,
       'normal_rate': 0.7169811320754716}),
     ((59,),
      {'total': 60,
       'success': 0,
       'success_rate': 0.0,
       'reset': 17,
       'reset_rate': 0.2833333333333333,
       'normal': 43,
       'normal_rate': 0.7166666666666667}),
     ((58,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 13,
       'reset_rate': 0.2708333333333333,
       'normal': 35,
       'normal_rate': 0.7291666666666666}),
     ((57,),
      {'total': 73,
       'success': 0,
       'success_rate': 0.0,
       'reset': 25,
       'reset_rate': 0.3424657534246575,
       'normal': 48,
       'normal_rate': 0.6575342465753424}),
     ((56,),
      {'total': 73,
       'success': 0,
       'success_rate': 0.0,
       'reset': 50,
       'reset_rate': 0.684931506849315,
       'normal': 23,
       'normal_rate': 0.3150684931506849}),
     ((55,),
      {'total': 53,
       'success': 0,
       'success_rate': 0.0,
       'reset': 27,
       'reset_rate': 0.5094339622641509,
       'normal': 26,
       'normal_rate': 0.49056603773584906}),
     ((54,),
      {'total': 58,
       'success': 0,
       'success_rate': 0.0,
       'reset': 15,
       'reset_rate': 0.25862068965517243,
       'normal': 43,
       'normal_rate': 0.7413793103448276}),
     ((53,),
      {'total': 52,
       'success': 0,
       'success_rate': 0.0,
       'reset': 14,
       'reset_rate': 0.2692307692307692,
       'normal': 38,
       'normal_rate': 0.7307692307692307}),
     ((52,),
      {'total': 72,
       'success': 0,
       'success_rate': 0.0,
       'reset': 26,
       'reset_rate': 0.3611111111111111,
       'normal': 46,
       'normal_rate': 0.6388888888888888}),
     ((51,),
      {'total': 73,
       'success': 0,
       'success_rate': 0.0,
       'reset': 48,
       'reset_rate': 0.6575342465753424,
       'normal': 25,
       'normal_rate': 0.3424657534246575}),
     ((50,),
      {'total': 58,
       'success': 0,
       'success_rate': 0.0,
       'reset': 35,
       'reset_rate': 0.603448275862069,
       'normal': 23,
       'normal_rate': 0.39655172413793105}),
     ((49,),
      {'total': 62,
       'success': 0,
       'success_rate': 0.0,
       'reset': 23,
       'reset_rate': 0.3709677419354839,
       'normal': 39,
       'normal_rate': 0.6290322580645161}),
     ((47,),
      {'total': 55,
       'success': 0,
       'success_rate': 0.0,
       'reset': 13,
       'reset_rate': 0.23636363636363636,
       'normal': 42,
       'normal_rate': 0.7636363636363637}),
     ((45,),
      {'total': 54,
       'success': 0,
       'success_rate': 0.0,
       'reset': 31,
       'reset_rate': 0.5740740740740741,
       'normal': 23,
       'normal_rate': 0.42592592592592593}),
     ((43,),
      {'total': 49,
       'success': 0,
       'success_rate': 0.0,
       'reset': 2,
       'reset_rate': 0.04081632653061224,
       'normal': 47,
       'normal_rate': 0.9591836734693877}),
     ((42,),
      {'total': 51,
       'success': 0,
       'success_rate': 0.0,
       'reset': 3,
       'reset_rate': 0.058823529411764705,
       'normal': 48,
       'normal_rate': 0.9411764705882353}),
     ((41,),
      {'total': 49,
       'success': 0,
       'success_rate': 0.0,
       'reset': 3,
       'reset_rate': 0.061224489795918366,
       'normal': 46,
       'normal_rate': 0.9387755102040817}),
     ((40,),
      {'total': 68,
       'success': 0,
       'success_rate': 0.0,
       'reset': 21,
       'reset_rate': 0.3088235294117647,
       'normal': 47,
       'normal_rate': 0.6911764705882353}),
     ((39,),
      {'total': 71,
       'success': 0,
       'success_rate': 0.0,
       'reset': 43,
       'reset_rate': 0.6056338028169014,
       'normal': 28,
       'normal_rate': 0.39436619718309857}),
     ((38,),
      {'total': 72,
       'success': 0,
       'success_rate': 0.0,
       'reset': 47,
       'reset_rate': 0.6527777777777778,
       'normal': 25,
       'normal_rate': 0.3472222222222222}),
     ((36,),
      {'total': 49,
       'success': 0,
       'success_rate': 0.0,
       'reset': 12,
       'reset_rate': 0.24489795918367346,
       'normal': 37,
       'normal_rate': 0.7551020408163265}),
     ((35,),
      {'total': 52,
       'success': 0,
       'success_rate': 0.0,
       'reset': 5,
       'reset_rate': 0.09615384615384616,
       'normal': 47,
       'normal_rate': 0.9038461538461539}),
     ((34,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 4,
       'reset_rate': 0.08333333333333333,
       'normal': 44,
       'normal_rate': 0.9166666666666666}),
     ((33,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 48,
       'normal_rate': 1.0}),
     ((32,),
      {'total': 53,
       'success': 0,
       'success_rate': 0.0,
       'reset': 5,
       'reset_rate': 0.09433962264150944,
       'normal': 48,
       'normal_rate': 0.9056603773584906}),
     ((31,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 5,
       'reset_rate': 0.10416666666666667,
       'normal': 43,
       'normal_rate': 0.8958333333333334}),
     ((30,),
      {'total': 69,
       'success': 0,
       'success_rate': 0.0,
       'reset': 21,
       'reset_rate': 0.30434782608695654,
       'normal': 48,
       'normal_rate': 0.6956521739130435}),
     ((29,),
      {'total': 71,
       'success': 0,
       'success_rate': 0.0,
       'reset': 44,
       'reset_rate': 0.6197183098591549,
       'normal': 27,
       'normal_rate': 0.38028169014084506}),
     ((28,),
      {'total': 71,
       'success': 0,
       'success_rate': 0.0,
       'reset': 46,
       'reset_rate': 0.647887323943662,
       'normal': 25,
       'normal_rate': 0.352112676056338}),
     ((26,),
      {'total': 49,
       'success': 0,
       'success_rate': 0.0,
       'reset': 13,
       'reset_rate': 0.2653061224489796,
       'normal': 36,
       'normal_rate': 0.7346938775510204}),
     ((25,),
      {'total': 55,
       'success': 0,
       'success_rate': 0.0,
       'reset': 8,
       'reset_rate': 0.14545454545454545,
       'normal': 47,
       'normal_rate': 0.8545454545454545}),
     ((24,),
      {'total': 50,
       'success': 0,
       'success_rate': 0.0,
       'reset': 9,
       'reset_rate': 0.18,
       'normal': 41,
       'normal_rate': 0.82}),
     ((23,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 2,
       'reset_rate': 0.041666666666666664,
       'normal': 46,
       'normal_rate': 0.9583333333333334}),
     ((22,),
      {'total': 50,
       'success': 0,
       'success_rate': 0.0,
       'reset': 2,
       'reset_rate': 0.04,
       'normal': 48,
       'normal_rate': 0.96}),
     ((21,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 2,
       'reset_rate': 0.041666666666666664,
       'normal': 46,
       'normal_rate': 0.9583333333333334}),
     ((20,),
      {'total': 67,
       'success': 0,
       'success_rate': 0.0,
       'reset': 19,
       'reset_rate': 0.2835820895522388,
       'normal': 48,
       'normal_rate': 0.7164179104477612}),
     ((19,),
      {'total': 73,
       'success': 0,
       'success_rate': 0.0,
       'reset': 44,
       'reset_rate': 0.6027397260273972,
       'normal': 29,
       'normal_rate': 0.3972602739726027}),
     ((18,),
      {'total': 71,
       'success': 0,
       'success_rate': 0.0,
       'reset': 48,
       'reset_rate': 0.676056338028169,
       'normal': 23,
       'normal_rate': 0.323943661971831}),
     ((17,),
      {'total': 58,
       'success': 0,
       'success_rate': 0.0,
       'reset': 33,
       'reset_rate': 0.5689655172413793,
       'normal': 25,
       'normal_rate': 0.43103448275862066}),
     ((16,),
      {'total': 49,
       'success': 0,
       'success_rate': 0.0,
       'reset': 11,
       'reset_rate': 0.22448979591836735,
       'normal': 38,
       'normal_rate': 0.7755102040816326}),
     ((15,),
      {'total': 54,
       'success': 0,
       'success_rate': 0.0,
       'reset': 7,
       'reset_rate': 0.12962962962962962,
       'normal': 47,
       'normal_rate': 0.8703703703703703}),
     ((14,),
      {'total': 49,
       'success': 0,
       'success_rate': 0.0,
       'reset': 7,
       'reset_rate': 0.14285714285714285,
       'normal': 42,
       'normal_rate': 0.8571428571428571}),
     ((13,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 48,
       'normal_rate': 1.0}),
     ((12,),
      {'total': 50,
       'success': 0,
       'success_rate': 0.0,
       'reset': 2,
       'reset_rate': 0.04,
       'normal': 48,
       'normal_rate': 0.96}),
     ((11,),
      {'total': 50,
       'success': 0,
       'success_rate': 0.0,
       'reset': 4,
       'reset_rate': 0.08,
       'normal': 46,
       'normal_rate': 0.92}),
     ((10,),
      {'total': 67,
       'success': 0,
       'success_rate': 0.0,
       'reset': 21,
       'reset_rate': 0.31343283582089554,
       'normal': 46,
       'normal_rate': 0.6865671641791045}),
     ((9,),
      {'total': 69,
       'success': 0,
       'success_rate': 0.0,
       'reset': 40,
       'reset_rate': 0.5797101449275363,
       'normal': 29,
       'normal_rate': 0.42028985507246375}),
     ((8,),
      {'total': 73,
       'success': 0,
       'success_rate': 0.0,
       'reset': 46,
       'reset_rate': 0.6301369863013698,
       'normal': 27,
       'normal_rate': 0.3698630136986301}),
     ((6,),
      {'total': 51,
       'success': 0,
       'success_rate': 0.0,
       'reset': 15,
       'reset_rate': 0.29411764705882354,
       'normal': 36,
       'normal_rate': 0.7058823529411765}),
     ((5,),
      {'total': 52,
       'success': 0,
       'success_rate': 0.0,
       'reset': 7,
       'reset_rate': 0.1346153846153846,
       'normal': 45,
       'normal_rate': 0.8653846153846154}),
     ((4,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 4,
       'reset_rate': 0.08333333333333333,
       'normal': 44,
       'normal_rate': 0.9166666666666666}),
     ((3,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 48,
       'normal_rate': 1.0}),
     ((2,),
      {'total': 51,
       'success': 0,
       'success_rate': 0.0,
       'reset': 3,
       'reset_rate': 0.058823529411764705,
       'normal': 48,
       'normal_rate': 0.9411764705882353}),
     ((1,),
      {'total': 48,
       'success': 0,
       'success_rate': 0.0,
       'reset': 3,
       'reset_rate': 0.0625,
       'normal': 45,
       'normal_rate': 0.9375}),
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

    [((1.6, -2.0000000000000004),
      {'total': 130,
       'success': 3,
       'success_rate': 0.023076923076923078,
       'reset': 90,
       'reset_rate': 0.6923076923076923,
       'normal': 37,
       'normal_rate': 0.2846153846153846}),
     ((2.4, -2.4000000000000004),
      {'total': 122,
       'success': 2,
       'success_rate': 0.01639344262295082,
       'reset': 64,
       'reset_rate': 0.5245901639344263,
       'normal': 56,
       'normal_rate': 0.45901639344262296}),
     ((2.4, -3.6),
      {'total': 118,
       'success': 1,
       'success_rate': 0.00847457627118644,
       'reset': 59,
       'reset_rate': 0.5,
       'normal': 58,
       'normal_rate': 0.4915254237288136}),
     ((2.8, -3.2),
      {'total': 122,
       'success': 1,
       'success_rate': 0.00819672131147541,
       'reset': 69,
       'reset_rate': 0.5655737704918032,
       'normal': 52,
       'normal_rate': 0.4262295081967213}),
     ((2.4, -3.2),
      {'total': 125,
       'success': 1,
       'success_rate': 0.008,
       'reset': 76,
       'reset_rate': 0.608,
       'normal': 48,
       'normal_rate': 0.384}),
     ((2.0, -2.0000000000000004),
      {'total': 128,
       'success': 1,
       'success_rate': 0.0078125,
       'reset': 86,
       'reset_rate': 0.671875,
       'normal': 41,
       'normal_rate': 0.3203125}),
     ((3.5999999999999996, -2.0000000000000004),
      {'total': 101,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 101,
       'normal_rate': 1.0}),
     ((3.5999999999999996, -2.4000000000000004),
      {'total': 101,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 101,
       'normal_rate': 1.0}),
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
       'reset': 1,
       'reset_rate': 0.009900990099009901,
       'normal': 100,
       'normal_rate': 0.9900990099009901}),
     ((3.5999999999999996, -3.6),
      {'total': 115,
       'success': 0,
       'success_rate': 0.0,
       'reset': 42,
       'reset_rate': 0.3652173913043478,
       'normal': 73,
       'normal_rate': 0.6347826086956522}),
     ((3.5999999999999996, -4),
      {'total': 118,
       'success': 0,
       'success_rate': 0.0,
       'reset': 56,
       'reset_rate': 0.4745762711864407,
       'normal': 62,
       'normal_rate': 0.5254237288135594}),
     ((3.1999999999999997, -2.0000000000000004),
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
       'reset': 1,
       'reset_rate': 0.009900990099009901,
       'normal': 100,
       'normal_rate': 0.9900990099009901}),
     ((3.1999999999999997, -3.2),
      {'total': 116,
       'success': 0,
       'success_rate': 0.0,
       'reset': 51,
       'reset_rate': 0.4396551724137931,
       'normal': 65,
       'normal_rate': 0.5603448275862069}),
     ((3.1999999999999997, -3.6),
      {'total': 120,
       'success': 0,
       'success_rate': 0.0,
       'reset': 61,
       'reset_rate': 0.5083333333333333,
       'normal': 59,
       'normal_rate': 0.49166666666666664}),
     ((3.1999999999999997, -4),
      {'total': 118,
       'success': 0,
       'success_rate': 0.0,
       'reset': 56,
       'reset_rate': 0.4745762711864407,
       'normal': 62,
       'normal_rate': 0.5254237288135594}),
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
       'reset': 1,
       'reset_rate': 0.009900990099009901,
       'normal': 100,
       'normal_rate': 0.9900990099009901}),
     ((2.8, -2.8000000000000003),
      {'total': 124,
       'success': 0,
       'success_rate': 0.0,
       'reset': 66,
       'reset_rate': 0.532258064516129,
       'normal': 58,
       'normal_rate': 0.46774193548387094}),
     ((2.8, -3.6),
      {'total': 119,
       'success': 0,
       'success_rate': 0.0,
       'reset': 60,
       'reset_rate': 0.5042016806722689,
       'normal': 59,
       'normal_rate': 0.4957983193277311}),
     ((2.8, -4),
      {'total': 118,
       'success': 0,
       'success_rate': 0.0,
       'reset': 52,
       'reset_rate': 0.4406779661016949,
       'normal': 66,
       'normal_rate': 0.559322033898305}),
     ((2.4, -2.0000000000000004),
      {'total': 101,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 101,
       'normal_rate': 1.0}),
     ((2.4, -2.8000000000000003),
      {'total': 128,
       'success': 0,
       'success_rate': 0.0,
       'reset': 87,
       'reset_rate': 0.6796875,
       'normal': 41,
       'normal_rate': 0.3203125}),
     ((2.4, -4),
      {'total': 118,
       'success': 0,
       'success_rate': 0.0,
       'reset': 54,
       'reset_rate': 0.4576271186440678,
       'normal': 64,
       'normal_rate': 0.5423728813559322}),
     ((2.0, -2.4000000000000004),
      {'total': 132,
       'success': 0,
       'success_rate': 0.0,
       'reset': 93,
       'reset_rate': 0.7045454545454546,
       'normal': 39,
       'normal_rate': 0.29545454545454547}),
     ((2.0, -2.8000000000000003),
      {'total': 125,
       'success': 0,
       'success_rate': 0.0,
       'reset': 78,
       'reset_rate': 0.624,
       'normal': 47,
       'normal_rate': 0.376}),
     ((2.0, -3.2),
      {'total': 122,
       'success': 0,
       'success_rate': 0.0,
       'reset': 70,
       'reset_rate': 0.5737704918032787,
       'normal': 52,
       'normal_rate': 0.4262295081967213}),
     ((2.0, -3.6),
      {'total': 118,
       'success': 0,
       'success_rate': 0.0,
       'reset': 58,
       'reset_rate': 0.4915254237288136,
       'normal': 60,
       'normal_rate': 0.5084745762711864}),
     ((2.0, -4),
      {'total': 118,
       'success': 0,
       'success_rate': 0.0,
       'reset': 53,
       'reset_rate': 0.4491525423728814,
       'normal': 65,
       'normal_rate': 0.5508474576271186}),
     ((1.6, -2.4000000000000004),
      {'total': 130,
       'success': 0,
       'success_rate': 0.0,
       'reset': 92,
       'reset_rate': 0.7076923076923077,
       'normal': 38,
       'normal_rate': 0.2923076923076923}),
     ((1.6, -2.8000000000000003),
      {'total': 127,
       'success': 0,
       'success_rate': 0.0,
       'reset': 86,
       'reset_rate': 0.6771653543307087,
       'normal': 41,
       'normal_rate': 0.3228346456692913}),
     ((1.6, -3.2),
      {'total': 131,
       'success': 0,
       'success_rate': 0.0,
       'reset': 87,
       'reset_rate': 0.6641221374045801,
       'normal': 44,
       'normal_rate': 0.33587786259541985}),
     ((1.6, -3.6),
      {'total': 123,
       'success': 0,
       'success_rate': 0.0,
       'reset': 71,
       'reset_rate': 0.5772357723577236,
       'normal': 52,
       'normal_rate': 0.42276422764227645}),
     ((1.6, -4),
      {'total': 125,
       'success': 0,
       'success_rate': 0.0,
       'reset': 70,
       'reset_rate': 0.56,
       'normal': 55,
       'normal_rate': 0.44}),
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
      {'total': 103,
       'success': 0,
       'success_rate': 0.0,
       'reset': 8,
       'reset_rate': 0.07766990291262135,
       'normal': 95,
       'normal_rate': 0.9223300970873787}),
     ((0.8, -2.4000000000000004),
      {'total': 102,
       'success': 0,
       'success_rate': 0.0,
       'reset': 4,
       'reset_rate': 0.0392156862745098,
       'normal': 98,
       'normal_rate': 0.9607843137254902}),
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
      {'total': 104,
       'success': 0,
       'success_rate': 0.0,
       'reset': 17,
       'reset_rate': 0.16346153846153846,
       'normal': 87,
       'normal_rate': 0.8365384615384616}),
     ((0.8, -4),
      {'total': 102,
       'success': 0,
       'success_rate': 0.0,
       'reset': 9,
       'reset_rate': 0.08823529411764706,
       'normal': 93,
       'normal_rate': 0.9117647058823529})]




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

