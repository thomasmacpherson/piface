USING UNITY FOR Piface C Interace Refactoring (pfio.h & pfio.c)

1. Download CMock (which includes Unity) to an approriate directory. The Makefile assumes it has been put into /usr/share but CMock can be locaed anywhere
$ wget http://downloads.sourceforge.net/project/cmock/cmock/cmock2.0/cmock_2_0_204.zip
$ unzip cmock_2_0_204.zip

2. You should now find a directory cmock; the unity files are found under cmock/vendor/unity

3. Install ruby
$ sudo apt-get instal ruby

4. The Unity test file is found at piface/c/unitytest/test/tests.c

5. To run the tests, in the unitytest directory type
$ make

6. Unity automatically builds a new test main() function and executes the tests

NOTE
To use the automatic test hardess, then you will need to wire output.0 to input.0, output.1 to input.1, etc.

