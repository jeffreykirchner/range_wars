/**
 * draw the selection ranges under the axis
 */
setup_selection_range : function setup_selection_range(){

    if(!app.session.started) return;
    
    for(let i=0;i<pixi_selection_ranges.length;i++)
    {
        pixi_selection_ranges[i].destroy();
    }

    let current_group_memebers = app.session.world_state.groups[app.current_group];
    let session_players = app.session.world_state.session_players;
    let parameter_set_players = app.session.parameter_set.parameter_set_players;

    let margin = 5;
    let box_height = 5;
    let start_y = origin_y + margin*4;
    
    //draw bars
    for(let i=current_group_memebers.length-1;i>=0;i--)
    {
        let player_id = current_group_memebers[i];
        let player = session_players[player_id];      
        let parameter_set_player = parameter_set_players[player.parameter_set_player_id];

        let range_start_x = app.range_to_x(player.range_start);
        let range_end_x = app.range_to_x(player.range_end);
        let range_middle_x = app.range_to_x(player.range_middle);

        //bar
        let range_bar = new PIXI.Graphics();
        range_bar.roundRect(range_start_x,
                    start_y, 
                    range_end_x-range_start_x + box_width, 
                    box_height,
                    2);

        range_bar.fill({color: parameter_set_player.hex_color});
        range_bar.stroke({color: "lightgrey", width: 1,alignment: 0});
        pixi_selection_ranges.push(range_bar);

        pixi_container_main.addChild(range_bar);

        //center point
        let center = new PIXI.Graphics();
        center.circle(range_middle_x, start_y + box_height/2, 4);
        center.fill({color: "white"});
        center.stroke({color: parameter_set_player.hex_color, width: 1, alignment:0.5});
        pixi_selection_ranges.push(center);
        pixi_container_main.addChild(center);
        
        start_y += box_height + margin;
    }
},