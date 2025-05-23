
{% load static %}

"use strict";

axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
axios.defaults.xsrfCookieName = "csrftoken";

//let app.session.world_state = {};
{%include "subject/subject_home/the_stage/pixi_globals.js"%}

let worker = null;

//vue app
let app = Vue.createApp({
    delimiters: ["[[", "]]"],

    data() {return {chat_socket : "",
                    reconnecting : true,
                    working : false,
                    is_subject : false,
                    first_load_done : false,          //true after software is loaded for the first time
                    help_text : "Loading ...",
                    help_modal_title : "Help",
                    user_id : {{user.id}},
                    session_id : {{session.id}},
                    session_key : "{{session.session_key}}",
                    session : null,
                    session_events : null,
                    the_feed : {},
                    staff_edit_name_etc_form_ids: {{staff_edit_name_etc_form_ids|safe}},
                    pixi_tick_tock : {value:"tick", time:Date.now()},

                    move_to_next_phase_text : 'Start Next Experiment Phase',

                    data_downloading : false,                   //show spinner when data downloading
                    earnings_copied : false,                    //if true show earnings copied   

                    staff_edit_name_etc_form : {name : "", student_id : "", email : "", id : -1},
                    send_message_modal_form : {subject : "", text : ""},

                    email_result : "",                          //result of sending invitation emails
                    email_default_subject : "{{parameters.invitation_subject}}",
                    email_default_text : `{{parameters.invitation_text|safe}}`,

                    email_list_error : "",
                    collaborators_list_error : "",

                    csv_email_list : "",           //csv email list
                    csv_collaborators_list : "",   //csv collaborators list

                    last_world_state_update : null,

                    //modals
                    edit_subject_modal : null,
                    edit_session_modal : null,
                    send_message_modal : null,
                    upload_email_modal : null,
                    upload_collaborators_modal : null,

                    //pixi
                    canvas_width  : null,
                    canvas_height : null,
                    move_speed : 5,
                    animation_speed : 0.5,
                    scroll_speed : 10,
                    pixi_mode : "staff",
                    pixi_scale : 1,
                    pixi_scale_range_control : 1,
                    stage_width : 10000,
                    stage_height : 10000,
                    scroll_direction : {x:0, y:0},
                    current_location : {x:0, y:0},
                    follow_subject : -1,
                    draw_bounding_boxes: false,

                    //replay
                    session_events : null,
                    session_ticks : null,
                    replay_mode : "paused",
                    replay_timeout : null,
                    replay_current_period : 0,

                    //current treatment and group
                    current_treatment : null,
                    current_group : 1,
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
            app.session.world_state.timer_running = false;
            if(worker) worker.terminate();
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
                case "update_session":
                    app.take_update_session(message_data);
                    break;
                case "update_start_experiment":
                    app.take_update_start_experiment(message_data);
                    break;
                case "update_reset_experiment":
                    app.take_reset_experiment(message_data);
                    break;
                case "next_phase":
                    app.take_next_phase(message_data);
                    break; 
                case "update_next_phase":
                    app.take_update_next_phase(message_data);
                    break; 
                case "update_chat":
                    app.take_update_chat(message_data);
                    break;
                case "update_time":
                    app.take_update_time(message_data);
                    break;
                case "start_timer":
                    app.take_start_timer(message_data);
                    break;   
                case "stop_timer_pulse":
                    app.take_stop_timer_pulse(message_data);
                case "update_connection_status":
                    app.take_update_connection_status(message_data);
                    break;   
                case "reset_connections":
                    app.take_reset_connections(message_data);
                    break; 
                case "update_reset_connections":
                    app.take_update_reset_connections(message_data);
                    break; 
                case "update_name":
                    app.take_update_name(message_data);
                    break;         
                case "download_summary_data":
                    app.take_download_summary_data(message_data);
                    break;
                case "download_period_block_data":
                    app.take_download_period_block_data(message_data);
                    break;
                case "download_action_data":
                    app.take_download_action_data(message_data);
                    break;
                case "download_recruiter_data":
                    app.take_download_recruiter_data(message_data);
                    break;
                case "download_payment_data":
                    app.take_download_payment_data(message_data);
                    break;
                case "update_next_instruction":
                    app.take_next_instruction(message_data);
                    break;
                case "update_finish_instructions":
                    app.take_finished_instructions(message_data);
                    break;
                case "help_doc":
                    app.take_load_help_doc(message_data);
                    break;
                case "end_early":
                    app.take_end_early(message_data);
                    break;
                case "update_subject":
                    app.take_update_subject(message_data);
                    break;
                case "send_invitations":
                    app.take_send_invitations(message_data);
                    break;
                case "email_list":
                    app.take_update_email_list(message_data);
                    break;
                case "update_anonymize_data":
                    app.take_anonymize_data(message_data);
                    break;
                case "update_survey_complete":
                    app.take_update_survey_complete(message_data);
                    break;
                case "update_refresh_screens":
                    app.take_refresh_screens(message_data);
                    break;
                case "update_interaction":
                    app.take_interaction(message_data);
                    break;
                case "update_cancel_interaction":
                    app.take_cancel_interaction(message_data);
                    break;   
                case "load_session_events":
                    app.take_load_session_events(message_data);
                    break; 
                case "update_rescue_subject":
                    app.take_rescue_subject(message_data);
                    break;
                case "add_collaborators":
                    app.take_add_collaborators(message_data);
                    break;
                case "lock_session":
                    app.take_lock_session(message_data);
                    break;
            }
            app.working = false;
            app.process_the_feed(message_type, message_data);
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
            app.edit_subject_modal = bootstrap.Modal.getOrCreateInstance(document.getElementById('edit_subject_modal'), {keyboard: false});
            app.edit_session_modal = bootstrap.Modal.getOrCreateInstance(document.getElementById('edit_session_modal'), {keyboard: false});;           
            app.send_message_modal = bootstrap.Modal.getOrCreateInstance(document.getElementById('send_message_modal'), {keyboard: false});           
            app.upload_email_modal = bootstrap.Modal.getOrCreateInstance(document.getElementById('upload_email_modal'), {keyboard: false});
            app.upload_collaborators_modal = bootstrap.Modal.getOrCreateInstance(document.getElementById('upload_collaborators_modal'), {keyboard: false});

            document.getElementById('edit_subject_modal').addEventListener('hidden.bs.modal', app.hide_edit_subject);
            document.getElementById('edit_session_modal').addEventListener('hidden.bs.modal', app.hide_edit_session);
            document.getElementById('send_message_modal').addEventListener('hidden.bs.modal', app.hide_send_invitations);
            document.getElementById('upload_email_modal').addEventListener('hidden.bs.modal', app.hide_send_email_list);
            document.getElementById('upload_collaborators_modal').addEventListener('hidden.bs.modal', app.hide_send_collaborators_list);

            tinyMCE.init({
                target: document.getElementById('id_invitation_text'),
                height : "400",
                theme: "silver",
                convert_urls: false,
                promotion: false,
                plugins: "searchreplace,code,link",
                toolbar: "undo redo | styleselect | forecolor | bold italic | alignleft aligncenter alignright alignjustify | outdent indent | link | code",
            });
    
            // Prevent Bootstrap dialog from blocking focusin
            document.addEventListener('focusin', (e) => {
                if (e.target.closest(".tox-tinymce-aux, .moxman-window, .tam-assetmanager-root") !== null) {
                    e.stopImmediatePropagation();
                }
                });
            
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
        },

        /** send winsock request to get session info
        */
        send_get_session: function send_get_session(){
            app.send_message("get_session",{"session_key" : app.session_key});
        },

        /** take create new session
        *    @param message_data {json} session day in json format
        */
        take_get_session: function take_get_session(message_data){
            
            app.session = message_data;

            app.session.world_state =  app.session.world_state;

            let world_state = app.session.world_state;

            if(app.session.started)
            {
                let session_period_id = world_state.session_periods_order[world_state.current_period-1];
                let session_period = world_state.session_periods[session_period_id];
                let parameter_set_periodblock = app.session.parameter_set.parameter_set_periodblocks[session_period.parameter_set_periodblock_id];
                
                app.current_treatment = app.get_current_treatment().id;
                app.current_group = 1;

                app.the_feed = {};
                for(let i in app.session.world_state.groups)
                {
                    app.the_feed[i] = [];
                }
            }
            else
            {
                app.current_treatment = app.session.parameter_set.parameter_set_treatments_order[0];
                app.current_group = 1;
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
            
            app.update_phase_button_text();
            let v = {};
            v.timer_running = app.session.world_state.timer_running;
            app.take_start_timer(v); 
        },

        /**update text of move on button based on current state
         */
        update_phase_button_text: function update_phase_button_text(){
            if(app.session.world_state.finished && app.session.world_state.current_experiment_phase == "Done")
            {
                app.move_to_next_phase_text = '** Session complete **';
            }
            else if( app.session.world_state.current_experiment_phase == "Names")
            {
                app.move_to_next_phase_text = 'Complete Session <i class="fas fa-flag-checkered"></i>';
            }
            else if( app.session.world_state.current_experiment_phase == "Run")
            {
                app.move_to_next_phase_text = 'Running ...';
            }
            else if(app.session.started && !app.session.world_state.finished)
            {
                if(app.session.world_state.current_experiment_phase == "Selection" && app.session.parameter_set.show_instructions)
                {
                    app.move_to_next_phase_text = 'Show Instrutions <i class="fas fa-map"></i>';
                }
                else
                {
                    app.move_to_next_phase_text = 'Continue Session <i class="far fa-play-circle"></i>';
                }
            }
        },

        /** take updated data from goods being moved by another player
        *    @param message_data {json} session day in json format
        */
        take_update_chat: function take_update_chat(message_data){
            
            if(message_data.status == "success")
            {
                let text = message_data.text;
                
            }
            else
            {
               
            }
        },

        /**
         * update time and start status
         */
        take_update_time: function take_update_time(message_data){
           
            let status = message_data.value;
            let world_state = app.session.world_state;

            if(status == "fail") return;

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
           
            app.update_phase_button_text();

            //check if a new period block is has started
            if(world_state.current_round == 1 && world_state.current_period > 1)
            {
                let session_period_id = world_state.session_periods_order[world_state.current_period-1];
                let session_period = world_state.session_periods[session_period_id];
                let parameter_set_periodblock = app.session.parameter_set.parameter_set_periodblocks[session_period.parameter_set_periodblock_id];
                
                app.current_treatment = app.get_current_treatment().id;
                
                app.setup_main_container();
                
                app.setup_axis();
                app.setup_treatment();
                // app.update_treatment();
                // app.setup_selection_range();
            }
            else
            {
                
            }

            app.update_treatment();
            app.setup_selection_range();
            app.setup_group_summary();
            
        },
       
        //do nothing on when enter pressed for post
        onSubmit(){
            //do nothing
        },
        
        {%include "staff/staff_session/control/control_card.js"%}
        {%include "staff/staff_session/session/session_card.js"%}
        {%include "staff/staff_session/subjects/subjects_card.js"%}
        {%include "staff/staff_session/summary/summary_card.js"%}
        {%include "staff/staff_session/data/data_card.js"%}
        {%include "staff/staff_session/interface/interface_card.js"%}
        {%include "staff/staff_session/replay/replay_card.js"%}
        {%include "staff/staff_session/the_feed/the_feed_card.js"%}        
        {%include "subject/subject_home/the_stage/pixi_setup.js"%}
        {%include "subject/subject_home/the_stage/axis.js"%}
        {%include "subject/subject_home/the_stage/treatments.js"%}
        {%include "subject/subject_home/the_stage/selection_range.js"%}
        {%include "subject/subject_home/the_stage/group_summary.js"%}
        {%include "subject/subject_home/the_stage/helpers.js"%}
       
        {%include "subject/subject_home/the_stage/staff.js"%}
        {%include "subject/subject_home/the_stage/text_emitter.js"%}
        {%include "js/help_doc.js"%}
    
        /** clear form error messages
        */
        clear_main_form_errors: function clear_main_form_errors(){
            
            for(let item in app.session)
            {
                let e = document.getElementById("id_errors_" + item);
                if(e) e.remove();
            }

            let s = app.staff_edit_name_etc_form_ids;
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
    },

    mounted(){

    },

}).mount('#app');

{%include "js/web_sockets.js"%}

  