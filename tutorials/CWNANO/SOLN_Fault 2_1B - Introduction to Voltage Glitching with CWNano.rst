Part 2, Topic 2: Introduction to Voltage Glitching (MAIN)
=========================================================



**SUMMARY:** *While it’s not as sophisticated as the ChipWhisperer Lite
or ChipWhisperer Pro’s glitch hardware, the ChipWhisperer Nano is also
capable of glitching. In this lab, we’ll do some simple glitch tests on
the Nano’s target board, showing how to scan through glitch settings and
seeing what effect it has on the hardware.*

**LEARNING OUTCOMES:**

-  Understanding how voltage glitching can be used to disrupt a target’s
   operation
-  Scanning glitch settings to determine successful ones

Digital hardware devices have certain voltage and clock requirements to
function properly. If these requirements are not met, the device can
fail to function, or even be damage. By shorting the voltage pins of a
microcontroller for controlled, short periods of time, we can cause it
to behave erratically, clearning registers and skipping instructions.
Such attacks can be immensely powerful in practice. Consider for example
the following code from ``linux-util-2.24``:

.. code:: c

   /*
    *   auth.c -- PAM authorization code, common between chsh and chfn
    *   (c) 2012 by Cody Maloney <cmaloney@theoreticalchaos.com>
    *
    *   this program is free software.  you can redistribute it and
    *   modify it under the terms of the gnu general public license.
    *   there is no warranty.
    *
    */

   #include "auth.h"
   #include "pamfail.h"

   int auth_pam(const char *service_name, uid_t uid, const char *username)
   {
       if (uid != 0) {
           pam_handle_t *pamh = NULL;
           struct pam_conv conv = { misc_conv, NULL };
           int retcode;

           retcode = pam_start(service_name, username, &conv, &pamh);
           if (pam_fail_check(pamh, retcode))
               return FALSE;

           retcode = pam_authenticate(pamh, 0);
           if (pam_fail_check(pamh, retcode))
               return FALSE;

           retcode = pam_acct_mgmt(pamh, 0);
           if (retcode == PAM_NEW_AUTHTOK_REQD)
               retcode =
                   pam_chauthtok(pamh, PAM_CHANGE_EXPIRED_AUTHTOK);
           if (pam_fail_check(pamh, retcode))
               return FALSE;

           retcode = pam_setcred(pamh, 0);
           if (pam_fail_check(pamh, retcode))
               return FALSE;

           pam_end(pamh, 0);
           /* no need to establish a session; this isn't a
            * session-oriented activity...  */
       }
       return TRUE;
   }

This is the login code for the Linux OS. Note that if we could skip the
check of ``if (uid != 0)`` and simply branch to the end, we could avoid
having to enter a password. This is the power of glitch attacks - not
that we are breaking encryption, but simply bypassing the entire
authentication module!

Glitch Hardware
~~~~~~~~~~~~~~~

The ChipWhisperer Nano’s glitch setup is pretty simple. Like its bigger
brothers, the Lite and the Pro, it uses a MOSFET to short the
microcontroller’s voltage supply to ground:

|image0|

For the Nano, ``Glitch In`` is controlled by 2 parameters:

1. ``scope.glitch.ext_offset`` - The glitch will be inserted roughly
   ``8.3ns * scope.glitch.ext_offset``
2. ``scope.glitch.repeat`` - The glitch will be inserted for roughly
   ``8.3ns * scope.glitch.repeat``

During this lab, we’ll be varying these parameters to see if we can get
the target to mess up a calculation that it’s doing.

.. |image0| image:: https://wiki.newae.com/images/8/82/Glitch-vccglitcher.png


**In [1]:**

.. code:: ipython3

    SCOPETYPE = 'CWNANO'
    PLATFORM = 'CWNANO'
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
        scope = cw.scope(hw_location=(5, 6))
    
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
        scope = cw.scope(hw_location=(5, 6))
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
    .
    Compiling:
    Compiling:
    Compiling:
    -en     simpleserial-glitch.c ...
    -en     .././simpleserial/simpleserial.c ...
    -en     .././hal/stm32f0\_nano/stm32f0\_hal\_nano.c ...
    .
    .
    Compiling:
    Assembling: .././hal/stm32f0/stm32f0\_startup.S
    -en     .././hal/stm32f0/stm32f0\_hal\_lowlevel.c ...
    arm-none-eabi-gcc -c -mcpu=cortex-m0 -I. -x assembler-with-cpp -mthumb -mfloat-abi=soft -ffunction-sections -DF\_CPU=7372800 -Wa,-gstabs,-adhlns=objdir-CWNANO/stm32f0\_startup.lst -I.././simpleserial/ -I.././hal -I.././hal/stm32f0 -I.././hal/stm32f0/CMSIS -I.././hal/stm32f0/CMSIS/core -I.././hal/stm32f0/CMSIS/device -I.././hal/stm32f0/Legacy -I.././simpleserial/ -I.././crypto/ .././hal/stm32f0/stm32f0\_startup.S -o objdir-CWNANO/stm32f0\_startup.o
    -e Done!
    -e Done!
    -e Done!
    -e Done!
    .
    LINKING:
    -en     simpleserial-glitch-CWNANO.elf ...
    -e Done!
    .
    .
    Creating load file for Flash: simpleserial-glitch-CWNANO.hex
    Creating load file for Flash: simpleserial-glitch-CWNANO.bin
    arm-none-eabi-objcopy -O ihex -R .eeprom -R .fuse -R .lock -R .signature simpleserial-glitch-CWNANO.elf simpleserial-glitch-CWNANO.hex
    arm-none-eabi-objcopy -O binary -R .eeprom -R .fuse -R .lock -R .signature simpleserial-glitch-CWNANO.elf simpleserial-glitch-CWNANO.bin
    .
    .
    Creating load file for EEPROM: simpleserial-glitch-CWNANO.eep
    Creating Symbol Table: simpleserial-glitch-CWNANO.sym
    arm-none-eabi-objcopy -j .eeprom --set-section-flags=.eeprom="alloc,load" \
    --change-section-lma .eeprom=0 --no-change-warnings -O ihex simpleserial-glitch-CWNANO.elf simpleserial-glitch-CWNANO.eep \|\| exit 0
    arm-none-eabi-nm -n simpleserial-glitch-CWNANO.elf > simpleserial-glitch-CWNANO.sym
    .
    Creating Extended Listing: simpleserial-glitch-CWNANO.lss
    arm-none-eabi-objdump -h -S -z simpleserial-glitch-CWNANO.elf > simpleserial-glitch-CWNANO.lss
    SS\_VER set to SS\_VER\_2\_1
    SS\_VER set to SS\_VER\_2\_1
    Size after:
    +--------------------------------------------------------
    +--------------------------------------------------------
       text	   data	    bss	    dec	    hex	filename
       5380	     12	   1364	   6756	   1a64	simpleserial-glitch-CWNANO.elf
    + Default target does full rebuild each time.
    + Built for platform CWNANO Built-in Target (STM32F030) with:
    + Specify buildtarget == allquick == to avoid full rebuild
    + CRYPTO\_TARGET = NONE
    +--------------------------------------------------------
    + CRYPTO\_OPTIONS = 
    +--------------------------------------------------------




**In [4]:**

.. code:: ipython3

    fw_path = "../../../hardware/victims/firmware/simpleserial-glitch/simpleserial-glitch-{}.hex".format(PLATFORM)
    cw.program_target(scope, prog, fw_path)


**Out [4]:**



.. parsed-literal::

    Detected known STMF32: STM32F04xxx
    Extended erase (0x44), this can take ten seconds or more
    Attempting to program 5391 bytes at 0x8000000
    STM32F Programming flash...
    STM32F Reading flash...
    Verified flash OK, 5391 bytes




**In [5]:**

.. code:: ipython3

    scope.io.clkout = 7.5E6
    def reboot_flush():            
        scope.io.nrst = False
        time.sleep(0.05)
        scope.io.nrst = "high_z"
        time.sleep(0.05)
        #Flush garbage too
        target.flush()


**In [6]:**

.. code:: ipython3

    scope


**Out [6]:**



.. parsed-literal::

    ChipWhisperer Nano Device
    fw_version = 
        major = 0
        minor = 66
        debug = 0
    io = 
        tio1         = None
        tio2         = None
        tio3         = None
        tio4         = high_z
        pdid         = True
        pdic         = False
        nrst         = True
        clkout       = 7500000.0
        cdc_settings = bytearray(b'\x01\x00\x00\x00')
    adc = 
        clk_src  = int
        clk_freq = 7500000.0
        samples  = 5000
    glitch = 
        repeat     = 0
        ext_offset = 500
    errors = 
        sam_errors      = False
        sam_led_setting = Default




**In [7]:**

.. code:: ipython3

    reboot_flush()
    scope.arm()
    target.simpleserial_write("g", bytearray([]))
    scope.capture()
    val = target.simpleserial_read_witherrors('r', 4, glitch_timeout=10)#For loop check
    valid = val['valid']
    if valid:
        response = val['payload']
        raw_serial = val['full_response']
        error_code = val['rv']
    print(val)


**Out [7]:**



.. parsed-literal::

    {'valid': True, 'payload': CWbytearray(b'c4 09 00 00'), 'full\_response': CWbytearray(b'00 72 04 c4 09 00 00 15 00'), 'rv': bytearray(b'\x00')}




**In [8]:**

.. code:: ipython3

    gc = cw.GlitchController(groups=["success", "reset", "normal"], parameters=["repeat", "ext_offset"])
    gc.display_stats()


**Out [8]:**


.. parsed-literal::

    IntText(value=0, description='success count:', disabled=True)



.. parsed-literal::

    IntText(value=0, description='reset count:', disabled=True)



.. parsed-literal::

    IntText(value=0, description='normal count:', disabled=True)



.. parsed-literal::

    FloatSlider(value=0.0, continuous_update=False, description='repeat setting:', disabled=True, max=10.0, readou…



.. parsed-literal::

    FloatSlider(value=0.0, continuous_update=False, description='ext_offset setting:', disabled=True, max=10.0, re…


Some tips for finding good glitches:

1. This is a VCC line that we’re shorting, so there’s going to be stuff
   fighting against us. If your glitch is too short, it might not have
   any effect
2. Likewise, if your glitch is too long, the target will always crash.
   There’s typically a small band where you’re able to affect the
   target, but it won’t always crash it.
3. Be patient. Glitching can be somewhat inconsistant, so don’t be
   discouraged if it takes a while to see some success!


**In [9]:**

.. code:: ipython3

    gc.glitch_plot(plotdots={"success":"+g", "reset":"xr", "normal":None})


**Out [9]:**






.. raw:: html

    <div class="data_html">
        <style>*[data-root-id],
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
        <div id='p1002'>
      <div id="fbad06ec-5302-45dd-ab42-bc2d704a541e" data-root-id="p1002" style="display: contents;"></div>
    </div>
    <script type="application/javascript">(function(root) {
      var docs_json = {"2ce6d87f-ae56-4d51-95b6-cba9b1b649ee":{"version":"3.4.2","title":"Bokeh Application","roots":[{"type":"object","name":"panel.models.browser.BrowserInfo","id":"p1002"},{"type":"object","name":"panel.models.comm_manager.CommManager","id":"p1003","attributes":{"plot_id":"p1002","comm_id":"36cbaab06edc428ea913901ff9a3b3ba","client_comm_id":"cab43136be5d4cd9a89167beddbf9023"}}],"defs":[{"type":"model","name":"ReactiveHTML1"},{"type":"model","name":"FlexBox1","properties":[{"name":"align_content","kind":"Any","default":"flex-start"},{"name":"align_items","kind":"Any","default":"flex-start"},{"name":"flex_direction","kind":"Any","default":"row"},{"name":"flex_wrap","kind":"Any","default":"wrap"},{"name":"gap","kind":"Any","default":""},{"name":"justify_content","kind":"Any","default":"flex-start"}]},{"type":"model","name":"FloatPanel1","properties":[{"name":"config","kind":"Any","default":{"type":"map"}},{"name":"contained","kind":"Any","default":true},{"name":"position","kind":"Any","default":"right-top"},{"name":"offsetx","kind":"Any","default":null},{"name":"offsety","kind":"Any","default":null},{"name":"theme","kind":"Any","default":"primary"},{"name":"status","kind":"Any","default":"normalized"}]},{"type":"model","name":"GridStack1","properties":[{"name":"mode","kind":"Any","default":"warn"},{"name":"ncols","kind":"Any","default":null},{"name":"nrows","kind":"Any","default":null},{"name":"allow_resize","kind":"Any","default":true},{"name":"allow_drag","kind":"Any","default":true},{"name":"state","kind":"Any","default":[]}]},{"type":"model","name":"drag1","properties":[{"name":"slider_width","kind":"Any","default":5},{"name":"slider_color","kind":"Any","default":"black"},{"name":"value","kind":"Any","default":50}]},{"type":"model","name":"click1","properties":[{"name":"terminal_output","kind":"Any","default":""},{"name":"debug_name","kind":"Any","default":""},{"name":"clears","kind":"Any","default":0}]},{"type":"model","name":"FastWrapper1","properties":[{"name":"object","kind":"Any","default":null},{"name":"style","kind":"Any","default":null}]},{"type":"model","name":"NotificationAreaBase1","properties":[{"name":"js_events","kind":"Any","default":{"type":"map"}},{"name":"position","kind":"Any","default":"bottom-right"},{"name":"_clear","kind":"Any","default":0}]},{"type":"model","name":"NotificationArea1","properties":[{"name":"js_events","kind":"Any","default":{"type":"map"}},{"name":"notifications","kind":"Any","default":[]},{"name":"position","kind":"Any","default":"bottom-right"},{"name":"_clear","kind":"Any","default":0},{"name":"types","kind":"Any","default":[{"type":"map","entries":[["type","warning"],["background","#ffc107"],["icon",{"type":"map","entries":[["className","fas fa-exclamation-triangle"],["tagName","i"],["color","white"]]}]]},{"type":"map","entries":[["type","info"],["background","#007bff"],["icon",{"type":"map","entries":[["className","fas fa-info-circle"],["tagName","i"],["color","white"]]}]]}]}]},{"type":"model","name":"Notification","properties":[{"name":"background","kind":"Any","default":null},{"name":"duration","kind":"Any","default":3000},{"name":"icon","kind":"Any","default":null},{"name":"message","kind":"Any","default":""},{"name":"notification_type","kind":"Any","default":null},{"name":"_destroyed","kind":"Any","default":false}]},{"type":"model","name":"TemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"BootstrapTemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"TemplateEditor1","properties":[{"name":"layout","kind":"Any","default":[]}]},{"type":"model","name":"MaterialTemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"copy_to_clipboard1","properties":[{"name":"fill","kind":"Any","default":"none"},{"name":"value","kind":"Any","default":null}]}]}};
      var render_items = [{"docid":"2ce6d87f-ae56-4d51-95b6-cba9b1b649ee","roots":{"p1002":"fbad06ec-5302-45dd-ab42-bc2d704a541e"},"root_ids":["p1002"]}];
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
        <div id='p1004'>
      <div id="adc50be5-5322-4460-b525-96f6d29807fc" data-root-id="p1004" style="display: contents;"></div>
    </div>
    <script type="application/javascript">(function(root) {
      var docs_json = {"a1edbb59-ddda-4f52-85dc-40caa0bf728b":{"version":"3.4.2","title":"Bokeh Application","roots":[{"type":"object","name":"Row","id":"p1004","attributes":{"name":"Row00890","stylesheets":["\n:host(.pn-loading):before, .pn-loading:before {\n  background-color: #c3c3c3;\n  mask-size: auto calc(min(50%, 400px));\n  -webkit-mask-size: auto calc(min(50%, 400px));\n}",{"type":"object","name":"ImportedStyleSheet","id":"p1007","attributes":{"url":"https://cdn.holoviz.org/panel/1.4.4/dist/css/loading.css"}},{"type":"object","name":"ImportedStyleSheet","id":"p1079","attributes":{"url":"https://cdn.holoviz.org/panel/1.4.4/dist/css/listpanel.css"}},{"type":"object","name":"ImportedStyleSheet","id":"p1005","attributes":{"url":"https://cdn.holoviz.org/panel/1.4.4/dist/bundled/theme/default.css"}},{"type":"object","name":"ImportedStyleSheet","id":"p1006","attributes":{"url":"https://cdn.holoviz.org/panel/1.4.4/dist/bundled/theme/native.css"}}],"min_width":800,"margin":0,"sizing_mode":"stretch_width","align":"start","children":[{"type":"object","name":"Spacer","id":"p1008","attributes":{"name":"HSpacer00894","stylesheets":["\n:host(.pn-loading):before, .pn-loading:before {\n  background-color: #c3c3c3;\n  mask-size: auto calc(min(50%, 400px));\n  -webkit-mask-size: auto calc(min(50%, 400px));\n}",{"id":"p1007"},{"id":"p1005"},{"id":"p1006"}],"margin":0,"sizing_mode":"stretch_width","align":"start"}},{"type":"object","name":"Figure","id":"p1019","attributes":{"width":800,"margin":[5,10],"sizing_mode":"fixed","align":"start","x_range":{"type":"object","name":"Range1d","id":"p1009","attributes":{"tags":[[["repeat",null]],[]]}},"y_range":{"type":"object","name":"Range1d","id":"p1010","attributes":{"tags":[[["ext_offset",null]],{"type":"map","entries":[["invert_yaxis",false],["autorange",false]]}]}},"x_scale":{"type":"object","name":"LinearScale","id":"p1029"},"y_scale":{"type":"object","name":"LinearScale","id":"p1030"},"title":{"type":"object","name":"Title","id":"p1022","attributes":{"text_color":"black","text_font_size":"12pt"}},"renderers":[{"type":"object","name":"GlyphRenderer","id":"p1059","attributes":{"data_source":{"type":"object","name":"ColumnDataSource","id":"p1050","attributes":{"selected":{"type":"object","name":"Selection","id":"p1051","attributes":{"indices":[],"line_indices":[]}},"selection_policy":{"type":"object","name":"UnionRenderers","id":"p1052"},"data":{"type":"map","entries":[["repeat",{"type":"ndarray","array":{"type":"bytes","data":""},"shape":[0],"dtype":"float64","order":"little"}],["ext_offset",{"type":"ndarray","array":{"type":"bytes","data":""},"shape":[0],"dtype":"float64","order":"little"}]]}}},"view":{"type":"object","name":"CDSView","id":"p1060","attributes":{"filter":{"type":"object","name":"AllIndices","id":"p1061"}}},"glyph":{"type":"object","name":"Scatter","id":"p1056","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"repeat"},"y":{"type":"field","field":"ext_offset"},"size":{"type":"value","value":10},"line_color":{"type":"value","value":"#007f00"},"fill_color":{"type":"value","value":"#007f00"},"hatch_color":{"type":"value","value":"#007f00"},"marker":{"type":"value","value":"cross"}}},"selection_glyph":{"type":"object","name":"Scatter","id":"p1062","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"repeat"},"y":{"type":"field","field":"ext_offset"},"size":{"type":"value","value":10},"angle":{"type":"value","value":0.0},"line_color":{"type":"value","value":"#007f00"},"line_alpha":{"type":"value","value":1.0},"line_width":{"type":"value","value":1},"line_join":{"type":"value","value":"bevel"},"line_cap":{"type":"value","value":"butt"},"line_dash":{"type":"value","value":[]},"line_dash_offset":{"type":"value","value":0},"fill_color":{"type":"value","value":"#007f00"},"fill_alpha":{"type":"value","value":1.0},"hatch_color":{"type":"value","value":"#007f00"},"hatch_alpha":{"type":"value","value":1.0},"hatch_scale":{"type":"value","value":12.0},"hatch_pattern":{"type":"value","value":null},"hatch_weight":{"type":"value","value":1.0},"marker":{"type":"value","value":"cross"}}},"nonselection_glyph":{"type":"object","name":"Scatter","id":"p1057","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"repeat"},"y":{"type":"field","field":"ext_offset"},"size":{"type":"value","value":10},"line_color":{"type":"value","value":"#007f00"},"line_alpha":{"type":"value","value":0.1},"fill_color":{"type":"value","value":"#007f00"},"fill_alpha":{"type":"value","value":0.1},"hatch_color":{"type":"value","value":"#007f00"},"hatch_alpha":{"type":"value","value":0.1},"marker":{"type":"value","value":"cross"}}},"muted_glyph":{"type":"object","name":"Scatter","id":"p1058","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"repeat"},"y":{"type":"field","field":"ext_offset"},"size":{"type":"value","value":10},"line_color":{"type":"value","value":"#007f00"},"line_alpha":{"type":"value","value":0.2},"fill_color":{"type":"value","value":"#007f00"},"fill_alpha":{"type":"value","value":0.2},"hatch_color":{"type":"value","value":"#007f00"},"hatch_alpha":{"type":"value","value":0.2},"marker":{"type":"value","value":"cross"}}}}},{"type":"object","name":"GlyphRenderer","id":"p1072","attributes":{"data_source":{"type":"object","name":"ColumnDataSource","id":"p1063","attributes":{"selected":{"type":"object","name":"Selection","id":"p1064","attributes":{"indices":[],"line_indices":[]}},"selection_policy":{"type":"object","name":"UnionRenderers","id":"p1065"},"data":{"type":"map","entries":[["repeat",{"type":"ndarray","array":{"type":"bytes","data":""},"shape":[0],"dtype":"float64","order":"little"}],["ext_offset",{"type":"ndarray","array":{"type":"bytes","data":""},"shape":[0],"dtype":"float64","order":"little"}]]}}},"view":{"type":"object","name":"CDSView","id":"p1073","attributes":{"filter":{"type":"object","name":"AllIndices","id":"p1074"}}},"glyph":{"type":"object","name":"Scatter","id":"p1069","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"repeat"},"y":{"type":"field","field":"ext_offset"},"size":{"type":"value","value":10},"angle":{"type":"value","value":0.7853981633974483},"line_color":{"type":"value","value":"#ff0000"},"fill_color":{"type":"value","value":"#ff0000"},"hatch_color":{"type":"value","value":"#ff0000"},"marker":{"type":"value","value":"cross"}}},"selection_glyph":{"type":"object","name":"Scatter","id":"p1075","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"repeat"},"y":{"type":"field","field":"ext_offset"},"size":{"type":"value","value":10},"angle":{"type":"value","value":0.7853981633974483},"line_color":{"type":"value","value":"#ff0000"},"line_alpha":{"type":"value","value":1.0},"line_width":{"type":"value","value":1},"line_join":{"type":"value","value":"bevel"},"line_cap":{"type":"value","value":"butt"},"line_dash":{"type":"value","value":[]},"line_dash_offset":{"type":"value","value":0},"fill_color":{"type":"value","value":"#ff0000"},"fill_alpha":{"type":"value","value":1.0},"hatch_color":{"type":"value","value":"#ff0000"},"hatch_alpha":{"type":"value","value":1.0},"hatch_scale":{"type":"value","value":12.0},"hatch_pattern":{"type":"value","value":null},"hatch_weight":{"type":"value","value":1.0},"marker":{"type":"value","value":"cross"}}},"nonselection_glyph":{"type":"object","name":"Scatter","id":"p1070","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"repeat"},"y":{"type":"field","field":"ext_offset"},"size":{"type":"value","value":10},"angle":{"type":"value","value":0.7853981633974483},"line_color":{"type":"value","value":"#ff0000"},"line_alpha":{"type":"value","value":0.1},"fill_color":{"type":"value","value":"#ff0000"},"fill_alpha":{"type":"value","value":0.1},"hatch_color":{"type":"value","value":"#ff0000"},"hatch_alpha":{"type":"value","value":0.1},"marker":{"type":"value","value":"cross"}}},"muted_glyph":{"type":"object","name":"Scatter","id":"p1071","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"repeat"},"y":{"type":"field","field":"ext_offset"},"size":{"type":"value","value":10},"angle":{"type":"value","value":0.7853981633974483},"line_color":{"type":"value","value":"#ff0000"},"line_alpha":{"type":"value","value":0.2},"fill_color":{"type":"value","value":"#ff0000"},"fill_alpha":{"type":"value","value":0.2},"hatch_color":{"type":"value","value":"#ff0000"},"hatch_alpha":{"type":"value","value":0.2},"marker":{"type":"value","value":"cross"}}}}}],"toolbar":{"type":"object","name":"Toolbar","id":"p1028","attributes":{"tools":[{"type":"object","name":"WheelZoomTool","id":"p1014","attributes":{"tags":["hv_created"],"renderers":"auto","zoom_together":"none"}},{"type":"object","name":"HoverTool","id":"p1015","attributes":{"tags":["hv_created"],"renderers":[{"id":"p1059"},{"id":"p1072"}],"tooltips":[["repeat","@{repeat}"],["ext_offset","@{ext_offset}"]]}},{"type":"object","name":"SaveTool","id":"p1041"},{"type":"object","name":"PanTool","id":"p1042"},{"type":"object","name":"BoxZoomTool","id":"p1043","attributes":{"overlay":{"type":"object","name":"BoxAnnotation","id":"p1044","attributes":{"syncable":false,"level":"overlay","visible":false,"left":{"type":"number","value":"nan"},"right":{"type":"number","value":"nan"},"top":{"type":"number","value":"nan"},"bottom":{"type":"number","value":"nan"},"left_units":"canvas","right_units":"canvas","top_units":"canvas","bottom_units":"canvas","line_color":"black","line_alpha":1.0,"line_width":2,"line_dash":[4,4],"fill_color":"lightgrey","fill_alpha":0.5}}}},{"type":"object","name":"ResetTool","id":"p1049"}],"active_drag":{"id":"p1042"},"active_scroll":{"id":"p1014"}}},"left":[{"type":"object","name":"LinearAxis","id":"p1036","attributes":{"ticker":{"type":"object","name":"BasicTicker","id":"p1037","attributes":{"mantissas":[1,2,5]}},"formatter":{"type":"object","name":"BasicTickFormatter","id":"p1038"},"axis_label":"ext_offset","major_label_policy":{"type":"object","name":"AllLabels","id":"p1039"}}}],"below":[{"type":"object","name":"LinearAxis","id":"p1031","attributes":{"ticker":{"type":"object","name":"BasicTicker","id":"p1032","attributes":{"mantissas":[1,2,5]}},"formatter":{"type":"object","name":"BasicTickFormatter","id":"p1033"},"axis_label":"repeat","major_label_policy":{"type":"object","name":"AllLabels","id":"p1034"}}}],"center":[{"type":"object","name":"Grid","id":"p1035","attributes":{"axis":{"id":"p1031"},"grid_line_color":null}},{"type":"object","name":"Grid","id":"p1040","attributes":{"dimension":1,"axis":{"id":"p1036"},"grid_line_color":null}}],"min_border_top":10,"min_border_bottom":10,"min_border_left":10,"min_border_right":10,"output_backend":"webgl"}},{"type":"object","name":"Spacer","id":"p1077","attributes":{"name":"HSpacer00895","stylesheets":["\n:host(.pn-loading):before, .pn-loading:before {\n  background-color: #c3c3c3;\n  mask-size: auto calc(min(50%, 400px));\n  -webkit-mask-size: auto calc(min(50%, 400px));\n}",{"id":"p1007"},{"id":"p1005"},{"id":"p1006"}],"margin":0,"sizing_mode":"stretch_width","align":"start"}}]}},{"type":"object","name":"panel.models.comm_manager.CommManager","id":"p1080","attributes":{"plot_id":"p1004","comm_id":"9ef53829bb464334a08b871be6f122a5","client_comm_id":"a85f7f48c59547c5b179a495957a9249"}}],"defs":[{"type":"model","name":"ReactiveHTML1"},{"type":"model","name":"FlexBox1","properties":[{"name":"align_content","kind":"Any","default":"flex-start"},{"name":"align_items","kind":"Any","default":"flex-start"},{"name":"flex_direction","kind":"Any","default":"row"},{"name":"flex_wrap","kind":"Any","default":"wrap"},{"name":"gap","kind":"Any","default":""},{"name":"justify_content","kind":"Any","default":"flex-start"}]},{"type":"model","name":"FloatPanel1","properties":[{"name":"config","kind":"Any","default":{"type":"map"}},{"name":"contained","kind":"Any","default":true},{"name":"position","kind":"Any","default":"right-top"},{"name":"offsetx","kind":"Any","default":null},{"name":"offsety","kind":"Any","default":null},{"name":"theme","kind":"Any","default":"primary"},{"name":"status","kind":"Any","default":"normalized"}]},{"type":"model","name":"GridStack1","properties":[{"name":"mode","kind":"Any","default":"warn"},{"name":"ncols","kind":"Any","default":null},{"name":"nrows","kind":"Any","default":null},{"name":"allow_resize","kind":"Any","default":true},{"name":"allow_drag","kind":"Any","default":true},{"name":"state","kind":"Any","default":[]}]},{"type":"model","name":"drag1","properties":[{"name":"slider_width","kind":"Any","default":5},{"name":"slider_color","kind":"Any","default":"black"},{"name":"value","kind":"Any","default":50}]},{"type":"model","name":"click1","properties":[{"name":"terminal_output","kind":"Any","default":""},{"name":"debug_name","kind":"Any","default":""},{"name":"clears","kind":"Any","default":0}]},{"type":"model","name":"FastWrapper1","properties":[{"name":"object","kind":"Any","default":null},{"name":"style","kind":"Any","default":null}]},{"type":"model","name":"NotificationAreaBase1","properties":[{"name":"js_events","kind":"Any","default":{"type":"map"}},{"name":"position","kind":"Any","default":"bottom-right"},{"name":"_clear","kind":"Any","default":0}]},{"type":"model","name":"NotificationArea1","properties":[{"name":"js_events","kind":"Any","default":{"type":"map"}},{"name":"notifications","kind":"Any","default":[]},{"name":"position","kind":"Any","default":"bottom-right"},{"name":"_clear","kind":"Any","default":0},{"name":"types","kind":"Any","default":[{"type":"map","entries":[["type","warning"],["background","#ffc107"],["icon",{"type":"map","entries":[["className","fas fa-exclamation-triangle"],["tagName","i"],["color","white"]]}]]},{"type":"map","entries":[["type","info"],["background","#007bff"],["icon",{"type":"map","entries":[["className","fas fa-info-circle"],["tagName","i"],["color","white"]]}]]}]}]},{"type":"model","name":"Notification","properties":[{"name":"background","kind":"Any","default":null},{"name":"duration","kind":"Any","default":3000},{"name":"icon","kind":"Any","default":null},{"name":"message","kind":"Any","default":""},{"name":"notification_type","kind":"Any","default":null},{"name":"_destroyed","kind":"Any","default":false}]},{"type":"model","name":"TemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"BootstrapTemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"TemplateEditor1","properties":[{"name":"layout","kind":"Any","default":[]}]},{"type":"model","name":"MaterialTemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"copy_to_clipboard1","properties":[{"name":"fill","kind":"Any","default":"none"},{"name":"value","kind":"Any","default":null}]}]}};
      var render_items = [{"docid":"a1edbb59-ddda-4f52-85dc-40caa0bf728b","roots":{"p1004":"adc50be5-5322-4460-b525-96f6d29807fc"},"root_ids":["p1004"]}];
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

    from importlib import reload
    import chipwhisperer.common.results.glitch as glitch
    from tqdm.notebook import trange
    import struct
    
    g_step = 1
    
    gc.set_global_step(g_step)
    gc.set_range("repeat", 1, 10)
    gc.set_range("ext_offset", 1, 500)
    scope.glitch.repeat = 0
    
    reboot_flush()
    sample_size = 1
    for glitch_setting in gc.glitch_values():
        scope.glitch.repeat = glitch_setting[0]
        scope.glitch.ext_offset = glitch_setting[1]
        successes = 0
        resets = 0
        for i in range(3):
            target.flush()
                
            scope.arm()
            
            #Do glitch loop
            target.simpleserial_write("g", bytearray([]))
            
            ret = scope.capture()
            
            val = target.simpleserial_read_witherrors('r', 4, glitch_timeout=10)#For loop check
            
            if ret:
                print('Timeout - no trigger')
                gc.add("reset")
                resets += 1
    
                #Device is slow to boot?
                reboot_flush()
    
            else:
                if val['valid'] is False:
                    reboot_flush()
                    gc.add("reset")
                    resets += 1
                else:
                    gcnt = struct.unpack("<I", val['payload'])[0]
                    
                    if gcnt != 2500: #for loop check
                        gc.add("success")
                        print(gcnt)
                        successes += 1
                    else:
                        gc.add("normal")
        if successes > 0:                
            print("successes = {}, resets = {}, repeat = {}, ext_offset = {}".format(successes, resets, scope.glitch.repeat, scope.glitch.ext_offset))
    print("Done glitching")


**Out [10]:**



.. parsed-literal::

    Done glitching




**In [11]:**

.. code:: ipython3

    gc.plot_2d(alpha=False)


**Out [11]:**






.. raw:: html

    <div class="data_html">
        <style>*[data-root-id],
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
        <div id='p1085'>
      <div id="daef36a3-bac9-4ecf-a0f1-7aa262169c9f" data-root-id="p1085" style="display: contents;"></div>
    </div>
    <script type="application/javascript">(function(root) {
      var docs_json = {"ac16aad6-a640-47a6-b310-a4724fee6c00":{"version":"3.4.2","title":"Bokeh Application","roots":[{"type":"object","name":"panel.models.browser.BrowserInfo","id":"p1085"},{"type":"object","name":"panel.models.comm_manager.CommManager","id":"p1086","attributes":{"plot_id":"p1085","comm_id":"1052975bdef843f29d61e531866667c1","client_comm_id":"d327e33f5ec54183ae0b00ff0db86d54"}}],"defs":[{"type":"model","name":"ReactiveHTML1"},{"type":"model","name":"FlexBox1","properties":[{"name":"align_content","kind":"Any","default":"flex-start"},{"name":"align_items","kind":"Any","default":"flex-start"},{"name":"flex_direction","kind":"Any","default":"row"},{"name":"flex_wrap","kind":"Any","default":"wrap"},{"name":"gap","kind":"Any","default":""},{"name":"justify_content","kind":"Any","default":"flex-start"}]},{"type":"model","name":"FloatPanel1","properties":[{"name":"config","kind":"Any","default":{"type":"map"}},{"name":"contained","kind":"Any","default":true},{"name":"position","kind":"Any","default":"right-top"},{"name":"offsetx","kind":"Any","default":null},{"name":"offsety","kind":"Any","default":null},{"name":"theme","kind":"Any","default":"primary"},{"name":"status","kind":"Any","default":"normalized"}]},{"type":"model","name":"GridStack1","properties":[{"name":"mode","kind":"Any","default":"warn"},{"name":"ncols","kind":"Any","default":null},{"name":"nrows","kind":"Any","default":null},{"name":"allow_resize","kind":"Any","default":true},{"name":"allow_drag","kind":"Any","default":true},{"name":"state","kind":"Any","default":[]}]},{"type":"model","name":"drag1","properties":[{"name":"slider_width","kind":"Any","default":5},{"name":"slider_color","kind":"Any","default":"black"},{"name":"value","kind":"Any","default":50}]},{"type":"model","name":"click1","properties":[{"name":"terminal_output","kind":"Any","default":""},{"name":"debug_name","kind":"Any","default":""},{"name":"clears","kind":"Any","default":0}]},{"type":"model","name":"FastWrapper1","properties":[{"name":"object","kind":"Any","default":null},{"name":"style","kind":"Any","default":null}]},{"type":"model","name":"NotificationAreaBase1","properties":[{"name":"js_events","kind":"Any","default":{"type":"map"}},{"name":"position","kind":"Any","default":"bottom-right"},{"name":"_clear","kind":"Any","default":0}]},{"type":"model","name":"NotificationArea1","properties":[{"name":"js_events","kind":"Any","default":{"type":"map"}},{"name":"notifications","kind":"Any","default":[]},{"name":"position","kind":"Any","default":"bottom-right"},{"name":"_clear","kind":"Any","default":0},{"name":"types","kind":"Any","default":[{"type":"map","entries":[["type","warning"],["background","#ffc107"],["icon",{"type":"map","entries":[["className","fas fa-exclamation-triangle"],["tagName","i"],["color","white"]]}]]},{"type":"map","entries":[["type","info"],["background","#007bff"],["icon",{"type":"map","entries":[["className","fas fa-info-circle"],["tagName","i"],["color","white"]]}]]}]}]},{"type":"model","name":"Notification","properties":[{"name":"background","kind":"Any","default":null},{"name":"duration","kind":"Any","default":3000},{"name":"icon","kind":"Any","default":null},{"name":"message","kind":"Any","default":""},{"name":"notification_type","kind":"Any","default":null},{"name":"_destroyed","kind":"Any","default":false}]},{"type":"model","name":"TemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"BootstrapTemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"TemplateEditor1","properties":[{"name":"layout","kind":"Any","default":[]}]},{"type":"model","name":"MaterialTemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"copy_to_clipboard1","properties":[{"name":"fill","kind":"Any","default":"none"},{"name":"value","kind":"Any","default":null}]}]}};
      var render_items = [{"docid":"ac16aad6-a640-47a6-b310-a4724fee6c00","roots":{"p1085":"daef36a3-bac9-4ecf-a0f1-7aa262169c9f"},"root_ids":["p1085"]}];
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




.. parsed-literal::

    [0, 1]
    ['repeat', 'ext\_offset']
    (1, 1)







.. raw:: html

    <div class="data_html">
        <div id='p1087'>
      <div id="e9de8e7c-e49e-4358-bbf3-35ef87b75aaa" data-root-id="p1087" style="display: contents;"></div>
    </div>
    <script type="application/javascript">(function(root) {
      var docs_json = {"eaa5a32d-da49-4971-a1b6-823720af60ec":{"version":"3.4.2","title":"Bokeh Application","roots":[{"type":"object","name":"Row","id":"p1087","attributes":{"name":"Row01099","tags":["embedded"],"stylesheets":["\n:host(.pn-loading):before, .pn-loading:before {\n  background-color: #c3c3c3;\n  mask-size: auto calc(min(50%, 400px));\n  -webkit-mask-size: auto calc(min(50%, 400px));\n}",{"type":"object","name":"ImportedStyleSheet","id":"p1090","attributes":{"url":"https://cdn.holoviz.org/panel/1.4.4/dist/css/loading.css"}},{"type":"object","name":"ImportedStyleSheet","id":"p1180","attributes":{"url":"https://cdn.holoviz.org/panel/1.4.4/dist/css/listpanel.css"}},{"type":"object","name":"ImportedStyleSheet","id":"p1088","attributes":{"url":"https://cdn.holoviz.org/panel/1.4.4/dist/bundled/theme/default.css"}},{"type":"object","name":"ImportedStyleSheet","id":"p1089","attributes":{"url":"https://cdn.holoviz.org/panel/1.4.4/dist/bundled/theme/native.css"}}],"min_width":800,"margin":0,"sizing_mode":"stretch_width","align":"start","children":[{"type":"object","name":"Spacer","id":"p1091","attributes":{"name":"HSpacer01105","stylesheets":["\n:host(.pn-loading):before, .pn-loading:before {\n  background-color: #c3c3c3;\n  mask-size: auto calc(min(50%, 400px));\n  -webkit-mask-size: auto calc(min(50%, 400px));\n}",{"id":"p1090"},{"id":"p1088"},{"id":"p1089"}],"margin":0,"sizing_mode":"stretch_width","align":"start"}},{"type":"object","name":"Figure","id":"p1104","attributes":{"width":800,"margin":[5,10],"sizing_mode":"fixed","align":"start","x_range":{"type":"object","name":"Range1d","id":"p1092","attributes":{"tags":[[["Repeat",null]],[]]}},"y_range":{"type":"object","name":"Range1d","id":"p1093","attributes":{"tags":[[["Ext_Offset",null]],{"type":"map","entries":[["invert_yaxis",false],["autorange",false]]}]}},"x_scale":{"type":"object","name":"LinearScale","id":"p1114"},"y_scale":{"type":"object","name":"LinearScale","id":"p1115"},"title":{"type":"object","name":"Title","id":"p1107","attributes":{"text_color":"black","text_font_size":"12pt"}},"renderers":[{"type":"object","name":"GlyphRenderer","id":"p1144","attributes":{"data_source":{"type":"object","name":"ColumnDataSource","id":"p1135","attributes":{"selected":{"type":"object","name":"Selection","id":"p1136","attributes":{"indices":[],"line_indices":[]}},"selection_policy":{"type":"object","name":"UnionRenderers","id":"p1137"},"data":{"type":"map","entries":[["Repeat",{"type":"ndarray","array":{"type":"bytes","data":""},"shape":[0],"dtype":"float64","order":"little"}],["Ext_Offset",{"type":"ndarray","array":{"type":"bytes","data":""},"shape":[0],"dtype":"float64","order":"little"}]]}}},"view":{"type":"object","name":"CDSView","id":"p1145","attributes":{"filter":{"type":"object","name":"AllIndices","id":"p1146"}}},"glyph":{"type":"object","name":"Scatter","id":"p1141","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"Repeat"},"y":{"type":"field","field":"Ext_Offset"},"size":{"type":"value","value":2.449489742783178},"line_color":{"type":"value","value":"#30a2da"},"fill_color":{"type":"value","value":"#30a2da"},"hatch_color":{"type":"value","value":"#30a2da"}}},"selection_glyph":{"type":"object","name":"Scatter","id":"p1147","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"Repeat"},"y":{"type":"field","field":"Ext_Offset"},"size":{"type":"value","value":2.449489742783178},"angle":{"type":"value","value":0.0},"line_color":{"type":"value","value":"#30a2da"},"line_alpha":{"type":"value","value":1.0},"line_width":{"type":"value","value":1},"line_join":{"type":"value","value":"bevel"},"line_cap":{"type":"value","value":"butt"},"line_dash":{"type":"value","value":[]},"line_dash_offset":{"type":"value","value":0},"fill_color":{"type":"value","value":"#30a2da"},"fill_alpha":{"type":"value","value":1.0},"hatch_color":{"type":"value","value":"#30a2da"},"hatch_alpha":{"type":"value","value":1.0},"hatch_scale":{"type":"value","value":12.0},"hatch_pattern":{"type":"value","value":null},"hatch_weight":{"type":"value","value":1.0},"marker":{"type":"value","value":"circle"}}},"nonselection_glyph":{"type":"object","name":"Scatter","id":"p1142","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"Repeat"},"y":{"type":"field","field":"Ext_Offset"},"size":{"type":"value","value":2.449489742783178},"line_color":{"type":"value","value":"#30a2da"},"line_alpha":{"type":"value","value":0.1},"fill_color":{"type":"value","value":"#30a2da"},"fill_alpha":{"type":"value","value":0.1},"hatch_color":{"type":"value","value":"#30a2da"},"hatch_alpha":{"type":"value","value":0.1}}},"muted_glyph":{"type":"object","name":"Scatter","id":"p1143","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"Repeat"},"y":{"type":"field","field":"Ext_Offset"},"size":{"type":"value","value":2.449489742783178},"line_color":{"type":"value","value":"#30a2da"},"line_alpha":{"type":"value","value":0.2},"fill_color":{"type":"value","value":"#30a2da"},"fill_alpha":{"type":"value","value":0.2},"hatch_color":{"type":"value","value":"#30a2da"},"hatch_alpha":{"type":"value","value":0.2}}}}},{"type":"object","name":"GlyphRenderer","id":"p1157","attributes":{"name":"Success","data_source":{"type":"object","name":"ColumnDataSource","id":"p1148","attributes":{"selected":{"type":"object","name":"Selection","id":"p1149","attributes":{"indices":[],"line_indices":[]}},"selection_policy":{"type":"object","name":"UnionRenderers","id":"p1150"},"data":{"type":"map","entries":[["repeat",{"type":"ndarray","array":{"type":"bytes","data":""},"shape":[0],"dtype":"float64","order":"little"}],["ext_offset",{"type":"ndarray","array":{"type":"bytes","data":""},"shape":[0],"dtype":"float64","order":"little"}],["success_rate",{"type":"ndarray","array":{"type":"bytes","data":""},"shape":[0],"dtype":"float64","order":"little"}]]}}},"view":{"type":"object","name":"CDSView","id":"p1158","attributes":{"filter":{"type":"object","name":"AllIndices","id":"p1159"}}},"glyph":{"type":"object","name":"Scatter","id":"p1154","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"repeat"},"y":{"type":"field","field":"ext_offset"},"size":{"type":"value","value":10},"line_color":{"type":"value","value":"#007f00"},"fill_color":{"type":"value","value":"#007f00"},"hatch_color":{"type":"value","value":"#007f00"},"marker":{"type":"value","value":"cross"}}},"selection_glyph":{"type":"object","name":"Scatter","id":"p1162","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"repeat"},"y":{"type":"field","field":"ext_offset"},"size":{"type":"value","value":10},"angle":{"type":"value","value":0.0},"line_color":{"type":"value","value":"#007f00"},"line_alpha":{"type":"value","value":1.0},"line_width":{"type":"value","value":1},"line_join":{"type":"value","value":"bevel"},"line_cap":{"type":"value","value":"butt"},"line_dash":{"type":"value","value":[]},"line_dash_offset":{"type":"value","value":0},"fill_color":{"type":"value","value":"#007f00"},"fill_alpha":{"type":"value","value":1.0},"hatch_color":{"type":"value","value":"#007f00"},"hatch_alpha":{"type":"value","value":1.0},"hatch_scale":{"type":"value","value":12.0},"hatch_pattern":{"type":"value","value":null},"hatch_weight":{"type":"value","value":1.0},"marker":{"type":"value","value":"cross"}}},"nonselection_glyph":{"type":"object","name":"Scatter","id":"p1155","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"repeat"},"y":{"type":"field","field":"ext_offset"},"size":{"type":"value","value":10},"line_color":{"type":"value","value":"#007f00"},"line_alpha":{"type":"value","value":0.1},"fill_color":{"type":"value","value":"#007f00"},"fill_alpha":{"type":"value","value":0.1},"hatch_color":{"type":"value","value":"#007f00"},"hatch_alpha":{"type":"value","value":0.1},"marker":{"type":"value","value":"cross"}}},"muted_glyph":{"type":"object","name":"Scatter","id":"p1156","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"repeat"},"y":{"type":"field","field":"ext_offset"},"size":{"type":"value","value":10},"line_color":{"type":"value","value":"#007f00"},"line_alpha":{"type":"value","value":0.2},"fill_color":{"type":"value","value":"#007f00"},"fill_alpha":{"type":"value","value":0.2},"hatch_color":{"type":"value","value":"#007f00"},"hatch_alpha":{"type":"value","value":0.2},"marker":{"type":"value","value":"cross"}}}}},{"type":"object","name":"GlyphRenderer","id":"p1172","attributes":{"name":"Reset","data_source":{"type":"object","name":"ColumnDataSource","id":"p1163","attributes":{"selected":{"type":"object","name":"Selection","id":"p1164","attributes":{"indices":[],"line_indices":[]}},"selection_policy":{"type":"object","name":"UnionRenderers","id":"p1165"},"data":{"type":"map","entries":[["repeat",{"type":"ndarray","array":{"type":"bytes","data":""},"shape":[0],"dtype":"float64","order":"little"}],["ext_offset",{"type":"ndarray","array":{"type":"bytes","data":""},"shape":[0],"dtype":"float64","order":"little"}],["reset_rate",{"type":"ndarray","array":{"type":"bytes","data":""},"shape":[0],"dtype":"float64","order":"little"}]]}}},"view":{"type":"object","name":"CDSView","id":"p1173","attributes":{"filter":{"type":"object","name":"AllIndices","id":"p1174"}}},"glyph":{"type":"object","name":"Scatter","id":"p1169","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"repeat"},"y":{"type":"field","field":"ext_offset"},"size":{"type":"value","value":10},"angle":{"type":"value","value":0.7853981633974483},"line_color":{"type":"value","value":"#ff0000"},"fill_color":{"type":"value","value":"#ff0000"},"hatch_color":{"type":"value","value":"#ff0000"},"marker":{"type":"value","value":"cross"}}},"selection_glyph":{"type":"object","name":"Scatter","id":"p1176","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"repeat"},"y":{"type":"field","field":"ext_offset"},"size":{"type":"value","value":10},"angle":{"type":"value","value":0.7853981633974483},"line_color":{"type":"value","value":"#ff0000"},"line_alpha":{"type":"value","value":1.0},"line_width":{"type":"value","value":1},"line_join":{"type":"value","value":"bevel"},"line_cap":{"type":"value","value":"butt"},"line_dash":{"type":"value","value":[]},"line_dash_offset":{"type":"value","value":0},"fill_color":{"type":"value","value":"#ff0000"},"fill_alpha":{"type":"value","value":1.0},"hatch_color":{"type":"value","value":"#ff0000"},"hatch_alpha":{"type":"value","value":1.0},"hatch_scale":{"type":"value","value":12.0},"hatch_pattern":{"type":"value","value":null},"hatch_weight":{"type":"value","value":1.0},"marker":{"type":"value","value":"cross"}}},"nonselection_glyph":{"type":"object","name":"Scatter","id":"p1170","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"repeat"},"y":{"type":"field","field":"ext_offset"},"size":{"type":"value","value":10},"angle":{"type":"value","value":0.7853981633974483},"line_color":{"type":"value","value":"#ff0000"},"line_alpha":{"type":"value","value":0.1},"fill_color":{"type":"value","value":"#ff0000"},"fill_alpha":{"type":"value","value":0.1},"hatch_color":{"type":"value","value":"#ff0000"},"hatch_alpha":{"type":"value","value":0.1},"marker":{"type":"value","value":"cross"}}},"muted_glyph":{"type":"object","name":"Scatter","id":"p1171","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"repeat"},"y":{"type":"field","field":"ext_offset"},"size":{"type":"value","value":10},"angle":{"type":"value","value":0.7853981633974483},"line_color":{"type":"value","value":"#ff0000"},"line_alpha":{"type":"value","value":0.2},"fill_color":{"type":"value","value":"#ff0000"},"fill_alpha":{"type":"value","value":0.2},"hatch_color":{"type":"value","value":"#ff0000"},"hatch_alpha":{"type":"value","value":0.2},"marker":{"type":"value","value":"cross"}}}}}],"toolbar":{"type":"object","name":"Toolbar","id":"p1113","attributes":{"tools":[{"type":"object","name":"WheelZoomTool","id":"p1097","attributes":{"tags":["hv_created"],"renderers":"auto","zoom_together":"none"}},{"type":"object","name":"HoverTool","id":"p1100","attributes":{"tags":["hv_created"],"renderers":[{"id":"p1157"}],"tooltips":[["repeat","@{repeat}"],["ext_offset","@{ext_offset}"],["success_rate","@{success_rate}"]]}},{"type":"object","name":"HoverTool","id":"p1103","attributes":{"tags":["hv_created"],"renderers":[{"id":"p1172"}],"tooltips":[["repeat","@{repeat}"],["ext_offset","@{ext_offset}"],["reset_rate","@{reset_rate}"]]}},{"type":"object","name":"SaveTool","id":"p1126"},{"type":"object","name":"PanTool","id":"p1127"},{"type":"object","name":"BoxZoomTool","id":"p1128","attributes":{"overlay":{"type":"object","name":"BoxAnnotation","id":"p1129","attributes":{"syncable":false,"level":"overlay","visible":false,"left":{"type":"number","value":"nan"},"right":{"type":"number","value":"nan"},"top":{"type":"number","value":"nan"},"bottom":{"type":"number","value":"nan"},"left_units":"canvas","right_units":"canvas","top_units":"canvas","bottom_units":"canvas","line_color":"black","line_alpha":1.0,"line_width":2,"line_dash":[4,4],"fill_color":"lightgrey","fill_alpha":0.5}}}},{"type":"object","name":"ResetTool","id":"p1134"}],"active_drag":{"id":"p1127"},"active_scroll":{"id":"p1097"}}},"left":[{"type":"object","name":"LinearAxis","id":"p1121","attributes":{"ticker":{"type":"object","name":"BasicTicker","id":"p1122","attributes":{"mantissas":[1,2,5]}},"formatter":{"type":"object","name":"BasicTickFormatter","id":"p1123"},"axis_label":"Ext_Offset","major_label_policy":{"type":"object","name":"AllLabels","id":"p1124"}}}],"below":[{"type":"object","name":"LinearAxis","id":"p1116","attributes":{"ticker":{"type":"object","name":"BasicTicker","id":"p1117","attributes":{"mantissas":[1,2,5]}},"formatter":{"type":"object","name":"BasicTickFormatter","id":"p1118"},"axis_label":"Repeat","major_label_policy":{"type":"object","name":"AllLabels","id":"p1119"}}}],"center":[{"type":"object","name":"Grid","id":"p1120","attributes":{"axis":{"id":"p1116"},"grid_line_color":null}},{"type":"object","name":"Grid","id":"p1125","attributes":{"dimension":1,"axis":{"id":"p1121"},"grid_line_color":null}},{"type":"object","name":"Legend","id":"p1160","attributes":{"click_policy":"mute","items":[{"type":"object","name":"LegendItem","id":"p1161","attributes":{"label":{"type":"value","value":"Success"},"renderers":[{"id":"p1157"}]}},{"type":"object","name":"LegendItem","id":"p1175","attributes":{"label":{"type":"value","value":"Reset"},"renderers":[{"id":"p1172"}]}}]}}],"min_border_top":10,"min_border_bottom":10,"min_border_left":10,"min_border_right":10,"output_backend":"webgl"}},{"type":"object","name":"Spacer","id":"p1178","attributes":{"name":"HSpacer01106","stylesheets":["\n:host(.pn-loading):before, .pn-loading:before {\n  background-color: #c3c3c3;\n  mask-size: auto calc(min(50%, 400px));\n  -webkit-mask-size: auto calc(min(50%, 400px));\n}",{"id":"p1090"},{"id":"p1088"},{"id":"p1089"}],"margin":0,"sizing_mode":"stretch_width","align":"start"}}]}}],"defs":[{"type":"model","name":"ReactiveHTML1"},{"type":"model","name":"FlexBox1","properties":[{"name":"align_content","kind":"Any","default":"flex-start"},{"name":"align_items","kind":"Any","default":"flex-start"},{"name":"flex_direction","kind":"Any","default":"row"},{"name":"flex_wrap","kind":"Any","default":"wrap"},{"name":"gap","kind":"Any","default":""},{"name":"justify_content","kind":"Any","default":"flex-start"}]},{"type":"model","name":"FloatPanel1","properties":[{"name":"config","kind":"Any","default":{"type":"map"}},{"name":"contained","kind":"Any","default":true},{"name":"position","kind":"Any","default":"right-top"},{"name":"offsetx","kind":"Any","default":null},{"name":"offsety","kind":"Any","default":null},{"name":"theme","kind":"Any","default":"primary"},{"name":"status","kind":"Any","default":"normalized"}]},{"type":"model","name":"GridStack1","properties":[{"name":"mode","kind":"Any","default":"warn"},{"name":"ncols","kind":"Any","default":null},{"name":"nrows","kind":"Any","default":null},{"name":"allow_resize","kind":"Any","default":true},{"name":"allow_drag","kind":"Any","default":true},{"name":"state","kind":"Any","default":[]}]},{"type":"model","name":"drag1","properties":[{"name":"slider_width","kind":"Any","default":5},{"name":"slider_color","kind":"Any","default":"black"},{"name":"value","kind":"Any","default":50}]},{"type":"model","name":"click1","properties":[{"name":"terminal_output","kind":"Any","default":""},{"name":"debug_name","kind":"Any","default":""},{"name":"clears","kind":"Any","default":0}]},{"type":"model","name":"FastWrapper1","properties":[{"name":"object","kind":"Any","default":null},{"name":"style","kind":"Any","default":null}]},{"type":"model","name":"NotificationAreaBase1","properties":[{"name":"js_events","kind":"Any","default":{"type":"map"}},{"name":"position","kind":"Any","default":"bottom-right"},{"name":"_clear","kind":"Any","default":0}]},{"type":"model","name":"NotificationArea1","properties":[{"name":"js_events","kind":"Any","default":{"type":"map"}},{"name":"notifications","kind":"Any","default":[]},{"name":"position","kind":"Any","default":"bottom-right"},{"name":"_clear","kind":"Any","default":0},{"name":"types","kind":"Any","default":[{"type":"map","entries":[["type","warning"],["background","#ffc107"],["icon",{"type":"map","entries":[["className","fas fa-exclamation-triangle"],["tagName","i"],["color","white"]]}]]},{"type":"map","entries":[["type","info"],["background","#007bff"],["icon",{"type":"map","entries":[["className","fas fa-info-circle"],["tagName","i"],["color","white"]]}]]}]}]},{"type":"model","name":"Notification","properties":[{"name":"background","kind":"Any","default":null},{"name":"duration","kind":"Any","default":3000},{"name":"icon","kind":"Any","default":null},{"name":"message","kind":"Any","default":""},{"name":"notification_type","kind":"Any","default":null},{"name":"_destroyed","kind":"Any","default":false}]},{"type":"model","name":"TemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"BootstrapTemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"TemplateEditor1","properties":[{"name":"layout","kind":"Any","default":[]}]},{"type":"model","name":"MaterialTemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"copy_to_clipboard1","properties":[{"name":"fill","kind":"Any","default":"none"},{"name":"value","kind":"Any","default":null}]}]}};
      var render_items = [{"docid":"eaa5a32d-da49-4971-a1b6-823720af60ec","roots":{"p1087":"e9de8e7c-e49e-4358-bbf3-35ef87b75aaa"},"root_ids":["p1087"]}];
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




**In [12]:**

.. code:: ipython3

    scope.dis()
    target.dis()

Unlike the other ChipWhisperers, the Nano doesn’t have sychronous
glitching. This means that ``ext_offset`` is a mixture of both the
offset within the clock cycle, which affects glitch success, and
ext_offset, which affects which instruction is being glitched. As such,
ext_offset settings you find in this lab won’t be directly applicable to
other labs. That being said, good ranges for repeat and the success rate
of glitches still gives valuable information that you can apply to other
labs.


**In [ ]:**

