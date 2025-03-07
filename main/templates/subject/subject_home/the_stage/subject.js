/**
 * take rescue subject
 */
take_rescue_subject: function take_rescue_subject(message_data)
{
    app.working = false;

    pixi_left_handle.alpha = 1;
    pixi_right_handle.alpha = 1;
    app.selection_handle = null;

    app.setup_control_handles();
},