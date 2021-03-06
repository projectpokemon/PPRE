
#include <stdio.h>

int xorstream(FILE *handle1, FILE *handle2, FILE *out) {
  const size_t BLOCK_READ_SIZE = 0x100000;
  char buffer1[BLOCK_READ_SIZE], buffer2[BLOCK_READ_SIZE], out_buffer[BLOCK_READ_SIZE];
  size_t read1, read2, read_both;
  int c;

  do {
    read1 = fread(buffer1, sizeof(char), BLOCK_READ_SIZE, handle1);
    read2 = fread(buffer2, sizeof(char), BLOCK_READ_SIZE, handle2);
    read_both = read1 < read2 ? read1 : read2;
    for(c = 0; c < read_both; ++c) {
      out_buffer[c] = buffer1[c] ^ buffer2[c];
    }
    fwrite(out_buffer, sizeof(char), read_both, out);
  } while(read1 == BLOCK_READ_SIZE && read2 == BLOCK_READ_SIZE);

  return 0;
}

