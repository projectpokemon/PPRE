#ifndef _POKEMON_PERSONAL_H
#define _POKEMON_PERSONAL_H

#include <ppre.h>

#define STRUCT_STATS(t) struct {\
    t hp;\
    t attack;\
    t defense;\
    t speed;\
    t spatk;\
    t spdef;\
}

STRUCT_VERSION(personal, dp) {
    STRUCT_STATS(uint8) base_stats;
    uint8 types[2];
    uint8 catchrate;
    uint8 baseexp;
    uint16 evs;
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
