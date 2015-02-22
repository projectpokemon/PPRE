
// Platinum offsets

typedef int (*func_t)(int, int, int, int);

struct script_state {
    unsigned char u0;
    // 0x1
    unsigned char ret;
    unsigned char u2, u3;
    // 0x4
    int *command; // used when ret == 2
    // 0x8
    int *buf_ptr;
    unsigned char u4[0x50];
    // 0x5c
    int *command_table;
    // 0x60
    int command_count;
    // 0x64
    int vals[0x14]; // unknown length and purpose
    // 0x78
    int u78;
    int u7c; // pad
    // 0x80
    int u5;
};

int script_handler(int r0, int r1, int r2, int r3){
    script_state *r4;

    r4 = (script_state*)r0;
    r1 = r4->ret;
    if(r1 != 0){
        if(r1 == 0){
            return 0;
        }
        if(r1 == 1 || r1 == 2){
            if(r1 == 2){
                // 0x3e796
                r1 = r4->command;
                if(r1 == 0){
                    r4->ret = 1;
                }else{
                    r0 = (*r1)((script_state*)r0); // switch/exec
                    if(r0 != 1){
                        return 1;
                    }
                    r4->ret = 1;
                    return 1;
                }
            }
            while(r4->buf_ptr){
                // 0x3e7ae
                r1 = get_command(r4);
                r0 = r4->command_count;
                if(r1 >= r0){
                    // 0x3e7d2
                    r2 = r4->command_table; // script table offset
                    r1 = r2[r1];
                    r0 = (*r1)(r4); // switch/exec
                    if(r0 == 1){
                        return 1;
                    }
                }else{
                    func_22974(r0);
                    r4->ret = 0;
                    return 0;
                }
            }
            r4->ret = 0;
            return 0;
        }
        return 1;
    }

    return 0;
}


int get_command(script_state *r0) {
    // 0x3e838
    int r1 = r0->buf_ptr;
    int r3 = r1+1;
    r0->buf_ptr = r3;
    unsigned char r2 = ((unsigned char*)r1)[0];
    r1 = r3+1;
    r0->buf_ptr = r1;
    r0 = ((unsigned char*)r3)[0];
    r0 <<= 8;
    r0 += r2;
    return r0 & 0xFFFF;
}

int read16(script_state *r0) {
    // 0x38c30
    int r1 = r0->buf_ptr;
    int r3 = r1+1;
    r0->buf_ptr = r3;
    unsigned char r2 = ((unsigned char*)r1)[0];
    r1 = r3+1;
    r0->buf_ptr = r1;
    r0 = ((unsigned char*)r3)[0];
    r0 <<= 8;
    r0 += r2;
    return r0 & 0xFFFF;
}

// Diamond commands (some for reference)

int cmd_0000(script_state *r0) {
    return 0;
}

int cmd_0001(script_state *r0) {
    return 0;
}

int cmd_0002(script_state *r0) {
    r0->ret = 0;
    r0->buf_ptr = 0;
    return 0;
}

int func_394b8(int r0, int r1){
    int r5 = r0;
    r0 = ((int*)r5)[12];
    int r4 = r1;
    func_462ac(r0, r1);
    r1 = 1<<14;
    if(r4 < r1){
        r1 <<= 1;
        // TODO
    }else{
        return 0;
    }
}

int cmd_0003(script_state *r0) {
    script_state *r5 = r0;
    int r6 = r5->u5;
    int r7 = read16(r5);
    int r4 = read16(r5);
    r0 = func_394b8(r6, r4);
    ((uint16_t *)r0)[0] = r7;
    int r1 = 0x020399e9;
    r5->vals[0] = r4;
    r5->ret = 2;
    r5->command = r1;
    return 1;
}

int func_399e9(script_state *r0) {
    int r1 = r0->vals[0];
    r1 &= 0xFFFF;
    int r0 = r0->u5;
    r0 = func_394b8(r0, r1);
    r1 = r0;
    ((uint16_t *)r0)[0] = r0-1;
    if(r0 != 1){
        return 0;
    }else{
        return 1;
    }
}

int cmd_0004(script_state *r0) {
    int r3 = *((unsigned char*)(r0->buf_ptr++));
    int r2 = *((unsigned char*)(r0->buf_ptr++));
    int r1 = r3 << 2;
    r0->vals[r1] = r2;
    return 0;
}

int func_462e4(int r0, int r1){
    int r4 = r1;
    r0 = func_46338(r0, r1);
    if(r0 == 0){
        return 0;
    }
    int r5 = r4 >> 31;
    int r3 = r4 << 29;
    r3 = r3-r5;
    int r2 = 29;
}

int func_462ac(int r0, int r1){
    func_t r3 = 0x02022611;
    r1 = 4;
    // r0 = r3(r0, 4);
    // 0x02022611
    int r4 = r1;
    int r5 = r0;
    if(r4 < 0x24){
        r0 = 0x85 << 2;
        int r2 = r5+r0;
        r0 = r4 << 4;
        r1 = r5+r0; // r1 = arg0+(arg1 << 4);
        r0 = 0x0002022c;
        r0 = *(r1+r0);
        return r2 + r0;
    }else{
        // 0x20c2c
        r0 = func_31810(r0);
        if(r0 == 0){
            return 0;
        }
        r0 = func_cd374(r0);
        if(r0 == 18){
            return 18;
        }
        return func_8a9b8(r0);
    }
}

int func_3953c(int r0, int r1){
    int r5 = r0;
    r0 = ((int*)r5)[12];
    int r4 = r1;
    r0 = func_462ac(r0, r1);
    r1 = r4;
    r0 = func_462e4(r0, r1);
    return r0;
}

int func_39550(int r0, int r1){
    int r5 = r0;
    r0 = ((int*)r5)[12];
    int r4 = r1;
    r0 = func_462ac(r0, r1);
    r1 = r4;
    r0 = func_4630c(r0, r1);
    return r0;
}

int cmd_0030(script_state *r0){
    // 0x39e39 - Setflag($1)
    int r4 = r0->u5;
    int r1 = read16(r0);
    int r0 = func_3953c(r4, r1);
    return 0;
}

int cmd_0031(script_state *r0){
    // 0x39e50 - Clearflag($1)
    int r4 = r0->u5;
    int r1 = read16(r0);
    int r0 = func_39550(r4, r1);
    return 0;
}

int cmd_0040(script_state *r0){
    // 0x39fb9 - Setvar($1, $2)
    script_state* r4 = r0;
    int r1 = read16(r0);
    int r0 = r0->u5;
    int r5 = func_394b8(r0, r1);
    script_state* r0 = r4;
    int r0 = read16(r0);
    ((uint16_t *)r5)[0] = (uint16_t)r0;
    return 0;
}

int cmd_0041(script_state *r0){
    // 0x39fdd - Copyvar($1, $2)
    script_state* r5 = r0;
    int r1 = read16(r0);
    int r0 = r0->u5;
    int r4 = func_394b8(r0, r1);
    script_state* r0 = r5;
    int r1 = read16(r0);
    int r0 = r0->u5;
    int r0 = func_394b8(r0, r1);
    ((uint16_t *)r4)[0] = ((uint16_t *)r0)[0];
    return 0;
}

int cmd_0042(script_state *r0){
    // 0x3a00d - 002A($1, $2)
    script_state* r4 = r0;
    int r1 = read16(r0);
    int r0 = r4->u5;
    r0 = func_394b8(r0, r1);
    int r5 = func_39550(r4, r1);
    script_state* r0 = r4;
    r1 = read16(r0);
    int r0 = r0->u5;
    r0 = func_394f0(r0, r1);
    ((uint16_t *)r5)[0] = (uint16_t)r0;
    return 0;
}

int cmd_0043(script_state *r0){
    // 0x3a039 - Message2($1)
    int r2 = *((unsigned char*)(r0->buf_ptr++));
    int r1 = r0->u78;
    func_1e2c24(r0, r1);
    return 0;
}

int cmd_0044(script_state *r0){
    // 0x3a2c4 - Message($1)
    int r3 = 1;
    int r2 = *((unsigned char*)(r0->buf_ptr++));
    int r1 = r0->u78;
    func_1e2bd0(r0, r1);
    func_38b5c(r0, 0x203a2f1);
    return 1;
}

