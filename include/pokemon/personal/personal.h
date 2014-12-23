#ifndef _POKEMON_PERSONAL_H
#define _POKEMON_PERSONAL_H

#include <ppre.h>

#define STRUCT_STATS(width) struct {\
    uint hp : width;\
    uint attack : width;\
    uint defense : width;\
    uint speed : width;\
    uint spatk : width;\
    uint spdef : width;\
}

STRUCT_VERSION(personal, dp) {
    STRUCT_STATS(8) base_stats;
    uint8 types[2];
    uint8 catchrate;
    uint8 baseexp;
    STRUCT_STATS(2) evs;
    uint16 items[2];
    uint8 gender;
    uint8 hatchcycles;
    uint8 basehappiness;
    uint8 growth;
    uint8 egggroups[2];
    uint8 abilities[2];
    uint8 flag;
    uint8 color;
    uint8 tms[13];
};

#endif /* _POKEMON_PERSONAL_H */
