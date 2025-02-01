Part 2, Topic 1: CPA Attack on 32bit AES (MAIN)
===============================================



**SUMMARY:** *So far, we’ve been focusing on a single implementation of
AES, TINYAES128C (or AVRCRYPTOLIB, if you’re on XMEGA). TINYAES128C,
which is designed to run on a variety of microcontrollers, doesn’t make
any implementation specific optimizations. In this lab, we’ll look at
how we can break a 32-bit optimized version of AES using a CPA attack.*

**LEARNING OUTCOMES:**

-  Understanding how AES can be optimized on 32-bit platforms.
-  Attacking an optimized version of AES using CPA

Optimizing AES
--------------

A 32-bit machine can operate on 32-bit words, so it seems wasteful to
use the same 8-bit operations. For example, if we look at the SBox
operation:

$ b = sbox(state) = sbox(:raw-latex:`\left[ \begin{array}
& S0 & S4 & S8 & S12 \\
S1 & S5 & S9 & S13 \\
S2 & S6 & S10 & S14 \\
S3 & S7 & S11 & S15
\end{array} \right]`) = :raw-latex:`\left[ \begin{array}
& S0 & S4 & S8 & S12 \\
S5 & S9 & S13 & S1 \\
S10 & S14 & S2 & S6 \\
S15 & S3 & S7 & S11
\end{array} \right]`$

we could consider each row as a 32-bit number and do three bitwise
rotates instead of moving a bunch of stuff around in memory. Even
better, we can speed up AES considerably by generating 32-bit lookup
tables, called T-Tables, as was described in the book `The Design of
Rijndael <http://www.springer.com/gp/book/9783540425809>`__ which was
published by the authors of AES.

In order to take full advantage of our 32 bit machine, we can examine a
typical round of AES. With the exception of the final round, each round
looks like:

:math:`\text{a = Round Input}`

:math:`\text{b = SubBytes(a)}`

:math:`\text{c = ShiftRows(b)}`

:math:`\text{d = MixColumns(c)}`

:math:`\text{a' = AddRoundKey(d) = Round Output}`

We’ll leave AddRoundKey the way it is. The other operations are:

:math:`b_{i,j} = \text{sbox}[a_{i,j}]`

:math:`\left[ \begin{array} { c } { c _ { 0 , j } } \\ { c _ { 1 , j } } \\ { c _ { 2 , j } } \\ { c _ { 3 , j } } \end{array} \right] = \left[ \begin{array} { l } { b _ { 0 , j + 0 } } \\ { b _ { 1 , j + 1 } } \\ { b _ { 2 , j + 2 } } \\ { b _ { 3 , j + 3 } } \end{array} \right]`

:math:`\left[ \begin{array} { l } { d _ { 0 , j } } \\ { d _ { 1 , j } } \\ { d _ { 2 , j } } \\ { d _ { 3 , j } } \end{array} \right] = \left[ \begin{array} { l l l l } { 02 } & { 03 } & { 01 } & { 01 } \\ { 01 } & { 02 } & { 03 } & { 01 } \\ { 01 } & { 01 } & { 02 } & { 03 } \\ { 03 } & { 01 } & { 01 } & { 02 } \end{array} \right] \times \left[ \begin{array} { c } { c _ { 0 , j } } \\ { c _ { 1 , j } } \\ { c _ { 2 , j } } \\ { c _ { 3 , j } } \end{array} \right]`

Note that the ShiftRows operation :math:`b_{i, j+c}` is a cyclic shift
and the matrix multiplcation in MixColumns denotes the xtime operation
in GF(\ :math:`2^8`).

It’s possible to combine all three of these operations into a single
line. We can write 4 bytes of :math:`d` as the linear combination of
four different 4 byte vectors:

:math:`\left[ \begin{array} { l } { d _ { 0 , j } } \\ { d _ { 1 , j } } \\ { d _ { 2 , j } } \\ { d _ { 3 , j } } \end{array} \right] = \left[ \begin{array} { l } { 02 } \\ { 01 } \\ { 01 } \\ { 03 } \end{array} \right] \operatorname { sbox } \left[ a _ { 0 , j + 0 } \right] \oplus \left[ \begin{array} { l } { 03 } \\ { 02 } \\ { 01 } \\ { 01 } \end{array} \right] \operatorname { sbox } \left[ a _ { 1 , j + 1 } \right] \oplus \left[ \begin{array} { c } { 01 } \\ { 03 } \\ { 02 } \\ { 01 } \end{array} \right] \operatorname { sbox } \left[ a _ { 2 , j + 2 } \right] \oplus \left[ \begin{array} { c } { 01 } \\ { 01 } \\ { 03 } \\ { 02 } \end{array} \right] \operatorname { sbox } \left[ a _ { 3 , j + 3 } \right]`

Now, for each of these four components, we can tabulate the outputs for
every possible 8-bit input:

:math:`T _ { 0 } [ a ] = \left[ \begin{array} { l l } { 02 \times \operatorname { sbox } [ a ] } \\ { 01 \times \operatorname { sbox } [ a ] } \\ { 01 \times \operatorname { sbox } [ a ] } \\ { 03 \times \operatorname { sbox } [ a ] } \end{array} \right]`

:math:`T _ { 1 } [ a ] = \left[ \begin{array} { l } { 03 \times \operatorname { sbox } [ a ] } \\ { 02 \times \operatorname { sbox } [ a ] } \\ { 01 \times \operatorname { sbox } [ a ] } \\ { 01 \times \operatorname { sbox } [ a ] } \end{array} \right]`

:math:`T _ { 2 } [ a ] = \left[ \begin{array} { l l } { 01 \times \operatorname { sbox } [ a ] } \\ { 03 \times \operatorname { sbox } [ a ] } \\ { 02 \times \operatorname { sbox } [ a ] } \\ { 01 \times \operatorname { sbox } [ a ] } \end{array} \right]`

:math:`T _ { 3 } [ a ] = \left[ \begin{array} { l l } { 01 \times \operatorname { sbox } [ a ] } \\ { 01 \times \operatorname { sbox } [ a ] } \\ { 03 \times \operatorname { sbox } [ a ] } \\ { 02 \times \operatorname { sbox } [ a ] } \end{array} \right]`

These tables have 2^8 different 32-bit entries, so together the tables
take up 4 kB. Finally, we can quickly compute one round of AES by
calculating

:math:`\left[ \begin{array} { l } { d _ { 0 , j } } \\ { d _ { 1 , j } } \\ { d _ { 2 , j } } \\ { d _ { 3 , j } } \end{array} \right] = T _ { 0 } \left[ a _ { 0 } , j + 0 \right] \oplus T _ { 1 } \left[ a _ { 1 } , j + 1 \right] \oplus T _ { 2 } \left[ a _ { 2 } , j + 2 \right] \oplus T _ { 3 } \left[ a _ { 3 } , j + 3 \right]`

All together, with AddRoundKey at the end, a single round now takes 16
table lookups and 16 32-bit XOR operations. This arrangement is much
more efficient than the traditional 8-bit implementation. There are a
few more tradeoffs that can be made: for instance, the tables only
differ by 8-bit shifts, so it’s also possible to store only 1 kB of
lookup tables at the expense of a few rotate operations.

While the TINYAES128C library we’ve been using doesn’t make this
optimization, another library included with ChipWhisperer called MBEDTLS
does.


**In [1]:**

.. code:: ipython3

    SCOPETYPE = 'CWNANO'
    PLATFORM = 'CWNANO'
    VERSION = 'HARDWARE'
    SS_VER = 'SS_VER_2_1'
    
    allowable_exceptions = None
    CRYPTO_TARGET = 'TINYAES128C'



**In [2]:**

.. code:: ipython3

    CRYPTO_TARGET = 'MBEDTLS' # overwrite auto inserted CRYPTO_TARGET


**In [3]:**

.. code:: ipython3

    if VERSION == 'HARDWARE':
        
        #!/usr/bin/env python
        # coding: utf-8
        
        # # Part 2, Topic 1: CPA Attack on 32bit AES (HARDWARE)
        
        # ---
        # NOTE: This lab references some (commercial) training material on [ChipWhisperer.io](https://www.ChipWhisperer.io). You can freely execute and use the lab per the open-source license (including using it in your own courses if you distribute similarly), but you must maintain notice about this source location. Consider joining our training course to enjoy the full experience.
        # 
        # ---
        
        # Usual capture, just using MBEDTLS instead of TINYAES128
        
        # In[ ]:
        
        
        
        
        
        # In[ ]:
        
        
        
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
        
        
    
        
        
        # In[ ]:
        
        
        try:
            get_ipython().run_cell_magic('bash', '-s "$PLATFORM" "$CRYPTO_TARGET" "$SS_VER"', 'cd ../../../firmware/mcu/simpleserial-aes\nmake PLATFORM=$1 CRYPTO_TARGET=$2 SS_VER=$3\n &> /tmp/tmp.txt')
        except:
            x=open("/tmp/tmp.txt").read(); print(x); raise OSError(x)
    
        
        
        # In[ ]:
        
        
        fw_path = '../../../firmware/mcu/simpleserial-aes/simpleserial-aes-{}.hex'.format(PLATFORM)
        cw.program_target(scope, prog, fw_path)
        
        
        # In[ ]:
        
        
        #Capture Traces
        from tqdm.notebook import trange, trange
        import numpy as np
        import time
        
        ktp = cw.ktp.Basic()
        
        traces = []
        N = 100  # Number of traces
        project = cw.create_project("traces/32bit_AES.cwp", overwrite=True)
        
        for i in trange(N, desc='Capturing traces'):
            key, text = ktp.next()  # manual creation of a key, text pair can be substituted here
        
            trace = cw.capture_trace(scope, target, text, key)
            if trace is None:
                continue
            project.traces.append(trace)
        
        try:
            print(scope.adc.trig_count) # print if this exists
        except:
            pass
        project.save()
        
        
        # In[ ]:
        
        
        scope.dis()
        target.dis()
        
        
    
    elif VERSION == 'SIMULATED':
        
        #!/usr/bin/env python
        # coding: utf-8
        
        # # Part 2, Topic 1: CPA Attack on 32bit AES (SIMULATED)
        
        # ---
        # NOTE: This lab references some (commercial) training material on [ChipWhisperer.io](https://www.ChipWhisperer.io). You can freely execute and use the lab per the open-source license (including using it in your own courses if you distribute similarly), but you must maintain notice about this source location. Consider joining our training course to enjoy the full experience.
        # 
        # ---
        
        # In[ ]:
        
        
        import chipwhisperer as cw
        project = cw.open_project("traces/32bit_AES.cwp")
        
        



**Out [3]:**



.. parsed-literal::

    INFO: Found ChipWhisperer😍
    Building for platform CWNANO with CRYPTO\_TARGET=MBEDTLS
    SS\_VER set to SS\_VER\_2\_1
    SS\_VER set to SS\_VER\_2\_1
    Blank crypto options, building for AES128
    .
    Welcome to another exciting ChipWhisperer target build!!
    arm-none-eabi-gcc (15:9-2019-q4-0ubuntu1) 9.2.1 20191025 (release) [ARM/arm-9-branch revision 277599]
    Copyright (C) 2019 Free Software Foundation, Inc.
    This is free software; see the source for copying conditions.  There is NO
    warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
    
    Size after:
       text	   data	    bss	    dec	    hex	filename
       5564	    536	   1568	   7668	   1df4	simpleserial-aes-CWNANO.elf
    +--------------------------------------------------------
    + Built for platform CWNANO Built-in Target (STM32F030) with:
    + CRYPTO\_TARGET = MBEDTLS
    + CRYPTO\_OPTIONS = AES128C
    +--------------------------------------------------------
    Detected known STMF32: STM32F04xxx
    Extended erase (0x44), this can take ten seconds or more
    Attempting to program 6099 bytes at 0x8000000
    STM32F Programming flash...
    STM32F Reading flash...
    Verified flash OK, 6099 bytes




.. parsed-literal::

    Capturing traces:   0%|          | 0/100 [00:00<?, ?it/s]


If we plot the AES power trace:


**In [4]:**

.. code:: ipython3

    cw.plot(project.waves[0])


**Out [4]:**


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
        <div id='f08e3cc9-686d-4196-91a4-9bad44e922a5'>
      <div id="f84e058d-3e78-409a-ad4c-498ae2948f70" data-root-id="f08e3cc9-686d-4196-91a4-9bad44e922a5" style="display: contents;"></div>
    </div>
    <script type="application/javascript">(function(root) {
      var docs_json = {"917af6ba-a670-4e8f-9741-eea899122476":{"version":"3.6.1","title":"Bokeh Application","roots":[{"type":"object","name":"panel.models.browser.BrowserInfo","id":"f08e3cc9-686d-4196-91a4-9bad44e922a5"},{"type":"object","name":"panel.models.comm_manager.CommManager","id":"e17cd5ee-fd2a-4f44-8bac-d9a66dda8f26","attributes":{"plot_id":"f08e3cc9-686d-4196-91a4-9bad44e922a5","comm_id":"04795ee036fe4ed3bb38db2e844761e3","client_comm_id":"ed71e019840447559278e6613c975f36"}}],"defs":[{"type":"model","name":"ReactiveHTML1"},{"type":"model","name":"FlexBox1","properties":[{"name":"align_content","kind":"Any","default":"flex-start"},{"name":"align_items","kind":"Any","default":"flex-start"},{"name":"flex_direction","kind":"Any","default":"row"},{"name":"flex_wrap","kind":"Any","default":"wrap"},{"name":"gap","kind":"Any","default":""},{"name":"justify_content","kind":"Any","default":"flex-start"}]},{"type":"model","name":"FloatPanel1","properties":[{"name":"config","kind":"Any","default":{"type":"map"}},{"name":"contained","kind":"Any","default":true},{"name":"position","kind":"Any","default":"right-top"},{"name":"offsetx","kind":"Any","default":null},{"name":"offsety","kind":"Any","default":null},{"name":"theme","kind":"Any","default":"primary"},{"name":"status","kind":"Any","default":"normalized"}]},{"type":"model","name":"GridStack1","properties":[{"name":"mode","kind":"Any","default":"warn"},{"name":"ncols","kind":"Any","default":null},{"name":"nrows","kind":"Any","default":null},{"name":"allow_resize","kind":"Any","default":true},{"name":"allow_drag","kind":"Any","default":true},{"name":"state","kind":"Any","default":[]}]},{"type":"model","name":"drag1","properties":[{"name":"slider_width","kind":"Any","default":5},{"name":"slider_color","kind":"Any","default":"black"},{"name":"value","kind":"Any","default":50}]},{"type":"model","name":"click1","properties":[{"name":"terminal_output","kind":"Any","default":""},{"name":"debug_name","kind":"Any","default":""},{"name":"clears","kind":"Any","default":0}]},{"type":"model","name":"FastWrapper1","properties":[{"name":"object","kind":"Any","default":null},{"name":"style","kind":"Any","default":null}]},{"type":"model","name":"NotificationAreaBase1","properties":[{"name":"js_events","kind":"Any","default":{"type":"map"}},{"name":"position","kind":"Any","default":"bottom-right"},{"name":"_clear","kind":"Any","default":0}]},{"type":"model","name":"NotificationArea1","properties":[{"name":"js_events","kind":"Any","default":{"type":"map"}},{"name":"notifications","kind":"Any","default":[]},{"name":"position","kind":"Any","default":"bottom-right"},{"name":"_clear","kind":"Any","default":0},{"name":"types","kind":"Any","default":[{"type":"map","entries":[["type","warning"],["background","#ffc107"],["icon",{"type":"map","entries":[["className","fas fa-exclamation-triangle"],["tagName","i"],["color","white"]]}]]},{"type":"map","entries":[["type","info"],["background","#007bff"],["icon",{"type":"map","entries":[["className","fas fa-info-circle"],["tagName","i"],["color","white"]]}]]}]}]},{"type":"model","name":"Notification","properties":[{"name":"background","kind":"Any","default":null},{"name":"duration","kind":"Any","default":3000},{"name":"icon","kind":"Any","default":null},{"name":"message","kind":"Any","default":""},{"name":"notification_type","kind":"Any","default":null},{"name":"_destroyed","kind":"Any","default":false}]},{"type":"model","name":"TemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"BootstrapTemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"TemplateEditor1","properties":[{"name":"layout","kind":"Any","default":[]}]},{"type":"model","name":"MaterialTemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"ReactiveESM1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"JSComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"ReactComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"AnyWidgetComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"request_value1","properties":[{"name":"fill","kind":"Any","default":"none"},{"name":"_synced","kind":"Any","default":null},{"name":"_request_sync","kind":"Any","default":0}]}]}};
      var render_items = [{"docid":"917af6ba-a670-4e8f-9741-eea899122476","roots":{"f08e3cc9-686d-4196-91a4-9bad44e922a5":"f84e058d-3e78-409a-ad4c-498ae2948f70"},"root_ids":["f08e3cc9-686d-4196-91a4-9bad44e922a5"]}];
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
        <div id='fa2ca670-4426-466d-beb8-b7990e9967af'>
      <div id="d8cda1f2-d3f1-4a05-a96f-3dd3f4496ab6" data-root-id="fa2ca670-4426-466d-beb8-b7990e9967af" style="display: contents;"></div>
    </div>
    <script type="application/javascript">(function(root) {
      var docs_json = {"1c2e8247-a674-47e1-a918-111b33e8fefa":{"version":"3.6.1","title":"Bokeh Application","roots":[{"type":"object","name":"Row","id":"fa2ca670-4426-466d-beb8-b7990e9967af","attributes":{"name":"Row00266","tags":["embedded"],"stylesheets":["\n:host(.pn-loading):before, .pn-loading:before {\n  background-color: #c3c3c3;\n  mask-size: auto calc(min(50%, 400px));\n  -webkit-mask-size: auto calc(min(50%, 400px));\n}",{"type":"object","name":"ImportedStyleSheet","id":"80d120fc-7bee-49c6-9c85-520aafe73b08","attributes":{"url":"https://cdn.holoviz.org/panel/1.5.4/dist/css/loading.css"}},{"type":"object","name":"ImportedStyleSheet","id":"7e8679ce-a6da-4f58-b731-39d4dc726ac9","attributes":{"url":"https://cdn.holoviz.org/panel/1.5.4/dist/css/listpanel.css"}},{"type":"object","name":"ImportedStyleSheet","id":"bfd7d645-80e0-46ba-9d4b-3bafc04dd6e6","attributes":{"url":"https://cdn.holoviz.org/panel/1.5.4/dist/bundled/theme/default.css"}},{"type":"object","name":"ImportedStyleSheet","id":"bb561f1c-3490-4e30-8893-f496cdff403e","attributes":{"url":"https://cdn.holoviz.org/panel/1.5.4/dist/bundled/theme/native.css"}}],"min_width":800,"margin":0,"sizing_mode":"stretch_width","align":"start","children":[{"type":"object","name":"Spacer","id":"9937aa75-fcaf-484e-92e0-6315bb4858f7","attributes":{"name":"HSpacer00270","stylesheets":["\n:host(.pn-loading):before, .pn-loading:before {\n  background-color: #c3c3c3;\n  mask-size: auto calc(min(50%, 400px));\n  -webkit-mask-size: auto calc(min(50%, 400px));\n}",{"id":"80d120fc-7bee-49c6-9c85-520aafe73b08"},{"id":"bfd7d645-80e0-46ba-9d4b-3bafc04dd6e6"},{"id":"bb561f1c-3490-4e30-8893-f496cdff403e"}],"margin":0,"sizing_mode":"stretch_width","align":"start"}},{"type":"object","name":"Figure","id":"cf7f064e-6d5e-46bf-90a4-ef78b3e9d9d7","attributes":{"width":800,"margin":[5,10],"sizing_mode":"fixed","align":"start","x_range":{"type":"object","name":"Range1d","id":"8574d977-48ec-455c-8a0d-58885acf0397","attributes":{"name":"x","tags":[[["x",null]],[]],"end":4999.0,"reset_start":0.0,"reset_end":4999.0}},"y_range":{"type":"object","name":"Range1d","id":"a5d7623e-fa8f-4660-bb26-67ca17a0b4e6","attributes":{"name":"y","tags":[[["y",null]],{"type":"map","entries":[["invert_yaxis",false],["autorange",false]]}],"start":-0.444140625,"end":0.010546875000000004,"reset_start":-0.444140625,"reset_end":0.010546875000000004}},"x_scale":{"type":"object","name":"LinearScale","id":"b1254399-bf58-40a6-b6f6-3970d45f5958"},"y_scale":{"type":"object","name":"LinearScale","id":"dcbb0bde-6220-4651-8c0c-903b95ef182d"},"title":{"type":"object","name":"Title","id":"5d17ed8d-ec1b-432e-b82d-988f150c7fcb","attributes":{"text_color":"black","text_font_size":"12pt"}},"renderers":[{"type":"object","name":"GlyphRenderer","id":"f1cb5d7b-f6f6-44e9-8d22-c1ed9d49a30a","attributes":{"data_source":{"type":"object","name":"ColumnDataSource","id":"89a741f5-c1a4-4f50-b32f-d9834eacbee1","attributes":{"selected":{"type":"object","name":"Selection","id":"f9985615-4b65-4d7a-89af-0b4d0198d74b","attributes":{"indices":[],"line_indices":[]}},"selection_policy":{"type":"object","name":"UnionRenderers","id":"bd3ee3f6-0364-437b-93a2-aa947869fc0d"},"data":{"type":"map","entries":[["x",{"type":"ndarray","array":{"type":"bytes","data":"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"},"shape":[5000],"dtype":"float64","order":"little"}],["y",{"type":"ndarray","array":{"type":"bytes","data":"AAAAAACAxb8AAAAAAAC/vwAAAAAAgMm/AAAAAACA1r8AAAAAAIDBvwAAAAAAgMK/AAAAAACAzr8AAAAAAIDWvwAAAAAAQNW/AAAAAADA1b8AAAAAAADHvwAAAAAAgM6/AAAAAAAAw78AAAAAAIDMvwAAAAAAwNW/AAAAAACAxb8AAAAAAAC0vwAAAAAAAMu/AAAAAADA078AAAAAAEDVvwAAAAAAALW/AAAAAACAw78AAAAAAIDAvwAAAAAAgMq/AAAAAACAxb8AAAAAAIDMvwAAAAAAgNS/AAAAAABA1b8AAAAAAAC2vwAAAAAAAK6/AAAAAAAAyb8AAAAAAADWvwAAAAAAALu/AAAAAACAx78AAAAAAMDWvwAAAAAAgMW/AAAAAACAzL8AAAAAAIDFvwAAAAAAAMu/AAAAAABA1r8AAAAAAAC7vwAAAAAAAMm/AAAAAAAA1r8AAAAAAADDvwAAAAAAgMy/AAAAAAAAv78AAAAAAIDAvwAAAAAAgM2/AAAAAACA1r8AAAAAAAC/vwAAAAAAAMm/AAAAAACA1r8AAAAAAIDCvwAAAAAAAM2/AAAAAACAwL8AAAAAAADCvwAAAAAAgM6/AAAAAAAA178AAAAAAAC+vwAAAAAAgMm/AAAAAADA1r8AAAAAAADEvwAAAAAAgM2/AAAAAACAwb8AAAAAAIDBvwAAAAAAAM+/AAAAAADA1r8AAAAAAAC+vwAAAAAAAMq/AAAAAADA1r8AAAAAAIDFvwAAAAAAgM6/AAAAAACAwb8AAAAAAADCvwAAAAAAgM6/AAAAAAAA178AAAAAAAC+vwAAAAAAAMq/AAAAAABA1r8AAAAAAADFvwAAAAAAgM2/AAAAAACAwb8AAAAAAADCvwAAAAAAANC/AAAAAABA178AAAAAAADBvwAAAAAAAMu/AAAAAADA1r8AAAAAAIDEvwAAAAAAgM6/AAAAAAAAwr8AAAAAAADDvwAAAAAAQNC/AAAAAADA178AAAAAAIDAvwAAAAAAgMq/AAAAAACA178AAAAAAIDFvwAAAAAAAM+/AAAAAAAAw78AAAAAAADEvwAAAAAAgNC/AAAAAABA178AAAAAAIDAvwAAAAAAgMq/AAAAAADA178AAAAAAIDGvwAAAAAAANC/AAAAAAAAw78AAAAAAIDDvwAAAAAAQNC/AAAAAADA178AAAAAAIDAvwAAAAAAgMy/AAAAAACA178AAAAAAIDGvwAAAAAAANC/AAAAAAAAw78AAAAAAADEvwAAAAAAgNC/AAAAAADA178AAAAAAADCvwAAAAAAgMy/AAAAAAAA2L8AAAAAAIDFvwAAAAAAQNC/AAAAAACAw78AAAAAAADFvwAAAAAAwNC/AAAAAACA2L8AAAAAAIDBvwAAAAAAAMy/AAAAAADA178AAAAAAADGvwAAAAAAANC/AAAAAACAw78AAAAAAADFvwAAAAAAwNC/AAAAAADA178AAAAAAADBvwAAAAAAAMu/AAAAAADA178AAAAAAIDGvwAAAAAAQNC/AAAAAACAw78AAAAAAADEvwAAAAAAgNC/AAAAAAAA2L8AAAAAAIDAvwAAAAAAAMy/AAAAAABA2L8AAAAAAADHvwAAAAAAQNC/AAAAAAAAw78AAAAAAIDDvwAAAAAAgNC/AAAAAADA178AAAAAAADCvwAAAAAAAMy/AAAAAAAA2L8AAAAAAIDFvwAAAAAAANC/AAAAAACAwr8AAAAAAIDDvwAAAAAAgNC/AAAAAABA2L8AAAAAAADCvwAAAAAAgMy/AAAAAADA178AAAAAAIDGvwAAAAAAANC/AAAAAAAAw78AAAAAAADEvwAAAAAAANG/AAAAAADA178AAAAAAIDBvwAAAAAAAMu/AAAAAADA178AAAAAAIDGvwAAAAAAgM+/AAAAAAAAx78AAAAAAAC6vwAAAAAAgMK/AAAAAAAA0b8AAAAAAEDZvwAAAAAAgMq/AAAAAAAA0L8AAAAAAIDFvwAAAAAAAMy/AAAAAACA1r8AAAAAAMDWvwAAAAAAQNe/AAAAAADA1r8AAAAAAIDVvwAAAAAAAL6/AAAAAACAzL8AAAAAAIDXvwAAAAAAgMW/AAAAAACAzb8AAAAAAADEvwAAAAAAAL6/AAAAAACAzL8AAAAAAADWvwAAAAAAgNe/AAAAAACA1r8AAAAAAMDVvwAAAAAAAL2/AAAAAACAxr8AAAAAAMDUvwAAAAAAgMe/AAAAAACAwr8AAAAAAIDOvwAAAAAAAMa/AAAAAAAAzb8AAAAAAADEvwAAAAAAgM2/AAAAAAAAxb8AAAAAAIDMvwAAAAAAANW/AAAAAADA1r8AAAAAAIDAvwAAAAAAgMq/AAAAAAAAw78AAAAAAIDMvwAAAAAAwNa/AAAAAACAwL8AAAAAAIDMvwAAAAAAgMC/AAAAAACAzr8AAAAAAADIvwAAAAAAAM2/AAAAAADA1b8AAAAAAEDXvwAAAAAAAMG/AAAAAACAy78AAAAAAIDDvwAAAAAAgMy/AAAAAACA1r8AAAAAAADCvwAAAAAAgM2/AAAAAACAwL8AAAAAAIDOvwAAAAAAgMe/AAAAAACAzb8AAAAAAADWvwAAAAAAwNe/AAAAAAAAwr8AAAAAAIDMvwAAAAAAAMS/AAAAAAAAzb8AAAAAAMDWvwAAAAAAgMG/AAAAAACAzL8AAAAAAIDBvwAAAAAAAM+/AAAAAACAx78AAAAAAIDMvwAAAAAAwNW/AAAAAABA178AAAAAAADCvwAAAAAAAM2/AAAAAACAxL8AAAAAAADNvwAAAAAAQNe/AAAAAACAwb8AAAAAAIDMvwAAAAAAgMK/AAAAAAAAzb8AAAAAAADFvwAAAAAAAMy/AAAAAAAAw78AAAAAAIDOvwAAAAAAAMe/AAAAAABA0L8AAAAAAIDGvwAAAAAAAM2/AAAAAABA1b8AAAAAAEDXvwAAAAAAAMG/AAAAAACAzL8AAAAAAADFvwAAAAAAAM2/AAAAAADA1r8AAAAAAIDCvwAAAAAAAM2/AAAAAAAAwb8AAAAAAADPvwAAAAAAgMi/AAAAAACAzb8AAAAAAEDWvwAAAAAAgNe/AAAAAACAwb8AAAAAAADMvwAAAAAAAMS/AAAAAAAAzb8AAAAAAMDWvwAAAAAAAMK/AAAAAACAzb8AAAAAAADBvwAAAAAAgM+/AAAAAAAAx78AAAAAAIDNvwAAAAAAQNa/AAAAAACA178AAAAAAIDCvwAAAAAAAM2/AAAAAAAAxb8AAAAAAIDNvwAAAAAAQNe/AAAAAAAAwr8AAAAAAIDNvwAAAAAAAMK/AAAAAACAz78AAAAAAIDIvwAAAAAAgM2/AAAAAADA1b8AAAAAAEDXvwAAAAAAAMK/AAAAAACAzL8AAAAAAADFvwAAAAAAgM2/AAAAAADA1r8AAAAAAIDBvwAAAAAAAM2/AAAAAACAwr8AAAAAAIDNvwAAAAAAgMW/AAAAAACAzL8AAAAAAIDEvwAAAAAAgM6/AAAAAACAx78AAAAAAEDQvwAAAAAAgMa/AAAAAACAzb8AAAAAAADWvwAAAAAAgNe/AAAAAAAAwr8AAAAAAIDMvwAAAAAAgMS/AAAAAACAzb8AAAAAAMDWvwAAAAAAAMK/AAAAAACAzb8AAAAAAIDBvwAAAAAAAM+/AAAAAACAyL8AAAAAAIDNvwAAAAAAQNa/AAAAAAAA2L8AAAAAAIDCvwAAAAAAgMy/AAAAAACAw78AAAAAAIDNvwAAAAAAwNa/AAAAAAAAwr8AAAAAAADOvwAAAAAAAMK/AAAAAACAz78AAAAAAADIvwAAAAAAgM2/AAAAAABA1r8AAAAAAIDXvwAAAAAAgMK/AAAAAACAzb8AAAAAAADFvwAAAAAAgM2/AAAAAABA178AAAAAAIDCvwAAAAAAgM2/AAAAAACAwr8AAAAAAADQvwAAAAAAAMm/AAAAAACAzb8AAAAAAMDVvwAAAAAAQNe/AAAAAACAwr8AAAAAAADNvwAAAAAAgMW/AAAAAACAzr8AAAAAAEDXvwAAAAAAAMK/AAAAAAAAzb8AAAAAAADDvwAAAAAAgM2/AAAAAACAxb8AAAAAAIDNvwAAAAAAAMS/AAAAAACAzr8AAAAAAIDGvwAAAAAAQNC/AAAAAAAAx78AAAAAAIDNvwAAAAAAwNW/AAAAAACA178AAAAAAADCvwAAAAAAgMy/AAAAAACAxL8AAAAAAADOvwAAAAAAgNe/AAAAAACAwr8AAAAAAIDNvwAAAAAAAMG/AAAAAAAA0L8AAAAAAADIvwAAAAAAgM2/AAAAAABA1r8AAAAAAIDXvwAAAAAAgMK/AAAAAACAzL8AAAAAAADEvwAAAAAAAM2/AAAAAABA178AAAAAAADCvwAAAAAAgM2/AAAAAACAwb8AAAAAAADPvwAAAAAAgMi/AAAAAACAzb8AAAAAAADWvwAAAAAAgNe/AAAAAAAAwr8AAAAAAADNvwAAAAAAgMS/AAAAAACAzb8AAAAAAEDXvwAAAAAAAMK/AAAAAACAzb8AAAAAAADCvwAAAAAAgM+/AAAAAACAyL8AAAAAAIDNvwAAAAAAwNW/AAAAAABA178AAAAAAADCvwAAAAAAgM2/AAAAAAAAxb8AAAAAAADOvwAAAAAAANe/AAAAAAAAwr8AAAAAAADNvwAAAAAAgMK/AAAAAAAAzr8AAAAAAIDFvwAAAAAAgMy/AAAAAAAAx78AAAAAAIDMvwAAAAAAwNW/AAAAAACA2L8AAAAAAMDXvwAAAAAAQNe/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AAAAAAAAzL8AAAAAAIDXvwAAAAAAAMe/AAAAAACAzr8AAAAAAIDFvwAAAAAAAM6/AAAAAACAw78AAAAAAIDNvwAAAAAAAMS/AAAAAAAAzb8AAAAAAADDvwAAAAAAgMy/AAAAAAAAwL8AAAAAAADCvwAAAAAAgM2/AAAAAADA1r8AAAAAAIDAvwAAAAAAAMy/AAAAAAAAv78AAAAAAADKvwAAAAAAgNW/AAAAAACA1L8AAAAAAAC/vwAAAAAAgMu/AAAAAACAwr8AAAAAAIDOvwAAAAAAgMW/AAAAAACAzr8AAAAAAADEvwAAAAAAgM2/AAAAAACAw78AAAAAAADNvwAAAAAAAMS/AAAAAACAzL8AAAAAAIDBvwAAAAAAAMy/AAAAAACAxL8AAAAAAIDKvwAAAAAAgNS/AAAAAAAAxr8AAAAAAADNvwAAAAAAQNa/AAAAAACAwL8AAAAAAIDFvwAAAAAAgNS/AAAAAACAxb8AAAAAAIDNvwAAAAAAgMS/AAAAAACAzb8AAAAAAIDFvwAAAAAAgM6/AAAAAACAxL8AAAAAAIDNvwAAAAAAgMS/AAAAAACAzb8AAAAAAIDDvwAAAAAAgMy/AAAAAACAwr8AAAAAAIDNvwAAAAAAgMK/AAAAAACAzb8AAAAAAADEvwAAAAAAAMq/AAAAAAAA1L8AAAAAAADXvwAAAAAAAMW/AAAAAACAxr8AAAAAAIDAvwAAAAAAAKC/AAAAAAAAwL8AAAAAAIDOvwAAAAAAANe/AAAAAAAAwL8AAAAAAADKvwAAAAAAQNW/AAAAAACA178AAAAAAIDFvwAAAAAAgMe/AAAAAABA1b8AAAAAAIDXvwAAAAAAAMK/AAAAAACAzL8AAAAAAMDWvwAAAAAAAMS/AAAAAACAxr8AAAAAAMDUvwAAAAAAQNe/AAAAAACAxb8AAAAAAADIvwAAAAAAAMG/AAAAAACAzb8AAAAAAMDWvwAAAAAAAMC/AAAAAACAzb8AAAAAAIDEvwAAAAAAgNC/AAAAAAAAyL8AAAAAAEDQvwAAAAAAgMW/AAAAAAAA0L8AAAAAAADFvwAAAAAAgM2/AAAAAAAAxL8AAAAAAADOvwAAAAAAgMS/AAAAAACAz78AAAAAAADHvwAAAAAAAMy/AAAAAAAA1b8AAAAAAIDHvwAAAAAAgM6/AAAAAADA1r8AAAAAAAC/vwAAAAAAgMq/AAAAAADA1r8AAAAAAEDVvwAAAAAAAL2/AAAAAACAy78AAAAAAIDXvwAAAAAAgMa/AAAAAACAzb8AAAAAAADFvwAAAAAAgM2/AAAAAACAw78AAAAAAADNvwAAAAAAgMO/AAAAAAAAzL8AAAAAAADDvwAAAAAAAMy/AAAAAAAAwL8AAAAAAIDBvwAAAAAAgM6/AAAAAACA1r8AAAAAAADBvwAAAAAAgMy/AAAAAACAwL8AAAAAAIDJvwAAAAAAQNW/AAAAAAAA1L8AAAAAAAC9vwAAAAAAgMu/AAAAAACAw78AAAAAAIDPvwAAAAAAgMW/AAAAAACAzr8AAAAAAADFvwAAAAAAAM6/AAAAAAAAxb8AAAAAAIDNvwAAAAAAAMS/AAAAAAAAzb8AAAAAAADCvwAAAAAAgMy/AAAAAACAxb8AAAAAAADLvwAAAAAAANW/AAAAAAAAx78AAAAAAIDOvwAAAAAAwNa/AAAAAACAwL8AAAAAAADFvwAAAAAAgNS/AAAAAAAAxb8AAAAAAIDNvwAAAAAAgMS/AAAAAACAzr8AAAAAAADGvwAAAAAAAM+/AAAAAACAxL8AAAAAAIDOvwAAAAAAAMW/AAAAAACAzb8AAAAAAADEvwAAAAAAAM2/AAAAAAAAwr8AAAAAAADOvwAAAAAAAMO/AAAAAACAzr8AAAAAAADFvwAAAAAAAMu/AAAAAACA1L8AAAAAAEDXvwAAAAAAgMS/AAAAAACAyL8AAAAAAADAvwAAAAAAAKS/AAAAAACAwL8AAAAAAADPvwAAAAAAANe/AAAAAACAwL8AAAAAAADKvwAAAAAAQNW/AAAAAADA178AAAAAAADHvwAAAAAAgMe/AAAAAACA1b8AAAAAAADYvwAAAAAAAMK/AAAAAACAzb8AAAAAAADXvwAAAAAAAMS/AAAAAACAx78AAAAAAIDVvwAAAAAAQNe/AAAAAACAxb8AAAAAAADJvwAAAAAAgMG/AAAAAACAzb8AAAAAAADXvwAAAAAAgMC/AAAAAACAzb8AAAAAAIDFvwAAAAAAgM+/AAAAAACAyL8AAAAAAMDQvwAAAAAAAMe/AAAAAACAz78AAAAAAIDFvwAAAAAAAM6/AAAAAAAAxb8AAAAAAIDNvwAAAAAAAMW/AAAAAAAAz78AAAAAAADHvwAAAAAAAMy/AAAAAABA1b8AAAAAAIDHvwAAAAAAAM6/AAAAAADA1r8AAAAAAAC+vwAAAAAAgMq/AAAAAABA1r8AAAAAAADVvwAAAAAAAL6/AAAAAAAAy78AAAAAAIDXvwAAAAAAAMe/AAAAAAAAzr8AAAAAAADFvwAAAAAAAM2/AAAAAAAAxL8AAAAAAADNvwAAAAAAgMK/AAAAAAAAzL8AAAAAAADDvwAAAAAAgMy/AAAAAAAAv78AAAAAAADCvwAAAAAAAM6/AAAAAADA1r8AAAAAAADBvwAAAAAAAMy/AAAAAAAAv78AAAAAAADKvwAAAAAAwNW/AAAAAADA1L8AAAAAAAC/vwAAAAAAgMu/AAAAAACAwr8AAAAAAIDOvwAAAAAAgMW/AAAAAAAAzr8AAAAAAIDDvwAAAAAAAM6/AAAAAAAAxL8AAAAAAADNvwAAAAAAAMO/AAAAAACAzL8AAAAAAIDBvwAAAAAAgMy/AAAAAAAAxb8AAAAAAADLvwAAAAAAwNS/AAAAAACAxr8AAAAAAIDNvwAAAAAAwNa/AAAAAACAwL8AAAAAAADGvwAAAAAAgNS/AAAAAACAxb8AAAAAAIDNvwAAAAAAAMW/AAAAAACAzr8AAAAAAADGvwAAAAAAAM+/AAAAAAAAxb8AAAAAAIDNvwAAAAAAAMW/AAAAAACAzb8AAAAAAIDDvwAAAAAAgMy/AAAAAACAwr8AAAAAAADOvwAAAAAAgMO/AAAAAAAAzr8AAAAAAIDEvwAAAAAAgMq/AAAAAADA1L8AAAAAAEDXvwAAAAAAgMS/AAAAAAAAx78AAAAAAADAvwAAAAAAgMy/AAAAAACAwb8AAAAAAIDMvwAAAAAAAMS/AAAAAAAAzL8AAAAAAADCvwAAAAAAgM2/AAAAAACAw78AAAAAAAC/vwAAAAAAAMy/AAAAAACA1b8AAAAAAEDXvwAAAAAAANa/AAAAAADA1b8AAAAAAAC+vwAAAAAAAMa/AAAAAABA1b8AAAAAAIDGvwAAAAAAAMK/AAAAAACAzb8AAAAAAIDGvwAAAAAAgM2/AAAAAAAAxL8AAAAAAIDOvwAAAAAAgMS/AAAAAAAAy78AAAAAAADVvwAAAAAAwNa/AAAAAAAAwb8AAAAAAADLvwAAAAAAgMO/AAAAAAAAzb8AAAAAAADWvwAAAAAAAMG/AAAAAACAzL8AAAAAAADBvwAAAAAAAM+/AAAAAACAyL8AAAAAAADNvwAAAAAAQNW/AAAAAACA1r8AAAAAAADBvwAAAAAAAMu/AAAAAACAw78AAAAAAIDNvwAAAAAAgNa/AAAAAAAAwb8AAAAAAIDMvwAAAAAAgMC/AAAAAAAAz78AAAAAAIDIvwAAAAAAgM2/AAAAAABA1r8AAAAAAEDXvwAAAAAAAMG/AAAAAACAy78AAAAAAADEvwAAAAAAgM2/AAAAAADA1r8AAAAAAIDCvwAAAAAAgM2/AAAAAAAAwr8AAAAAAADPvwAAAAAAgMi/AAAAAACAzb8AAAAAAEDWvwAAAAAAQNe/AAAAAACAwr8AAAAAAADMvwAAAAAAgMS/AAAAAACAzb8AAAAAAIDXvwAAAAAAgMK/AAAAAAAAzb8AAAAAAADDvwAAAAAAAM2/AAAAAACAxb8AAAAAAADNvwAAAAAAAMS/AAAAAAAA0L8AAAAAAADIvwAAAAAAwNC/AAAAAACAxr8AAAAAAIDNvwAAAAAAgNW/AAAAAACA178AAAAAAADCvwAAAAAAgM2/AAAAAACAxb8AAAAAAIDOvwAAAAAAQNe/AAAAAAAAwr8AAAAAAIDNvwAAAAAAAMK/AAAAAACAz78AAAAAAADJvwAAAAAAAM6/AAAAAABA1r8AAAAAAEDXvwAAAAAAgMK/AAAAAAAAzb8AAAAAAADEvwAAAAAAgM2/AAAAAACA178AAAAAAADCvwAAAAAAAM2/AAAAAACAwb8AAAAAAADPvwAAAAAAgMi/AAAAAAAAzr8AAAAAAEDWvwAAAAAAQNe/AAAAAACAwb8AAAAAAADNvwAAAAAAAMS/AAAAAACAzb8AAAAAAMDWvwAAAAAAgMK/AAAAAACAzb8AAAAAAADBvwAAAAAAgM6/AAAAAACAyL8AAAAAAADNvwAAAAAAQNa/AAAAAACA178AAAAAAADCvwAAAAAAgMy/AAAAAACAw78AAAAAAIDNvwAAAAAAANe/AAAAAAAAwr8AAAAAAIDMvwAAAAAAAMO/AAAAAAAAzb8AAAAAAIDFvwAAAAAAgMu/AAAAAAAAxL8AAAAAAIDPvwAAAAAAAMe/AAAAAAAA0L8AAAAAAADHvwAAAAAAAM2/AAAAAABA1b8AAAAAAEDXvwAAAAAAgMG/AAAAAAAAzb8AAAAAAADFvwAAAAAAgM2/AAAAAADA1r8AAAAAAADCvwAAAAAAAM2/AAAAAAAAwr8AAAAAAIDPvwAAAAAAgMm/AAAAAACAzb8AAAAAAEDWvwAAAAAAQNe/AAAAAACAwb8AAAAAAIDMvwAAAAAAgMS/AAAAAAAAzr8AAAAAAMDWvwAAAAAAgMK/AAAAAAAAzb8AAAAAAADCvwAAAAAAgM+/AAAAAAAAyb8AAAAAAADOvwAAAAAAgNa/AAAAAADA178AAAAAAIDCvwAAAAAAAM2/AAAAAACAw78AAAAAAADOvwAAAAAAwNa/AAAAAACAwr8AAAAAAADOvwAAAAAAgMK/AAAAAACAz78AAAAAAADJvwAAAAAAgM2/AAAAAACA1r8AAAAAAIDXvwAAAAAAAMO/AAAAAACAzb8AAAAAAADFvwAAAAAAgM2/AAAAAAAA178AAAAAAIDCvwAAAAAAgM2/AAAAAACAxL8AAAAAAADOvwAAAAAAgMW/AAAAAAAAzb8AAAAAAIDEvwAAAAAAgM+/AAAAAAAAyL8AAAAAAIDQvwAAAAAAgMe/AAAAAACAzb8AAAAAAIDVvwAAAAAAQNe/AAAAAAAAwr8AAAAAAIDNvwAAAAAAgMW/AAAAAACAzr8AAAAAAEDXvwAAAAAAgMK/AAAAAACAzb8AAAAAAADCvwAAAAAAANC/AAAAAACAyb8AAAAAAADOvwAAAAAAwNa/AAAAAADA178AAAAAAADCvwAAAAAAgMy/AAAAAACAw78AAAAAAIDOvwAAAAAAgNe/AAAAAAAAw78AAAAAAADNvwAAAAAAgMG/AAAAAAAAz78AAAAAAIDIvwAAAAAAgM2/AAAAAACA1r8AAAAAAMDXvwAAAAAAAMK/AAAAAAAAzb8AAAAAAADEvwAAAAAAgM2/AAAAAADA1r8AAAAAAADCvwAAAAAAgM2/AAAAAAAAwr8AAAAAAADPvwAAAAAAAMm/AAAAAACAzb8AAAAAAEDWvwAAAAAAgNe/AAAAAAAAw78AAAAAAADNvwAAAAAAgMS/AAAAAACAzb8AAAAAAMDXvwAAAAAAgMK/AAAAAAAAzb8AAAAAAADEvwAAAAAAgM2/AAAAAAAAxb8AAAAAAIDLvwAAAAAAgMa/AAAAAACAzL8AAAAAAEDWvwAAAAAAANi/AAAAAAAA2L8AAAAAAEDXvwAAAAAAgMi/AAAAAAAAzr8AAAAAAIDBvwAAAAAAgMu/AAAAAAAAuL8AAAAAAIDPvwAAAAAAAMK/AAAAAACAz78AAAAAAIDCvwAAAAAAAM2/AAAAAACAxb8AAAAAAACkvwAAAAAAgM6/AAAAAADA1r8AAAAAAMDWvwAAAAAAAL+/AAAAAACAx78AAAAAAIDVvwAAAAAAAMi/AAAAAAAAt78AAAAAAIDOvwAAAAAAgMa/AAAAAAAA0L8AAAAAAIDFvwAAAAAAgM2/AAAAAAAA178AAAAAAADDvwAAAAAAAMq/AAAAAABA1b8AAAAAAMDXvwAAAAAAgMS/AAAAAAAAyb8AAAAAAADCvwAAAAAAAL2/AAAAAAAAxL8AAAAAAMDQvwAAAAAAgNe/AAAAAACAwr8AAAAAAIDKvwAAAAAAgNW/AAAAAACA2L8AAAAAAADFvwAAAAAAAMq/AAAAAAAAxL8AAAAAAAC+vwAAAAAAAMS/AAAAAAAA0b8AAAAAAEDYvwAAAAAAAMS/AAAAAACAzL8AAAAAAIDWvwAAAAAAwNi/AAAAAACAxb8AAAAAAIDKvwAAAAAAgMS/AAAAAACAwL8AAAAAAIDFvwAAAAAAgNG/AAAAAABA2L8AAAAAAIDEvwAAAAAAAMy/AAAAAABA1r8AAAAAAADZvwAAAAAAAMa/AAAAAAAAy78AAAAAAIDDvwAAAAAAgM6/AAAAAACAxL8AAAAAAIDOvwAAAAAAgMS/AAAAAACAxL8AAAAAAMDRvwAAAAAAAMi/AAAAAAAA0L8AAAAAAEDYvwAAAAAAAMO/AAAAAAAAzL8AAAAAAIDWvwAAAAAAQNm/AAAAAACAx78AAAAAAADLvwAAAAAAgMS/AAAAAACAwL8AAAAAAIDFvwAAAAAAgNG/AAAAAACA2L8AAAAAAADFvwAAAAAAgMy/AAAAAAAA1r8AAAAAAEDZvwAAAAAAAMe/AAAAAACAy78AAAAAAADFvwAAAAAAAMK/AAAAAACAxb8AAAAAAEDRvwAAAAAAQNi/AAAAAAAAxb8AAAAAAIDMvwAAAAAAgNa/AAAAAABA2b8AAAAAAADIvwAAAAAAAMu/AAAAAACAxL8AAAAAAIDAvwAAAAAAgMW/AAAAAADA0b8AAAAAAMDYvwAAAAAAgMW/AAAAAACAzL8AAAAAAIDWvwAAAAAAANm/AAAAAACAx78AAAAAAIDLvwAAAAAAgMS/AAAAAABA0L8AAAAAAIDFvwAAAAAAgM6/AAAAAAAAxL8AAAAAAADFvwAAAAAAwNG/AAAAAAAAyb8AAAAAAIDQvwAAAAAAwNi/AAAAAAAAxL8AAAAAAADNvwAAAAAAwNa/AAAAAAAA2b8AAAAAAADHvwAAAAAAgMu/AAAAAACAxb8AAAAAAIDBvwAAAAAAgMW/AAAAAACA0b8AAAAAAMDYvwAAAAAAgMS/AAAAAAAAzb8AAAAAAMDWvwAAAAAAQNm/AAAAAAAAyL8AAAAAAADMvwAAAAAAAMW/AAAAAAAAwb8AAAAAAIDFvwAAAAAAwNG/AAAAAAAA2b8AAAAAAIDDvwAAAAAAgMy/AAAAAADA1r8AAAAAAADZvwAAAAAAAMi/AAAAAAAAzL8AAAAAAADFvwAAAAAAgMG/AAAAAACAxb8AAAAAAIDRvwAAAAAAwNi/AAAAAAAAxb8AAAAAAADNvwAAAAAAANe/AAAAAACA2b8AAAAAAADIvwAAAAAAAMu/AAAAAACAxL8AAAAAAADQvwAAAAAAAMW/AAAAAAAAz78AAAAAAADFvwAAAAAAAMW/AAAAAADA0b8AAAAAAIDIvwAAAAAAwNC/AAAAAADA2L8AAAAAAIDEvwAAAAAAgM2/AAAAAADA1r8AAAAAAMDYvwAAAAAAAMe/AAAAAAAAzL8AAAAAAADGvwAAAAAAAMK/AAAAAAAAxr8AAAAAAEDRvwAAAAAAANm/AAAAAAAAxL8AAAAAAADNvwAAAAAAwNa/AAAAAADA2b8AAAAAAIDIvwAAAAAAgMy/AAAAAACAxb8AAAAAAIDBvwAAAAAAgMW/AAAAAADA0b8AAAAAAADZvwAAAAAAAMW/AAAAAACAzb8AAAAAAMDWvwAAAAAAQNm/AAAAAACAx78AAAAAAIDMvwAAAAAAgMW/AAAAAAAAwr8AAAAAAADHvwAAAAAAANK/AAAAAADA2L8AAAAAAADEvwAAAAAAgM2/AAAAAADA1r8AAAAAAIDZvwAAAAAAAMi/AAAAAACAzL8AAAAAAIDEvwAAAAAAQNC/AAAAAACAxb8AAAAAAADPvwAAAAAAgMq/AAAAAAAA0b8AAAAAAADXvwAAAAAAQNi/AAAAAAAAyL8AAAAAAEDRvwAAAAAAgMi/AAAAAABA0L8AAAAAAADGvwAAAAAAQNG/AAAAAAAAyL8AAAAAAIDDvwAAAAAAgM+/AAAAAADA178AAAAAAIDCvwAAAAAAgM+/AAAAAAAA1r8AAAAAAEDYvwAAAAAAgMC/AAAAAAAAzr8AAAAAAMDWvwAAAAAAwNa/AAAAAACAwb8AAAAAAADPvwAAAAAAQNe/AAAAAACA1r8AAAAAAADBvwAAAAAAAM2/AAAAAADA1r8AAAAAAMDWvwAAAAAAgMS/AAAAAACAy78AAAAAAEDWvwAAAAAAgNi/AAAAAAAAv78AAAAAAADOvwAAAAAAQNe/AAAAAADA1r8AAAAAAADAvwAAAAAAAM2/AAAAAADA1r8AAAAAAIDWvwAAAAAAAL6/AAAAAACAzb8AAAAAAADXvwAAAAAAANe/AAAAAAAAwL8AAAAAAADNvwAAAAAAwNa/AAAAAACA1r8AAAAAAAC+vwAAAAAAAM6/AAAAAADA1r8AAAAAAMDWvwAAAAAAAMC/AAAAAAAAzr8AAAAAAMDWvwAAAAAAwNa/AAAAAACAwr8AAAAAAIDNvwAAAAAAQNe/AAAAAACA1r8AAAAAAIDHvwAAAAAAALe/AAAAAABA0L8AAAAAAADJvwAAAAAAALS/AAAAAACAz78AAAAAAIDXvwAAAAAAAMK/AAAAAACAzb8AAAAAAADGvwAAAAAAgM6/AAAAAADA178AAAAAAIDWvwAAAAAAgMK/AAAAAAAAzL8AAAAAAIDWvwAAAAAAQNi/AAAAAACAyL8AAAAAAADJvwAAAAAAwNa/AAAAAADA2L8AAAAAAIDDvwAAAAAAgM6/AAAAAADA178AAAAAAIDFvwAAAAAAAMm/AAAAAADA1b8AAAAAAEDYvwAAAAAAAMi/AAAAAAAAyr8AAAAAAIDBvwAAAAAAAM6/AAAAAABA178AAAAAAIDBvwAAAAAAAM+/AAAAAAAAxr8AAAAAAIDQvwAAAAAAAMi/AAAAAADA0L8AAAAAAIDHvwAAAAAAQNC/AAAAAACAxr8AAAAAAIDPvwAAAAAAgMW/AAAAAACAzr8AAAAAAADFvwAAAAAAAM+/AAAAAAAAyL8AAAAAAADNvwAAAAAAwNW/AAAAAAAAyL8AAAAAAIDPvwAAAAAAwNa/AAAAAAAAv78AAAAAAIDLvwAAAAAAwNa/AAAAAACA1b8AAAAAAAC+vwAAAAAAAMy/AAAAAACA178AAAAAAADHvwAAAAAAgM6/AAAAAACAxb8AAAAAAIDOvwAAAAAAgMS/AAAAAACAzb8AAAAAAADDvwAAAAAAgMy/AAAAAACAwr8AAAAAAADNvwAAAAAAgMC/AAAAAAAAw78AAAAAAADPvwAAAAAAgNa/AAAAAAAAwL8AAAAAAIDLvwAAAAAAAL+/AAAAAACAyr8AAAAAAADWvwAAAAAAANW/AAAAAAAAv78AAAAAAIDLvwAAAAAAAMO/AAAAAACAzr8AAAAAAIDGvwAAAAAAgM6/AAAAAAAAxb8AAAAAAADOvwAAAAAAAMO/AAAAAACAzL8AAAAAAADDvwAAAAAAgMy/AAAAAACAwr8AAAAAAIDNvwAAAAAAgMW/AAAAAAAAy78AAAAAAMDUvwAAAAAAgMa/AAAAAACAzb8AAAAAAMDWvwAAAAAAAMG/AAAAAAAAxr8AAAAAAMDUvwAAAAAAAMW/AAAAAAAAzb8AAAAAAADEvwAAAAAAgM6/AAAAAACAxr8AAAAAAIDOvwAAAAAAAMW/AAAAAACAzb8AAAAAAIDEvwAAAAAAgMy/AAAAAACAxL8AAAAAAADNvwAAAAAAgMO/AAAAAACAzb8AAAAAAADDvwAAAAAAgM2/AAAAAAAAw78AAAAAAADLvwAAAAAAgNS/AAAAAACA178AAAAAAADFvwAAAAAAgMe/AAAAAACAwL8AAAAAAACivwAAAAAAAMC/AAAAAAAAz78AAAAAAEDXvwAAAAAAgMG/AAAAAAAAyr8AAAAAAIDVvwAAAAAAgNe/AAAAAACAxb8AAAAAAIDHvwAAAAAAgNW/AAAAAADA178AAAAAAIDBvwAAAAAAAM2/AAAAAADA1r8AAAAAAADFvwAAAAAAAMe/AAAAAACA1b8AAAAAAIDXvwAAAAAAAMa/AAAAAACAyL8AAAAAAIDAvwAAAAAAgM2/AAAAAADA1r8AAAAAAADBvwAAAAAAAM6/AAAAAACAxb8AAAAAAADQvwAAAAAAAMe/AAAAAABA0L8AAAAAAIDFvwAAAAAAQNC/AAAAAACAxb8AAAAAAADPvwAAAAAAgMS/AAAAAACAzb8AAAAAAADDvwAAAAAAgM6/AAAAAACAxr8AAAAAAADNvwAAAAAAgNW/AAAAAAAAyL8AAAAAAIDOvwAAAAAAwNa/AAAAAAAAvb8AAAAAAIDLvwAAAAAAwNa/AAAAAADA1b8AAAAA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AIDMvwAAAAAAQNW/AAAAAAAAyL8AAAAAAIDOvwAAAAAAgNa/AAAAAAAAu78AAAAAAADLvwAAAAAAgNa/AAAAAACA1b8AAAAAAAC/vwAAAAAAgMu/AAAAAABA178AAAAAAIDGvwAAAAAAgM2/AAAAAACAxb8AAAAAAADOvwAAAAAAgMS/AAAAAAAAzb8AAAAAAIDDvwAAAAAAAMy/AAAAAAAAwr8AAAAAAADMvwAAAAAAAMG/AAAAAAAAwr8AAAAAAADOvwAAAAAAgNa/AAAAAAAAwL8AAAAAAADKvwAAAAAAAL+/AAAAAAAAyr8AAAAAAMDVvwAAAAAAANW/AAAAAAAAv78AAAAAAIDKvwAAAAAAAMK/AAAAAACAzb8AAAAAAADGvwAAAAAAgM6/AAAAAAAAxb8AAAAAAIDNvwAAAAAAAMO/AAAAAAAAzL8AAAAAAIDCvwAAAAAAgMy/AAAAAAAAwr8AAAAAAIDMvwAAAAAAgMW/AAAAAAAAy78AAAAAAIDUvwAAAAAAgMW/AAAAAACAzb8AAAAAAEDWvwAAAAAAAMG/AAAAAACAxb8AAAAAAEDUvwAAAAAAgMS/AAAAAAAAzb8AAAAAAADDvwAAAAAAgM6/AAAAAACAxr8AAAAAAADQvwAAAAAAgMS/AAAAAAAAzr8AAAAAAADDvwAAAAAAgMy/AAAAAACAwr8AAAAAAIDMvwAAAAAAgMK/AAAAAACAzb8AAAAAAIDCvwAAAAAAgM2/AAAAAACAwr8AAAAAAIDKvwAAAAAAgNS/AAAAAACA178AAAAAAIDEvwAAAAAAgMe/AAAAAAAAv78AAAAAAIDLvwAAAAAAAMG/AAAAAACAzb8AAAAAAADEvwAAAAAAgMy/AAAAAACAwb8AAAAAAIDNvwAAAAAAgMO/AAAAAAAAv78AAAAAAIDMvwAAAAAAQNa/AAAAAAAA2L8AAAAAAEDWvwAAAAAAANa/AAAAAAAAvr8AAAAAAIDGvwAAAAAAQNW/AAAAAAAAx78AAAAAAIDDvwAAAAAAgM2/AAAAAAAAxr8AAAAAAADNvwAAAAAAgMO/AAAAAACAzb8AAAAAAIDFvwAAAAAAgMy/AAAAAABA1b8AAAAAAADXvwAAAAAAAMG/AAAAAACAy78AAAAAAIDDvwAAAAAAAM2/AAAAAADA1r8AAAAAAADCvwAAAAAAAM2/AAAAAAAAwL8AAAAAAADOvwAAAAAAAMe/AAAAAAAAzb8AAAAAAADWvwAAAAAAANe/AAAAAAAAwb8AAAAAAIDLvwAAAAAAgMO/AAAAAAAAzb8AAAAAAEDXvwAAAAAAAMK/AAAAAAAAzb8AAAAAAADCvwAAAAAAgM6/AAAAAACAx78AAAAAAIDMvwAAAAAAANa/AAAAAAAA178AAAAAAADCvwAAAAAAgMy/AAAAAACAw78AAAAAAIDNvwAAAAAAgNa/AAAAAACAwb8AAAAAAADNvwAAAAAAgMG/AAAAAACAz78AAAAAAADIvwAAAAAAAM2/AAAAAABA1b8AAAAAAADXvwAAAAAAgMG/AAAAAACAzL8AAAAAAADEvwAAAAAAgM2/AAAAAACA1r8AAAAAAADCvwAAAAAAgMy/AAAAAAAAw78AAAAAAADNvwAAAAAAgMW/AAAAAACAzL8AAAAAAIDDvwAAAAAAgM6/AAAAAACAxr8AAAAAAADQvwAAAAAAgMa/AAAAAACAzb8AAAAAAIDVvwAAAAAAwNa/AAAAAAAAwr8AAAAAAADNvwAAAAAAAMS/AAAAAACAzb8AAAAAAADXvwAAAAAAgMK/AAAAAAAAzr8AAAAAAADBvwAAAAAAANC/AAAAAAAAyL8AAAAAAIDNvwAAAAAAQNa/AAAAAACA178AAAAAAADCvwAAAAAAAM2/AAAAAACAxL8AAAAAAADOvwAAAAAAQNe/AAAAAACAwr8AAAAAAIDNvwAAAAAAAMK/AAAAAACAz78AAAAAAIDIvwAAAAAAgM2/AAAAAAAA1r8AAAAAAEDXvwAAAAAAgMK/AAAAAAAAzb8AAAAAAIDEvwAAAAAAgM2/AAAAAAAA178AAAAAAIDCvwAAAAAAgM2/AAAAAAAAwr8AAAAAAADQvwAAAAAAgMi/AAAAAACAzb8AAAAAAADWvwAAAAAAQNe/AAAAAAAAwr8AAAAAAADNvwAAAAAAgMW/AAAAAACAzr8AAAAAAIDXvwAAAAAAAMK/AAAAAAAAzb8AAAAAAIDDvwAAAAAAgM2/AAAAAAAAxr8AAAAAAIDNvwAAAAAAgMS/AAAAAACAz78AAAAAAIDHvwAAAAAAANC/AAAAAACAxr8AAAAAAIDNvwAAAAAAwNW/AAAAAACA178AAAAAAADCvwAAAAAAgM2/AAAAAAAAxb8AAAAAAIDNvwAAAAAAgNe/AAAAAAAAw78AAAAAAIDOvwAAAAAAAMG/AAAAAACAz78AAAAAAADIvwAAAAAAgM2/AAAAAAAA1r8AAAAAAMDXvwAAAAAAgMK/AAAAAAAAzb8AAAAAAADEvwAAAAAAgM2/AAAAAADA1r8AAAAAAIDCvwAAAAAAgM2/AAAAAAAAw78AAAAAAIDPvwAAAAAAAMm/AAAAAACAzb8AAAAAAADWvwAAAAAAQNe/AAAAAAAAwr8AAAAAAIDNvwAAAAAAAMW/AAAAAACAzb8AAAAAAEDXvwAAAAAAAMK/AAAAAAAAzb8AAAAAAADCvwAAAAAAgM+/AAAAAAAAyb8AAAAAAIDNvwAAAAAAANa/AAAAAABA178AAAAAAIDBvwAAAAAAAM2/AAAAAACAxL8AAAAAAIDNvwAAAAAAwNa/AAAAAAAAwr8AAAAAAADMvwAAAAAAgMK/AAAAAACAzb8AAAAAAADGvwAAAAAAAM2/AAAAAAAAxb8AAAAAAADPvwAAAAAAgMa/AAAAAAAAz78AAAAAAIDGvwAAAAAAgM2/AAAAAADA1b8AAAAAAIDXvwAAAAAAAMK/AAAAAACAzL8AAAAAAIDEvwAAAAAAAM6/AAAAAADA1r8AAAAAAADDvwAAAAAAAM6/AAAAAAAAwr8AAAAAAADQvwAAAAAAgMe/AAAAAAAAzr8AAAAAAEDWvwAAAAAAwNe/AAAAAAAAwr8AAAAAAADNvwAAAAAAAMW/AAAAAACAzb8AAAAAAEDXvwAAAAAAgMK/AAAAAACAzb8AAAAAAADCvwAAAAAAANC/AAAAAACAyL8AAAAAAADNvwAAAAAAANa/AAAAAACA178AAAAAAADCvwAAAAAAgMy/AAAAAAAAxb8AAAAAAIDOvwAAAAAAwNa/AAAAAACAwr8AAAAAAADOvwAAAAAAAMK/AAAAAABA0L8AAAAAAIDJvwAAAAAAgM6/AAAAAABA1r8AAAAAAADXvwAAAAAAAMK/AAAAAAAAzb8AAAAAAADEvwAAAAAAgM6/AAAAAABA178AAAAAAIDCvwAAAAAAAM2/AAAAAACAw78AAAAAAIDNvwAAAAAAgMa/AAAAAAAAzb8AAAAAAIDIvwAAAAAAgMy/AAAAAABA1r8AAAAAAADYvwAAAAAAANi/AAAAAABA178AAAAAAADKvwAAAAAAgM+/AAAAAAAAwr8AAAAAAADLvwAAAAAAALm/AAAAAAAAz78AAAAAAIDCvwAAAAAAQNC/AAAAAAAAxb8AAAAAAIDNvwAAAAAAAMa/AAAAAAAAor8AAAAAAIDOvwAAAAAAQNa/AAAAAACA178AAAAAAIDAvwAAAAAAgMi/AAAAAAAA1r8AAAAAAADIvwAAAAAAALW/AAAAAACAzr8AAAAAAIDGvwAAAAAAgNC/AAAAAACAxr8AAAAAAADOvwAAAAAAwNa/AAAAAAAAwr8AAAAAAADKvwAAAAAAQNW/AAAAAADA178AAAAAAIDEvwAAAAAAgMm/AAAAAACAwr8AAAAAAAC9vwAAAAAAgMO/AAAAAACA0L8AAAAAAMDXvwAAAAAAgMO/AAAAAACAy78AAAAAAMDVvwAAAAAAwNi/AAAAAAAAxb8AAAAAAADKvwAAAAAAAMS/AAAAAACAwL8AAAAAAADFvwAAAAAAANG/AAAAAAAA2L8AAAAAAIDDvwAAAAAAgMu/AAAAAAAA1r8AAAAAAIDYvwAAAAAAgMW/AAAAAACAyr8AAAAAAIDEvwAAAAAAAMC/AAAAAAAAxb8AAAAAAEDRvwAAAAAAwNi/AAAAAAAAxL8AAAAAAIDMvwAAAAAAQNa/AAAAAAAA2b8AAAAAAADGvwAAAAAAAMu/AAAAAAAAxb8AAAAAAIDPvwAAAAAAgMW/AAAAAAAAzr8AAAAAAADEvwAAAAAAAMW/AAAAAACA0b8AAAAAAADJvwAAAAAAQNC/AAAAAADA2L8AAAAAAADEvwAAAAAAgMy/AAAAAABA1r8AAAAAAADZvwAAAAAAAMi/AAAAAACAy78AAAAAAIDFvwAAAAAAgMG/AAAAAAAAxb8AAAAAAEDRvwAAAAAAgNi/AAAAAAAAxL8AAAAAAADNvwAAAAAAwNa/AAAAAABA2b8AAAAAAIDHvwAAAAAAAMu/AAAAAAAAxb8AAAAAAADBvwAAAAAAgMW/AAAAAADA0b8AAAAAAMDYvwAAAAAAgMS/AAAAAACAzL8AAAAAAEDWvwAAAAAAQNm/AAAAAAAAx78AAAAAAIDLvwAAAAAAAMW/AAAAAACAwb8AAAAAAIDFvwAAAAAAgNG/AAAAAACA2L8AAAAAAADEvwAAAAAAAM2/AAAAAACA1r8AAAAAAIDZvwAAAAAAAMa/AAAAAACAyr8AAAAAAIDEvwAAAAAAANC/AAAAAACAxb8AAAAAAADPvwAAAAAAgMW/AAAAAAAAxb8AAAAAAMDRvwAAAAAAgMi/AAAAAADA0L8AAAAAAMDYvwAAAAAAgMS/AAAAAACAzb8AAAAAAMDWvwAAAAAAANm/AAAAAAAAyL8AAAAAAIDLvwAAAAAAAMW/AAAAAAAAwb8AAAAAAADGvwAAAAAAANK/AAAAAAAA2b8AAAAAAIDEvwAAAAAAAM2/AAAAAADA1r8AAAAAAIDZvwAAAAAAAMi/AAAAAAAAzb8AAAAAAIDFvwAAAAAAAMG/AAAAAACAxb8AAAAAAEDRvwAAAAAAwNi/AAAAAAAAxb8AAAAAAIDNvwAAAAAAANe/AAAAAAAA2b8AAAAAAADIvwAAAAAAAMy/AAAAAACAxb8AAAAAAIDBvwAAAAAAgMa/AAAAAACA0b8AAAAAAMDYvwAAAAAAgMS/AAAAAAAAzb8AAAAAAIDWvwAAAAAAQNm/AAAAAAAAx78AAAAAAIDMvwAAAAAAAMS/AAAAAAAA0L8AAAAAAIDFvwAAAAAAAM+/AAAAAAAAxb8AAAAAAIDFvwAAAAAAQNK/AAAAAAAAyb8AAAAAAEDQvwAAAAAAwNi/AAAAAAAAxL8AAAAAAIDNvwAAAAAAANe/AAAAAACA2b8AAAAAAADIvwAAAAAAAMy/AAAAAAAAxb8AAAAAAIDBvwAAAAAAAMa/AAAAAADA0b8AAAAAAADZvwAAAAAAgMW/AAAAAACAzb8AAAAAAMDWvwAAAAAAQNm/AAAAAAAAyL8AAAAAAADLvwAAAAAAgMa/AAAAAAAAwr8AAAAAAIDGvwAAAAAAgNG/AAAAAAAA2b8AAAAAAADEvwAAAAAAgM2/AAAAAADA1r8AAAAAAMDZvwAAAAAAAMi/AAAAAACAy78AAAAAAIDFvwAAAAAAAMG/AAAAAACAxr8AAAAAAADSvwAAAAAAQNm/AAAAAAAAxb8AAAAAAIDMvwAAAAAAwNa/AAAAAAAA2r8AAAAAAADIvwAAAAAAgMy/AAAAAACAxb8AAAAAAIDQvwAAAAAAAMa/AAAAAACAzr8AAAAAAADKvwAAAAAAQNC/AAAAAABA178AAAAAAIDYvwAAAAAAAMm/AAAAAACA0b8AAAAAAIDIvwAAAAAAANC/AAAAAACAxb8AAAAAAADRvwAAAAAAgMi/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AAAAAACAzL8AAAAAAEDVvwAAAAAAAMi/AAAAAACAz78AAAAAAMDWvwAAAAAAAL6/AAAAAACAyr8AAAAAAEDWvwAAAAAAQNW/AAAAAAAAv78AAAAAAADLvwAAAAAAgNe/AAAAAACAxr8AAAAAAIDNvwAAAAAAAMW/AAAAAACAzr8AAAAAAIDEvwAAAAAAgM2/AAAAAAAAxL8AAAAAAADNvwAAAAAAgMK/AAAAAACAy78AAAAAAAC/vwAAAAAAAMG/AAAAAACAzb8AAAAAAIDWvwAAAAAAgMC/AAAAAAAAy78AAAAAAAC/vwAAAAAAgMm/AAAAAAAA1b8AAAAAAEDUvwAAAAAAAL6/AAAAAAAAzL8AAAAAAIDCvwAAAAAAgM2/AAAAAAAAxb8AAAAAAIDOvwAAAAAAAMS/AAAAAAAAzr8AAAAAAADEvwAAAAAAgMy/AAAAAAAAwr8AAAAAAIDMvwAAAAAAgMG/AAAAAACAzL8AAAAAAADFvwAAAAAAgMu/AAAAAACA1L8AAAAAAIDFvwAAAAAAgMy/AAAAAABA1r8AAAAAAADAvwAAAAAAAMW/AAAAAABA1L8AAAAAAIDEvwAAAAAAAM2/AAAAAAAAw78AAAAAAIDNvwAAAAAAgMW/AAAAAACAzr8AAAAAAADFvwAAAAAAAM6/AAAAAAAAxL8AAAAAAADMvwAAAAAAAMK/AAAAAAAAzL8AAAAAAIDCvwAAAAAAgM2/AAAAAAAAw78AAAAAAIDNvwAAAAAAgMO/AAAAAAAAyr8AAAAAAIDUvwAAAAAAgNe/AAAAAACAxL8AAAAAAIDHvwAAAAAAgMC/AAAAAAAAzL8AAAAAAIDAvwAAAAAAgM2/AAAAAACAw78AAAAAAADMvwAAAAAAAMK/AAAAAACAzb8AAAAAAIDDvwAAAAAAAL2/AAAAAAAAy78AAAAAAADWvwAAAAAAwNe/AAAAAABA1r8AAAAAAMDVvwAAAAAAAL2/AAAAAACAxb8AAAAAAIDUvwAAAAAAgMa/AAAAAAAAwr8AAAAAAIDNvwAAAAAAgMa/AAAAAACAzb8AAAAAAIDCvwAAAAAAgM2/AAAAAAAAxL8AAAAAAADMvwAAAAAAANW/AAAAAABA178AAAAAAIDBvwAAAAAAgMu/AAAAAACAwr8AAAAAAIDLvwAAAAAAANa/AAAAAACAwL8AAAAA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AAAAAAAAzL8AAAAAAIDAvwAAAAAAgM6/AAAAAACAx78AAAAAAIDMvwAAAAAAQNW/AAAAAADA1r8AAAAAAIDAvwAAAAAAgMy/AAAAAACAw78AAAAAAIDNvwAAAAAAwNa/AAAAAAAAwb8AAAAAAIDMvwAAAAAAAMG/AAAAAACAzr8AAAAAAADJvwAAAAAAgM2/AAAAAADA1b8AAAAAAMDWvwAAAAAAAMG/AAAAAAAAzL8AAAAAAIDEvwAAAAAAgM2/AAAAAAAA178AAAAAAADCvwAAAAAAAM2/AAAAAACAwL8AAAAAAIDPvwAAAAAAAMi/AAAAAAAAzr8AAAAAAEDWvwAAAAAAwNe/AAAAAAAAwr8AAAAAAADNvwAAAAAAAMS/AAAAAACAzb8AAAAAAEDXvwAAAAAAAMK/AAAAAAAAzb8AAAAAAADDvwAAAAAAAM2/AAAAAAAAxb8AAAAAAADMvwAAAAAAgMO/AAAAAAAAz78AAAAAAADIvwAAAAAAANC/AAAAAACAxr8AAAAAAIDMvwAAAAAAQNW/AAAAAAAA178AAAAAAADCvwAAAAAAAM2/AAAAAAAAxb8AAAAAAIDNvwAAAAAAwNa/AAAAAACAwb8AAAAAAIDNvwAAAAAAAMK/AAAAAAAA0L8AAAAAAADJvwAAAAAAgM2/AAAAAABA1r8AAAAAAADXvwAAAAAAgMG/AAAAAAAAzb8AAAAAAIDEvwAAAAAAgM6/AAAAAACA178AAAAAAADCvwAAAAAAgM2/AAAAAAAAwr8AAAAAAIDPvwAAAAAAAMm/AAAAAACAzb8AAAAAAIDWvwAAAAAAgNe/AAAAAAAAwr8AAAAAAIDMvwAAAAAAAMW/AAAAAACAzb8AAAAAAIDXvwAAAAAAAMK/AAAAAACAzb8AAAAAAADBvwAAAAAAAM+/AAAAAAAAyL8AAAAAAIDNvwAAAAAAQNa/AAAAAACA178AAAAAAADBvwAAAAAAgMy/AAAAAACAxL8AAAAAAIDNvwAAAAAAwNa/AAAAAAAAwr8AAAAAAIDNvwAAAAAAgMO/AAAAAACAzb8AAAAAAIDFvwAAAAAAgMy/AAAAAAAAxb8AAAAAAADQvwAAAAAAgMi/AAAAAABA0L8AAAAAAIDGvwAAAAAAgM2/AAAAAACA1b8AAAAAAEDXvwAAAAAAAMK/AAAAAACAzb8AAAAA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"},"shape":[5000],"dtype":"float64","order":"little"}]]}}},"view":{"type":"object","name":"CDSView","id":"530eb368-4e4a-4829-91ad-a848030c7a9f","attributes":{"filter":{"type":"object","name":"AllIndices","id":"429256ed-220e-43d9-81fc-62223b685330"}}},"glyph":{"type":"object","name":"Line","id":"132950ce-e709-45f0-8e3c-fcceb90e4928","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"x"},"y":{"type":"field","field":"y"},"line_color":"#30a2da","line_width":2}},"selection_glyph":{"type":"object","name":"Line","id":"c3a52a41-8139-43e3-84e5-ab7318a9eaef","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"x"},"y":{"type":"field","field":"y"},"line_color":"#30a2da","line_width":2}},"nonselection_glyph":{"type":"object","name":"Line","id":"22abc792-02f8-4ca1-b53c-86985b2721fb","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"x"},"y":{"type":"field","field":"y"},"line_color":"#30a2da","line_alpha":0.1,"line_width":2}},"muted_glyph":{"type":"object","name":"Line","id":"05e8da9e-b56f-4a19-a576-21a95dded281","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"x"},"y":{"type":"field","field":"y"},"line_color":"#30a2da","line_alpha":0.2,"line_width":2}}}}],"toolbar":{"type":"object","name":"Toolbar","id":"0a9e487f-f900-4800-be44-ff5239bb6e5e","attributes":{"tools":[{"type":"object","name":"WheelZoomTool","id":"ce8b5e52-4ba3-4a8d-a666-05563515df8e","attributes":{"tags":["hv_created"],"renderers":"auto","zoom_together":"none"}},{"type":"object","name":"HoverTool","id":"493fe415-4775-4d7d-a432-b31bb99575b2","attributes":{"tags":["hv_created"],"renderers":[{"id":"f1cb5d7b-f6f6-44e9-8d22-c1ed9d49a30a"}],"tooltips":[["x","@{x}"],["y","@{y}"]]}},{"type":"object","name":"SaveTool","id":"bfa6c627-7c88-4d42-8d4f-1ddab8b2d113"},{"type":"object","name":"PanTool","id":"3f5aabb0-8e3d-4b4f-b78e-17e3021eecfa"},{"type":"object","name":"BoxZoomTool","id":"e1ab79a6-b52e-4d41-8997-5698f58cc547","attributes":{"overlay":{"type":"object","name":"BoxAnnotation","id":"909e26d8-2da5-4077-aab2-ff049db36649","attributes":{"syncable":false,"line_color":"black","line_alpha":1.0,"line_width":2,"line_dash":[4,4],"fill_color":"lightgrey","fill_alpha":0.5,"level":"overlay","visible":false,"left":{"type":"number","value":"nan"},"right":{"type":"number","value":"nan"},"top":{"type":"number","value":"nan"},"bottom":{"type":"number","value":"nan"},"left_units":"canvas","right_units":"canvas","top_units":"canvas","bottom_units":"canvas","handles":{"type":"object","name":"BoxInteractionHandles","id":"1768279e-859d-4ea2-a183-f14c37ddebbe","attributes":{"all":{"type":"object","name":"AreaVisuals","id":"6cbf7857-3940-4804-bb7e-7a1bcb072370","attributes":{"fill_color":"white","hover_fill_color":"lightgray"}}}}}}}},{"type":"object","name":"ResetTool","id":"34872618-29d7-4411-9039-32da40bddf7f"}],"active_drag":{"id":"e1ab79a6-b52e-4d41-8997-5698f58cc547"}}},"left":[{"type":"object","name":"LinearAxis","id":"fe954855-7db7-40ff-abb2-cef59a48601c","attributes":{"ticker":{"type":"object","name":"BasicTicker","id":"2491f5a4-14b1-49cd-b27c-96d3a7a13445","attributes":{"mantissas":[1,2,5]}},"formatter":{"type":"object","name":"BasicTickFormatter","id":"a4c0eaf9-89a5-4511-904c-ad9673ea83ca"},"axis_label":"y","major_label_policy":{"type":"object","name":"AllLabels","id":"90fe59a3-c5de-4b04-a011-bf243e8b6d21"}}}],"below":[{"type":"object","name":"LinearAxis","id":"9f7728e1-996f-4599-b144-e2cdd5124873","attributes":{"ticker":{"type":"object","name":"BasicTicker","id":"d4f6fc9e-b973-4ebd-a8a0-0ae752603429","attributes":{"mantissas":[1,2,5]}},"formatter":{"type":"object","name":"BasicTickFormatter","id":"c59d982d-18fe-4d11-ac81-7ccb3e11bec5"},"axis_label":"x","major_label_policy":{"type":"object","name":"AllLabels","id":"182f3fe8-64f3-4af7-8a9a-9d961909040e"}}}],"center":[{"type":"object","name":"Grid","id":"80dc23a8-27d7-4ee7-927d-2ef75178c949","attributes":{"axis":{"id":"9f7728e1-996f-4599-b144-e2cdd5124873"},"grid_line_color":null}},{"type":"object","name":"Grid","id":"0454d756-3f8c-4257-9b8e-c917b9d96f64","attributes":{"dimension":1,"axis":{"id":"fe954855-7db7-40ff-abb2-cef59a48601c"},"grid_line_color":null}}],"min_border_top":10,"min_border_bottom":10,"min_border_left":10,"min_border_right":10,"output_backend":"webgl"}},{"type":"object","name":"Spacer","id":"4a824fd0-c4fb-4619-958f-240ad1a77593","attributes":{"name":"HSpacer00271","stylesheets":["\n:host(.pn-loading):before, .pn-loading:before {\n  background-color: #c3c3c3;\n  mask-size: auto calc(min(50%, 400px));\n  -webkit-mask-size: auto calc(min(50%, 400px));\n}",{"id":"80d120fc-7bee-49c6-9c85-520aafe73b08"},{"id":"bfd7d645-80e0-46ba-9d4b-3bafc04dd6e6"},{"id":"bb561f1c-3490-4e30-8893-f496cdff403e"}],"margin":0,"sizing_mode":"stretch_width","align":"start"}}]}}],"defs":[{"type":"model","name":"ReactiveHTML1"},{"type":"model","name":"FlexBox1","properties":[{"name":"align_content","kind":"Any","default":"flex-start"},{"name":"align_items","kind":"Any","default":"flex-start"},{"name":"flex_direction","kind":"Any","default":"row"},{"name":"flex_wrap","kind":"Any","default":"wrap"},{"name":"gap","kind":"Any","default":""},{"name":"justify_content","kind":"Any","default":"flex-start"}]},{"type":"model","name":"FloatPanel1","properties":[{"name":"config","kind":"Any","default":{"type":"map"}},{"name":"contained","kind":"Any","default":true},{"name":"position","kind":"Any","default":"right-top"},{"name":"offsetx","kind":"Any","default":null},{"name":"offsety","kind":"Any","default":null},{"name":"theme","kind":"Any","default":"primary"},{"name":"status","kind":"Any","default":"normalized"}]},{"type":"model","name":"GridStack1","properties":[{"name":"mode","kind":"Any","default":"warn"},{"name":"ncols","kind":"Any","default":null},{"name":"nrows","kind":"Any","default":null},{"name":"allow_resize","kind":"Any","default":true},{"name":"allow_drag","kind":"Any","default":true},{"name":"state","kind":"Any","default":[]}]},{"type":"model","name":"drag1","properties":[{"name":"slider_width","kind":"Any","default":5},{"name":"slider_color","kind":"Any","default":"black"},{"name":"value","kind":"Any","default":50}]},{"type":"model","name":"click1","properties":[{"name":"terminal_output","kind":"Any","default":""},{"name":"debug_name","kind":"Any","default":""},{"name":"clears","kind":"Any","default":0}]},{"type":"model","name":"FastWrapper1","properties":[{"name":"object","kind":"Any","default":null},{"name":"style","kind":"Any","default":null}]},{"type":"model","name":"NotificationAreaBase1","properties":[{"name":"js_events","kind":"Any","default":{"type":"map"}},{"name":"position","kind":"Any","default":"bottom-right"},{"name":"_clear","kind":"Any","default":0}]},{"type":"model","name":"NotificationArea1","properties":[{"name":"js_events","kind":"Any","default":{"type":"map"}},{"name":"notifications","kind":"Any","default":[]},{"name":"position","kind":"Any","default":"bottom-right"},{"name":"_clear","kind":"Any","default":0},{"name":"types","kind":"Any","default":[{"type":"map","entries":[["type","warning"],["background","#ffc107"],["icon",{"type":"map","entries":[["className","fas fa-exclamation-triangle"],["tagName","i"],["color","white"]]}]]},{"type":"map","entries":[["type","info"],["background","#007bff"],["icon",{"type":"map","entries":[["className","fas fa-info-circle"],["tagName","i"],["color","white"]]}]]}]}]},{"type":"model","name":"Notification","properties":[{"name":"background","kind":"Any","default":null},{"name":"duration","kind":"Any","default":3000},{"name":"icon","kind":"Any","default":null},{"name":"message","kind":"Any","default":""},{"name":"notification_type","kind":"Any","default":null},{"name":"_destroyed","kind":"Any","default":false}]},{"type":"model","name":"TemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"BootstrapTemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"TemplateEditor1","properties":[{"name":"layout","kind":"Any","default":[]}]},{"type":"model","name":"MaterialTemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"ReactiveESM1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"JSComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"ReactComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"AnyWidgetComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"request_value1","properties":[{"name":"fill","kind":"Any","default":"none"},{"name":"_synced","kind":"Any","default":null},{"name":"_request_sync","kind":"Any","default":0}]}]}};
      var render_items = [{"docid":"1c2e8247-a674-47e1-a918-111b33e8fefa","roots":{"fa2ca670-4426-466d-beb8-b7990e9967af":"d8cda1f2-d3f1-4a05-a96f-3dd3f4496ab6"},"root_ids":["fa2ca670-4426-466d-beb8-b7990e9967af"]}];
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



You probably can’t even pick out the different AES rounds anymore
(whereas it was pretty obvious on TINYAES128C). MBED is also way faster
- we only got part way into round 2 with 5000 samples of TINYAES, but
with MBED we can finish the entire encryption in less than 5000 samples!
Two questions we need to answer now are:

1. Is it possible for us to break this AES implementation?
2. If so, what sort of leakage model do we need?

As it turns out, the answers are:

1. Yes!
2. We can continue to use the same leakage model - the SBox output

This might come as a surprise, but it’s true! Two of the t_table lookups
are just the sbox[key^plaintext] that we used before. Try the analysis
for yourself now and verify that this is correct:


**In [5]:**

.. code:: ipython3

    import chipwhisperer.analyzer as cwa
    #pick right leakage model for your attack
    leak_model = cwa.leakage_models.sbox_output
    attack = cwa.cpa(project, leak_model)
    results = attack.run(cwa.get_jupyter_callback(attack))


**Out [5]:**


.. raw:: html

    <div class="data_html">
        <style type="text/css">
    #T_7b5e6_row1_col0, #T_7b5e6_row1_col1, #T_7b5e6_row1_col2, #T_7b5e6_row1_col3, #T_7b5e6_row1_col4, #T_7b5e6_row1_col5, #T_7b5e6_row1_col6, #T_7b5e6_row1_col7, #T_7b5e6_row1_col8, #T_7b5e6_row1_col9, #T_7b5e6_row1_col10, #T_7b5e6_row1_col11, #T_7b5e6_row1_col12, #T_7b5e6_row1_col13, #T_7b5e6_row1_col14, #T_7b5e6_row1_col15 {
      color: red;
    }
    </style>
    <table id="T_7b5e6">
      <caption>Finished traces 75 to 100</caption>
      <thead>
        <tr>
          <th class="blank level0" >&nbsp;</th>
          <th id="T_7b5e6_level0_col0" class="col_heading level0 col0" >0</th>
          <th id="T_7b5e6_level0_col1" class="col_heading level0 col1" >1</th>
          <th id="T_7b5e6_level0_col2" class="col_heading level0 col2" >2</th>
          <th id="T_7b5e6_level0_col3" class="col_heading level0 col3" >3</th>
          <th id="T_7b5e6_level0_col4" class="col_heading level0 col4" >4</th>
          <th id="T_7b5e6_level0_col5" class="col_heading level0 col5" >5</th>
          <th id="T_7b5e6_level0_col6" class="col_heading level0 col6" >6</th>
          <th id="T_7b5e6_level0_col7" class="col_heading level0 col7" >7</th>
          <th id="T_7b5e6_level0_col8" class="col_heading level0 col8" >8</th>
          <th id="T_7b5e6_level0_col9" class="col_heading level0 col9" >9</th>
          <th id="T_7b5e6_level0_col10" class="col_heading level0 col10" >10</th>
          <th id="T_7b5e6_level0_col11" class="col_heading level0 col11" >11</th>
          <th id="T_7b5e6_level0_col12" class="col_heading level0 col12" >12</th>
          <th id="T_7b5e6_level0_col13" class="col_heading level0 col13" >13</th>
          <th id="T_7b5e6_level0_col14" class="col_heading level0 col14" >14</th>
          <th id="T_7b5e6_level0_col15" class="col_heading level0 col15" >15</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th id="T_7b5e6_level0_row0" class="row_heading level0 row0" >PGE=</th>
          <td id="T_7b5e6_row0_col0" class="data row0 col0" >0</td>
          <td id="T_7b5e6_row0_col1" class="data row0 col1" >0</td>
          <td id="T_7b5e6_row0_col2" class="data row0 col2" >0</td>
          <td id="T_7b5e6_row0_col3" class="data row0 col3" >0</td>
          <td id="T_7b5e6_row0_col4" class="data row0 col4" >0</td>
          <td id="T_7b5e6_row0_col5" class="data row0 col5" >0</td>
          <td id="T_7b5e6_row0_col6" class="data row0 col6" >0</td>
          <td id="T_7b5e6_row0_col7" class="data row0 col7" >0</td>
          <td id="T_7b5e6_row0_col8" class="data row0 col8" >0</td>
          <td id="T_7b5e6_row0_col9" class="data row0 col9" >0</td>
          <td id="T_7b5e6_row0_col10" class="data row0 col10" >0</td>
          <td id="T_7b5e6_row0_col11" class="data row0 col11" >0</td>
          <td id="T_7b5e6_row0_col12" class="data row0 col12" >0</td>
          <td id="T_7b5e6_row0_col13" class="data row0 col13" >0</td>
          <td id="T_7b5e6_row0_col14" class="data row0 col14" >0</td>
          <td id="T_7b5e6_row0_col15" class="data row0 col15" >0</td>
        </tr>
        <tr>
          <th id="T_7b5e6_level0_row1" class="row_heading level0 row1" >0</th>
          <td id="T_7b5e6_row1_col0" class="data row1 col0" >2B<br>0.719</td>
          <td id="T_7b5e6_row1_col1" class="data row1 col1" >7E<br>0.610</td>
          <td id="T_7b5e6_row1_col2" class="data row1 col2" >15<br>0.716</td>
          <td id="T_7b5e6_row1_col3" class="data row1 col3" >16<br>0.588</td>
          <td id="T_7b5e6_row1_col4" class="data row1 col4" >28<br>0.701</td>
          <td id="T_7b5e6_row1_col5" class="data row1 col5" >AE<br>0.581</td>
          <td id="T_7b5e6_row1_col6" class="data row1 col6" >D2<br>0.729</td>
          <td id="T_7b5e6_row1_col7" class="data row1 col7" >A6<br>0.656</td>
          <td id="T_7b5e6_row1_col8" class="data row1 col8" >AB<br>0.631</td>
          <td id="T_7b5e6_row1_col9" class="data row1 col9" >F7<br>0.664</td>
          <td id="T_7b5e6_row1_col10" class="data row1 col10" >15<br>0.684</td>
          <td id="T_7b5e6_row1_col11" class="data row1 col11" >88<br>0.664</td>
          <td id="T_7b5e6_row1_col12" class="data row1 col12" >09<br>0.603</td>
          <td id="T_7b5e6_row1_col13" class="data row1 col13" >CF<br>0.719</td>
          <td id="T_7b5e6_row1_col14" class="data row1 col14" >4F<br>0.528</td>
          <td id="T_7b5e6_row1_col15" class="data row1 col15" >3C<br>0.524</td>
        </tr>
        <tr>
          <th id="T_7b5e6_level0_row2" class="row_heading level0 row2" >1</th>
          <td id="T_7b5e6_row2_col0" class="data row2 col0" >AB<br>0.456</td>
          <td id="T_7b5e6_row2_col1" class="data row2 col1" >1C<br>0.468</td>
          <td id="T_7b5e6_row2_col2" class="data row2 col2" >2F<br>0.505</td>
          <td id="T_7b5e6_row2_col3" class="data row2 col3" >09<br>0.489</td>
          <td id="T_7b5e6_row2_col4" class="data row2 col4" >D8<br>0.507</td>
          <td id="T_7b5e6_row2_col5" class="data row2 col5" >C8<br>0.484</td>
          <td id="T_7b5e6_row2_col6" class="data row2 col6" >5C<br>0.488</td>
          <td id="T_7b5e6_row2_col7" class="data row2 col7" >95<br>0.480</td>
          <td id="T_7b5e6_row2_col8" class="data row2 col8" >53<br>0.464</td>
          <td id="T_7b5e6_row2_col9" class="data row2 col9" >94<br>0.461</td>
          <td id="T_7b5e6_row2_col10" class="data row2 col10" >2E<br>0.473</td>
          <td id="T_7b5e6_row2_col11" class="data row2 col11" >B0<br>0.466</td>
          <td id="T_7b5e6_row2_col12" class="data row2 col12" >DE<br>0.463</td>
          <td id="T_7b5e6_row2_col13" class="data row2 col13" >71<br>0.470</td>
          <td id="T_7b5e6_row2_col14" class="data row2 col14" >C0<br>0.471</td>
          <td id="T_7b5e6_row2_col15" class="data row2 col15" >70<br>0.484</td>
        </tr>
        <tr>
          <th id="T_7b5e6_level0_row3" class="row_heading level0 row3" >2</th>
          <td id="T_7b5e6_row3_col0" class="data row3 col0" >C0<br>0.455</td>
          <td id="T_7b5e6_row3_col1" class="data row3 col1" >71<br>0.451</td>
          <td id="T_7b5e6_row3_col2" class="data row3 col2" >89<br>0.493</td>
          <td id="T_7b5e6_row3_col3" class="data row3 col3" >D5<br>0.463</td>
          <td id="T_7b5e6_row3_col4" class="data row3 col4" >18<br>0.461</td>
          <td id="T_7b5e6_row3_col5" class="data row3 col5" >35<br>0.471</td>
          <td id="T_7b5e6_row3_col6" class="data row3 col6" >70<br>0.482</td>
          <td id="T_7b5e6_row3_col7" class="data row3 col7" >11<br>0.479</td>
          <td id="T_7b5e6_row3_col8" class="data row3 col8" >41<br>0.450</td>
          <td id="T_7b5e6_row3_col9" class="data row3 col9" >57<br>0.459</td>
          <td id="T_7b5e6_row3_col10" class="data row3 col10" >EC<br>0.461</td>
          <td id="T_7b5e6_row3_col11" class="data row3 col11" >30<br>0.459</td>
          <td id="T_7b5e6_row3_col12" class="data row3 col12" >3E<br>0.453</td>
          <td id="T_7b5e6_row3_col13" class="data row3 col13" >28<br>0.469</td>
          <td id="T_7b5e6_row3_col14" class="data row3 col14" >06<br>0.463</td>
          <td id="T_7b5e6_row3_col15" class="data row3 col15" >98<br>0.453</td>
        </tr>
        <tr>
          <th id="T_7b5e6_level0_row4" class="row_heading level0 row4" >3</th>
          <td id="T_7b5e6_row4_col0" class="data row4 col0" >71<br>0.451</td>
          <td id="T_7b5e6_row4_col1" class="data row4 col1" >BB<br>0.451</td>
          <td id="T_7b5e6_row4_col2" class="data row4 col2" >E3<br>0.472</td>
          <td id="T_7b5e6_row4_col3" class="data row4 col3" >81<br>0.462</td>
          <td id="T_7b5e6_row4_col4" class="data row4 col4" >85<br>0.440</td>
          <td id="T_7b5e6_row4_col5" class="data row4 col5" >B3<br>0.463</td>
          <td id="T_7b5e6_row4_col6" class="data row4 col6" >95<br>0.452</td>
          <td id="T_7b5e6_row4_col7" class="data row4 col7" >8C<br>0.468</td>
          <td id="T_7b5e6_row4_col8" class="data row4 col8" >14<br>0.443</td>
          <td id="T_7b5e6_row4_col9" class="data row4 col9" >C4<br>0.452</td>
          <td id="T_7b5e6_row4_col10" class="data row4 col10" >A6<br>0.460</td>
          <td id="T_7b5e6_row4_col11" class="data row4 col11" >87<br>0.454</td>
          <td id="T_7b5e6_row4_col12" class="data row4 col12" >22<br>0.452</td>
          <td id="T_7b5e6_row4_col13" class="data row4 col13" >8F<br>0.464</td>
          <td id="T_7b5e6_row4_col14" class="data row4 col14" >EE<br>0.459</td>
          <td id="T_7b5e6_row4_col15" class="data row4 col15" >3F<br>0.452</td>
        </tr>
        <tr>
          <th id="T_7b5e6_level0_row5" class="row_heading level0 row5" >4</th>
          <td id="T_7b5e6_row5_col0" class="data row5 col0" >C1<br>0.449</td>
          <td id="T_7b5e6_row5_col1" class="data row5 col1" >A2<br>0.448</td>
          <td id="T_7b5e6_row5_col2" class="data row5 col2" >0C<br>0.470</td>
          <td id="T_7b5e6_row5_col3" class="data row5 col3" >EE<br>0.460</td>
          <td id="T_7b5e6_row5_col4" class="data row5 col4" >89<br>0.437</td>
          <td id="T_7b5e6_row5_col5" class="data row5 col5" >0F<br>0.461</td>
          <td id="T_7b5e6_row5_col6" class="data row5 col6" >4A<br>0.441</td>
          <td id="T_7b5e6_row5_col7" class="data row5 col7" >B5<br>0.466</td>
          <td id="T_7b5e6_row5_col8" class="data row5 col8" >C6<br>0.431</td>
          <td id="T_7b5e6_row5_col9" class="data row5 col9" >69<br>0.451</td>
          <td id="T_7b5e6_row5_col10" class="data row5 col10" >11<br>0.457</td>
          <td id="T_7b5e6_row5_col11" class="data row5 col11" >75<br>0.448</td>
          <td id="T_7b5e6_row5_col12" class="data row5 col12" >21<br>0.447</td>
          <td id="T_7b5e6_row5_col13" class="data row5 col13" >A5<br>0.463</td>
          <td id="T_7b5e6_row5_col14" class="data row5 col14" >E6<br>0.452</td>
          <td id="T_7b5e6_row5_col15" class="data row5 col15" >F3<br>0.450</td>
        </tr>
      </tbody>
    </table>

    </div>


Improving the Model
-------------------

While this model works alright for mbedtls, you probably wouldn’t be
surprised if it wasn’t the best model to attack with. Instead, we can
attack the full T-Tables. Returning again to the T-Tables:

:math:`T _ { 0 } [ a ] = \left[ \begin{array} { l l } { 02 \times \operatorname { sbox } [ a ] } \\ { 01 \times \operatorname { sbox } [ a ] } \\ { 01 \times \operatorname { sbox } [ a ] } \\ { 03 \times \operatorname { sbox } [ a ] } \end{array} \right]`

:math:`T _ { 1 } [ a ] = \left[ \begin{array} { l } { 03 \times \operatorname { sbox } [ a ] } \\ { 02 \times \operatorname { sbox } [ a ] } \\ { 01 \times \operatorname { sbox } [ a ] } \\ { 01 \times \operatorname { sbox } [ a ] } \end{array} \right]`

:math:`T _ { 2 } [ a ] = \left[ \begin{array} { l l } { 01 \times \operatorname { sbox } [ a ] } \\ { 03 \times \operatorname { sbox } [ a ] } \\ { 02 \times \operatorname { sbox } [ a ] } \\ { 01 \times \operatorname { sbox } [ a ] } \end{array} \right]`

:math:`T _ { 3 } [ a ] = \left[ \begin{array} { l l } { 01 \times \operatorname { sbox } [ a ] } \\ { 01 \times \operatorname { sbox } [ a ] } \\ { 03 \times \operatorname { sbox } [ a ] } \\ { 02 \times \operatorname { sbox } [ a ] } \end{array} \right]`

we can see that for each T-Table lookup, the following is accessed:

:math:`\operatorname {sbox}[a]`, :math:`\operatorname {sbox}[a]`,
:math:`2 \times \operatorname {sbox}[a]`,
:math:`3 \times \operatorname {sbox}[a]`

so instead of just taking the Hamming weight of the SBox, we can instead
take the Hamming weight of this whole access:

:math:`h = \operatorname {hw}[\operatorname {sbox}[a]] + \operatorname {hw}[\operatorname {sbox}[a]] + \operatorname {hw}[2 \times \operatorname {sbox}[a]] + \operatorname {hw}[3 \times \operatorname {sbox}[a]]`

Again, ChipWhisperer already has this model built in, which you can
access with ``cwa.leakage_models.t_table``. Retry your CPA attack with
this new leakage model:


**In [6]:**

.. code:: ipython3

    import chipwhisperer.analyzer as cwa
    #pick right leakage model for your attack
    leak_model = cwa.leakage_models.t_table
    attack = cwa.cpa(project, leak_model)
    results = attack.run(cwa.get_jupyter_callback(attack))


**Out [6]:**


.. raw:: html

    <div class="data_html">
        <style type="text/css">
    #T_21ea5_row1_col0, #T_21ea5_row1_col1, #T_21ea5_row1_col2, #T_21ea5_row1_col3, #T_21ea5_row1_col4, #T_21ea5_row1_col6, #T_21ea5_row1_col7, #T_21ea5_row1_col8, #T_21ea5_row1_col9, #T_21ea5_row1_col10, #T_21ea5_row1_col11, #T_21ea5_row1_col12, #T_21ea5_row1_col13, #T_21ea5_row1_col14 {
      color: red;
    }
    </style>
    <table id="T_21ea5">
      <caption>Finished traces 75 to 100</caption>
      <thead>
        <tr>
          <th class="blank level0" >&nbsp;</th>
          <th id="T_21ea5_level0_col0" class="col_heading level0 col0" >0</th>
          <th id="T_21ea5_level0_col1" class="col_heading level0 col1" >1</th>
          <th id="T_21ea5_level0_col2" class="col_heading level0 col2" >2</th>
          <th id="T_21ea5_level0_col3" class="col_heading level0 col3" >3</th>
          <th id="T_21ea5_level0_col4" class="col_heading level0 col4" >4</th>
          <th id="T_21ea5_level0_col5" class="col_heading level0 col5" >5</th>
          <th id="T_21ea5_level0_col6" class="col_heading level0 col6" >6</th>
          <th id="T_21ea5_level0_col7" class="col_heading level0 col7" >7</th>
          <th id="T_21ea5_level0_col8" class="col_heading level0 col8" >8</th>
          <th id="T_21ea5_level0_col9" class="col_heading level0 col9" >9</th>
          <th id="T_21ea5_level0_col10" class="col_heading level0 col10" >10</th>
          <th id="T_21ea5_level0_col11" class="col_heading level0 col11" >11</th>
          <th id="T_21ea5_level0_col12" class="col_heading level0 col12" >12</th>
          <th id="T_21ea5_level0_col13" class="col_heading level0 col13" >13</th>
          <th id="T_21ea5_level0_col14" class="col_heading level0 col14" >14</th>
          <th id="T_21ea5_level0_col15" class="col_heading level0 col15" >15</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th id="T_21ea5_level0_row0" class="row_heading level0 row0" >PGE=</th>
          <td id="T_21ea5_row0_col0" class="data row0 col0" >0</td>
          <td id="T_21ea5_row0_col1" class="data row0 col1" >0</td>
          <td id="T_21ea5_row0_col2" class="data row0 col2" >0</td>
          <td id="T_21ea5_row0_col3" class="data row0 col3" >0</td>
          <td id="T_21ea5_row0_col4" class="data row0 col4" >0</td>
          <td id="T_21ea5_row0_col5" class="data row0 col5" >5</td>
          <td id="T_21ea5_row0_col6" class="data row0 col6" >0</td>
          <td id="T_21ea5_row0_col7" class="data row0 col7" >0</td>
          <td id="T_21ea5_row0_col8" class="data row0 col8" >0</td>
          <td id="T_21ea5_row0_col9" class="data row0 col9" >0</td>
          <td id="T_21ea5_row0_col10" class="data row0 col10" >0</td>
          <td id="T_21ea5_row0_col11" class="data row0 col11" >0</td>
          <td id="T_21ea5_row0_col12" class="data row0 col12" >0</td>
          <td id="T_21ea5_row0_col13" class="data row0 col13" >0</td>
          <td id="T_21ea5_row0_col14" class="data row0 col14" >0</td>
          <td id="T_21ea5_row0_col15" class="data row0 col15" >12</td>
        </tr>
        <tr>
          <th id="T_21ea5_level0_row1" class="row_heading level0 row1" >0</th>
          <td id="T_21ea5_row1_col0" class="data row1 col0" >2B<br>0.623</td>
          <td id="T_21ea5_row1_col1" class="data row1 col1" >7E<br>0.523</td>
          <td id="T_21ea5_row1_col2" class="data row1 col2" >15<br>0.587</td>
          <td id="T_21ea5_row1_col3" class="data row1 col3" >16<br>0.512</td>
          <td id="T_21ea5_row1_col4" class="data row1 col4" >28<br>0.581</td>
          <td id="T_21ea5_row1_col5" class="data row1 col5" >43<br>0.466</td>
          <td id="T_21ea5_row1_col6" class="data row1 col6" >D2<br>0.675</td>
          <td id="T_21ea5_row1_col7" class="data row1 col7" >A6<br>0.532</td>
          <td id="T_21ea5_row1_col8" class="data row1 col8" >AB<br>0.625</td>
          <td id="T_21ea5_row1_col9" class="data row1 col9" >F7<br>0.533</td>
          <td id="T_21ea5_row1_col10" class="data row1 col10" >15<br>0.669</td>
          <td id="T_21ea5_row1_col11" class="data row1 col11" >88<br>0.588</td>
          <td id="T_21ea5_row1_col12" class="data row1 col12" >09<br>0.585</td>
          <td id="T_21ea5_row1_col13" class="data row1 col13" >CF<br>0.636</td>
          <td id="T_21ea5_row1_col14" class="data row1 col14" >4F<br>0.561</td>
          <td id="T_21ea5_row1_col15" class="data row1 col15" >7C<br>0.490</td>
        </tr>
        <tr>
          <th id="T_21ea5_level0_row2" class="row_heading level0 row2" >1</th>
          <td id="T_21ea5_row2_col0" class="data row2 col0" >20<br>0.486</td>
          <td id="T_21ea5_row2_col1" class="data row2 col1" >D6<br>0.473</td>
          <td id="T_21ea5_row2_col2" class="data row2 col2" >36<br>0.470</td>
          <td id="T_21ea5_row2_col3" class="data row2 col3" >2C<br>0.471</td>
          <td id="T_21ea5_row2_col4" class="data row2 col4" >CB<br>0.461</td>
          <td id="T_21ea5_row2_col5" class="data row2 col5" >D6<br>0.457</td>
          <td id="T_21ea5_row2_col6" class="data row2 col6" >57<br>0.481</td>
          <td id="T_21ea5_row2_col7" class="data row2 col7" >1C<br>0.476</td>
          <td id="T_21ea5_row2_col8" class="data row2 col8" >9A<br>0.493</td>
          <td id="T_21ea5_row2_col9" class="data row2 col9" >80<br>0.486</td>
          <td id="T_21ea5_row2_col10" class="data row2 col10" >D1<br>0.524</td>
          <td id="T_21ea5_row2_col11" class="data row2 col11" >30<br>0.486</td>
          <td id="T_21ea5_row2_col12" class="data row2 col12" >3E<br>0.466</td>
          <td id="T_21ea5_row2_col13" class="data row2 col13" >73<br>0.493</td>
          <td id="T_21ea5_row2_col14" class="data row2 col14" >DB<br>0.474</td>
          <td id="T_21ea5_row2_col15" class="data row2 col15" >70<br>0.476</td>
        </tr>
        <tr>
          <th id="T_21ea5_level0_row3" class="row_heading level0 row3" >2</th>
          <td id="T_21ea5_row3_col0" class="data row3 col0" >8B<br>0.456</td>
          <td id="T_21ea5_row3_col1" class="data row3 col1" >4F<br>0.467</td>
          <td id="T_21ea5_row3_col2" class="data row3 col2" >E3<br>0.470</td>
          <td id="T_21ea5_row3_col3" class="data row3 col3" >81<br>0.455</td>
          <td id="T_21ea5_row3_col4" class="data row3 col4" >D8<br>0.459</td>
          <td id="T_21ea5_row3_col5" class="data row3 col5" >81<br>0.455</td>
          <td id="T_21ea5_row3_col6" class="data row3 col6" >4C<br>0.466</td>
          <td id="T_21ea5_row3_col7" class="data row3 col7" >D6<br>0.465</td>
          <td id="T_21ea5_row3_col8" class="data row3 col8" >64<br>0.450</td>
          <td id="T_21ea5_row3_col9" class="data row3 col9" >57<br>0.469</td>
          <td id="T_21ea5_row3_col10" class="data row3 col10" >2E<br>0.466</td>
          <td id="T_21ea5_row3_col11" class="data row3 col11" >1E<br>0.465</td>
          <td id="T_21ea5_row3_col12" class="data row3 col12" >17<br>0.447</td>
          <td id="T_21ea5_row3_col13" class="data row3 col13" >53<br>0.478</td>
          <td id="T_21ea5_row3_col14" class="data row3 col14" >C0<br>0.473</td>
          <td id="T_21ea5_row3_col15" class="data row3 col15" >79<br>0.466</td>
        </tr>
        <tr>
          <th id="T_21ea5_level0_row4" class="row_heading level0 row4" >3</th>
          <td id="T_21ea5_row4_col0" class="data row4 col0" >B6<br>0.454</td>
          <td id="T_21ea5_row4_col1" class="data row4 col1" >1E<br>0.462</td>
          <td id="T_21ea5_row4_col2" class="data row4 col2" >A8<br>0.457</td>
          <td id="T_21ea5_row4_col3" class="data row4 col3" >D9<br>0.449</td>
          <td id="T_21ea5_row4_col4" class="data row4 col4" >17<br>0.457</td>
          <td id="T_21ea5_row4_col5" class="data row4 col5" >B1<br>0.450</td>
          <td id="T_21ea5_row4_col6" class="data row4 col6" >10<br>0.444</td>
          <td id="T_21ea5_row4_col7" class="data row4 col7" >20<br>0.454</td>
          <td id="T_21ea5_row4_col8" class="data row4 col8" >FC<br>0.431</td>
          <td id="T_21ea5_row4_col9" class="data row4 col9" >D6<br>0.466</td>
          <td id="T_21ea5_row4_col10" class="data row4 col10" >A9<br>0.459</td>
          <td id="T_21ea5_row4_col11" class="data row4 col11" >63<br>0.451</td>
          <td id="T_21ea5_row4_col12" class="data row4 col12" >34<br>0.445</td>
          <td id="T_21ea5_row4_col13" class="data row4 col13" >06<br>0.462</td>
          <td id="T_21ea5_row4_col14" class="data row4 col14" >AE<br>0.461</td>
          <td id="T_21ea5_row4_col15" class="data row4 col15" >D6<br>0.449</td>
        </tr>
        <tr>
          <th id="T_21ea5_level0_row5" class="row_heading level0 row5" >4</th>
          <td id="T_21ea5_row5_col0" class="data row5 col0" >5E<br>0.443</td>
          <td id="T_21ea5_row5_col1" class="data row5 col1" >D9<br>0.458</td>
          <td id="T_21ea5_row5_col2" class="data row5 col2" >4D<br>0.454</td>
          <td id="T_21ea5_row5_col3" class="data row5 col3" >63<br>0.438</td>
          <td id="T_21ea5_row5_col4" class="data row5 col4" >CF<br>0.453</td>
          <td id="T_21ea5_row5_col5" class="data row5 col5" >E9<br>0.444</td>
          <td id="T_21ea5_row5_col6" class="data row5 col6" >C2<br>0.443</td>
          <td id="T_21ea5_row5_col7" class="data row5 col7" >18<br>0.452</td>
          <td id="T_21ea5_row5_col8" class="data row5 col8" >41<br>0.430</td>
          <td id="T_21ea5_row5_col9" class="data row5 col9" >8A<br>0.456</td>
          <td id="T_21ea5_row5_col10" class="data row5 col10" >77<br>0.458</td>
          <td id="T_21ea5_row5_col11" class="data row5 col11" >F2<br>0.442</td>
          <td id="T_21ea5_row5_col12" class="data row5 col12" >A5<br>0.443</td>
          <td id="T_21ea5_row5_col13" class="data row5 col13" >28<br>0.460</td>
          <td id="T_21ea5_row5_col14" class="data row5 col14" >87<br>0.457</td>
          <td id="T_21ea5_row5_col15" class="data row5 col15" >DD<br>0.443</td>
        </tr>
      </tbody>
    </table>

    </div>


Did this attack work better than the previous one?

T-Tables for Decryption:
------------------------

Recall that the last round of AES is different than the rest of the
rounds. Instead of it applying ``subbytes``, ``shiftrows``,
``mixcolumns``, and ``addroundkey``, it leaves out ``mixcolumns``. You
might expect that this means that decryption doesn’t use a reverse
T-Table in the first decryption round, but this isn’t necessarily the
case! Since ``mixcolumns`` is a linear operation,
:math:`\operatorname{mixcolumns}( \operatorname{key} + \operatorname{state})`
is equal to
:math:`\operatorname{mixcolumns}(\operatorname{key}) + \operatorname{mixcolumns}(\operatorname{state})`.
Again, this is the approach that MBEDTLS takes, so we would be able to
use the reverse T-Table to attack decryption.
