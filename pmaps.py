#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys
import commands
import math

LONG_BIT = int(commands.getoutput("getconf LONG_BIT"))
TARGET_FILE = 'example.maps'

BUSY_BLOCK = "\033[1;31;40m|-------------------------------|\033[0m" # red block
FREE_BLOCK = "\033[1;32;40m|+++++++++++++++++++++++++++++++|\033[0m" # green block

USAGE_EXAMPLE = \
    "This is tool to show the virtual address maps as a visiable pic\n" \
    "Usage:\n"\
    "./pmaps.py (-h) (-f [file]) (-a) (-b [size]) (-k [keyword]) (-l [bitsSize])\n" \
    "\n" \
    "-h : show help\n" \
    "-f : the file need to be checked, default: use ./example.maps\n" \
    "-a : show avaliable free blocks\n" \
    "-b : show free blocks size bigger than given\n" \
    "-k : show blocks owner have the give keyword\n" \
    "-l : set long bit size(64/32), used when maps file is not match with current env\n" \
    "If no parameters given, then show the whole virtual address maps as a pic\n"

def print_red(log_str):
    print("\033[1;31;40m\t%s\033[0m" % log_str)

def print_green(log_str):
    print("\033[1;32;40m\t%s\033[0m" % log_str)

def get_maps_line(num):
    return commands.getoutput("cat %s | awk '{print $%d}'" % (TARGET_FILE, num)).split('\n')

def get_virtaddr_list():
    vaddr_start = []
    vaddr_end = []
    vaddr_list = get_maps_line(1)
    #print(vaddr_list)

    for i in vaddr_list:
        vaddr_start.append(i.split('-')[0])
        vaddr_end.append(i.split('-')[1])
    #print vaddr_start
    #print vaddr_end

    return vaddr_start, vaddr_end

def get_flag_list():
    return get_maps_line(2)

def get_pgoff_list():
    return get_maps_line(3)

def get_dev_list():
    return get_maps_line(4)

def get_inode_list():
    return get_maps_line(5)

def get_owner_list():
    return get_maps_line(6)

def get_size_list(vm_start, vm_end):
    i = 0
    size = 0
    sz_list = []

    for i in range(len(vm_start)):
        size = long(vm_end[i], 16) - long(vm_start[i], 16)
        #print(hex(size))
        sz_list.append(hex(int(size)))

    return sz_list

# len(free_list) = len(vm_start) + 1
def get_free_list(max_addr, vm_start, vm_end):
    i = 0
    size = 0
    sz_list = []
    #0~first addr
    size = long(vm_start[i], 16) - 0
    sz_list.append(hex(size))

    for i in range(len(vm_start)-1):
        size = long(vm_start[i+1], 16) - long(vm_end[i], 16)
        sz_list.append(hex(size))

    #last addr ~ end
    size = max_addr - long(vm_end[-1], 16)
    sz_list.append(hex(size))

    return sz_list

def draw_pic(vm_start, vm_end, sz_list, free_list, max_addr, owner_list):
    print(FREE_BLOCK + ' 0x0 \t None')
    print_green(free_list[0])

    for i in range(len(vm_start)):
        print(BUSY_BLOCK + ' 0x' + vm_start[i] + '\t' + owner_list[i])
        print_red(sz_list[i])
        if free_list[i+1] != '0x0L':
            print(FREE_BLOCK + ' 0x' + vm_end[i] + '\t None')
            print_green(free_list[i+1])

    print(BUSY_BLOCK + ' ' + hex(max_addr))
    return

def show_help(vm_start, vm_end, sz_list, free_list, max_addr, owner_list, params):
    print(USAGE_EXAMPLE)
    return

def show_avaliable_block(vm_start, vm_end, sz_list, free_list, max_addr, owner_list, params):
    if free_list[0] != '0x0L':
        print(FREE_BLOCK + ' 0x0')
        print_green(free_list[0])
        print(FREE_BLOCK + ' 0x' + vm_start[0])
        print('')

    #notice i = len(free_list)-2 at for end
    for i in range(1, len(free_list) - 1):
        if free_list[i] != '0x0L':
            print(FREE_BLOCK + ' 0x' + vm_end[i-1])
            print_green(free_list[i])
            print(FREE_BLOCK + ' 0x' + vm_start[i])
            print('')

    if free_list[-1] != '0x0L':
        print(FREE_BLOCK + ' 0x' + vm_end[-1])
        print_green(free_list[-1])
        print(FREE_BLOCK + ' ' + hex(max_addr))
        print('')

def show_blocks_bigger_than_size(vm_start, vm_end, sz_list, free_list, max_addr, owner_list, params):
    given_size = int(params[1], 16) if '0x' in params[1] else int(params[1])

    if free_list[0] != '0x0L' and long(free_list[0], 16) > given_size:
        print(FREE_BLOCK + ' 0x0')
        print_green(free_list[0])
        print(FREE_BLOCK + ' 0x' + vm_start[1])
        print('')

    #notice i = len(free_list)-2 at for end
    for i in range(1, len(free_list) - 1):
        if free_list[i] != '0x0L' and long(free_list[i], 16) > given_size:
            print(FREE_BLOCK + ' 0x' + vm_end[i-1])
            print_green(free_list[i])
            print(FREE_BLOCK + ' 0x' + vm_start[i])
            print('')

    if free_list[-1] != '0x0L' and long(free_list[-1], 16) > given_size:
        print(FREE_BLOCK + ' 0x' + vm_end[-1])
        print_green(free_list[-1])
        print(FREE_BLOCK + ' ' + hex(max_addr))
        print('')

def filter_owner_with_key(vm_start, vm_end, sz_list, free_list, max_addr, owner_list, params):
    for i in range(1, len(owner_list)):
        if params[1] in owner_list[i]:
            print(BUSY_BLOCK + ' 0x' + vm_start[i] + '\t' + owner_list[i])
            print_red(sz_list[i])
            print(BUSY_BLOCK + ' 0x' + vm_end[i])
            print('')

    return

def parse_args_by_key(params_list, key):
    key_value = ''
    if key in params_list:
        i = params_list.index(key)
        key_value = params_list[i + 1]
        del params_list[i + 1]
        del params_list[i]
        #print(params_list)
    return key_value

ACTION_MAPS = {
    '-h' : show_help,
    '-a' : show_avaliable_block,
    '-b' : show_blocks_bigger_than_size,
    '-k' : filter_owner_with_key
}

def _main():
    params_list = sys.argv[1:]

    global LONG_BIT
    global TARGET_FILE
    long_bit_str = parse_args_by_key(params_list, '-l')
    target_file  = parse_args_by_key(params_list, '-f')
    LONG_BIT = float(long_bit_str) if long_bit_str else LONG_BIT
    TARGET_FILE = target_file if target_file else TARGET_FILE

    max_addr = long(math.pow(2, LONG_BIT)) - 1
    vm_start,vm_end = get_virtaddr_list()
    sz_list = get_size_list(vm_start, vm_end)
    free_list = get_free_list(max_addr, vm_start, vm_end)
    owner_list = get_owner_list()

    if len(params_list) > 0:
        ACTION_MAPS[params_list[0]](vm_start, vm_end, sz_list, free_list, max_addr, owner_list, params_list)
    else:
        draw_pic(vm_start, vm_end, sz_list, free_list, max_addr, owner_list)

    return

if __name__ == "__main__":
    _main()