/**show edit parameter set player_group
 */
show_edit_parameter_set_player_group: function show_edit_parameter_set_player_group(player, index){
    
    if(app.session.started) return;
    if(app.working) return;

    app.clear_main_form_errors();
    app.current_parameter_set_player_group = Object.assign({}, app.parameter_set.parameter_set_players[player].parameter_set_player_groups[index]);
    
    app.edit_parameterset_player_group_modal.toggle();
},

/** update parameterset player_group
*/
send_update_parameter_set_player_group: function send_update_parameter_set_player_group(){
    
    app.working = true;

    app.send_message("update_parameter_set_player_group", {"session_id" : app.session.id,
                                                           "parameterset_player_group_id" : app.current_parameter_set_player_group.id,
                                                           "form_data" : app.current_parameter_set_player_group});
}, 