module ap_controller(
    input ap_clk,
    input ap_rst_n,

    input start_trig,
    input complete_trig,
    output reg finish,
    output idle,

    output ap_start,
    input ap_ready,
    input ap_done,
    input ap_idle);

    reg start;
    /**
     * Finish: flag when a task finishes and the controller doesn't claim it
     * - ap_done: flag when the task finishs
     * - complete_trig: controller claim the task
     *
     * Start: ap_start signal, said in doc to keep high until ap_ready=1
     * - finish: flag of last task, stop start from 0->1
     * - trig: start a new task, ignore when finish=1
     * - ap_ready: end of current task, make start 1->0 if trig not function
     *
     */
    wire next_finish = ap_done | (finish & ~complete_trig);
    always @(posedge ap_clk) begin
        if (~ap_rst_n) begin
            finish <= 0;
        end else begin
            finish <= next_finish;
        end
    end

    wire next_start = (start_trig & ~finish) | (start & ~ap_ready);
    always @(posedge ap_clk) begin
        if (~ap_rst_n) begin
            start <= 0;
        end else begin
            start <= next_start;
        end
    end

    assign idle = ap_idle & ~finish;
    assign ap_start = next_start;

endmodule
