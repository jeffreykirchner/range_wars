/**
 * setup boxes for the current treatment
 */
setup_treatment : function setup_treatment(){
    let values = app.session.parameter_set.parameter_set_treatments[current_treatment].values.split(",");
    let parameter_set_players = app.session.parameter_set.parameter_set_players;
    let parameter_set_players_order = app.session.parameter_set.parameter_set_players_order;

    box_width = axis_width / values.length;

    let start_location_x = y_axis_margin;

    for(let i in values)
    {
        let box_json = {revenue_boxes: {}};
                        
        let box = new PIXI.Container();

        let outline = new PIXI.Graphics();

        let value = parseFloat(values[i]);
        let y = app.value_to_y(value);

        outline.rect(0,0, box_width, y);
        outline.stroke({color: "lightgray",
                        width: 2,
                        lineJoin: "round",
                        cap: "round"});

        box.x = start_location_x;
        box.y = origin_y - y;

        box_json.box = box;

        box.addChild(outline);

        pixi_boxes.push(box_json);

        pixi_container_main.addChild(box);
        start_location_x += box_width;
    }
},

/**
 * update the boxes for the current treatment
 */
update_treatment : function update_treatment(){
    let values = app.session.parameter_set.parameter_set_treatments[current_treatment].values.split(",");
    let parameter_set_players = app.session.parameter_set.parameter_set_players;
    let parameter_set_players_order = app.session.parameter_set.parameter_set_players_order;
    let world_state = app.session.world_state;
    let current_group_memebers = world_state["groups"][current_group];
    let session_players = world_state["session_players"];

    for(let i=0;i<pixi_boxes.length;i++)
    {   
        let value = values[i];
        let box = pixi_boxes[i].box;

        //set box height to zero
        for(let b in pixi_boxes[i].revenue_boxes)
        {
            pixi_boxes[i].revenue_boxes[b].height = 0;
        }

        //find number if group members in this box
        let group_members_in_box = [];
        for(let p in current_group_memebers)
        {
            let session_player = session_players[current_group_memebers[p]];
            if(session_player.revenues[value] > 0)
            {
                group_members_in_box.push(p);
            }
        }

        let total_height = pixi_boxes[i].box.height;
        let height_per_player = total_height / group_members_in_box.length;
        let start_y = total_height;

        //destory old boxes
        for(let p in pixi_boxes[i].revenue_boxes)
        {
            pixi_boxes[i].revenue_boxes[p].destroy();
        }

        for(let p in group_members_in_box)
        {
            let parameter_set_player_id = parameter_set_players_order[group_members_in_box[p]];
            let parameter_set_player = parameter_set_players[parameter_set_player_id];

            let revenue_box = new PIXI.Graphics();
            revenue_box.rect(0,start_y-height_per_player, box_width, height_per_player)
            revenue_box.fill({color: parameter_set_player.hex_color});

            start_y -= height_per_player;

            box.addChild(revenue_box);
            pixi_boxes[i].revenue_boxes[p] = revenue_box;
        }
    }
},

/**
 * convert a value to a y coordinate
 */
value_to_y : function value_to_y(value){

    let unit_rate = axis_height / app.session.parameter_set.parameter_set_treatments[current_treatment].range_height;

    return value * unit_rate;

},