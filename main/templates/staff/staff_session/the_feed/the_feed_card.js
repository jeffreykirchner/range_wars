/**
 * process incoming message for the feed
 */
process_the_feed: function process_the_feed(message_type, message_data)
{
    if(message_data.status != "success") return;
    
    let html_text = "";
    let sender_label = "";
    let receiver_label = "";

    let parameter_set_player = app.get_parameter_set_player_from_player_id(message_data.player_id);
    let session_player = app.session.world_state.session_players[message_data.player_id];

    switch(message_type) {                
        
        case "update_chat":
            html_text = "<span style='color:" + parameter_set_player.hex_color + "'>" + parameter_set_player.id_label + "</span>: " +  message_data.text;
            break;
        case "update_cents":
            html_text = "<i>" + message_data.text + "</i>";
            break;
        case "update_range":
            if(message_data.ready_to_go_pressed)
            {
                html_text = "<span style='color:" + parameter_set_player.hex_color + "'>" + parameter_set_player.id_label + "</span> Ready to Start";
            }
            else
            {
                let start_range = parseInt(message_data.range_start) + 1;
                let end_range = parseInt(message_data.range_end) + 1;
                html_text = "<span style='color:" + parameter_set_player.hex_color + "'>" + parameter_set_player.id_label + "</span> Range: " +  start_range + " to " + end_range;
            }
            
            break;
    }

    if(html_text != "") {
        if(app.the_feed[session_player.group_number].length > 100) app.the_feed[session_player.group_number].pop();
        app.the_feed[session_player.group_number].unshift(html_text);
    }

},