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
    scope.adc.trig\_count                     changed from 10858414                  to 21862926                 
    scope.clock.adc\_src                      changed from clkgen\_x1                 to clkgen\_x4                
    scope.clock.adc\_freq                     changed from 11856433                  to 29842071                 
    scope.clock.adc\_rate                     changed from 11856433.0                to 29842071.0               
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
    avr-gcc (GCC) 5.4.0
    Copyright (C) 2015 Free Software Foundation, Inc.
    This is free software; see the source for copying conditions.  There is NO
    warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
    
    Welcome to another exciting ChipWhisperer target build!!
    Size after:
    +--------------------------------------------------------
    + Built for platform CW-Lite XMEGA with:
    + CRYPTO\_TARGET = NONE
       text	   data	    bss	    dec	    hex	filename
       2792	      6	     82	   2880	    b40	simpleserial-glitch-CWLITEXMEGA.elf
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

    XMEGA Programming flash...
    XMEGA Reading flash...
    Verified flash OK, 2797 bytes




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

    scope.clock.adc\_freq                     changed from 29842071                  to 29538459                 
    scope.clock.adc\_rate                     changed from 29842071.0                to 29538459.0               



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
        <div id='de022c1d-6969-48b9-ad22-0f4871b92361'>
      <div id="e7c5f8e1-cec3-43a3-9cfc-1755f866d7b9" data-root-id="de022c1d-6969-48b9-ad22-0f4871b92361" style="display: contents;"></div>
    </div>
    <script type="application/javascript">(function(root) {
      var docs_json = {"200781c2-5a63-434b-86f5-2f0c7129cf58":{"version":"3.6.1","title":"Bokeh Application","roots":[{"type":"object","name":"panel.models.browser.BrowserInfo","id":"de022c1d-6969-48b9-ad22-0f4871b92361"},{"type":"object","name":"panel.models.comm_manager.CommManager","id":"6d7cc32c-5492-4aaa-85fd-3b7aaa8f61c2","attributes":{"plot_id":"de022c1d-6969-48b9-ad22-0f4871b92361","comm_id":"32592970b34342579950a55dd0ec4c21","client_comm_id":"79a21e137d244531be140fc3449d86ac"}}],"defs":[{"type":"model","name":"ReactiveHTML1"},{"type":"model","name":"FlexBox1","properties":[{"name":"align_content","kind":"Any","default":"flex-start"},{"name":"align_items","kind":"Any","default":"flex-start"},{"name":"flex_direction","kind":"Any","default":"row"},{"name":"flex_wrap","kind":"Any","default":"wrap"},{"name":"gap","kind":"Any","default":""},{"name":"justify_content","kind":"Any","default":"flex-start"}]},{"type":"model","name":"FloatPanel1","properties":[{"name":"config","kind":"Any","default":{"type":"map"}},{"name":"contained","kind":"Any","default":true},{"name":"position","kind":"Any","default":"right-top"},{"name":"offsetx","kind":"Any","default":null},{"name":"offsety","kind":"Any","default":null},{"name":"theme","kind":"Any","default":"primary"},{"name":"status","kind":"Any","default":"normalized"}]},{"type":"model","name":"GridStack1","properties":[{"name":"mode","kind":"Any","default":"warn"},{"name":"ncols","kind":"Any","default":null},{"name":"nrows","kind":"Any","default":null},{"name":"allow_resize","kind":"Any","default":true},{"name":"allow_drag","kind":"Any","default":true},{"name":"state","kind":"Any","default":[]}]},{"type":"model","name":"drag1","properties":[{"name":"slider_width","kind":"Any","default":5},{"name":"slider_color","kind":"Any","default":"black"},{"name":"value","kind":"Any","default":50}]},{"type":"model","name":"click1","properties":[{"name":"terminal_output","kind":"Any","default":""},{"name":"debug_name","kind":"Any","default":""},{"name":"clears","kind":"Any","default":0}]},{"type":"model","name":"FastWrapper1","properties":[{"name":"object","kind":"Any","default":null},{"name":"style","kind":"Any","default":null}]},{"type":"model","name":"NotificationAreaBase1","properties":[{"name":"js_events","kind":"Any","default":{"type":"map"}},{"name":"position","kind":"Any","default":"bottom-right"},{"name":"_clear","kind":"Any","default":0}]},{"type":"model","name":"NotificationArea1","properties":[{"name":"js_events","kind":"Any","default":{"type":"map"}},{"name":"notifications","kind":"Any","default":[]},{"name":"position","kind":"Any","default":"bottom-right"},{"name":"_clear","kind":"Any","default":0},{"name":"types","kind":"Any","default":[{"type":"map","entries":[["type","warning"],["background","#ffc107"],["icon",{"type":"map","entries":[["className","fas fa-exclamation-triangle"],["tagName","i"],["color","white"]]}]]},{"type":"map","entries":[["type","info"],["background","#007bff"],["icon",{"type":"map","entries":[["className","fas fa-info-circle"],["tagName","i"],["color","white"]]}]]}]}]},{"type":"model","name":"Notification","properties":[{"name":"background","kind":"Any","default":null},{"name":"duration","kind":"Any","default":3000},{"name":"icon","kind":"Any","default":null},{"name":"message","kind":"Any","default":""},{"name":"notification_type","kind":"Any","default":null},{"name":"_destroyed","kind":"Any","default":false}]},{"type":"model","name":"TemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"BootstrapTemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"TemplateEditor1","properties":[{"name":"layout","kind":"Any","default":[]}]},{"type":"model","name":"MaterialTemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"ReactiveESM1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"JSComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"ReactComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"AnyWidgetComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"request_value1","properties":[{"name":"fill","kind":"Any","default":"none"},{"name":"_synced","kind":"Any","default":null},{"name":"_request_sync","kind":"Any","default":0}]}]}};
      var render_items = [{"docid":"200781c2-5a63-434b-86f5-2f0c7129cf58","roots":{"de022c1d-6969-48b9-ad22-0f4871b92361":"e7c5f8e1-cec3-43a3-9cfc-1755f866d7b9"},"root_ids":["de022c1d-6969-48b9-ad22-0f4871b92361"]}];
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
        <div id='89c67481-06d5-4b07-b9c8-4f5dce6a048b'>
      <div id="dd89bdc7-4b8f-4252-a614-bae01bae2b24" data-root-id="89c67481-06d5-4b07-b9c8-4f5dce6a048b" style="display: contents;"></div>
    </div>
    <script type="application/javascript">(function(root) {
      var docs_json = {"379fe16d-bbaf-4a3c-adab-335007aedb35":{"version":"3.6.1","title":"Bokeh Application","roots":[{"type":"object","name":"Row","id":"89c67481-06d5-4b07-b9c8-4f5dce6a048b","attributes":{"name":"Row00289","stylesheets":["\n:host(.pn-loading):before, .pn-loading:before {\n  background-color: #c3c3c3;\n  mask-size: auto calc(min(50%, 400px));\n  -webkit-mask-size: auto calc(min(50%, 400px));\n}",{"type":"object","name":"ImportedStyleSheet","id":"38b1426c-9f24-401a-8c2f-f2b22947e985","attributes":{"url":"https://cdn.holoviz.org/panel/1.5.4/dist/css/loading.css"}},{"type":"object","name":"ImportedStyleSheet","id":"e5fe9ec3-0aa6-4494-acb1-3e44f873b20c","attributes":{"url":"https://cdn.holoviz.org/panel/1.5.4/dist/css/listpanel.css"}},{"type":"object","name":"ImportedStyleSheet","id":"b073215c-5b63-4459-9f2e-1e7924cf411c","attributes":{"url":"https://cdn.holoviz.org/panel/1.5.4/dist/bundled/theme/default.css"}},{"type":"object","name":"ImportedStyleSheet","id":"76379e9d-e8e2-47f9-b406-33e2a6ea8497","attributes":{"url":"https://cdn.holoviz.org/panel/1.5.4/dist/bundled/theme/native.css"}}],"min_width":800,"margin":0,"sizing_mode":"stretch_width","align":"start","children":[{"type":"object","name":"Spacer","id":"9f24b9fc-a85a-49fc-9004-3a339913dc87","attributes":{"name":"HSpacer00293","stylesheets":["\n:host(.pn-loading):before, .pn-loading:before {\n  background-color: #c3c3c3;\n  mask-size: auto calc(min(50%, 400px));\n  -webkit-mask-size: auto calc(min(50%, 400px));\n}",{"id":"38b1426c-9f24-401a-8c2f-f2b22947e985"},{"id":"b073215c-5b63-4459-9f2e-1e7924cf411c"},{"id":"76379e9d-e8e2-47f9-b406-33e2a6ea8497"}],"margin":0,"sizing_mode":"stretch_width","align":"start"}},{"type":"object","name":"Figure","id":"303e6443-3966-43f9-b294-335d2f597eb7","attributes":{"js_event_callbacks":{"type":"map","entries":[["reset",[{"type":"object","name":"CustomJS","id":"e9c6f2e8-f3e5-4dad-a093-3a2e0bb7062b","attributes":{"code":"export default (_, cb_obj) => { cb_obj.origin.hold_render = false }"}}]]]},"subscribed_events":{"type":"set","entries":["rangesupdate","reset"]},"width":800,"margin":[5,10],"sizing_mode":"fixed","align":"start","x_range":{"type":"object","name":"Range1d","id":"c2e3a9b8-67d2-4bf6-b24a-1fd1f4e90fa8","attributes":{"name":"ext_offset","tags":[[["ext_offset",null]],[]]}},"y_range":{"type":"object","name":"Range1d","id":"db0f104d-3999-499f-a594-68f5216b3018","attributes":{"name":"offset","tags":[[["offset",null]],{"type":"map","entries":[["invert_yaxis",false],["autorange",false]]}]}},"x_scale":{"type":"object","name":"LinearScale","id":"cffd6eb6-3690-4e4e-adba-985efc755adc"},"y_scale":{"type":"object","name":"LinearScale","id":"88522451-032a-4744-8c7c-eaeab6bd38f4"},"title":{"type":"object","name":"Title","id":"9b557b5f-03ba-41fc-9b90-d844490d4d9e","attributes":{"text_color":"black","text_font_size":"12pt"}},"renderers":[{"type":"object","name":"GlyphRenderer","id":"61eca273-3f47-4957-8a1c-5c637c3bafbd","attributes":{"data_source":{"type":"object","name":"ColumnDataSource","id":"2652dcf7-ebcf-4c2e-a5f2-1401dd0bbfb6","attributes":{"selected":{"type":"object","name":"Selection","id":"d0a1c341-0e7d-4ea9-81c1-ca8087ca9d6b","attributes":{"indices":[],"line_indices":[]}},"selection_policy":{"type":"object","name":"UnionRenderers","id":"5f49b6b1-56f4-45ef-9e5c-6ce2100761ec"},"data":{"type":"map","entries":[["ext_offset",{"type":"ndarray","array":{"type":"bytes","data":""},"shape":[0],"dtype":"float64","order":"little"}],["offset",{"type":"ndarray","array":{"type":"bytes","data":""},"shape":[0],"dtype":"float64","order":"little"}]]}}},"view":{"type":"object","name":"CDSView","id":"8d744ebf-c152-46f5-9221-5efd2ee1344b","attributes":{"filter":{"type":"object","name":"AllIndices","id":"5914fa4b-8541-4a43-bdd7-5d759dfc6002"}}},"glyph":{"type":"object","name":"Scatter","id":"70a09cc9-bc95-4e55-841c-b0d5aa5f4736","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"ext_offset"},"y":{"type":"field","field":"offset"},"size":{"type":"value","value":10},"line_color":{"type":"value","value":"#007f00"},"fill_color":{"type":"value","value":"#007f00"},"hatch_color":{"type":"value","value":"#007f00"},"marker":{"type":"value","value":"cross"}}},"selection_glyph":{"type":"object","name":"Scatter","id":"448fc408-e390-4430-bb23-77e5b31990a0","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"ext_offset"},"y":{"type":"field","field":"offset"},"size":{"type":"value","value":10},"angle":{"type":"value","value":0.0},"line_color":{"type":"value","value":"#007f00"},"line_alpha":{"type":"value","value":1.0},"line_width":{"type":"value","value":1},"line_join":{"type":"value","value":"bevel"},"line_cap":{"type":"value","value":"butt"},"line_dash":{"type":"value","value":[]},"line_dash_offset":{"type":"value","value":0},"fill_color":{"type":"value","value":"#007f00"},"fill_alpha":{"type":"value","value":1.0},"hatch_color":{"type":"value","value":"#007f00"},"hatch_alpha":{"type":"value","value":1.0},"hatch_scale":{"type":"value","value":12.0},"hatch_pattern":{"type":"value","value":null},"hatch_weight":{"type":"value","value":1.0},"marker":{"type":"value","value":"cross"}}},"nonselection_glyph":{"type":"object","name":"Scatter","id":"a3636bfb-6a5f-4869-b2c7-1245b73b7cbb","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"ext_offset"},"y":{"type":"field","field":"offset"},"size":{"type":"value","value":10},"line_color":{"type":"value","value":"#007f00"},"line_alpha":{"type":"value","value":0.1},"fill_color":{"type":"value","value":"#007f00"},"fill_alpha":{"type":"value","value":0.1},"hatch_color":{"type":"value","value":"#007f00"},"hatch_alpha":{"type":"value","value":0.1},"marker":{"type":"value","value":"cross"}}},"muted_glyph":{"type":"object","name":"Scatter","id":"2360b652-f818-4331-8bd7-27f5eb204aab","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"ext_offset"},"y":{"type":"field","field":"offset"},"size":{"type":"value","value":10},"line_color":{"type":"value","value":"#007f00"},"line_alpha":{"type":"value","value":0.2},"fill_color":{"type":"value","value":"#007f00"},"fill_alpha":{"type":"value","value":0.2},"hatch_color":{"type":"value","value":"#007f00"},"hatch_alpha":{"type":"value","value":0.2},"marker":{"type":"value","value":"cross"}}}}},{"type":"object","name":"GlyphRenderer","id":"2961fe9a-d2c0-406d-80aa-0cbf3c802424","attributes":{"data_source":{"type":"object","name":"ColumnDataSource","id":"571e689e-76ec-4f00-b13d-bebdd6c1caa8","attributes":{"selected":{"type":"object","name":"Selection","id":"12a5103d-4535-4cab-9bf3-1ba86bede9eb","attributes":{"indices":[],"line_indices":[]}},"selection_policy":{"type":"object","name":"UnionRenderers","id":"e8f398b4-85c3-40ce-ba4b-d790ebce4f98"},"data":{"type":"map","entries":[["ext_offset",{"type":"ndarray","array":{"type":"bytes","data":""},"shape":[0],"dtype":"float64","order":"little"}],["offset",{"type":"ndarray","array":{"type":"bytes","data":""},"shape":[0],"dtype":"float64","order":"little"}]]}}},"view":{"type":"object","name":"CDSView","id":"0aaeb997-3292-4887-b3c1-e5dfc810931e","attributes":{"filter":{"type":"object","name":"AllIndices","id":"c6ea3fa4-fd0e-4a7a-8695-e887ce80996f"}}},"glyph":{"type":"object","name":"Scatter","id":"084058e3-366d-400a-a4ab-90fb98b9512b","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"ext_offset"},"y":{"type":"field","field":"offset"},"size":{"type":"value","value":10},"angle":{"type":"value","value":0.7853981633974483},"line_color":{"type":"value","value":"#ff0000"},"fill_color":{"type":"value","value":"#ff0000"},"hatch_color":{"type":"value","value":"#ff0000"},"marker":{"type":"value","value":"cross"}}},"selection_glyph":{"type":"object","name":"Scatter","id":"ddd51710-3213-4a62-9785-3003627d67dc","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"ext_offset"},"y":{"type":"field","field":"offset"},"size":{"type":"value","value":10},"angle":{"type":"value","value":0.7853981633974483},"line_color":{"type":"value","value":"#ff0000"},"line_alpha":{"type":"value","value":1.0},"line_width":{"type":"value","value":1},"line_join":{"type":"value","value":"bevel"},"line_cap":{"type":"value","value":"butt"},"line_dash":{"type":"value","value":[]},"line_dash_offset":{"type":"value","value":0},"fill_color":{"type":"value","value":"#ff0000"},"fill_alpha":{"type":"value","value":1.0},"hatch_color":{"type":"value","value":"#ff0000"},"hatch_alpha":{"type":"value","value":1.0},"hatch_scale":{"type":"value","value":12.0},"hatch_pattern":{"type":"value","value":null},"hatch_weight":{"type":"value","value":1.0},"marker":{"type":"value","value":"cross"}}},"nonselection_glyph":{"type":"object","name":"Scatter","id":"eaf458b5-7b78-4b15-816e-e79013db8d66","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"ext_offset"},"y":{"type":"field","field":"offset"},"size":{"type":"value","value":10},"angle":{"type":"value","value":0.7853981633974483},"line_color":{"type":"value","value":"#ff0000"},"line_alpha":{"type":"value","value":0.1},"fill_color":{"type":"value","value":"#ff0000"},"fill_alpha":{"type":"value","value":0.1},"hatch_color":{"type":"value","value":"#ff0000"},"hatch_alpha":{"type":"value","value":0.1},"marker":{"type":"value","value":"cross"}}},"muted_glyph":{"type":"object","name":"Scatter","id":"516f585b-c739-43e7-a590-5e57ae6a8547","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"ext_offset"},"y":{"type":"field","field":"offset"},"size":{"type":"value","value":10},"angle":{"type":"value","value":0.7853981633974483},"line_color":{"type":"value","value":"#ff0000"},"line_alpha":{"type":"value","value":0.2},"fill_color":{"type":"value","value":"#ff0000"},"fill_alpha":{"type":"value","value":0.2},"hatch_color":{"type":"value","value":"#ff0000"},"hatch_alpha":{"type":"value","value":0.2},"marker":{"type":"value","value":"cross"}}}}}],"toolbar":{"type":"object","name":"Toolbar","id":"a4153318-ab78-4c26-b1e2-f37b81497186","attributes":{"tools":[{"type":"object","name":"WheelZoomTool","id":"7d4f5315-e344-4f18-b124-1f1cc9a8f5b6","attributes":{"tags":["hv_created"],"renderers":"auto","zoom_together":"none"}},{"type":"object","name":"HoverTool","id":"6c10274a-ddf9-4a8b-9888-414458dadee0","attributes":{"tags":["hv_created"],"renderers":[{"id":"61eca273-3f47-4957-8a1c-5c637c3bafbd"},{"id":"2961fe9a-d2c0-406d-80aa-0cbf3c802424"}],"tooltips":[["ext_offset","@{ext_offset}"],["offset","@{offset}"]]}},{"type":"object","name":"SaveTool","id":"6522fea4-daa2-4acb-9394-ff3328ba2502"},{"type":"object","name":"PanTool","id":"26cb019c-c480-4cf6-9ca7-92b7741fe34e"},{"type":"object","name":"BoxZoomTool","id":"982b866e-7740-4eff-a569-933a2677722a","attributes":{"overlay":{"type":"object","name":"BoxAnnotation","id":"db8c7e6c-175e-430b-bfe2-b96f0f33a796","attributes":{"syncable":false,"line_color":"black","line_alpha":1.0,"line_width":2,"line_dash":[4,4],"fill_color":"lightgrey","fill_alpha":0.5,"level":"overlay","visible":false,"left":{"type":"number","value":"nan"},"right":{"type":"number","value":"nan"},"top":{"type":"number","value":"nan"},"bottom":{"type":"number","value":"nan"},"left_units":"canvas","right_units":"canvas","top_units":"canvas","bottom_units":"canvas","handles":{"type":"object","name":"BoxInteractionHandles","id":"8ffdceb3-ef33-45ff-98ee-c39653c5f023","attributes":{"all":{"type":"object","name":"AreaVisuals","id":"fa8624da-4cad-4642-8bc5-661382bae882","attributes":{"fill_color":"white","hover_fill_color":"lightgray"}}}}}}}},{"type":"object","name":"ResetTool","id":"f75262d7-db6a-4936-9cb9-f7283a483272"}],"active_drag":{"id":"26cb019c-c480-4cf6-9ca7-92b7741fe34e"},"active_scroll":{"id":"7d4f5315-e344-4f18-b124-1f1cc9a8f5b6"}}},"left":[{"type":"object","name":"LinearAxis","id":"3c66bf06-b413-4117-8529-a1dc861ead9b","attributes":{"ticker":{"type":"object","name":"BasicTicker","id":"5b2d7040-b829-4c94-8749-61d8fa73fc7b","attributes":{"mantissas":[1,2,5]}},"formatter":{"type":"object","name":"BasicTickFormatter","id":"c516c04f-d676-4089-8177-d06d931d8642"},"axis_label":"offset","major_label_policy":{"type":"object","name":"AllLabels","id":"bf96a0b0-5e66-49f0-9625-a07cd4ed8ac7"}}}],"below":[{"type":"object","name":"LinearAxis","id":"d7c488ea-e6ee-48f0-a783-8e2fa7221949","attributes":{"ticker":{"type":"object","name":"BasicTicker","id":"7f62d5b7-948e-4d6c-883a-bcdcde6b5d1d","attributes":{"mantissas":[1,2,5]}},"formatter":{"type":"object","name":"BasicTickFormatter","id":"d63a60fb-8798-4e15-bad6-21d48cf49d3f"},"axis_label":"ext_offset","major_label_policy":{"type":"object","name":"AllLabels","id":"437502e2-988f-43a0-98f3-3ad8e9b355e5"}}}],"center":[{"type":"object","name":"Grid","id":"70647bd3-7393-4239-99a6-6fa8f6a82905","attributes":{"axis":{"id":"d7c488ea-e6ee-48f0-a783-8e2fa7221949"},"grid_line_color":null}},{"type":"object","name":"Grid","id":"ad569e37-bbd5-4542-8f3c-9a7cabec0670","attributes":{"dimension":1,"axis":{"id":"3c66bf06-b413-4117-8529-a1dc861ead9b"},"grid_line_color":null}}],"min_border_top":10,"min_border_bottom":10,"min_border_left":10,"min_border_right":10,"output_backend":"webgl"}},{"type":"object","name":"Spacer","id":"ea9651c2-70d4-4359-a9c8-99996634d9c8","attributes":{"name":"HSpacer00294","stylesheets":["\n:host(.pn-loading):before, .pn-loading:before {\n  background-color: #c3c3c3;\n  mask-size: auto calc(min(50%, 400px));\n  -webkit-mask-size: auto calc(min(50%, 400px));\n}",{"id":"38b1426c-9f24-401a-8c2f-f2b22947e985"},{"id":"b073215c-5b63-4459-9f2e-1e7924cf411c"},{"id":"76379e9d-e8e2-47f9-b406-33e2a6ea8497"}],"margin":0,"sizing_mode":"stretch_width","align":"start"}}]}},{"type":"object","name":"panel.models.comm_manager.CommManager","id":"8fb22e50-b483-4584-adfb-a4ad54dc9c27","attributes":{"plot_id":"89c67481-06d5-4b07-b9c8-4f5dce6a048b","comm_id":"c7b1bce19f1e4dd79ad166224c111e5f","client_comm_id":"8276e8370d9442378729e00636ebe9cc"}}],"defs":[{"type":"model","name":"ReactiveHTML1"},{"type":"model","name":"FlexBox1","properties":[{"name":"align_content","kind":"Any","default":"flex-start"},{"name":"align_items","kind":"Any","default":"flex-start"},{"name":"flex_direction","kind":"Any","default":"row"},{"name":"flex_wrap","kind":"Any","default":"wrap"},{"name":"gap","kind":"Any","default":""},{"name":"justify_content","kind":"Any","default":"flex-start"}]},{"type":"model","name":"FloatPanel1","properties":[{"name":"config","kind":"Any","default":{"type":"map"}},{"name":"contained","kind":"Any","default":true},{"name":"position","kind":"Any","default":"right-top"},{"name":"offsetx","kind":"Any","default":null},{"name":"offsety","kind":"Any","default":null},{"name":"theme","kind":"Any","default":"primary"},{"name":"status","kind":"Any","default":"normalized"}]},{"type":"model","name":"GridStack1","properties":[{"name":"mode","kind":"Any","default":"warn"},{"name":"ncols","kind":"Any","default":null},{"name":"nrows","kind":"Any","default":null},{"name":"allow_resize","kind":"Any","default":true},{"name":"allow_drag","kind":"Any","default":true},{"name":"state","kind":"Any","default":[]}]},{"type":"model","name":"drag1","properties":[{"name":"slider_width","kind":"Any","default":5},{"name":"slider_color","kind":"Any","default":"black"},{"name":"value","kind":"Any","default":50}]},{"type":"model","name":"click1","properties":[{"name":"terminal_output","kind":"Any","default":""},{"name":"debug_name","kind":"Any","default":""},{"name":"clears","kind":"Any","default":0}]},{"type":"model","name":"FastWrapper1","properties":[{"name":"object","kind":"Any","default":null},{"name":"style","kind":"Any","default":null}]},{"type":"model","name":"NotificationAreaBase1","properties":[{"name":"js_events","kind":"Any","default":{"type":"map"}},{"name":"position","kind":"Any","default":"bottom-right"},{"name":"_clear","kind":"Any","default":0}]},{"type":"model","name":"NotificationArea1","properties":[{"name":"js_events","kind":"Any","default":{"type":"map"}},{"name":"notifications","kind":"Any","default":[]},{"name":"position","kind":"Any","default":"bottom-right"},{"name":"_clear","kind":"Any","default":0},{"name":"types","kind":"Any","default":[{"type":"map","entries":[["type","warning"],["background","#ffc107"],["icon",{"type":"map","entries":[["className","fas fa-exclamation-triangle"],["tagName","i"],["color","white"]]}]]},{"type":"map","entries":[["type","info"],["background","#007bff"],["icon",{"type":"map","entries":[["className","fas fa-info-circle"],["tagName","i"],["color","white"]]}]]}]}]},{"type":"model","name":"Notification","properties":[{"name":"background","kind":"Any","default":null},{"name":"duration","kind":"Any","default":3000},{"name":"icon","kind":"Any","default":null},{"name":"message","kind":"Any","default":""},{"name":"notification_type","kind":"Any","default":null},{"name":"_destroyed","kind":"Any","default":false}]},{"type":"model","name":"TemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"BootstrapTemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"TemplateEditor1","properties":[{"name":"layout","kind":"Any","default":[]}]},{"type":"model","name":"MaterialTemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"ReactiveESM1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"JSComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"ReactComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"AnyWidgetComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"request_value1","properties":[{"name":"fill","kind":"Any","default":"none"},{"name":"_synced","kind":"Any","default":null},{"name":"_request_sync","kind":"Any","default":0}]}]}};
      var render_items = [{"docid":"379fe16d-bbaf-4a3c-adab-335007aedb35","roots":{"89c67481-06d5-4b07-b9c8-4f5dce6a048b":"dd89bdc7-4b8f-4252-a614-bae01bae2b24"},"root_ids":["89c67481-06d5-4b07-b9c8-4f5dce6a048b"]}];
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
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 114
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 101
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 114
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 101
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 114
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 101
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 114
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 101
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 114
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 101
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 114
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 101
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 114
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 101
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 114
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 101
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 114
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 101
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 114
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 101
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 114
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 101
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 114
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 101
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 114
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 101
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 114
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 101
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 114
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 101
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 114
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 101
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 114
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 101
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 114
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 69, 1





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
    CWbytearray(b'01')
    44.921875 -46.875 53
    🐙CWbytearray(b'01')
    44.921875 -46.875 53
    🐙CWbytearray(b'01')
    44.921875 -46.875 53
    🐙CWbytearray(b'01')
    44.921875 -46.875 53
    🐙CWbytearray(b'01')
    44.921875 -46.875 53
    🐙CWbytearray(b'01')
    44.921875 -46.875 53
    🐙CWbytearray(b'01')
    44.921875 -46.875 53
    🐙CWbytearray(b'01')
    44.921875 -46.875 53
    🐙




.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1





.. parsed-literal::

    CWbytearray(b'01')
    44.921875 -46.875 53
    🐙




.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
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
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
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
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    CWbytearray(b'01')
    46.09375 -47.65625 54
    🐙CWbytearray(b'01')
    46.09375 -47.65625 54
    🐙CWbytearray(b'01')
    46.09375 -47.65625 54
    🐙CWbytearray(b'01')
    46.09375 -47.65625 54
    🐙CWbytearray(b'01')
    46.09375 -47.65625 54
    🐙CWbytearray(b'01')
    46.09375 -47.65625 54
    🐙CWbytearray(b'01')
    46.09375 -47.65625 54
    🐙CWbytearray(b'01')
    46.09375 -47.65625 54
    🐙CWbytearray(b'01')
    46.09375 -47.65625 54
    🐙CWbytearray(b'01')
    46.09375 -47.65625 54
    🐙




.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
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
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 69, 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 69, 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 69, 1
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
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 69, 1
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





.. parsed-literal::

    Trigger still high!
    Trigger still high!
    CWbytearray(b'01')
    46.875 -49.609375 54
    🐙




.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 69, 1
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
    CWbytearray(b'01')
    46.875 -48.828125 54
    🐙CWbytearray(b'01')
    46.875 -48.828125 54
    🐙CWbytearray(b'01')
    46.875 -48.828125 54
    🐙CWbytearray(b'01')
    46.875 -48.828125 54
    🐙CWbytearray(b'01')
    46.875 -48.828125 54
    🐙CWbytearray(b'01')
    46.875 -48.828125 54
    🐙CWbytearray(b'01')
    46.875 -48.828125 54
    🐙CWbytearray(b'01')
    46.875 -48.828125 54
    🐙




.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
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





.. parsed-literal::

    Trigger still high!
    Trigger still high!
    Trigger still high!
    CWbytearray(b'01')
    46.875 -47.65625 55
    🐙




.. parsed-literal::

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





.. parsed-literal::

    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1





.. parsed-literal::

    CWbytearray(b'01')
    48.046875 -49.609375 55
    🐙




.. parsed-literal::

    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0b
    (ChipWhisperer Scope WARNING\|File \_OpenADCInterface.py:732) Timeout in OpenADC capture(), no trigger seen! Trigger forced, data is invalid. Status: 0a





.. parsed-literal::

    Timeout - no trigger





.. parsed-literal::

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





.. parsed-literal::

    Trigger still high!
    Trigger still high!
    Trigger still high!





.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:528) Didn't get all data 7, 71
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:529) CWbytearray(b'53 45 54 20 20 20 0a')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:530) CWbytearray(b'00 52 45')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:543) Unexpected length 69, 5
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:285) Device did not ack





.. parsed-literal::

    CWbytearray(b'01')
    48.046875 -47.65625 55
    🐙




.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 6
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:288) Device reported error 0x3
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:290) CWbytearray(b'00 06 06 03 72 01 00 06 06 86 00')
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





.. parsed-literal::

    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    Trigger still high!
    CWbytearray(b'01')
    48.828125 -47.65625 55
    🐙CWbytearray(b'01')
    48.828125 -47.65625 55
    🐙




.. parsed-literal::

    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 1
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:377) Unexpected start to command 82
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:410) Unexpected length 69, 1
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:288) Device reported error 0x6
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:290) CWbytearray(b'00 65 01 06 08 00')
    (ChipWhisperer Target WARNING\|File SimpleSerial2.py:514) Unexpected start to command 6
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:288) Device reported error 0x3
    (ChipWhisperer Target ERROR\|File SimpleSerial2.py:290) CWbytearray(b'00 06 06 03 72 01 00 06 06 86 00')
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



For this lab, you may want two copies of your results; one for finding
effective ext_offsets:


**In [12]:**

.. code:: ipython3

    results = gc.calc(ignore_params=["width", "offset"], sort="success_rate")
    results


**Out [12]:**



.. parsed-literal::

    [((54,),
      {'total': 200,
       'success': 19,
       'success_rate': 0.095,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 181,
       'normal_rate': 0.905}),
     ((53,),
      {'total': 201,
       'success': 9,
       'success_rate': 0.04477611940298507,
       'reset': 1,
       'reset_rate': 0.004975124378109453,
       'normal': 191,
       'normal_rate': 0.9502487562189055}),
     ((55,),
      {'total': 200,
       'success': 5,
       'success_rate': 0.025,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 195,
       'normal_rate': 0.975}),
     ((70,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 13,
       'reset_rate': 0.065,
       'normal': 187,
       'normal_rate': 0.935}),
     ((69,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 22,
       'reset_rate': 0.11,
       'normal': 178,
       'normal_rate': 0.89}),
     ((68,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 29,
       'reset_rate': 0.145,
       'normal': 171,
       'normal_rate': 0.855}),
     ((67,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 37,
       'reset_rate': 0.185,
       'normal': 163,
       'normal_rate': 0.815}),
     ((66,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 12,
       'reset_rate': 0.06,
       'normal': 188,
       'normal_rate': 0.94}),
     ((65,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 6,
       'reset_rate': 0.03,
       'normal': 194,
       'normal_rate': 0.97}),
     ((64,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 7,
       'reset_rate': 0.035,
       'normal': 193,
       'normal_rate': 0.965}),
     ((63,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 2,
       'reset_rate': 0.01,
       'normal': 198,
       'normal_rate': 0.99}),
     ((62,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 4,
       'reset_rate': 0.02,
       'normal': 196,
       'normal_rate': 0.98}),
     ((61,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 200,
       'normal_rate': 1.0}),
     ((60,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 200,
       'normal_rate': 1.0}),
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
       'reset': 20,
       'reset_rate': 0.1,
       'normal': 180,
       'normal_rate': 0.9}),
     ((57,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 26,
       'reset_rate': 0.13,
       'normal': 174,
       'normal_rate': 0.87}),
     ((56,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 12,
       'reset_rate': 0.06,
       'normal': 188,
       'normal_rate': 0.94}),
     ((52,),
      {'total': 205,
       'success': 0,
       'success_rate': 0.0,
       'reset': 5,
       'reset_rate': 0.024390243902439025,
       'normal': 200,
       'normal_rate': 0.975609756097561}),
     ((51,),
      {'total': 220,
       'success': 0,
       'success_rate': 0.0,
       'reset': 20,
       'reset_rate': 0.09090909090909091,
       'normal': 200,
       'normal_rate': 0.9090909090909091}),
     ((50,),
      {'total': 224,
       'success': 0,
       'success_rate': 0.0,
       'reset': 25,
       'reset_rate': 0.11160714285714286,
       'normal': 199,
       'normal_rate': 0.8883928571428571}),
     ((49,),
      {'total': 207,
       'success': 0,
       'success_rate': 0.0,
       'reset': 7,
       'reset_rate': 0.033816425120772944,
       'normal': 200,
       'normal_rate': 0.966183574879227}),
     ((48,),
      {'total': 202,
       'success': 0,
       'success_rate': 0.0,
       'reset': 2,
       'reset_rate': 0.009900990099009901,
       'normal': 200,
       'normal_rate': 0.9900990099009901}),
     ((47,),
      {'total': 202,
       'success': 0,
       'success_rate': 0.0,
       'reset': 2,
       'reset_rate': 0.009900990099009901,
       'normal': 200,
       'normal_rate': 0.9900990099009901}),
     ((46,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 200,
       'normal_rate': 1.0}),
     ((45,),
      {'total': 202,
       'success': 0,
       'success_rate': 0.0,
       'reset': 3,
       'reset_rate': 0.01485148514851485,
       'normal': 199,
       'normal_rate': 0.9851485148514851}),
     ((44,),
      {'total': 209,
       'success': 0,
       'success_rate': 0.0,
       'reset': 19,
       'reset_rate': 0.09090909090909091,
       'normal': 190,
       'normal_rate': 0.9090909090909091}),
     ((43,),
      {'total': 204,
       'success': 0,
       'success_rate': 0.0,
       'reset': 9,
       'reset_rate': 0.04411764705882353,
       'normal': 195,
       'normal_rate': 0.9558823529411765}),
     ((42,),
      {'total': 201,
       'success': 0,
       'success_rate': 0.0,
       'reset': 1,
       'reset_rate': 0.004975124378109453,
       'normal': 200,
       'normal_rate': 0.9950248756218906}),
     ((41,),
      {'total': 203,
       'success': 0,
       'success_rate': 0.0,
       'reset': 11,
       'reset_rate': 0.054187192118226604,
       'normal': 192,
       'normal_rate': 0.9458128078817734}),
     ((40,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 200,
       'normal_rate': 1.0}),
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
      {'total': 201,
       'success': 0,
       'success_rate': 0.0,
       'reset': 1,
       'reset_rate': 0.004975124378109453,
       'normal': 200,
       'normal_rate': 0.9950248756218906}),
     ((35,),
      {'total': 200,
       'success': 0,
       'success_rate': 0.0,
       'reset': 1,
       'reset_rate': 0.005,
       'normal': 199,
       'normal_rate': 0.995}),
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

    [((46, -47.8),
      {'total': 698,
       'success': 10,
       'success_rate': 0.014326647564469915,
       'reset': 86,
       'reset_rate': 0.12320916905444126,
       'normal': 602,
       'normal_rate': 0.8624641833810889}),
     ((45, -46.8),
      {'total': 689,
       'success': 9,
       'success_rate': 0.013062409288824383,
       'reset': 81,
       'reset_rate': 0.11756168359941944,
       'normal': 599,
       'normal_rate': 0.8693759071117562}),
     ((47, -48.8),
      {'total': 686,
       'success': 8,
       'success_rate': 0.011661807580174927,
       'reset': 61,
       'reset_rate': 0.08892128279883382,
       'normal': 617,
       'normal_rate': 0.8994169096209913}),
     ((49, -47.8),
      {'total': 677,
       'success': 2,
       'success_rate': 0.0029542097488921715,
       'reset': 19,
       'reset_rate': 0.028064992614475627,
       'normal': 656,
       'normal_rate': 0.9689807976366323}),
     ((48, -49.8),
      {'total': 671,
       'success': 1,
       'success_rate': 0.0014903129657228018,
       'reset': 12,
       'reset_rate': 0.01788375558867362,
       'normal': 658,
       'normal_rate': 0.9806259314456036}),
     ((47, -49.8),
      {'total': 672,
       'success': 1,
       'success_rate': 0.001488095238095238,
       'reset': 8,
       'reset_rate': 0.011904761904761904,
       'normal': 663,
       'normal_rate': 0.9866071428571429}),
     ((48, -47.8),
      {'total': 673,
       'success': 1,
       'success_rate': 0.0014858841010401188,
       'reset': 14,
       'reset_rate': 0.020802377414561663,
       'normal': 658,
       'normal_rate': 0.9777117384843982}),
     ((47, -47.8),
      {'total': 673,
       'success': 1,
       'success_rate': 0.0014858841010401188,
       'reset': 11,
       'reset_rate': 0.01634472511144131,
       'normal': 661,
       'normal_rate': 0.9821693907875185}),
     ((49, -46.8),
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
     ((48, -48.8),
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
     ((46, -46.8),
      {'total': 670,
       'success': 0,
       'success_rate': 0.0,
       'reset': 0,
       'reset_rate': 0.0,
       'normal': 670,
       'normal_rate': 1.0}),
     ((46, -48.8),
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
     ((45, -47.8),
      {'total': 672,
       'success': 0,
       'success_rate': 0.0,
       'reset': 5,
       'reset_rate': 0.00744047619047619,
       'normal': 667,
       'normal_rate': 0.9925595238095238}),
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

