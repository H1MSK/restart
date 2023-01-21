# Interface connections
| Interface |           Function           |
| :-------: | :--------------------------: |
| M AXI GP0 |  Controls S_AxiLite of ips   |
| S AXI HP0 | Reader of in_x and param_in  |
| S AXI HP1 | Writer of out_y and grad_out |
| S AXI HP2 |     Reader of in_grad_y      |
|   EMIO    |    Individual controllers    |

## EMIO connections
| Port  | Direction |          Function          | Interrupt |
| :---: | :-------: | :------------------------: | :-------: |
| 0x00  |    Out    |    ap_start of forward     |    --     |
| 0x01  |    In     |     ap_done of forward     |    up     |
| 0x02  |    In     |     ap_idle of forward     |    --     |
| 0x04  |    Out    |    ap_start of backward    |    --     |
| 0x05  |    In     |    ap_done of backward     |    up     |
| 0x06  |    In     |    ap_idle of backward     |    --     |
| 0x08  |    Out    |  ap_start of param loader  |    --     |
| 0x09  |    In     |  ap_done of param loader   |    up     |
| 0x0a  |    In     |  ap_idle of param loader   |    --     |
| 0x0c  |    Out    | ap_start of grad extractor |    --     |
| 0x0d  |    In     | ap_done of grad extractor  |    up     |
| 0x0e  |    In     | ap_idle of grad extractor  |    --     |
| 0x10  |    Out    |   1 to reset param bram    |    --     |
| 0x11  |    In     |   param bram reset busy    |   down    |
| 0x14  |    Out    |    1 to reset grad bram    |    --     |
| 0x15  |    In     |    grad bram reset busy    |   down    |
