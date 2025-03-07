/**
 * send request to add new instruction page
 */
function send_add_help_doc(){
    app.working = true;
    app.send_message("add_help_doc_page", {id:app.instruction_set.id});
}

/**
 * send request to delete instruction page
 */
function send_delete_help_doc(instruction_id){
    if (!confirm('Delete Page?')) {
        return;
    }

    app.working = true;
    app.send_message("delete_help_doc_page", {id:app.instruction_set.id, instruction_id:instruction_id});
}

/**
 * show edit instruction modal
 */
function show_edit_help_doc_modal(id){
    app.clear_main_form_errors();
    app.cancel_modal = true;

    let instruction = app.instruction_set.instruction_pages[id];

    tinymce.get("id_text").setContent(instruction.text);
    
    app.current_help_doc = Object.assign({}, instruction);
    app.edit_help_doc_modal.show();
}

/**
 * send request to update instruction
 */
function send_update_help_doc(){
    app.working = true;
    app.current_help_doc.text = tinymce.get("id_text").getContent();
    app.send_message("update_help_doc", {form_data:app.current_help_doc});
}

/** hide edit instruction modal
*/
function hide_edit_help_doc_modal(){

    if(app.cancel_modal) Object.assign(app.instruction_set, app.paramterset_before_edit);
    app.paramterset_before_edit=null;
    app.cancel_modal = false;
    
}



