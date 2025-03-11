
{% load static %}

"use strict";

axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
axios.defaults.xsrfCookieName = "csrftoken";

//global letiables
let subject_status_overlay = {container:null, current_period_label:null, time_remaining_label:null, profit_label:null};
let pixi_target = null;                        //target sprite for your avatar
let pixi_mini_map = {container:null};               //mini map container
let pixi_notices = {container:null, notices:{}};                         //notices
let pixi_notices_key = 0;

let selection_handle = null;                             //the currently selected handle

let last_location_update = Date.now();          //last time location was updated

//prevent right click
document.addEventListener('contextmenu', event => event.preventDefault());

let worker = null;

{%include "subject/subject_home/the_stage/pixi_globals.js"%}

//vue app
let app = Vue.createApp({
    delimiters: ["[[", "]]"],

    data() {return {chat_socket : "",
                    reconnecting : true,
                    help_text : "Loading ...",
                    is_subject : true,
                    working : false,
                    reconnection_count : 0,
                    first_load_done : false,                       //true after software is loaded for the first time
                    player_key : "{{session_player.player_key}}",
                    session_player : null, 
                    session : null,
                    website_instance_id : "{{website_instance_id}}",
                    pixi_tick_tock : {value:"tick", time:Date.now()}, //tick tock

                    form_ids: {{form_ids|safe}},

                    chat_text : "",
                    chat_button_label : "Chat",
                    chat_history : {{session_player.chat_display_history|safe}},
                    chat_header : "Chat",

                    send_cents_amount : 0,
                    send_cents_to : null,
                    send_cents_to_group : [],
                    send_cents_button_text : "Transfer",
                    send_cents_error : null,
                    send_cents_success : false,                        //if true show success check mark for sending cents

                    end_game_modal_visible : false,

                    instructions : {{instructions|safe}},
                    instruction_pages_show_scroll : false,

                    current_selection_range : {start:null, end:null},    //the current selection range
                    range_update_success : false,                        //if true show success check mark for updating range
                    show_range_update_button : true,                     //if true show update button

                    notices_seen: [],

                    // modals
                    end_game_modal : null,
                    help_modal : null,
                    test_mode : {%if session.parameter_set.test_mode%}true{%else%}false{%endif%},

                    //pixi
                    canvas_width  : null,
                    canvas_height : null,
                    move_speed : 5,
                    animation_speed : 0.5,
                    scroll_speed : 10,
                    pixi_mode : "subject",
                    pixi_scale : 1,
                    stage_width : 10000,
                    stage_height : 10000,
                    scroll_direction : {x:0, y:0},
                    draw_bounding_boxes: false,

                    //forms
                    interaction_form : {direction:null, amount:null},

                    //test mode
                    test_mode_location_target : null,

                    //errors
                    interaction_start_error: null,
                    interaction_error: null,
                    range_update_error: null,

                    //open modals
                    interaction_start_modal_open : false,
                }},
    methods: {

        /** fire when websocket connects to server
        */
        handle_socket_connected: function handle_socket_connected(){            
            app.send_get_session();
            app.working = false;
        },

        /** fire trys to connect to server
         * return true if re-connect should be allowed else false
        */
        handle_socket_connection_try: function handle_socket_connection_try(){            
            if(!app.session) return true;

            app.reconnection_count+=1;

            if(app.reconnection_count > app.session.parameter_set.reconnection_limit)
            {
                app.reconnection_failed = true;
                app.check_in_error_message = "Refresh your browser."
                return false;
            }

            return true;
        },

        /** take websocket message from server
        *    @param data {json} incoming data from server, contains message and message type
        */
        take_message: function take_message(data) {

            {%if DEBUG%}
            console.log(data);
            {%endif%}

            let message_type = data.message.message_type;
            let message_data = data.message.message_data;

            switch(message_type) {                
                case "get_session":
                    app.take_get_session(message_data);
                    break; 
                case "help_doc_subject":
                    app.take_load_help_doc_subject(message_data);
                    break;
                case "update_start_experiment":
                    app.take_update_start_experiment(message_data);
                    break;
                case "update_reset_experiment":
                    app.take_reset_experiment(message_data);
                    break;
                case "update_chat":
                    app.take_update_chat(message_data);
                    break;
                case "update_time":
                    app.take_update_time(message_data);
                    break;
                case "name":
                    app.take_name(message_data);
                    break;
                case "update_next_phase":
                    app.take_update_next_phase(message_data);
                    break;
                case "next_instruction":
                    app.take_next_instruction(message_data);
                    break;
                case "finish_instructions":
                    app.take_finish_instructions(message_data);
                    break;
                case "update_refresh_screens":
                    app.take_refresh_screens(message_data);
                    break;
                case "update_rescue_subject":
                    app.take_rescue_subject(message_data);
                    break;
                case "update_range":
                    app.take_update_range(message_data);
                    break;
                case "update_cents":
                    app.take_update_cents(message_data);
                    break;
            }

            app.working = false;
        },

        /** send websocket message to server
        *    @param message_type {string} type of message sent to server
        *    @param message_text {json} body of message being sent to server
        */
        send_message: function send_message(message_type, message_text, message_target="self")
        {          
            app.chat_socket.send(JSON.stringify({
                    'message_type': message_type,
                    'message_text': message_text,
                    'message_target': message_target,
                }));
        },

        /**
         * do after session has loaded
        */
        do_first_load: function do_first_load()
        {           
            app.end_game_modal = bootstrap.Modal.getOrCreateInstance(document.getElementById('end_game_modal'), {keyboard: false})               
            app.help_modal = bootstrap.Modal.getOrCreateInstance(document.getElementById('help_modal'), {keyboard: false})
            
            document.getElementById('end_game_modal').addEventListener('hidden.bs.modal', app.hide_end_game_modal);

            {%if session.parameter_set.test_mode%} setTimeout(app.do_test_mode, app.random_number(1000 , 1500)); {%endif%}

            // if game is finished show modal
            if( app.session.world_state.current_experiment_phase == 'Names')
            {
                app.show_end_game_modal();
            }
            else if(app.session.world_state.current_experiment_phase == 'Done' && 
                    app.session.parameter_set.survey_required && 
                    !app.session_player.survey_complete)
            {
                window.location.replace(app.session_player.survey_link);
            }

            if(document.getElementById('instructions_frame_a'))
            {
                document.getElementById('instructions_frame_a').addEventListener('scroll',
                    function()
                    {
                        app.scroll_update();
                    },
                    false
                )

                app.scroll_update();
            }

            app.setup_pixi();                        
            app.first_load_done = true;
        },

        /**
         * after reconnection, load again
         */
        do_reload: function do_reload()
        {
            app.setup_main_container();

            app.setup_axis();
            app.setup_treatment();
            app.update_treatment();
            app.setup_selection_range();

            app.setup_group_summary();
            app.setup_control_handles();

            // app.update_left_handle_position();
            // app.update_right_handle_position();
        },

        /** send winsock request to get session info
        */
        send_get_session: function send_get_session(){
            app.send_message("get_session", {"player_key" : app.player_key});
        },
        
        /** take create new session
        *    @param message_data {json} session day in json format
        */
        take_get_session: function take_get_session(message_data){
    
            app.session = message_data.session;
            app.session_player = message_data.session_player;

            let world_state = app.session.world_state;

            if(app.session.started)
            {
                let session_period_id = world_state.session_periods_order[world_state.current_period-1];
                let session_period = app.session.session_periods[session_period_id];
                let parameter_set_periodblock = app.session.parameter_set.parameter_set_periodblocks[session_period.parameter_set_periodblock_id];
                let session_player = app.session.world_state.session_players[app.session_player.id];
                
                current_treatment = app.session.parameter_set.parameter_set_treatments[parameter_set_periodblock.parameter_set_treatment].id;
                
                app.update_group_order();               
            }
            else
            {
                return;
            } 
            
            if(app.session.world_state.current_experiment_phase != 'Done')
            {
                                
            }

            if(app.session.world_state.current_experiment_phase == 'Instructions')
            {
                //load instruction examples
                // for(let i=0;i<app.session.world_state.session_players_order.length;i++)
                // {
                //     let session_player_id = app.session.world_state.session_players_order[i];
                //     let session_player = app.session.world_state.session_players[session_player_id];

                //     let index = i+1;

                //     session_player.range_start = app.instructions["p" + index + "_example_start_range"];
                //     session_player.range_end = app.instructions["p" + index + "_example_end_range"];
                // }

                Vue.nextTick(() => {
                    app.process_instruction_page();
                    app.instruction_display_scroll();
                });
            }

            if(!app.first_load_done)
            {
                Vue.nextTick(() => {
                    app.do_first_load();
                });
            }
            else
            {
                Vue.nextTick(() => {
                    app.do_reload();
                });
            }

            //test code
            // let my_group = 1;
            // for(let i=0; i<20; i++)
            // {
            //     let random_number = app.random_number(0, app.session.world_state.groups[1].length-1);
            //     let chat = {session_player:app.session.world_state.groups[1][random_number], message:"talk " + i};
            //     app.chat_history.unshift(chat);
            // }
        },

        /**
         * put local player at the beginning of the group order
         */
        update_group_order: function update_group_order(){
            let current_period_block = app.session.world_state.current_period_block;
            let session_player = app.session.world_state.session_players[app.session_player.id];
            let parameter_set_player = app.session.parameter_set.parameter_set_players[session_player.parameter_set_player_id]; 

            current_group = session_player.group_number;
            let group = app.session.world_state.groups[current_group];

            //handled server side
            //move local player to front of group list 
            // let group = app.session.world_state.groups[current_group];
            // let index = group.indexOf(app.session_player.id);
            // if(index != -1)
            // {                    
            //     group.splice(index, 1);
            //     group.unshift(app.session_player.id);
            // }

            //add all players except local player to send cents group
            app.send_cents_to_group = [];
            for(let i in group)
            {
                if(group[i] != app.session_player.id)
                {
                    let parameter_set_player = app.session.parameter_set.parameter_set_players[app.session.world_state.session_players[group[i]].parameter_set_player_id];
                    let text=parameter_set_player.id_label;
                    let value=group[i];
                    app.send_cents_to_group.push({text:text, value:value});
                }
            }
            

            
        },

        /** update start status
        *    @param message_data {json} session day in json format
        */
        take_update_start_experiment:function take_update_start_experiment(message_data){
            app.take_get_session(message_data);
        },

        /** update reset status
        *    @param message_data {json} session day in json format
        */
        take_reset_experiment: function take_reset_experiment(message_data){
            app.take_get_session(message_data);

            app.end_game_modal.hide();        
            app.help_modal.hide();

            app.remove_all_notices();

            app.notices_seen = [];
            app.chat_history = [];

            app.show_range_update_button = true;
            app.range_update_success = false;
            app.send_cents_success = false;
        },

        /**
        * update time and start status
        */
        take_update_time: function take_update_time(message_data){
          
            let status = message_data.value;

            if(status == "fail") return;

            let period_change = false;
            let period_earnings = 0;

            let world_state = app.session.world_state;

            // if (message_data.period_is_over)
            // {
            //     period_earnings = message_data.earnings[app.session_player.id].period_earnings;
            //     app.session.world_state.session_players[app.session_player.id].earnings = message_data.earnings[app.session_player.id].total_earnings;
            // }

            app.session.started = message_data.started;

            world_state.current_period = message_data.current_period;
            world_state.current_round = message_data.current_round;
            world_state.time_remaining = message_data.time_remaining;
            world_state.timer_running = message_data.timer_running;
            world_state.started = message_data.started;
            world_state.finished = message_data.finished;
            world_state.current_experiment_phase = message_data.current_experiment_phase;
            world_state.session_players = message_data.session_players
            world_state.period_blocks = message_data.period_blocks;
            world_state.current_period_block = message_data.current_period_block;

            //pixi updates

            if(world_state.current_round == 1 && world_state.current_period > 1)
            {
                let session_period_id = world_state.session_periods_order[world_state.current_period-1];
                let session_period = app.session.session_periods[session_period_id];
                let parameter_set_periodblock = app.session.parameter_set.parameter_set_periodblocks[session_period.parameter_set_periodblock_id];
                let session_player = world_state.session_players[app.session_player.id];
                let period_block = world_state.period_blocks[world_state.current_period_block];
                
                app.current_selection_range.start = session_player.range_start;
                app.current_selection_range.end = session_player.range_end;

                current_treatment = app.session.parameter_set.parameter_set_treatments[parameter_set_periodblock.parameter_set_treatment].id;
                
                pixi_left_handle.alpha = 1;
                pixi_right_handle.alpha = 1;
                app.selection_handle = null;

                app.setup_main_container();
                
                app.setup_axis();
                app.setup_treatment();
                app.update_treatment();
                app.setup_selection_range();
                app.setup_control_handles();

                app.range_update_success = false;
                app.send_cents_success = false;
                

                //notice help pop up
                if(parameter_set_periodblock.help_doc && period_block.phase == 'start')
                {
                    app.send_load_help_doc_subject(parameter_set_periodblock.help_doc_title);
                }
            }
            else
            {
                app.update_treatment();
                app.setup_selection_range();
                app.setup_group_summary();                
            }

            //collect names
            if(app.session.world_state.current_experiment_phase == 'Names')
            {
                app.show_end_game_modal();
            }            

            Vue.nextTick(() => {
               
            });


            //update any notices on screen
            app.update_notices();

            app.show_range_update_button = true;

        },

        /**
         * show the end game modal
         */
        show_end_game_modal: function show_end_game_modal(){
            if(app.end_game_modal_visible) return;
   
            app.help_modal.hide();

            app.end_game_modal.toggle();

            app.end_game_modal_visible = true;
            app.working = false;
        },

        /** take refresh screen
         * @param messageData {json} result of update, either sucess or fail with errors
        */
        take_refresh_screens: function take_refresh_screens(message_data){
            if(message_data.value == "success")
            {           
                app.session = message_data.session;
                app.session_player = message_data.session_player;
            } 
            else
            {
            
            }
        },

      
        /** take next period response
         * @param message_data {json}
        */
        take_update_next_phase: function take_update_next_phase(message_data){
            app.end_game_modal.hide();

            app.session.world_state.current_experiment_phase = message_data.current_experiment_phase;
            app.session.world_state.finished = message_data.finished;

            if(app.session.world_state.current_experiment_phase == 'Names')
            {
                app.show_end_game_modal();
            }
            else
            {
                app.hide_end_game_modal();
            }
            
            if(app.session.world_state.current_experiment_phase == 'Done' && 
                    app.session.parameter_set.survey_required && 
                    !app.session_player.survey_complete)
            {
                window.location.replace(app.session_player.survey_link);
            }

            if(app.session.world_state.current_experiment_phase == 'Run' || 
                app.session.world_state.current_experiment_phase == 'Instructions')
            {
                app.session.world_state = message_data.world_state;
                
                app.do_reload();
                app.remove_all_notices();
            }
        },

        /** hide choice grid modal modal
        */
        hide_end_game_modal: function hide_end_game_modal(){
            app.end_game_modal_visible=false;
        },

        //do nothing on when enter pressed for post
        onSubmit: function onSubmit(){
            //do nothing
        },
        
        {%include "subject/subject_home/chat/chat_card.js"%}
        {%include "subject/subject_home/summary/summary_card.js"%}
        {%include "subject/subject_home/test_mode/test_mode.js"%}
        {%include "subject/subject_home/instructions/instructions_card.js"%}
        {%include "subject/subject_home/the_stage/pixi_setup.js"%}
        {%include "subject/subject_home/the_stage/helpers.js"%}
        {%include "subject/subject_home/the_stage/axis.js"%}
        {%include "subject/subject_home/the_stage/treatments.js"%}
        {%include "subject/subject_home/the_stage/selection_range.js"%}
        {%include "subject/subject_home/the_stage/group_summary.js"%}
        {%include "subject/subject_home/the_stage/controls.js"%}
        {%include "subject/subject_home/the_stage/subject.js"%}
        {%include "subject/subject_home/the_stage/text_emitter.js"%}
        {%include "subject/subject_home/the_stage/notices.js"%}
        {%include "subject/subject_home/help_doc_subject.js"%}

        /** clear form error messages
        */
        clear_main_form_errors: function clear_main_form_errors(){
            
            let s = app.form_ids;
            for(let i in s)
            {
                let e = document.getElementById("id_errors_" + s[i]);
                if(e) e.remove();
            }
        },

        /** display form error messages
        */
        display_errors: function display_errors(errors){
            for(let e in errors)
                {
                    //e = document.getElementById("id_" + e).getAttribute("class", "form-control is-invalid")
                    let str='<span id=id_errors_'+ e +' class="text-danger">';
                    
                    for(let i in errors[e])
                    {
                        str +=errors[e][i] + '<br>';
                    }

                    str+='</span>';

                    document.getElementById("div_id_" + e).insertAdjacentHTML('beforeend', str);
                    document.getElementById("div_id_" + e).scrollIntoView(); 
                }
        }, 

        /**
         * handle window resize event
         */
        handleResize: function handleResize(){
            
        },

    },

    mounted(){
        Vue.nextTick(() => {
            window.addEventListener('resize', app.handleResize);
        });
    },

}).mount('#app');

{%include "js/web_sockets.js"%}

  