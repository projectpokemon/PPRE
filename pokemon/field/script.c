
// Platinum offsets

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
    int vals[0x1C]; // unknown length and purpose
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
    func_462ac(r0);
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

int cmd_0004(script_state *r0) {
    int r3 = *((unsigned char*)(r0->buf_ptr++));
    int r2 = *((unsigned char*)(r0->buf_ptr++));
    int r1 = r3 << 2;
    r0->vals[r1] = r2;
    return 0;
}


