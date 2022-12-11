#pragma once

#define OBS_DIM 376
#define ACT_DIM 16

enum NN_OP {
    NN_OP_None              = 0x00,
    NN_OP_LoadParam         = 0x01,
    NN_OP_DumpGradAndZero   = 0x02,
    NN_OP_Forward           = 0x10,
    NN_OP_ForwardWithCache  = 0x20,
    NN_OP_Backward          = 0x40,
};

using cm_float = float;
