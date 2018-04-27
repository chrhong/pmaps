#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys
import commands
import math

LONG_BIT = int(commands.getoutput("getconf LONG_BIT"))

RED_BLOCK =   "\033[1;31;40m|-------------------------------|\033[0m"
EMPTY_BLOCK = "\033[1;37;40m|\t|\033[0m"
GREEN_BLOCK = "\033[1;32;40m|+++++++++++++++++++++++++++++++|\033[0m"

USAGE_EXAMPLE = \
    "This is tool to show the virtual address maps as a visiable pic\n" \
    "Usage:\n"\
    "./pmaps.py (-h) (-f) (-b [size]) (-k [keyword]) (-long [bitsSize])\n" \
    "\n" \
    "-h : show help\n" \
    "-f : show free blocks\n" \
    "-b : show free blocks size bigger than given\n" \
    "-k : show blocks owner have the give keyword\n" \
    "-l : set long bit size(64/32), used when maps file is not match with current env\n" \
    "If no parameters given, then show the whole virtual address maps as a pic\n"

def print_red(log_str):
    print("\033[1;31;40m\t%s\033[0m" % log_str)

def print_green(log_str):
    print("\033[1;32;40m\t%s\033[0m" % log_str)

def get_maps_line(num):
    return commands.getoutput("cat virtualaddr.txt | awk '{print $%d}'" % num).split('\n')

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
    while i < len(vm_start):
        size = long(vm_end[i], 16) - long(vm_start[i], 16)
        #print(hex(size))
        sz_list.append(hex(int(size)))
        i += 1

    return sz_list

# len(free_list) = len(vm_start) + 1
def get_free_list(max_addr, vm_start, vm_end):
    i = 0
    size = 0
    sz_list = []
    #0~first addr
    size = long(vm_start[i+1], 16) - 0
    sz_list.append(hex(size))

    while i < len(vm_start) - 1:
        size = long(vm_start[i+1], 16) - long(vm_end[i], 16)
        sz_list.append(hex(size))
        i += 1

    #last addr ~ end
    size = max_addr - long(vm_end[i], 16)
    sz_list.append(hex(size))

    return sz_list

def draw_pic(vm_start, vm_end, sz_list, free_list, max_addr, owner_list):
    print(GREEN_BLOCK + ' 0x0 \t None')
    print_green(free_list[0])

    i = 0
    while i < len(vm_start):
        print(RED_BLOCK + ' 0x' + vm_start[i] + '\t' + owner_list[i])
        print_red(sz_list[i])
        if free_list[i+1] != '0x0L':
            print(GREEN_BLOCK + ' 0x' + vm_end[i] + '\t None')
            print_green(free_list[i+1])
        i += 1

    print(RED_BLOCK + ' ' + hex(max_addr))
    return

def show_help(vm_start, vm_end, sz_list, free_list, max_addr, owner_list, params):
    print(USAGE_EXAMPLE)
    return

def show_avaliable_block(vm_start, vm_end, sz_list, free_list, max_addr, owner_list, params):
    if free_list[0] != '0x0L':
        print(GREEN_BLOCK + ' 0x0')
        print_green(free_list[0])
        print(GREEN_BLOCK + ' 0x' + vm_start[1])
        print('')

    i = 1
    while i < len(free_list) - 1:
        if free_list[i] != '0x0L':
            print(GREEN_BLOCK + ' 0x' + vm_end[i-1])
            print_green(free_list[i])
            print(GREEN_BLOCK + ' 0x' + vm_start[i])
            print('')
        i += 1

    if free_list[-1] != '0x0L':
        print(GREEN_BLOCK + ' 0x' + vm_end[i-1])
        print_green(free_list[-1])
        print(GREEN_BLOCK + ' ' + hex(max_addr))
        print('')

def show_blocks_bigger_than_size(vm_start, vm_end, sz_list, free_list, max_addr, owner_list, params):
    given_size = int(params[1], 16) if '0x' in params[1] else int(params[1])

    if free_list[0] != '0x0L' and long(free_list[0], 16) > given_size:
        print(GREEN_BLOCK + ' 0x0')
        print_green(free_list[0])
        print(GREEN_BLOCK + ' 0x' + vm_start[1])
        print('')

    i = 1
    while i < len(free_list) - 1:
        if free_list[i] != '0x0L' and long(free_list[i], 16) > given_size:
            print(GREEN_BLOCK + ' 0x' + vm_end[i-1])
            print_green(free_list[i])
            print(GREEN_BLOCK + ' 0x' + vm_start[i])
            print('')
        i += 1

    if free_list[-1] != '0x0L' and long(free_list[-1], 16) > given_size:
        print(GREEN_BLOCK + ' 0x' + vm_end[i-1])
        print_green(free_list[-1])
        print(GREEN_BLOCK + ' ' + hex(max_addr))
        print('')

def filter_owner_with_key(vm_start, vm_end, sz_list, free_list, max_addr, owner_list, params):
    i = 1
    while i < len(owner_list):
        if params[1] in owner_list[i]:
            print(RED_BLOCK + ' 0x' + vm_start[i] + '\t' + owner_list[i])
            print_red(sz_list[i])
            print(RED_BLOCK + ' 0x' + vm_end[i])
            print('')
        i += 1

    return

ACTION_MAPS = {
    '-h' : show_help,
    '-f' : show_avaliable_block,
    '-b' : show_blocks_bigger_than_size,
    '-k' : filter_owner_with_key
}

def _main():
    params_list = sys.argv[1:]
    if '-l' in params_list:
        i = params_list.index('-l')
        long_bit = float(params_list[i + 1])
        del params_list[i + 1]
        del params_list[i]
        #print(params_list)
    else:
        long_bit = LONG_BIT

    #print(LONG_BIT)

    max_addr = long(math.pow(2, long_bit)) - 1
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