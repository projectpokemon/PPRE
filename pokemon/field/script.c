
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
            while(1){
                // 0x3e7ae
                r0 = r4->buf_ptr;
                if(r0 != 0){
                    r1 = get_command(r4);
                    r0 = r4->command_count;
                    if(r1 >= r0){
                        // 0x3e7d2
                        r2 = r4->command_table; // script table offset
                        r1 = r2[r1*4];
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
