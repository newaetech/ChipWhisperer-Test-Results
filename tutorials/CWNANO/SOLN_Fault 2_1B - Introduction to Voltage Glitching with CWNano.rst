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
    
    VERSION = 'HARDWARE'
    allowable_exceptions = None
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
    .
    .
    Compiling:
    Compiling:
    -en     simpleserial-glitch.c ...
    -en     .././simpleserial/simpleserial.c ...
    +--------------------------------------------------------
    + Built for platform CWNANO Built-in Target (STM32F030) with:
    + CRYPTO\_TARGET = NONE
    + CRYPTO\_OPTIONS = 
    +--------------------------------------------------------
    -e Done!
    -e Done!
    .
    LINKING:
    -en     simpleserial-glitch-CWNANO.elf ...
    -e Done!
    .
    .
    Creating load file for Flash: simpleserial-glitch-CWNANO.hex
    arm-none-eabi-objcopy -O ihex -R .eeprom -R .fuse -R .lock -R .signature simpleserial-glitch-CWNANO.elf simpleserial-glitch-CWNANO.hex
    Creating load file for Flash: simpleserial-glitch-CWNANO.bin
    arm-none-eabi-objcopy -O binary -R .eeprom -R .fuse -R .lock -R .signature simpleserial-glitch-CWNANO.elf simpleserial-glitch-CWNANO.bin
    .
    .
    .
    Creating load file for EEPROM: simpleserial-glitch-CWNANO.eep
    Creating Extended Listing: simpleserial-glitch-CWNANO.lss
    arm-none-eabi-objcopy -j .eeprom --set-section-flags=.eeprom="alloc,load" \
    --change-section-lma .eeprom=0 --no-change-warnings -O ihex simpleserial-glitch-CWNANO.elf simpleserial-glitch-CWNANO.eep \|\| exit 0
    Creating Symbol Table: simpleserial-glitch-CWNANO.sym
    arm-none-eabi-objdump -h -S -z simpleserial-glitch-CWNANO.elf > simpleserial-glitch-CWNANO.lss
    arm-none-eabi-nm -n simpleserial-glitch-CWNANO.elf > simpleserial-glitch-CWNANO.sym
    Size after:
       text	   data	    bss	    dec	    hex	filename
       5380	     12	   1364	   6756	   1a64	simpleserial-glitch-CWNANO.elf




**In [4]:**

.. code:: ipython3

    fw_path = "../../../firmware/mcu/simpleserial-glitch/simpleserial-glitch-{}.hex".format(PLATFORM)
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
        <div id='f68a656f-bca2-41ef-9f4f-1675e809bf9c'>
      <div id="e1217071-5184-48ce-8b37-0769922e0997" data-root-id="f68a656f-bca2-41ef-9f4f-1675e809bf9c" style="display: contents;"></div>
    </div>
    <script type="application/javascript">(function(root) {
      var docs_json = {"1c6d0d85-d3ed-42cb-8a90-10cfeb9c8186":{"version":"3.6.2","title":"Bokeh Application","roots":[{"type":"object","name":"panel.models.browser.BrowserInfo","id":"f68a656f-bca2-41ef-9f4f-1675e809bf9c"},{"type":"object","name":"panel.models.comm_manager.CommManager","id":"508e6508-33b8-49f9-bd25-4bc6d4ae7339","attributes":{"plot_id":"f68a656f-bca2-41ef-9f4f-1675e809bf9c","comm_id":"1d0d0b04355a44b3a62060cc36530e53","client_comm_id":"08340b3d5a454a50aa344892cc3662ff"}}],"defs":[{"type":"model","name":"ReactiveHTML1"},{"type":"model","name":"FlexBox1","properties":[{"name":"align_content","kind":"Any","default":"flex-start"},{"name":"align_items","kind":"Any","default":"flex-start"},{"name":"flex_direction","kind":"Any","default":"row"},{"name":"flex_wrap","kind":"Any","default":"wrap"},{"name":"gap","kind":"Any","default":""},{"name":"justify_content","kind":"Any","default":"flex-start"}]},{"type":"model","name":"FloatPanel1","properties":[{"name":"config","kind":"Any","default":{"type":"map"}},{"name":"contained","kind":"Any","default":true},{"name":"position","kind":"Any","default":"right-top"},{"name":"offsetx","kind":"Any","default":null},{"name":"offsety","kind":"Any","default":null},{"name":"theme","kind":"Any","default":"primary"},{"name":"status","kind":"Any","default":"normalized"}]},{"type":"model","name":"GridStack1","properties":[{"name":"mode","kind":"Any","default":"warn"},{"name":"ncols","kind":"Any","default":null},{"name":"nrows","kind":"Any","default":null},{"name":"allow_resize","kind":"Any","default":true},{"name":"allow_drag","kind":"Any","default":true},{"name":"state","kind":"Any","default":[]}]},{"type":"model","name":"drag1","properties":[{"name":"slider_width","kind":"Any","default":5},{"name":"slider_color","kind":"Any","default":"black"},{"name":"value","kind":"Any","default":50}]},{"type":"model","name":"click1","properties":[{"name":"terminal_output","kind":"Any","default":""},{"name":"debug_name","kind":"Any","default":""},{"name":"clears","kind":"Any","default":0}]},{"type":"model","name":"FastWrapper1","properties":[{"name":"object","kind":"Any","default":null},{"name":"style","kind":"Any","default":null}]},{"type":"model","name":"NotificationAreaBase1","properties":[{"name":"js_events","kind":"Any","default":{"type":"map"}},{"name":"position","kind":"Any","default":"bottom-right"},{"name":"_clear","kind":"Any","default":0}]},{"type":"model","name":"NotificationArea1","properties":[{"name":"js_events","kind":"Any","default":{"type":"map"}},{"name":"notifications","kind":"Any","default":[]},{"name":"position","kind":"Any","default":"bottom-right"},{"name":"_clear","kind":"Any","default":0},{"name":"types","kind":"Any","default":[{"type":"map","entries":[["type","warning"],["background","#ffc107"],["icon",{"type":"map","entries":[["className","fas fa-exclamation-triangle"],["tagName","i"],["color","white"]]}]]},{"type":"map","entries":[["type","info"],["background","#007bff"],["icon",{"type":"map","entries":[["className","fas fa-info-circle"],["tagName","i"],["color","white"]]}]]}]}]},{"type":"model","name":"Notification","properties":[{"name":"background","kind":"Any","default":null},{"name":"duration","kind":"Any","default":3000},{"name":"icon","kind":"Any","default":null},{"name":"message","kind":"Any","default":""},{"name":"notification_type","kind":"Any","default":null},{"name":"_destroyed","kind":"Any","default":false}]},{"type":"model","name":"TemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"BootstrapTemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"TemplateEditor1","properties":[{"name":"layout","kind":"Any","default":[]}]},{"type":"model","name":"MaterialTemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"ReactiveESM1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"JSComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"ReactComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"AnyWidgetComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"request_value1","properties":[{"name":"fill","kind":"Any","default":"none"},{"name":"_synced","kind":"Any","default":null},{"name":"_request_sync","kind":"Any","default":0}]}]}};
      var render_items = [{"docid":"1c6d0d85-d3ed-42cb-8a90-10cfeb9c8186","roots":{"f68a656f-bca2-41ef-9f4f-1675e809bf9c":"e1217071-5184-48ce-8b37-0769922e0997"},"root_ids":["f68a656f-bca2-41ef-9f4f-1675e809bf9c"]}];
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
        <div id='f5641ae1-61f0-49f8-b1fd-4adc1206f41d'>
      <div id="c565afdf-3dc5-4080-bb44-904065c9240e" data-root-id="f5641ae1-61f0-49f8-b1fd-4adc1206f41d" style="display: contents;"></div>
    </div>
    <script type="application/javascript">(function(root) {
      var docs_json = {"84237989-28d8-4fec-b2b6-9c7ce56280dc":{"version":"3.6.2","title":"Bokeh Application","roots":[{"type":"object","name":"Row","id":"f5641ae1-61f0-49f8-b1fd-4adc1206f41d","attributes":{"name":"Row00289","stylesheets":["\n:host(.pn-loading):before, .pn-loading:before {\n  background-color: #c3c3c3;\n  mask-size: auto calc(min(50%, 400px));\n  -webkit-mask-size: auto calc(min(50%, 400px));\n}",{"type":"object","name":"ImportedStyleSheet","id":"10ae6d79-9a8c-4897-9f6a-6ac9e23e4e2d","attributes":{"url":"https://cdn.holoviz.org/panel/1.5.4/dist/css/loading.css"}},{"type":"object","name":"ImportedStyleSheet","id":"1cad1528-3609-46e7-834a-280f103a1ef9","attributes":{"url":"https://cdn.holoviz.org/panel/1.5.4/dist/css/listpanel.css"}},{"type":"object","name":"ImportedStyleSheet","id":"c89279b1-dfe2-49cc-b2e8-3c929208fef0","attributes":{"url":"https://cdn.holoviz.org/panel/1.5.4/dist/bundled/theme/default.css"}},{"type":"object","name":"ImportedStyleSheet","id":"124dac2d-193a-4b12-9cbd-01c8f08fb124","attributes":{"url":"https://cdn.holoviz.org/panel/1.5.4/dist/bundled/theme/native.css"}}],"min_width":800,"margin":0,"sizing_mode":"stretch_width","align":"start","children":[{"type":"object","name":"Spacer","id":"cb27dcef-0369-4344-90d0-630f1cddb5ea","attributes":{"name":"HSpacer00293","stylesheets":["\n:host(.pn-loading):before, .pn-loading:before {\n  background-color: #c3c3c3;\n  mask-size: auto calc(min(50%, 400px));\n  -webkit-mask-size: auto calc(min(50%, 400px));\n}",{"id":"10ae6d79-9a8c-4897-9f6a-6ac9e23e4e2d"},{"id":"c89279b1-dfe2-49cc-b2e8-3c929208fef0"},{"id":"124dac2d-193a-4b12-9cbd-01c8f08fb124"}],"margin":0,"sizing_mode":"stretch_width","align":"start"}},{"type":"object","name":"Figure","id":"b847b330-cacd-4b49-bd1f-e175fc2e168e","attributes":{"js_event_callbacks":{"type":"map","entries":[["reset",[{"type":"object","name":"CustomJS","id":"6e9d1855-eabd-477d-acb2-06c27ff3a6a9","attributes":{"code":"export default (_, cb_obj) => { cb_obj.origin.hold_render = false }"}}]]]},"subscribed_events":{"type":"set","entries":["reset","rangesupdate"]},"width":800,"margin":[5,10],"sizing_mode":"fixed","align":"start","x_range":{"type":"object","name":"Range1d","id":"3cb360c5-dc36-49b3-8f9f-074ff4ce2a11","attributes":{"name":"repeat","tags":[[["repeat",null]],[]]}},"y_range":{"type":"object","name":"Range1d","id":"ae081d1c-cedf-433f-a252-0566a1dfb03f","attributes":{"name":"ext_offset","tags":[[["ext_offset",null]],{"type":"map","entries":[["invert_yaxis",false],["autorange",false]]}]}},"x_scale":{"type":"object","name":"LinearScale","id":"f301ff7a-74a2-4fe5-8df0-01f837f9a54a"},"y_scale":{"type":"object","name":"LinearScale","id":"76debf9d-90a3-4d02-8d6c-effdf4fb79ae"},"title":{"type":"object","name":"Title","id":"205e3026-3374-455a-927a-4c98760401bb","attributes":{"text_color":"black","text_font_size":"12pt"}},"renderers":[{"type":"object","name":"GlyphRenderer","id":"f72c822c-88dc-4a39-8912-b04e9ef9f04a","attributes":{"data_source":{"type":"object","name":"ColumnDataSource","id":"02dde217-6c45-420f-8b8b-add37dffd534","attributes":{"selected":{"type":"object","name":"Selection","id":"d4809f9a-8c16-4642-9bfb-044909140db9","attributes":{"indices":[],"line_indices":[]}},"selection_policy":{"type":"object","name":"UnionRenderers","id":"165fcf4d-e062-44e1-b7b3-f699b80658fb"},"data":{"type":"map","entries":[["repeat",{"type":"ndarray","array":{"type":"bytes","data":""},"shape":[0],"dtype":"float64","order":"little"}],["ext_offset",{"type":"ndarray","array":{"type":"bytes","data":""},"shape":[0],"dtype":"float64","order":"little"}]]}}},"view":{"type":"object","name":"CDSView","id":"0302db3c-117d-4a2c-8497-eaa893242189","attributes":{"filter":{"type":"object","name":"AllIndices","id":"45e54e2e-fe37-432a-981f-404a69dacffc"}}},"glyph":{"type":"object","name":"Scatter","id":"39f1aba1-427a-4fa3-8ada-992b1d3b0eb5","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"repeat"},"y":{"type":"field","field":"ext_offset"},"size":{"type":"value","value":10},"line_color":{"type":"value","value":"#007f00"},"fill_color":{"type":"value","value":"#007f00"},"hatch_color":{"type":"value","value":"#007f00"},"marker":{"type":"value","value":"cross"}}},"selection_glyph":{"type":"object","name":"Scatter","id":"7646a30f-6ab9-4c6f-849e-bf98c04fc9d1","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"repeat"},"y":{"type":"field","field":"ext_offset"},"size":{"type":"value","value":10},"angle":{"type":"value","value":0.0},"line_color":{"type":"value","value":"#007f00"},"line_alpha":{"type":"value","value":1.0},"line_width":{"type":"value","value":1},"line_join":{"type":"value","value":"bevel"},"line_cap":{"type":"value","value":"butt"},"line_dash":{"type":"value","value":[]},"line_dash_offset":{"type":"value","value":0},"fill_color":{"type":"value","value":"#007f00"},"fill_alpha":{"type":"value","value":1.0},"hatch_color":{"type":"value","value":"#007f00"},"hatch_alpha":{"type":"value","value":1.0},"hatch_scale":{"type":"value","value":12.0},"hatch_pattern":{"type":"value","value":null},"hatch_weight":{"type":"value","value":1.0},"marker":{"type":"value","value":"cross"}}},"nonselection_glyph":{"type":"object","name":"Scatter","id":"445756b6-a934-4d2e-bf00-f38611864d9e","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"repeat"},"y":{"type":"field","field":"ext_offset"},"size":{"type":"value","value":10},"line_color":{"type":"value","value":"#007f00"},"line_alpha":{"type":"value","value":0.1},"fill_color":{"type":"value","value":"#007f00"},"fill_alpha":{"type":"value","value":0.1},"hatch_color":{"type":"value","value":"#007f00"},"hatch_alpha":{"type":"value","value":0.1},"marker":{"type":"value","value":"cross"}}},"muted_glyph":{"type":"object","name":"Scatter","id":"5ddec650-f646-4714-9362-ff5c28334242","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"repeat"},"y":{"type":"field","field":"ext_offset"},"size":{"type":"value","value":10},"line_color":{"type":"value","value":"#007f00"},"line_alpha":{"type":"value","value":0.2},"fill_color":{"type":"value","value":"#007f00"},"fill_alpha":{"type":"value","value":0.2},"hatch_color":{"type":"value","value":"#007f00"},"hatch_alpha":{"type":"value","value":0.2},"marker":{"type":"value","value":"cross"}}}}},{"type":"object","name":"GlyphRenderer","id":"33bc7c2d-a949-480e-a750-f99b09397db5","attributes":{"data_source":{"type":"object","name":"ColumnDataSource","id":"8fbce05e-ebd4-453e-a4a8-8ba1579e1401","attributes":{"selected":{"type":"object","name":"Selection","id":"484a5038-e5f4-43f5-91c7-643f74c9ccb3","attributes":{"indices":[],"line_indices":[]}},"selection_policy":{"type":"object","name":"UnionRenderers","id":"b0e5f100-3a48-46d3-a434-75aa87e752ff"},"data":{"type":"map","entries":[["repeat",{"type":"ndarray","array":{"type":"bytes","data":""},"shape":[0],"dtype":"float64","order":"little"}],["ext_offset",{"type":"ndarray","array":{"type":"bytes","data":""},"shape":[0],"dtype":"float64","order":"little"}]]}}},"view":{"type":"object","name":"CDSView","id":"fbfe5259-c24c-41da-b6d6-ee6dbaa8e148","attributes":{"filter":{"type":"object","name":"AllIndices","id":"241b6ebc-3755-49a1-b0d6-6e0a9028b9e1"}}},"glyph":{"type":"object","name":"Scatter","id":"447e747b-93fd-498c-b880-00a818b84417","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"repeat"},"y":{"type":"field","field":"ext_offset"},"size":{"type":"value","value":10},"angle":{"type":"value","value":0.7853981633974483},"line_color":{"type":"value","value":"#ff0000"},"fill_color":{"type":"value","value":"#ff0000"},"hatch_color":{"type":"value","value":"#ff0000"},"marker":{"type":"value","value":"cross"}}},"selection_glyph":{"type":"object","name":"Scatter","id":"45ca9408-87bb-45c5-afef-66ec1926bc85","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"repeat"},"y":{"type":"field","field":"ext_offset"},"size":{"type":"value","value":10},"angle":{"type":"value","value":0.7853981633974483},"line_color":{"type":"value","value":"#ff0000"},"line_alpha":{"type":"value","value":1.0},"line_width":{"type":"value","value":1},"line_join":{"type":"value","value":"bevel"},"line_cap":{"type":"value","value":"butt"},"line_dash":{"type":"value","value":[]},"line_dash_offset":{"type":"value","value":0},"fill_color":{"type":"value","value":"#ff0000"},"fill_alpha":{"type":"value","value":1.0},"hatch_color":{"type":"value","value":"#ff0000"},"hatch_alpha":{"type":"value","value":1.0},"hatch_scale":{"type":"value","value":12.0},"hatch_pattern":{"type":"value","value":null},"hatch_weight":{"type":"value","value":1.0},"marker":{"type":"value","value":"cross"}}},"nonselection_glyph":{"type":"object","name":"Scatter","id":"354d6a04-6755-4440-8513-14714419213e","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"repeat"},"y":{"type":"field","field":"ext_offset"},"size":{"type":"value","value":10},"angle":{"type":"value","value":0.7853981633974483},"line_color":{"type":"value","value":"#ff0000"},"line_alpha":{"type":"value","value":0.1},"fill_color":{"type":"value","value":"#ff0000"},"fill_alpha":{"type":"value","value":0.1},"hatch_color":{"type":"value","value":"#ff0000"},"hatch_alpha":{"type":"value","value":0.1},"marker":{"type":"value","value":"cross"}}},"muted_glyph":{"type":"object","name":"Scatter","id":"cf4157c0-d533-4c2b-b011-ae2928e8a920","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"repeat"},"y":{"type":"field","field":"ext_offset"},"size":{"type":"value","value":10},"angle":{"type":"value","value":0.7853981633974483},"line_color":{"type":"value","value":"#ff0000"},"line_alpha":{"type":"value","value":0.2},"fill_color":{"type":"value","value":"#ff0000"},"fill_alpha":{"type":"value","value":0.2},"hatch_color":{"type":"value","value":"#ff0000"},"hatch_alpha":{"type":"value","value":0.2},"marker":{"type":"value","value":"cross"}}}}}],"toolbar":{"type":"object","name":"Toolbar","id":"76d528c2-c519-4cef-b4a8-4a5924f68c31","attributes":{"tools":[{"type":"object","name":"WheelZoomTool","id":"28de8a29-9b4c-49b9-95a6-800caa092bbc","attributes":{"tags":["hv_created"],"renderers":"auto","zoom_together":"none"}},{"type":"object","name":"HoverTool","id":"aabf6949-af53-4053-851a-291300ba200f","attributes":{"tags":["hv_created"],"renderers":[{"id":"f72c822c-88dc-4a39-8912-b04e9ef9f04a"},{"id":"33bc7c2d-a949-480e-a750-f99b09397db5"}],"tooltips":[["repeat","@{repeat}"],["ext_offset","@{ext_offset}"]]}},{"type":"object","name":"SaveTool","id":"c962d0f8-9e17-4ef6-82e8-e081324e18bf"},{"type":"object","name":"PanTool","id":"e5183861-5f85-4e1a-90c7-ab6a9138f473"},{"type":"object","name":"BoxZoomTool","id":"fbfa0e70-0102-4100-b7f8-f050dcc53bd5","attributes":{"overlay":{"type":"object","name":"BoxAnnotation","id":"e6e882cc-320e-4b70-9c36-43a358402b0e","attributes":{"syncable":false,"line_color":"black","line_alpha":1.0,"line_width":2,"line_dash":[4,4],"fill_color":"lightgrey","fill_alpha":0.5,"level":"overlay","visible":false,"left":{"type":"number","value":"nan"},"right":{"type":"number","value":"nan"},"top":{"type":"number","value":"nan"},"bottom":{"type":"number","value":"nan"},"left_units":"canvas","right_units":"canvas","top_units":"canvas","bottom_units":"canvas","handles":{"type":"object","name":"BoxInteractionHandles","id":"1b0d26e0-893e-4191-ac79-e57bd193c9f4","attributes":{"all":{"type":"object","name":"AreaVisuals","id":"f2529604-f13e-4e0c-a362-5dfd282b72f5","attributes":{"fill_color":"white","hover_fill_color":"lightgray"}}}}}}}},{"type":"object","name":"ResetTool","id":"265cdad7-9541-44f4-9455-3b6915c16a4f"}],"active_drag":{"id":"e5183861-5f85-4e1a-90c7-ab6a9138f473"},"active_scroll":{"id":"28de8a29-9b4c-49b9-95a6-800caa092bbc"}}},"left":[{"type":"object","name":"LinearAxis","id":"4fb0212c-f1f1-48a0-a982-89f2e4edc8ac","attributes":{"ticker":{"type":"object","name":"BasicTicker","id":"4bafad35-ff24-4159-bbbe-b6dafe7534a3","attributes":{"mantissas":[1,2,5]}},"formatter":{"type":"object","name":"BasicTickFormatter","id":"0a68487a-399d-45c0-a68b-506b31f73cee"},"axis_label":"ext_offset","major_label_policy":{"type":"object","name":"AllLabels","id":"0ad824e3-24a1-4290-a40b-0e08fc0fbdf5"}}}],"below":[{"type":"object","name":"LinearAxis","id":"68d5ea57-2cb3-4ca0-a5d2-e51c8bbb5245","attributes":{"ticker":{"type":"object","name":"BasicTicker","id":"0d473c63-1a6a-4178-825d-5fd7339bad9c","attributes":{"mantissas":[1,2,5]}},"formatter":{"type":"object","name":"BasicTickFormatter","id":"750c6989-6496-4742-a6c3-ed89d59673b0"},"axis_label":"repeat","major_label_policy":{"type":"object","name":"AllLabels","id":"706c759c-ba3d-48f7-ac92-d53f6213c867"}}}],"center":[{"type":"object","name":"Grid","id":"2b662221-6369-4755-8039-96ccf1cec08c","attributes":{"axis":{"id":"68d5ea57-2cb3-4ca0-a5d2-e51c8bbb5245"},"grid_line_color":null}},{"type":"object","name":"Grid","id":"1b36323c-114e-4c01-964f-9af5bbc538c1","attributes":{"dimension":1,"axis":{"id":"4fb0212c-f1f1-48a0-a982-89f2e4edc8ac"},"grid_line_color":null}}],"min_border_top":10,"min_border_bottom":10,"min_border_left":10,"min_border_right":10,"output_backend":"webgl"}},{"type":"object","name":"Spacer","id":"74cb2ef2-9580-43ab-86d9-c6fa6f91a5b0","attributes":{"name":"HSpacer00294","stylesheets":["\n:host(.pn-loading):before, .pn-loading:before {\n  background-color: #c3c3c3;\n  mask-size: auto calc(min(50%, 400px));\n  -webkit-mask-size: auto calc(min(50%, 400px));\n}",{"id":"10ae6d79-9a8c-4897-9f6a-6ac9e23e4e2d"},{"id":"c89279b1-dfe2-49cc-b2e8-3c929208fef0"},{"id":"124dac2d-193a-4b12-9cbd-01c8f08fb124"}],"margin":0,"sizing_mode":"stretch_width","align":"start"}}]}},{"type":"object","name":"panel.models.comm_manager.CommManager","id":"fbcd14cf-3f87-4286-a006-8dd453c614e2","attributes":{"plot_id":"f5641ae1-61f0-49f8-b1fd-4adc1206f41d","comm_id":"5b42d0a89e814432be8afb6189b3b596","client_comm_id":"8ef4a30253a940c7a54c648a5e7e3370"}}],"defs":[{"type":"model","name":"ReactiveHTML1"},{"type":"model","name":"FlexBox1","properties":[{"name":"align_content","kind":"Any","default":"flex-start"},{"name":"align_items","kind":"Any","default":"flex-start"},{"name":"flex_direction","kind":"Any","default":"row"},{"name":"flex_wrap","kind":"Any","default":"wrap"},{"name":"gap","kind":"Any","default":""},{"name":"justify_content","kind":"Any","default":"flex-start"}]},{"type":"model","name":"FloatPanel1","properties":[{"name":"config","kind":"Any","default":{"type":"map"}},{"name":"contained","kind":"Any","default":true},{"name":"position","kind":"Any","default":"right-top"},{"name":"offsetx","kind":"Any","default":null},{"name":"offsety","kind":"Any","default":null},{"name":"theme","kind":"Any","default":"primary"},{"name":"status","kind":"Any","default":"normalized"}]},{"type":"model","name":"GridStack1","properties":[{"name":"mode","kind":"Any","default":"warn"},{"name":"ncols","kind":"Any","default":null},{"name":"nrows","kind":"Any","default":null},{"name":"allow_resize","kind":"Any","default":true},{"name":"allow_drag","kind":"Any","default":true},{"name":"state","kind":"Any","default":[]}]},{"type":"model","name":"drag1","properties":[{"name":"slider_width","kind":"Any","default":5},{"name":"slider_color","kind":"Any","default":"black"},{"name":"value","kind":"Any","default":50}]},{"type":"model","name":"click1","properties":[{"name":"terminal_output","kind":"Any","default":""},{"name":"debug_name","kind":"Any","default":""},{"name":"clears","kind":"Any","default":0}]},{"type":"model","name":"FastWrapper1","properties":[{"name":"object","kind":"Any","default":null},{"name":"style","kind":"Any","default":null}]},{"type":"model","name":"NotificationAreaBase1","properties":[{"name":"js_events","kind":"Any","default":{"type":"map"}},{"name":"position","kind":"Any","default":"bottom-right"},{"name":"_clear","kind":"Any","default":0}]},{"type":"model","name":"NotificationArea1","properties":[{"name":"js_events","kind":"Any","default":{"type":"map"}},{"name":"notifications","kind":"Any","default":[]},{"name":"position","kind":"Any","default":"bottom-right"},{"name":"_clear","kind":"Any","default":0},{"name":"types","kind":"Any","default":[{"type":"map","entries":[["type","warning"],["background","#ffc107"],["icon",{"type":"map","entries":[["className","fas fa-exclamation-triangle"],["tagName","i"],["color","white"]]}]]},{"type":"map","entries":[["type","info"],["background","#007bff"],["icon",{"type":"map","entries":[["className","fas fa-info-circle"],["tagName","i"],["color","white"]]}]]}]}]},{"type":"model","name":"Notification","properties":[{"name":"background","kind":"Any","default":null},{"name":"duration","kind":"Any","default":3000},{"name":"icon","kind":"Any","default":null},{"name":"message","kind":"Any","default":""},{"name":"notification_type","kind":"Any","default":null},{"name":"_destroyed","kind":"Any","default":false}]},{"type":"model","name":"TemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"BootstrapTemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"TemplateEditor1","properties":[{"name":"layout","kind":"Any","default":[]}]},{"type":"model","name":"MaterialTemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"ReactiveESM1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"JSComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"ReactComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"AnyWidgetComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"request_value1","properties":[{"name":"fill","kind":"Any","default":"none"},{"name":"_synced","kind":"Any","default":null},{"name":"_request_sync","kind":"Any","default":0}]}]}};
      var render_items = [{"docid":"84237989-28d8-4fec-b2b6-9c7ce56280dc","roots":{"f5641ae1-61f0-49f8-b1fd-4adc1206f41d":"c565afdf-3dc5-4080-bb44-904065c9240e"},"root_ids":["f5641ae1-61f0-49f8-b1fd-4adc1206f41d"]}];
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
        <div id='28f23adf-9c67-403f-93c6-5a44053db5d3'>
      <div id="f7cf2cfd-8487-4ed4-943c-662c6aa0bd26" data-root-id="28f23adf-9c67-403f-93c6-5a44053db5d3" style="display: contents;"></div>
    </div>
    <script type="application/javascript">(function(root) {
      var docs_json = {"5705fb71-56c8-4962-ae0f-9328ca770c04":{"version":"3.6.2","title":"Bokeh Application","roots":[{"type":"object","name":"panel.models.browser.BrowserInfo","id":"28f23adf-9c67-403f-93c6-5a44053db5d3"},{"type":"object","name":"panel.models.comm_manager.CommManager","id":"c42d27fc-3dd4-49ef-ac84-2ba4976b37e5","attributes":{"plot_id":"28f23adf-9c67-403f-93c6-5a44053db5d3","comm_id":"2dba18a2bb444473ae072d4b523087e3","client_comm_id":"6bc417eb709d4770b671261921811233"}}],"defs":[{"type":"model","name":"ReactiveHTML1"},{"type":"model","name":"FlexBox1","properties":[{"name":"align_content","kind":"Any","default":"flex-start"},{"name":"align_items","kind":"Any","default":"flex-start"},{"name":"flex_direction","kind":"Any","default":"row"},{"name":"flex_wrap","kind":"Any","default":"wrap"},{"name":"gap","kind":"Any","default":""},{"name":"justify_content","kind":"Any","default":"flex-start"}]},{"type":"model","name":"FloatPanel1","properties":[{"name":"config","kind":"Any","default":{"type":"map"}},{"name":"contained","kind":"Any","default":true},{"name":"position","kind":"Any","default":"right-top"},{"name":"offsetx","kind":"Any","default":null},{"name":"offsety","kind":"Any","default":null},{"name":"theme","kind":"Any","default":"primary"},{"name":"status","kind":"Any","default":"normalized"}]},{"type":"model","name":"GridStack1","properties":[{"name":"mode","kind":"Any","default":"warn"},{"name":"ncols","kind":"Any","default":null},{"name":"nrows","kind":"Any","default":null},{"name":"allow_resize","kind":"Any","default":true},{"name":"allow_drag","kind":"Any","default":true},{"name":"state","kind":"Any","default":[]}]},{"type":"model","name":"drag1","properties":[{"name":"slider_width","kind":"Any","default":5},{"name":"slider_color","kind":"Any","default":"black"},{"name":"value","kind":"Any","default":50}]},{"type":"model","name":"click1","properties":[{"name":"terminal_output","kind":"Any","default":""},{"name":"debug_name","kind":"Any","default":""},{"name":"clears","kind":"Any","default":0}]},{"type":"model","name":"FastWrapper1","properties":[{"name":"object","kind":"Any","default":null},{"name":"style","kind":"Any","default":null}]},{"type":"model","name":"NotificationAreaBase1","properties":[{"name":"js_events","kind":"Any","default":{"type":"map"}},{"name":"position","kind":"Any","default":"bottom-right"},{"name":"_clear","kind":"Any","default":0}]},{"type":"model","name":"NotificationArea1","properties":[{"name":"js_events","kind":"Any","default":{"type":"map"}},{"name":"notifications","kind":"Any","default":[]},{"name":"position","kind":"Any","default":"bottom-right"},{"name":"_clear","kind":"Any","default":0},{"name":"types","kind":"Any","default":[{"type":"map","entries":[["type","warning"],["background","#ffc107"],["icon",{"type":"map","entries":[["className","fas fa-exclamation-triangle"],["tagName","i"],["color","white"]]}]]},{"type":"map","entries":[["type","info"],["background","#007bff"],["icon",{"type":"map","entries":[["className","fas fa-info-circle"],["tagName","i"],["color","white"]]}]]}]}]},{"type":"model","name":"Notification","properties":[{"name":"background","kind":"Any","default":null},{"name":"duration","kind":"Any","default":3000},{"name":"icon","kind":"Any","default":null},{"name":"message","kind":"Any","default":""},{"name":"notification_type","kind":"Any","default":null},{"name":"_destroyed","kind":"Any","default":false}]},{"type":"model","name":"TemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"BootstrapTemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"TemplateEditor1","properties":[{"name":"layout","kind":"Any","default":[]}]},{"type":"model","name":"MaterialTemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"ReactiveESM1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"JSComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"ReactComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"AnyWidgetComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"request_value1","properties":[{"name":"fill","kind":"Any","default":"none"},{"name":"_synced","kind":"Any","default":null},{"name":"_request_sync","kind":"Any","default":0}]}]}};
      var render_items = [{"docid":"5705fb71-56c8-4962-ae0f-9328ca770c04","roots":{"28f23adf-9c67-403f-93c6-5a44053db5d3":"f7cf2cfd-8487-4ed4-943c-662c6aa0bd26"},"root_ids":["28f23adf-9c67-403f-93c6-5a44053db5d3"]}];
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
        <div id='7e5b8aaa-281a-489e-8073-88858a299a51'>
      <div id="b15a22e6-f577-477d-aca9-7a45e31ab0fc" data-root-id="7e5b8aaa-281a-489e-8073-88858a299a51" style="display: contents;"></div>
    </div>
    <script type="application/javascript">(function(root) {
      var docs_json = {"c10c2311-2af9-40b5-abfa-449d06ede219":{"version":"3.6.2","title":"Bokeh Application","roots":[{"type":"object","name":"Row","id":"7e5b8aaa-281a-489e-8073-88858a299a51","attributes":{"name":"Row00450","tags":["embedded"],"stylesheets":["\n:host(.pn-loading):before, .pn-loading:before {\n  background-color: #c3c3c3;\n  mask-size: auto calc(min(50%, 400px));\n  -webkit-mask-size: auto calc(min(50%, 400px));\n}",{"type":"object","name":"ImportedStyleSheet","id":"01034b92-7a1f-40d8-96e3-98666811ad31","attributes":{"url":"https://cdn.holoviz.org/panel/1.5.4/dist/css/loading.css"}},{"type":"object","name":"ImportedStyleSheet","id":"dfc496cb-3ec1-4410-958e-74f444e13f76","attributes":{"url":"https://cdn.holoviz.org/panel/1.5.4/dist/css/listpanel.css"}},{"type":"object","name":"ImportedStyleSheet","id":"6d7c9615-a9c1-4020-8422-87d37a1bcbe6","attributes":{"url":"https://cdn.holoviz.org/panel/1.5.4/dist/bundled/theme/default.css"}},{"type":"object","name":"ImportedStyleSheet","id":"860c7e7b-a1a3-4e95-95e4-c38808f509aa","attributes":{"url":"https://cdn.holoviz.org/panel/1.5.4/dist/bundled/theme/native.css"}}],"min_width":800,"margin":0,"sizing_mode":"stretch_width","align":"start","children":[{"type":"object","name":"Spacer","id":"7aa8a006-0f28-43fa-945c-35220e744ef5","attributes":{"name":"HSpacer00454","stylesheets":["\n:host(.pn-loading):before, .pn-loading:before {\n  background-color: #c3c3c3;\n  mask-size: auto calc(min(50%, 400px));\n  -webkit-mask-size: auto calc(min(50%, 400px));\n}",{"id":"01034b92-7a1f-40d8-96e3-98666811ad31"},{"id":"6d7c9615-a9c1-4020-8422-87d37a1bcbe6"},{"id":"860c7e7b-a1a3-4e95-95e4-c38808f509aa"}],"margin":0,"sizing_mode":"stretch_width","align":"start"}},{"type":"object","name":"Figure","id":"ad854e92-e797-4570-8adb-5f3bcbfb6c69","attributes":{"width":800,"margin":[5,10],"sizing_mode":"fixed","align":"start","x_range":{"type":"object","name":"Range1d","id":"4870170c-5e6f-4701-9b2b-a5b8cb521743","attributes":{"name":"Repeat","tags":[[["Repeat",null]],[]]}},"y_range":{"type":"object","name":"Range1d","id":"b85456a5-f335-4308-aa0b-9e26ccc35f53","attributes":{"name":"Ext_Offset","tags":[[["Ext_Offset",null]],{"type":"map","entries":[["invert_yaxis",false],["autorange",false]]}]}},"x_scale":{"type":"object","name":"LinearScale","id":"a89aa303-243b-41e5-b6b3-49b6c2e090ae"},"y_scale":{"type":"object","name":"LinearScale","id":"5e344287-6944-437f-900a-68855e3d04a0"},"title":{"type":"object","name":"Title","id":"cb9127e6-c15a-4bc4-a216-960037e02bce","attributes":{"text_color":"black","text_font_size":"12pt"}},"renderers":[{"type":"object","name":"GlyphRenderer","id":"85319c12-3078-4eca-84ed-488a13cd33f8","attributes":{"data_source":{"type":"object","name":"ColumnDataSource","id":"51460e95-d03e-424f-8e3a-855d8ddfedf1","attributes":{"selected":{"type":"object","name":"Selection","id":"080f053b-8981-4147-bf48-6b9ba572ad38","attributes":{"indices":[],"line_indices":[]}},"selection_policy":{"type":"object","name":"UnionRenderers","id":"db9ad203-7090-4ff2-81f6-f3cf60e3fbbb"},"data":{"type":"map","entries":[["Repeat",{"type":"ndarray","array":{"type":"bytes","data":""},"shape":[0],"dtype":"float64","order":"little"}],["Ext_Offset",{"type":"ndarray","array":{"type":"bytes","data":""},"shape":[0],"dtype":"float64","order":"little"}]]}}},"view":{"type":"object","name":"CDSView","id":"ad9804fc-d3fd-4162-bf8d-08afaccaa646","attributes":{"filter":{"type":"object","name":"AllIndices","id":"70c67876-099d-4a0d-bbf3-a9ea14037832"}}},"glyph":{"type":"object","name":"Scatter","id":"4cba1116-c580-4be5-92d6-d4ed8be47819","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"Repeat"},"y":{"type":"field","field":"Ext_Offset"},"size":{"type":"value","value":2.449489742783178},"line_color":{"type":"value","value":"#30a2da"},"fill_color":{"type":"value","value":"#30a2da"},"hatch_color":{"type":"value","value":"#30a2da"}}},"selection_glyph":{"type":"object","name":"Scatter","id":"8d49e2c6-e81a-49b1-93fc-ac85a4919f52","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"Repeat"},"y":{"type":"field","field":"Ext_Offset"},"size":{"type":"value","value":2.449489742783178},"angle":{"type":"value","value":0.0},"line_color":{"type":"value","value":"#30a2da"},"line_alpha":{"type":"value","value":1.0},"line_width":{"type":"value","value":1},"line_join":{"type":"value","value":"bevel"},"line_cap":{"type":"value","value":"butt"},"line_dash":{"type":"value","value":[]},"line_dash_offset":{"type":"value","value":0},"fill_color":{"type":"value","value":"#30a2da"},"fill_alpha":{"type":"value","value":1.0},"hatch_color":{"type":"value","value":"#30a2da"},"hatch_alpha":{"type":"value","value":1.0},"hatch_scale":{"type":"value","value":12.0},"hatch_pattern":{"type":"value","value":null},"hatch_weight":{"type":"value","value":1.0},"marker":{"type":"value","value":"circle"}}},"nonselection_glyph":{"type":"object","name":"Scatter","id":"bde348ad-f7b6-45ab-9c62-a2bf422c72f3","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"Repeat"},"y":{"type":"field","field":"Ext_Offset"},"size":{"type":"value","value":2.449489742783178},"line_color":{"type":"value","value":"#30a2da"},"line_alpha":{"type":"value","value":0.1},"fill_color":{"type":"value","value":"#30a2da"},"fill_alpha":{"type":"value","value":0.1},"hatch_color":{"type":"value","value":"#30a2da"},"hatch_alpha":{"type":"value","value":0.1}}},"muted_glyph":{"type":"object","name":"Scatter","id":"2176cc49-83ce-467a-a0a1-3a7506f2e4f3","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"Repeat"},"y":{"type":"field","field":"Ext_Offset"},"size":{"type":"value","value":2.449489742783178},"line_color":{"type":"value","value":"#30a2da"},"line_alpha":{"type":"value","value":0.2},"fill_color":{"type":"value","value":"#30a2da"},"fill_alpha":{"type":"value","value":0.2},"hatch_color":{"type":"value","value":"#30a2da"},"hatch_alpha":{"type":"value","value":0.2}}}}},{"type":"object","name":"GlyphRenderer","id":"e44a155f-ea0b-4c50-9478-308955c0fcf5","attributes":{"name":"Success","data_source":{"type":"object","name":"ColumnDataSource","id":"f9364545-9eb7-431e-8b78-36c18be39c60","attributes":{"selected":{"type":"object","name":"Selection","id":"b92935d8-6741-418e-b43a-50678e74e009","attributes":{"indices":[],"line_indices":[]}},"selection_policy":{"type":"object","name":"UnionRenderers","id":"14f89f72-432f-4fd7-8bc7-6a81418f72db"},"data":{"type":"map","entries":[["repeat",{"type":"ndarray","array":{"type":"bytes","data":""},"shape":[0],"dtype":"float64","order":"little"}],["ext_offset",{"type":"ndarray","array":{"type":"bytes","data":""},"shape":[0],"dtype":"float64","order":"little"}],["success_rate",{"type":"ndarray","array":{"type":"bytes","data":""},"shape":[0],"dtype":"float64","order":"little"}]]}}},"view":{"type":"object","name":"CDSView","id":"f52101f4-a600-46c7-a96e-c8c60d588257","attributes":{"filter":{"type":"object","name":"AllIndices","id":"54fc7be5-db04-4462-8312-a2d8fddab3ab"}}},"glyph":{"type":"object","name":"Scatter","id":"c2e99d0b-a1fd-423e-9af8-75185862ec05","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"repeat"},"y":{"type":"field","field":"ext_offset"},"size":{"type":"value","value":10},"line_color":{"type":"value","value":"#007f00"},"fill_color":{"type":"value","value":"#007f00"},"hatch_color":{"type":"value","value":"#007f00"},"marker":{"type":"value","value":"cross"}}},"selection_glyph":{"type":"object","name":"Scatter","id":"e29dd654-432e-405e-8c84-410d8a2e2768","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"repeat"},"y":{"type":"field","field":"ext_offset"},"size":{"type":"value","value":10},"angle":{"type":"value","value":0.0},"line_color":{"type":"value","value":"#007f00"},"line_alpha":{"type":"value","value":1.0},"line_width":{"type":"value","value":1},"line_join":{"type":"value","value":"bevel"},"line_cap":{"type":"value","value":"butt"},"line_dash":{"type":"value","value":[]},"line_dash_offset":{"type":"value","value":0},"fill_color":{"type":"value","value":"#007f00"},"fill_alpha":{"type":"value","value":1.0},"hatch_color":{"type":"value","value":"#007f00"},"hatch_alpha":{"type":"value","value":1.0},"hatch_scale":{"type":"value","value":12.0},"hatch_pattern":{"type":"value","value":null},"hatch_weight":{"type":"value","value":1.0},"marker":{"type":"value","value":"cross"}}},"nonselection_glyph":{"type":"object","name":"Scatter","id":"9357ea6c-c7f6-4873-bc9d-d0eac0b323d9","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"repeat"},"y":{"type":"field","field":"ext_offset"},"size":{"type":"value","value":10},"line_color":{"type":"value","value":"#007f00"},"line_alpha":{"type":"value","value":0.1},"fill_color":{"type":"value","value":"#007f00"},"fill_alpha":{"type":"value","value":0.1},"hatch_color":{"type":"value","value":"#007f00"},"hatch_alpha":{"type":"value","value":0.1},"marker":{"type":"value","value":"cross"}}},"muted_glyph":{"type":"object","name":"Scatter","id":"01ce54cf-8492-4640-b8c5-ba1daa5a0634","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"repeat"},"y":{"type":"field","field":"ext_offset"},"size":{"type":"value","value":10},"line_color":{"type":"value","value":"#007f00"},"line_alpha":{"type":"value","value":0.2},"fill_color":{"type":"value","value":"#007f00"},"fill_alpha":{"type":"value","value":0.2},"hatch_color":{"type":"value","value":"#007f00"},"hatch_alpha":{"type":"value","value":0.2},"marker":{"type":"value","value":"cross"}}}}},{"type":"object","name":"GlyphRenderer","id":"d36dcc45-4c22-4ffd-8245-c5e3affd25db","attributes":{"name":"Reset","data_source":{"type":"object","name":"ColumnDataSource","id":"e604a06b-d7e7-4f86-8c62-6b30ef1d5f07","attributes":{"selected":{"type":"object","name":"Selection","id":"4aee5746-dccc-4aae-9a93-08b23419dc0d","attributes":{"indices":[],"line_indices":[]}},"selection_policy":{"type":"object","name":"UnionRenderers","id":"3f0d220c-4b1f-4f45-adca-6f91d4eb6fdb"},"data":{"type":"map","entries":[["repeat",{"type":"ndarray","array":{"type":"bytes","data":""},"shape":[0],"dtype":"float64","order":"little"}],["ext_offset",{"type":"ndarray","array":{"type":"bytes","data":""},"shape":[0],"dtype":"float64","order":"little"}],["reset_rate",{"type":"ndarray","array":{"type":"bytes","data":""},"shape":[0],"dtype":"float64","order":"little"}]]}}},"view":{"type":"object","name":"CDSView","id":"0d978329-f59e-4e02-a50a-b947284e1573","attributes":{"filter":{"type":"object","name":"AllIndices","id":"933dde6b-0d95-42b5-8e27-f820e85c1120"}}},"glyph":{"type":"object","name":"Scatter","id":"bd9517ba-ff8a-4cc4-b792-93abbd7ffcd0","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"repeat"},"y":{"type":"field","field":"ext_offset"},"size":{"type":"value","value":10},"angle":{"type":"value","value":0.7853981633974483},"line_color":{"type":"value","value":"#ff0000"},"fill_color":{"type":"value","value":"#ff0000"},"hatch_color":{"type":"value","value":"#ff0000"},"marker":{"type":"value","value":"cross"}}},"selection_glyph":{"type":"object","name":"Scatter","id":"724d57f3-eced-4655-a96f-526bf060cb16","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"repeat"},"y":{"type":"field","field":"ext_offset"},"size":{"type":"value","value":10},"angle":{"type":"value","value":0.7853981633974483},"line_color":{"type":"value","value":"#ff0000"},"line_alpha":{"type":"value","value":1.0},"line_width":{"type":"value","value":1},"line_join":{"type":"value","value":"bevel"},"line_cap":{"type":"value","value":"butt"},"line_dash":{"type":"value","value":[]},"line_dash_offset":{"type":"value","value":0},"fill_color":{"type":"value","value":"#ff0000"},"fill_alpha":{"type":"value","value":1.0},"hatch_color":{"type":"value","value":"#ff0000"},"hatch_alpha":{"type":"value","value":1.0},"hatch_scale":{"type":"value","value":12.0},"hatch_pattern":{"type":"value","value":null},"hatch_weight":{"type":"value","value":1.0},"marker":{"type":"value","value":"cross"}}},"nonselection_glyph":{"type":"object","name":"Scatter","id":"60189114-3b80-4cc6-81ba-80bf89cc64f9","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"repeat"},"y":{"type":"field","field":"ext_offset"},"size":{"type":"value","value":10},"angle":{"type":"value","value":0.7853981633974483},"line_color":{"type":"value","value":"#ff0000"},"line_alpha":{"type":"value","value":0.1},"fill_color":{"type":"value","value":"#ff0000"},"fill_alpha":{"type":"value","value":0.1},"hatch_color":{"type":"value","value":"#ff0000"},"hatch_alpha":{"type":"value","value":0.1},"marker":{"type":"value","value":"cross"}}},"muted_glyph":{"type":"object","name":"Scatter","id":"09c536fc-5ed3-49d8-b35f-58a36a2865e0","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"repeat"},"y":{"type":"field","field":"ext_offset"},"size":{"type":"value","value":10},"angle":{"type":"value","value":0.7853981633974483},"line_color":{"type":"value","value":"#ff0000"},"line_alpha":{"type":"value","value":0.2},"fill_color":{"type":"value","value":"#ff0000"},"fill_alpha":{"type":"value","value":0.2},"hatch_color":{"type":"value","value":"#ff0000"},"hatch_alpha":{"type":"value","value":0.2},"marker":{"type":"value","value":"cross"}}}}}],"toolbar":{"type":"object","name":"Toolbar","id":"c497d6be-b23d-4dbc-a6f9-5e30af3ba4a8","attributes":{"tools":[{"type":"object","name":"WheelZoomTool","id":"1dc4da7b-6a38-44f4-80d4-7976ae7ebe5b","attributes":{"tags":["hv_created"],"renderers":"auto","zoom_together":"none"}},{"type":"object","name":"HoverTool","id":"df1181fb-3e7b-4916-8deb-076d9b29eba2","attributes":{"tags":["hv_created"],"renderers":[{"id":"e44a155f-ea0b-4c50-9478-308955c0fcf5"}],"tooltips":[["repeat","@{repeat}"],["ext_offset","@{ext_offset}"],["success_rate","@{success_rate}"]]}},{"type":"object","name":"HoverTool","id":"aa898b3d-6eaa-4e99-b943-56829e2aecf9","attributes":{"tags":["hv_created"],"renderers":[{"id":"d36dcc45-4c22-4ffd-8245-c5e3affd25db"}],"tooltips":[["repeat","@{repeat}"],["ext_offset","@{ext_offset}"],["reset_rate","@{reset_rate}"]]}},{"type":"object","name":"SaveTool","id":"349af029-55f1-4f40-9eaf-f22ccf545568"},{"type":"object","name":"PanTool","id":"6b9127f5-5759-4cba-ba1e-337efde8bfa3"},{"type":"object","name":"BoxZoomTool","id":"92bba3d0-eefb-432a-9d56-81cf266dc830","attributes":{"overlay":{"type":"object","name":"BoxAnnotation","id":"1b433402-9816-408a-aad7-44a7dff1405f","attributes":{"syncable":false,"line_color":"black","line_alpha":1.0,"line_width":2,"line_dash":[4,4],"fill_color":"lightgrey","fill_alpha":0.5,"level":"overlay","visible":false,"left":{"type":"number","value":"nan"},"right":{"type":"number","value":"nan"},"top":{"type":"number","value":"nan"},"bottom":{"type":"number","value":"nan"},"left_units":"canvas","right_units":"canvas","top_units":"canvas","bottom_units":"canvas","handles":{"type":"object","name":"BoxInteractionHandles","id":"1a2f3bf0-adc7-4e08-8a5d-c6b885c0ea58","attributes":{"all":{"type":"object","name":"AreaVisuals","id":"5f9249aa-b544-4bf1-bda4-0cc0f4094083","attributes":{"fill_color":"white","hover_fill_color":"lightgray"}}}}}}}},{"type":"object","name":"ResetTool","id":"b7544d3e-6ca7-47b0-bf07-104b2da680dc"}],"active_drag":{"id":"6b9127f5-5759-4cba-ba1e-337efde8bfa3"},"active_scroll":{"id":"1dc4da7b-6a38-44f4-80d4-7976ae7ebe5b"}}},"left":[{"type":"object","name":"LinearAxis","id":"a955c3a0-932f-4e95-9523-85d944abb7b6","attributes":{"ticker":{"type":"object","name":"BasicTicker","id":"1d65dd9e-f7f8-4ce6-bcb7-cba5cc738c05","attributes":{"mantissas":[1,2,5]}},"formatter":{"type":"object","name":"BasicTickFormatter","id":"b28b014d-d6d9-4e10-9ba1-a2102f5bf6df"},"axis_label":"Ext_Offset","major_label_policy":{"type":"object","name":"AllLabels","id":"e67e54f8-8ed1-49e0-845f-fcbb1ab5505a"}}}],"below":[{"type":"object","name":"LinearAxis","id":"34ecf7e9-8f61-425c-b0f7-af7e96854064","attributes":{"ticker":{"type":"object","name":"BasicTicker","id":"1d7a64d7-12dc-4130-93e0-022f19ab2b72","attributes":{"mantissas":[1,2,5]}},"formatter":{"type":"object","name":"BasicTickFormatter","id":"e8b1c7e5-edbd-4738-bd65-8b92eefc75bd"},"axis_label":"Repeat","major_label_policy":{"type":"object","name":"AllLabels","id":"6dcd7873-4f63-4a7a-b963-753472207914"}}}],"center":[{"type":"object","name":"Grid","id":"04491546-d4ef-42f4-8861-e168e702a176","attributes":{"axis":{"id":"34ecf7e9-8f61-425c-b0f7-af7e96854064"},"grid_line_color":null}},{"type":"object","name":"Grid","id":"61d71195-fb09-4518-b86c-910d529c7206","attributes":{"dimension":1,"axis":{"id":"a955c3a0-932f-4e95-9523-85d944abb7b6"},"grid_line_color":null}},{"type":"object","name":"Legend","id":"6536e734-6e73-45d2-8922-b55410954916","attributes":{"click_policy":"mute","items":[{"type":"object","name":"LegendItem","id":"d8d7827d-59b4-4f7d-8bad-fb4ee263fbfb","attributes":{"label":{"type":"value","value":"Success"},"renderers":[{"id":"e44a155f-ea0b-4c50-9478-308955c0fcf5"}]}},{"type":"object","name":"LegendItem","id":"0e5411b6-98eb-4121-854f-3cfd5228b65b","attributes":{"label":{"type":"value","value":"Reset"},"renderers":[{"id":"d36dcc45-4c22-4ffd-8245-c5e3affd25db"}]}}]}}],"min_border_top":10,"min_border_bottom":10,"min_border_left":10,"min_border_right":10,"output_backend":"webgl"}},{"type":"object","name":"Spacer","id":"82064bd0-12db-41a2-a2fd-8f8d41ac4fb8","attributes":{"name":"HSpacer00455","stylesheets":["\n:host(.pn-loading):before, .pn-loading:before {\n  background-color: #c3c3c3;\n  mask-size: auto calc(min(50%, 400px));\n  -webkit-mask-size: auto calc(min(50%, 400px));\n}",{"id":"01034b92-7a1f-40d8-96e3-98666811ad31"},{"id":"6d7c9615-a9c1-4020-8422-87d37a1bcbe6"},{"id":"860c7e7b-a1a3-4e95-95e4-c38808f509aa"}],"margin":0,"sizing_mode":"stretch_width","align":"start"}}]}}],"defs":[{"type":"model","name":"ReactiveHTML1"},{"type":"model","name":"FlexBox1","properties":[{"name":"align_content","kind":"Any","default":"flex-start"},{"name":"align_items","kind":"Any","default":"flex-start"},{"name":"flex_direction","kind":"Any","default":"row"},{"name":"flex_wrap","kind":"Any","default":"wrap"},{"name":"gap","kind":"Any","default":""},{"name":"justify_content","kind":"Any","default":"flex-start"}]},{"type":"model","name":"FloatPanel1","properties":[{"name":"config","kind":"Any","default":{"type":"map"}},{"name":"contained","kind":"Any","default":true},{"name":"position","kind":"Any","default":"right-top"},{"name":"offsetx","kind":"Any","default":null},{"name":"offsety","kind":"Any","default":null},{"name":"theme","kind":"Any","default":"primary"},{"name":"status","kind":"Any","default":"normalized"}]},{"type":"model","name":"GridStack1","properties":[{"name":"mode","kind":"Any","default":"warn"},{"name":"ncols","kind":"Any","default":null},{"name":"nrows","kind":"Any","default":null},{"name":"allow_resize","kind":"Any","default":true},{"name":"allow_drag","kind":"Any","default":true},{"name":"state","kind":"Any","default":[]}]},{"type":"model","name":"drag1","properties":[{"name":"slider_width","kind":"Any","default":5},{"name":"slider_color","kind":"Any","default":"black"},{"name":"value","kind":"Any","default":50}]},{"type":"model","name":"click1","properties":[{"name":"terminal_output","kind":"Any","default":""},{"name":"debug_name","kind":"Any","default":""},{"name":"clears","kind":"Any","default":0}]},{"type":"model","name":"FastWrapper1","properties":[{"name":"object","kind":"Any","default":null},{"name":"style","kind":"Any","default":null}]},{"type":"model","name":"NotificationAreaBase1","properties":[{"name":"js_events","kind":"Any","default":{"type":"map"}},{"name":"position","kind":"Any","default":"bottom-right"},{"name":"_clear","kind":"Any","default":0}]},{"type":"model","name":"NotificationArea1","properties":[{"name":"js_events","kind":"Any","default":{"type":"map"}},{"name":"notifications","kind":"Any","default":[]},{"name":"position","kind":"Any","default":"bottom-right"},{"name":"_clear","kind":"Any","default":0},{"name":"types","kind":"Any","default":[{"type":"map","entries":[["type","warning"],["background","#ffc107"],["icon",{"type":"map","entries":[["className","fas fa-exclamation-triangle"],["tagName","i"],["color","white"]]}]]},{"type":"map","entries":[["type","info"],["background","#007bff"],["icon",{"type":"map","entries":[["className","fas fa-info-circle"],["tagName","i"],["color","white"]]}]]}]}]},{"type":"model","name":"Notification","properties":[{"name":"background","kind":"Any","default":null},{"name":"duration","kind":"Any","default":3000},{"name":"icon","kind":"Any","default":null},{"name":"message","kind":"Any","default":""},{"name":"notification_type","kind":"Any","default":null},{"name":"_destroyed","kind":"Any","default":false}]},{"type":"model","name":"TemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"BootstrapTemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"TemplateEditor1","properties":[{"name":"layout","kind":"Any","default":[]}]},{"type":"model","name":"MaterialTemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"ReactiveESM1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"JSComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"ReactComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"AnyWidgetComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"request_value1","properties":[{"name":"fill","kind":"Any","default":"none"},{"name":"_synced","kind":"Any","default":null},{"name":"_request_sync","kind":"Any","default":0}]}]}};
      var render_items = [{"docid":"c10c2311-2af9-40b5-abfa-449d06ede219","roots":{"7e5b8aaa-281a-489e-8073-88858a299a51":"b15a22e6-f577-477d-aca9-7a45e31ab0fc"},"root_ids":["7e5b8aaa-281a-489e-8073-88858a299a51"]}];
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

