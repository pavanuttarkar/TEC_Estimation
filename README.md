# TEC Estimation

The python package for TEC estimation using Trimble Thunderbolt Single Frequency GPS module is written in python, with Klobuchar's algorithm for the TEC estimation. The Ionosphereic delay is used to calculate the vertical total electron content. 

This package requires the following modules to work
  1. numpy
  2. matplotlib
  3. TSIP (Python wrapper for the Trimble communication)
  4. mpld3

Everday a plot of the TEC and Ionospheric delay is produced, and updated on midnight, local time. An example plot can be seen here,


