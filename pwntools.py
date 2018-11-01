#-------------------------------------------------------------------------------
# Name:        模块1
# Purpose:
#
# Author:      w00344136
#
# Created:     27/04/2018
# Copyright:   (c) w00344136 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------
# pop rdi; ret ==> p64(pop_ret_addr) + p64(binsh_addr) + p64(system_addr)
# pop rax ; pop rdi ; call rax  => p64(pop_pop_call_addr) + p64(system_addr) + p64(binsh_addr)
def main():
    pass

if __name__ == '__main__':
    main()


from pwn import *
context(os='linux', arch='amd64/i386', log_level='debug')
r = remote('exploitme.example.com', 31337)
r = process("./test")

r.send()
r.interactive()
p32(),p64() #打包一个整数,分别打包为32或64位
u32(),u64() #解包一个字符串,得到整数
log.info(some_str)#

cyclic(0x100) # 生成一个0x100大小的pattern，即一个特殊的y符串
cyclic_find(0x61616161) # 找到该数据在pattern中的位置
cyclic_find('aaaa') # 查找位置也可以使用字符串去定位

def leak(address):
    data = p.read(address, 4)
    log.debug("%#x => %s" % (address, (data or '').encode('hex')))
    return data
main   = 0xfeedf4ce
d = DynELF(leak, main, elf=ELF('./pwnme'))
assert d.lookup(None,     'libc') == libc  #base address
assert d.lookup('system', 'libc') == system

p.sendlineafter('WANT PLAY[Y/N]\n', 'Y')
p.sendlineafter('GET YOUR NAME:\n\n', name)
p.recvuntil('WELCOME \n')
content = p.recvuntil('GET YOUR ', drop=True)
p.sendafter('AGE:\n\n', age)
p.sendline('Y',timeout=1)
r.recvuntil('\n')
r.recv(numb = 2048, timeout = dufault)  接受数据，numb指定接收的字节，timeout指定超时
r.recvline(keepends=True)  接受一行数据，keepends为是否保留行尾的\n
r.recvall()  一直接收直到EOF
r.recvrepeat(timeout = default)  持续接受直到EOF或timeout
r.sendline(payload)
r.interactive()  直接进行交互，相当于回到shell的模式，在取得shell之后使用
info = r.recv().splitlines()[1]

asm("xor eax,eax")

l = listen()
r = remote('localhost', l.lport)
c = l.wait_for_connection()
r.send('hello')
c.recv()

e = ELF('/bin/cat')
hex(e.address)  # 文件装载的基地址
hex(e.symbols['write']) # 函数地址
hex(e.got['write']) # GOT表的地址
hex(e.plt['write']) # PLT的地址

Shellcode生成器
print shellcraft.i386.nop().strip('\n')
print shellcraft.i386.linux.sh()

ROP链生成器
elf = ELF('ropasaurusrex') 
rop = ROP(elf) 
rop.read(0, elf.bss(0x80)) 
rop.dump() 
str(rop)

fmtstr_payload(offset,{key:value}) 用来生成格式化字符串漏洞写内存的payload.offset偏移，往key的地址，写入value的值

