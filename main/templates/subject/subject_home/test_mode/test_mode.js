{%if session.parameter_set.test_mode%}

do_test_mode: function do_test_mode(){

    if(worker) worker.terminate();

    {%if DEBUG%}
    console.log("Do Test Mode");
    {%endif%}

    if(app.end_game_modal_visible && app.test_mode)
    {
        if(app.session_player.name == "")
        {
            Vue.nextTick(() => {
                app.session_player.name = app.random_string(5, 20);
                app.session_player.student_id =  app.random_number(1000, 10000);

                app.send_name();
            })
        }

        return;
    }

    if(app.session.started &&
       app.test_mode
       )
    {
        
        switch (app.session.world_state.current_experiment_phase)
        {
            case "Instructions":
                app.do_test_mode_instructions();
                break;
            case "Run":
                app.do_test_mode_run();
                break;
            
        }        
       
    }

    // setTimeout(app.do_test_mode, app.random_number(1000 , 1500));
    worker = new Worker("/static/js/worker_test_mode.js");

    worker.onmessage = function (evt) {   
        app.do_test_mode();
    };

    worker.postMessage(0);
},

/**
 * test during instruction phase
 */
do_test_mode_instructions: function do_test_mode_instructions()
 {
    if(app.session_player.instructions_finished) return;
    if(app.working) return;
    
   
    if(app.session_player.current_instruction == app.session_player.current_instruction_complete)
    {

        if(app.session_player.current_instruction == app.instructions.instruction_pages.length)
            document.getElementById("instructions_start_id").click();
        else
            document.getElementById("instructions_next_id").click();

    }else
    {
        //take action if needed to complete page
        switch (app.session_player.current_instruction)
        {
            case app.instructions.action_page_1:
                app.test_mode_move_range();
                break;
            case app.instructions.action_page_2:              
                app.test_mode_submit_range();  
                break;
        }   
    }

    
 },

/**
 * test during run phase
 */
do_test_mode_run: function do_test_mode_run()
{
    //do chat
    let go = true;

    if(go)
        if(app.chat_text != "")
        {
            if(!app.show_chat())
            {
                app.chat_text = "";
                go = false;
            }
            else
            {
                try{
                    document.getElementById("send_chat_id").click();
                    go=false;
                }catch(e){
                   // console.log(e);
                }
            }
        }
    
    if(app.session.world_state.finished) return;
        
    if(go)
        switch (app.random_number(1, 4)){
            case 1:
                app.do_test_mode_chat();
                break;            
            case 2:                
                app.test_mode_send_cents();
                break;
            case 3:
                app.test_mode_move_range();
                break;
            case 4:
                app.test_mode_submit_range();
                break;
        }
},

/**
 * test mode chat
 */
do_test_mode_chat: function do_test_mode_chat(){
    if(!app.show_chat()) return;
    if(app.working) return;

    app.chat_text = app.random_string(5, 20);
},

/**
 * test mode move range
 */
test_mode_move_range: function test_mode_move_range()
{
    if(app.random_number(1, 2) == 1)
    {
        app.pixi_left_handle_pointerdown(null);
        app.pixi_left_handle_drag(app.random_number(0, axis_width));
        app.pixi_container_main_pointerup(null);
    }
    else
    {
        app.pixi_right_handle_pointerdown(null);
        app.pixi_right_handle_drag(app.random_number(0, axis_width));
        app.pixi_container_main_pointerup(null);
    }    
},

/**
 * test mode move submit range
 */
test_mode_submit_range: function test_mode_submit_range()
{
    if(app.working) return;

    if(!app.show_contest_controls()) return;

    app.send_range();
},

/**
 * test mode send cents
 */
test_mode_send_cents: function test_mode_send_cents()
{
    if(app.working) return;

    if(!app.show_transfer_cents()) return;

    app.send_cents_amount = app.random_number(1, 10);
    app.send_cents_to = app.send_cents_to_group[app.random_number(0, app.send_cents_to_group.length - 1)].value;

    app.send_cents();
},
{%endif%}