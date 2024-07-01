Part 3, Topic 1: Large Hamming Weight Swings (MAIN)
===================================================



**SUMMARY:** *In the previous part of the course, you saw that a
microcontroller's power consumption changes based on what it's doing. In
the case of a simple password check, this allowed us to see how many
characters of the password we had correct, eventually resulting in the
password being broken.*

*That attack was based on different code execution paths showing up
differently in power traces. In this next set of labs, we'll posit that,
not only does different instructions affect power consumption, the data
being manipulated in the microcontroller also affects power
consumption.*

**LEARNING OUTCOMES:**

-  Using a power measurement to 'validate' a possible device model.
-  Detecting the value of a single bit using power measurement.
-  Breaking AES using the classic DPA attack.

Prerequisites
-------------

Hold up! Before you continue, check you've done the following tutorials:

-  ☑ Jupyter Notebook Intro (you should be OK with plotting & running
   blocks).
-  ☑ SCA101 Intro (you should have an idea of how to get
   hardware-specific versions running).
-  ☑ SCA101 Part 2 (you should understand how power consupmtion changes
   based on what code is being run)

Power Trace Gathering
---------------------

At this point you've got to insert code to perform the power trace
capture. There are two options here: \* Capture from physical device. \*
Read from a file.

You get to choose your adventure - see the two notebooks with the same
name of this, but called ``(SIMULATED)`` or ``(HARDWARE)`` to continue.
Inside those notebooks you should get some code to copy into the
following section, which will define the capture function.

Be sure you get the ``"✔️ OK to continue!"`` print once you run the next
cell, otherwise things will fail later on!


**In [1]:**

.. code:: ipython3

    SCOPETYPE = 'NONE'
    PLATFORM = 'NONE'
    CRYPTO_TARGET = 'NONE'
    VERSION = 'SIMULATED'
    allowable_exceptions = None
    SS_VER = 'SS_VER_2_1'


**In [2]:**

.. code:: ipython3

    if VERSION == 'HARDWARE':
        %run "Lab 3_1 - Large Hamming Weight Swings (HARDWARE).ipynb"
    elif VERSION == 'SIMULATED':
        %run "Lab 3_1 - Large Hamming Weight Swings (SIMULATED).ipynb"


**In [3]:**

.. code:: ipython3

    print(len(trace_array))


**Out [3]:**



.. parsed-literal::

    100




**In [4]:**

.. code:: ipython3

    assert len(trace_array) == 100
    print("✔️ OK to continue!")


**Out [4]:**



.. parsed-literal::

    ✔️ OK to continue!



Grouping Traces
---------------

As we've seen in the slides, we've made an assumption that setting bits
on the data lines consumes a measurable amount of power. Now, we're
going test that theory by getting our target to manipulate data with a
very high Hamming weight (0xFF) and a very low Hamming weight (0x00).
For this purpose, the target is currently running AES, and it encrypted
the text we sent it. If we're correct in our assumption, we should see a
measurable difference between power traces with a high Hamming weight
and a low one.

Currently, these traces are all mixed up. Separate them into two groups:
``one_list`` and ``zero_list``:


**In [5]:**

.. code:: ipython3

    # ###################
    # Add your code here
    # ###################
    #raise NotImplementedError("Add Your Code Here")
    
    # ###################
    # START SOLUTION
    # ###################
    one_list = []
    zero_list = []
    
    for i in range(len(trace_array)):
        if textin_array[i][0] == 0x00:
            one_list.append(trace_array[i])
        else:
            zero_list.append(trace_array[i])
    # ###################
    # END SOLUTION
    # ###################
    
    assert len(one_list) > len(zero_list)/2
    assert len(zero_list) > len(one_list)/2

We should have two different lists. Whether we sent 0xFF or 0x00 was
random, so these lists likely won't be evenly dispersed. Next, we'll
want to take an average of each group (make sure you take an average of
each trace at each point! We don't want an average of the traces in
time), which will help smooth out any outliers and also fix our issue of
having a different number of traces for each group:


**In [6]:**

.. code:: ipython3

    # ###################
    # Add your code here
    # ###################
    #raise NotImplementedError("Add Your Code Here")
    
    # ###################
    # START SOLUTION
    # ###################
    one_avg = np.mean(one_list, axis=0)
    zero_avg = np.mean(zero_list, axis=0)
    # ###################
    # END SOLUTION
    # ###################

Finally, subtract the two averages and plot the resulting data:


**In [7]:**

.. code:: ipython3

    # ###################
    # Add your code here
    # ###################
    #raise NotImplementedError("Add Your Code Here")
    
    # ###################
    # START SOLUTION
    # ###################
    %matplotlib inline
    import matplotlib.pyplot as plt
    
    diff = one_avg - zero_avg
    
    plt.plot(diff)
    plt.show()
    # ###################
    # END SOLUTION
    # ###################


**Out [7]:**


.. image:: img/NONE-NONE-SOLN_Lab3_1-LargeHammingWeightSwings_14_0.png


You should see a very distinct trace near the beginning of the plot,
meaning that the data being manipulated in the target device is visible
in its power trace! Again, there's a lot of room to explore here:

-  Try setting multiple bytes to 0x00 and 0xFF.
-  Try using smaller hamming weight differences. Is the spike still
   distinct? What about if you capture more traces?
-  We focused on the first byte here. Try putting the difference plots
   for multiple different bytes on the same plot.
-  The target is running AES here. Can you get the spikes to appear in
   different places if you set a byte in a later round of AES (say round
   5) to 0x00 or 0xFF?

--------------

NO-FUN DISCLAIMER: This material is Copyright (C) NewAE Technology Inc.,
2015-2020. ChipWhisperer is a trademark of NewAE Technology Inc.,
claimed in all jurisdictions, and registered in at least the United
States of America, European Union, and Peoples Republic of China.

Tutorials derived from our open-source work must be released under the
associated open-source license, and notice of the source must be
*clearly displayed*. Only original copyright holders may license or
authorize other distribution - while NewAE Technology Inc. holds the
copyright for many tutorials, the github repository includes community
contributions which we cannot license under special terms and **must**
be maintained as an open-source release. Please contact us for special
permissions (where possible).

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
