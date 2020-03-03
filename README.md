# GDS2tov30
Converts a GDSII layout file to Jeol v30 format
This project was last updated on 6/30/2014

Hello,

This project was developed to extend the capabilities of our Jeol JBX-5500FS at the University of Houston Nanofabrication Facility. The motivation was to provide a free alternative to GeniSys Beamer which costs over $50,000 with a recurring annual cost of over $10,000. I am writing this on 3/3/2020. It has been nearly 6 years since I last worked on this project, but I'll try my best to help you get started.

This project was developed using python 2.7. I suggest starting with the latest version of the Anaconda Python 2.7 package. Each *.py file is a class with a test() function. The test function is designed to provide a basic test to ensure that everything is in working order. If the test fails, you are most likely missing a required library and the error message should provide you with enough information to fix the problem.

This project contains 3 major classes:
  GDSII:  This class can read and write GDSII Stream file format release 6.0 (file extension is .gds)
  v3:     This class can only write a Jeol 3.0 format (file extension is .v30)
  ELD:    The Ebeam Lithography Datastructure class provides additional fuctions to support electronbeam lithography such as pattern fracturing, field fracturing, array fracturing, coordinate transforms, scaling, displacements, etc.
  
I use the free layout editor from KLayout.de. KLayout provides python scripting support which is an interesting opportunity to develop a user friendly interface. A very useful first project is to develop a fracturing algorithm for KLayout to produce Ebeam compatible shapes. Then the layout file can be converted using the basic software provided by the vendor. This approach will help out researchers no matter what Ebeam writer they own!

Best,
Long
