#include "global.hpp"
#include "net/net.hpp"

using CriticNetType = Sequence<Linear<OBS_DIM, HIDDEN_WIDTH>,
                               Tanh<HIDDEN_WIDTH>,
                               Linear<HIDDEN_WIDTH, HIDDEN_WIDTH>,
                               Tanh<HIDDEN_WIDTH>,
                               Linear<HIDDEN_WIDTH, 1> >;

#if ACT_CONTINUOUS
using ActorNetType = Sequence<
    Linear<OBS_DIM, HIDDEN_WIDTH>,
    Tanh<HIDDEN_WIDTH>,
    Linear<HIDDEN_WIDTH, HIDDEN_WIDTH>,
    Tanh<HIDDEN_WIDTH>,
    ForkJoin<Linear<HIDDEN_WIDTH, ACT_DIM>,
             Sequence<Linear<HIDDEN_WIDTH, ACT_DIM>, Exp<ACT_DIM> > > >;
#else
using ActorNetType = Sequence<Linear<OBS_DIM, HIDDEN_WIDTH>,
                              Tanh<HIDDEN_WIDTH>,
                              Linear<HIDDEN_WIDTH, HIDDEN_WIDTH>,
                              Tanh<HIDDEN_WIDTH>,
                              Linear<HIDDEN_WIDTH, ACT_DIM>,
                              Softmax<ACT_DIM> >;
#endif


template <typename NetType>
void forwardAndBackward(NetType& net,
						hls::stream<cm_float>& in_x,
						hls::stream<cm_float>& in_grad_y,
						hls::stream<cm_float>& out_y) {
#pragma HLS INTERFACE mode=ap_ctrl_chain port=return
//#pragma HLS DATAFLOW
    net.forward(in_x, out_y, true);
    net.backward(in_grad_y);
}

void actor_top(NN_OP op,
               hls::stream<cm_float>& in_param,
               hls::stream<cm_float>& out_grad,
               hls::stream<cm_float>& in_x,
               hls::stream<cm_float>& in_grad_y,
               hls::stream<cm_float>& out_y) {
#pragma HLS INTERFACE mode=ap_ctrl_chain port=return
#pragma HLS INTERFACE mode=s_axilite port=op
#pragma HLS INTERFACE mode=axis port=in_param register_mode=reverse
#pragma HLS INTERFACE mode=axis port=out_grad register_mode=forward
#pragma HLS INTERFACE mode=axis port=in_x register_mode=reverse
#pragma HLS INTERFACE mode=axis port=in_grad_y register_mode=reverse
#pragma HLS INTERFACE mode=axis port=out_y register_mode=forward
    static ActorNetType net;
    switch (op) {
        case NN_OP_LoadParam:
            net.loadParam(in_param);
            break;
        case NN_OP_DumpGradAndZero:
            net.dumpGradAndZero(out_grad);
            break;
        case NN_OP_Forward:
            net.forward(in_x, out_y, false);
            break;
        case NN_OP_ForwardAndBackward:
            net.forward(in_x, out_y, true);
            net.backward(in_grad_y);
        	break;
#ifndef __SYNTHESIS__
        case NN_OP_ForwardWithCache:
            net.forward(in_x, out_y, true);
            break;
        case NN_OP_Backward:
            net.backward(in_grad_y);
            break;
#endif
        default:
            break;
    }
}

void critic_top(NN_OP op,
                hls::stream<cm_float>& in_param,
                hls::stream<cm_float>& out_grad,
                hls::stream<cm_float>& in_x,
                hls::stream<cm_float>& in_grad_y,
                hls::stream<cm_float>& out_y) {
    static CriticNetType net;
    switch (op) {
        case NN_OP_LoadParam:
            net.loadParam(in_param);
            break;
        case NN_OP_DumpGradAndZero:
            net.dumpGradAndZero(out_grad);
            break;
        case NN_OP_Forward:
            net.forward(in_x, out_y, false);
            break;
        case NN_OP_ForwardAndBackward:
            net.forward(in_x, out_y, true);
            net.backward(in_grad_y);
        	break;
#ifndef __SYNTHESIS__
        case NN_OP_ForwardWithCache:
            net.forward(in_x, out_y, true);
            break;
        case NN_OP_Backward:
            net.backward(in_grad_y);
            break;
#endif
        default:
            break;
    }
}

CM_API void get_net_parameters(int* obs, int* act, int *hidden, int* aparam, int* cparam, int* act_continuous) {
    *obs = OBS_DIM;
    *act = ACT_DIM;
    *hidden = HIDDEN_WIDTH;
    *aparam = ActorNetType::param_size;
    *cparam = CriticNetType::param_size;
    *act_continuous = ACT_CONTINUOUS;
}

CM_API void actor_arr_top(NN_OP op,
                          cm_float* in_param,
                          cm_float* out_grad,
                          cm_float* in_x,
                          cm_float* in_grad_y,
                          cm_float* out_y) {
    static hls::stream<cm_float> s_in_param("actor_in_param");
    static hls::stream<cm_float> s_out_grad("actor_out_grad");
    static hls::stream<cm_float> s_in_x("actor_in_x");
    static hls::stream<cm_float> s_in_grad_y("actor_in_grad_y");
    static hls::stream<cm_float> s_out_y("actor_out_y");

    switch (op) {
        case NN_OP_LoadParam:
            for (int i = 0; i < ActorNetType::param_size; ++i)
                s_in_param << in_param[i];
            break;
        case NN_OP_DumpGradAndZero:
            break;
        case NN_OP_Forward:
            for (int i = 0; i < ActorNetType::in_size; ++i)
                s_in_x << in_x[i];
            break;
        case NN_OP_ForwardWithCache:
            for (int i = 0; i < ActorNetType::in_size; ++i)
                s_in_x << in_x[i];
            break;
        case NN_OP_Backward:
            for (int i = 0; i < ActorNetType::out_size; ++i)
                s_in_grad_y << in_grad_y[i];
            break;
        default:
            break;
    }

    actor_top(op, s_in_param, s_out_grad, s_in_x, s_in_grad_y, s_out_y);

    switch (op) {
        case NN_OP_LoadParam:
            break;
        case NN_OP_DumpGradAndZero:
            for (int i = 0; i < ActorNetType::param_size; ++i)
                s_out_grad >> out_grad[i];
            break;
        case NN_OP_Forward:
            for (int i = 0; i < ActorNetType::out_size; ++i)
                s_out_y >> out_y[i];
            break;
        case NN_OP_ForwardWithCache:
            for (int i = 0; i < ActorNetType::out_size; ++i)
                s_out_y >> out_y[i];
            break;
        case NN_OP_Backward:
            break;
        default:
            break;
    }
}

CM_API void critic_arr_top(NN_OP op,
                           cm_float* in_param,
                           cm_float* out_grad,
                           cm_float* in_x,
                           cm_float* in_grad_y,
                           cm_float* out_y) {
    static hls::stream<cm_float> s_in_param("critic_in_param");
    static hls::stream<cm_float> s_out_grad("critic_out_grad");
    static hls::stream<cm_float> s_in_x("critic_in_x");
    static hls::stream<cm_float> s_in_grad_y("critic_in_grad_y");
    static hls::stream<cm_float> s_out_y("critic_out_y");

    switch (op) {
        case NN_OP_LoadParam:
            for (int i = 0; i < CriticNetType::param_size; ++i)
                s_in_param << in_param[i];
            break;
        case NN_OP_DumpGradAndZero:
            break;
        case NN_OP_Forward:
            for (int i = 0; i < CriticNetType::in_size; ++i)
                s_in_x << in_x[i];
            break;
        case NN_OP_ForwardWithCache:
            for (int i = 0; i < CriticNetType::in_size; ++i)
                s_in_x << in_x[i];
            break;
        case NN_OP_Backward:
            for (int i = 0; i < CriticNetType::out_size; ++i)
                s_in_grad_y << in_grad_y[i];
            break;
        default:
            break;
    }

    critic_top(op, s_in_param, s_out_grad, s_in_x, s_in_grad_y, s_out_y);

    switch (op) {
        case NN_OP_LoadParam:
            break;
        case NN_OP_DumpGradAndZero:
            for (int i = 0; i < CriticNetType::param_size; ++i)
                s_out_grad >> out_grad[i];
            break;
        case NN_OP_Forward:
            for (int i = 0; i < CriticNetType::out_size; ++i)
                s_out_y >> out_y[i];
            break;
        case NN_OP_ForwardWithCache:
            for (int i = 0; i < CriticNetType::out_size; ++i)
                s_out_y >> out_y[i];
            break;
        case NN_OP_Backward:
            break;
        default:
            break;
    }
}
