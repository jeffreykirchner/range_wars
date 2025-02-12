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
                        width: 0.5,
                        lineJoin: "round",
                        alignment: 1,
                        cap: "round"});
        outline.zIndex = 999;

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
        let start_y = total_height-height_per_player;

        //destory old boxes
        for(let p in pixi_boxes[i].revenue_boxes)
        {
            pixi_boxes[i].revenue_boxes[p].destroy();
        }

        for(let p in group_members_in_box)
        {
            let session_player_id = current_group_memebers[group_members_in_box[p]];
            let session_player = app.session.world_state.session_players[session_player_id];
            let parameter_set_player = parameter_set_players[session_player.parameter_set_player_id];

            let revenue_box = new PIXI.Container();

            let revenue_box_fill = new PIXI.Graphics();
            revenue_box_fill.rect(0, 0, box_width, height_per_player)
            revenue_box_fill.fill({color: parameter_set_player.hex_color});

            revenue_box.addChild(revenue_box_fill);

            //draw cost line for local player
            if(session_player_id == app.session_player.id)
            {
                let cost_box = new PIXI.Graphics();
                let cost_y = app.value_to_y(session_player.cost);
                cost_box.rect(0, height_per_player-cost_y, box_width, cost_y);
                cost_box.fill({color: "white", alpha: 0.5});
                revenue_box.addChild(cost_box);

                cost_box = new PIXI.Graphics();
                cost_box.rect(0, height_per_player-cost_y, box_width, 1);
                cost_box.fill({color: parameter_set_player.hex_color, alpha: 0.5});
                revenue_box.addChild(cost_box);
            }

            revenue_box.x = 0;
            revenue_box.y = start_y;

            pixi_boxes[i].revenue_boxes[p] = revenue_box;
            box.addChild(revenue_box);

            start_y -= height_per_player;
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

/**
 * convert range selection to x coordinate
 */
range_to_x : function range_to_x(range)
{
    return (box_width * range) + y_axis_margin;
},

/**
 * convert x value to range
 */
x_to_range : function x_to_range(x)
{
    if(x < y_axis_margin) return 0;
    if(x > (axis_width + y_axis_margin)) return app.session.parameter_set.parameter_set_treatments[current_treatment].values.length - 1;

    return Math.floor((x - y_axis_margin) / box_width);
},