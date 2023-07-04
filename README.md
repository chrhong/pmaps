# **It is recommended to use linux `pmap` instead.**

# pmaps
This is tool to show `/proc/pid/maps` as picture, easy to find the free virtual address area.
Especially used to debug the continues virtual address not enough issue.

## Usage:
./pmaps.py (-h) (-f [file]) (-a) (-b [size]) (-k [keyword]) (-long [bitsSize])

* -h : show help
* -f : the file need to be checked, default: use ./example.maps
* -a : show avaliable free blocks
* -b : show free blocks size bigger than given
* -k : show blocks owner have the give keyword
* -l : set long bit size(64/32), used when maps file is not match with current env
* If no parameters given, then show the whole virtual address maps as a pic

## Demo:
![](demo.png)