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

    SCOPETYPE = 'OPENADC'
    PLATFORM = 'CWLITEARM'
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
    scope.gain.mode                          changed from low                       to high                     
    scope.gain.gain                          changed from 0                         to 30                       
    scope.gain.db                            changed from 5.5                       to 24.8359375               
    scope.adc.basic\_mode                     changed from low                       to rising\_edge              
    scope.adc.samples                        changed from 24400                     to 5000                     
    scope.adc.trig\_count                     changed from 11104360                  to 22080511                 
    scope.clock.adc\_src                      changed from clkgen\_x1                 to clkgen\_x4                
    scope.clock.adc\_freq                     changed from 23714561                  to 30081127                 
    scope.clock.adc\_rate                     changed from 23714561.0                to 30081127.0               
    scope.clock.clkgen\_div                   changed from 1                         to 26                       
    scope.clock.clkgen\_freq                  changed from 192000000.0               to 7384615.384615385        
    scope.io.tio1                            changed from serial\_tx                 to serial\_rx                
    scope.io.tio2                            changed from serial\_rx                 to serial\_tx                
    scope.io.hs2                             changed from None                      to clkgen                   
    Building for platform CWLITEARM with CRYPTO\_TARGET=MBEDTLS
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
       5704	    532	   1572	   7808	   1e80	simpleserial-aes-CWLITEARM.elf
    +--------------------------------------------------------
    + Built for platform CW-Lite Arm \(STM32F3\) with:
    + CRYPTO\_TARGET = MBEDTLS
    + CRYPTO\_OPTIONS = AES128C
    +--------------------------------------------------------
    Detected known STMF32: STM32F302xB(C)/303xB(C)
    Extended erase (0x44), this can take ten seconds or more
    Attempting to program 6235 bytes at 0x8000000
    STM32F Programming flash...
    STM32F Reading flash...
    Verified flash OK, 6235 bytes




.. parsed-literal::

    Capturing traces:   0%|          | 0/100 [00:00<?, ?it/s]




.. parsed-literal::

    27744



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
        <div id='eee26987-014b-4950-a720-a3d076ead593'>
      <div id="b82add86-6c60-473e-b6c6-ffa7f998db1a" data-root-id="eee26987-014b-4950-a720-a3d076ead593" style="display: contents;"></div>
    </div>
    <script type="application/javascript">(function(root) {
      var docs_json = {"696b8e75-7a8e-444c-b814-84fdd66dc812":{"version":"3.6.1","title":"Bokeh Application","roots":[{"type":"object","name":"panel.models.browser.BrowserInfo","id":"eee26987-014b-4950-a720-a3d076ead593"},{"type":"object","name":"panel.models.comm_manager.CommManager","id":"bbde3fc5-0976-4b32-ba6f-7e08383669ad","attributes":{"plot_id":"eee26987-014b-4950-a720-a3d076ead593","comm_id":"17446a650db84ae2aab18f6106d9ce81","client_comm_id":"bf3e602198b24cb19fdf37f535be8475"}}],"defs":[{"type":"model","name":"ReactiveHTML1"},{"type":"model","name":"FlexBox1","properties":[{"name":"align_content","kind":"Any","default":"flex-start"},{"name":"align_items","kind":"Any","default":"flex-start"},{"name":"flex_direction","kind":"Any","default":"row"},{"name":"flex_wrap","kind":"Any","default":"wrap"},{"name":"gap","kind":"Any","default":""},{"name":"justify_content","kind":"Any","default":"flex-start"}]},{"type":"model","name":"FloatPanel1","properties":[{"name":"config","kind":"Any","default":{"type":"map"}},{"name":"contained","kind":"Any","default":true},{"name":"position","kind":"Any","default":"right-top"},{"name":"offsetx","kind":"Any","default":null},{"name":"offsety","kind":"Any","default":null},{"name":"theme","kind":"Any","default":"primary"},{"name":"status","kind":"Any","default":"normalized"}]},{"type":"model","name":"GridStack1","properties":[{"name":"mode","kind":"Any","default":"warn"},{"name":"ncols","kind":"Any","default":null},{"name":"nrows","kind":"Any","default":null},{"name":"allow_resize","kind":"Any","default":true},{"name":"allow_drag","kind":"Any","default":true},{"name":"state","kind":"Any","default":[]}]},{"type":"model","name":"drag1","properties":[{"name":"slider_width","kind":"Any","default":5},{"name":"slider_color","kind":"Any","default":"black"},{"name":"value","kind":"Any","default":50}]},{"type":"model","name":"click1","properties":[{"name":"terminal_output","kind":"Any","default":""},{"name":"debug_name","kind":"Any","default":""},{"name":"clears","kind":"Any","default":0}]},{"type":"model","name":"FastWrapper1","properties":[{"name":"object","kind":"Any","default":null},{"name":"style","kind":"Any","default":null}]},{"type":"model","name":"NotificationAreaBase1","properties":[{"name":"js_events","kind":"Any","default":{"type":"map"}},{"name":"position","kind":"Any","default":"bottom-right"},{"name":"_clear","kind":"Any","default":0}]},{"type":"model","name":"NotificationArea1","properties":[{"name":"js_events","kind":"Any","default":{"type":"map"}},{"name":"notifications","kind":"Any","default":[]},{"name":"position","kind":"Any","default":"bottom-right"},{"name":"_clear","kind":"Any","default":0},{"name":"types","kind":"Any","default":[{"type":"map","entries":[["type","warning"],["background","#ffc107"],["icon",{"type":"map","entries":[["className","fas fa-exclamation-triangle"],["tagName","i"],["color","white"]]}]]},{"type":"map","entries":[["type","info"],["background","#007bff"],["icon",{"type":"map","entries":[["className","fas fa-info-circle"],["tagName","i"],["color","white"]]}]]}]}]},{"type":"model","name":"Notification","properties":[{"name":"background","kind":"Any","default":null},{"name":"duration","kind":"Any","default":3000},{"name":"icon","kind":"Any","default":null},{"name":"message","kind":"Any","default":""},{"name":"notification_type","kind":"Any","default":null},{"name":"_destroyed","kind":"Any","default":false}]},{"type":"model","name":"TemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"BootstrapTemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"TemplateEditor1","properties":[{"name":"layout","kind":"Any","default":[]}]},{"type":"model","name":"MaterialTemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"ReactiveESM1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"JSComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"ReactComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"AnyWidgetComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"request_value1","properties":[{"name":"fill","kind":"Any","default":"none"},{"name":"_synced","kind":"Any","default":null},{"name":"_request_sync","kind":"Any","default":0}]}]}};
      var render_items = [{"docid":"696b8e75-7a8e-444c-b814-84fdd66dc812","roots":{"eee26987-014b-4950-a720-a3d076ead593":"b82add86-6c60-473e-b6c6-ffa7f998db1a"},"root_ids":["eee26987-014b-4950-a720-a3d076ead593"]}];
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
        <div id='a4917fce-5811-4910-b9b8-0dd134c70437'>
      <div id="eaf0cdcc-bf4d-4fb7-9dd5-82dfd0720bb4" data-root-id="a4917fce-5811-4910-b9b8-0dd134c70437" style="display: contents;"></div>
    </div>
    <script type="application/javascript">(function(root) {
      var docs_json = {"ed4dfdbc-c2a6-4f2b-b7a6-8ba2914da90c":{"version":"3.6.1","title":"Bokeh Application","roots":[{"type":"object","name":"Row","id":"a4917fce-5811-4910-b9b8-0dd134c70437","attributes":{"name":"Row00266","tags":["embedded"],"stylesheets":["\n:host(.pn-loading):before, .pn-loading:before {\n  background-color: #c3c3c3;\n  mask-size: auto calc(min(50%, 400px));\n  -webkit-mask-size: auto calc(min(50%, 400px));\n}",{"type":"object","name":"ImportedStyleSheet","id":"4fd1a44d-fd90-41eb-90b7-f46d2b1f75fb","attributes":{"url":"https://cdn.holoviz.org/panel/1.5.4/dist/css/loading.css"}},{"type":"object","name":"ImportedStyleSheet","id":"637b80d6-b677-4103-8475-7bc22df0651a","attributes":{"url":"https://cdn.holoviz.org/panel/1.5.4/dist/css/listpanel.css"}},{"type":"object","name":"ImportedStyleSheet","id":"172822fb-6c39-4cb7-b889-637c753a069a","attributes":{"url":"https://cdn.holoviz.org/panel/1.5.4/dist/bundled/theme/default.css"}},{"type":"object","name":"ImportedStyleSheet","id":"8739d8e1-ea4d-475d-845d-aa45a77cab0e","attributes":{"url":"https://cdn.holoviz.org/panel/1.5.4/dist/bundled/theme/native.css"}}],"min_width":800,"margin":0,"sizing_mode":"stretch_width","align":"start","children":[{"type":"object","name":"Spacer","id":"27a9ea75-de77-41d4-b865-1c4f66de8ccd","attributes":{"name":"HSpacer00270","stylesheets":["\n:host(.pn-loading):before, .pn-loading:before {\n  background-color: #c3c3c3;\n  mask-size: auto calc(min(50%, 400px));\n  -webkit-mask-size: auto calc(min(50%, 400px));\n}",{"id":"4fd1a44d-fd90-41eb-90b7-f46d2b1f75fb"},{"id":"172822fb-6c39-4cb7-b889-637c753a069a"},{"id":"8739d8e1-ea4d-475d-845d-aa45a77cab0e"}],"margin":0,"sizing_mode":"stretch_width","align":"start"}},{"type":"object","name":"Figure","id":"8fca0e34-ff2e-4c0c-ac1b-c64867602ac9","attributes":{"width":800,"margin":[5,10],"sizing_mode":"fixed","align":"start","x_range":{"type":"object","name":"Range1d","id":"3c78718b-c359-4ded-b548-91d7430147eb","attributes":{"name":"x","tags":[[["x",null]],[]],"end":4999.0,"reset_start":0.0,"reset_end":4999.0}},"y_range":{"type":"object","name":"Range1d","id":"84c95793-e00d-4422-84f9-502f183cc9e7","attributes":{"name":"y","tags":[[["y",null]],{"type":"map","entries":[["invert_yaxis",false],["autorange",false]]}],"start":-0.4578125,"end":0.2546875,"reset_start":-0.4578125,"reset_end":0.2546875}},"x_scale":{"type":"object","name":"LinearScale","id":"d39dbdc8-203c-4fb3-ba5a-b296625856ac"},"y_scale":{"type":"object","name":"LinearScale","id":"d5e7ca2a-0086-47a0-8e9a-efe1a337ab60"},"title":{"type":"object","name":"Title","id":"e39f596e-397c-4f5e-8f9a-f0c0de2f0e1c","attributes":{"text_color":"black","text_font_size":"12pt"}},"renderers":[{"type":"object","name":"GlyphRenderer","id":"b9348d4a-5ce7-4181-abe6-92d695893d79","attributes":{"data_source":{"type":"object","name":"ColumnDataSource","id":"a301a695-0f84-4338-9b52-138d44fdfc3c","attributes":{"selected":{"type":"object","name":"Selection","id":"319a5c4f-6a89-4d56-9baa-8e7cb694fd60","attributes":{"indices":[],"line_indices":[]}},"selection_policy":{"type":"object","name":"UnionRenderers","id":"53022f81-ba1f-4d51-bcdf-6e72eefc6160"},"data":{"type":"map","entries":[["x",{"type":"ndarray","array":{"type":"bytes","data":"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"},"shape":[5000],"dtype":"float64","order":"little"}],["y",{"type":"ndarray","array":{"type":"bytes","data":"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"},"shape":[5000],"dtype":"float64","order":"little"}]]}}},"view":{"type":"object","name":"CDSView","id":"81f18e42-6dcd-453d-a589-167fd61eed6f","attributes":{"filter":{"type":"object","name":"AllIndices","id":"d93527e7-fd19-43f0-932f-0545972d9c2a"}}},"glyph":{"type":"object","name":"Line","id":"c0200a24-499b-4353-b97b-92f0b120af59","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"x"},"y":{"type":"field","field":"y"},"line_color":"#30a2da","line_width":2}},"selection_glyph":{"type":"object","name":"Line","id":"416402f3-f55f-43b9-839b-8cbfd65acb87","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"x"},"y":{"type":"field","field":"y"},"line_color":"#30a2da","line_width":2}},"nonselection_glyph":{"type":"object","name":"Line","id":"999bac1f-b764-4480-94e3-1d093ecf57f8","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"x"},"y":{"type":"field","field":"y"},"line_color":"#30a2da","line_alpha":0.1,"line_width":2}},"muted_glyph":{"type":"object","name":"Line","id":"6a2a29a1-883a-49ad-be4f-9be93b58b319","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"x"},"y":{"type":"field","field":"y"},"line_color":"#30a2da","line_alpha":0.2,"line_width":2}}}}],"toolbar":{"type":"object","name":"Toolbar","id":"5eedb039-59b9-4728-84bd-a3690138f12b","attributes":{"tools":[{"type":"object","name":"WheelZoomTool","id":"f938bb7c-eaf7-458f-9119-5422c107541b","attributes":{"tags":["hv_created"],"renderers":"auto","zoom_together":"none"}},{"type":"object","name":"HoverTool","id":"58d07896-8abd-45a8-baef-b05efe70b43c","attributes":{"tags":["hv_created"],"renderers":[{"id":"b9348d4a-5ce7-4181-abe6-92d695893d79"}],"tooltips":[["x","@{x}"],["y","@{y}"]]}},{"type":"object","name":"SaveTool","id":"6b675d5e-ba56-4792-89d9-cbdb04898376"},{"type":"object","name":"PanTool","id":"703d84d2-0793-4d3c-8f69-70b28ec6470a"},{"type":"object","name":"BoxZoomTool","id":"eddbf352-c822-48f1-918a-18bf85077449","attributes":{"overlay":{"type":"object","name":"BoxAnnotation","id":"9287de28-618c-44dd-834e-bddfbd9c0d1c","attributes":{"syncable":false,"line_color":"black","line_alpha":1.0,"line_width":2,"line_dash":[4,4],"fill_color":"lightgrey","fill_alpha":0.5,"level":"overlay","visible":false,"left":{"type":"number","value":"nan"},"right":{"type":"number","value":"nan"},"top":{"type":"number","value":"nan"},"bottom":{"type":"number","value":"nan"},"left_units":"canvas","right_units":"canvas","top_units":"canvas","bottom_units":"canvas","handles":{"type":"object","name":"BoxInteractionHandles","id":"31ba3f68-d70b-4983-99a2-0f687d1e7369","attributes":{"all":{"type":"object","name":"AreaVisuals","id":"de10b039-8788-4ede-b4c7-605ed2018c98","attributes":{"fill_color":"white","hover_fill_color":"lightgray"}}}}}}}},{"type":"object","name":"ResetTool","id":"09f62a8e-dd5e-4390-b4b6-f849ae7b6513"}],"active_drag":{"id":"eddbf352-c822-48f1-918a-18bf85077449"}}},"left":[{"type":"object","name":"LinearAxis","id":"1117f9f5-4504-4197-a7f8-dc9faa8a69fa","attributes":{"ticker":{"type":"object","name":"BasicTicker","id":"893e9eda-cc48-4dfa-8953-dce4b70135fd","attributes":{"mantissas":[1,2,5]}},"formatter":{"type":"object","name":"BasicTickFormatter","id":"f63135f9-997e-45c7-be1a-819336e9369b"},"axis_label":"y","major_label_policy":{"type":"object","name":"AllLabels","id":"ed55ec72-a766-46b8-b26f-738ea93f8514"}}}],"below":[{"type":"object","name":"LinearAxis","id":"9a208f1d-b5fc-4023-91ef-1de345b65418","attributes":{"ticker":{"type":"object","name":"BasicTicker","id":"4a8028dc-2eb6-44db-a84e-c74a30ff9371","attributes":{"mantissas":[1,2,5]}},"formatter":{"type":"object","name":"BasicTickFormatter","id":"118edf11-5f64-4ea0-9a45-cde0637458c8"},"axis_label":"x","major_label_policy":{"type":"object","name":"AllLabels","id":"b029f529-78b2-4e60-a2ee-5448a87dd4d4"}}}],"center":[{"type":"object","name":"Grid","id":"d6339025-259e-49cb-b987-71e317603fed","attributes":{"axis":{"id":"9a208f1d-b5fc-4023-91ef-1de345b65418"},"grid_line_color":null}},{"type":"object","name":"Grid","id":"120323c3-d813-404c-807c-4e3820cec425","attributes":{"dimension":1,"axis":{"id":"1117f9f5-4504-4197-a7f8-dc9faa8a69fa"},"grid_line_color":null}}],"min_border_top":10,"min_border_bottom":10,"min_border_left":10,"min_border_right":10,"output_backend":"webgl"}},{"type":"object","name":"Spacer","id":"3ecf7aa3-cb4d-4a1b-949b-7dcc67517201","attributes":{"name":"HSpacer00271","stylesheets":["\n:host(.pn-loading):before, .pn-loading:before {\n  background-color: #c3c3c3;\n  mask-size: auto calc(min(50%, 400px));\n  -webkit-mask-size: auto calc(min(50%, 400px));\n}",{"id":"4fd1a44d-fd90-41eb-90b7-f46d2b1f75fb"},{"id":"172822fb-6c39-4cb7-b889-637c753a069a"},{"id":"8739d8e1-ea4d-475d-845d-aa45a77cab0e"}],"margin":0,"sizing_mode":"stretch_width","align":"start"}}]}}],"defs":[{"type":"model","name":"ReactiveHTML1"},{"type":"model","name":"FlexBox1","properties":[{"name":"align_content","kind":"Any","default":"flex-start"},{"name":"align_items","kind":"Any","default":"flex-start"},{"name":"flex_direction","kind":"Any","default":"row"},{"name":"flex_wrap","kind":"Any","default":"wrap"},{"name":"gap","kind":"Any","default":""},{"name":"justify_content","kind":"Any","default":"flex-start"}]},{"type":"model","name":"FloatPanel1","properties":[{"name":"config","kind":"Any","default":{"type":"map"}},{"name":"contained","kind":"Any","default":true},{"name":"position","kind":"Any","default":"right-top"},{"name":"offsetx","kind":"Any","default":null},{"name":"offsety","kind":"Any","default":null},{"name":"theme","kind":"Any","default":"primary"},{"name":"status","kind":"Any","default":"normalized"}]},{"type":"model","name":"GridStack1","properties":[{"name":"mode","kind":"Any","default":"warn"},{"name":"ncols","kind":"Any","default":null},{"name":"nrows","kind":"Any","default":null},{"name":"allow_resize","kind":"Any","default":true},{"name":"allow_drag","kind":"Any","default":true},{"name":"state","kind":"Any","default":[]}]},{"type":"model","name":"drag1","properties":[{"name":"slider_width","kind":"Any","default":5},{"name":"slider_color","kind":"Any","default":"black"},{"name":"value","kind":"Any","default":50}]},{"type":"model","name":"click1","properties":[{"name":"terminal_output","kind":"Any","default":""},{"name":"debug_name","kind":"Any","default":""},{"name":"clears","kind":"Any","default":0}]},{"type":"model","name":"FastWrapper1","properties":[{"name":"object","kind":"Any","default":null},{"name":"style","kind":"Any","default":null}]},{"type":"model","name":"NotificationAreaBase1","properties":[{"name":"js_events","kind":"Any","default":{"type":"map"}},{"name":"position","kind":"Any","default":"bottom-right"},{"name":"_clear","kind":"Any","default":0}]},{"type":"model","name":"NotificationArea1","properties":[{"name":"js_events","kind":"Any","default":{"type":"map"}},{"name":"notifications","kind":"Any","default":[]},{"name":"position","kind":"Any","default":"bottom-right"},{"name":"_clear","kind":"Any","default":0},{"name":"types","kind":"Any","default":[{"type":"map","entries":[["type","warning"],["background","#ffc107"],["icon",{"type":"map","entries":[["className","fas fa-exclamation-triangle"],["tagName","i"],["color","white"]]}]]},{"type":"map","entries":[["type","info"],["background","#007bff"],["icon",{"type":"map","entries":[["className","fas fa-info-circle"],["tagName","i"],["color","white"]]}]]}]}]},{"type":"model","name":"Notification","properties":[{"name":"background","kind":"Any","default":null},{"name":"duration","kind":"Any","default":3000},{"name":"icon","kind":"Any","default":null},{"name":"message","kind":"Any","default":""},{"name":"notification_type","kind":"Any","default":null},{"name":"_destroyed","kind":"Any","default":false}]},{"type":"model","name":"TemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"BootstrapTemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"TemplateEditor1","properties":[{"name":"layout","kind":"Any","default":[]}]},{"type":"model","name":"MaterialTemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"ReactiveESM1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"JSComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"ReactComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"AnyWidgetComponent1","properties":[{"name":"esm_constants","kind":"Any","default":{"type":"map"}}]},{"type":"model","name":"request_value1","properties":[{"name":"fill","kind":"Any","default":"none"},{"name":"_synced","kind":"Any","default":null},{"name":"_request_sync","kind":"Any","default":0}]}]}};
      var render_items = [{"docid":"ed4dfdbc-c2a6-4f2b-b7a6-8ba2914da90c","roots":{"a4917fce-5811-4910-b9b8-0dd134c70437":"eaf0cdcc-bf4d-4fb7-9dd5-82dfd0720bb4"},"root_ids":["a4917fce-5811-4910-b9b8-0dd134c70437"]}];
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
    #T_380a1_row1_col0, #T_380a1_row1_col1, #T_380a1_row1_col2, #T_380a1_row1_col3, #T_380a1_row1_col4, #T_380a1_row1_col5, #T_380a1_row1_col6, #T_380a1_row1_col7, #T_380a1_row1_col8, #T_380a1_row1_col9, #T_380a1_row1_col10, #T_380a1_row1_col11, #T_380a1_row1_col12, #T_380a1_row1_col13, #T_380a1_row1_col14, #T_380a1_row1_col15 {
      color: red;
    }
    </style>
    <table id="T_380a1">
      <caption>Finished traces 75 to 100</caption>
      <thead>
        <tr>
          <th class="blank level0" >&nbsp;</th>
          <th id="T_380a1_level0_col0" class="col_heading level0 col0" >0</th>
          <th id="T_380a1_level0_col1" class="col_heading level0 col1" >1</th>
          <th id="T_380a1_level0_col2" class="col_heading level0 col2" >2</th>
          <th id="T_380a1_level0_col3" class="col_heading level0 col3" >3</th>
          <th id="T_380a1_level0_col4" class="col_heading level0 col4" >4</th>
          <th id="T_380a1_level0_col5" class="col_heading level0 col5" >5</th>
          <th id="T_380a1_level0_col6" class="col_heading level0 col6" >6</th>
          <th id="T_380a1_level0_col7" class="col_heading level0 col7" >7</th>
          <th id="T_380a1_level0_col8" class="col_heading level0 col8" >8</th>
          <th id="T_380a1_level0_col9" class="col_heading level0 col9" >9</th>
          <th id="T_380a1_level0_col10" class="col_heading level0 col10" >10</th>
          <th id="T_380a1_level0_col11" class="col_heading level0 col11" >11</th>
          <th id="T_380a1_level0_col12" class="col_heading level0 col12" >12</th>
          <th id="T_380a1_level0_col13" class="col_heading level0 col13" >13</th>
          <th id="T_380a1_level0_col14" class="col_heading level0 col14" >14</th>
          <th id="T_380a1_level0_col15" class="col_heading level0 col15" >15</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th id="T_380a1_level0_row0" class="row_heading level0 row0" >PGE=</th>
          <td id="T_380a1_row0_col0" class="data row0 col0" >0</td>
          <td id="T_380a1_row0_col1" class="data row0 col1" >0</td>
          <td id="T_380a1_row0_col2" class="data row0 col2" >0</td>
          <td id="T_380a1_row0_col3" class="data row0 col3" >0</td>
          <td id="T_380a1_row0_col4" class="data row0 col4" >0</td>
          <td id="T_380a1_row0_col5" class="data row0 col5" >0</td>
          <td id="T_380a1_row0_col6" class="data row0 col6" >0</td>
          <td id="T_380a1_row0_col7" class="data row0 col7" >0</td>
          <td id="T_380a1_row0_col8" class="data row0 col8" >0</td>
          <td id="T_380a1_row0_col9" class="data row0 col9" >0</td>
          <td id="T_380a1_row0_col10" class="data row0 col10" >0</td>
          <td id="T_380a1_row0_col11" class="data row0 col11" >0</td>
          <td id="T_380a1_row0_col12" class="data row0 col12" >0</td>
          <td id="T_380a1_row0_col13" class="data row0 col13" >0</td>
          <td id="T_380a1_row0_col14" class="data row0 col14" >0</td>
          <td id="T_380a1_row0_col15" class="data row0 col15" >0</td>
        </tr>
        <tr>
          <th id="T_380a1_level0_row1" class="row_heading level0 row1" >0</th>
          <td id="T_380a1_row1_col0" class="data row1 col0" >2B<br>0.897</td>
          <td id="T_380a1_row1_col1" class="data row1 col1" >7E<br>0.774</td>
          <td id="T_380a1_row1_col2" class="data row1 col2" >15<br>0.898</td>
          <td id="T_380a1_row1_col3" class="data row1 col3" >16<br>0.843</td>
          <td id="T_380a1_row1_col4" class="data row1 col4" >28<br>0.883</td>
          <td id="T_380a1_row1_col5" class="data row1 col5" >AE<br>0.886</td>
          <td id="T_380a1_row1_col6" class="data row1 col6" >D2<br>0.896</td>
          <td id="T_380a1_row1_col7" class="data row1 col7" >A6<br>0.821</td>
          <td id="T_380a1_row1_col8" class="data row1 col8" >AB<br>0.870</td>
          <td id="T_380a1_row1_col9" class="data row1 col9" >F7<br>0.850</td>
          <td id="T_380a1_row1_col10" class="data row1 col10" >15<br>0.861</td>
          <td id="T_380a1_row1_col11" class="data row1 col11" >88<br>0.901</td>
          <td id="T_380a1_row1_col12" class="data row1 col12" >09<br>0.842</td>
          <td id="T_380a1_row1_col13" class="data row1 col13" >CF<br>0.822</td>
          <td id="T_380a1_row1_col14" class="data row1 col14" >4F<br>0.857</td>
          <td id="T_380a1_row1_col15" class="data row1 col15" >3C<br>0.876</td>
        </tr>
        <tr>
          <th id="T_380a1_level0_row2" class="row_heading level0 row2" >1</th>
          <td id="T_380a1_row2_col0" class="data row2 col0" >A3<br>0.449</td>
          <td id="T_380a1_row2_col1" class="data row2 col1" >33<br>0.486</td>
          <td id="T_380a1_row2_col2" class="data row2 col2" >7A<br>0.458</td>
          <td id="T_380a1_row2_col3" class="data row2 col3" >A1<br>0.438</td>
          <td id="T_380a1_row2_col4" class="data row2 col4" >AF<br>0.468</td>
          <td id="T_380a1_row2_col5" class="data row2 col5" >EC<br>0.475</td>
          <td id="T_380a1_row2_col6" class="data row2 col6" >6F<br>0.479</td>
          <td id="T_380a1_row2_col7" class="data row2 col7" >8A<br>0.462</td>
          <td id="T_380a1_row2_col8" class="data row2 col8" >9B<br>0.488</td>
          <td id="T_380a1_row2_col9" class="data row2 col9" >A6<br>0.484</td>
          <td id="T_380a1_row2_col10" class="data row2 col10" >37<br>0.491</td>
          <td id="T_380a1_row2_col11" class="data row2 col11" >BF<br>0.491</td>
          <td id="T_380a1_row2_col12" class="data row2 col12" >7D<br>0.494</td>
          <td id="T_380a1_row2_col13" class="data row2 col13" >DF<br>0.511</td>
          <td id="T_380a1_row2_col14" class="data row2 col14" >68<br>0.489</td>
          <td id="T_380a1_row2_col15" class="data row2 col15" >3E<br>0.494</td>
        </tr>
        <tr>
          <th id="T_380a1_level0_row3" class="row_heading level0 row3" >2</th>
          <td id="T_380a1_row3_col0" class="data row3 col0" >E0<br>0.440</td>
          <td id="T_380a1_row3_col1" class="data row3 col1" >1D<br>0.477</td>
          <td id="T_380a1_row3_col2" class="data row3 col2" >04<br>0.438</td>
          <td id="T_380a1_row3_col3" class="data row3 col3" >C6<br>0.434</td>
          <td id="T_380a1_row3_col4" class="data row3 col4" >66<br>0.454</td>
          <td id="T_380a1_row3_col5" class="data row3 col5" >F6<br>0.450</td>
          <td id="T_380a1_row3_col6" class="data row3 col6" >5E<br>0.457</td>
          <td id="T_380a1_row3_col7" class="data row3 col7" >37<br>0.450</td>
          <td id="T_380a1_row3_col8" class="data row3 col8" >EB<br>0.464</td>
          <td id="T_380a1_row3_col9" class="data row3 col9" >AD<br>0.453</td>
          <td id="T_380a1_row3_col10" class="data row3 col10" >94<br>0.486</td>
          <td id="T_380a1_row3_col11" class="data row3 col11" >DC<br>0.489</td>
          <td id="T_380a1_row3_col12" class="data row3 col12" >DD<br>0.435</td>
          <td id="T_380a1_row3_col13" class="data row3 col13" >50<br>0.477</td>
          <td id="T_380a1_row3_col14" class="data row3 col14" >C6<br>0.454</td>
          <td id="T_380a1_row3_col15" class="data row3 col15" >E8<br>0.481</td>
        </tr>
        <tr>
          <th id="T_380a1_level0_row4" class="row_heading level0 row4" >3</th>
          <td id="T_380a1_row4_col0" class="data row4 col0" >E4<br>0.438</td>
          <td id="T_380a1_row4_col1" class="data row4 col1" >75<br>0.450</td>
          <td id="T_380a1_row4_col2" class="data row4 col2" >73<br>0.432</td>
          <td id="T_380a1_row4_col3" class="data row4 col3" >B0<br>0.429</td>
          <td id="T_380a1_row4_col4" class="data row4 col4" >97<br>0.453</td>
          <td id="T_380a1_row4_col5" class="data row4 col5" >1E<br>0.450</td>
          <td id="T_380a1_row4_col6" class="data row4 col6" >DF<br>0.439</td>
          <td id="T_380a1_row4_col7" class="data row4 col7" >52<br>0.438</td>
          <td id="T_380a1_row4_col8" class="data row4 col8" >A8<br>0.455</td>
          <td id="T_380a1_row4_col9" class="data row4 col9" >70<br>0.445</td>
          <td id="T_380a1_row4_col10" class="data row4 col10" >39<br>0.449</td>
          <td id="T_380a1_row4_col11" class="data row4 col11" >72<br>0.472</td>
          <td id="T_380a1_row4_col12" class="data row4 col12" >60<br>0.426</td>
          <td id="T_380a1_row4_col13" class="data row4 col13" >9F<br>0.453</td>
          <td id="T_380a1_row4_col14" class="data row4 col14" >0B<br>0.439</td>
          <td id="T_380a1_row4_col15" class="data row4 col15" >3F<br>0.468</td>
        </tr>
        <tr>
          <th id="T_380a1_level0_row5" class="row_heading level0 row5" >4</th>
          <td id="T_380a1_row5_col0" class="data row5 col0" >0A<br>0.433</td>
          <td id="T_380a1_row5_col1" class="data row5 col1" >CE<br>0.442</td>
          <td id="T_380a1_row5_col2" class="data row5 col2" >BC<br>0.427</td>
          <td id="T_380a1_row5_col3" class="data row5 col3" >53<br>0.428</td>
          <td id="T_380a1_row5_col4" class="data row5 col4" >7B<br>0.445</td>
          <td id="T_380a1_row5_col5" class="data row5 col5" >2D<br>0.446</td>
          <td id="T_380a1_row5_col6" class="data row5 col6" >F4<br>0.438</td>
          <td id="T_380a1_row5_col7" class="data row5 col7" >2A<br>0.431</td>
          <td id="T_380a1_row5_col8" class="data row5 col8" >FA<br>0.449</td>
          <td id="T_380a1_row5_col9" class="data row5 col9" >D0<br>0.439</td>
          <td id="T_380a1_row5_col10" class="data row5 col10" >8F<br>0.448</td>
          <td id="T_380a1_row5_col11" class="data row5 col11" >AB<br>0.463</td>
          <td id="T_380a1_row5_col12" class="data row5 col12" >C7<br>0.423</td>
          <td id="T_380a1_row5_col13" class="data row5 col13" >8D<br>0.449</td>
          <td id="T_380a1_row5_col14" class="data row5 col14" >E5<br>0.425</td>
          <td id="T_380a1_row5_col15" class="data row5 col15" >31<br>0.458</td>
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
    #T_fee45_row1_col0, #T_fee45_row1_col1, #T_fee45_row1_col2, #T_fee45_row1_col3, #T_fee45_row1_col4, #T_fee45_row1_col5, #T_fee45_row1_col6, #T_fee45_row1_col7, #T_fee45_row1_col8, #T_fee45_row1_col9, #T_fee45_row1_col10, #T_fee45_row1_col11, #T_fee45_row1_col12, #T_fee45_row1_col13, #T_fee45_row1_col14, #T_fee45_row1_col15 {
      color: red;
    }
    </style>
    <table id="T_fee45">
      <caption>Finished traces 75 to 100</caption>
      <thead>
        <tr>
          <th class="blank level0" >&nbsp;</th>
          <th id="T_fee45_level0_col0" class="col_heading level0 col0" >0</th>
          <th id="T_fee45_level0_col1" class="col_heading level0 col1" >1</th>
          <th id="T_fee45_level0_col2" class="col_heading level0 col2" >2</th>
          <th id="T_fee45_level0_col3" class="col_heading level0 col3" >3</th>
          <th id="T_fee45_level0_col4" class="col_heading level0 col4" >4</th>
          <th id="T_fee45_level0_col5" class="col_heading level0 col5" >5</th>
          <th id="T_fee45_level0_col6" class="col_heading level0 col6" >6</th>
          <th id="T_fee45_level0_col7" class="col_heading level0 col7" >7</th>
          <th id="T_fee45_level0_col8" class="col_heading level0 col8" >8</th>
          <th id="T_fee45_level0_col9" class="col_heading level0 col9" >9</th>
          <th id="T_fee45_level0_col10" class="col_heading level0 col10" >10</th>
          <th id="T_fee45_level0_col11" class="col_heading level0 col11" >11</th>
          <th id="T_fee45_level0_col12" class="col_heading level0 col12" >12</th>
          <th id="T_fee45_level0_col13" class="col_heading level0 col13" >13</th>
          <th id="T_fee45_level0_col14" class="col_heading level0 col14" >14</th>
          <th id="T_fee45_level0_col15" class="col_heading level0 col15" >15</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th id="T_fee45_level0_row0" class="row_heading level0 row0" >PGE=</th>
          <td id="T_fee45_row0_col0" class="data row0 col0" >0</td>
          <td id="T_fee45_row0_col1" class="data row0 col1" >0</td>
          <td id="T_fee45_row0_col2" class="data row0 col2" >0</td>
          <td id="T_fee45_row0_col3" class="data row0 col3" >0</td>
          <td id="T_fee45_row0_col4" class="data row0 col4" >0</td>
          <td id="T_fee45_row0_col5" class="data row0 col5" >0</td>
          <td id="T_fee45_row0_col6" class="data row0 col6" >0</td>
          <td id="T_fee45_row0_col7" class="data row0 col7" >0</td>
          <td id="T_fee45_row0_col8" class="data row0 col8" >0</td>
          <td id="T_fee45_row0_col9" class="data row0 col9" >0</td>
          <td id="T_fee45_row0_col10" class="data row0 col10" >0</td>
          <td id="T_fee45_row0_col11" class="data row0 col11" >0</td>
          <td id="T_fee45_row0_col12" class="data row0 col12" >0</td>
          <td id="T_fee45_row0_col13" class="data row0 col13" >0</td>
          <td id="T_fee45_row0_col14" class="data row0 col14" >0</td>
          <td id="T_fee45_row0_col15" class="data row0 col15" >0</td>
        </tr>
        <tr>
          <th id="T_fee45_level0_row1" class="row_heading level0 row1" >0</th>
          <td id="T_fee45_row1_col0" class="data row1 col0" >2B<br>0.823</td>
          <td id="T_fee45_row1_col1" class="data row1 col1" >7E<br>0.705</td>
          <td id="T_fee45_row1_col2" class="data row1 col2" >15<br>0.771</td>
          <td id="T_fee45_row1_col3" class="data row1 col3" >16<br>0.757</td>
          <td id="T_fee45_row1_col4" class="data row1 col4" >28<br>0.809</td>
          <td id="T_fee45_row1_col5" class="data row1 col5" >AE<br>0.830</td>
          <td id="T_fee45_row1_col6" class="data row1 col6" >D2<br>0.827</td>
          <td id="T_fee45_row1_col7" class="data row1 col7" >A6<br>0.756</td>
          <td id="T_fee45_row1_col8" class="data row1 col8" >AB<br>0.770</td>
          <td id="T_fee45_row1_col9" class="data row1 col9" >F7<br>0.731</td>
          <td id="T_fee45_row1_col10" class="data row1 col10" >15<br>0.736</td>
          <td id="T_fee45_row1_col11" class="data row1 col11" >88<br>0.797</td>
          <td id="T_fee45_row1_col12" class="data row1 col12" >09<br>0.768</td>
          <td id="T_fee45_row1_col13" class="data row1 col13" >CF<br>0.763</td>
          <td id="T_fee45_row1_col14" class="data row1 col14" >4F<br>0.773</td>
          <td id="T_fee45_row1_col15" class="data row1 col15" >3C<br>0.793</td>
        </tr>
        <tr>
          <th id="T_fee45_level0_row2" class="row_heading level0 row2" >1</th>
          <td id="T_fee45_row2_col0" class="data row2 col0" >B2<br>0.491</td>
          <td id="T_fee45_row2_col1" class="data row2 col1" >9B<br>0.483</td>
          <td id="T_fee45_row2_col2" class="data row2 col2" >02<br>0.435</td>
          <td id="T_fee45_row2_col3" class="data row2 col3" >5C<br>0.475</td>
          <td id="T_fee45_row2_col4" class="data row2 col4" >7B<br>0.452</td>
          <td id="T_fee45_row2_col5" class="data row2 col5" >F6<br>0.465</td>
          <td id="T_fee45_row2_col6" class="data row2 col6" >6F<br>0.483</td>
          <td id="T_fee45_row2_col7" class="data row2 col7" >70<br>0.457</td>
          <td id="T_fee45_row2_col8" class="data row2 col8" >47<br>0.463</td>
          <td id="T_fee45_row2_col9" class="data row2 col9" >A6<br>0.504</td>
          <td id="T_fee45_row2_col10" class="data row2 col10" >94<br>0.474</td>
          <td id="T_fee45_row2_col11" class="data row2 col11" >7C<br>0.454</td>
          <td id="T_fee45_row2_col12" class="data row2 col12" >3B<br>0.497</td>
          <td id="T_fee45_row2_col13" class="data row2 col13" >CA<br>0.496</td>
          <td id="T_fee45_row2_col14" class="data row2 col14" >2A<br>0.464</td>
          <td id="T_fee45_row2_col15" class="data row2 col15" >E8<br>0.498</td>
        </tr>
        <tr>
          <th id="T_fee45_level0_row3" class="row_heading level0 row3" >2</th>
          <td id="T_fee45_row3_col0" class="data row3 col0" >A3<br>0.459</td>
          <td id="T_fee45_row3_col1" class="data row3 col1" >85<br>0.446</td>
          <td id="T_fee45_row3_col2" class="data row3 col2" >73<br>0.433</td>
          <td id="T_fee45_row3_col3" class="data row3 col3" >C6<br>0.433</td>
          <td id="T_fee45_row3_col4" class="data row3 col4" >66<br>0.443</td>
          <td id="T_fee45_row3_col5" class="data row3 col5" >53<br>0.458</td>
          <td id="T_fee45_row3_col6" class="data row3 col6" >B0<br>0.454</td>
          <td id="T_fee45_row3_col7" class="data row3 col7" >C6<br>0.447</td>
          <td id="T_fee45_row3_col8" class="data row3 col8" >27<br>0.457</td>
          <td id="T_fee45_row3_col9" class="data row3 col9" >C5<br>0.454</td>
          <td id="T_fee45_row3_col10" class="data row3 col10" >39<br>0.441</td>
          <td id="T_fee45_row3_col11" class="data row3 col11" >06<br>0.450</td>
          <td id="T_fee45_row3_col12" class="data row3 col12" >AC<br>0.488</td>
          <td id="T_fee45_row3_col13" class="data row3 col13" >9F<br>0.477</td>
          <td id="T_fee45_row3_col14" class="data row3 col14" >DD<br>0.450</td>
          <td id="T_fee45_row3_col15" class="data row3 col15" >3E<br>0.497</td>
        </tr>
        <tr>
          <th id="T_fee45_level0_row4" class="row_heading level0 row4" >3</th>
          <td id="T_fee45_row4_col0" class="data row4 col0" >61<br>0.453</td>
          <td id="T_fee45_row4_col1" class="data row4 col1" >EB<br>0.428</td>
          <td id="T_fee45_row4_col2" class="data row4 col2" >59<br>0.426</td>
          <td id="T_fee45_row4_col3" class="data row4 col3" >0E<br>0.425</td>
          <td id="T_fee45_row4_col4" class="data row4 col4" >F9<br>0.441</td>
          <td id="T_fee45_row4_col5" class="data row4 col5" >49<br>0.446</td>
          <td id="T_fee45_row4_col6" class="data row4 col6" >22<br>0.448</td>
          <td id="T_fee45_row4_col7" class="data row4 col7" >3A<br>0.441</td>
          <td id="T_fee45_row4_col8" class="data row4 col8" >66<br>0.452</td>
          <td id="T_fee45_row4_col9" class="data row4 col9" >D0<br>0.450</td>
          <td id="T_fee45_row4_col10" class="data row4 col10" >52<br>0.439</td>
          <td id="T_fee45_row4_col11" class="data row4 col11" >72<br>0.447</td>
          <td id="T_fee45_row4_col12" class="data row4 col12" >F6<br>0.434</td>
          <td id="T_fee45_row4_col13" class="data row4 col13" >DF<br>0.472</td>
          <td id="T_fee45_row4_col14" class="data row4 col14" >68<br>0.446</td>
          <td id="T_fee45_row4_col15" class="data row4 col15" >77<br>0.471</td>
        </tr>
        <tr>
          <th id="T_fee45_level0_row5" class="row_heading level0 row5" >4</th>
          <td id="T_fee45_row5_col0" class="data row5 col0" >6E<br>0.446</td>
          <td id="T_fee45_row5_col1" class="data row5 col1" >A2<br>0.426</td>
          <td id="T_fee45_row5_col2" class="data row5 col2" >BA<br>0.426</td>
          <td id="T_fee45_row5_col3" class="data row5 col3" >71<br>0.423</td>
          <td id="T_fee45_row5_col4" class="data row5 col4" >B5<br>0.438</td>
          <td id="T_fee45_row5_col5" class="data row5 col5" >65<br>0.441</td>
          <td id="T_fee45_row5_col6" class="data row5 col6" >D1<br>0.440</td>
          <td id="T_fee45_row5_col7" class="data row5 col7" >8A<br>0.437</td>
          <td id="T_fee45_row5_col8" class="data row5 col8" >E3<br>0.444</td>
          <td id="T_fee45_row5_col9" class="data row5 col9" >CA<br>0.431</td>
          <td id="T_fee45_row5_col10" class="data row5 col10" >37<br>0.429</td>
          <td id="T_fee45_row5_col11" class="data row5 col11" >25<br>0.445</td>
          <td id="T_fee45_row5_col12" class="data row5 col12" >2D<br>0.423</td>
          <td id="T_fee45_row5_col13" class="data row5 col13" >FF<br>0.439</td>
          <td id="T_fee45_row5_col14" class="data row5 col14" >BD<br>0.440</td>
          <td id="T_fee45_row5_col15" class="data row5 col15" >B4<br>0.459</td>
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
