# -*- coding: utf-8 -*-
import sys


class VComputer(object):
    '''
    有一台假想的计算机，页大小（page size）为32 Bytes，支持32KB的虚拟地址空间（virtual address space）,
    有4KB的物理内存空间（physical memory），采用二级页表，一个页目录项（page directory entry ，PDE）大小为1 Byte,
    一个页表项（page-table entries PTEs）大小为1 Byte，1个页目录表大小为32 Bytes，1个页表大小为32 Bytes。
    页目录基址寄存器（page directory base register，PDBR）保存了页目录表的物理地址（按页对齐）），其值为0x220（十进制为544）.
    '''

    def __init__(self):
        self.pages = []
        self.disks = []
        self.PT1 = self.PT2 = self.PG = self.DISKSEC = 5
        self.PDBR = 0xd80

    def loadmem(self, memfilename):
        self.pages = self.__load(memfilename)

    def loaddisk(self, diskfilename):
        self.disks = self.__load(diskfilename)

    def __load(self, filename):
        temp = []
        with open(filename, 'r') as memf:
            lines = memf.readlines()
            for line in lines:
                page = map(lambda hexn: int(hexn, 16), line.rstrip('\r\n').split()[2:])
                temp += page
        return temp

    def addrtrans(self, vaddr):
        pt1, pt2, pg = self.__analyze_vaddr(vaddr)
        pdevalid, pde = self.__analyze_entry(self.pages[self.PDBR + pt1])
        ptevalid, pte = self.__analyze_entry(self.pages[(pde << self.PT2) + pt2])
        phyaddr = (pte << self.PG) + pg
        if ptevalid == 1:
            data = self.pages[phyaddr]
        elif pte != 0x7f:
            data = self.disks[phyaddr]

        resstr = '''Virtual Address %s:
    --> pde index:%s  pde contents:(valid %s, pfn %s)''' % (hex(vaddr), hex(pt1), pdevalid, hex(pde))
        if pdevalid == 0:
            resstr += '''
        --> Fault (page directory entry not valid)'''
        else:
            resstr += '''
        --> pte index:%s  pte contents:(valid %s, pfn %s)''' % (hex(pt2), ptevalid, hex(pte))
            if pte == 0x7f:
                resstr += '''
            --> Fault (page table entry not valid)'''
            elif ptevalid == 0:
                resstr += '''
            --> To Disk Sector Address %s --> Value: %s''' % (hex(phyaddr), hex(data))
            else:
                resstr += '''
            --> To Physical Address %s --> Value: %s''' % (hex(phyaddr), hex(data))
        print resstr

    def __analyze_vaddr(self, vaddr):
        pt1 = (vaddr >> (self.PT2 + self.PG)) & ((1 << self.PT1) - 1)
        pt2 = (vaddr >> (self.PG)) & ((1 << self.PT2) - 1)
        pg = vaddr & ((1 << self.PG) - 1)
        return pt1, pt2, pg

    def __analyze_entry(self, entry):
        return ((entry >> 7) & 1), (entry & 0x7F)


if __name__ == '__main__':
    memfilename = sys.argv[1]
    diskfilename = sys.argv[2]
    vaddrs = map(lambda x: int(x, 16), sys.argv[3:])
    vcomputer = VComputer()
    vcomputer.loadmem(memfilename)
    vcomputer.loaddisk(diskfilename)
    for vaddr in vaddrs:
        vcomputer.addrtrans(vaddr)
