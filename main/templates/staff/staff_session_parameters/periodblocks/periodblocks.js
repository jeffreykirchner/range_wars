/**show edit parameter set periodblock
 */
show_edit_parameter_set_periodblock: function show_edit_parameter_set_periodblock(index){
    
    if(app.session.started) return;
    if(app.working) return;

    app.clear_main_form_errors();
    app.current_parameter_set_periodblock = Object.assign({}, app.parameter_set.parameter_set_periodblocks[index]);
    
    app.edit_parameterset_periodblock_modal.toggle();
},

/** update parameterset periodblock
*/
send_update_parameter_set_periodblock: function send_update_parameter_set_periodblock(){
    
    app.working = true;

    app.send_message("update_parameter_set_periodblock", {"session_id" : app.session.id,
                                                    "parameterset_periodblock_id" : app.current_parameter_set_periodblock.id,
                                                    "form_data" : app.current_parameter_set_periodblock});
},

/** remove the selected parameterset periodblock
*/
send_remove_parameter_set_periodblock: function send_remove_parameter_set_periodblock(){

    app.working = true;
    app.send_message("remove_parameterset_periodblock", {"session_id" : app.session.id,
                                                   "parameterset_periodblock_id" : app.current_parameter_set_periodblock.id,});
                                                   
},

/** add a new parameterset periodblock
*/
send_add_parameter_set_periodblock: function send_add_parameter_set_periodblock(periodblock_id){
    app.working = true;
    app.send_message("add_parameterset_periodblock", {"session_id" : app.session.id});
                                                   
},

/**
 * duplicate the selected parameterset periodblock
 */
send_duplicate_parameter_set_periodblock: function send_duplicate_parameter_set_periodblock(){
    app.working = true;
    app.send_message("duplicate_parameterset_periodblock", {"session_id" : app.session.id,
                                                            "parameterset_periodblock_id" : app.current_parameter_set_periodblock.id,});
},