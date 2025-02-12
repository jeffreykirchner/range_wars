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
    let y = origin_y + x_axis_margin/2;

    //left handle
    //line
    let left_line = new PIXI.Graphics();
    left_line.moveTo(handle_width, 0);
    left_line.lineTo(handle_width, x_axis_margin/2 + handle_height-5);
    left_line.stroke({color: "black", width: 3,alignment: 1, cap: "round"});
    pixi_left_handle.addChild(left_line);

    //box
    let left_box = new PIXI.Graphics();
    left_box.roundRect(0, x_axis_margin/2, handle_width, handle_height, 6);
    left_box.fill({color: parameter_set_player.hex_color});
    left_box.stroke({color: "black", width: 3,alignment: 0, cap: "round"});
    pixi_left_handle.addChild(left_box);

    let left_text = new PIXI.Text({text:"Start",style:control_style});
    left_text.position.set(handle_width/2, x_axis_margin/2+handle_height/2);
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

    // pixi_left_handle.position.set(left_handle_x - pixi_left_handle.width, origin_y);

    pixi_container_main.addChild(pixi_left_handle);
    
    //right handle
    //line
    let right_line = new PIXI.Graphics();
    right_line.moveTo(0, 0);
    right_line.lineTo(0, x_axis_margin/2 + handle_height-5);
    right_line.stroke({color: "black", width: 3,alignment: 0, cap: "round"});
    pixi_right_handle.addChild(right_line);

    //box
    let right_box = new PIXI.Graphics();
    right_box.roundRect(0, x_axis_margin/2, handle_width, handle_height, 6);
    right_box.fill({color: parameter_set_player.hex_color});
    right_box.stroke({color: "black", width: 3,alignment: 0, cap: "round"});
    pixi_right_handle.addChild(right_box);

    let right_text = new PIXI.Text({text:"End",style:control_style});
    right_text.position.set(handle_width/2, x_axis_margin/2+handle_height/2);
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

    // pixi_right_handle.position.set(right_handle_x, origin_y);

    pixi_container_main.addChild(pixi_right_handle);

    app.update_left_handle_position();
    app.update_right_handle_position();

    //add interactivity
    pixi_left_handle.eventMode = 'dynamic';
    pixi_right_handle.eventMode = 'static';

    pixi_left_handle.on("pointerdown", app.pixi_left_handle_pointerdown);
    pixi_left_handle.on('pointermove', app.pixi_left_handle_pointermove);

    pixi_right_handle.on("pointerdown", app.pixi_right_handle_drag_start);
    // pixi_right_handle.on('pointermove', app.pixi_container_main_move);

},

/**
 * upldate left handle position
 */
update_left_handle_position : function update_left_handle_position(){
    let session_player = app.session.world_state.session_players[app.session_player.id];
    let left_handle_x = app.range_to_x(session_player.range_start);

    pixi_left_handle.position.set(left_handle_x - pixi_left_handle.width, origin_y);
},

/**
 * update right handle position
 */
update_right_handle_position : function update_right_handle_position(){
    let session_player = app.session.world_state.session_players[app.session_player.id];
    let right_handle_x = app.range_to_x(session_player.range_end) + box_width + 3;

    pixi_right_handle.position.set(right_handle_x, origin_y);
},

/**
 * pointer down on left handle
 */
pixi_left_handle_pointerdown: function pixi_left_handle_pointerdown(event){
    pixi_left_handle.alpha = 0.5;
    app.selection_handle = "left";
},

/**
 * pointer move on left handle
 */
pixi_left_handle_pointermove: function pixi_left_handle_pointermove(event){
    if(app.selection_handle == "left")
    {
        let local_pos = event.data.getLocalPosition(event.currentTarget);
        app.pixi_left_handle_drag(local_pos.x + pixi_left_handle.x);
    }
    
},

/**
 * drag the left handle action
 */
pixi_left_handle_drag: function pixi_left_handle_drag(x){
    let r = app.x_to_range(x);

    let session_player = app.session.world_state.session_players[app.session_player.id];

    if(r != session_player.range_start)
    {
        session_player.range_start = r;
        app.update_left_handle_position();
    }
},

pixi_right_handle_drag_start: function pixi_right_handle_drag_start(event){
    pixi_right_handle.alpha = 0.5;
    app.selection_handle = "right";
},

pixi_container_pointerup: function pixi_container_pointerup(event){
    pixi_left_handle.alpha = 1;
    pixi_right_handle.alpha = 1;
    app.selection_handle = null;
},

pixi_container_main_move: function pixi_container_main_move(event){
    if(app.selection_handle == "left")
    {
        let local_pos = event.data.getLocalPosition(event.currentTarget);
        app.pixi_left_handle_drag(local_pos.x);
    }
    else if(app.selection_handle == "right")
    {
        
    }
},