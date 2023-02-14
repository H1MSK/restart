# Interface connections
| Interface |              Function               |
| :-------: | :---------------------------------: |
| M AXI GP0 |      Controls S_AxiLite of ips      |
| S AXI HP0 |  Bus for forward and param loader   |
| S AXI HP1 | Bus for backward and grad extractor |
|   EMIO    |       Individual controllers        |

## EMIO connections
| Port  | Direction |          Function          | Interrupt |
| :---: | :-------: | :------------------------: | :-------: |
|       |           |                            |           |
| 0x00  |    Out    |      start of forward      |    --     |
| 0x01  |    Out    |    complete of forward     |    --     |
| 0x02  |    In     |    end flag of forward     |    up     |
| 0x03  |    In     |     ap_idle of forward     |   down    |
|       |           |                            |           |
| 0x04  |    Out    |     start of backward      |    --     |
| 0x05  |    Out    |    complete of backward    |    --     |
| 0x06  |    In     |    end flag of backward    |    up     |
| 0x07  |    In     |    ap_idle of backward     |   down    |
|       |           |                            |           |
| 0x08  |    Out    |   start of param loader    |    --     |
| 0x09  |    Out    |  complete of param loader  |    --     |
| 0x0a  |    In     |  end flag of param loader  |    up     |
| 0x0b  |    In     |  ap_idle of param loader   |   down    |
|       |           |                            |           |
| 0x0c  |    Out    |  start of grad extractor   |    --     |
| 0x0d  |    Out    | complete of grad extractor |    --     |
| 0x0e  |    In     | end flag of grad extractor |    up     |
| 0x0f  |    In     | ap_idle of grad extractor  |   down    |
|       |           |                            |           |
| 0x10  |    Out    |   1 to reset param bram    |    --     |
| 0x11  |    In     |   param bram reset busy    |   down    |
|       |           |                            |           |
| 0x14  |    Out    |    1 to reset grad bram    |    --     |
| 0x15  |    In     |    grad bram reset busy    |   down    |
|       |           |                            |           |
| 0x18  |    Out    |          cache_en          |    --     |
| 0x19  |    Out    |          bram_sel          |    --     |
