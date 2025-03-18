send_chat: function send_chat(){

    if(app.working) return;
    if(app.chat_text.trim() == "") return;
    if(app.chat_text.trim().length > 100) return;

   
    if(app.session.world_state.current_experiment_phase == 'Instructions')
    {
        app.send_chat_instructions(app.chat_text);
    }
    else
    {
        app.working = true;
        app.send_message("chat", 
                        {"text" : app.chat_text,},
                        "group");
    }
    
    app.chat_text = "";       
                   
},

/** take updated data from goods being moved by another player
*    @param message_data {json} session day in json format
*/
take_update_chat: function take_update_chat(message_data){
    
    if(message_data.status == "success")
    {
        let text = message_data.text;
        let session_player_id = message_data.player_id;

        let chat = {session_player:session_player_id, 
                    message: text,
                    type:"chat"};
        app.chat_history.unshift(chat);
    }

    if(message_data.player_id == app.session_player.id)
    {
        app.working = false;
    }

},

/**
 * true if chat should be displayed
 */
show_chat: function show_chat()
{
    if(!app.session.started) return false;

    if(app.session.world_state.current_round > 1) return false;

    let period_block = app.session.parameter_set.parameter_set_periodblocks[app.session.world_state.current_period_block];
    let treatment = app.session.parameter_set.parameter_set_treatments[period_block.parameter_set_treatment];

    if(!treatment.enable_chat) return false;

    return true;
},

