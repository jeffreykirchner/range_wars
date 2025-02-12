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
        let session_player_id = message_data.sender_id;

        let chat = {session_player:session_player_id, message: text};
        app.chat_history.unshift(chat);
    }

    if(message_data.sender_id == app.session_player.id)
    {
        app.working = false;
    }

},

