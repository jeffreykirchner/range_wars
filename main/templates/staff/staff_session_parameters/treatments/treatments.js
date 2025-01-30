/**show edit parameter set treatment
 */
show_edit_parameter_set_treatment: function show_edit_parameter_set_treatment(index){
    
    if(app.session.started) return;
    if(app.working) return;

    app.clear_main_form_errors();
    app.current_parameter_set_treatment = Object.assign({}, app.parameter_set.parameter_set_treatments[index]);
    
    app.edit_parameterset_treatment_modal.toggle();
},

/** update parameterset treatment
*/
send_update_parameter_set_treatment: function send_update_parameter_set_treatment(){
    
    app.working = true;

    app.send_message("update_parameter_set_treatment", {"session_id" : app.session.id,
                                                    "parameterset_treatment_id" : app.current_parameter_set_treatment.id,
                                                    "form_data" : app.current_parameter_set_treatment});
},

/** remove the selected parameterset treatment
*/
send_remove_parameter_set_treatment: function send_remove_parameter_set_treatment(){

    app.working = true;
    app.send_message("remove_parameterset_treatment", {"session_id" : app.session.id,
                                                   "parameterset_treatment_id" : app.current_parameter_set_treatment.id,});
                                                   
},

/** add a new parameterset treatment
*/
send_add_parameter_set_treatment: function send_add_parameter_set_treatment(treatment_id){
    app.working = true;
    app.send_message("add_parameterset_treatment", {"session_id" : app.session.id});
                                                   
},