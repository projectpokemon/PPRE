
typedef load_info_s load_info_t;

struct load_info_s{
    // 0x02000ba0
    int u0, u4, u8;
    int u0c, u10;
    struct compression_info_s{
        int beacon;
        load_info_t *load_info;
        int pad;
    } *compression; // compressed end
    int u18;
    int beacon;
    int unbeacon;  // reversed endian of beacon
};

int _start(){
    // 0x800 (rom 0x4800 @ ram 0x02000800)
    int r0;
    int ip = 0x4000000;  // r12
    *((char *)ip+0x208) = ip;
    do{
        r0 = *(ip+6);
    }while(r0 != 0);
    func_ab0();
    // CSPR_c = 19;
    int sp = 0x027e0000+0x3fc0;
    // CSPR_c = 18;
    r0 = 0x027e0000+0x3fc0;
    r0 -= 0x40;
    sp = r0-4;
    if(sp & 0x4){
        sp -= 4;
    }
    int r1 = 0x00000800;
    r1 = r0-r1;
    // CPSR_fsxc = 31
    sp = r1-4;
    func_954(0, 0x027e0000, 0x4000);
    func_954(0, 0x05000000, 0x400);
    func_954(0x200, 0x07000000, 0x400);
    load_info_s * r1 = (load_info_s *)0x02000ba0;
    blz_decompress(r1->compression);
    func_a1c();
}


void func_954(int r0, int r1, int r2){
    int ip = r1+r2;
    while(r1 < ip){
        *(r1++) = r0;
    }
    // msr      SP_hyp, lr, lsl pc
    return;
}

void func_970(int r0, int r1, int r2, int r3){
    int r5;
    int ip;
    if(r0 == 0){
        // 0xa18
        // msr  SP_hyp, lr, lsl pc
    }
    *(--r0) = r1;
    *(--r0) = r2;
    r2 = r0+r2;
    int r3 = r0-(r1<<24);
    r1 = r1 & ~0xff000000;
    r1 = r0-r1;
    int r4 = r2;
    do{
        if(r3 <= r1){
            break;
        }
        r5 = *((char*)r3--);
        int r6 = 8;
    }while((r6 -= 1) < 0);
    if(r5 & 0x80){
        // 0x9c0
    }
    // 0x9b4
    r0 = *((char*)r3--);
    *((char*)r2--) = r0;
    // 0x9e8
    ip = *((char*)r3--);
    int r7 = *((char*)r3--);
    r7 = r7 | (ip << 8);
    r7 = r7 & ~0xf000;
    r7 += 2;
    ip += 32;
    do{
        r0 = *((char*)r2+r7);
        *((char*)r2--) = r0;
    }while((ip -= 16) >= 0);
    r5 <<= 1;
    if(r3 > r1){}
}

void blz_decompress(int r0){
    // 0x970
    int r4, r5, r6, r7, ip;
    if(r0 == 0){
        return;
    }
    int r1 = *(r0-8); // 090b615a
    int r2 = *(r0-4); // 00057be4
    r2 += r0;
    int r3 = r0-(r1>>24);  // current end (compressed bottom)
    r1 &= ~0xff000000;
    r1 = r0-r1;  // stop address (top) ~ 41ba
    r4 = r2; // end (decompressed bottom)
    while(r3 > r1){
        r5 = *((char*)r3--);
        r6 = 8;
        while(--r6 >= 0){
            if(r5 & 0x80){
                ip = *((char*)r3--);
                r7 = *((char*)r3--);
                r7 |= ip << 8;
                r7 = r7 & ~0xf000;
                r7 += 2;
                ip += 32;
                do{
                    r0 = *((char*)r2+r7);
                    *((char*)r2--) = r0;
                }while((ip -= 16) >= 0);
            }else{
                r0 = *((char*)r3--);
                *((char*)r2--) = r0;
            }
            r5 <<= 1;
            if(r1 <= r3){
                break;
            }
        }
    }
    r0 = 0;
    r3 = r1 & ~0x1f;
    do{
        // mcr      15, 0, r0, cr7, cr10, {4}
        // mcr      15, 0, r3, cr7, cr5, {1}
        // mcr      15, 0, r3, cr7, cr14, {1}
        r3 += 32;
    }while(r3 < r4);
    return;
}
