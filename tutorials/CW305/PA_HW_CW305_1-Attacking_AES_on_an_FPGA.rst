Breaking Hardware AES on CW305 FPGA
===================================

This tutorial relies on previous knowledge from the SCA101 course
notebooks (in ``../courses/sca101/``); make sure you go through these
first to understand how a CPA attack works.

In this notebook, we'll apply knowledge from sca101 to break a hardware
AES implementation on the CW305 Artix FPGA.

Some out-of-date background on the target FPGA project is can be found
here: `Tutorial CW305-1 Building a
Project <http://wiki.newae.com/Tutorial_CW305-1_Building_a_Project>`__
(ignore the "capture setup" section, which uses the obsolete
ChipWhisperer GUI; this notebook shows all you need to know about
capture setup on the CW305 with Jupyter).

Background Theory
-----------------

During this tutorial, we'll be working with a hardware AES
implementation. This type of attack can be much more difficult than a
software AES attack. In the software AES attacks, we needed hundreds or
thousands of clock cycles to capture the algorithm's full execution. In
contrast, a hardware AES implementation may have a variety of speeds.
Depending on the performance of the hardware, a whole spectrum of
execution speeds can be achieved by executing many operations in a
single clock cycle. It is theoretically possible to execute the entire
AES encryption in a single cycle, given enough hardware space and
provided that the clock is not too fast. Most hardware accelerators are
designed to complete one round or one large part of a round in a single
cycle.

This fast execution may cause problems with a regular CPA attack. In
software, we found that it was easy to search for the outputs of the
s-boxes because these values would need to be loaded from memory onto a
high-capacitance data bus. This is not necessarily true on an FPGA,
where the output of the s-boxes may be directly fed into the next stage
of the algorithm. In general, we may need some more knowledge of the
hardware implementation to successfully complete an attack.

In our case, let's suppose that every round of AES is completed in a
single clock cycle. Recall the execution of AES:

Here, every blue block is executed in one clock cycle. This means that
an excellent candidate for a CPA attack is the difference between the
input and output of the final round. It is likely that this state is
stored in a port that is updated every round, so we expect that the
Hamming distance between the round input and output is the most
important factor on the power consumption. Also, the last round is the
easiest to attack because it has no MixColumns operation. We'll use this
Hamming distance as the target in our CPA attack.

Capture Notes
-------------

Most of the capture settings used below are similar to the standard
ChipWhisperer scope settings. However, there are a couple of interesting
points:

-  We're only capturing 129 samples (the minimum allowed), and the
   encryption is completed in less than 60 samples with an x4 ADC clock.
   This makes sense - as we mentioned above, our AES implementation is
   computing each round in a single clock cycle.
-  We're using EXTCLK x4 for our ADC clock. This means that the FPGA is
   outputting a clock signal, and we aren't driving it.

Other than these, the last interesting setting is the number of traces.
By default, the capture software is ready to capture 5000 traces - many
more than were required for software AES! It is difficult for us to
measure the small power spikes from the Hamming distance on the last
round: these signals are dwarfed by noise and the other operations on
the chip. To deal with this small signal level, we need to capture many
more traces.

Capture Setup
-------------

Setup is somewhat similar to other targets, except that we are using an
external clock (driven from the FPGA). We'll also do the rest of the
setup manually:


**In [1]:**

.. code:: ipython3

    FPGA_ID = '35t'  # change if not using K100t CW305
    allowable_exceptions = None
    CRYPTO_TARGET = 'NONE'
    VERSION = 'HARDWARE'
    SS_VER = 'SS_VER_2_1'
    SCOPETYPE = 'OPENADC'
    PLATFORM = 'CW305'


**In [2]:**

.. code:: ipython3

    import chipwhisperer as cw
    scope = cw.scope(hw_location=(5, 5))
    scope.gain.db = 25
    scope.adc.samples = 129
    scope.adc.offset = 0
    scope.adc.basic_mode = "rising_edge"
    scope.trigger.triggers = "tio4"
    scope.io.tio1 = "serial_rx"
    scope.io.tio2 = "serial_tx"
    scope.io.hs2 = "disabled"

Before setting the ADC clock, we connect to the CW305 board. Here we'll
need to specify our bitstream file to load as well as the usual scope
and target\_type arguments.

Pick the correct bitfile for your CW305 board (e.g. either '35t' or
'100t'). By setting ``force=False``, the bitfile will only be programmed
if the FPGA is uninitialized (e.g. after powering up). Change to
``force=True`` to always program the FPGA (e.g. if you have generated a
new bitfile).


**In [3]:**

.. code:: ipython3

    #target = cw.target(scope, cw.targets.CW305, fpga_id='35t', force=False, hw_location=(5, 9))
    target = cw.target(scope, cw.targets.CW305, fpga_id=FPGA_ID, force=True, hw_location=(5, 9))

Next we set all the PLLs. We enable CW305's PLL1; this clock will feed
both the target and the CW ADC. As explained
`here <http://wiki.newae.com/Tutorial_CW305-1_Building_a_Project#Capture_Setup>`__,
**make sure the DIP switches on the CW305 board are set as follows**: -
J16 = 0 - K16 = 1


**In [4]:**

.. code:: ipython3

    target.vccint_set(1.0)
    # we only need PLL1:
    target.pll.pll_enable_set(True)
    target.pll.pll_outenable_set(False, 0)
    target.pll.pll_outenable_set(True, 1)
    target.pll.pll_outenable_set(False, 2)
    
    # run at 10 MHz:
    target.pll.pll_outfreq_set(10E6, 1)
    
    # 1ms is plenty of idling time
    target.clkusbautooff = True
    target.clksleeptime = 1

CW-Husky requires a different setup when the ADC clock is driven by the
target:


**In [5]:**

.. code:: ipython3

    if scope._is_husky:
        scope.clock.clkgen_freq = 40e6
        scope.clock.clkgen_src = 'extclk'
        scope.clock.adc_mul = 4
        # if the target PLL frequency is changed, the above must also be changed accordingly
    else:
        scope.clock.adc_src = "extclk_x4"

Ensure the ADC clock is locked:


**In [6]:**

.. code:: ipython3

    import time
    for i in range(5):
        scope.clock.reset_adc()
        time.sleep(1)
        if scope.clock.adc_locked:
            break 
    assert (scope.clock.adc_locked), "ADC failed to lock"

Occasionally the ADC will fail to lock on the first try; when that
happens, the above assertion will fail (and on the CW-Lite, the red LED
will be on). Simply re-running the above cell again should fix things.

Trace Capture
-------------

Below is the capture loop. The main body of the loop loads some new
plaintext, arms the scope, sends the key and plaintext, then finally
records and appends our new trace to the ``traces[]`` list.

Because we're capturing 5000 traces, this takes a bit longer than the
attacks against software AES implementations.

Note that the encryption result is read from the target and compared to
the expected results, as a sanity check.


**In [7]:**

.. code:: ipython3

    project_file = "projects/Tutorial_HW_CW305.cwp"
    project = cw.create_project(project_file, overwrite=True)


**In [8]:**

.. code:: ipython3

    from tqdm import tnrange
    import numpy as np
    import time
    from Crypto.Cipher import AES
    
    ktp = cw.ktp.Basic()
    
    traces = []
    textin = []
    keys = []
    N = 5000  # Number of traces
    
    # initialize cipher to verify DUT result:
    key, text = ktp.next()
    cipher = AES.new(bytes(key), AES.MODE_ECB)
    
    for i in tnrange(N, desc='Capturing traces'):
        # run aux stuff that should come before trace here
    
        key, text = ktp.next()  # manual creation of a key, text pair can be substituted here
        textin.append(text)
        keys.append(key)
        
        ret = cw.capture_trace(scope, target, text, key)
        if not ret:
            print("Failed capture")
            continue
    
        assert (list(ret.textout) == list(cipher.encrypt(bytes(text)))), "Incorrect encryption result!\nGot {}\nExp {}\n".format(ret.textout, list(text))
        #trace += scope.getLastTrace()
            
        traces.append(ret.wave)
        project.traces.append(ret)


**Out [8]:**



.. parsed-literal::

    /tmp/ipykernel\_270/777411826.py:17: TqdmDeprecationWarning: Please use \`tqdm.notebook.trange\` instead of \`tqdm.tnrange\`
      for i in tnrange(N, desc='Capturing traces'):




.. parsed-literal::

    Capturing traces:   0%|          | 0/5000 [00:00<?, ?it/s]


This shows how a captured trace can be plotted:


**In [9]:**

.. code:: ipython3

    from bokeh.plotting import figure, show
    from bokeh.io import output_notebook
    
    output_notebook()
    p = figure(plot_width=800)
    
    xrange = range(len(traces[0]))
    p.line(xrange, traces[0], line_color="red")
    show(p)


**Out [9]:**


.. raw:: html

    <div class="data_html">
        
    <div class="bk-root">
        <a href="https://bokeh.org" target="_blank" class="bk-logo bk-logo-small bk-logo-notebook"></a>
        <span id="1002">Loading BokehJS ...</span>
    </div>
    </div>





.. raw:: html

    <div class="data_html">
        
    
    
    
    
    
    <div class="bk-root" id="d7e0f8e6-0e33-430e-b92a-a053d2708265" data-root-id="1003"></div>

    </div>




Finally we save our traces and disconnect. By saving the traces, the
attack can be repeated in the future without having to repeat the trace
acquisition steps above.


**In [10]:**

.. code:: ipython3

    project.save()
    scope.dis()
    target.dis()

Attack
------

Now we re-open our saved project and specify the attack parameters. For
this hardware AES implementation, we use a different leakage model and
attack than what is used for the software AES implementations.

Note that this attack requires only the ciphertext, not the plaintext.


**In [11]:**

.. code:: ipython3

    import chipwhisperer as cw
    import chipwhisperer.analyzer as cwa
    project_file = "projects/Tutorial_HW_CW305"
    project = cw.open_project(project_file)
    attack = cwa.cpa(project, cwa.leakage_models.last_round_state_diff)
    cb = cwa.get_jupyter_callback(attack)

This runs the attack:


**In [12]:**

.. code:: ipython3

    attack_results = attack.run(cb)


**Out [12]:**


.. raw:: html

    <div class="data_html">
        <style type="text/css">
    #T_aa0a2_row1_col0, #T_aa0a2_row1_col1, #T_aa0a2_row1_col2, #T_aa0a2_row1_col3, #T_aa0a2_row1_col4, #T_aa0a2_row1_col5, #T_aa0a2_row1_col6, #T_aa0a2_row1_col7, #T_aa0a2_row1_col8, #T_aa0a2_row1_col9, #T_aa0a2_row1_col10, #T_aa0a2_row1_col11, #T_aa0a2_row1_col12, #T_aa0a2_row1_col13, #T_aa0a2_row1_col14, #T_aa0a2_row1_col15 {
      color: red;
    }
    </style>
    <table id="T_aa0a2">
      <caption>Finished traces 4975 to 5000</caption>
      <thead>
        <tr>
          <th class="blank level0" >&nbsp;</th>
          <th id="T_aa0a2_level0_col0" class="col_heading level0 col0" >0</th>
          <th id="T_aa0a2_level0_col1" class="col_heading level0 col1" >1</th>
          <th id="T_aa0a2_level0_col2" class="col_heading level0 col2" >2</th>
          <th id="T_aa0a2_level0_col3" class="col_heading level0 col3" >3</th>
          <th id="T_aa0a2_level0_col4" class="col_heading level0 col4" >4</th>
          <th id="T_aa0a2_level0_col5" class="col_heading level0 col5" >5</th>
          <th id="T_aa0a2_level0_col6" class="col_heading level0 col6" >6</th>
          <th id="T_aa0a2_level0_col7" class="col_heading level0 col7" >7</th>
          <th id="T_aa0a2_level0_col8" class="col_heading level0 col8" >8</th>
          <th id="T_aa0a2_level0_col9" class="col_heading level0 col9" >9</th>
          <th id="T_aa0a2_level0_col10" class="col_heading level0 col10" >10</th>
          <th id="T_aa0a2_level0_col11" class="col_heading level0 col11" >11</th>
          <th id="T_aa0a2_level0_col12" class="col_heading level0 col12" >12</th>
          <th id="T_aa0a2_level0_col13" class="col_heading level0 col13" >13</th>
          <th id="T_aa0a2_level0_col14" class="col_heading level0 col14" >14</th>
          <th id="T_aa0a2_level0_col15" class="col_heading level0 col15" >15</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th id="T_aa0a2_level0_row0" class="row_heading level0 row0" >PGE=</th>
          <td id="T_aa0a2_row0_col0" class="data row0 col0" >0</td>
          <td id="T_aa0a2_row0_col1" class="data row0 col1" >0</td>
          <td id="T_aa0a2_row0_col2" class="data row0 col2" >0</td>
          <td id="T_aa0a2_row0_col3" class="data row0 col3" >0</td>
          <td id="T_aa0a2_row0_col4" class="data row0 col4" >0</td>
          <td id="T_aa0a2_row0_col5" class="data row0 col5" >0</td>
          <td id="T_aa0a2_row0_col6" class="data row0 col6" >0</td>
          <td id="T_aa0a2_row0_col7" class="data row0 col7" >0</td>
          <td id="T_aa0a2_row0_col8" class="data row0 col8" >0</td>
          <td id="T_aa0a2_row0_col9" class="data row0 col9" >0</td>
          <td id="T_aa0a2_row0_col10" class="data row0 col10" >0</td>
          <td id="T_aa0a2_row0_col11" class="data row0 col11" >0</td>
          <td id="T_aa0a2_row0_col12" class="data row0 col12" >0</td>
          <td id="T_aa0a2_row0_col13" class="data row0 col13" >0</td>
          <td id="T_aa0a2_row0_col14" class="data row0 col14" >0</td>
          <td id="T_aa0a2_row0_col15" class="data row0 col15" >0</td>
        </tr>
        <tr>
          <th id="T_aa0a2_level0_row1" class="row_heading level0 row1" >0</th>
          <td id="T_aa0a2_row1_col0" class="data row1 col0" >D0<br>0.174</td>
          <td id="T_aa0a2_row1_col1" class="data row1 col1" >14<br>0.201</td>
          <td id="T_aa0a2_row1_col2" class="data row1 col2" >F9<br>0.184</td>
          <td id="T_aa0a2_row1_col3" class="data row1 col3" >A8<br>0.165</td>
          <td id="T_aa0a2_row1_col4" class="data row1 col4" >C9<br>0.175</td>
          <td id="T_aa0a2_row1_col5" class="data row1 col5" >EE<br>0.206</td>
          <td id="T_aa0a2_row1_col6" class="data row1 col6" >25<br>0.184</td>
          <td id="T_aa0a2_row1_col7" class="data row1 col7" >89<br>0.187</td>
          <td id="T_aa0a2_row1_col8" class="data row1 col8" >E1<br>0.161</td>
          <td id="T_aa0a2_row1_col9" class="data row1 col9" >3F<br>0.180</td>
          <td id="T_aa0a2_row1_col10" class="data row1 col10" >0C<br>0.157</td>
          <td id="T_aa0a2_row1_col11" class="data row1 col11" >C8<br>0.182</td>
          <td id="T_aa0a2_row1_col12" class="data row1 col12" >B6<br>0.225</td>
          <td id="T_aa0a2_row1_col13" class="data row1 col13" >63<br>0.188</td>
          <td id="T_aa0a2_row1_col14" class="data row1 col14" >0C<br>0.165</td>
          <td id="T_aa0a2_row1_col15" class="data row1 col15" >A6<br>0.201</td>
        </tr>
        <tr>
          <th id="T_aa0a2_level0_row2" class="row_heading level0 row2" >1</th>
          <td id="T_aa0a2_row2_col0" class="data row2 col0" >C6<br>0.073</td>
          <td id="T_aa0a2_row2_col1" class="data row2 col1" >4A<br>0.055</td>
          <td id="T_aa0a2_row2_col2" class="data row2 col2" >B5<br>0.059</td>
          <td id="T_aa0a2_row2_col3" class="data row2 col3" >BA<br>0.056</td>
          <td id="T_aa0a2_row2_col4" class="data row2 col4" >F7<br>0.062</td>
          <td id="T_aa0a2_row2_col5" class="data row2 col5" >C9<br>0.053</td>
          <td id="T_aa0a2_row2_col6" class="data row2 col6" >74<br>0.054</td>
          <td id="T_aa0a2_row2_col7" class="data row2 col7" >7F<br>0.054</td>
          <td id="T_aa0a2_row2_col8" class="data row2 col8" >6E<br>0.060</td>
          <td id="T_aa0a2_row2_col9" class="data row2 col9" >A2<br>0.055</td>
          <td id="T_aa0a2_row2_col10" class="data row2 col10" >4C<br>0.052</td>
          <td id="T_aa0a2_row2_col11" class="data row2 col11" >62<br>0.054</td>
          <td id="T_aa0a2_row2_col12" class="data row2 col12" >C9<br>0.069</td>
          <td id="T_aa0a2_row2_col13" class="data row2 col13" >57<br>0.056</td>
          <td id="T_aa0a2_row2_col14" class="data row2 col14" >75<br>0.063</td>
          <td id="T_aa0a2_row2_col15" class="data row2 col15" >F1<br>0.057</td>
        </tr>
        <tr>
          <th id="T_aa0a2_level0_row3" class="row_heading level0 row3" >2</th>
          <td id="T_aa0a2_row3_col0" class="data row3 col0" >77<br>0.062</td>
          <td id="T_aa0a2_row3_col1" class="data row3 col1" >64<br>0.054</td>
          <td id="T_aa0a2_row3_col2" class="data row3 col2" >E6<br>0.056</td>
          <td id="T_aa0a2_row3_col3" class="data row3 col3" >6A<br>0.053</td>
          <td id="T_aa0a2_row3_col4" class="data row3 col4" >FF<br>0.062</td>
          <td id="T_aa0a2_row3_col5" class="data row3 col5" >52<br>0.053</td>
          <td id="T_aa0a2_row3_col6" class="data row3 col6" >E4<br>0.051</td>
          <td id="T_aa0a2_row3_col7" class="data row3 col7" >85<br>0.051</td>
          <td id="T_aa0a2_row3_col8" class="data row3 col8" >44<br>0.059</td>
          <td id="T_aa0a2_row3_col9" class="data row3 col9" >5D<br>0.053</td>
          <td id="T_aa0a2_row3_col10" class="data row3 col10" >E7<br>0.051</td>
          <td id="T_aa0a2_row3_col11" class="data row3 col11" >D7<br>0.054</td>
          <td id="T_aa0a2_row3_col12" class="data row3 col12" >9A<br>0.060</td>
          <td id="T_aa0a2_row3_col13" class="data row3 col13" >93<br>0.050</td>
          <td id="T_aa0a2_row3_col14" class="data row3 col14" >25<br>0.061</td>
          <td id="T_aa0a2_row3_col15" class="data row3 col15" >9B<br>0.055</td>
        </tr>
        <tr>
          <th id="T_aa0a2_level0_row4" class="row_heading level0 row4" >3</th>
          <td id="T_aa0a2_row4_col0" class="data row4 col0" >F5<br>0.054</td>
          <td id="T_aa0a2_row4_col1" class="data row4 col1" >BA<br>0.052</td>
          <td id="T_aa0a2_row4_col2" class="data row4 col2" >90<br>0.056</td>
          <td id="T_aa0a2_row4_col3" class="data row4 col3" >E5<br>0.052</td>
          <td id="T_aa0a2_row4_col4" class="data row4 col4" >E3<br>0.061</td>
          <td id="T_aa0a2_row4_col5" class="data row4 col5" >31<br>0.052</td>
          <td id="T_aa0a2_row4_col6" class="data row4 col6" >60<br>0.050</td>
          <td id="T_aa0a2_row4_col7" class="data row4 col7" >B0<br>0.051</td>
          <td id="T_aa0a2_row4_col8" class="data row4 col8" >36<br>0.057</td>
          <td id="T_aa0a2_row4_col9" class="data row4 col9" >11<br>0.052</td>
          <td id="T_aa0a2_row4_col10" class="data row4 col10" >84<br>0.050</td>
          <td id="T_aa0a2_row4_col11" class="data row4 col11" >8F<br>0.052</td>
          <td id="T_aa0a2_row4_col12" class="data row4 col12" >DC<br>0.056</td>
          <td id="T_aa0a2_row4_col13" class="data row4 col13" >1B<br>0.049</td>
          <td id="T_aa0a2_row4_col14" class="data row4 col14" >D4<br>0.061</td>
          <td id="T_aa0a2_row4_col15" class="data row4 col15" >9C<br>0.054</td>
        </tr>
        <tr>
          <th id="T_aa0a2_level0_row5" class="row_heading level0 row5" >4</th>
          <td id="T_aa0a2_row5_col0" class="data row5 col0" >04<br>0.052</td>
          <td id="T_aa0a2_row5_col1" class="data row5 col1" >99<br>0.052</td>
          <td id="T_aa0a2_row5_col2" class="data row5 col2" >66<br>0.055</td>
          <td id="T_aa0a2_row5_col3" class="data row5 col3" >B9<br>0.052</td>
          <td id="T_aa0a2_row5_col4" class="data row5 col4" >B9<br>0.058</td>
          <td id="T_aa0a2_row5_col5" class="data row5 col5" >78<br>0.051</td>
          <td id="T_aa0a2_row5_col6" class="data row5 col6" >5B<br>0.050</td>
          <td id="T_aa0a2_row5_col7" class="data row5 col7" >27<br>0.050</td>
          <td id="T_aa0a2_row5_col8" class="data row5 col8" >34<br>0.056</td>
          <td id="T_aa0a2_row5_col9" class="data row5 col9" >F7<br>0.052</td>
          <td id="T_aa0a2_row5_col10" class="data row5 col10" >1E<br>0.050</td>
          <td id="T_aa0a2_row5_col11" class="data row5 col11" >F0<br>0.049</td>
          <td id="T_aa0a2_row5_col12" class="data row5 col12" >AD<br>0.054</td>
          <td id="T_aa0a2_row5_col13" class="data row5 col13" >D1<br>0.047</td>
          <td id="T_aa0a2_row5_col14" class="data row5 col14" >61<br>0.059</td>
          <td id="T_aa0a2_row5_col15" class="data row5 col15" >99<br>0.054</td>
        </tr>
      </tbody>
    </table>

    </div>


The attack results can be saved for later viewing or processing without
having to repeat the attack:


**In [13]:**

.. code:: ipython3

    import pickle
    pickle_file = project_file + ".results.pickle"
    pickle.dump(attack_results, open(pickle_file, "wb"))

You may notice that we didn't get the expected key from this attack, but
still got a good difference in correlation between the best guess and
the next best guess. This is because we actually recovered the key from
the last round of AES. We'll need to use analyzer to get the actual AES
key:


**In [14]:**

.. code:: ipython3

    from chipwhisperer.analyzer.attacks.models.aes.key_schedule import key_schedule_rounds
    recv_lastroundkey = [kguess[0][0] for kguess in attack_results.find_maximums()]
    recv_key = key_schedule_rounds(recv_lastroundkey, 10, 0)
    for subkey in recv_key:
        print(hex(subkey))


**Out [14]:**



.. parsed-literal::

    0x2b
    0x7e
    0x15
    0x16
    0x28
    0xae
    0xd2
    0xa6
    0xab
    0xf7
    0x15
    0x88
    0x9
    0xcf
    0x4f
    0x3c



Tests
-----

Check that the key obtained by the attack is the key that was used. This
attack targets the last round key, so we have to roll it back to compare
against the key we provided.


**In [15]:**

.. code:: ipython3

    key = list(key)
    assert (key == recv_key), "Failed to recover encryption key\nGot:      {}\nExpected: {}".format(recv_key, key)

Next steps
----------

The ``jupyter/demos/CW305_ECC/`` folder contains a series of tutorials
for attacking hardware ECC on the CW305.

This CW305 appnote contains additional details on the CW305 platform:
http://media.newae.com/appnotes/NAE0010\_Whitepaper\_CW305\_AES\_SCA\_Attack.pdf


**In [ ]:**

