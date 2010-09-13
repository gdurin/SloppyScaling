==========================
Data and Fitting functions
==========================

Introduction
------------
Data (experimental or simulated) can be fit with functions. But to be able to make a fit in case of multiple data files, we must do a series of steps:
   
#. Define one or more fitting functions, with fitting parameters
#. Associate each experimental data with its fitting function
#. Load the data and find the best fit

Data are usually taken at different 'experimental' conditions, changing an external parameter.
Consider for instance the blackbody radiation density :math:`\rho(\lambda, T)` which is a function of the wavelength :math:`\lambda`, and the temperature :math:`T`. A measure of :math:`\rho` is actually a series of :math:`\rho(\lambda)`   at different temperatures. 

To express it in our code, we use the following notation:

:math:`\rho(\lambda|T)`

which looks like a conditional probability, but tells the code to consider data as a function of :math:`\lambda`, and see files for different temperatures :math:`T`. (By the way, this notation is correct for a conditional probabilities). 

Writing functions
-----------------

But... how to write our fitting function :math:`\rho(\lambda|T)` to be read by the code? 

Python can read function with the simple usual math. Here we want to introduce a few rules to have i) the most *natural style*, that is 'write functions as you think they are fine', and ii) switch to latex (almost) automatically. For instance, our density could be written as::

   rho(lambda|T) = (8*pi*h*c)/lambda**5 * (exp(h*c/(k*T*lambda))-1)**(-1)

which is (tentatively) translated into a LaTeX string as:

.. image:: eqn000.png

The LaTeX equation which can be further tweaked for better rendering in the plots.

A few simple rules
++++++++++++++++++

Let's introduce a few simple mnemonic rules to write the equations without pain. These rules highly help the automatic switch to the LaTeX equation:

* write Greek letters in full
* to see a space in the LaTeX eq. between two terms use " * " (i.e. space+*+space), otherwise do not introduce any space. So that, "(1+x)*(1+y)" -> :math:`(1+x)(1+y)`, while "(1+x) * (1+y)" -> :math:`(1+x)~(1+y)`
* Subscript notation "_" can be a nightmare for the LaTex equation. Use as many underscores as the number of elements to be put as subscript. So. "I_y" -> :math:`I_y`, and "I__xy" -> :math:`I_{xy}` etc (but no more that 3!)
* Scaling variables: if you have a variable "X", define its scaling variable as "X_s"

A good example is the following::

    s = "P(S|W) = alpha**2 + eta * (S/W)**1.5 * exp(-(S/S_0)**2.5)"

that is:

.. image:: eqn0000.png

Now let's try a doctest:

>>> print "Hello world"
