/**
 * draw the control handles for the selection range
 */
setup_control_handles : function setup_control_handles(){

    if(pixi_left_handle) pixi_left_handle.destroy();
    if(pixi_right_handle) pixi_right_handle.destroy();

    let session_player = app.session.world_state.session_players[app.session_player.id];
    let parameter_set_player = app.session.parameter_set.parameter_set_players[session_player.parameter_set_player_id];

    pixi_left_handle = new PIXI.Container();
    pixi_right_handle = new PIXI.Container();

    let handle_width = 50;
    let handle_height = 40;

    // let left_handle_x = app.range_to_x(session_player.range_start);
    // let right_handle_x = app.range_to_x(session_player.range_end) + box_width + 3;
    let y = x_axis_margin - handle_height - 7;

    //left handle
    //line
    let left_line = new PIXI.Graphics();
    left_line.moveTo(handle_width, 0);
    left_line.lineTo(handle_width, y + handle_height-5);
    left_line.stroke({color: "black", width: 3,alignment: 1, cap: "round"});
    pixi_left_handle.addChild(left_line);

    //box
    let left_box = new PIXI.Graphics();
    left_box.roundRect(0, y, handle_width, handle_height, 6);
    left_box.fill({color: parameter_set_player.hex_color});
    left_box.stroke({color: "black", width: 3,alignment: 0, cap: "round"});
    pixi_left_handle.addChild(left_box);

    let left_text = new PIXI.Text({text:"Start",style:control_style});
    left_text.position.set(handle_width/2, y+handle_height/2);
    left_text.anchor.set(0.5);
    pixi_left_handle.addChild(left_text);

    //triangle end cap
    let left_triangle = new PIXI.Graphics();
    left_triangle.moveTo(handle_width, 0);
    left_triangle.lineTo(handle_width, 10);
    left_triangle.lineTo(handle_width-10, 10);
    left_triangle.lineTo(handle_width, 0);
    left_triangle.fill({color: "black"});
    
    pixi_left_handle.addChild(left_triangle);

    pixi_left_handle.zIndex = 997;

    // pixi_left_handle.position.set(left_handle_x - pixi_left_handle.width, origin_y);

    pixi_container_main.addChild(pixi_left_handle);
    
    //right handle
    //line
    let right_line = new PIXI.Graphics();
    right_line.moveTo(0, 0);
    right_line.lineTo(0, y + handle_height-5);
    right_line.stroke({color: "black", width: 3,alignment: 0, cap: "round"});
    pixi_right_handle.addChild(right_line);

    //box
    let right_box = new PIXI.Graphics();
    right_box.roundRect(0, y, handle_width, handle_height, 6);
    right_box.fill({color: parameter_set_player.hex_color});
    right_box.stroke({color: "black", width: 3,alignment: 0, cap: "round"});
    pixi_right_handle.addChild(right_box);

    let right_text = new PIXI.Text({text:"End",style:control_style});
    right_text.position.set(handle_width/2, y+handle_height/2);
    right_text.anchor.set(0.5);
    pixi_right_handle.addChild(right_text);

    //triangle end cap
    let right_triangle = new PIXI.Graphics();
    right_triangle.moveTo(0, 0);
    right_triangle.lineTo(0, 10);
    right_triangle.lineTo(10, 10);
    right_triangle.lineTo(0, 0);
    right_triangle.fill({color: "black"});
    pixi_right_handle.addChild(right_triangle);

    pixi_right_handle.zIndex = 998;

    // pixi_right_handle.position.set(right_handle_x, origin_y);

    pixi_container_main.addChild(pixi_right_handle);

    app.update_left_handle_position();
    app.update_right_handle_position();
},

/**
 * check if the pointer is over the left handle
 */
is_over_left_handle: function is_over_left_handle(pt){
   if(pt.x >= pixi_left_handle.x && pt.x <= pixi_left_handle.x + pixi_left_handle.width &&
      pt.y >= pixi_left_handle.y && pt.y <= pixi_left_handle.y + pixi_left_handle.height)
   {
        return true;
   }

    return false;
},

/**
 * check if the pointer is over the right handle
 */
is_over_right_handle: function is_over_right_handle(pt){
    if(pt.x >= pixi_right_handle.x && pt.x <= pixi_right_handle.x + pixi_right_handle.width &&
       pt.y >= pixi_right_handle.y && pt.y <= pixi_right_handle.y + pixi_right_handle.height)
    {
         return true;
    }

     return false;
},

/**
 * upldate left handle position
 */
update_left_handle_position : function update_left_handle_position(){
    let session_player = app.session.world_state.session_players[app.session_player.id];
    let left_handle_x = app.range_to_x(app.current_selection_range.start);

    pixi_left_handle.position.set(left_handle_x - pixi_left_handle.width, origin_y);
},

/**
 * update right handle position
 */
update_right_handle_position : function update_right_handle_position(){
    let session_player = app.session.world_state.session_players[app.session_player.id];
    let right_handle_x = app.range_to_x(app.current_selection_range.end) + box_width + 3;

    pixi_right_handle.position.set(right_handle_x, origin_y);
},

/**
 * pointer down on left handle
 */
pixi_left_handle_pointerdown: function pixi_left_handle_pointerdown(event){
    if(!app.show_range_update_button) return;

    pixi_left_handle.alpha = 0.5;
    app.selection_handle = "left";
},

/**
 * pointer down on right handle
 */
pixi_right_handle_pointerdown: function pixi_right_handle_pointerdown(event){
    if(!app.show_range_update_button) return;
    
    pixi_right_handle.alpha = 0.5;
    app.selection_handle = "right";
},

/**
 * drag the left handle action
 */
pixi_left_handle_drag: function pixi_left_handle_drag(x){
    let r = app.x_to_range(x + pixi_left_handle.width/2);

    let session_player = app.session.world_state.session_players[app.session_player.id];

    if(r <= app.current_selection_range.end)
    {
        app.current_selection_range.start = r;
        app.update_left_handle_position();
        app.range_update_success = false;
    }
},

/**
 * drag the right handle action
 */
pixi_right_handle_drag: function pixi_right_handle_drag(x){
    let r = app.x_to_range(x - pixi_right_handle.width/2);

    let session_player = app.session.world_state.session_players[app.session_player.id];

    if(r >= app.current_selection_range.start)
    {
        app.current_selection_range.end = r;
        app.update_right_handle_position();
        app.range_update_success = false;
    }
},

/**
 * pointer up on the main container
 */
pixi_container_main_pointerup: function pixi_container_main_pointerup(event){
    pixi_left_handle.alpha = 1;
    pixi_right_handle.alpha = 1;
    app.selection_handle = null;
},

/**
 * handle pointer down on the main container
 */
pixi_container_main_pointerdown: function pixi_container_main_pointerdown(event){
    let local_pos = event.data.getLocalPosition(event.currentTarget);
    let pt = {x:local_pos.x, y:local_pos.y};

    if(app.is_over_left_handle(local_pos))
    {
        app.pixi_left_handle_pointerdown(event);
    }
    else if(app.is_over_right_handle(local_pos))
    {
        app.pixi_right_handle_pointerdown(event);
    }
},

pixi_container_main_pointermove: function pixi_container_main_pointermove(event){
    if(app.selection_handle == "left")
    {
        // let local_pos = event.data.getLocalPosition(event.currentTarget);
        app.pixi_left_handle_drag(event.data.getLocalPosition(event.currentTarget).x);
    }
    else if(app.selection_handle == "right")
    {
        // let local_pos = event.data.getLocalPosition(event.currentTarget);
        app.pixi_right_handle_drag(event.data.getLocalPosition(event.currentTarget).x);
    }
},

/**
 * submit new range to the server
 */
send_range: function send_range(){
    let session_player = app.session.world_state.session_players[app.session_player.id];
    let period_block = app.session.world_state.period_blocks[app.session.world_state.current_period_block];

    let data = {       
        range_start: app.current_selection_range.start,
        range_end: app.current_selection_range.end
    };

    if(period_block.phase="start") app.show_range_update_button = false;
    app.working = true;
    app.send_message("range", data, "group");
                    
},

/**
 * take result from send_range
 */
take_update_range: function take_update_range(message_data){
    app.working = false;
    let period_block = app.session.world_state.period_blocks[app.session.world_state.current_period_block];
    
    if(message_data.status == "success")
    {
        //display success message
        if(period_block.phase=="play")
        {
            app.range_update_success = true;
        }
    }
    else
    {
        //display error message
    }
},

/**
 * send cents to another person
 */
send_cents: function send_cents(){
    let data = {amount: app.send_cents_amount,
                recipient: app.send_cents_to};

    app.send_cents_error = null;
    app.working = true;
    app.send_message("cents", data, "group");
},

/**
 * take result from send_cents
 */
take_update_cents: function take_update_cents(message_data){
    app.working = false;
    
    if(message_data.status == "success")
    {
        app.send_cents_amount = 0;
        app.send_cents_to = null;       

        let session_player_id = message_data.player_id;
        let amount = message_data.amount;
        let recipient = message_data.recipient;
        let text = message_data.text;

        let chat = {session_player:session_player_id, 
                    message: text,
                    type:"cents"};

        app.chat_history.unshift(chat);
    }
    else
    {
        app.send_cents_error = "Error: " + message_data.error_message;
    }
},

